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
      def update_partners(text):
        partners.delete('1.0', 'end')
        partners.insert('1.0', text)

      status = result['status']
      content = result['content']
      if status == Status.IN_PROGRESS or status == Status.ERROR:
        update_partners(content)
      elif status == Status.FINISHED:
        if isinstance(content, str):
          update_partners(content)
        else:
          update_partners('\n'.join(str(id) for id in content))
      if status != Status.IN_PROGRESS:
        hide_loading_indicator()

    get_synaptic_partners(source_ids, callback,  direction=direction)

  get_partners_group_wrapper = widgets.column_wrapper(parent=left_column)
  target_selection_wrapper = widgets.column(parent=get_partners_group_wrapper)
  target_selection = widgets.radiogroup(parent=target_selection_wrapper, options=['upstream', 'downstream', 'both'])
  get_partners_wrapper = widgets.column(parent=get_partners_group_wrapper,  anchor='w')
  get_partners = widgets.button(parent=get_partners_wrapper, label='Get partners', action=get_synaptic_partners_handler)
  partners = widgets.countTextbox(parent=left_column, label='Partners')

  widgets.spacer(parent=left_column, height=46)

  def get_partners_of_partners_handler():
    show_loading_indicator(root)
    num_of_partners = no_of_partners.get().strip()
  
    def callback(result):
      def update_partners_of_partners(text):
        partners_of_partners.delete('1.0', 'end')
        partners_of_partners.insert('1.0', text)
      
      status = result['status']
      content = result['content']
      if status == Status.IN_PROGRESS or status == Status.ERROR:
        update_partners_of_partners(content)
      elif status == Status.FINISHED:
        if isinstance(content, str):
          update_partners_of_partners(content)
        else:
          update_partners_of_partners('\n'.join(str(id) for id in content))
      if status != Status.IN_PROGRESS:
        hide_loading_indicator()

    get_partners_of_partners(num_of_partners, callback)

  widgets.button(parent=left_column, label='Get partners of partners', action=get_partners_of_partners_handler)
  partners_of_partners = widgets.countTextbox(parent=left_column, label='Partners of partners')

  right_column = widgets.column(parent=frame, border=True)

  widgets.label(parent=right_column, text='For:')
  common_target_selection_group = widgets.radiogroup(parent=right_column, options=['partners', 'partners of partners'])

  widgets.spacer(parent=right_column, height=10)

  
  def get_common_handler():
    source_ids = clean_input(input_ids.get('1.0', 'end').strip())
    num_of_common_partners = int(no_of_partners.get())
    #results = get_common_of_common(source_ids, num_of_common_partners)
    filtered_partners.delete('1.0', 'end')
    filtered_partners.insert('1.0', '\n'.join(map(str, '')))

  def filter_dust_handler():
    show_loading_indicator(root)
    max_size = no_of_synapses.get().strip()
    source_ids = clean_input(partners_of_partners.get('1.0', 'end').strip())
    #filter_dust(source_ids, int(max_size), filter_dust_callback)

  def filter_dust_callback(result):
    if isinstance(result, str) and result.startswith('MSG:'):
      msg_type = result.split(':')[1]
      msg_content = ':'.join(result.split(':')[2:])
      match msg_type:
        case 'IN_PROGRESS':
          filtered_partners.delete('1.0', 'end')
          filtered_partners.insert('1.0', msg_content)
        case 'COMPLETE':
          hide_loading_indicator()
          filtered_partners.delete('1.0', 'end')
          filtered_partners.insert('1.0', '\n'.join(map(str, result)))
        case 'ERROR':
          hide_loading_indicator()
          filtered_partners.delete('1.0', 'end')
          filtered_partners.insert('1.0', msg_content)
    else:
      hide_loading_indicator()
      filtered_partners.delete('1.0', 'end')
      filtered_partners.insert('1.0', '\n'.join(map(str, result)))
  

  border1 = widgets.column_wrapper(parent=right_column, border=True)
  widgets.header(parent=border1, text='Get common partners')

  get_common_wrapper = widgets.column_wrapper(parent=border1)
  get_common_button_column = widgets.column(parent=get_common_wrapper, anchor='sw')
  get_common_button = widgets.button(parent=get_common_button_column, label='Get', action=get_common_handler)
  no_of_partners_wrapper = widgets.column(parent=get_common_wrapper)
  no_of_partners = widgets.labeledEntry(parent=no_of_partners_wrapper, label='No of partners', default_value='50')
  common_partners = widgets.countTextbox(parent=border1, label='Common partners')

  widgets.spacer(parent=right_column, height=10)
  
  border2 = widgets.column_wrapper(parent=right_column, border=True)
  widgets.header(parent=border2, text='Filter by number of synapses')

  filter_wrapper = widgets.column_wrapper(parent=border2)
  filter_button_column = widgets.column(parent=filter_wrapper, anchor='sw')
  filter_button = widgets.button(parent=filter_button_column, label='Filter', action=filter_dust_handler)
  no_of_synapses_wrapper = widgets.column(parent=filter_wrapper)
  no_of_synapses = widgets.labeledEntry(parent=no_of_synapses_wrapper, label='No of synapses', default_value='100')
  filtered_partners = widgets.countTextbox(parent=border2, label='Filtered')
  