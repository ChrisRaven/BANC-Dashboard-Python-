__all__ = ['get_synaptic_partners', 'get_partners_of_partners', 'get_common_of_common', 'filter_dust']

import threading
from api_token import API_TOKEN
from caveclient import CAVEclient
import pandas as pd
import time
from collections import Counter


all_partners_ids = []

upstream_partners = pd.Series()
downstream_partners = pd.Series()

def get_synaptic_partners(source_ids, callback, direction='downstream', return_complete_data=False, save_globally=True):
  threading.Thread(target=lambda: get_synaptic_partners_request(
    source_ids,
    callback,
    direction,
    return_complete_data,
    save_globally,
  ), daemon=True).start()

def get_synaptic_partners_request(source_ids, callback, direction='downstream', return_complete_data=False, save_globally=True):
  global upstream_partners
  global downstream_partners
  downstream = []
  upstream = []
  if save_globally:
    upstream_partners = pd.Series()
    downstream_partners = pd.Series()
  try:
    client = CAVEclient(datastack_name='brain_and_nerve_cord', auth_token=API_TOKEN)
    BATCH_SIZE = 50

    total_batches = (len(source_ids) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(source_ids), BATCH_SIZE):
      batch = source_ids[i:i+BATCH_SIZE]
      current_batch = (i // BATCH_SIZE) + 1
      # Update progress with prefix to prevent splitting
      callback(f'MSG:IN_PROGRESS:Processing batch {current_batch} of {total_batches}...')

      if direction == 'downstream' or direction == 'both':
        downstream.append(client.materialize.synapse_query(pre_ids=batch))
      if direction == 'upstream' or direction == 'both':
        upstream.append(client.materialize.synapse_query(post_ids=batch))

    if downstream or upstream:
      if downstream:
        downstream = pd.concat(downstream, ignore_index=True)['post_pt_root_id']
      if upstream:
        upstream = pd.concat(upstream, ignore_index=True)['pre_pt_root_id']

      if save_globally:
        upstream_partners = upstream
        downstream_partners = downstream

      unique_ids = set(upstream) | set(downstream)
      if return_complete_data:
        return callback(list(unique_ids))

      callback(sorted(unique_ids))
    else:
      callback('MSG:COMPLETE:No results found')

  except Exception as e:
    callback(f'MSG:ERROR:Error: {repr(e)}')

def get_partners_of_partners(num_of_partners, callback):
  threading.Thread(target=lambda: get_partners_of_partners_request(
    num_of_partners,
    callback
  ), daemon=True).start()

def get_partners_of_partners_request(num_of_partners, callback):
  global upstream_partners
  global downstream_partners

  def get_n_most_common(n, items):
    return [id for id, _ in Counter(items).most_common(int(n))]

  try:
    most_common_upstream = []
    most_common_downstream = []
    if isinstance(upstream_partners, pd.core.series.Series) and not upstream_partners.empty:
      most_common_upstream = get_n_most_common(num_of_partners, upstream_partners)
    if isinstance(downstream_partners, pd.core.series.Series) and not downstream_partners.empty:
      most_common_downstream = get_n_most_common(num_of_partners, downstream_partners)

    def local_callback(result):
      if isinstance(result, str) and result.startswith('MSG:'):
        callback(result)
      else:
        local_callback.result.extend(result)
        local_callback.call_count += 1
      if local_callback.call_count == local_callback.expected_calls:
        callback(local_callback.result)

    local_callback.call_count = 0
    local_callback.expected_calls = 2 if most_common_upstream and most_common_downstream else 1
    local_callback.result = []

    if most_common_upstream:
      get_synaptic_partners(most_common_upstream, local_callback, save_globally=False, direction='downstream')
    if most_common_downstream:
      get_synaptic_partners(most_common_downstream, local_callback, save_globally=False, direction='upstream')
  except Exception as e:
    callback(f'Error2: {str(e)}')












def get_common_of_common(source_ids, x=20):
  id_counts = Counter(all_partners_ids)
  repeated_partners = [id for id, count in id_counts.items() if count > x and id not in source_ids]
  return repeated_partners

def filter_dust(source_ids, max_size, callback):
  threading.Thread(target=lambda: filter_dust_request(source_ids, max_size, callback), daemon=True).start()

def filter_dust_request(source_ids, max_size, callback):
  try:
    client = CAVEclient('brain_and_nerve_cord', auth_token=API_TOKEN)
    
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
            if total_synapses > max_size:
              batch_results.append(seg_id)
        
          return batch_results

        except TimeoutError:
          retries += 1
          print(f'Timeout occurred. Retry attempt {retries}/5 for batch')
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
    print(f'Full error: {str(e)}')
    callback(f'MSG:ERROR:Error: {str(e)}')
