from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_proofread_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  source = widgets.countTextbox(parent=frame, label='Source')

  def get_proofread_handler():
    show_loading_indicator(root)
    source_data = clean_input(source.get('1.0', 'end'))
    
    def proofread_callback(proofread_ids, not_proofread_ids):
      hide_loading_indicator()
      insert(proofread, '\n'.join(map(str, proofread_ids)))
      insert(not_proofread, '\n'.join(map(str, not_proofread_ids)))
      
    get_proofread(source_data, proofread_callback)

  widgets.button(parent=frame, label='Get', action=get_proofread_handler)

  proofread = widgets.countTextbox(parent=frame, label='Proofread')
  not_proofread = widgets.countTextbox(parent=frame, label='Not Proofread')
