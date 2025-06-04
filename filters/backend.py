__all__ = ['filter_by_no_of_fragments', 'filter_by_planes']

import threading
from caveclient import CAVEclient
from api_token import API_TOKEN
from constants import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import get, exceptions
import random
import pandas as pd
import numpy as np
import re

'''
def filter_dust(source_group, min_no_of_synapses, callback):
  threading.Thread(target=lambda: filter_dust_request(source_group, min_no_of_synapses, callback), daemon=True).start()

def filter_dust_request(source_group, min_no_of_synapses, callback):
  try:
    client = CAVEclient('brain_and_nerve_cord', auth_token=API_TOKEN)

    key = 'partners' if source_group == 'partners' else 'partners_of_partners'
    source = data[key]
    direction = data['direction']

    if direction == 'both':
      source_ids = pd.concat([source['upstream'], source['downstream']], ignore_index=True).values.flatten().tolist()
    else:
      source_ids = source[direction].values.flatten().tolist()

    results = []
    total = len(source_ids)
    processed = 0
    BATCH_SIZE = 500

    def process_batch(batch):
      retries = 0
      while retries < 5:
        try:
          # Query both pre and post synapses for this batch
          pre_synapses = client.materialize.synapse_query(pre_ids=batch)
          post_synapses = client.materialize.synapse_query(post_ids=batch)
          
          # Convert to dictionaries for faster lookup
          pre_counts = pre_synapses['pre_pt_root_id'].value_counts().to_dict()
          post_counts = post_synapses['post_pt_root_id'].value_counts().to_dict()
          
          # Collect IDs with synapse counts above max_size
          batch_results = []
          for seg_id in batch:
            total_synapses = pre_counts.get(seg_id, 0) + post_counts.get(seg_id, 0)
            if total_synapses > min_no_of_synapses:
              batch_results.append(seg_id)
          
          return batch_results

        except TimeoutError:
          retries += 1
          if retries == 5:
            raise Exception('Max retries reached after timeout for batch')
          time.sleep(0.5)  # Wait 1 second before retrying

    # Process each batch sequentially
    for i in range(0, len(source_ids), BATCH_SIZE):
      batch = source_ids[i:i + BATCH_SIZE]
      batch_results = process_batch(batch)
      results.extend(batch_results)
      processed += len(batch)
      callback(f'MSG:IN_PROGRESS:Processed {processed}/{total} IDs. Kept {len(results)} IDs so far.')

    callback(f'MSG:COMPLETE:Completed processing {total} segments')
    callback(sorted(results))
    
  except Exception as e:
    callback(f'MSG:ERROR:Error: {str(e)}')
'''

def filter_by_no_of_fragments(source_ids, min_size, min_frags, max_frags, callback):
  threading.Thread(target=lambda: filter_by_no_of_fragments_request(source_ids, min_size, min_frags, max_frags, callback), daemon=True).start()

def filter_by_no_of_fragments_request(source_ids, min_size, min_frags, max_frags, callback, max_workers=100):
  base_url = 'https://cave.fanc-fly.com/meshing/api/v1/table/wclee_fly_cns_001/manifest/'
  headers = {
    'Content-Type': 'application/json',
    'Accept-Encoding': 'zstd',
    'Authorization': f'Bearer {API_TOKEN}',
    'Cookie': f'middle_auth_token={API_TOKEN}'
  }

  def check_fragments(seg_id, min_size=10000, min_frags=2, max_frags=100, max_retries=5):
    url = f'{base_url}{seg_id}:0?verify=1&prepend_seg_ids=1'
    retries = 0
    while retries < max_retries:
      try:
        response = get(url, headers=headers, timeout=10)
        if response.status_code == 200:
          total_size = 0
          fragments = response.json().get('fragments', [])
          length = len(fragments)

          if length > max_frags:
            return { 'type': 'large', 'id': seg_id }
          
          for frag in fragments:
            if '/' not in frag:
              #return { 'type': 'small', 'id': seg_id } # ???
              continue
            total_size += int(frag.rsplit(':', 1)[-1])

          if total_size >= min_size:
            return { 'type': 'middle', 'id': seg_id }
          
          # if min_size is smaller than minimum, but the number of fragments is still equal/larger, than the min_frags
          if length >= min_frags:
            return { 'type': 'middle', 'id': seg_id }

          return { 'type': 'small', 'id': seg_id }

        elif response.status_code in {429, 500, 502, 503, 504}:
          time.sleep(2 ** retries + random.random())
          retries += 1
        else:
          break

      except exceptions.RequestException:
        time.sleep(2 ** retries)
        retries += 1

    return None

  processed = 0
  correct = 0
  smaller = 0
  larger = 0
  total = len(source_ids)
  results = {
    'small': [],
    'middle': [],
    'large': []
  }

  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_seg = {executor.submit(check_fragments, seg_id, min_size, min_frags, max_frags): seg_id for seg_id in source_ids}

    for future in as_completed(future_to_seg):  # Process completed requests first
      result = future.result()
      res_type = result['type']

      results[res_type].append(result['id'])
      
      if res_type == 'small':
        smaller += 1
      elif res_type == 'middle':
        correct += 1
      elif res_type == 'large':
        larger += 1


      processed += 1

      if processed % 1000 == 0:  # Cool-down after every 1000 processed requests
        wait_time = random.uniform(1, 2)
        callback(f'MSG:COOLDOWN:Pausing for {wait_time:.2f} seconds...')
        time.sleep(wait_time)

      if processed % 100 == 0:
        callback(f'MSG:IN_PROGRESS:Processed: {processed}/{total}\nToo small: {smaller}\nCorrect size: {correct}\nToo large: {larger}')

  callback(results)

