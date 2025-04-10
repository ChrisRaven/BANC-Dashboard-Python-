from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *


def create_synaptic_partners_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  left_column = widgets.column(parent=frame, border=True)
  
  input_ids = widgets.countTextbox(parent=left_column, label='Input IDs')

  def get_synaptic_partners_handler():
    show_loading_indicator(root)
    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    direction = target_selection.get_selected()
    
    def callback(result):
      status = result['status']
      content = result['content']
      if status == Status.IN_PROGRESS or status == Status.ERROR:
        insert(partners, content)
      elif status == Status.FINISHED:
        if isinstance(content, str):
          insert(partners, content)
        else:
          insert(partners, '\n'.join(str(id) for id in content))
      if status != Status.IN_PROGRESS:
        hide_loading_indicator()

    get_synaptic_partners(source_ids, callback, direction=direction)

  get_partners_group_wrapper = widgets.column_wrapper(parent=left_column)
  target_selection_wrapper = widgets.column(parent=get_partners_group_wrapper)
  target_selection = widgets.radiogroup(parent=target_selection_wrapper, options=['upstream', 'downstream', 'both'])
  get_partners_wrapper = widgets.column(parent=get_partners_group_wrapper,  anchor='w')
  widgets.button(parent=get_partners_wrapper, label='Get partners', action=get_synaptic_partners_handler)
  partners = widgets.countTextbox(parent=left_column, label='Partners')

  def get_partners_of_partners_handler():
    show_loading_indicator(root)
    num_of_partners = no_of_most_common_partners.get().strip()
  
    def callback(result):
      status = result['status']
      content = result['content']
      if status == Status.IN_PROGRESS or status == Status.ERROR:
        insert(partners_of_partners, content)
      elif status == Status.FINISHED:
        if isinstance(content, str):
          insert(partners_of_partners, content)
        else:
          insert(partners_of_partners, '\n'.join(str(id) for id in content))
      if status != Status.IN_PROGRESS:
        hide_loading_indicator()

    get_partners_of_partners(num_of_partners, callback)

  border1 = widgets.column_wrapper(parent=left_column, border=True)
  widgets.header(parent=border1, text='Get partners of partners')

  most_common_wrapper = widgets.column_wrapper(parent=border1)
  partners_of_partners_button_column = widgets.column(parent=most_common_wrapper, anchor='sw')
  widgets.button(parent=partners_of_partners_button_column, label='Get', action=get_partners_of_partners_handler)
  no_of_most_common_partners_wrapper = widgets.column(parent=most_common_wrapper)
  no_of_most_common_partners  = widgets.labeledEntry(parent=no_of_most_common_partners_wrapper, label='No of partners', default_value=50)

  partners_of_partners = widgets.countTextbox(parent=border1, label='Partners of partners')

  right_column = widgets.column(parent=frame, border=True)

  widgets.label(parent=right_column, text='For:')
  common_source_selection = widgets.radiogroup(parent=right_column, options=['input IDs', 'partners', 'partners of partners'])

  widgets.spacer(parent=right_column, height=30)
  
  def get_most_common_handler():
    source_group = common_source_selection.get_selected()
    num_of_most_common_partners = int(no_of_partners.get())
    results = get_most_common(source_group, num_of_most_common_partners)
    insert(common_partners, '\n'.join(map(str, results)))

  def filter_dust_handler():
    show_loading_indicator(root)
    min_size = min_size_input.get().strip()
    source_group = common_source_selection.get_selected()
    #filter_dust(source_group, int(min_no_of_synapses), filter_dust_callback)

    # source_ids used only, if the source_group is selected to 'input IDs'
    source_text = input_ids.get('1.0', 'end').strip()
    source_ids = clean_input(source_text)
    filter_by_no_of_fragments(source_group, int(min_size), 50, source_ids, filter_dust_callback)

  def filter_dust_callback(result):
    if isinstance(result, str) and result.startswith('MSG:'):
      msg_type = result.split(':')[1]
      msg_content = ':'.join(result.split(':')[2:])
      match msg_type:
        case 'IN_PROGRESS':
          insert(filtered_partners, msg_content)
        case 'COMPLETE':
          hide_loading_indicator()
          insert(filtered_partners, '\n'.join(map(str, result)))
        case 'ERROR':
          hide_loading_indicator()
          insert(filtered_partners, msg_content)
    else:
      hide_loading_indicator()
      insert(filtered_partners, '\n'.join(map(str, result)))
  

  border2 = widgets.column_wrapper(parent=right_column, border=True)
  widgets.header(parent=border2, text='Get common partners')

  get_common_wrapper = widgets.column_wrapper(parent=border2)
  get_common_button_column = widgets.column(parent=get_common_wrapper, anchor='sw')
  widgets.button(parent=get_common_button_column, label='Get', action=get_most_common_handler)
  no_of_partners_wrapper = widgets.column(parent=get_common_wrapper)
  no_of_partners = widgets.labeledEntry(parent=no_of_partners_wrapper, label='No of partners', default_value='50')
  common_partners = widgets.countTextbox(parent=border2, label='Common partners')

  widgets.spacer(parent=right_column, height=10)
  
  border3 = widgets.column_wrapper(parent=right_column, border=True)
  widgets.header(parent=border3, text='Filter by min size')

  filter_wrapper = widgets.column_wrapper(parent=border3)
  filter_button_column = widgets.column(parent=filter_wrapper, anchor='sw')
  widgets.button(parent=filter_button_column, label='Filter', action=filter_dust_handler)
  min_size_wrapper = widgets.column(parent=filter_wrapper)
  min_size_input = widgets.labeledEntry(parent=min_size_wrapper, label='Min size', default_value='10000')
  filtered_partners = widgets.countTextbox(parent=border3, label='Filtered')
  