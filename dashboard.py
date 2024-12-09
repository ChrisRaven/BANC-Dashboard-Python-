from functionalities.find_annotated import *
from functionalities.get_synaptic_partners import *
from functionalities.update_outdated import *
from functionalities.get_proofread import *
from functionalities.find_differences import *
from functionalities.check_coords import *
from common import *
import customtkinter as ctk
import platform
import os
import json


# Style constants
BUTTON_PADDING = 12
FRAME_WIDTH = 700       # Wider frames for better spacing
FRAME_HEIGHT = 850      # Taller frames
FONT_FAMILY = "Roboto"  # Modern Google font
FONT_SIZE = 12
FONT_WEIGHT = 'bold'
TEXT_FIELD_WIDTH = 680
TEXT_FIELD_HEIGHT = 150
LARGE_BUTTON_WIDTH = 380
SMALL_BUTTON_WIDTH = 200
BUTTON_HEIGHT = 35
PADDING_X = 20



def create_text_with_counter(parent, width, height, padx=PADDING_X):
    """Create a textbox with a line counter"""
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(pady=0, padx=padx, fill='x')
    
    # Create textbox first
    textbox = ctk.CTkTextbox(container, width=width, height=height)
    textbox.pack(fill='x')
    
    # Create counter label that floats over textbox
    counter = ctk.CTkLabel(container, text="0", anchor='e', 
                          fg_color="gray20", corner_radius=6)
    counter.place(relx=1.0, y=0, anchor='ne')
    
    def update_counter(event=None):
        text = textbox.get('1.0', 'end-1c')
        num_lines = len(text.split('\n')) if text.strip() else 0
        counter.configure(text=f"{num_lines}")
    
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
    
    return textbox

