from utils.frontend import *
from constants import *
import tkinter as tk
import pyperclip
from connectivity.backend import *
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import fcluster

# Moved variables to the upper level
current_frame = None
current_ax = None
threshold_line = None
dendro_frame = None
results_container = None
root = None
canvas = None
averaged_nblast_scores = None
cluster_count_label = None
averaged_nblast_scores = None
Z = None

def show_message(msg):
  widgets.frame(results_container)
  widgets.label(current_frame, text=msg)

def copy_neurons(neurons):
  pyperclip.copy('\n'.join(map(str, neurons)))

def update_threshold_line(value):
  global threshold_line, current_ax, canvas
  try:
    if threshold_line is not None:
      threshold_line.set_ydata([value / 100, value / 100])
      current_ax.figure.canvas.draw()
  except Exception as e:
    print(f"Error in update_threshold_line: {str(e)}")

def _normalize_linkage(Z):
  heights = Z[:, 2]
  min_height = heights.min()
  max_height = heights.max()
  height_range = max_height - min_height
  if height_range > 0:
    padding = 0.05 * height_range  # Add padding of 5% of the range on both sides
    Z[:, 2] = (heights - min_height + padding) / (height_range + 2 * padding)
  return Z

def update_dendrogram(distances, eps):
  global current_ax, threshold_line, canvas, averaged_nblast_scores, Z
  
  if current_ax is not None:
    current_ax.clear()
  threshold_line = None

  # Check if the distances array is already a square matrix or a condensed distance matrix
  if isinstance(distances, np.ndarray) and len(distances.shape) == 2:
    if distances.shape[0] != distances.shape[1]:
      # For rectangular matrices (feature vectors from partner-based clustering)
      from scipy.spatial.distance import pdist
      aba_vec = pdist(distances, 'euclidean')
      max_dist = np.max(aba_vec) if len(aba_vec) > 0 else 1
      averaged_nblast_scores = 1 - (aba_vec / max_dist)
    else:
      # For square distance matrix (NBLAST)
      # Fill diagonal with zeros to avoid warning
      np.fill_diagonal(distances, 0)
      aba_vec = squareform(distances, checks=False)
      averaged_nblast_scores = 1 - distances
  else:
    # Already a condensed distance matrix
    aba_vec = distances
    averaged_nblast_scores = 1 - distances

  # Compute linkage for hierarchical clustering
  Z = linkage(aba_vec, method="ward", optimal_ordering=True)

  color_threshold = eps / 100
  dendro = dendrogram(
    _normalize_linkage(Z),
    ax=current_ax,
    no_labels=True,
    color_threshold=color_threshold,
    above_threshold_color='gray',
    leaf_rotation=0,
  )

  # Store both the leaf order and color data
  update_dendrogram.leaf_order = dendro['leaves']
  update_dendrogram.color_list = dendro['color_list']
  update_dendrogram.leaves_color_list = dendro['leaves_color_list']

  threshold_line = current_ax.axhline(y=color_threshold, color='r', linestyle='--')
  current_ax.set_ylim(bottom=0, top=1.0)

  yticks = np.linspace(0, 1, 11)
  current_ax.set_yticks(yticks)
  current_ax.set_yticklabels([f"{y * 100:.0f}" for y in yticks])
  current_ax.set_xticks([])
  current_ax.figure.tight_layout()
  canvas.draw()

  return dendro


