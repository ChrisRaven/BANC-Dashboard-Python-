from constants import *
import customtkinter as ctk

loading_indicator = None

def show_loading_indicator(root):
  """Display an indeterminate progress bar"""
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
  """Hide and destroy the loading indicator"""
  global loading_indicator
  if loading_indicator:
    loading_indicator.stop()
    loading_indicator.place_forget()
    loading_indicator = None


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
