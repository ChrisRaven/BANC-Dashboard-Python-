__all__ = ['ctk', 'show_loading_indicator', 'hide_loading_indicator', 'widgets']

from constants import *
from .backend import *

import customtkinter as ctk
from types import SimpleNamespace


loading_indicator = None

def show_loading_indicator(root):
  global loading_indicator
  if not loading_indicator:
    loading_indicator = ctk.CTkProgressBar(
      root,
      mode='indeterminate',
      width=400,
    )
    loading_indicator.place(relx=0.5, rely=0.98, anchor='center')
  loading_indicator.start()


def hide_loading_indicator():
  global loading_indicator
  if loading_indicator:
    loading_indicator.stop()
    loading_indicator.place_forget()
    loading_indicator = None


def countTextbox(parent, label=''):
  container = ctk.CTkFrame(parent, fg_color='transparent')
  container.pack(fill='x', padx=2, pady=2)

  if label:
    lbl = ctk.CTkLabel(
      container,
      text=label,
      anchor='w',
      font=(
        FONT_FAMILY,
        12,
        'normal'
      ),
      text_color='#2CA06F'
    )
    lbl.pack(anchor='w', pady=(15, 0), padx=(5, 0)) # 15 to have some vertical space from the previous widget

  textbox = ctk.CTkTextbox(container, height=TEXT_FIELD_HEIGHT)
  textbox.pack(fill='x', anchor='nw', padx=2, pady=(0, 2))
  
  counter = ctk.CTkLabel(
    container,
    text='0',
    anchor='e',
    fg_color='gray20',
    corner_radius=6
  )
  counter.place(relx=1.0, x=-2, y=45, anchor='ne')

  copy_button = ctk.CTkButton(
    container,
    text='Copy',
    width=60,
    height=25,
    command=lambda: copytext(textbox.get('1.0', 'end-1c'))
  )
  copy_button.visible = False

  def show_copy_button(event):
    if not copy_button.visible:
      copy_button.place(relx=0.995, rely=0.85, anchor='ne')
      copy_button.visible = True

  def hide_copy_button(event):
    if copy_button.visible:
      copy_button.place_forget()
      copy_button.visible = False
  
  def update_counter(event=None):
    text = textbox.get('1.0', 'end-1c')
    num_lines = len(text.split('\n')) if text.strip() else 0
    counter.configure(text=f'{num_lines}')
  
  textbox.bind('<Enter>', show_copy_button)
  textbox.bind('<Leave>', hide_copy_button)
  copy_button.bind('<Enter>', show_copy_button)
  copy_button.bind('<Leave>', hide_copy_button)
  
  # Bind to both key events and textbox modifications
  textbox.bind('<KeyRelease>', update_counter)
  
  # Override insert and delete methods to trigger counter update
  original_insert = textbox.insert
  original_delete = textbox.delete
  
  def insert_wrapper(*args, **kwargs):
    original_insert(*args, **kwargs)
    update_counter()
  
  def delete_wrapper(*args, **kwargs):
    original_delete(*args, **kwargs)
    update_counter()
      
  textbox.insert = insert_wrapper
  textbox.delete = delete_wrapper
  textbox.pack()
  
  return textbox


def label(parent, text):
    label = ctk.CTkLabel(
      parent,
      text=text,
      font=(
        FONT_FAMILY,
        FONT_SIZE,
        FONT_WEIGHT
      )
    )
    label.pack(anchor='nw', padx=2, pady=2)
    return label


def header(parent, text):
  label = ctk.CTkLabel(
    parent,
    text=text,
    font=(
      FONT_FAMILY,
      16,
      'normal'
    )
  )
  label.pack(anchor='nw', padx=5, pady=5)
  return label


def button(parent, label, action):
  button = ctk.CTkButton(
    parent,
    text=label,
    height=BUTTON_HEIGHT,
    command=action,
  )

  button.pack(pady=(5, 2), fill='x', padx=2)
  return button


def entry(parent, default_value='0'):
  entry = ctk.CTkEntry(
    parent,
    height=BUTTON_HEIGHT
  )
  entry.insert(0, default_value) 
  entry.pack(fill='x', anchor='nw', padx=2, pady=2)
  return entry


def labeledEntry(parent, label, default_value='0'):
  lbl = widgets.label(parent=parent, text=label)
  lbl.pack_configure(pady=(2, 0))
  entry = widgets.entry(parent=parent, default_value=default_value)
  entry.pack_configure(pady=(0, 2))
  return entry


def column_wrapper(parent, border=False):
  col = ctk.CTkFrame(parent, border_width=1 if border else 0, border_color='#444')
  col.pack(fill='x', expand=True, padx=5, pady=5, anchor='nw')
  return col


def column(parent, anchor='nw', border=False):
  col = ctk.CTkFrame(parent, fg_color='transparent', border_width=1 if border else 0, border_color='#444')
  col.pack(side='left', fill='x', expand=True, padx=5, pady=2, anchor=anchor)
  return col


def spacer(parent, height=20):
  col = ctk.CTkFrame(parent, height=height, fg_color='transparent')
  col.pack(fill='x', expand=True, side='top', padx=2, pady=2)


def radiogroup(parent, options, callback=None):
  frame = ctk.CTkFrame(parent, fg_color='transparent')
  frame.pack(fill='x', pady=10, padx=10, anchor='nw')

  selected_option = ctk.StringVar(value=options[0])

  def on_selection_change():
    if callback:
      callback(selected_option.get())

  for option in options:
    rb = ctk.CTkRadioButton(
      frame, 
      text=option, 
      value=option, 
      variable=selected_option, 
      command=on_selection_change
    )
    rb.pack(pady=5, anchor='nw')
  
  def get_selected():
    return selected_option.get()
  
  frame.get_selected = get_selected

  return frame


widgets = SimpleNamespace(
  countTextbox = countTextbox,
  label = label,
  header = header,
  button = button,
  entry = entry,
  labeledEntry = labeledEntry,
  column_wrapper = column_wrapper,
  column=column,
  spacer=spacer,
  radiogroup=radiogroup
)
