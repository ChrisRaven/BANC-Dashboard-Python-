from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_differences_section(root, x, y):
  diff_frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  diff_frame.place(x=x, y=y)

  textfield_a_label = ctk.CTkLabel(diff_frame, text='A', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  textfield_a_label.pack(anchor='w', padx=PADDING_X)
  textfield_a = create_text_with_counter(diff_frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
  textfield_a.pack()

  textfield_b_label = ctk.CTkLabel(diff_frame, text='B', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  textfield_b_label.pack(anchor='w', padx=PADDING_X, pady=(10, 0))
  textfield_b = create_text_with_counter(diff_frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
  textfield_b.pack()

  def find_differences_callback(results):
    a_only_textfield.delete('1.0', 'end')
    a_only_textfield.insert('1.0', '\n'.join(map(str, results['a_only'])) if results['a_only'] else 'None')
    
    a_plus_b_textfield.delete('1.0', 'end')
    a_plus_b_textfield.insert('1.0', '\n'.join(map(str, results['a_plus_b'])) if results['a_plus_b'] else 'None')
     
    b_only_textfield.delete('1.0', 'end')
    b_only_textfield.insert('1.0', '\n'.join(map(str, results['b_only'])) if results['b_only'] else 'None')
     
  def find_differences_handler():
    A = clean_input(textfield_a.get('1.0', 'end'))
    B = clean_input(textfield_b.get('1.0', 'end'))
    find_differences(A, B, find_differences_callback)

  find_diff_button = ctk.CTkButton(
    diff_frame,
    text='Find Differences',
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    command=find_differences_handler
  )
  find_diff_button.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  differences_frame = ctk.CTkFrame(diff_frame, fg_color='transparent')  # Remove background
  differences_frame.pack(fill='x', padx=PADDING_X)

  a_only_column = ctk.CTkFrame(differences_frame)
  a_only_column.pack(side='left', fill='both', expand=True, padx=(5, 5))

  a_only_label = ctk.CTkLabel(a_only_column, text='A only', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  a_only_label.pack(anchor='w')
  a_only_textfield = create_text_with_counter(a_only_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
  a_only_textfield.pack(fill='both', expand=True)
  a_only_copy_button = ctk.CTkButton(
    a_only_column,
    text='Copy',
    width=TEXT_FIELD_WIDTH // 3.5,
    height=BUTTON_HEIGHT,
    command=lambda: copy(a_only_textfield)
  )
  a_only_copy_button.pack(fill='x')

  a_plus_b_column = ctk.CTkFrame(differences_frame)
  a_plus_b_column.pack(side='left', fill='both', expand=True, padx=(5, 5))

  a_plus_b_label = ctk.CTkLabel(a_plus_b_column, text='A + B', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  a_plus_b_label.pack(anchor='w')
  a_plus_b_textfield = create_text_with_counter(a_plus_b_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
  a_plus_b_textfield.pack(fill='both', expand=True)
  a_plus_b_copy_button = ctk.CTkButton(
    a_plus_b_column,
    text='Copy',
    width=TEXT_FIELD_WIDTH // 3.5,
    height=BUTTON_HEIGHT,
    command=lambda: copy(a_plus_b_textfield)
  )
  a_plus_b_copy_button.pack(fill='x')

  b_only_column = ctk.CTkFrame(differences_frame)
  b_only_column.pack(side='left', fill='both', expand=True, padx=(5, 5))

  b_only_label = ctk.CTkLabel(b_only_column, text='B only', font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  b_only_label.pack(anchor='w')
  b_only_textfield = create_text_with_counter(b_only_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
  b_only_textfield.pack(fill='both', expand=True)
  b_only_copy_button = ctk.CTkButton(
    b_only_column,
    text='Copy',
    width=TEXT_FIELD_WIDTH // 3.5,
    height=BUTTON_HEIGHT,
    command=lambda: copy(b_only_textfield)
  )
  b_only_copy_button.pack(fill='x')