def display_clusters(data):
  global current_frame, cluster_count_label, current_ax, Z

  if isinstance(data, str) and data.startswith("MSG:"):
    show_message(data[4:])
    return
  
  try:
    # Clear existing buttons
    if current_frame is not None:
      for widget in current_frame.winfo_children():
        widget.destroy()
      current_frame.destroy()
    
    # Clear results container first
    for widget in results_container.winfo_children():
      widget.destroy()
    
    # Create new frame in results_container
    current_frame = ctk.CTkFrame(results_container, fg_color="transparent")
    current_frame.pack(fill='x', padx=10, pady=(0, 5))

    # Handle initial clustering vs slider updates
    if isinstance(data, dict) and 'distances' in data:
      # Handle both partner-based and NBLAST clustering
      if 'clusters' in data:
        # Partner-based clustering
        neuron_ids = []
        for cluster in data['clusters']:
          neuron_ids.extend(cluster['neurons'])
      else:
        # NBLAST clustering
        neuron_ids = data['neuron_ids']
        
      display_clusters.neuron_ids = neuron_ids
      display_clusters.eps_used = data['eps_used']
      display_clusters.distances = data['distances']
      dendro = update_dendrogram(data['distances'], data['eps_used'])
    else:
      if not hasattr(display_clusters, 'distances') or not hasattr(display_clusters, 'neuron_ids'):
        return
      display_clusters.eps_used = data
      dendro = update_dendrogram(display_clusters.distances, data)

    if Z is None:
      raise ValueError("Linkage matrix not created")

    # Get clusters using fcluster
    # Get clusters using fcluster
    # Get clusters using fcluster
    cluster_labels = fcluster(Z, t=display_clusters.eps_used/100, criterion='distance')
    
    # Create mapping from original indices to leaf order
    leaf_to_orig = {leaf: i for i, leaf in enumerate(update_dendrogram.leaf_order)}
    
    # Group neurons by cluster and track their positions
    clusters = {}
    cluster_positions = {}  # Store leftmost position for each cluster
    cluster_sizes = {}
    
    # First pass - collect clusters and find their leftmost positions
    for i, label in enumerate(cluster_labels):
      if label not in clusters:
        clusters[label] = []
        cluster_sizes[label] = 0
        cluster_positions[label] = len(update_dendrogram.leaf_order)  # Initialize with max position
      
      clusters[label].append(display_clusters.neuron_ids[i])
      cluster_sizes[label] += 1
      
      # Update leftmost position
      leaf_pos = update_dendrogram.leaf_order.index(i)
      if leaf_pos < cluster_positions[label]:
        cluster_positions[label] = leaf_pos

    # Sort clusters by their leftmost position in the dendrogram
    ordered_labels = sorted(cluster_positions.keys(), key=lambda x: cluster_positions[x])

    # Get colors from dendrogram's color_list
    unique_colors = []
    for color in update_dendrogram.color_list:
      if color != 'gray' and color not in unique_colors:
        unique_colors.append(color)

    # Map colors to clusters
    color_map = {}
    color_idx = 0
    
    for label in ordered_labels:
      size = cluster_sizes[label]
      if size > 1 and color_idx < len(unique_colors):
        color_map[label] = matplotlib.colors.to_rgba(unique_colors[color_idx])
        color_idx += 1
      else:
        color_map[label] = np.array([0.5, 0.5, 0.5, 1])  # gray

    # Update cluster count
    if cluster_count_label:
      cluster_count_label.configure(text=f"Found {len(clusters)} clusters")

    # Create a frame for button rows
    buttons_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
    buttons_frame.pack(fill='x', expand=True)
    
    # Fixed number of buttons per row (adjust if needed)
    buttons_per_row = 10
    
    current_row_frame = None
    button_count = 0
    
    # Create buttons in dendrogram order
    for label in ordered_labels:
      # Create new row frame if needed
      if button_count % buttons_per_row == 0:
        current_row_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        current_row_frame.pack(fill='x', pady=(0, 2))
      
      cluster_neurons = clusters[label]
      color = color_map[label]
      
      hex_color = '#{:02x}{:02x}{:02x}'.format(
        int(color[0] * 255),
        int(color[1] * 255),
        int(color[2] * 255)
      )

      btn = ctk.CTkButton(
        master=current_row_frame,
        text=str(len(cluster_neurons)),
        width=60,
        height=30,
        command=lambda ids=cluster_neurons: copy_neurons(ids),
        fg_color=hex_color,
        hover_color=hex_color
      )
      btn.pack(side='left', padx=2)
      button_count += 1

    # Force update of frames
    buttons_frame.update()
    current_frame.update()
    results_container.update()

  except Exception as e:
    print(f"Error in display_clusters: {str(e)}")
    show_message(f"Error displaying clusters: {str(e)}")

