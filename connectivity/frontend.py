from utils.frontend import *
from constants import *
import tkinter as tk
import pyperclip
from connectivity.backend import *
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial.distance import squareform

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
            # Compute pairwise distances between neurons
            aba_vec = pdist(distances, 'euclidean')
            # We'll use 1-normalized distances as similarity scores
            max_dist = np.max(aba_vec) if len(aba_vec) > 0 else 1
            averaged_nblast_scores = 1 - (aba_vec / max_dist)
        else:
            # Already a square distance matrix
            aba_vec = squareform(distances, checks=False)
            averaged_nblast_scores = 1 - distances
    else:
        # Already a condensed distance matrix
        aba_vec = distances
        averaged_nblast_scores = 1 - distances

    # Compute linkage for hierarchical clustering
    Z = linkage(aba_vec, method="ward", optimal_ordering=False)

    color_threshold = eps / 100
    dendro = dendrogram(
        _normalize_linkage(Z),
        ax=current_ax,
        no_labels=True,
        color_threshold=color_threshold,
        above_threshold_color='gray',
        leaf_rotation=0,
    )

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
    global current_frame, cluster_count_label

    if isinstance(data, str) and data.startswith("MSG:"):
        show_message(data[4:])
        return
    
    try:
        if 'distances' in data:
            dendro = update_dendrogram(data['distances'], data['eps_used'])
        
            epsilon = data['eps_used']
            
            # Extract neuron_ids from the appropriate data structure
            if 'neuron_ids' in data:
                neuron_ids = data['neuron_ids']
                # For NBLAST clustering - create empty clusters dict
                clusters = {}
                cluster_labels = fcluster(Z, t=epsilon/100, criterion='distance')
                optimized_order = dendro['leaves']
                reordered_cluster_labels = [cluster_labels[i] for i in optimized_order]
                for i, label in enumerate(reordered_cluster_labels):
                    neuron_id = neuron_ids[optimized_order[i]]
                    clusters.setdefault(label, []).append(neuron_id)
                # No patterns for NBLAST clusters
                cluster_patterns = {}
            else:
                # For partner-based clustering, use the clusters from the data
                clusters = {}
                cluster_patterns = {}
                for i, cluster in enumerate(data['clusters']):
                    cluster_id = i + 1  # 1-based cluster IDs
                    clusters[cluster_id] = cluster['neurons']
                    cluster_patterns[cluster_id] = cluster['patterns']

        # Reuse the existing frame or create if none
        if current_frame is None:
            current_frame = ctk.CTkScrollableFrame(results_container)
            current_frame.pack(fill='both', expand=True)
        else:
            # Clear existing cluster frames within the scrollable frame
            for widget in current_frame.winfo_children():
                widget.destroy()
        
        # Update the cluster count label
        if cluster_count_label:
            cluster_count_label.configure(text=f"Found {len(clusters)} clusters")
        
        for cluster_id, neuron_ids in clusters.items():
            try:
                cluster_frame = ctk.CTkFrame(current_frame)
                cluster_frame.pack(fill='x', pady=5, padx=5)

                header_frame = ctk.CTkFrame(cluster_frame)
                header_frame.pack(fill='x', padx=5, pady=5)

                title = f"Cluster {cluster_id} ({len(neuron_ids)} neurons)"
                ctk.CTkLabel(
                    header_frame,
                    text=title,
                    font=(FONT_FAMILY, 12, "bold")
                ).pack(side='left')

                copy_cmd = lambda n=neuron_ids: copy_neurons(n)
                ctk.CTkButton(
                    header_frame,
                    text="Copy IDs",
                    width=80,
                    height=25,
                    command=copy_cmd
                ).pack(side='right')

                neuron_text = ctk.CTkTextbox(cluster_frame, height=50)
                neuron_text.pack(fill='x', padx=5, pady=(0, 5))
                neuron_text.insert('1.0', ' '.join(map(str, neuron_ids)))
                neuron_text.configure(state='disabled')
                
                # Display patterns if available for this cluster
                if cluster_id in cluster_patterns and cluster_patterns[cluster_id]:
                    patterns_frame = ctk.CTkFrame(cluster_frame)
                    patterns_frame.pack(fill='x', padx=5, pady=5)
                    
                    ctk.CTkLabel(
                        patterns_frame,
                        text="Connection Patterns:",
                        font=(FONT_FAMILY, 11, "bold")
                    ).pack(anchor='w', padx=5, pady=(5, 0))
                    
                    for pattern in cluster_patterns[cluster_id]:
                        direction = "Receives from" if pattern['type'] == 'upstream' else "Connects to"
                        strength = "strongly" if pattern['strength'] > 1.5 else "moderately"
                        
                        # Use pattern['id'] if available, otherwise use pattern['partner']
                        partner_id = pattern.get('id', pattern.get('partner', 'Unknown'))
                        pattern_text = f"• {direction} {partner_id} {strength}"
                        
                        ctk.CTkLabel(
                            patterns_frame,
                            text=pattern_text,
                            anchor='w'
                        ).pack(fill='x', padx=10)

            except Exception as e:
                print(f"Error creating cluster UI: {str(e)}")
    
    except Exception as e:
        print(f"Error in display_clusters: {str(e)}")
        show_message(f"Error displaying clusters: {str(e)}")


def create_connectivity_section(r):
    global root, dendro_frame, current_ax, canvas, results_container, current_frame, cluster_count_label
    root = r
    main_frame = widgets.frame(r)
    input_frame = widgets.frame(main_frame)

    input_box = widgets.countTextbox(parent=input_frame, label='Input Neuron IDs')
    #input_box.insert("1.0", "1")  # TEMP

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
    eps_slider.pack(fill='x', padx=10, pady=(0, 5)) # Reduced padding below slider

    cluster_count_label = ctk.CTkLabel(
        sensitivity_column,
        text="Found 0 clusters",  # Initial text
        font=(FONT_FAMILY, 12, "bold"),
        text_color="#A9A9A9"
    )
    cluster_count_label.pack(pady=(5, 10)) # Added padding above and below

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
        on_slider_release.last_cluster_type = 'partners'  # Mark that we're using partner clustering
        get_clusters(input_text, handle_results, eps)

    def on_nblast():
        input_text = input_box.get('1.0', 'end').strip()
        eps = eps_var.get()

        if not input_text:
            show_message("Please enter neuron IDs")
            return
        show_loading_indicator(root)
        on_slider_release.last_cluster_type = 'nblast'  # Mark that we're using NBLAST
        get_nblast_clusters(input_text, handle_results, eps)

    cluster_button.configure(command=on_cluster)
    nblast_button.configure(command=on_nblast)

    def on_slider_move(value):
        value_label.configure(text=f"{float(value):.1f}")
        update_threshold_line(float(value))

    def on_slider_release(event):
        show_loading_indicator(root)
        # Store the current input to determine which clustering type to use
        current_input = input_box.get('1.0', 'end').strip()
        
        # If we have cached data and the data source is the same, just recluster
        # Otherwise, fetch new data with the new threshold
        if hasattr(on_slider_release, 'last_cluster_type'):
            if on_slider_release.last_cluster_type == 'nblast':
                get_nblast_clusters(None, handle_results, eps_var.get())
            else:
                get_clusters(current_input, handle_results, eps_var.get())
                

    eps_slider.configure(command=on_slider_move)
    eps_slider.bind("<ButtonRelease-1>", on_slider_release)