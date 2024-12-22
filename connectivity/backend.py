__all__ = ['get_clusters']

import threading
from utils.backend import *
from find_annotated.backend import get_entries
from get_synaptic_partners.backend import get_synaptic_partners
import numpy as np
import pyperclip


def get_clusters(input_ids, callback):
  threading.Thread(target=lambda: get_clusters_thread(input_ids, callback), daemon=True).start()

def get_clusters_thread(input_ids, callback):
  tags = []
  root_ids = []

  i = 0
  def replace_with_tags(row):
    nonlocal tags
    nonlocal root_ids
    nonlocal i
    if i == 0:
      print(root_ids)
      i = 1
    try:
      # Find index of post_pt_root_id in root_ids
      idx = np.where(root_ids == row['pre_pt_root_id'])[0]
      if idx.size > 0:
        print('found')
        print(idx)
        return tags[idx[0]]  # Replace with corresponding tag
    except:
        pass
    return 'Other'  # Keep original if not found


  def group(synapses):
    if not (isinstance(synapses, str) and synapses.startswith('MSG:')) and not synapses.empty:
      #TODO: zastanowić się, co zrobić z nieotypowanymi segmentami (łączyć, pominąć, analizować w grupowaniu?, co jeśli segment nie ma żadnych oznaczonych partnerów?)
      synapses.drop(
        columns=[
          'id',
          'created',
          'superceded_id',
          'valid',
          'pre_pt_supervoxel_id',
          'post_pt_supervoxel_id',
          'pre_pt_position',
          'post_pt_position',
          'ctr_pt_position'
        ],
        inplace=True
      )
      synapses['pre_pt_root_id'] = synapses['pre_pt_root_id'].astype(np.int64)
      synapses['post_pt_root_id'] = synapses['post_pt_root_id'].astype(np.int64)
      synapses['pre_pt_root_id'] = synapses.apply(replace_with_tags, axis=1)

    # Step 2: Group by `pre_pt_root_id` and `post_pt_root_id` to sum `size`
      synapses_grouped = (
        synapses
        .groupby(['pre_pt_root_id', 'post_pt_root_id'], as_index=False)
        .agg({'size': 'sum'})
      )

      # Step 3: Create the custom structure
      result = []
      for pre_pt_root_id, group in synapses_grouped.groupby('post_pt_root_id'):
        row = {
          'id': pre_pt_root_id,
          'partners': group[['pre_pt_root_id', 'size']].values.tolist()
        }
        result.append(row)

      # Output the result
      pyperclip.copy(result)
      #print(result)

  def get_partners():
    nonlocal input_ids
    callback('MSG:Getting synaptic partners...')
    input_ids = clean_input(input_ids)
    get_synaptic_partners(input_ids, group, return_complete_data=True)

  def process_entries(entries):
    nonlocal tags
    nonlocal root_ids
    if not isinstance(entries, str):
      tags = np.array(entries['tag'].values)
      root_ids = np.array(entries['pt_root_id'].values)
      unwanted_tags = np.array([
        'sensory neuron', 'chordotonal neuron', 'Johnston\'s organ neuron', 'club chordotonal neuron',
        'claw chordotonal neuron', 'hook chordotonal neuron', 'bristle mechanosensory neuron',
        'bristle mechanosensory neuron at gustatory sensillum', 'hair plate neuron', 'campaniform sensillum neuron',
        'olfactory receptor neuron', 'gustatory neuron', 'thermosensory neuron', 'hygrosensory neuron',
        'central neuron', 'optic lobe intrinsic', 'visual projection', 'visual centrifugal', 'central brain intrinsic',
        'VNC intrinsic', 'efferent', 'motor neuron', 'UM neuron', 'endocrine',
        'glia', 'trachea', 'astrocyte', 'cortex glia', 'ensheathing glia', 'perineural glia', 'subperineural glia',
        'cholinergic', 'GABAergic', 'glutamatergic', 'dopaminergic', 'histaminergic', 'octopaminergic', 'serotonergic',
        'tyraminergic',
        'soma on left', 'soma on midline', 'soma on right', 'soma in brain', 'soma in central brain',
        'soma in optic lobe', 'soma in VNC', 'soma in T1', 'soma in T2', 'soma in T3', 'soma in abdominal ganglion',
        'descending', 'ascending',
        'unilateral', 'bilateral', 'midplane',
        'innervates antenna', 'innervates maxillary palp', 'innervates proboscis', 'innervates retina',
        'innervates ocelli', 'innervates neck', 'innervates corpus cardiacum', 'innervates corpus allatum',
        'innervates leg', 'innervates T1 leg', 'innervates T2 leg', 'innervates T3 leg',
        'innervates thorax', 'innervates thorax-coxa joint', 'innervates coxa', 'innervates coxa-trochanter joint',
        'innervates trochanter', 'innervates femur', 'innervates femur-tibia joint', 'innervates tibia',
        'innervates tarsus', 'innervates wing', 'innervates haltere', 'innervates spiracle', 'innervates abdomen',
        'innervates tergopleural promotor', 'innervates pleural promotor', 'innervates pleural remotor and abductor',
        'innervates sternal anterior rotator', 'innervates sternal posterior rotator', 'innervates sternal adductor',
        'innervates tergotrochanter extensor', 'innervates sternotrochanter extensor', 'innervates trochanter extensor',
        'innervates trochanter flexor', 'innervates accessory trochanter flexor', 'innervates femur reductor',
        'innervates tibia extensor', 'innervates tibia flexor', 'innervates accessory tibia flexor',
        'innervates tarsus depressor', 'innervates tarsus retro depressor', 'innervates tarsus levator',
        'innervates long tendon muscle', 'innervates long tendon muscle 1', 'innervates long tendon muscle 2',
        'innervates dorsal longitudinal muscle', 'innervates dorsoventral muscle', 'innervates wing steering muscle',
        'innervates wing tension muscle', 'innervates indirect flight muscle',
        'centrifugal', 'distal medulla', 'distal medulla dorsal rim area',
        'lamina intrinsic', 'lamina monopolar', 'lamina tangential', 'lamina wide field',
        'lobula intrinsic', 'lobula lobula plate tangential', 'lobula medulla amacrine', 'lobula medulla tangential',
        'lobula plate intrinsic', 'medulla intrinsic', 'medulla lobula lobula plate amacrine',
        'medulla lobula tangential', 'photoreceptors', 'proximal distal medulla tangential', 'proximal medulla',
        'serpentine medulla', 'T neuron', 'translobula plate', 'transmedullary', 'transmedullary Y', 'Y neuron'
      ])

      # Create a mask for tags not in unwanted_tags
      mask = ~np.isin(tags, unwanted_tags)

      # Filter tags and root_ids based on the mask
      tags = tags[mask]
      root_ids = root_ids[mask].astype(np.int64)
      get_partners()

  get_entries('cell_info', process_entries, return_result=True)
