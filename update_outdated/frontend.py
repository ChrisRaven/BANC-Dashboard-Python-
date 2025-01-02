from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *


def create_update_outdated_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  source = widgets.countTextbox(parent=frame, label='Source')
  widgets.button(parent=frame, label='Update', action=lambda: update_handler())

  def update_handler():
    show_loading_indicator(root)
    source_data = clean_input(source.get('1.0', 'end'))
    update_outdated(source_data, update_callback)
    
  def update_callback(result1, result2):
    hide_loading_indicator()
    insert(source_without_outdated, '\n'.join(map(str, result1)))
    insert(updated, '\n'.join(map(str, result2)))

  source_without_outdated = widgets.countTextbox(parent=frame, label='Source without Outdated')
  updated = widgets.countTextbox(parent=frame, label='Updated')
