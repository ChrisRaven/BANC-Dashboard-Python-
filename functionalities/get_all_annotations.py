from caveclient import CAVEclient
import pyperclip

def get_all_annotations():
  client = CAVEclient(datastack_name = 'brain_and_nerve_cord')
  valid_ids = []
  batch_size = 500
  for x in range(250):
    ids = client.annotation.get_annotation('backbone_proofread', range(x * batch_size, (x + 1) * batch_size))
    valid_ids += [item['valid_id'] for item in ids if item['proofread']]
    print(x)

#print(valid_ids)

# source: https://stackoverflow.com/a/3590168
#pyperclip.copy('\r\n'.join(str(x) for x in valid_ids))
