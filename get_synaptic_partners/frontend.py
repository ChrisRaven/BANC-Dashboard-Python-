from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *

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
    