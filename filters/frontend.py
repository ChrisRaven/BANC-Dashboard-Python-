from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *


def create_filters_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
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
    filter_by_planes(source_ids, planes, thresholds_values, filter_by_planes_callback)

  def filter_by_planes_callback(result):
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
    

  widgets.label(parent=frame, text='Filter by planes')

  filter_by_planes_wrapper = widgets.column_wrapper(parent=frame)
  
  col1 = widgets.column(parent=filter_by_planes_wrapper)
  smaller_results = widgets.countTextbox(parent=col1, label='Smaller')
  col2 = widgets.column(parent=filter_by_planes_wrapper)
  middle_results = widgets.countTextbox(parent=col2, label='Middle')
  col3 = widgets.column(parent=filter_by_planes_wrapper)
  larger_results = widgets.countTextbox(parent=col3, label='Larger')

  widgets.button(parent=frame, label='Filter', action=filter_by_planes_handler)
