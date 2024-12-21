__all__ = ['get_synaptic_partners', 'get_partners_of_partners', 'get_common_of_common', 'filter_dust']

import threading
from api_token import API_TOKEN
from caveclient import CAVEclient
import pandas as pd
import time
from collections import Counter



all_partners_ids = []

def get_synaptic_partners(source_ids, callback, return_complete_data=False):
  threading.Thread(target=lambda: get_synaptic_partners_request(source_ids, callback, return_complete_data), daemon=True).start()

def get_synaptic_partners_request(source_ids, callback, return_complete_data=False):
  try:
    # Initialize the CAVE client with your token
    client = CAVEclient(
        datastack_name='brain_and_nerve_cord',
        auth_token=API_TOKEN  # Use your existing API_TOKEN
    )
    
    # Process in batches of 50
    BATCH_SIZE = 50
    all_ids = []
    total_batches = (len(source_ids) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(source_ids), BATCH_SIZE):
      batch = source_ids[i:i+BATCH_SIZE]
      current_batch = (i // BATCH_SIZE) + 1
      
      # Update progress with prefix to prevent splitting
      callback(f"MSG:IN_PROGRESS:Processing batch {current_batch} of {total_batches}...")
      
      # Query this batch
      batch_ids = client.materialize.synapse_query(pre_ids=batch, post_ids=batch)
      all_ids.append(batch_ids)

    # Combine all results
    if len(all_ids) > 0:
      ids = pd.concat(all_ids, ignore_index=True)
      if (return_complete_data):
         return callback(ids)
      pd.set_option("display.max_columns", None) #temp
      #print(ids.head()) #temp
      # Extract post_pt_root_ids
      post_ids = set(ids['post_pt_root_id'].unique())
      
      # Store all partners including duplicates in global variable  
      global all_partners_ids
      all_partners_ids = ids['post_pt_root_id'].tolist()
      
      # Send completion message before results
      callback("MSG:COMPLETE:Processing complete")
      callback(sorted(post_ids))
    else:
      callback("MSG:COMPLETE:No results found")
      callback([])

  except Exception as e:
    print(f"Full error: {str(e)}")
    callback(f'MSG:ERROR:Error: {str(e)}')

def get_partners_of_partners(num_of_partners, callback, partners_ids):
  threading.Thread(target=lambda: get_partners_of_partners_request(num_of_partners, callback, partners_ids), daemon=True).start()

def get_partners_of_partners_request(num_of_partners, callback, partners_ids):
  global all_partners_ids
  try:
    # Count occurrences of each id in source_ids
    id_counts = {}
    if not len(all_partners_ids):
      all_partners_ids = partners_ids

    for id in all_partners_ids:
      id_counts[id] = id_counts.get(id, 0) + 1
    # Sort by count and get top num_of_partners
    try:
      num_partners = int(num_of_partners)
    except:
      num_partners = 50  # Default if invalid input
      
    most_common = sorted(id_counts.items(), key=lambda x: x[1], reverse=True)[:num_partners]
    most_common_ids = [id for id, count in most_common]

    # Get partners of the most common partners
    get_synaptic_partners(most_common_ids, callback)

  except Exception as e:
    print(e.with_traceback())
    callback(f'Error: {str(e)}')

def get_common_of_common(source_ids, x=20):
    # Count occurrences of each id in all_partners_ids
    id_counts = Counter(all_partners_ids)
    # Filter out IDs that appear more than x times and are not in source_ids
    repeated_partners = [id for id, count in id_counts.items() if count > x and id not in source_ids]
    return repeated_partners

def filter_dust(source_ids, max_size, callback):
  """
  Filter out 'dust' segments by checking fragment counts.
  
  Args:
      source_ids: List of segment IDs to check
      max_size: Maximum number of fragments to consider as dust
      callback: Callback function to report progress and results
  """
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
                    print(f"Timeout occurred. Retry attempt {retries}/5 for batch")
                    if retries == 5:
                        raise Exception("Max retries reached after timeout for batch")
                    time.sleep(0.5)  # Wait 1 second before retrying

        # Process each batch sequentially
        for i in range(0, len(source_ids), BATCH_SIZE):
            batch = source_ids[i:i + BATCH_SIZE]
            batch_results = process_batch(batch)
            results.extend(batch_results)
            processed += len(batch)
            callback(f"MSG:IN_PROGRESS:Processed {processed}/{total} IDs. Kept {len(results)} IDs so far.")

        callback(f"MSG:COMPLETE:Completed processing {total} segments")
        callback(sorted(results))
        
    except Exception as e:
        print(f"Full error: {str(e)}")
        callback(f"MSG:ERROR:Error: {str(e)}")
