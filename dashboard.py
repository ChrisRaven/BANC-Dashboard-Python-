import zstandard
from functionalities.get_synaptic_partners import get_synaptic_partners
from functionalities.update_outdated import update_outdated
from functionalities.get_all_annotations import get_all_annotations
from tkinter import ttk, LabelFrame, Label, Text, Button, Entry, Frame, LEFT, RIGHT, X, W, Y, Tk, END
from api_token import API_TOKEN
import pyarrow as pa
import pandas as pd
import requests
import json
from datetime import datetime
import threading


# Style constants
PRIMARY_COLOR = '#2196F3'    # Material Design Blue
SECONDARY_COLOR = 'orange'  # Material Design Amber
BG_COLOR = '#FAFAFA'        # Light gray background
TEXT_COLOR = '#212121'      # Dark gray text
BUTTON_BG_COLOR = SECONDARY_COLOR
BUTTON_FG_COLOR = 'white'
BUTTON_FONT_SIZE = 12
BUTTON_PADDING = 8
FRAME_PADDING_X = 15
FRAME_PADDING_Y = 10
TEXT_HEIGHT_SMALL = 8
TEXT_HEIGHT_LARGE = 12
FRAME_WIDTH = 480          # Slightly wider frames
FRAME_HEIGHT = 800
FONT_FAMILY = "Segoe UI"   # Modern font
FONT_SIZE = 10
FONT_WEIGHT = 'bold'
CORNER_RADIUS = 8         # Rounded corners

class ModernButton(Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            cursor='hand2'  # Hand cursor on hover
        )
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self['background'] = '#1976D2'  # Darker shade on hover

    def on_leave(self, e):
        self['background'] = BUTTON_BG_COLOR


# Global variable to store results
entries_result = None
loading_indicator = None

def show_loading_indicator(root):
    global loading_indicator
    if not loading_indicator:
        loading_indicator = ttk.Progressbar(root, mode='indeterminate', length=200)
        loading_indicator.place(relx=0.5, rely=0.95, anchor='center')
    loading_indicator.start()

def hide_loading_indicator():
    global loading_indicator
    if loading_indicator:
        loading_indicator.stop()
        loading_indicator.place_forget()

def get_entries(table_name, root):
    #global entries_result
    threading.Thread(target=lambda: make_request(table_name, root), daemon=True).start()

