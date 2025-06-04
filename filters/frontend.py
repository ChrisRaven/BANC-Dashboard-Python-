from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *


def create_filters_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  input_ids = widgets.countTextbox(parent=frame, label='Input ids')


  def filter_dust_handler():
    show_loading_indicator(root)
    min_size = min_size_input.get().strip()
    min_frags = min_fragments.get().strip()
    max_frags = max_fragments.get().strip()

    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    filter_by_no_of_fragments(source_ids, int(min_size), int(min_frags), int(max_frags), filter_dust_callback)

  def filter_dust_callback(result):
    if isinstance(result, str) and result.startswith('MSG:'):
      msg_type = result.split(':')[1]
      msg_content = ':'.join(result.split(':')[2:])
      match msg_type:
        case 'IN_PROGRESS':
          insert(filtered_partners_small, msg_content)
        case 'COMPLETE':
          hide_loading_indicator()
          insert(filtered_partners_small, '\n'.join(map(str, result['small'])))
          insert(filtered_partners_middle, '\n'.join(map(str, result['middle'])))
          insert(filtered_partners_large, '\n'.join(map(str, result['large'])))
        case 'ERROR':
          hide_loading_indicator()
          insert(filtered_partners_small, msg_content)
    else:
      hide_loading_indicator()
      insert(filtered_partners_small, '\n'.join(map(str, result['small'])))
      insert(filtered_partners_middle, '\n'.join(map(str, result['middle'])))
      insert(filtered_partners_large, '\n'.join(map(str, result['large'])))
  

  filter_wrapper = widgets.column_wrapper(parent=frame)

  filter_button_column = widgets.column(parent=filter_wrapper, anchor='sw')
  widgets.button(parent=filter_button_column, label='Filter', action=filter_dust_handler)
  min_size_wrapper = widgets.column(parent=filter_wrapper)
  min_size_input = widgets.labeledEntry(parent=min_size_wrapper, label='Min size', default_value='10000')
  min_fragments_wrapper = widgets.column(parent=filter_wrapper)
  min_fragments = widgets.labeledEntry(parent=min_fragments_wrapper, label='Min frags', default_value='2')
  max_fragments_wrapper = widgets.column(parent=filter_wrapper)
  max_fragments = widgets.labeledEntry(parent=max_fragments_wrapper, label='Max frags', default_value='100')

  
  filtered_results_wrapper = widgets.column_wrapper(parent=frame)
  small_column = widgets.column(parent=filtered_results_wrapper)
  filtered_partners_small = widgets.countTextbox(parent=small_column, label='Small')
  middle_column = widgets.column(parent=filtered_results_wrapper)
  filtered_partners_middle = widgets.countTextbox(parent=middle_column, label='Middle')
  large_column = widgets.column(parent=filtered_results_wrapper)
  filtered_partners_large = widgets.countTextbox(parent=large_column, label='Large')
  
  def filter_by_planes_handler():
    show_loading_indicator(root)
    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    planes = planes_textbox.get('1.0', 'end').strip()
    filter_by_planes(source_ids, planes, filter_by_planes_callback)

  def filter_by_planes_callback(result):
    if isinstance(result, str) and result.startswith('MSG:'):
      msg_type = result.split(':')[1]
      msg_content = ':'.join(result.split(':')[2:])
      match msg_type:
        case 'IN_PROGRESS':
          insert(inside_results, msg_content)
          insert(outside_results, msg_content)
        case 'COMPLETE':
          hide_loading_indicator()
          insert(inside_results, '\n'.join(map(str, result['inside'])))
          insert(outside_results, '\n'.join(map(str, result['outside'])))
        case 'ERROR':
          hide_loading_indicator()
          insert(inside_results, msg_content)
          insert(outside_results, msg_content)
    else:
      hide_loading_indicator()
      insert(inside_results, '\n'.join(map(str, result['inside']))) 
      insert(outside_results, '\n'.join(map(str, result['outside']))) 
    

  widgets.label(parent=frame, text='Filter by planes')

  filter_by_planes_wrapper = widgets.column_wrapper(parent=frame)
  
  col1 = widgets.column(parent=filter_by_planes_wrapper)
  planes_textbox = widgets.countTextbox(parent=col1, label='Planes')
  col2 = widgets.column(parent=filter_by_planes_wrapper)
  inside_results = widgets.countTextbox(parent=col2, label='Inside')
  col3 = widgets.column(parent=filter_by_planes_wrapper)
  outside_results = widgets.countTextbox(parent=col3, label='Outside')

  widgets.button(parent=frame, label='Filter', action=filter_by_planes_handler)











'''
from caveclient import CAVEclient;
import pandas as pd;
client = CAVEclient(datastack_name='brain_and_nerve_cord', auth_token=API_TOKEN);
bbox = [[0, 0, 80000], [2000000, 10000000, 85000]]
result=client.materialize.synapse_query(pre_ids=[720575941502620978], bounding_box=bbox);
pd.options.display.max_columns = None
pd.options.display.max_rows = None
print('-----')
print(result['post_pt_root_id'].to_string(index=False))
'''
