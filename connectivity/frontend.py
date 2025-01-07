from utils.frontend import *
from constants import *
import tkinter as tk
import pyperclip
from connectivity.backend import *
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np
import pandas as pd

# Moved variables to the upper level
current_frame = None
current_dendro = None
current_ax = None
threshold_line = None
dendro_frame = None
results_container = None
root = None
canvas = None
Z = None


def show_message(msg):
  global current_frame

  current_frame = ctk.CTkFrame(results_container)
  current_frame.pack(fill='both', expand=True)

  label = ctk.CTkLabel(current_frame, text=msg)
  label.pack(pady=20)


def copy_neurons(neurons):
  pyperclip.copy('\n'.join(map(str, neurons)))


def update_threshold_line(value):
  global threshold_line, current_ax, canvas
  try:
    value = float(value)
    if threshold_line is not None:
      threshold_line.set_ydata([value / 100, value / 100])
      current_ax.figure.canvas.draw()
  except Exception as e:
    print(f"Error in update_threshold_line: {str(e)}")


def update_cluster_colors(eps):
  global current_ax, canvas, Z
  try:
    # Recalculate clusters below the threshold
    eps_scaled = eps / 100  # Scale threshold to match normalized heights
    clusters = fcluster(Z, t=eps_scaled, criterion='distance')

    # Get unique cluster IDs and assign colors
    unique_clusters = np.unique(clusters)
    cluster_colors = {cluster: plt.cm.tab10(i % 10) for i, cluster in enumerate(unique_clusters)}

    # Update dendrogram colors dynamically
    for i, d in enumerate(current_ax.collections):
      if i < len(clusters):
        d.set_color(cluster_colors[clusters[i]])

    # Redraw canvas
    current_ax.figure.canvas.draw()
  except Exception as e:
    print(f"Error in update_cluster_colors: {str(e)}")


def update_dendrogram(X, Z_input, eps):
  global current_ax, threshold_line, canvas, Z
  Z = Z_input  # Store linkage matrix for cluster recalculation

  # Clear existing dendrogram
  if current_ax is not None:
    current_ax.clear()
  threshold_line = None

  # Calculate the range of heights in the linkage matrix
  height_range = Z[:, 2].max() - Z[:, 2].min()
  if height_range > 0:
    # Normalize heights to spread them out
    Z_normalized = Z.copy()
    Z_normalized[:, 2] = (Z[:, 2] - Z[:, 2].min()) / height_range
  else:
    Z_normalized = Z

  # Calculate color threshold based on eps
  color_threshold = eps / 100  # eps is already 0-100

  # Draw dendrogram with automatic coloring
  dendrogram(
    Z_normalized,
    ax=current_ax,
    no_labels=True,
    color_threshold=color_threshold,
    above_threshold_color='gray',
    leaf_rotation=0
  )

  # Add threshold line at the exact same height as color threshold
  threshold_line = current_ax.axhline(y=color_threshold, color='r', linestyle='--')

  # Set y-axis limits
  current_ax.set_ylim(bottom=0, top=1.0)

  # Create fixed ticks and labels that match the eps scale
  yticks = np.linspace(0, 1, 11)
  current_ax.set_yticks(yticks)
  current_ax.set_yticklabels([f"{y * 100:.0f}" for y in yticks])

  # Remove x-axis ticks and labels
  current_ax.set_xticks([])

  # Adjust layout
  current_ax.figure.tight_layout()

  # Redraw canvas
  canvas.draw()


