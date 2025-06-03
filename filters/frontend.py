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
  
  def filter_bounding_box_handler():
    show_loading_indicator(root)
    min_x = min_x_input.get().strip()
    min_y = min_y_input.get().strip()
    min_z = min_z_input.get().strip()
    max_x = max_x_input.get().strip()
    max_y = max_y_input.get().strip()
    max_z = max_z_input.get().strip()
    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    filter_by_bounding_box(source_ids, min_x, min_y, min_z, max_x, max_y, max_z, filter_bounding_box_callback)

  def filter_bounding_box_callback(result):
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
    

  widgets.label(parent=frame, text='Filter by bounding box')

  filter_by_bounding_box_wrapper = widgets.column_wrapper(parent=frame)
  
  col1 = widgets.column(parent=filter_by_bounding_box_wrapper)
  # Create 2x3 matrix of input fields
  input_matrix = widgets.column_wrapper(parent=col1)
  x_constraints = widgets.column_wrapper(parent=input_matrix)
  y_constraints = widgets.column_wrapper(parent=input_matrix)
  z_constraints = widgets.column_wrapper(parent=input_matrix)
  
  # Row 1 inputs
  min_x_col = widgets.column(parent=x_constraints)
  min_x_input = widgets.entry(parent=min_x_col, width=60)
  max_x_col = widgets.column(parent=x_constraints)
  max_x_input = widgets.entry(parent=max_x_col, width=60)
  
  # Row 2 inputs
  min_y_col = widgets.column(parent=y_constraints)
  min_y_input = widgets.entry(parent=min_y_col, width=60)
  max_y_col = widgets.column(parent=y_constraints)
  max_y_input = widgets.entry(parent=max_y_col, width=60)
  
  # Row 3 inputs
  min_z_col = widgets.column(parent=z_constraints)
  min_z_input = widgets.entry(parent=min_z_col, width=60)
  max_z_col = widgets.column(parent=z_constraints)
  max_z_input = widgets.entry(parent=max_z_col, width=60)
  
  # Create two countTextboxes
  col2 = widgets.column(parent=filter_by_bounding_box_wrapper)
  inside_results = widgets.countTextbox(parent=col2, label='Inside')
  col3 = widgets.column(parent=filter_by_bounding_box_wrapper)
  outside_results = widgets.countTextbox(parent=col3, label='Outside')

  widgets.button(parent=frame, label='Filter', action=filter_bounding_box_handler)
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
