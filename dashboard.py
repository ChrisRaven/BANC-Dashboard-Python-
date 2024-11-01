import zstandard
from functionalities.get_synaptic_partners import get_synaptic_partners
from functionalities.update_outdated import update_outdated
from functionalities.get_all_annotations import get_all_annotations
import customtkinter as ctk
from api_token import API_TOKEN
import pyarrow as pa
import pandas as pd
import requests
from datetime import datetime
import threading

# Style constants
BUTTON_PADDING = 12
FRAME_WIDTH = 600       # Wider frames for better spacing
FRAME_HEIGHT = 850      # Taller frames
FONT_FAMILY = "Roboto"    # Modern Google font
FONT_SIZE = 12
FONT_WEIGHT = 'bold'
TEXT_FIELD_WIDTH = 580
TEXT_FIELD_HEIGHT = 150
LARGE_BUTTON_WIDTH = 380
SMALL_BUTTON_WIDTH = 200
BUTTON_HEIGHT = 35
PADDING_X = 20
# Global variables
entries_result = None
loading_indicator = None


def show_loading_indicator(root):
  """Display an indeterminate progress bar"""
  global loading_indicator
  if not loading_indicator:
    loading_indicator = ctk.CTkProgressBar(
      root,
      mode='indeterminate',
      width=LARGE_BUTTON_WIDTH,
    )
    loading_indicator.place(relx=0.5, rely=0.95, anchor='center')
  loading_indicator.start()

def hide_loading_indicator():
  """Hide and destroy the loading indicator"""
  global loading_indicator
  if loading_indicator:
    loading_indicator.stop()
    loading_indicator.place_forget()
    loading_indicator = None

def get_entries(table_name, root):
  """Start request in separate thread"""
  threading.Thread(target=lambda: make_request(table_name, root), daemon=True).start()

def make_request(table_name, root):
  """Make API request with error handling"""
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
    arrow_data = pa.BufferReader(response.content)
    entries_result = pa.ipc.open_stream(arrow_data).read_all().to_pandas()
    print(entries_result)
  except Exception as e:
    print(f"Error: {e}")
  finally:
    hide_loading_indicator()

