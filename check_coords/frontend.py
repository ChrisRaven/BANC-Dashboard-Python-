from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_coords_section(root, x, y):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT, fg_color='transparent')
  frame.place(x=x, y=y)

  data_label = ctk.CTkLabel(frame, text='Data', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  data_label.pack(anchor='w', padx=PADDING_X)
  data_textfield = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
  data_textfield.pack()

  
  def check_coords_handler():
    show_loading_indicator(root)
    data_text = data_textfield.get('1.0', 'end').strip()

    def callback(valid_coords, invalid_segment_ids):
      hide_loading_indicator()
      if len(valid_coords) or len(invalid_segment_ids):
        correct_coords_textfield.delete('1.0', 'end')
        correct_coords_textfield.insert('1.0', valid_coords)
        incorrect_ids_textfield.delete('1.0', 'end')
        incorrect_ids_textfield.insert('1.0', invalid_segment_ids)
      else:
        error_message = 'Invalid coordinates or segment IDs. Please check and try again'
        error_label = ctk.CTkLabel(frame, text=error_message, font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
        error_label.pack(pady=(10, 0), padx=PADDING_X)

    check_coords(data_text, callback)

  check_button = ctk.CTkButton(
    frame,
    text='Check',
    width=TEXT_FIELD_WIDTH,
    height=BUTTON_HEIGHT,
    command=check_coords_handler
  )
  check_button.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

  correct_coords_column = ctk.CTkFrame(frame)
  correct_coords_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
  correct_coords_label = ctk.CTkLabel(
    correct_coords_column,
    text='Correct Coords',
    font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT)
  )
  correct_coords_label.pack(anchor='w', padx=PADDING_X)
  correct_coords_textfield = create_text_with_counter(
    correct_coords_column,
    TEXT_FIELD_WIDTH // 2.5,
    TEXT_FIELD_HEIGHT,
    padx=(PADDING_X, 0)
  )
  correct_coords_textfield.pack()
  correct_coords_copy_button = ctk.CTkButton(
    correct_coords_column,
    text='Copy',
    width=SMALL_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(correct_coords_textfield)
  )
  correct_coords_copy_button.pack(fill='x', padx=(PADDING_X, 0), pady=BUTTON_PADDING)

  incorrect_ids_column = ctk.CTkFrame(frame)
  incorrect_ids_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
  incorrect_ids_label = ctk.CTkLabel(
    incorrect_ids_column,
    text='Incorrect IDs',
    font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT)
  )
  incorrect_ids_label.pack(anchor='w', padx=PADDING_X)
  incorrect_ids_textfield = create_text_with_counter(
    incorrect_ids_column,
    TEXT_FIELD_WIDTH // 2.5,
    TEXT_FIELD_HEIGHT,
    padx=(0, PADDING_X)
  )
  incorrect_ids_textfield.pack()
  incorrect_ids_copy_button = ctk.CTkButton(
    incorrect_ids_column,
    text='Copy',
    width=SMALL_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=lambda: copy(incorrect_ids_textfield)
  )
  incorrect_ids_copy_button.pack(fill='x', padx=(0, PADDING_X), pady=BUTTON_PADDING)
