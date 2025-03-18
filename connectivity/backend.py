__all__ = ['get_clusters', 'recluster', 'get_nblast_clusters']

import threading
import meshparty.skeleton_io as mpsk
from utils.backend import *
from constants import *
from find_annotated.backend import get_entries
from get_synaptic_partners.backend import get_synaptic_partners
import numpy as np
from functools import partial
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster
from concurrent.futures import ThreadPoolExecutor
import banc
import pandas as pd
import banc
import navis
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


# Store the merged_partners data
_merged_partners_data = None

# Add this at the top with other global variables
_current_nblast_data = None
_current_partner_data = None

def get_clusters(input_ids, callback, eps=0.5):
  global _merged_partners_data, _current_partner_data
  
  def clustering_callback(result):
    # Force complete reclustering when button is clicked
    if input_ids is not None:
      _current_partner_data = None
    callback(result)

  if input_ids is None and _current_partner_data is not None:
    # Reclustering with existing data (slider movement)
    _perform_clustering(_current_partner_data['merged_partners'], callback, eps)
  else:
    # New clustering request or no cached data
    _merged_partners_data = None
    _current_partner_data = None
    threading.Thread(target=lambda: get_clusters_thread(input_ids, clustering_callback, eps), daemon=True).start()


def recluster(eps, callback):
  """Recluster using stored NBLAST data."""
  global _current_nblast_data
  if _current_nblast_data is not None:
    get_nblast_clusters(None, callback, eps)
  else:
    callback("MSG:No data available for reclustering. Please fetch clusters first.")

