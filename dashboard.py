from functionalities.find_annotated import *
from functionalities.get_synaptic_partners import *
from functionalities.update_outdated import update_outdated
from functionalities.get_all_annotations import get_all_annotations
from common import *
import customtkinter as ctk


# Style constants
BUTTON_PADDING = 12
FRAME_WIDTH = 600       # Wider frames for better spacing
FRAME_HEIGHT = 850      # Taller frames
FONT_FAMILY = "Roboto"  # Modern Google font
FONT_SIZE = 12
FONT_WEIGHT = 'bold'
TEXT_FIELD_WIDTH = 580
TEXT_FIELD_HEIGHT = 150
LARGE_BUTTON_WIDTH = 380
SMALL_BUTTON_WIDTH = 200
BUTTON_HEIGHT = 35
PADDING_X = 20


def create_annotated_section(root, x, y):
  """Create the annotated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  def get_all_annotations_calllback():
    show_loading_indicator(root)
    get_entries("cell_info", hide_loading_indicator)

  get_ann_btn = ctk.CTkButton(frame, text="Get All Annotations",
                command=get_all_annotations_calllback,
                width=LARGE_BUTTON_WIDTH,
                height=BUTTON_HEIGHT)
  get_ann_btn.pack(pady=(BUTTON_PADDING, 20), padx=PADDING_X, fill='x')

  search_frame = ctk.CTkFrame(frame)
  search_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

  search_entry = ctk.CTkEntry(search_frame, width=200, height=BUTTON_HEIGHT)
  search_entry.pack(side='left', expand=True,
          fill='x', padx=(0, BUTTON_PADDING))

  def find_button_callback():
    show_loading_indicator(root)
    search_text = search_entry.get().strip()

    def callback(found):
      results.delete('1.0', 'end')
      if found:
        results.insert('1.0', '\n'.join(str(row_id)
                for row_id in found))
      else:
        results.insert('1.0', 'No matches found')
      hide_loading_indicator()

    find_annotated(search_text, callback)

  find_button = ctk.CTkButton(search_frame, text="Find",
                command=find_button_callback,
                width=SMALL_BUTTON_WIDTH,
                height=BUTTON_HEIGHT)
  find_button.pack(side='right')

  results_label = ctk.CTkLabel(frame, text="Results", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  results_label.pack(anchor='w', padx=PADDING_X)

  results = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  results.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_btn = ctk.CTkButton(frame, text="Copy",
               command=lambda: copy(results),
               width=LARGE_BUTTON_WIDTH,
               height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_synaptic_partners_section(root, x, y):
  """Create the synaptic partners section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text="Source", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  get_partners_btn = ctk.CTkButton(
    frame, text="Get Partners", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  get_partners_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  get_partners_btn.configure(command=lambda: get_synaptic_partners_handler())

  partners_label = ctk.CTkLabel(frame, text="Partners", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  partners_label.pack(anchor='w', padx=PADDING_X)

  partners = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  partners.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  def get_synaptic_partners_handler():
    show_loading_indicator(root)
    get_synaptic_partners(clean_input(source.get('1.0', 'end').strip()), get_synaptic_partners_callback)

  def get_synaptic_partners_callback(result_partners):
    hide_loading_indicator()
    partners.delete('1.0', 'end')
    partners.insert('1.0', '\n'.join(map(str, result_partners)))

  button_frame = ctk.CTkFrame(frame)
  button_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

  copy_partners = ctk.CTkButton(button_frame,
              text="Copy",
              width=SMALL_BUTTON_WIDTH,
              height=BUTTON_HEIGHT,
              command=lambda: copy(partners))
  copy_partners.pack(side='left', padx=(0, BUTTON_PADDING))

  number_of_partners = ctk.CTkEntry(button_frame,
              width=100,
              height=BUTTON_HEIGHT)
  number_of_partners.pack(side='right')
  number_of_partners.insert(0, '50')

  get_partners_of_partners_btn = ctk.CTkButton(button_frame,
              text="Get Partners of Partners",
              width=SMALL_BUTTON_WIDTH,
              height=BUTTON_HEIGHT)
  get_partners_of_partners_btn.pack(side='right', padx=(0, BUTTON_PADDING))
  get_partners_of_partners_btn.configure(command=lambda: get_partners_of_partners_handler())

  def get_partners_of_partners_handler():
    show_loading_indicator(root)
    num_of_partners = number_of_partners.get().strip()
    get_partners_of_partners(num_of_partners, get_partners_of_partners_callback)
    
  def get_partners_of_partners_callback(result):
    hide_loading_indicator()
    partners_of_partners.delete('1.0', 'end')
    partners_of_partners.insert('1.0', '\n'.join(map(str, result)))

  partners_of_partners_lbl = ctk.CTkLabel(frame, text="Partners of Most Common Partners", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  partners_of_partners_lbl.pack(anchor='w', padx=PADDING_X)

  partners_of_partners = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  partners_of_partners.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_partners_of_partners = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(partners_of_partners))
  copy_partners_of_partners.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

def create_outdated_section(root, x, y):
  """Create the outdated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text="Source", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  update_btn = ctk.CTkButton(
    frame, text="Update", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  update_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  results_label = ctk.CTkLabel(frame, text="Source Without Outdated", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  results_label.pack(anchor='w', padx=PADDING_X)

  results = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  results.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  updated_label = ctk.CTkLabel(frame, text="Updated", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  updated_label.pack(anchor='w', padx=PADDING_X)

  updated = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  updated.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_btn2 = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn2.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_proofread_section(root, x, y):
  """Create the proofread section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text="Source", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  get_btn = ctk.CTkButton(
    frame, text="Get", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  get_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  proofread_label = ctk.CTkLabel(
    frame, text="Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  proofread_label.pack(anchor='w', padx=PADDING_X)

  proofread = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  proofread.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  not_proofread_label = ctk.CTkLabel(
    frame, text="Not Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  not_proofread_label.pack(anchor='w', padx=PADDING_X)

  not_proofread = ctk.CTkTextbox(
    frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  not_proofread.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  copy_btn2 = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn2.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def main():
  """Initialize and run the main application"""
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("green")

  root = ctk.CTk()
  root.geometry('650x900')  # Wider window
  root.title('BANC Dashboard')
  root.resizable(False, False)

  tabview = ctk.CTkTabview(root)
  tabview.pack(expand=True, fill='both', padx=10, pady=10)

  # Create tabs
  tabs = {
    'annotated': tabview.add('Find Annotated'),
    'synaptic': tabview.add('Synaptic Partners'),
    'outdated': tabview.add('Update Outdated'),
    'proofread': tabview.add('Find Proofread')
  }

  # Create sections
  create_annotated_section(tabs['annotated'], 0, 0)
  create_synaptic_partners_section(tabs['synaptic'], 0, 0)
  create_outdated_section(tabs['outdated'], 0, 0)
  create_proofread_section(tabs['proofread'], 0, 0)

  root.mainloop()


main()