def filter_by_planes(source_ids, planes, callback):
  threading.Thread(target=lambda: filter_by_planes_request(source_ids, planes, callback), daemon=True).start()

def filter_by_planes_request(source_ids, planes, callback):
  client = CAVEclient('brain_and_nerve_cord', auth_token=API_TOKEN)
  leaves = []
  processed = 0
  total = len(source_ids)
  lock = threading.Lock()
  # Map source_id to its leaves
  source_to_leaves = {}

  def safe_get_leaves(seg_id):
    try:
      return get_leaves(seg_id)
    except Exception as e:
      return []

  with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_seg = {executor.submit(safe_get_leaves, seg_id): seg_id for seg_id in source_ids}
    for i, future in enumerate(as_completed(future_to_seg), 1):
      seg_id = future_to_seg[future]
      seg_leaves = future.result()
      with lock:
        leaves.extend(seg_leaves)
        source_to_leaves[seg_id] = seg_leaves
      processed += 1
      if processed % 100 == 0 or processed == total:
        callback(f'MSG:IN_PROGRESS:Processed {processed}/{total} segment leaves')

  # Notify frontend before analyzing
  callback('MSG:IN_PROGRESS:Analyzing collected data...')

  coords = client.l2cache.get_l2data(leaves, attributes=['rep_coord_nm'])

  # Build DataFrame from coords
  df = pd.DataFrame.from_dict(coords, orient='index')
  df['id'] = df.index # keep as string to avoid OverflowError
  df[['x', 'y', 'z']] = pd.DataFrame(df['rep_coord_nm'].tolist(), index=df.index)

  # Filter for valid rows (rep_coord_nm present and length 3)
  df_valid = df[df['rep_coord_nm'].apply(lambda v: isinstance(v, list) and len(v) == 3)]

  def filter_by_single_plane(plane):
    # Plane defined by three points
    plane = re.split(r';\s*', plane)
    p1_unscaled = np.array([float(x) for x in re.split(r',\s*', plane[0])])
    p2_unscaled = np.array([float(x) for x in re.split(r',\s*', plane[1])])
    p3_unscaled = np.array([float(x) for x in re.split(r',\s*', plane[2])])

    # Normal vector to the plane
    v1 = p2_unscaled - p1_unscaled
    v2 = p3_unscaled - p1_unscaled
    normal_unscaled = np.cross(v1, v2)


    scaling_factors = np.array([4, 4, 45])
    normal = normal_unscaled / scaling_factors
    normal = normal / np.linalg.norm(normal)

    p1 = p1_unscaled * scaling_factors

    def point_side(point):
      return np.dot(normal, point - p1)
    inside_source_ids = []
    outside_source_ids = []

    for source_id, leaf_list in source_to_leaves.items():
      if not leaf_list:
        outside_source_ids.append(source_id)
        continue
      # Get coordinates for all leaves
      leaf_coords = [df_valid.loc[str(leaf_id), ['x', 'y', 'z']].values for leaf_id in leaf_list if str(leaf_id) in df_valid.index]
      if not leaf_coords:
        outside_source_ids.append(source_id)
        continue
      # Check the sign of all points
      sides = [point_side(coord) for coord in leaf_coords]

      if all(s >= 0 for s in sides):
        inside_source_ids.append(source_id)
      else:
        outside_source_ids.append(source_id)
    callback({'inside': inside_source_ids, 'outside': outside_source_ids})
    return
  
  planes = planes.splitlines()

  for plane in planes:
    filter_by_single_plane(plane)

def get_leaves(seg_id):
  url = f'https://cave.fanc-fly.com/segmentation/api/v1/table/wclee_fly_cns_001/node/{seg_id}/leaves?stop_layer=2'
  headers = {
    'Content-Type': 'application/json',
    'Accept-Encoding': 'zstd',
    'Authorization': f'Bearer {API_TOKEN}',
    'Cookie': f'middle_auth_token={API_TOKEN}'
  }

  response = get(url, headers=headers, timeout=10)
  if response.status_code == 200:
    return response.json()['leaf_ids']
