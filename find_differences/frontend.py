from constants import *
from utils.backend import *
from utils.frontend import *
from .backend import *


def create_differences_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  textbox_a = widgets.countTextbox(parent=frame, label='A')
  textbox_b = widgets.countTextbox(parent=frame, label='B')
  textbox_large_neurons = widgets.countTextbox(parent=frame, label='Large neurons')
  checkbox_subtract_large_neurons = widgets.checkbox(parent=frame, label='Subtract large neurons', checked=True)

  def find_differences_callback(results):
    def fill(field, target):
      text = '\n'.join(map(str, results[field])) if results[field] else 'None'
      insert(target, text)

    fill('a_only', a_only_textbox)
    fill('a_plus_b', a_plus_b_textbox)
    fill('b_only', b_only_textbox)

  def find_differences_handler():
    A = clean_input(textbox_a.get('1.0', 'end'))
    B = clean_input(textbox_b.get('1.0', 'end'))
    large_neurons = clean_input(textbox_large_neurons.get('1.0', 'end'))
    subtract_large_neurons = checkbox_subtract_large_neurons.is_checked()
    find_differences(A, B, large_neurons, subtract_large_neurons, find_differences_callback)

  widgets.button(
    parent=frame,
    label='Find Differences',
    action=find_differences_handler
  )

  results_wrapper = widgets.column_wrapper(parent=frame)

  a_only_column = widgets.column(parent=results_wrapper)
  a_only_textbox = widgets.countTextbox(parent=a_only_column, label='A only')

  a_plus_b_column = widgets.column(parent=results_wrapper)
  a_plus_b_textbox = widgets.countTextbox(parent=a_plus_b_column, label='A + B')

  b_only_column = widgets.column(parent=results_wrapper)
  b_only_textbox = widgets.countTextbox(parent=b_only_column, label='B only')
  