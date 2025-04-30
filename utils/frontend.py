__all__ = ['ctk', 'show_loading_indicator', 'hide_loading_indicator', 'insert', 'widgets']

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

def insert(where, what):
  where.delete('1.0', 'end')
  where.insert('1.0', what)

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
    lbl.pack(anchor='w', pady=(5, 0), padx=(5, 0))

  textbox = ctk.CTkTextbox(container, height=TEXT_FIELD_HEIGHT)
  textbox.pack(fill='x', anchor='nw', padx=2, pady=(0, 2))
  
  counter = ctk.CTkLabel(
    container,
    text='0',
    anchor='e',
    fg_color='gray20',
    corner_radius=6
  )
  counter.place(relx=1.0, x=-2, y=33, anchor='ne')

  copy_button = ctk.CTkButton(
    container,
    text='Copy',
    width=60,
    height=25
  )
  copy_button.visible = False
  
  # Store original button color
  original_button_color = copy_button._fg_color
  
  def copy_with_feedback():
    # Copy text to clipboard
    text_content = textbox.get('1.0', 'end-1c')
    copytext(text_content)
    
    orange = "#F77F00"
    copy_button.configure(fg_color=orange)
    container.after(250, lambda: copy_button.configure(fg_color=original_button_color))
    container.after(500, lambda: copy_button.configure(fg_color=orange))
    container.after(750, lambda: copy_button.configure(fg_color=original_button_color))
    container.after(1000, lambda: copy_button.configure(fg_color=orange))
    container.after(1250, lambda: copy_button.configure(fg_color=original_button_color))
  
  # Assign the feedback-enabled copy function
  copy_button.configure(command=copy_with_feedback)
  
  # Track mouse over status for both elements
  mouse_over_textbox = False
  mouse_over_button = False

  def update_button_visibility():
    if mouse_over_textbox or mouse_over_button:
      if not copy_button.visible:
        copy_button.place(relx=0.995, rely=0.85, anchor='ne')
        copy_button.visible = True
    else:
      if copy_button.visible:
        copy_button.place_forget()
        copy_button.visible = False

  def textbox_enter(event):
    nonlocal mouse_over_textbox
    mouse_over_textbox = True
    update_button_visibility()

  def textbox_leave(event):
    nonlocal mouse_over_textbox
    mouse_over_textbox = False
    # Small delay to allow transition between elements
    container.after(100, update_button_visibility)
  
  def button_enter(event):
    nonlocal mouse_over_button
    mouse_over_button = True
    update_button_visibility()

  def button_leave(event):
    nonlocal mouse_over_button
    mouse_over_button = False
    update_button_visibility()
  
  def update_counter(event=None):
    text = textbox.get('1.0', 'end-1c')
    num_lines = len(text.split('\n')) if text.strip() else 0
    counter.configure(text=f'{num_lines}')
  
  textbox.bind('<Enter>', textbox_enter)
  textbox.bind('<Leave>', textbox_leave)
  copy_button.bind('<Enter>', button_enter)
  copy_button.bind('<Leave>', button_leave)
  
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


def frame(parent):
  frame = ctk.CTkFrame(parent)
  frame.pack(fill='both', expand=True)
  return frame


def column_wrapper(parent, border=False):
  col = ctk.CTkFrame(parent, fg_color='transparent', border_width=1 if border else 0, border_color='#444')
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

def checkbox(parent, label, checked=False):
  var = ctk.BooleanVar(value=checked)
  checkbox = ctk.CTkCheckBox(parent, text=label, variable=var)
  checkbox.pack(pady=5, anchor='nw')
  
  def is_checked():
    return var.get()
  
  checkbox.is_checked = is_checked

  return checkbox


widgets = SimpleNamespace(
  countTextbox = countTextbox,
  label = label,
  header = header,
  button = button,
  entry = entry,
  labeledEntry = labeledEntry,
  frame = frame,
  column_wrapper = column_wrapper,
  column = column,
  spacer = spacer,
  radiogroup = radiogroup,
  checkbox = checkbox,
  insert = insert
)
