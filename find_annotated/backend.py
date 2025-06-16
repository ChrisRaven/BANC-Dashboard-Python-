__all__ = ['get_entries', 'find_annotated', 'get_user_annotation_counts']

import pandas as pd
import pyarrow as pa
import numpy as np
import threading
import requests
import json

from api_token import API_TOKEN
from datetime import datetime
from utils.backend import *


entries_result = None

def get_entries(table_name, callback, return_result=False):
  threading.Thread(target=lambda: make_request(table_name, callback, return_result), daemon=True).start()

def make_request(table_name, callback, return_result=False):
  global entries_result
  try:
    url = 'https://cave.fanc-fly.com/materialize/api/v3/datastack/brain_and_nerve_cord/query'
    params = {
      'return_pyarrow': 'True',
      'arrow_format': 'True', 
      'merge_reference': 'False',
      'allow_missing_lookups': 'False',
      'allow_invalid_root_ids': 'False'
    }
    
    headers = {
      'Content-Type': 'application/json',
      'Accept-Encoding': 'zstd',
      'Authorization': f'Bearer {API_TOKEN}',
      'Cookie': f'middle_auth_token={API_TOKEN}'
    }
    
    data = {
      'table': table_name,
      'timestamp': datetime.now().isoformat()
    }
    # copy "backbone proofread" to the clipboard
    #data = {
    #  'table': 'backbone_proofread',
    #  'timestamp': datetime.now().isoformat()
    #}
    
    response = requests.post(url, params=params, headers=headers, json=data)
    content_type = response.headers.get('Content-Type', '')

    if 'application/json' in content_type:
      try:
        json_data = response.json()
        callback(json_data['message'])
      except json.JSONDecodeError:
        callback('ERR:Error decoding JSON')
    else:
      try:
        arrow_data = pa.BufferReader(response.content)
        entries_result = pa.ipc.open_stream(arrow_data).read_all().to_pandas()
        #pd.set_option('display.max_columns', None)
        #print(entries_result)
        # copy "backbone proofread" to the clipboard
        #entries_result[['pt_position_x', 'pt_root_id']].to_clipboard(index=False, sep=', ')
        #entries_result[entries_result['pt_position_x'] < 80000]['pt_root_id'].to_clipboard(index=False)
        if return_result:
          callback(entries_result)
      except Exception as e:
        callback('ERR:Error decoding Arrow data')
  except Exception as e:
    callback('ERR:' + e)
  finally:
    if not return_result:
      callback(len(entries_result) if isinstance(entries_result, pd.DataFrame) else '')


def get_user_annotation_counts(callback):
  threading.Thread(target=lambda: get_user_annotation_counts_thread(callback), daemon=True).start()

def get_user_annotation_counts_thread(callback):
  try:
    # Count tag annotations (excluding empty/null)
    tag_counts = entries_result[entries_result['tag'].notna()].groupby('user_id').size().sort_values(ascending=False)

    # Format results as string
    results = []
    for user_id, count in tag_counts.items():
      results.append(f"User {user_id}: {count} annotations")
      
    callback('\n'.join(results))
    
  except Exception as e:
    callback(f'ERR: {str(e)}')


def find_annotated(search_text, callback):
  threading.Thread(target=lambda: find_annotated_thread(search_text, callback), daemon=True).start()

def find_annotated_thread(search_text, callback):
  if not search_text:
    callback([]) # Return empty list if search is empty
    return

  search_text = search_text.strip() # Trim overall search text
  matching_rows = []

  # Access the globally loaded or cached data
  # Ensure entries_result is a DataFrame and accessible here
  if 'entries_result' not in globals() or entries_result is None:
      print("Error: entries_result DataFrame not loaded.")
      callback([])
      return

  tags = entries_result['tag'] # Access as pandas Series for string methods
  root_ids = entries_result['pt_root_id'].values

  # Check for special prefixes
  if search_text.startswith("STARTS_WITH:"):
    phrase = search_text[len("STARTS_WITH:"):].strip()
    if phrase: # Only search if phrase is not empty
      mask = tags.str.startswith(phrase, na=False)
      matching_rows.extend(root_ids[mask])

  elif search_text.startswith("ENDS_WITH:"):
    phrase = search_text[len("ENDS_WITH:"):].strip()
    if phrase:
      mask = tags.str.endswith(phrase, na=False)
      matching_rows.extend(root_ids[mask])

  elif search_text.startswith("CONTAINS:"):
    phrase = search_text[len("CONTAINS:"):].strip()
    if phrase:
      mask = tags.str.contains(phrase, na=False, regex=False) # Use regex=False for literal contains
      matching_rows.extend(root_ids[mask])

  else:
    # --- Original exact match logic (modified slightly for clarity) ---
    search_terms = set(clean_input(search_text, output_type=str))
    if not search_terms: # Handle case where clean_input results in empty set
        callback([])
        return
        
    # Vectorized check for exact tag matches
    # Ensure tags is treated as strings for isin if necessary
    tag_matches = tags.astype(str).isin(list(search_terms))
    matching_rows.extend(root_ids[tag_matches])

    # Check tag2s (only in exact match mode)
    tag2s = entries_result['tag2'] # Access as Series
    valid_tag2s_mask = pd.notna(tag2s)
    
    if valid_tag2s_mask.any():
        # Apply split and check only on valid tag2s
        tag2s_to_check = tag2s[valid_tag2s_mask].astype(str)
        # Efficiently check if any search term is in the split tag2 words
        tag2_match_flags = tag2s_to_check.str.split(expand=True).isin(list(search_terms)).any(axis=1)
        # Get the root_ids corresponding to these matches
        matched_tag2_root_ids = root_ids[valid_tag2s_mask][tag2_match_flags]
        matching_rows.extend(matched_tag2_root_ids)

  # Remove duplicates before calling back
  unique_matching_rows = list(set(matching_rows))
  callback(unique_matching_rows)
