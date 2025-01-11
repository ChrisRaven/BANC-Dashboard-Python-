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
    height_range = Z[:, 2].max() - Z[:, 2].min()
    if height_range > 0:
        padding = 0.05 * height_range  # Add padding of 10% of the range on both sides
        Z_normalized = Z.copy()
        Z_normalized[:, 2] = (Z[:, 2] - Z[:, 2].min() + padding) / (height_range + 2 * padding)
    else:
        Z_normalized = Z
    return Z_normalized

def update_dendrogram(distances, eps):
    global current_ax, threshold_line, canvas, averaged_nblast_scores
    averaged_nblast_scores = 1 - distances

    if current_ax is not None:
      current_ax.clear()
    threshold_line = None

    aba_vec = squareform(distances, checks=False)
    Z = linkage(aba_vec, method="ward")

    color_threshold = eps / 100
    dendrogram(
        _normalize_linkage(Z),
        ax=current_ax,
        no_labels=True,
        color_threshold=color_threshold,
        above_threshold_color='gray',
        leaf_rotation=0
    )

    threshold_line = current_ax.axhline(y=color_threshold, color='r', linestyle='--')
    current_ax.set_ylim(bottom=0, top=1.0)

    yticks = np.linspace(0, 1, 11)
    current_ax.set_yticks(yticks)
    current_ax.set_yticklabels([f"{y * 100:.0f}" for y in yticks])
    current_ax.set_xticks([])
    current_ax.figure.tight_layout()
    canvas.draw()

def display_clusters(data):
    global current_frame, cluster_count_label

    if isinstance(data, str) and data.startswith("MSG:"):
        show_message(data[4:])
        return

    try:
        if 'distances' in data:
            update_dendrogram(data['distances'], data['eps_used'])

        # Reuse the existing frame or create if none
        if current_frame is None:
            current_frame = ctk.CTkScrollableFrame(results_container)
            current_frame.pack(fill='both', expand=True)
        else:
            # Clear existing cluster frames within the scrollable frame
            for widget in current_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):  # Only destroy cluster frames
                    widget.destroy()
        '''
        # Update the cluster count label
        if cluster_count_label:
            cluster_count_label.configure(text=f"Found 1 clusters")
        for cluster in data['clusters']:
            try:
                cluster_frame = ctk.CTkFrame(current_frame)
                cluster_frame.pack(fill='x', pady=5, padx=5)

                header_frame = ctk.CTkFrame(cluster_frame)
                header_frame.pack(fill='x', padx=5, pady=5)

                title = f"Cluster ({cluster['size']} neurons)"
                ctk.CTkLabel(
                    header_frame,
                    text=title,
                    font=(FONT_FAMILY, 12, "bold")
                ).pack(side='left')

                copy_cmd = lambda n=cluster['neurons']: copy_neurons(n)
                ctk.CTkButton(
                    header_frame,
                    text="Copy IDs",
                    width=80,
                    height=25,
                    command=copy_cmd
                ).pack(side='right')

                neuron_text = ctk.CTkTextbox(cluster_frame, height=50)
                neuron_text.pack(fill='x', padx=5, pady=(0, 5))
                neuron_text.insert('1.0', ' '.join(map(str, cluster['neurons'])))
                neuron_text.configure(state='disabled')

            except Exception as e:
                print(f"Error creating cluster UI: {str(e)}")
    '''
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
    eps_var = tk.DoubleVar(value=50)
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
        get_clusters(input_text, handle_results, eps)

    def on_nblast():
        input_text = input_box.get('1.0', 'end').strip()
        eps = eps_var.get()

        if not input_text:
            show_message("Please enter neuron IDs")
            return
        show_loading_indicator(root)
        get_nblast_clusters(input_text, handle_results, eps)

    cluster_button.configure(command=on_cluster)
    nblast_button.configure(command=on_nblast)

    def on_slider_move(value):
        value_label.configure(text=f"{float(value):.1f}")
        update_threshold_line(float(value))

    def on_slider_release(event):
        show_loading_indicator(root)
        get_nblast_clusters(None, handle_results, eps_var.get())
        #update_cluster_colors(float(eps_var.get()))
        #recluster(float(eps_var.get()), handle_results)

    eps_slider.configure(command=on_slider_move)
    eps_slider.bind("<ButtonRelease-1>", on_slider_release)