from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *
import json
import os


def create_annotated_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  def get_all_annotations_callback(msg):
    hide_loading_indicator()
    if not msg:
      status_label.configure(text='')
      return

    if isinstance(msg, str) and msg.startswith('ERR:'):
      results.insert('1.0', msg.replace('ERR:', ''))
      results.insert('1.0', '')
      status_label.configure(text='')
    else:
      status_label.configure(text=f'Found {msg} annotations')

  def get_all_annotations_handler():
    show_loading_indicator(root)
    status_label.configure(text=f'Fetching annotations...')
    get_entries('cell_info', get_all_annotations_callback)

  widgets.spacer(parent=frame, height=20)

  widgets.button(
    parent=frame,
    label='Get all annotations',
    action=get_all_annotations_handler
  )

  status_label = ctk.CTkLabel(
    frame,
    text='Click "Get all annotations" to start',
    text_color='Yellow'
  )
  status_label.pack(anchor='w', padx=(PADDING_X + 20, 0))

  last_entered_value = None
  if os.path.exists('last_search_entry.json'):
    with open('last_search_entry.json', 'r') as file:
      last_entered_value = json.load(file)

  def save_search_entry():
    value = find_entry.get()
    with open('last_search_entry.json', 'w') as file:
      json.dump(value, file)

  widgets.spacer(parent=frame, height=20)

  find_wrapper = widgets.column_wrapper(parent=frame)
  find_entry_column = widgets.column(parent=find_wrapper)
  find_entry = widgets.labeledEntry(parent=find_entry_column, label='Annotations to search for')

  if last_entered_value:
    find_entry.delete(0, 'end')
    find_entry.insert(0, last_entered_value)

  
  def on_search_entry_change(event=None):
    nonlocal last_entered_value
    new_value = find_entry.get()
    if new_value != last_entered_value:
      last_entered_value = new_value
      save_search_entry()

  find_entry.bind('<KeyRelease>', on_search_entry_change)
  

  def find_button_callback():
    show_loading_indicator(root)
    find_text = find_entry.get().strip()

    def callback(found):
      if isinstance(found, str) and found.startswith('MSG:'):
        insert(results, found[4:])
      elif found:
        insert(results, '\n'.join(str(row_id) for row_id in found))
      else:
        insert(results, 'No matches found')
      hide_loading_indicator()

    find_annotated(find_text, callback)

  find_button_column = widgets.column(parent=find_wrapper, anchor='sw')
  widgets.button(
    parent=find_button_column,
    label='Find',
    action=find_button_callback
  )

  widgets.spacer(parent=frame, height=20)

  results = widgets.countTextbox(parent=frame, label='Results')
