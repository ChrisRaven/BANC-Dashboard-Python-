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
        insert(correct_coords, valid_coords)
        insert(incorrect_ids, invalid_segment_ids)
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
  

  def execute_code():
    code = exec_code.get('1.0', 'end').strip()
    execute(code)

  exec_code = widgets.countTextbox(parent=frame, label='Code')
  exec_button = widgets.button(parent=frame, label='Execute', action=execute_code)
