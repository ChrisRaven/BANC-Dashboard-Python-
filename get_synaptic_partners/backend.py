__all__ = ['get_synaptic_partners', 'get_partners_of_partners', 'get_most_common', 'filter_dust']

''' SP == Synaptic Partners '''

import pandas as pd
from caveclient import CAVEclient
from collections import Counter
import threading
from api_token import API_TOKEN
from constants import *
from functools import partial
import time


data = {
  'partners': {
    'upstream': pd.DataFrame(),
    'downstream': pd.DataFrame(),
  },
  'partners_of_partners': {
    'upstream': pd.DataFrame(),
    'downstream': pd.DataFrame()
  },
  'direction': ''
}

def get_synaptic_partners(source_ids, callback, direction='downstream'):
  threading.Thread(target=lambda: _get_SP_thread(source_ids, callback, direction=direction), daemon=True).start()


def _get_SP_thread(source_ids, callback, direction='downstream'):
  try:
    data['direction'] = direction


    def local_callback(result, local_direction):
      if not result['status'] == Status.FINISHED: return callback(result)
      if isinstance(result['content'], str): return callback(result)

      if local_direction == 'upstream':
        data['partners']['upstream'] = result['content']
      elif local_direction == 'downstream':
        data['partners']['downstream'] = result['content']
      else: return False

      local_callback.executed_calls += 1
      if local_callback.executed_calls == local_callback.expected_calls:
        upstream = set(data['partners']['upstream'])
        downstream = set(data['partners']['downstream'])

        final_result = set()
        match direction:
          case 'upstream':
            final_result = upstream
          case 'downstream':
            final_result = downstream
          case 'both':
            final_result = upstream | downstream

        callback({
          'status': Status.FINISHED,
          'content': sorted(final_result)
        })

    local_callback.expected_calls = 2 if direction == 'both' else 1
    local_callback.executed_calls = 0

    if direction == 'downstream' or direction == 'both':
      bound_callback = partial(local_callback, local_direction='downstream')
      _get_directional_SP(source_ids, callback=bound_callback , direction='downstream')
    if direction == 'upstream' or direction == 'both':
      bound_callback = partial(local_callback, local_direction='upstream')
      _get_directional_SP(source_ids, callback=bound_callback, direction='upstream')

  except Exception as e:
    callback({
      'status': Status.ERROR,
      'content': f'Error: {repr(e)}'
    })


def _get_directional_SP(source_ids, callback, direction):
  try:
    client = CAVEclient(datastack_name='brain_and_nerve_cord', auth_token=API_TOKEN)
    BATCH_SIZE = 50
    key_query = 'pre_ids' if direction == 'downstream' else 'post_ids'
    key_result = 'post_pt_root_id' if direction == 'downstream' else 'pre_pt_root_id'
    result = pd.DataFrame()
    total_batches = (len(source_ids) + BATCH_SIZE - 1) // BATCH_SIZE
    for batch_index, i in enumerate(range(0, len(source_ids), BATCH_SIZE), start=1):
      batch = source_ids[i:i + BATCH_SIZE]
      callback({
        'status': Status.IN_PROGRESS,
        'content': f'Processing batch {batch_index} of {total_batches} ({direction})...'
      })
      result = pd.concat([result, client.materialize.synapse_query(**{key_query: batch})], ignore_index=True)
    if not result.empty:
      unique_ids = result[key_result]
      callback({
        'status': Status.FINISHED,
        'content': unique_ids
      })
    else:
      callback({
        'status': Status.FINISHED,
        'content': 'No results found',
      })
  except Exception as e:
    callback({
      'status': Status.ERROR,
      'content': f'Error: {repr(e)}'
    })


def get_partners_of_partners(num_of_partners, callback):
  old_direction = data['direction']
  
  new_direction = None
  match old_direction:
    case 'both':
      new_direction = 'both'
    case 'upstream':
      new_direction = 'downstream'
    case 'downstream':
      new_direction = 'upstream'

  if not new_direction:
    callback({
      'status': Status.ERROR,
      'content': 'You have to have original partners first ("Get partners" button, above)'
    })
    return None
  
  # this callback only combines the final result
  def local_callback(result):
    if not result['status'] == Status.FINISHED: return callback(result)
    if isinstance(result['content'], str): return callback(result)

    local_callback.executed_calls += 1
    if local_callback.executed_calls == local_callback.expected_calls:
      upstream = set(data['partners_of_partners']['upstream'])
      downstream = set(data['partners_of_partners']['downstream'])
      final_result = set()
      match new_direction:
        case 'upstream':
          final_result = upstream
        case 'downstream':
          final_result = downstream
        case 'both':
          final_result = upstream | downstream
      callback({
        'status': Status.FINISHED,
        'content': sorted(final_result)
      })

  local_callback.expected_calls = 2 if new_direction == 'both' else 1
  local_callback.executed_calls = 0

  if new_direction == 'both':
    threading.Thread(target=lambda: _get_partners_of_partners_request(num_of_partners, local_callback, 'downstream'), daemon=True).start()
    threading.Thread(target=lambda: _get_partners_of_partners_request(num_of_partners, local_callback, 'upstream'), daemon=True).start()
  else:
    threading.Thread(target=lambda: _get_partners_of_partners_request(num_of_partners, local_callback, new_direction), daemon=True).start()


def _get_partners_of_partners_request(num_of_partners, callback, direction):
  starting_direction = 'upstream' if direction == 'downstream' else 'downstream'
  try:
    partners = data['partners'][starting_direction]
    if partners.empty:
      callback({
        'status': Status.FINISHED,
        'content': 'No results found'
      })
      return None
        
    def get_n_most_common(n, items):
      return [id for id, _ in Counter(items).most_common(int(n))]
    
    # this callback stores the result and calls the callback from get_partners_of_partners()
    def local_callback(result):
      if not result['status'] == Status.FINISHED: return callback(result)
      if isinstance(result['content'], str): return callback(result)

      data['partners_of_partners'][direction] = result['content']
      callback(result)

    most_common = get_n_most_common(num_of_partners, partners)
    _get_directional_SP(most_common, local_callback, direction)

  except Exception as e:
    callback({
      'status': Status.ERROR,
      'content': f'Error2: {str(e)}'
    })


def get_most_common(source_group, num_of_most_common_partners=50):
  key = 'partners' if source_group == 'partners' else 'partners_of_partners'
  source = data[key]
  direction = data['direction']

  if direction == 'both':
    to_be_counted = pd.concat([source['upstream'], source['downstream']], ignore_index=True).values.flatten().tolist()
  else:
    to_be_counted = source[direction].values.flatten().tolist()

  most_common_entries = Counter(to_be_counted).most_common(num_of_most_common_partners)
  most_common_ids = [element for element, count in most_common_entries]

  return most_common_ids


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