# Initialize static variables
display_clusters.neuron_ids = []
display_clusters.eps_used = None
display_clusters.distances = None

def create_connectivity_section(r):
  global root, dendro_frame, current_ax, canvas, results_container, current_frame, cluster_count_label
  root = r
  main_frame = widgets.frame(r)
  input_frame = widgets.frame(main_frame)

  input_box = widgets.countTextbox(parent=input_frame, label='Input Neuron IDs')

  controls = widgets.column_wrapper(parent=main_frame)

  # --- Sensitivity Control ---
  sensitivity_column = widgets.column(parent=controls)
  eps_var = tk.DoubleVar(value=90)
  widgets.label(sensitivity_column, "Clustering Sensitivity").pack(pady=(0, 5))

  value_label = ctk.CTkLabel(sensitivity_column, text=eps_var.get())
  value_label.pack(side='right', padx=10)
  
  eps_slider = ctk.CTkSlider(
    sensitivity_column,
    from_=0.1,
    to=100.0,
    number_of_steps=100,
    variable=eps_var,
    width=200
  )
  eps_slider.pack(fill='x', padx=10, pady=(0, 5))

  cluster_count_label = ctk.CTkLabel(
    sensitivity_column,
    text="Found 0 clusters",
    font=(FONT_FAMILY, 12, "bold"),
    text_color="#A9A9A9"
  )
  cluster_count_label.pack(pady=(5, 10))

  # --- Buttons ---
  buttons_column = widgets.column(parent=controls)
  cluster_button = widgets.button(buttons_column, "Cluster by Partners", None)
  nblast_button = widgets.button(buttons_column, "Cluster by Shape", None)

  # --- Dendrogram Frame ---
  dendro_frame = widgets.frame(main_frame)
  fig = Figure(figsize=(6, 2), dpi=100)
  current_ax = fig.add_subplot(111)
  canvas = FigureCanvasTkAgg(fig, master=dendro_frame)
  canvas.get_tk_widget().pack(fill='both', expand=True)

  # --- Results Container ---
  results_container = widgets.frame(main_frame)
  
  def handle_results(data):
    hide_loading_indicator()
    if isinstance(data, str) and data.startswith('MSG:'):
      show_message(data[4:])
    else:
      display_clusters(data)
  
  def on_cluster():
    input_text = input_box.get('1.0', 'end').strip()
    eps = eps_var.get()
    
    if not input_text:
      show_message("Please enter neuron IDs")
      return
    
    show_loading_indicator(root)
    on_slider_release.last_cluster_type = 'partners'
    get_clusters(input_text, handle_results, eps)
  
  def on_nblast():
    input_text = input_box.get('1.0', 'end').strip()
    eps = eps_var.get()
    
    if not input_text:
      show_message("Please enter neuron IDs")
      return
    show_loading_indicator(root)
    on_slider_release.last_cluster_type = 'nblast'
    get_nblast_clusters(input_text, handle_results, eps)
  
  cluster_button.configure(command=on_cluster)
  nblast_button.configure(command=on_nblast)
  
  def on_slider_move(value):
    value_label.configure(text=f"{float(value):.1f}")
    update_threshold_line(float(value))
  
  def on_slider_release(event):
    show_loading_indicator(root)
    if hasattr(on_slider_release, 'last_cluster_type'):
      if on_slider_release.last_cluster_type == 'nblast':
        get_nblast_clusters(None, handle_results, eps_var.get())
      else:
        get_clusters(None, handle_results, eps_var.get())
  
  eps_slider.configure(command=on_slider_move)
  eps_slider.bind("<ButtonRelease-1>", on_slider_release)