def make_request(table_name, root):
    global entries_result
    try:
        show_loading_indicator(root)
        
        url = "https://cave.fanc-fly.com/materialize/api/v3/datastack/brain_and_nerve_cord/query"
        params = {
            "return_pyarrow": "True",
            "arrow_format": "True", 
            "merge_reference": "False",
            "allow_missing_lookups": "False",
            "allow_invalid_root_ids": "False"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'zstd',
            'Authorization': f'Bearer {API_TOKEN}',
            'Cookie': f'middle_auth_token={API_TOKEN}'
        }
        
        data = {
            "table": table_name,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(url, params=params, headers=headers, json=data)
        arrow_data = pa.BufferReader(response.content)  # No decompression
        entries_result = pa.ipc.open_stream(arrow_data).read_all().to_pandas()
        print(entries_result)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        hide_loading_indicator()

    # Run request in separate thread to prevent GUI freezing
    

def create_annotated_section(root, x, y):
    style = ttk.Style()
    style.configure('Modern.TLabelframe', background=BG_COLOR)
    
    frame = LabelFrame(root, text="", padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y, 
                      font=(FONT_FAMILY, FONT_SIZE), bg=BG_COLOR)
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    get_ann_btn = ModernButton(frame, text="Get All Annotations", 
                              bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                              font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    get_ann_btn.pack(pady=(BUTTON_PADDING,10), fill=X)
    get_ann_btn.config(command=lambda: get_entries("cell_info", root))
    
    search_frame = Frame(frame, bg=BG_COLOR)
    search_frame.pack(fill=X, pady=BUTTON_PADDING)
    search_entry = Entry(search_frame, font=(FONT_FAMILY, FONT_SIZE),
                        relief='solid', bd=1)
    search_entry.pack(side=LEFT, expand=True, fill=X, padx=(0,BUTTON_PADDING))
    
    def search_entries():
        search_text = search_entry.get().strip()
        if not search_text:
            return
            
        # Split on comma or semicolon and clean up whitespace
        search_terms = [term.strip() for term in search_text.replace(';',',').split(',')]
        search_terms = set(filter(None, search_terms))  # Remove empty strings and make unique
        
        matching_rows = []
        for _, row in entries_result.iterrows():
            # Check tag column for exact match
            if row['tag'] in search_terms:
                matching_rows.append(row['pt_root_id'])
                continue
                
            # Split tag2 on spaces and check for matches
            if pd.notna(row['tag2']):  # Check if tag2 is not NaN
                tag2_terms = set(row['tag2'].split())
                if tag2_terms & search_terms:  # Check for intersection
                    matching_rows.append(row['pt_root_id'])
        
        # Display matching rows in results field
        results.delete('1.0', END)
        if matching_rows:
            results.insert('1.0', '\n'.join(str(row_id) for row_id in matching_rows))
        else:
            results.insert('1.0', 'No matches found')
    
    find_button = ModernButton(search_frame, text="Find",
                              bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                              font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT),
                              command=search_entries)
    find_button.pack(side=RIGHT)
    
    Label(frame, text="Results", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W, pady=(10,5))
    
    results = Text(frame, height=TEXT_HEIGHT_LARGE, font=(FONT_FAMILY, FONT_SIZE),
                  relief='solid', bd=1)
    results.pack(pady=BUTTON_PADDING, fill=X)
    
    def copy_results():
        # Get content from results text widget
        content = results.get('1.0', END).strip()
        if content:
            # Split on newlines and join with comma-space
            formatted_content = ', '.join(content.split('\n'))
            # Copy to clipboard
            root.clipboard_clear()
            root.clipboard_append(formatted_content)
            root.update()

    copy_btn = ModernButton(frame, text="Copy",
                           bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                           font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT),
                           command=copy_results)
    copy_btn.pack(pady=BUTTON_PADDING, fill=X)