def display_clusters(data):
  global current_frame

  # Check if we received an error message
  if isinstance(data, str) and data.startswith("MSG:"):
    show_message(data[4:])
    return

  try:
    # Update dendrogram first
    if 'distances' in data and 'linkage' in data:
      Z = data['linkage']
      update_dendrogram(data['distances'], Z, data['eps_used'])

    # Create new frame for clusters
    current_frame = ctk.CTkScrollableFrame(results_container)
    current_frame.pack(fill='both', expand=True)

    # Header
    header = ctk.CTkLabel(
      current_frame,
      text=f"Found {data['n_clusters']} clusters",
      font=(FONT_FAMILY, 14, "bold")
    )
    header.pack(pady=(0, 10))

    if not current_frame:
      return
    # Display clusters
    for cluster in data['clusters']:
      try:
        cluster_frame = ctk.CTkFrame(current_frame)
        cluster_frame.pack(fill='x', pady=5, padx=5)

        # Header frame
        header_frame = ctk.CTkFrame(cluster_frame)
        header_frame.pack(fill='x', padx=5, pady=5)

        # Title
        title = f"Cluster ({cluster['size']} neurons)"
        ctk.CTkLabel(
          header_frame,
          text=title,
          font=(FONT_FAMILY, 12, "bold")
        ).pack(side='left')

        # Copy button
        copy_cmd = lambda n=cluster['neurons']: copy_neurons(n)
        ctk.CTkButton(
          header_frame,
          text="Copy IDs",
          width=80,
          height=25,
          command=copy_cmd
        ).pack(side='right')

        # Neuron IDs
        neuron_text = ctk.CTkTextbox(cluster_frame, height=50)
        neuron_text.pack(fill='x', padx=5, pady=(0, 5))
        neuron_text.insert('1.0', ' '.join(map(str, cluster['neurons'])))
        neuron_text.configure(state='disabled')

      except Exception as e:
        print(f"Error creating cluster UI: {str(e)}")
        continue

  except Exception as e:
    print(f"Error in display_clusters: {str(e)}")
    show_message(f"Error displaying clusters: {str(e)}")


def create_connectivity_section(r):
  global root, dendro_frame, current_ax, canvas
  root = r
  main_frame = ctk.CTkFrame(r)
  main_frame.pack(fill='both', expand=True, padx=10, pady=10)

  # Input section
  input_frame = ctk.CTkFrame(main_frame)
  input_frame.pack(fill='x', pady=(0, 10))

  input_box = widgets.countTextbox(parent=input_frame, label='Input Neuron IDs')

  # Button frame for multiple actions
  button_frame = ctk.CTkFrame(main_frame)
  button_frame.pack(fill='x', pady=(0, 10))

  cluster_button = widgets.button(button_frame, "Cluster by Partners", None)
  nblast_button = widgets.button(button_frame, "Cluster by Shape", None)

  # Controls and Dendrogram container
  mid_frame = ctk.CTkFrame(main_frame)
  mid_frame.pack(fill='x', pady=(0, 10))

  # Controls on the left
  control_frame = ctk.CTkFrame(mid_frame)
  control_frame.pack(side='left', fill='y', padx=(0, 10))

  # Sensitivity control with value display
  sens_frame = ctk.CTkFrame(control_frame)
  sens_frame.pack(fill='x', padx=5, pady=5)

  eps_var = tk.DoubleVar(value=50)
  eps_label = widgets.label(sens_frame, "Clustering Sensitivity")

  # Value display
  value_label = ctk.CTkLabel(sens_frame, text=eps_var.get())
  value_label.pack(side='right')

  eps_slider = ctk.CTkSlider(
    control_frame,
    from_=0.1,
    to=100.0,
    number_of_steps=100,
    variable=eps_var,
    width=200
  )
  eps_slider.pack(fill='x', padx=10, pady=(0, 10))

  # Dendrogram frame on the right
  dendro_frame = ctk.CTkFrame(mid_frame)
  dendro_frame.pack(side='left', fill='both', expand=True)

  # Initialize matplotlib canvas
  fig = Figure(figsize=(6, 4), dpi=100)
  current_ax = fig.add_subplot(111)
  canvas = FigureCanvasTkAgg(fig, master=dendro_frame)
  canvas.get_tk_widget().pack(fill='both', expand=True)

  # Results container
  results_container = ctk.CTkFrame(main_frame)
  results_container.pack(fill='both', expand=True)

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
    get_clusters(input_text, handle_results, eps)

  def on_nblast():
    input_text = input_box.get('1.0', 'end').strip()
    eps = eps_var.get()

    if not input_text:
      show_message("Please enter neuron IDs")
      return

    show_loading_indicator(root)
    get_nblast_clusters(input_text, handle_results, eps)

  # Set the button commands
  cluster_button.configure(command=on_cluster)
  nblast_button.configure(command=on_nblast)

  # Slider events
  def on_slider_move(value):
    # Update value display and threshold line
    value_label.configure(text=f"{float(value):.1f}")
    update_threshold_line(float(value))

  def on_slider_release(event):
    # Recalculate clusters only when slider is released
    show_loading_indicator(root)
    update_cluster_colors(float(eps_var.get()))
    recluster(float(eps_var.get()), handle_results)

  eps_slider.configure(command=on_slider_move)
  eps_slider.bind("<ButtonRelease-1>", on_slider_release)