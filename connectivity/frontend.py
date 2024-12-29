from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_connectivity_section(root):
  frame = ctk.CTkFrame(root)
  frame.pack(fill='x')

  input = widgets.countTextbox(parent=frame, label='Input IDs')

  def get_clusters_handler():
    show_loading_indicator(root)
    input_text = input.get('1.0', 'end').strip()

    def callback(figure):
      # Handle messages vs results
      if isinstance(figure, str) and figure.startswith('MSG:'):
        # Remove any existing message labels
        for widget in frame.winfo_children():
          if isinstance(widget, ctk.CTkLabel) and hasattr(widget, 'is_message'):
            widget.destroy()

        message = figure.replace('MSG:', '')
        message_label = widgets.label(parent=frame, text=message)
        message_label.is_message = True
        return
      
      # Clear any existing message labels and canvas
      for widget in frame.winfo_children():
        if isinstance(widget, ctk.CTkLabel) and hasattr(widget, 'is_message'):
          widget.destroy()
        elif isinstance(widget, FigureCanvasTkAgg().get_tk_widget().__class__):
          widget.destroy()
      hide_loading_indicator()
      if figure:
        canvas = FigureCanvasTkAgg(figure, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=PADDING_X)
      else:
        error_message = 'Error generating clusters. Please check input and try again'
        error_label = widgets.label(parent=frame, text=error_message)

    get_clusters(input_text, callback)

  widgets.button(parent=frame, label='Get clusters', action=get_clusters_handler)
