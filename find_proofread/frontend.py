from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_proofread_section(root, x, y):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text='Source', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  def get_proofread_handler():
    show_loading_indicator(root)
    source_data = clean_input(source.get('1.0', 'end'))
    
    def proofread_callback(proofread_ids, not_proofread_ids):
      hide_loading_indicator()
      proofread.delete('1.0', 'end')
      proofread.insert('1.0', '\n'.join(map(str, proofread_ids)))
      not_proofread.delete('1.0', 'end')
      not_proofread.insert('1.0', '\n'.join(map(str, not_proofread_ids)))
      
    get_proofread(source_data, proofread_callback)

  get_proofread_btn = ctk.CTkButton(
    frame,
    text='Get',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=get_proofread_handler
  )
  get_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  proofread_label = ctk.CTkLabel(frame, text='Proofread', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  proofread_label.pack(anchor='w', padx=PADDING_X)

  proofread = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_proofread_btn = ctk.CTkButton(
    frame,
    text='Copy',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(proofread)
  )
  copy_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  not_proofread_label = ctk.CTkLabel(frame, text='Not Proofread', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  not_proofread_label.pack(anchor='w', padx=PADDING_X)

  not_proofread = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_not_proofread_btn = ctk.CTkButton(
    frame,
    text='Copy',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(not_proofread)
  )
  copy_not_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
