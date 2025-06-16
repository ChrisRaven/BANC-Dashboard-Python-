__all__ = ['filter_by_no_of_fragments', 'filter_by_planes']

import threading
from caveclient import CAVEclient
from api_token import API_TOKEN
from constants import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import get, post, exceptions
import random
import pandas as pd
import numpy as np
import re
import json


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
  segid_to_leaves = {}
  lock = threading.Lock()
  total = len(source_ids)
  processed = 0
  
  def get_leaves_worker(seg_ids):
    try:
      leaves = get_leaves(seg_ids)
      if leaves:
        # Filter out any source_ids that have 10 or fewer leaves
        return {seg_id: leaf_list for seg_id, leaf_list in leaves.items() if len(leaf_list) > 10}
    except Exception:
      return None
    return None

  # Create batches of 200 source_ids
  batches = [source_ids[i:i + 200] for i in range(0, len(source_ids), 200)]
  
  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(get_leaves_worker, batch): batch for batch in batches}
    for i, future in enumerate(as_completed(futures), 1):
      result = future.result()
      if result:
        with lock:
          segid_to_leaves.update(result)
      processed += len(futures[future])
      if processed % 200 == 0 or processed == total:
        callback(f'MSG:IN_PROGRESS:Got leaves for {processed}/{total} segments')

  # Only use eligible source_ids from segid_to_leaves for all further processing
  source_to_leaves = segid_to_leaves.copy()

  # If planes is empty or only whitespace, return all eligible source_ids as 'inside'
  if not planes or not planes.strip():
    callback({'inside': list(source_to_leaves.keys()), 'outside': []})
    return

  callback('MSG:IN_PROGRESS:Getting L2 centroids...')
  # Sample every 5th leaf to optimize processing
  sampled_leaves = []
  for leaf_list in source_to_leaves.values():
    sampled_leaves.extend(leaf_list[::5])

  # Process L2 centroids in batches of 10000
  BATCH_SIZE = 10000
  all_coords = {}
  lock = threading.Lock()
  total_batches = (len(sampled_leaves) + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division
  processed_batches = 0

  def process_l2_batch(batch_num, batch_leaves):
    try:
      batch_coords = client.l2cache.get_l2data(batch_leaves, attributes=['rep_coord_nm'])
      with lock:
        all_coords.update(batch_coords)
        nonlocal processed_batches
        processed_batches += 1
        callback(f'MSG:IN_PROGRESS:Processed {processed_batches} of {total_batches} batches of leaves')
    except Exception as e:
      callback(f'MSG:ERROR:Error processing batch {batch_num}: {str(e)}')
    return batch_num

  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {
      executor.submit(process_l2_batch, batch_num, sampled_leaves[i:i + BATCH_SIZE]): batch_num 
      for batch_num, i in enumerate(range(0, len(sampled_leaves), BATCH_SIZE), 1)
    }
    
    # Wait for all futures to complete
    for future in as_completed(futures):
      try:
        future.result()
      except Exception as e:
        callback(f'MSG:ERROR:Error in batch {futures[future]}: {str(e)}')

  callback('MSG:IN_PROGRESS:Rearranging coords...')
  # Build DataFrame from coords
  df = pd.DataFrame.from_dict(all_coords, orient='index')
  df['id'] = df.index # keep as string to avoid OverflowError
  df[['x', 'y', 'z']] = pd.DataFrame(df['rep_coord_nm'].tolist(), index=df.index)

  # Filter for valid rows (rep_coord_nm present and length 3)
  df_valid = df[df['rep_coord_nm'].apply(lambda v: isinstance(v, list) and len(v) == 3)]

  plane_defs = []
  planes_list = planes.splitlines()
  for plane in planes_list:
    plane_split = re.split(r';\s*', plane)
    p1_unscaled = np.array([float(x) for x in re.split(r',\s*', plane_split[0])])
    p2_unscaled = np.array([float(x) for x in re.split(r',\s*', plane_split[1])])
    p3_unscaled = np.array([float(x) for x in re.split(r',\s*', plane_split[2])])
    v1 = p2_unscaled - p1_unscaled
    v2 = p3_unscaled - p1_unscaled
    normal_unscaled = np.cross(v1, v2)
    scaling_factors = np.array([4, 4, 45])
    normal = normal_unscaled / scaling_factors
    normal = normal / np.linalg.norm(normal)
    p1 = p1_unscaled * scaling_factors
    plane_defs.append({'normal': normal, 'p1': p1})

  inside_source_ids = []
  outside_source_ids = []

  callback('MSG:IN_PROGRESS:Pre-computing valid leaf coordinates...')
  # Pre-compute all valid leaf coordinates for faster lookup
  # Convert DataFrame to dictionary first for faster lookups
  coords_dict = {
    str(idx): row[['x', 'y', 'z']].values 
    for idx, row in df_valid.iterrows()
  }
  
  # Create valid_coords dictionary using the pre-computed coords_dict
  valid_coords = {
    str(leaf_id): coords_dict[str(leaf_id)]
    for leaf_id in set().union(*source_to_leaves.values())
    if str(leaf_id) in coords_dict
  }

  callback('MSG:IN_PROGRESS:Checking leaves against planes...')
  # Process all eligible source IDs in parallel
  with ThreadPoolExecutor(max_workers=10) as executor:
    def process_source(source_id, leaf_list):
      if not leaf_list:
        return source_id, False
      # Get coordinates for all leaves in this source that have valid coordinates
      leaf_coords = [valid_coords[str(leaf_id)] for leaf_id in leaf_list if str(leaf_id) in valid_coords]
      if not leaf_coords:
        return source_id, False
      leaf_coords_array = np.array(leaf_coords)
      for plane in plane_defs:
        sides = np.dot(leaf_coords_array - plane['p1'], plane['normal'])
        if not np.all(sides >= 0):
          return source_id, False
      return source_id, True

    futures = [executor.submit(process_source, source_id, leaf_list) 
              for source_id, leaf_list in source_to_leaves.items()]

    for future in as_completed(futures):
      source_id, is_inside = future.result()
      if is_inside:
        inside_source_ids.append(source_id)
      else:
        outside_source_ids.append(source_id)
  callback({'inside': inside_source_ids, 'outside': outside_source_ids})
  return

def get_leaves(seg_ids):
  url = f'https://cave.fanc-fly.com/segmentation/api/v1/table/wclee_fly_cns_001/node/leaves_many?stop_layer=2'
  headers = {
    'Content-Type': 'application/json',
    'Accept-Encoding': 'zstd',
    'Authorization': f'Bearer {API_TOKEN}',
    'Cookie': f'middle_auth_token={API_TOKEN}'
  }
  data = json.dumps({"node_ids": seg_ids})

  response = post(url, data=data, headers=headers, timeout=10)
  if response.status_code == 200:
    return response.json()
