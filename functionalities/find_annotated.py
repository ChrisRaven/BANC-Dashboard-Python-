__all__ = ['get_entries', 'find_annotated']

import pandas as pd
import pyarrow as pa
import numpy as np
import threading
import requests
import json

from api_token import API_TOKEN
from datetime import datetime
from common import *



entries_result = None


def get_entries(table_name, callback):
  """Start request in separate thread"""
  threading.Thread(target=lambda: make_request(table_name, callback), daemon=True).start()

def make_request(table_name, callback):
  """Make API request with error handling"""
  global entries_result
  try:
    url = "https://cave.fanc-fly.com/materialize/api/v3/datastack/brain_and_nerve_cord/query"
    params = {
      "return_pyarrow": "True",
      "arrow_format": "True", 
      "merge_reference": "False",
      "allow_missing_lookups": "False",
      "allow_invalid_root_ids": "False"
    }
    
    headers = {
      'Content-Type': 'application/json',
      'Accept-Encoding': 'zstd',
      'Authorization': f'Bearer {API_TOKEN}',
      'Cookie': f'middle_auth_token={API_TOKEN}'
    }
    
    data = {
      "table": table_name,
      "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(url, params=params, headers=headers, json=data)
    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
      # Response is JSON
      try:
        json_data = response.json()  # Parse JSON
        callback(json_data['message'])
      except json.JSONDecodeError:
        callback("Error decoding JSON")
    elif "application/vnd.apache.arrow" in content_type:
      # Response is Arrow
      try:
        arrow_data = pa.BufferReader(response.content)
        entries_result = pa.ipc.open_stream(arrow_data).read_all().to_pandas()
        print("Arrow Data:", entries_result)
      except Exception as e:
        callback("Error decoding Arrow data")

    
  except Exception as e:
    print(f"Error: {e}")
  finally:
    callback('')


def find_annotated(search_text, callback):
  threading.Thread(target=lambda: find_annotated_thread(search_text, callback), daemon=True).start()

def find_annotated_thread(search_text, callback):
  """Search functionality with improved matching"""
  
  if not search_text:
    return
    
  search_terms = set(clean_input(search_text, output_type=str))

  matching_rows = []
  # Convert to numpy arrays for faster operations
  tags = entries_result['tag'].values
  root_ids = entries_result['pt_root_id'].values
  tag2s = entries_result['tag2'].values
  copytext('\n'.join(map(str, root_ids)))
  # Vectorized check for tag matches
  tag_matches = np.isin(tags, list(search_terms))
  matching_rows.extend(root_ids[tag_matches])
  
  # Vectorized check for tag2 matches
  valid_tag2s = pd.notna(tag2s)
  if valid_tag2s.any():
    # Split and check tag2s only where they exist
    tag2_terms = [set(str(t).split()) if pd.notna(t) else set() for t in tag2s[valid_tag2s]]
    tag2_matches = [bool(t & search_terms) for t in tag2_terms]
    matching_rows.extend(root_ids[valid_tag2s][tag2_matches])
  
  callback(matching_rows)
