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

  def get_most_common_handler():
    source_group = common_source_selection.get_selected()
    num_of_most_common_partners = int(no_of_partners.get())
    results = get_most_common(source_group, num_of_most_common_partners)
    insert(common_partners, '\n'.join(map(str, results)))

  border2 = widgets.column_wrapper(parent=right_column, border=True)
  widgets.header(parent=border2, text='Get common partners')

  get_common_wrapper = widgets.column_wrapper(parent=border2)
  get_common_button_column = widgets.column(parent=get_common_wrapper, anchor='sw')
  widgets.button(parent=get_common_button_column, label='Get', action=get_most_common_handler)
  no_of_partners_wrapper = widgets.column(parent=get_common_wrapper)
  no_of_partners = widgets.labeledEntry(parent=no_of_partners_wrapper, label='No of partners', default_value='50')
  common_partners = widgets.countTextbox(parent=border2, label='Common partners')
