__all__ = ['get_clusters', 'recluster', 'get_nblast_clusters']

DEBUG = True
SAVE = False

import threading
from utils.backend import *
from constants import *
from find_annotated.backend import get_entries
from get_synaptic_partners.backend import get_synaptic_partners
import numpy as np
import pyperclip
from functools import partial
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from anytree import Node, RenderTree

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import ThreadPoolExecutor
import banc
import requests
import json
from io import StringIO
import pandas as pd
from api_token import API_TOKEN
from caveclient import CAVEclient
import banc
import fafbseg
import navis

# Store the merged_partners data
_merged_partners_data = None

# Add this at the top with other global variables
_current_nblast_data = None

def get_clusters(input_ids, callback, eps=0.5):
  global _merged_partners_data
  _merged_partners_data = None # Reset data on new get_clusters call
  threading.Thread(target=lambda: get_clusters_thread(input_ids, callback, eps), daemon=True).start()

def recluster(eps, callback):
  """Recluster using stored NBLAST data."""
  global _current_nblast_data
  if _current_nblast_data is not None:
    get_nblast_clusters(None, callback, eps)
  else:
    callback("MSG:No data available for reclustering. Please fetch clusters first.")

def group_by_types_of_partners(synapses, tags, root_ids, eps, callback):
  global _merged_partners_data
  if isinstance(synapses, str): return None
  if synapses['status'] != Status.FINISHED: return None
  if synapses['content']['upstream'].empty and synapses['content']['downstream'].empty: return None
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
  _perform_clustering(merged_partners, callback, eps)

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
    'distances': X,  # For dendrogram
    'linkage': Z    # Add linkage matrix for better dendrogram updates
  })

def skeleton_to_TreeNeuron(skeleton):
  nodes = []  # Will hold (id, x, y, z, radius, parent_id) tuples
  for i, coord in enumerate(skeleton.vertices):
    radius = 1  # Placeholder radius, adjust if available
    parent_id = skeleton.parent_index
    nodes.append((i, coord[0], coord[1], coord[2], radius, parent_id))
    columns = ['node_id', 'x', 'y', 'z', 'radius', 'parent_id']
  return navis.TreeNeuron(pd.DataFrame(data=nodes, columns=columns))

def get_nblast_clusters_original(neuron_ids_text, callback, eps):
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
      else:
        callback("MSG:No data available for reclustering")
        return

      # Use stored data for clustering if available
      if _current_nblast_data is not None:
        distances = _current_nblast_data['distances']
      else:
        neurons = []
        for nid in neuron_ids:
          try:
            skel = banc.skeletonize.get_pcg_skeleton(nid)
            skel.parent_index = nid
            neuron = navis.make_dotprops(skeleton_to_TreeNeuron(skel))
            neurons.append(neuron)
          except Exception as e:
            print(f"MSG:Error loading skeleton for {nid}: {str(e)}")
            callback(f"MSG:Error loading skeleton for {nid}: {str(e)}")
            return
        
        if len(neurons) < 2:
          callback("MSG:Need at least 2 neurons for clustering")
          return

        # Get all-by-all NBLAST scores
        nblast_scores = navis.nblast_allbyall(neurons)
        # Convert similarity scores to distances
        distances = 1 - nblast_scores.values
        np.fill_diagonal(distances, 0)
        
        # Store the data for reclustering
        _current_nblast_data = {
          'distances': distances,
          'neuron_ids': neuron_ids
        }
      
      # Get condensed distance matrix (upper triangle)
      dist_condensed = distances[np.triu_indices(len(neuron_ids), k=1)]
      
      # Perform hierarchical clustering
      Z = linkage(dist_condensed, method='ward')
      
      # Get cluster labels using the current eps value
      scaled_eps = eps / 100  # eps is already 0-100
      labels = fcluster(Z, scaled_eps, criterion='distance') - 1  # 0-based indexing
      
      # Group neurons by cluster
      clusters = []
      unique_labels = np.unique(labels)
      for label in unique_labels:
        cluster_neurons = [neuron_ids[i] for i, l in enumerate(labels) if l == label]
        if cluster_neurons:  # Only add non-empty clusters
          clusters.append({
            'type': 'cluster',
            'neurons': cluster_neurons,
            'size': len(cluster_neurons),
            'patterns': []
          })
      
      # Sort clusters by size
      clusters.sort(key=lambda x: -x['size'])
      
      # Prepare results with fresh clustering
      result = {
        'distances': distances,
        'linkage': Z,
        'eps_used': eps,
        'n_clusters': len(clusters),
        'clusters': clusters,
        'neuron_ids': neuron_ids
      }
      callback(result)
    
    except Exception as e:
      print(f"Error in NBLAST clustering: {str(e)}")
      callback(f"MSG:Error during NBLAST clustering: {str(e)}")
  
  threading.Thread(target=worker).start()

def get_nblast_clusters(neuron_ids_text, callback, eps):
  global _current_nblast_data

  def save_data(data):
    import json
    data_serializable = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in data.items()}

    # Save the modified dictionary to a JSON file
    with open('data.json', 'w') as f:
      json.dump(data_serializable, f)

  def sideload_data():
    import json
    with open('data.json', 'r') as f:
      data = json.load(f)

    data['distances'] = np.array(data['distances'])
    data['linkage'] = np.array(data['linkage'])
    #data['eps_used'] = float(data['eps_used'])
    data['eps_used'] = eps
    return data

  if not DEBUG:
    get_nblast_clusters_original(neuron_ids_text, callback, eps)
  else:
    data = None
    if SAVE:
      save_data(data)
    else:
      data = sideload_data()
      _current_nblast_data = data

    callback(data)