from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *


def create_update_outdated_section(root, x, y):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text='Source', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  update_btn = ctk.CTkButton(frame, text='Update', width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  update_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  update_btn.configure(command=lambda: update_handler())

  def update_handler():
    show_loading_indicator(root)
    source_data = clean_input(source.get('1.0', 'end'))
    update_outdated(source_data, update_callback)
    
  def update_callback(result1, result2):
    hide_loading_indicator()
    source_without_outdated.delete('1.0', 'end')
    source_without_outdated.insert('1.0', '\n'.join(map(str, result1)))
    updated.delete('1.0', 'end')
    updated.insert('1.0', '\n'.join(map(str, result2)))

  source_without_outdated_label = ctk.CTkLabel(
    frame,
    text='Source Without Outdated',
    font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT)
  )
  source_without_outdated_label.pack(anchor='w', padx=PADDING_X)

  source_without_outdated = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_source_without_outdated_btn = ctk.CTkButton(
    frame,
    text='Copy',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(source_without_outdated)
  )
  copy_source_without_outdated_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  updated_label = ctk.CTkLabel(frame, text='Updated', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  updated_label.pack(anchor='w', padx=PADDING_X)

  updated = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_updated_btn = ctk.CTkButton(
    frame,
    text='Copy',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(updated)
  )
  copy_updated_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
