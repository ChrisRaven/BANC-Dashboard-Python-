from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_connectivity_section(root, x, y):
  frame = ctk.CTkFrame(root)
  frame.place(x=x, y=y)

  input_label = ctk.CTkLabel(frame, text='Input IDs', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  input_label.pack(anchor='w', padx=PADDING_X)
  input_textfield = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
  input_textfield.pack()

  def get_clusters_handler():
    show_loading_indicator(root)
    input_text = input_textfield.get('1.0', 'end').strip()

    def callback(figure):
      # Handle messages vs results
      if isinstance(figure, str) and figure.startswith('MSG:'):
        # Remove any existing message labels
        for widget in frame.winfo_children():
          if isinstance(widget, ctk.CTkLabel) and hasattr(widget, 'is_message'):
            widget.destroy()

        message = figure.replace('MSG:', '')
        message_label = ctk.CTkLabel(frame, text=message, 
                                   font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
        message_label.is_message = True  # Add attribute to identify message labels
        message_label.pack(pady=(10, 0), padx=PADDING_X)
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
        error_label = ctk.CTkLabel(frame, text=error_message, font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
        error_label.pack(pady=(10, 0), padx=PADDING_X)

    get_clusters(input_text, callback)

  get_clusters_button = ctk.CTkButton(
    frame,
    text='Get clusters',
    width=TEXT_FIELD_WIDTH,
    height=BUTTON_HEIGHT,
    command=get_clusters_handler
  )
  get_clusters_button.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)