def create_annotated_section(root, x, y):
  """Create the annotated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)
  
  get_ann_btn = ctk.CTkButton(frame, text="Get All Annotations",
    command=lambda: get_entries("cell_info", root),
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT)
  get_ann_btn.pack(pady=(BUTTON_PADDING,20), padx=PADDING_X, fill='x')
  
  search_frame = ctk.CTkFrame(frame)
  search_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)
  
  search_entry = ctk.CTkEntry(search_frame, width=200, height=BUTTON_HEIGHT)
  search_entry.pack(side='left', expand=True, fill='x', padx=(0,BUTTON_PADDING))
  
  def search_entries():
    """Search functionality with improved matching"""
    search_text = search_entry.get().strip()
    if not search_text:
      return
      
    search_terms = [term.strip() for term in search_text.replace(';',',').split(',')]
    search_terms = set(filter(None, search_terms))
    
    matching_rows = []
    for _, row in entries_result.iterrows():
      if row['tag'] in search_terms:
        matching_rows.append(row['pt_root_id'])
        continue
        
      if pd.notna(row['tag2']):
        tag2_terms = set(row['tag2'].split())
        if tag2_terms & search_terms:
          matching_rows.append(row['pt_root_id'])
    
    results.delete('1.0', 'end')
    if matching_rows:
      results.insert('1.0', '\n'.join(str(row_id) for row_id in matching_rows))
    else:
      results.insert('1.0', 'No matches found')
  
  find_button = ctk.CTkButton(search_frame, text="Find",
    command=search_entries,
    width=SMALL_BUTTON_WIDTH,
    height=BUTTON_HEIGHT)
  find_button.pack(side='right')
  
  results_label = ctk.CTkLabel(frame, text="Results", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  results_label.pack(anchor='w', padx=PADDING_X)
  
  results = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  results.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  def copy_results():
    """Copy results with improved formatting"""
    content = results.get('1.0', 'end').strip()
    if content:
      formatted_content = ', '.join(content.split('\n'))
      root.clipboard_clear()
      root.clipboard_append(formatted_content)
      root.update()

  copy_btn = ctk.CTkButton(frame, text="Copy",
    command=copy_results,
    width=LARGE_BUTTON_WIDTH,
    height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_synaptic_partners_section(root, x, y):
  """Create the synaptic partners section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)
  
  source_label = ctk.CTkLabel(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)
  
  source = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  get_partners_btn = ctk.CTkButton(frame, text="Get Partners", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  get_partners_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  partners_label = ctk.CTkLabel(frame, text="Partners", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  partners_label.pack(anchor='w', padx=PADDING_X)
  
  partners = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  partners.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  button_frame = ctk.CTkFrame(frame)
  button_frame.pack(fill='x', pady=BUTTON_PADDING, padx=PADDING_X)
  
  copy_btn = ctk.CTkButton(button_frame, text="Copy", width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn.pack(side='left', padx=(0,BUTTON_PADDING))
  
  number_of_partners = ctk.CTkEntry(button_frame, width=100, height=BUTTON_HEIGHT)
  number_of_partners.pack(side='right')

  partners_btn = ctk.CTkButton(button_frame, text="Get Partners of Partners", width=SMALL_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  partners_btn.pack(side='right', padx=(0,BUTTON_PADDING))
  
  common_label = ctk.CTkLabel(frame, text="Partners of Most Common Partners", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  common_label.pack(anchor='w', padx=PADDING_X)
  
  common_partners = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  common_partners.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  copy_btn2 = ctk.CTkButton(frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn2.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_outdated_section(root, x, y):
  """Create the outdated section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)
  
  source_label = ctk.CTkLabel(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)
  
  source = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  update_btn = ctk.CTkButton(frame, text="Update", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  update_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  results_label = ctk.CTkLabel(frame, text="Source Without Outdated", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  results_label.pack(anchor='w', padx=PADDING_X)
  
  results = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  results.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  copy_btn = ctk.CTkButton(frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  updated_label = ctk.CTkLabel(frame, text="Updated", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  updated_label.pack(anchor='w', padx=PADDING_X)
  
  updated = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  updated.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  copy_btn2 = ctk.CTkButton(frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn2.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def create_proofread_section(root, x, y):
  """Create the proofread section with modern styling"""
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.place(x=x, y=y)
  
  source_label = ctk.CTkLabel(frame, text="Source", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  source_label.pack(anchor='w', padx=PADDING_X)
  
  source = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  source.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  get_btn = ctk.CTkButton(frame, text="Get", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  get_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  proofread_label = ctk.CTkLabel(frame, text="Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  proofread_label.pack(anchor='w', padx=PADDING_X)
  
  proofread = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  proofread.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  copy_btn = ctk.CTkButton(frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  not_proofread_label = ctk.CTkLabel(frame, text="Not Proofread", font=(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
  not_proofread_label.pack(anchor='w', padx=PADDING_X)
  
  not_proofread = ctk.CTkTextbox(frame, width=TEXT_FIELD_WIDTH, height=TEXT_FIELD_HEIGHT)
  not_proofread.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')
  
  copy_btn2 = ctk.CTkButton(frame, text="Copy", width=LARGE_BUTTON_WIDTH, height=BUTTON_HEIGHT)
  copy_btn2.pack(pady=BUTTON_PADDING, padx=PADDING_X, fill='x')


def main():
  """Initialize and run the main application"""
  ctk.set_appearance_mode("light")
  ctk.set_default_color_theme("blue")
  
  root = ctk.CTk()
  root.geometry('650x850')  # Wider window
  root.title('Neuron Dashboard')
  
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