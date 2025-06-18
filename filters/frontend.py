from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *

# Try to import matplotlib, but handle gracefully if not available
try:
  import matplotlib.pyplot as plt
  import matplotlib
  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
  import numpy as np
  MATPLOTLIB_AVAILABLE = True
  # Set matplotlib to use a non-interactive backend
  matplotlib.use('TkAgg')
except ImportError:
  MATPLOTLIB_AVAILABLE = False
  print("Warning: matplotlib not available. Histogram display will be disabled.")

def create_filters_section(root):
  # Create a scrollable frame for the entire content
  scrollable_frame = ctk.CTkScrollableFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  scrollable_frame.pack(fill='both', expand=True)

  frame = ctk.CTkFrame(scrollable_frame, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  filter_settings = widgets.column_wrapper(parent=frame)

  input_col = widgets.column(parent=filter_settings)
  input_ids = widgets.countTextbox(parent=input_col, label='Input ids')
  params_col = widgets.column(parent=filter_settings)
  thresholds = widgets.labeledEntry(parent=params_col, label='Thresholds', width=120, default_value='20, 600')
  planes_textbox = widgets.countTextbox(parent=params_col, label='Planes')

  def filter_by_planes_handler():
    show_loading_indicator(root)
    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    planes = planes_textbox.get('1.0', 'end').strip()
    thresholds_text = thresholds.get().strip()
    thresholds_values = [int(x.strip()) for x in thresholds_text.split(',')]
    if len(thresholds_values) != 2:
      hide_loading_indicator()
      insert(smaller_results, "Error: Please provide exactly two threshold values separated by comma")
      insert(middle_results, "Error: Please provide exactly two threshold values separated by comma")
      insert(larger_results, "Error: Please provide exactly two threshold values separated by comma")
      return
    
    def callback_with_thresholds(result):
      filter_by_planes_callback(result, thresholds_values)
    
    filter_by_planes(source_ids, planes, thresholds_values, callback_with_thresholds)

  def filter_by_planes_callback(result, thresholds_values):
    if isinstance(result, str) and result.startswith('MSG:'):
      msg_type = result.split(':')[1]
      msg_content = ':'.join(result.split(':')[2:])
      match msg_type:
        case 'IN_PROGRESS':
          insert(smaller_results, msg_content)
          insert(middle_results, msg_content)
          insert(larger_results, msg_content)
        case 'COMPLETE':
          hide_loading_indicator()
          insert(smaller_results, '\n'.join(map(str, result['smaller'])))
          insert(middle_results, '\n'.join(map(str, result['middle'])))
          insert(larger_results, '\n'.join(map(str, result['larger'])))
        case 'ERROR':
          hide_loading_indicator()
          insert(smaller_results, msg_content)
          insert(middle_results, msg_content)
          insert(larger_results, msg_content)
    else:
      hide_loading_indicator()
      insert(smaller_results, '\n'.join(map(str, result['smaller'])))
      insert(middle_results, '\n'.join(map(str, result['middle'])))
      insert(larger_results, '\n'.join(map(str, result['larger'])))
      
      # Display histogram if leaf counts are available
      if 'leaf_counts' in result and result['leaf_counts'] and MATPLOTLIB_AVAILABLE and ax and canvas and canvas_widget:
        display_histogram(result['leaf_counts'], thresholds_values, ax, canvas, canvas_widget)

  def display_histogram(leaf_counts, thresholds, ax, canvas, canvas_widget):
    if not MATPLOTLIB_AVAILABLE:
      return
      
    try:
      # Filter out counts over 1000
      filtered_counts = [c for c in leaf_counts if c <= 1000]

      # Clear the entire figure and recreate a single axes
      ax.figure.clf()
      ax = ax.figure.add_subplot(111)
      
      # Calculate statistics
      mean_count = np.mean(filtered_counts)
      median_count = np.median(filtered_counts)
      std_count = np.std(filtered_counts)
      min_count = np.min(filtered_counts)
      max_count = np.max(filtered_counts)
      
      # Create histogram with log y-axis
      counts, bins, _ = ax.hist(filtered_counts, bins=50, alpha=0.7, color='skyblue', edgecolor='black', log=True)
      
      # Add vertical lines for thresholds
      smaller_threshold, larger_threshold = thresholds
      ax.axvline(x=smaller_threshold, color='red', linestyle='--', linewidth=2, label=f'Smaller threshold ({smaller_threshold})')
      ax.axvline(x=larger_threshold, color='orange', linestyle='--', linewidth=2, label=f'Larger threshold ({larger_threshold})')
      
      # Add mean and median lines
      ax.axvline(x=mean_count, color='green', linestyle='-', linewidth=2, label=f'Mean ({mean_count:.1f})')
      ax.axvline(x=median_count, color='purple', linestyle='-', linewidth=2, label=f'Median ({median_count:.1f})')
      
      # Customize plot
      ax.set_xlabel('Number of Leaves')
      ax.set_ylabel('Frequency (log scale)')
      ax.set_title(f'Distribution of Leaf Counts (n={len(filtered_counts)})')
      ax.legend()
      ax.grid(True, alpha=0.3)
      
      # Add statistics text box
      stats_text = f'Min: {min_count:.0f}\nMax: {max_count:.0f}\nStd: {std_count:.1f}'
      ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
      
      # Show the canvas
      canvas_widget.pack(fill='x', padx=2, pady=2)
      canvas.draw()
    except Exception as e:
      print(f"Error displaying histogram: {e}")
      canvas_widget.pack_forget()

  widgets.label(parent=frame, text='Filter by planes')

  filter_by_planes_wrapper = widgets.column_wrapper(parent=frame)
  
  col1 = widgets.column(parent=filter_by_planes_wrapper)
  smaller_results = widgets.countTextbox(parent=col1, label='Smaller')
  col2 = widgets.column(parent=filter_by_planes_wrapper)
  middle_results = widgets.countTextbox(parent=col2, label='Middle')
  col3 = widgets.column(parent=filter_by_planes_wrapper)
  larger_results = widgets.countTextbox(parent=col3, label='Larger')

  widgets.button(parent=frame, label='Filter', action=filter_by_planes_handler)

  # Create histogram frame at the end, only if matplotlib is available
  histogram_frame = None
  fig = None
  ax = None
  canvas = None
  canvas_widget = None
  
  if MATPLOTLIB_AVAILABLE:
    histogram_frame = ctk.CTkFrame(frame, fg_color='transparent')
    histogram_frame.pack(fill='x', padx=2, pady=5)
    
    # Create matplotlib figure for histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    canvas = FigureCanvasTkAgg(fig, histogram_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='x', padx=2, pady=2)
    
    # Initially hide the histogram
    canvas_widget.pack_forget()
