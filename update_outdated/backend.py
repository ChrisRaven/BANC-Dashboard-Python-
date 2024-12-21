__all__ = ['update_outdated']
from api_token import API_TOKEN
import threading

def update_outdated(ids, callback):
  threading.Thread(target=lambda: update_outdated_request(ids, callback), daemon=True).start()

def update_outdated_request(ids, callback):
  
  import requests
  from datetime import datetime, timezone

  # Get current timestamp in seconds
  current_timestamp = int(datetime.now(timezone.utc).timestamp())

  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_TOKEN}',
    'Cookie': f'middle_auth_token={API_TOKEN}'
  }

  # First request - check if roots are latest
  response = requests.post(
    "https://cave.fanc-fly.com/segmentation/api/v1/table/wclee_fly_cns_001/is_latest_roots",
    headers=headers,
    json={"node_ids": ids}
  )
  is_latest = response.json()["is_latest"]

  # Find outdated IDs
  outdated_ids = []
  for i, is_current in enumerate(is_latest):
    if not is_current:
      outdated_ids.append(ids[i])

  # Process each outdated ID
  all_latest_leaves = []
  for outdated_id in outdated_ids:
    # Get root timestamps
    response = requests.post(
      f"https://cave.fanc-fly.com/segmentation/api/v1/table/wclee_fly_cns_001/root_timestamps",
      headers=headers,
      params={"latest": "False", "timestamp": current_timestamp},
      json={"node_ids": [outdated_id]}
    )
    past_timestamp = response.json()["timestamp"][0]

    # Get lineage graph
    response = requests.post(
      "https://cave.fanc-fly.com/segmentation/api/v1/table/wclee_fly_cns_001/lineage_graph_multiple",
      headers=headers,
      json={
        "root_ids": [outdated_id],
        "timestamp_past": past_timestamp,
        "timestamp_future": current_timestamp
      }
    )
    graph_data = response.json()

    # Get latest leaves from graph
    nodes = graph_data["nodes"]
    links = graph_data["links"]
    
    # Find nodes without outgoing edges
    outgoing_nodes = set(link["source"] for link in links)
    leaves = [node for node in nodes if node["id"] not in outgoing_nodes]
    
    # Sort by timestamp descending and get IDs
    leaves.sort(key=lambda x: x["timestamp"], reverse=True)
    latest_leaves = [leaf["id"] for leaf in leaves]
    
    all_latest_leaves.extend(latest_leaves)

  # Remove outdated IDs from original list
  up_to_date_ids = list(set(ids) - set(outdated_ids))

  # Call callback with results
  callback(up_to_date_ids, all_latest_leaves)
