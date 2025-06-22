__all__ = ['filter_by_planes']

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

def filter_by_planes(source_ids, planes, thresholds, callback):
  threading.Thread(target=lambda: filter_by_planes_request(source_ids, planes, thresholds, callback), daemon=True).start()

def filter_by_planes_request(source_ids, planes, thresholds, callback):
  client = CAVEclient('brain_and_nerve_cord')
  segid_to_leaves = {}
  lock = threading.Lock()
  total = len(source_ids)
  processed = 0
  
  def get_leaves_worker(seg_ids):
    try:
      leaves = get_leaves(seg_ids)
      if leaves:
        return leaves
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

  # Categorize source_ids based on number of leaves
  smaller_threshold, larger_threshold = thresholds
  smaller_source_ids = []
  middle_source_ids = []
  larger_source_ids = []
  
  # Collect leaf count data for histogram
  leaf_counts = []

  for source_id, leaf_list in segid_to_leaves.items():
    num_leaves = len(leaf_list)
    leaf_counts.append(num_leaves)
    if num_leaves < smaller_threshold:
      smaller_source_ids.append(source_id)
    elif num_leaves > larger_threshold:
      larger_source_ids.append(source_id)
    else:
      middle_source_ids.append(source_id)

  # If no planes specified, return all results immediately
  if not planes or not planes.strip():
    callback({
      'smaller': smaller_source_ids,
      'middle': middle_source_ids,
      'larger': larger_source_ids,
      'leaf_counts': leaf_counts
    })
    return

  # Only process middle_source_ids against planes
  callback('MSG:IN_PROGRESS:Getting L2 centroids...')
  # Sample every 5th leaf to optimize processing
  sampled_leaves = []
  for source_id in middle_source_ids:
    leaf_list = segid_to_leaves[source_id]
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

  inside_middle_ids = []
  outside_middle_ids = []

  callback('MSG:IN_PROGRESS:Pre-computing valid leaf coordinates...')
  # Pre-compute all valid leaf coordinates for faster lookup
  coords_dict = {
    str(idx): row[['x', 'y', 'z']].values 
    for idx, row in df_valid.iterrows()
  }
  
  # Create valid_coords dictionary using the pre-computed coords_dict
  valid_coords = {
    str(leaf_id): coords_dict[str(leaf_id)]
    for leaf_id in set().union(*[segid_to_leaves[source_id] for source_id in middle_source_ids])
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

    futures = [executor.submit(process_source, source_id, segid_to_leaves[source_id]) 
              for source_id in middle_source_ids]

    for future in as_completed(futures):
      source_id, is_inside = future.result()
      if is_inside:
        inside_middle_ids.append(source_id)
      else:
        outside_middle_ids.append(source_id)

  callback({
    'smaller': smaller_source_ids,
    'middle': inside_middle_ids,
    'larger': larger_source_ids,
    'leaf_counts': leaf_counts
  })
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