def group_by_types_of_partners(synapses, tags, root_ids, eps, callback):
  global _merged_partners_data, _current_partner_data
  if isinstance(synapses, str): return None
  if synapses['status'] != Status.FINISHED: return None
  if synapses['content']['upstream'].empty and synapses['content']['downstream'].empty: return None
  
  try:
    data = synapses['content']

    def switch_ids_to_tags(row, field, tags, root_ids):
      try:
        idx = np.where(root_ids == row[field])[0]
        if idx.size > 0:
          return tags[idx[0]]
      except:
        pass
      return 'Other'

    def create_groups(data, key, field1, field2):
      data[key].drop(
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
      data[key][field1] = data[key][field1].astype(np.int64)
      data[key][field2] = data[key][field2].astype(np.int64)
      data[key][field1] = data[key].apply(switch_ids_to_tags, axis=1, args=(field1, tags, root_ids))

      synapses_grouped = (
        data[key]
        .groupby([field1, field2], as_index=False)
        .agg({'size': 'sum'})
      )

      result = []
      for pt_root_id, group in synapses_grouped.groupby(field2):
        row = {
          'id': pt_root_id,
          'partners': group[[field1, 'size']].values.tolist()
        }
        result.append(row)

      return result

    synapses_grouped = {
      'upstream': create_groups(data, 'upstream', 'pre_pt_root_id', 'post_pt_root_id'),
      'downstream': create_groups(data, 'downstream', 'post_pt_root_id', 'pre_pt_root_id')
    }

    def create_partner_feature(partners, side):
      partner_dict = {}
      for partner in partners:
        tag, count = partner
        new_tag = f"{side}_{tag}"
        partner_dict[new_tag] = count
      return partner_dict

    all_tags = set()
    for upstream, downstream in zip(synapses_grouped['upstream'], synapses_grouped['downstream']):
      all_tags.update([tag for tag, _ in upstream['partners']])
      all_tags.update([tag for tag, _ in downstream['partners']])

    all_tags = sorted(all_tags)

    merged_partners = {}
    for upstream, downstream in zip(synapses_grouped['upstream'], synapses_grouped['downstream']):
      id = upstream['id']
      upstream_partners = create_partner_feature(upstream['partners'], 'upstream')
      downstream_partners = create_partner_feature(downstream['partners'], 'downstream')
      merged_partners[id] = {**upstream_partners, **downstream_partners}

    _merged_partners_data = merged_partners
    _current_partner_data = None  # Reset cache before new clustering
    _perform_clustering(merged_partners, callback, eps)
  except Exception as e:
    print(f"Error in group_by_types_of_partners: {str(e)}")
    callback({
      'status': Status.ERROR,
      'content': f'Error processing partners: {str(e)}'
    })

def get_clusters_thread(input_ids, callback, eps):
  tags = []
  root_ids = []

  def get_partners():
    nonlocal input_ids
    callback('MSG:Getting synaptic partners...')
    input_ids = clean_input(input_ids)
    group_with_context = partial(group_by_types_of_partners, tags=tags, root_ids=root_ids, eps=eps, callback=callback)
    get_synaptic_partners(input_ids, group_with_context, direction='both', raw=True)

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

      mask = ~np.isin(tags, unwanted_tags)
      tags = tags[mask]
      root_ids = root_ids[mask].astype(np.int64)
      get_partners()

  get_entries('cell_info', process_entries, return_result=True)

def _perform_clustering(merged_partners, callback, eps):
  global _current_partner_data
  try:
    # Convert dictionary data to feature matrix
    neuron_ids = list(merged_partners.keys())
    
    # Collect all unique neuron types (excluding 'Other')
    all_types = set()
    for connections in merged_partners.values():
      for key in connections.keys():
        if 'Other' not in key:
          all_types.add(key)
    all_types = sorted(list(all_types))
    
    # Create feature matrix
    X = np.zeros((len(neuron_ids), len(all_types)))
    for i, neuron_id in enumerate(neuron_ids):
      for j, type_ in enumerate(all_types):
        X[i, j] = merged_partners[neuron_id].get(type_, 0)
    
    # Log transform to handle varying scales
    X = np.log1p(X)
    
    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Store the data for reclustering
    _current_partner_data = {
      'merged_partners': merged_partners,
      'X': X,
      'neuron_ids': neuron_ids,
      'all_types': all_types
    }

    # Calculate linkage matrix
    Z = linkage(X, method='ward')
    
    # Scale eps to match dendrogram scale
    scaled_eps = eps * np.max(Z[:, 2]) / 100  # Convert slider value (0-100) to actual distance
    
    # Get clusters from hierarchical clustering
    labels = fcluster(Z, scaled_eps, criterion='distance')
    
    
    # Convert to 0-based indexing
    labels = labels - 1
    
    unique_labels = sorted(set(labels))
    clusters = []
    
    # Process each cluster
    for label in unique_labels:
      mask = labels == label
      cluster_neurons = [neuron_ids[i] for i, is_member in enumerate(mask) if is_member]
      
      # Calculate cluster characteristics
      cluster_features = X[mask]
      mean_pattern = np.mean(cluster_features, axis=0)
      
      # Find significant patterns
      patterns = []
      for i, type_ in enumerate(all_types):
        if abs(mean_pattern[i]) > 0.5:  # Lower threshold for significance
          is_upstream = type_.startswith('upstream_')
          partner_type = type_.replace('upstream_', '').replace('downstream_', '')
          
          patterns.append({
            'type': 'upstream' if is_upstream else 'downstream',
            'partner': partner_type,
            'strength': abs(mean_pattern[i])
          })
      
      # Sort patterns by strength
      patterns.sort(key=lambda x: x['strength'], reverse=True)
      
      clusters.append({
        'type': 'cluster',
        'neurons': cluster_neurons,
        'size': len(cluster_neurons),
        'patterns': patterns[:5]  # Top 5 patterns
      })
    
    # Sort clusters by size
    clusters.sort(key=lambda x: -x['size'])
    
    # Calculate silhouette score only if we have a valid number of clusters
    silhouette = 0
    n_samples = len(neuron_ids)
    n_clusters = len(unique_labels)
    if 2 <= n_clusters <= n_samples - 1:
      try:
        silhouette = silhouette_score(X, labels)
      except:
        silhouette = 0
    
    callback({
      'n_clusters': len(clusters),
      'clusters': clusters,
      'silhouette': silhouette,
      'eps_used': eps,
      'distances': X,
      'linkage': Z
    })
  except Exception as e:
    print(f"Error in _perform_clustering: {str(e)}")
    callback({
      'status': Status.ERROR,
      'content': f'Error during clustering: {str(e)}'
    })

def download_skeleton(nid):
  path = os.path.join('skeleton_cache', f'{nid}.h5')
  if os.path.exists(path):
    skel = mpsk.read_skeleton_h5(path)
  else:
    skel = banc.skeletonize.get_pcg_skeleton(nid)
    mpsk.write_skeleton_h5(skel, path)

  skel = banc.skeletonize.mp_to_navis(skel, xyz_scaling=1000)
  return skel

def download_all_skeletons(nids):
  results = navis.NeuronList([])
  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(download_skeleton, nid): nid for nid in nids}
    for future in as_completed(futures):
      nid = futures[future]
      try:
        result = future.result()
        results.append(result)
      except Exception as e:
        print(f"Error downloading skeleton for {nid}: {e}")
  return results

def _calculate_distances(neuron_ids):
  skeletons = download_all_skeletons(neuron_ids)
  neurons = navis.make_dotprops(skeletons)
  nblast_scores = navis.nblast_allbyall(neurons, normalized=True)
  averaged_nblast_scores = (nblast_scores + nblast_scores.T) / 2
  distances = 1 - averaged_nblast_scores
  
  return distances

def get_nblast_clusters(neuron_ids_text, callback, eps):
  def worker():
    global _current_nblast_data
    try:
      # Only clean input if we're not reclustering
      if neuron_ids_text is not None:
        neuron_ids = clean_input(neuron_ids_text)
        _current_nblast_data = None  # Reset stored data for new query
      elif _current_nblast_data is not None:
        # Use stored neuron IDs if reclustering
        neuron_ids = _current_nblast_data['neuron_ids']
        distances = _current_nblast_data['distances']

      if not _current_nblast_data:
        if len(neuron_ids) < 2:
          callback("MSG:Need at least 2 neurons for clustering")
          return
        distances = _calculate_distances(neuron_ids)

        # Store the data for reclustering
        _current_nblast_data = {
          'distances': distances,
          'neuron_ids': neuron_ids
        }
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)

      result = {
        **_current_nblast_data,
        'eps_used': eps
      }
      callback(result)
    
    except Exception as e:
      print(f"Error in NBLAST clustering: {str(e)}")
      callback(f"MSG:Error during NBLAST clustering: {str(e)}")
  
  threading.Thread(target=worker).start()
