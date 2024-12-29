from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_coords_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  data_textfield = widgets.countTextbox(parent=frame, label='Data')

  def check_coords_handler():
    show_loading_indicator(root)
    data_text = data_textfield.get('1.0', 'end').strip()

    def callback(valid_coords, invalid_segment_ids):
      hide_loading_indicator()
      if len(valid_coords) or len(invalid_segment_ids):
        correct_coords.delete('1.0', 'end')
        correct_coords.insert('1.0', valid_coords)
        incorrect_ids.delete('1.0', 'end')
        incorrect_ids.insert('1.0', invalid_segment_ids)
      else:
        error_message = 'Invalid coordinates or segment IDs. Please check and try again'
        widgets.label(parent=frame, text=error_message)
    check_coords(data_text, callback)

  widgets.button(parent=frame, label='Check', action=check_coords_handler)

  wrapper = widgets.column_wrapper(parent=frame)
  left_column = widgets.column(parent=wrapper)
  correct_coords = widgets.countTextbox(parent=left_column, label='Correct coords')
  right_column = widgets.column(parent=wrapper)
  incorrect_ids = widgets.countTextbox(parent=right_column, label='Incorrect IDs')
  