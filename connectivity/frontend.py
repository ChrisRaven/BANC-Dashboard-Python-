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
import matplotlib.pyplot as plt

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
  """ Plots dendrogram, stores leaf order/colors, returns NORMALIZED Z. """
  global current_ax, threshold_line, canvas, Z # Z still stores original linkage
  
  if current_ax is not None:
    current_ax.clear()
  threshold_line = None
        
  # --- Calculate Distance Vector 'aba_vec' ---
  if isinstance(distances, np.ndarray) and len(distances.shape) == 2:
    if distances.shape[0] != distances.shape[1]: # Partner features
      from scipy.spatial.distance import pdist
      aba_vec = pdist(distances, 'euclidean') 
    else: # NBLAST distances
      np.fill_diagonal(distances, 0)
      aba_vec = squareform(distances, checks=False)
  else: # Condensed distances
    aba_vec = distances
  aba_vec = np.maximum(aba_vec, 0) # Clip negative values

  # --- Linkage ---
  Z = linkage(aba_vec, method="ward", optimal_ordering=True) 

  # --- Normalize and Plot ---
  normalized_Z = _normalize_linkage(Z.copy()) # Critical: Use a copy
  color_threshold_normalized = eps / 100 

  dendro = dendrogram(
    normalized_Z, # Plot using normalized Z
    ax=current_ax,
    no_labels=True,
    color_threshold=color_threshold_normalized, 
    above_threshold_color='gray',
    leaf_rotation=0,
  )

  # --- Store Results Needed by display_clusters ---
  update_dendrogram.leaf_order = dendro['leaves']
  # Store the color assigned by dendrogram plot to each leaf
  update_dendrogram.leaves_color_list = dendro['leaves_color_list'] 
  # We don't strictly need dendro['color_list'] for buttons

  # --- Plot Threshold Line and Adjust Axes ---
  threshold_line = current_ax.axhline(y=color_threshold_normalized, color='r', linestyle='--')
  current_ax.set_ylim(bottom=0, top=1.0)
  yticks = np.linspace(0, 1, 11)
  current_ax.set_yticks(yticks)
  current_ax.set_yticklabels([f"{y * 100:.0f}" for y in yticks])
  current_ax.set_xticks([])
  current_ax.figure.tight_layout()
  canvas.draw()

  # Return the normalized linkage matrix used for plotting
  return normalized_Z

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

    normalized_Z_for_clustering = None # Initialize

    # --- Dendrogram Update and Data Fetching ---
    if isinstance(data, dict) and 'distances' in data:
      # Initial clustering
      neuron_ids = data.get('neuron_ids', []) 
      if not neuron_ids:
          raise ValueError("Neuron IDs ('neuron_ids') missing from backend.")
          
      display_clusters.neuron_ids = neuron_ids
      display_clusters.eps_used = data['eps_used']
      display_clusters.distances = data['distances']
      # Update dendrogram plots AND returns normalized Z
      normalized_Z_for_clustering = update_dendrogram(display_clusters.distances, display_clusters.eps_used)
    else:
      # Slider update (reclustering)
      if not hasattr(display_clusters, 'distances') or not hasattr(display_clusters, 'neuron_ids'):
        return 
      display_clusters.eps_used = data 
      # Re-plot dendrogram AND get updated normalized Z
      normalized_Z_for_clustering = update_dendrogram(display_clusters.distances, display_clusters.eps_used)

    if Z is None or normalized_Z_for_clustering is None:
      raise ValueError("Linkage matrix (Z or normalized_Z) not created")
    # We still need leaf_order for button arrangement
    if not hasattr(update_dendrogram, 'leaf_order') or not hasattr(update_dendrogram, 'leaves_color_list'):
       raise ValueError("Dendrogram leaf order or leaves_color_list not available")

    # --- Cluster Processing using fcluster on NORMALIZED data ---
    
    # Use the normalized threshold directly with the normalized linkage matrix
    normalized_threshold_t = display_clusters.eps_used / 100.0

    # *** CRITICAL: Use normalized_Z_for_clustering and normalized_threshold_t ***
    cluster_labels = fcluster(normalized_Z_for_clustering, t=normalized_threshold_t, criterion='distance')
    
    unique_labels, counts = np.unique(cluster_labels, return_counts=True)
    num_clusters = len(unique_labels)
    label_counts = dict(zip(unique_labels, counts))

    # --- Map cluster labels to Dendrogram plot colors (using leaves_color_list) ---
    fcluster_to_dendro_color_map = {}
    for i, leaf_orig_idx in enumerate(update_dendrogram.leaf_order):
        current_fcluster_label = cluster_labels[leaf_orig_idx]
        if current_fcluster_label not in fcluster_to_dendro_color_map:
            dendro_color_str = update_dendrogram.leaves_color_list[i]
            try:
                color_rgba = matplotlib.colors.to_rgba(dendro_color_str)
                if matplotlib.colors.same_color(color_rgba, 'black') or matplotlib.colors.same_color(color_rgba, 'gray') or dendro_color_str in ['k', 'grey', 'gray']:
                   color_rgba = np.array([0.5, 0.5, 0.5, 1])
            except ValueError:
                 color_rgba = np.array([0.5, 0.5, 0.5, 1])
            fcluster_to_dendro_color_map[current_fcluster_label] = color_rgba

    # --- Process clusters in dendrogram order for Buttons ---
    processed_clusters = []
    visited_labels = set()
    
    for leaf_index in update_dendrogram.leaf_order:
      current_label = cluster_labels[leaf_index]

      if current_label not in visited_labels:
        visited_labels.add(current_label)
        
        indices_in_cluster = [i for i, lbl in enumerate(cluster_labels) if lbl == current_label]
        neurons_in_cluster = [display_clusters.neuron_ids[i] for i in indices_in_cluster]
        
        cluster_color_rgba = fcluster_to_dendro_color_map.get(current_label, np.array([0.5, 0.5, 0.5, 1]))
        if label_counts[current_label] == 1:
             cluster_color_rgba = np.array([0.5, 0.5, 0.5, 1])

        processed_clusters.append({
            'label': current_label,
            'neurons': neurons_in_cluster,
            'color': cluster_color_rgba 
        })

    # --- Update UI ---
    if cluster_count_label:
      cluster_count_label.configure(text=f"Found {num_clusters} clusters") # This should now match dendrogram visually

    # Create a frame for button rows
    buttons_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
    buttons_frame.pack(fill='x', expand=True)
    
    # Fixed number of buttons per row (adjust if needed)
    buttons_per_row = 10
    
    current_row_frame = None
    button_count = 0
    
    # Create buttons in dendrogram order
    for cluster_info in processed_clusters:
      # Create new row frame if needed
      if button_count % buttons_per_row == 0:
        current_row_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        current_row_frame.pack(fill='x', pady=(0, 2))
      
      cluster_neurons = cluster_info['neurons']
      color = cluster_info['color']
      
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