def create_synaptic_section(root, x, y):
    frame = LabelFrame(root, text="", 
                      padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y,
                      font=(FONT_FAMILY, FONT_SIZE, "bold"), bg=BG_COLOR)
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    Label(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    source = Text(frame, height=TEXT_HEIGHT_SMALL, font=(FONT_FAMILY, FONT_SIZE),
                 relief='solid', bd=1)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    get_partners_btn = ModernButton(frame, text="Get Partners",
                                   bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                                   font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    get_partners_btn.pack(pady=BUTTON_PADDING, fill=X)
    
    Label(frame, text="Partners", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    partners = Text(frame, height=TEXT_HEIGHT_SMALL, font=(FONT_FAMILY, FONT_SIZE),
                   relief='solid', bd=1)
    partners.pack(pady=BUTTON_PADDING, fill=X)
    
    button_frame = Frame(frame, bg=BG_COLOR)
    button_frame.pack(fill=X, pady=BUTTON_PADDING)
    
    copy_btn = ModernButton(button_frame, text="Copy",
                           bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                           font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn.pack(side=LEFT, padx=(0,BUTTON_PADDING))
    
    partners_btn = ModernButton(button_frame, text="Get Partners of Partners",
                               bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                               font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    partners_btn.pack(side=LEFT, padx=(0,BUTTON_PADDING))
    
    entry = Entry(button_frame, width=5, font=(FONT_FAMILY, FONT_SIZE),
                 relief='solid', bd=1)
    entry.pack(side=LEFT)
    
    Label(frame, text="Partners of Most Common Partners",
          font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    common_partners = Text(frame, height=TEXT_HEIGHT_SMALL,
                          font=(FONT_FAMILY, FONT_SIZE),
                          relief='solid', bd=1)
    common_partners.pack(pady=BUTTON_PADDING, fill=X)
    
    copy_btn2 = ModernButton(frame, text="Copy",
                            bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                            font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn2.pack(pady=BUTTON_PADDING, fill=X)

def create_outdated_section(root, x, y):
    frame = LabelFrame(root, text="",
                      padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y,
                      font=(FONT_FAMILY, FONT_SIZE, "bold"), bg=BG_COLOR)
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    Label(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    source = Text(frame, height=TEXT_HEIGHT_LARGE, font=(FONT_FAMILY, FONT_SIZE),
                 relief='solid', bd=1)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    update_btn = ModernButton(frame, text="Update",
                             bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                             font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    update_btn.pack(pady=BUTTON_PADDING, fill=X)
    
    Label(frame, text="Source Without Outdated",
          font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    results = Text(frame, height=TEXT_HEIGHT_LARGE, font=(FONT_FAMILY, FONT_SIZE),
                  relief='solid', bd=1)
    results.pack(pady=BUTTON_PADDING, fill=X)
    
    copy_btn = ModernButton(frame, text="Copy",
                           bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                           font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn.pack(pady=BUTTON_PADDING, fill=X)
    
    Label(frame, text="Updated", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    updated = Text(frame, height=TEXT_HEIGHT_SMALL, font=(FONT_FAMILY, FONT_SIZE),
                  relief='solid', bd=1)
    updated.pack(pady=BUTTON_PADDING, fill=X)
    
    copy_btn2 = ModernButton(frame, text="Copy",
                            bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                            font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn2.pack(pady=BUTTON_PADDING, fill=X)

def create_proofread_section(root, x, y):
    frame = LabelFrame(root, text="",
                      padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y,
                      font=(FONT_FAMILY, FONT_SIZE, "bold"), bg=BG_COLOR)
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    Label(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    source = Text(frame, height=TEXT_HEIGHT_LARGE, font=(FONT_FAMILY, FONT_SIZE),
                 relief='solid', bd=1)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    get_btn = ModernButton(frame, text="Get",
                          bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                          font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    get_btn.pack(pady=BUTTON_PADDING, fill=X)
    
    Label(frame, text="Proofread", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    proofread = Text(frame, height=TEXT_HEIGHT_LARGE, font=(FONT_FAMILY, FONT_SIZE),
                     relief='solid', bd=1)
    proofread.pack(pady=BUTTON_PADDING, fill=X)
    
    copy_btn = ModernButton(frame, text="Copy",
                           bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                           font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn.pack(pady=BUTTON_PADDING, fill=X)
    
    Label(frame, text="Not Proofread", font=(FONT_FAMILY, FONT_SIZE, "bold"),
          bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor=W)
    
    not_proofread = Text(frame, height=TEXT_HEIGHT_SMALL,
                         font=(FONT_FAMILY, FONT_SIZE),
                         relief='solid', bd=1)
    not_proofread.pack(pady=BUTTON_PADDING, fill=X)
    
    copy_btn2 = ModernButton(frame, text="Copy",
                            bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR,
                            font=(FONT_FAMILY, BUTTON_FONT_SIZE, FONT_WEIGHT))
    copy_btn2.pack(pady=BUTTON_PADDING, fill=X)

def main():
    root = Tk()
    root.geometry('500x900')
    root.title('Dashboard')
    root.configure(bg=BG_COLOR)
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure('TNotebook', background=BG_COLOR)
    style.configure('TNotebook.Tab', padding=[6, 4], font=(FONT_FAMILY, FONT_SIZE))
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)
    
    annotated_frame = Frame(notebook, bg=BG_COLOR)
    synaptic_frame = Frame(notebook, bg=BG_COLOR)
    outdated_frame = Frame(notebook, bg=BG_COLOR)
    proofread_frame = Frame(notebook, bg=BG_COLOR)
    
    notebook.add(annotated_frame, text='Find Annotated')
    notebook.add(synaptic_frame, text='Get Synaptic Partners')
    notebook.add(outdated_frame, text='Update Outdated')
    notebook.add(proofread_frame, text='Find Proofread')
    
    create_annotated_section(annotated_frame, 0, 0)
    create_synaptic_section(synaptic_frame, 0, 0)
    create_outdated_section(outdated_frame, 0, 0)
    create_proofread_section(proofread_frame, 0, 0)
    
    root.mainloop()

main()

#get_synaptic_partners([720575941536100318,720575941338817903,720575941605725549])