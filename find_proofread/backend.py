__all__ = ['get_proofread']

import threading
import requests
import pyarrow as pa

from api_token import API_TOKEN
from datetime import datetime

def get_proofread(source_ids, callback):
    threading.Thread(target=lambda: get_proofread_request(source_ids, callback), daemon=True).start()

def get_proofread_request(source_ids, callback):
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
            'Accept-Encoding': 'gzip',
            'Authorization': f'Bearer {API_TOKEN}',
            'Cookie': f'middle_auth_token={API_TOKEN}'
        }
        
        data = {
            "table": "backbone_proofread",
            "timestamp": datetime.now().isoformat()
        }

        response = requests.post(url, params=params, headers=headers, json=data)
        
        # Read arrow data from response
        arrow_data = pa.BufferReader(response.content)
        table = pa.ipc.open_stream(arrow_data).read_all()
        
        # Extract proofread IDs from column index 10 (like in JS code)
        proofread_ids = table.column(10).to_pylist()
        
        # Find common and unique IDs
        proofread_set = set(proofread_ids)
        source_set = set(source_ids)
        
        # IDs that appear in both sets (proofread)
        common = list(source_set & proofread_set)
        
        # IDs that only appear in source (not proofread) 
        only_in_source = list(source_set - proofread_set)
        
        callback(common, only_in_source)

    except Exception as e:
        print(f"Error: {e}")
        callback([], [])
