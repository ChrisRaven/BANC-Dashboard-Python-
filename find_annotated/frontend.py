from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *
import json
import os


def create_annotated_section(root, x, y):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

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

  get_ann_btn = ctk.CTkButton(
    frame,
    text='Get all annotations',
    command=get_all_annotations_handler,
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT
  )
  get_ann_btn.pack(pady=(BUTTON_PADDING, 20), padx=PADDING_X, fill='x')

  status_label = ctk.CTkLabel(frame, text='Click "Get all annotations" to start', text_color='Yellow')
  status_label.pack(anchor='w', padx=(PADDING_X + 20, 0))

  search_frame = ctk.CTkFrame(frame)
  search_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

  last_entered_value = None
  if os.path.exists('last_search_entry.json'):
    with open('last_search_entry.json', 'r') as file:
      last_entered_value = json.load(file)

  def save_search_entry():
    value = search_entry.get()
    with open('last_search_entry.json', 'w') as file:
      json.dump(value, file)

  search_entry = ctk.CTkEntry(search_frame, width=200, height=BUTTON_HEIGHT)
  if last_entered_value:
    search_entry.insert(0, last_entered_value)

  def on_search_entry_change(event=None):
    save_search_entry()

  search_entry.bind('<KeyRelease>', on_search_entry_change)
  search_entry.pack(side='left', expand=True, fill='x', padx=(0, BUTTON_PADDING))

  def find_button_callback():
    show_loading_indicator(root)
    search_text = search_entry.get().strip()

    def callback(found):
      results.delete('1.0', 'end')
      if isinstance(found, str) and found.startswith('MSG:'):
        results.insert('1.0', found[4:])
      elif found:
        results.insert('1.0', '\n'.join(str(row_id) for row_id in found))
      else:
        results.insert('1.0', 'No matches found')
      hide_loading_indicator()

    find_annotated(search_text, callback)

  find_button = ctk.CTkButton(
    search_frame,
    text='Find',
    command=find_button_callback,
    width=SMALL_BUTTON_WIDTH,
    height=BUTTON_HEIGHT
  )
  find_button.pack(side='right')

  results_label = ctk.CTkLabel(frame, text='Results', font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  results_label.pack(anchor='w', padx=PADDING_X)

  results = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_btn = ctk.CTkButton(
    frame,
    text='Copy',
    command=lambda: copy(results),
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT
  )
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
