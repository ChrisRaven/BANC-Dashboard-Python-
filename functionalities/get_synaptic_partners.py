__all__ = ['get_synaptic_partners', 'get_partners_of_partners']

import threading
from api_token import API_TOKEN
from caveclient import CAVEclient
import pandas as pd



all_partners_ids = []

def get_synaptic_partners(source_ids, callback):
  threading.Thread(target=lambda: get_synaptic_partners_request(source_ids, callback), daemon=True).start()

def get_synaptic_partners_request(source_ids, callback):
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
      batch_ids = client.materialize.synapse_query(pre_ids=batch)
      all_ids.append(batch_ids)
    
    # Combine all results
    if len(all_ids) > 0:
      ids = pd.concat(all_ids, ignore_index=True)
      
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
