__all__ = ['get_synaptic_partners', 'get_partners_of_partners']

import requests
import pyarrow as pa
import threading
from api_token import API_TOKEN


all_partners_ids = []

def get_synaptic_partners(source_ids, callback):
  threading.Thread(target=lambda: get_synaptic_partners_request(source_ids, callback), daemon=True).start()

def get_synaptic_partners_request(source_ids, callback):
  try:
    response = requests.post(
      "https://cave.fanc-fly.com/materialize/api/v3/datastack/brain_and_nerve_cord/version/372/table/synapses_v1/query",
      params={
        "return_pyarrow": "True",
        "arrow_format": "True",
        "split_positions": "True"
      },
      headers={
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': f'Bearer {API_TOKEN}',
        'Cookie': f'middle_auth_token={API_TOKEN}'
      },
      json={
        "filter_in_dict": {
          "synapses_v1": {
            "pre_pt_root_id": source_ids
          }
        },
        "filter_equal_dict": {
          "synapses_v1": {}
        }
      }
    )

    # Convert response to pyarrow table
    buffer = pa.py_buffer(response.content)
    reader = pa.ipc.RecordBatchStreamReader(buffer)
    table = reader.read_all()
    # Extract unique post_pt_root_ids for callback
    post_ids = set()
    # Store all post_pt_root_ids including duplicates in global variable
    global all_partners_ids
    all_partners_ids = []
    for batch in table.to_batches():
        post_batch = batch.column('post_pt_root_id').to_pylist()
        post_ids.update(post_batch)
        all_partners_ids.extend(post_batch)
    
    callback(sorted(post_ids))

  except Exception as e:
    callback(f'Error: {str(e)}')

def get_partners_of_partners(num_of_partners, callback):
  threading.Thread(target=lambda: get_partners_of_partners_request(num_of_partners, callback), daemon=True).start()

def get_partners_of_partners_request(num_of_partners, callback):
  try:
    # Count occurrences of each id in source_ids
    id_counts = {}
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
    callback(f'Error: {str(e)}')
