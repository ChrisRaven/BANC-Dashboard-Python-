from caveclient import CAVEclient
from datetime import datetime, timezone

def update_outdated(ids):
  client = CAVEclient(datastack_name = 'brain_and_nerve_cord')

  #ids = [720575941505773381, 720575941459216595, 720575941592289899]

  print('searching for outdated ids...')
  checks = client.chunkedgraph.is_latest_roots(ids)

  outdated_ids = []

  for i in range(len(ids)):
      if not checks[i]:
          outdated_ids.append(ids[i])
          print(ids[i])

  updated_ids = []

  print('updating...')
  for outdated_id in outdated_ids:
      updated_id = client.chunkedgraph.get_latest_roots(outdated_id)
      updated_ids.extend(updated_id)
      print(updated_id)

  print('old minus changed')
  ids = list(set(ids) - set(outdated_ids))
  print(ids)

  print('changed')
  print(updated_ids)
