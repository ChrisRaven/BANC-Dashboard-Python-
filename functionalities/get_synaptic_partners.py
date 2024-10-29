from caveclient import CAVEclient
from datetime import datetime, timezone

def get_synaptic_partners(source_ids):
  client = CAVEclient(datastack_name = 'brain_and_nerve_cord')

  #source_ids = [ 720575941662397564,720575941642728530,720575941448136117 ]

  ids = client.materialize.synapse_query(pre_ids=source_ids)
  print('done')
  ids.to_clipboard(index=False, header=False, columns=['post_pt_root_id'], sep=',')
  return ids