def create_annotated_section(root, x, y):
  """Create the annotated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  def get_all_annotations_callback(msg):
     hide_loading_indicator()
     if (msg):
       results.insert('1.0', msg)

  def get_all_annotations_handler():
    show_loading_indicator(root)
    get_entries("cell_info", get_all_annotations_callback)

  get_ann_btn = ctk.CTkButton(frame, text="Get All Annotations",
                command=get_all_annotations_handler,
                width=LARGE_BUTTON_WIDTH,
                height=BUTTON_HEIGHT)
  get_ann_btn.pack(pady=(BUTTON_PADDING, 20), padx=PADDING_X, fill='x')

  search_frame = ctk.CTkFrame(frame)
  search_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

  # Load last entered value from file
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

  # Save the search entry value whenever it changes
  def on_search_entry_change(event=None):
    save_search_entry()

  search_entry.bind('<KeyRelease>', on_search_entry_change)
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

  results = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_btn = ctk.CTkButton(frame, text="Copy",
               command=lambda: copy(results),
               width=LARGE_BUTTON_WIDTH,
               height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_synaptic_partners_section(root, x, y):
    frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    frame.place(x=x, y=y)

    # Source section (full width)
    source_label = ctk.CTkLabel(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    source_label.pack(anchor='w', padx=PADDING_X)

    # Source section remains the same but with reduced height
    source = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

    def get_synaptic_partners_handler():
        show_loading_indicator(root)
        source_text = source.get('1.0', 'end').strip()
        source_ids = clean_input(source_text)
        
        def callback(result):
            if isinstance(result, str) and result.startswith('MSG:'):
                msg_type, msg = result.split(':', 2)[1:]
                if msg_type == 'IN_PROGRESS':
                    partners.delete('1.0', 'end')
                    partners.insert('1.0', msg)
                elif msg_type == 'ERROR':
                    hide_loading_indicator()
                    partners.delete('1.0', 'end')
                    partners.insert('1.0', msg)
                elif msg_type == 'COMPLETE':
                    hide_loading_indicator()
            else:
                partners.delete('1.0', 'end')
                if result:
                    partners.insert('1.0', '\n'.join(str(id) for id in result))
                else:
                    partners.insert('1.0', 'No partners found')
                hide_loading_indicator()

        get_synaptic_partners(source_ids, callback)

    get_partners_btn = ctk.CTkButton(frame, text="Get Partners", 
                                   width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
    get_partners_btn.pack(pady=5, padx=PADDING_X, fill='x')
    get_partners_btn.configure(command=lambda: get_synaptic_partners_handler())

    # Three-column layout
    columns_frame = ctk.CTkFrame(frame, fg_color="transparent")  # Remove background
    columns_frame.pack(fill='x', padx=PADDING_X)

    # Left column (Partners)
    left_column = ctk.CTkFrame(columns_frame)
    left_column.pack(side='left', fill='both', expand=True, padx=(0, 0))
    
    partners_label = ctk.CTkLabel(left_column, text="Partners", 
                                font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    partners_label.pack(anchor='w')
    
    partners = create_text_with_counter(left_column, TEXT_FIELD_WIDTH//3, TEXT_FIELD_HEIGHT, padx=0)
    
    copy_partners = ctk.CTkButton(left_column, text="Copy", 
                                width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                command=lambda: copy(partners))
    copy_partners.pack(pady=(BUTTON_PADDING//2, 0))

    # Middle column (Controls) - with transparent background
    middle_column = ctk.CTkFrame(columns_frame, fg_color="transparent")
    middle_column.pack(side='left', fill='y', padx=PADDING_X//2)
    
    num_partners_label = ctk.CTkLabel(middle_column, 
                                    text="Number of most\ncommon partners",
                                    font=(FONT_FAMILY, FONT_SIZE))
    num_partners_label.pack(pady=(30, 0))
    
    number_of_partners = ctk.CTkEntry(middle_column, width=80, height=BUTTON_HEIGHT)
    number_of_partners.pack()
    number_of_partners.insert(0, '50')
    
    get_partners_of_partners_btn = ctk.CTkButton(middle_column,
                                               text="Get Partners\nof Partners",
                                               width=150,
                                               height=BUTTON_HEIGHT)
    get_partners_of_partners_btn.pack(pady=BUTTON_PADDING//2)
    get_partners_of_partners_btn.configure(command=lambda: get_partners_of_partners_handler())

    # Add checkbox
    add_original = ctk.CTkCheckBox(middle_column, text="Add the original partners")
    add_original.pack(pady=BUTTON_PADDING//2)
    add_original.select()  # Checked by default

    find_common_of_common = ctk.CTkCheckBox(middle_column, text="Find common of common", 
                                          command=lambda: update_filter_dust_label(find_common_of_common))
    find_common_of_common.pack(pady=BUTTON_PADDING//2)

    def update_filter_dust_label(checkbox):
        if checkbox.get():
            filter_dust_btn.configure(text="Get common of common")
        else:
            filter_dust_btn.configure(text="Filter dust")

    # Right column (Partners of Partners)
    right_column = ctk.CTkFrame(columns_frame)
    right_column.pack(side='left', fill='both', expand=True)
    
    partners_of_partners_label = ctk.CTkLabel(right_column, 
                                            text="Partners of Partners",
                                            font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    partners_of_partners_label.pack(anchor='w')
    
    partners_of_partners = create_text_with_counter(right_column, TEXT_FIELD_WIDTH//3, TEXT_FIELD_HEIGHT, padx=0)
    
    def copy_partners_of_partners_handler():
        partners_text = partners_of_partners.get('1.0', 'end').strip()
        if add_original.get():
            original_partners = partners.get('1.0', 'end').strip()
            combined_text = f"{partners_text}\n{original_partners}"
            # Convert to array, remove duplicates and back to string
            combined_array = combined_text.split('\n')
            unique_array = list(dict.fromkeys(combined_array))  # Remove duplicates while preserving order
            # Use OS-dependent newline character for separators
            newline = '\r\n' if platform.system() == 'Windows' else '\n'
            combined_text = newline.join(unique_array)
            copytext(combined_text)
        else:
            copy(partners_of_partners)
    copy_partners_of_partners = ctk.CTkButton(right_column, text="Copy",
                            width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT,
                            command=copy_partners_of_partners_handler)
    copy_partners_of_partners.pack(pady=(BUTTON_PADDING, 0))

    # Dust filter controls - adjusted width
    dust_frame = ctk.CTkFrame(frame)
    dust_frame.pack(fill='x', padx=PADDING_X, pady=(20, 10))
    
    filter_dust_btn = ctk.CTkButton(
      dust_frame,
      text="Remove dust",
      width=LARGE_BUTTON_WIDTH,
      height=BUTTON_HEIGHT,
      command=lambda: get_common_of_common_handler() if find_common_of_common.get() else filter_dust_handler()
    )
    filter_dust_btn.pack(side='left', padx=(0, BUTTON_PADDING))

    def get_common_of_common_handler():
        source_ids = clean_input(source.get('1.0', 'end').strip())
        num_of_common_partners = int(number_of_partners.get())
        results = get_common_of_common(source_ids, num_of_common_partners)
        filtered_results.delete('1.0', 'end')
        filtered_results.insert('1.0', '\n'.join(map(str, results)))

    def filter_dust_handler():
        show_loading_indicator(root)
        max_size = max_dust_size.get().strip()
        source_ids = clean_input(partners_of_partners.get('1.0', 'end').strip())
        if add_original.get():
            original_ids = clean_input(partners.get('1.0', 'end').strip())
            source_ids += original_ids
        filter_dust(source_ids, int(max_size), filter_dust_callback)

    def filter_dust_callback(result):
        if isinstance(result, str) and result.startswith('MSG:'):
            msg_type = result.split(':')[1]
            msg_content = ':'.join(result.split(':')[2:])
            match msg_type:
                case 'IN_PROGRESS':
                    filtered_results.delete('1.0', 'end')
                    filtered_results.insert('1.0', msg_content)
                case 'COMPLETE':
                    hide_loading_indicator()
                    filtered_results.delete('1.0', 'end')
                    filtered_results.insert('1.0', '\n'.join(map(str, result)))
                case 'ERROR':
                    hide_loading_indicator()
                    filtered_results.delete('1.0', 'end')
                    filtered_results.insert('1.0', msg_content)
        else:
            hide_loading_indicator()
            filtered_results.delete('1.0', 'end')
            filtered_results.insert('1.0', '\n'.join(map(str, result)))
    
    max_dust_size = ctk.CTkEntry(dust_frame, width=50, height=BUTTON_HEIGHT)
    max_dust_size.pack(side='right')
    max_dust_size.insert(0, '100')
    
    dust_size_label = ctk.CTkLabel(dust_frame, text="No of synapses",  # Shortened text
                                 font=(FONT_FAMILY, FONT_SIZE))
    dust_size_label.pack(side='right', padx=BUTTON_PADDING)


    # Add Filtered Results label
    filtered_results_label = ctk.CTkLabel(frame, text="Filtered Results", 
                                        font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    filtered_results_label.pack(anchor='w', padx=PADDING_X)

    # Filtered results with reduced height
    filtered_results = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
    
    copy_filtered = ctk.CTkButton(frame, text="Copy",
                               width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT,
                               command=lambda: copy(filtered_results))
    copy_filtered.pack(pady=(BUTTON_PADDING//2, BUTTON_PADDING), padx=PADDING_X, fill='x')

    def get_partners_of_partners_handler():
        show_loading_indicator(root)
        num_of_partners = number_of_partners.get().strip()
        partners_ids = clean_input(partners.get('1.0', 'end').strip())
        get_partners_of_partners(num_of_partners, get_partners_of_partners_callback, partners_ids)
    
    def get_partners_of_partners_callback(result):
        if isinstance(result, str) and result.startswith('MSG:'):
            # Parse message format
            msg_type = result.split(':')[1]
            msg_content = ':'.join(result.split(':')[2:])
            match msg_type:
                case 'IN_PROGRESS':
                    # Show progress message but keep loading indicator
                    partners_of_partners.delete('1.0', 'end')
                    partners_of_partners.insert('1.0', msg_content)
                case 'COMPLETE':
                    # Hide loading and show completion message
                    hide_loading_indicator()
                    partners_of_partners.delete('1.0', 'end')
                    partners_of_partners.insert('1.0', msg_content)
                case 'ERROR':
                    # Hide loading and show error
                    hide_loading_indicator()
                    partners_of_partners.delete('1.0', 'end')
                    partners_of_partners.insert('1.0', msg_content)
        else:
            # Results received, hide loading and display partners
            hide_loading_indicator()
            partners_of_partners.delete('1.0', 'end')
            partners_of_partners.insert('1.0', '\n'.join(map(str, result)))
    

def create_update_outdated_section(root, x, y):
  """Create the outdated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text="Source", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)

  source = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  update_btn = ctk.CTkButton(
    frame, text="Update", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
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

  source_without_outdated_label = ctk.CTkLabel(frame, text="Source Without Outdated", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_without_outdated_label.pack(anchor='w', padx=PADDING_X)

  source_without_outdated = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_source_without_outdated_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(source_without_outdated))
  copy_source_without_outdated_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  updated_label = ctk.CTkLabel(frame, text="Updated", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  updated_label.pack(anchor='w', padx=PADDING_X)

  updated = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_updated_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(updated))
  copy_updated_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_proofread_section(root, x, y):
  """Create the proofread section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)

  source_label = ctk.CTkLabel(frame, text="Source", font=(
    FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
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
    frame, text="Get", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT,
    command=get_proofread_handler)
  get_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  proofread_label = ctk.CTkLabel(
    frame, text="Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  proofread_label.pack(anchor='w', padx=PADDING_X)

  proofread = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_proofread_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(proofread))
  copy_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

  not_proofread_label = ctk.CTkLabel(
    frame, text="Not Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  not_proofread_label.pack(anchor='w', padx=PADDING_X)

  not_proofread = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)

  copy_not_proofread_btn = ctk.CTkButton(
    frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(not_proofread))
  copy_not_proofread_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_differences_section(root, x, y):
    """Create the differences section with modern styling"""
    diff_frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    diff_frame.place(x=x, y=y)

    # Textfield A with label and counter
    textfield_a_label = ctk.CTkLabel(diff_frame, text="A", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    textfield_a_label.pack(anchor='w', padx=PADDING_X)
    textfield_a = create_text_with_counter(diff_frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
    textfield_a.pack()

    # Textfield B with label and counter
    textfield_b_label = ctk.CTkLabel(diff_frame, text="B", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    textfield_b_label.pack(anchor='w', padx=PADDING_X, pady=(10, 0))
    textfield_b = create_text_with_counter(diff_frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
    textfield_b.pack()

    def find_differences_callback(results):
       a_only_textfield.delete('1.0', 'end')
       a_only_textfield.insert('1.0', "\n".join(map(str, results['a_only'])) if results['a_only'] else "None")
       
       a_plus_b_textfield.delete('1.0', 'end')
       a_plus_b_textfield.insert('1.0', "\n".join(map(str, results['a_plus_b'])) if results['a_plus_b'] else "None")
       
       b_only_textfield.delete('1.0', 'end')
       b_only_textfield.insert('1.0', "\n".join(map(str, results['b_only'])) if results['b_only'] else "None")
       
    def find_differences_handler():
       A = clean_input(textfield_a.get('1.0', 'end'))
       B = clean_input(textfield_b.get('1.0', 'end'))
       find_differences(A, B, find_differences_callback)

    # Button to Find Differences
    find_diff_button = ctk.CTkButton(diff_frame, text="Find Differences", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=find_differences_handler)
    find_diff_button.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')

    # Textfields for differences with counters and copy buttons
    differences_frame = ctk.CTkFrame(diff_frame, fg_color="transparent")  # Remove background
    differences_frame.pack(fill='x', padx=PADDING_X)

    # Column 1: A only
    a_only_column = ctk.CTkFrame(differences_frame)
    a_only_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
    
    a_only_label = ctk.CTkLabel(a_only_column, text="A only", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    a_only_label.pack(anchor='w')
    a_only_textfield = create_text_with_counter(a_only_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
    a_only_textfield.pack(fill='both', expand=True)
    a_only_copy_button = ctk.CTkButton(a_only_column, text="Copy", width=TEXT_FIELD_WIDTH // 3.5, height=BUTTON_HEIGHT, command=lambda: copy(a_only_textfield))
    a_only_copy_button.pack(fill='x')

    # Column 2: A + B
    a_plus_b_column = ctk.CTkFrame(differences_frame)
    a_plus_b_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
    
    a_plus_b_label = ctk.CTkLabel(a_plus_b_column, text="A + B", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    a_plus_b_label.pack(anchor='w')
    a_plus_b_textfield = create_text_with_counter(a_plus_b_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
    a_plus_b_textfield.pack(fill='both', expand=True)
    a_plus_b_copy_button = ctk.CTkButton(a_plus_b_column, text="Copy", width=TEXT_FIELD_WIDTH // 3.5, height=BUTTON_HEIGHT, command=lambda: copy(a_plus_b_textfield))
    a_plus_b_copy_button.pack(fill='x')

    # Column 3: B only
    b_only_column = ctk.CTkFrame(differences_frame)
    b_only_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
    
    b_only_label = ctk.CTkLabel(b_only_column, text="B only", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    b_only_label.pack(anchor='w')
    b_only_textfield = create_text_with_counter(b_only_column, TEXT_FIELD_WIDTH // 3.5, TEXT_FIELD_HEIGHT, padx=0)
    b_only_textfield.pack(fill='both', expand=True)
    b_only_copy_button = ctk.CTkButton(b_only_column, text="Copy", width=TEXT_FIELD_WIDTH // 3.5, height=BUTTON_HEIGHT, command=lambda: copy(b_only_textfield))
    b_only_copy_button.pack(fill='x')


def create_coords_section(root, x, y):
    """Create the coords section with modern styling"""
    frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT, fg_color="transparent")
    frame.place(x=x, y=y)

    data_label = ctk.CTkLabel(frame, text="Data", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    data_label.pack(anchor='w', padx=PADDING_X)
    data_textfield = create_text_with_counter(frame, TEXT_FIELD_WIDTH, TEXT_FIELD_HEIGHT)
    data_textfield.pack()

    
    def check_coords_handler():
      """Handler function for checking coordinates"""
      show_loading_indicator(root)
      data_text = data_textfield.get('1.0', 'end').strip()
#39976,46041,2637;53726,40883,1741;55333,24777,2427
#720575941605809023 720575941515598739 720575941160721276
      def callback(valid_coords, invalid_segment_ids):
        hide_loading_indicator()
        if len(valid_coords) or len(invalid_segment_ids):
          correct_coords_textfield.delete('1.0', 'end')
          correct_coords_textfield.insert('1.0', valid_coords)
          incorrect_ids_textfield.delete('1.0', 'end')
          incorrect_ids_textfield.insert('1.0', invalid_segment_ids)
        else:
          error_message = "Invalid coordinates or segment IDs. Please check and try again."
          ctk.CTkLabel(frame, text=error_message, font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT)).pack(pady=(10, 0), padx=PADDING_X)

      check_coords(data_text, callback)

    check_button = ctk.CTkButton(frame, text="Check", width=TEXT_FIELD_WIDTH, height=BUTTON_HEIGHT, command=check_coords_handler)
    check_button.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)

    correct_coords_column = ctk.CTkFrame(frame)
    correct_coords_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
    correct_coords_label = ctk.CTkLabel(correct_coords_column, text="Correct Coords", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    correct_coords_label.pack(anchor='w', padx=PADDING_X)
    correct_coords_textfield = create_text_with_counter(correct_coords_column, TEXT_FIELD_WIDTH // 2.5, TEXT_FIELD_HEIGHT, padx=(PADDING_X, 0))
    correct_coords_textfield.pack()
    correct_coords_copy_button = ctk.CTkButton(correct_coords_column, text="Copy", width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(correct_coords_textfield))
    correct_coords_copy_button.pack(fill='x', padx=(PADDING_X, 0), pady=BUTTON_PADDING)

    incorrect_ids_column = ctk.CTkFrame(frame)
    incorrect_ids_column.pack(side='left', fill='both', expand=True, padx=(5, 5))
    incorrect_ids_label = ctk.CTkLabel(incorrect_ids_column, text="Incorrect IDs", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
    incorrect_ids_label.pack(anchor='w', padx=PADDING_X)
    incorrect_ids_textfield = create_text_with_counter(incorrect_ids_column, TEXT_FIELD_WIDTH // 2.5, TEXT_FIELD_HEIGHT, padx=(0, PADDING_X))
    incorrect_ids_textfield.pack()
    incorrect_ids_copy_button = ctk.CTkButton(incorrect_ids_column, text="Copy", width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT, command=lambda: copy(incorrect_ids_textfield))
    incorrect_ids_copy_button.pack(fill='x', padx=(0, PADDING_X), pady=BUTTON_PADDING)


def main():
  """Initialize and run the main application"""
  ctk.set_appearance_mode("dark")
  ctk.set_default_color_theme("green")

  root = ctk.CTk()
  root.geometry('750x830')
  root.title('BANC Dashboard')
  root.resizable(False, False)

  tabview = ctk.CTkTabview(root)
  tabview.pack(expand=True, fill='both', padx=10, pady=10)

  # Create tabs
  tabs = {
    'annotated': tabview.add('Find Annotated'),
    'synaptic': tabview.add('Synaptic Partners'),
    'outdated': tabview.add('Update Outdated'),
    'proofread': tabview.add('Find Proofread'),
    'differences': tabview.add('Differences'),
    'coords': tabview.add('Check coords')
  }

  # Create sections
  create_annotated_section(tabs['annotated'], 0, 0)
  create_synaptic_partners_section(tabs['synaptic'], 0, 0)
  create_update_outdated_section(tabs['outdated'], 0, 0)
  create_proofread_section(tabs['proofread'], 0, 0)
  create_differences_section(tabs['differences'], 0, 0)
  create_coords_section(tabs['coords'], 0, 0)

  root.mainloop()


main()
