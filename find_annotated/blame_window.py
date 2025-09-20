import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from utils.frontend import *
from utils.backend import *
import re
from .backend import entries_result
from .frontend import usernames

# Default page size
DEFAULT_PAGE_SIZE = 50
PAGE_SIZE_OPTIONS = [25, 50, 100, 200]

class BlameWindow(ctk.CTkToplevel):
  def __init__(self):
    super().__init__()
    self.title("Blame")
    self.geometry("800x700")
    
    # Data storage
    self.df_all = pd.DataFrame()
    self.df_filtered = pd.DataFrame()
    self.page_size = DEFAULT_PAGE_SIZE
    self.current_page = 0
    
    # Search variables
    self.label_search_var = tk.StringVar()
    self.author_search_var = tk.StringVar()
    
    self._build_ui()
    
    # Set up cleanup on window close
    def cleanup_and_close():
      def cleanup_widgets(widget):
        if hasattr(widget, 'cleanup_callbacks'):
          widget.cleanup_callbacks()
        for child in widget.winfo_children():
          cleanup_widgets(child)
      cleanup_widgets(self)
      self.destroy()
    
    self.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # Bring window to front and focus
    self.lift()
    self.focus_force()
    self.grab_set()

  def _build_ui(self):
    # Main frame
    main_frame = ctk.CTkFrame(self)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Input section
    input_frame = ctk.CTkFrame(main_frame)
    input_frame.pack(fill='x', pady=(0, 10))
    
    # CountTextbox for IDs
    self.ids_textbox = widgets.countTextbox(parent=input_frame, label='Enter IDs to analyze')
    
    # Show labels button
    show_button = ctk.CTkButton(
      input_frame,
      text="Show labels",
      command=self._show_labels,
      height=30
    )
    show_button.pack(pady=5)
    
    # Search inputs frame
    search_frame = ctk.CTkFrame(main_frame)
    search_frame.pack(fill='x', pady=(0, 10))
    
    # Create a horizontal layout for both search inputs
    search_row = ctk.CTkFrame(search_frame)
    search_row.pack(fill='x', pady=5)
    
    # Label filter (left side)
    label_frame = ctk.CTkFrame(search_row)
    label_frame.pack(side='left', fill='x', expand=True, padx=(0, 5))
    ctk.CTkLabel(label_frame, text="Filter by label:").pack(side='left', padx=5)
    self.label_entry = ctk.CTkEntry(label_frame, textvariable=self.label_search_var, width=200)
    self.label_entry.pack(side='left', padx=5)
    self.label_entry.bind('<KeyRelease>', lambda e: self._on_search())
    
    # Author filter (right side)
    author_frame = ctk.CTkFrame(search_row)
    author_frame.pack(side='right', fill='x', expand=True, padx=(5, 0))
    ctk.CTkLabel(author_frame, text="Filter by author:").pack(side='left', padx=5)
    self.author_entry = ctk.CTkEntry(author_frame, textvariable=self.author_search_var, width=200)
    self.author_entry.pack(side='left', padx=5)
    self.author_entry.bind('<KeyRelease>', lambda e: self._on_search())
    
    # Table frame
    table_frame = ctk.CTkFrame(main_frame)
    table_frame.pack(fill='both', expand=True, pady=(0, 10))
    
    # Create table
    self.tree = ttk.Treeview(table_frame, columns=("id", "label", "author"), show='headings', height=10)
    self.tree.heading("id", text="ID")
    self.tree.heading("label", text="Label")
    self.tree.heading("author", text="Author")
    self.tree.column("id", width=150)
    self.tree.column("label", width=300)
    self.tree.column("author", width=200)
    self.tree.pack(fill='both', expand=True, side='left', padx=5, pady=5)
    
    # Scrollbar for table
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y', pady=5)
    
    # Pagination controls
    pagination_frame = ctk.CTkFrame(main_frame)
    pagination_frame.pack(fill='x', pady=(0, 10))
    
    # Page controls
    ctk.CTkButton(pagination_frame, text="< Prev", command=self._prev_page, width=80).pack(side='left', padx=5)
    ctk.CTkButton(pagination_frame, text="Next >", command=self._next_page, width=80).pack(side='left', padx=5)
    
    # Page size selector
    ctk.CTkLabel(pagination_frame, text="Page size:").pack(side='left', padx=(20, 5))
    self.page_size_var = tk.IntVar(value=self.page_size)
    page_size_menu = ttk.Combobox(pagination_frame, textvariable=self.page_size_var, values=PAGE_SIZE_OPTIONS, width=5, state="readonly")
    page_size_menu.pack(side='left', padx=5)
    page_size_menu.bind('<<ComboboxSelected>>', lambda e: self._on_page_size())
    
    # Page info label
    self.page_label = ctk.CTkLabel(pagination_frame, text="")
    self.page_label.pack(side='left', padx=20)
    
    # Copy button
    copy_button = ctk.CTkButton(
      main_frame,
      text="Copy visible",
      command=self._copy_visible,
      height=30
    )
    copy_button.pack(pady=5)
    
    # Style the Treeview to match CTk theme
    self._style_treeview()

  def _style_treeview(self):
    style = ttk.Style(self)
    theme_mode = ctk.get_appearance_mode()
    if theme_mode == 'Dark':
      bg = ctk.ThemeManager.theme['CTkFrame']['fg_color'][1]
      fg = ctk.ThemeManager.theme['CTkLabel']['text_color'][1]
      sel_bg = ctk.ThemeManager.theme['CTkButton']['fg_color'][1]
      sel_fg = ctk.ThemeManager.theme['CTkButton']['text_color'][1]
      header_fg = ctk.ThemeManager.theme['CTkLabel']['text_color'][1]
    else:
      bg = ctk.ThemeManager.theme['CTkFrame']['fg_color'][0]
      fg = ctk.ThemeManager.theme['CTkLabel']['text_color'][0]
      sel_bg = ctk.ThemeManager.theme['CTkButton']['fg_color'][0]
      sel_fg = ctk.ThemeManager.theme['CTkButton']['text_color'][0]
      header_fg = ctk.ThemeManager.theme['CTkLabel']['text_color'][0]
    
    style.configure('Treeview',
      background=bg,
      foreground=fg,
      fieldbackground=bg,
      rowheight=24,
      font=("Segoe UI", 10))
    style.map('Treeview',
      background=[('selected', sel_bg)],
      foreground=[('selected', sel_fg)])
    style.configure('Treeview.Heading',
      foreground=header_fg,
      font=("Segoe UI", 11, "bold"))

  def _show_labels(self):
    """Load data based on entered IDs"""
    ids_text = self.ids_textbox.get('1.0', 'end-1c')
    if not ids_text:
      return
    
    # Parse IDs
    try:
      ids = clean_input(ids_text)
    except ValueError:
      return
    
    if not ids:
      return

    # Get data from entries_result
    if entries_result is None or not isinstance(entries_result, pd.DataFrame):
      self.df_all = pd.DataFrame(columns=["pt_root_id", "tag", "user_id"])
    else:
      # Filter by the entered IDs
      mask = entries_result['pt_root_id'].isin(ids)
      filtered_data = entries_result[mask].copy()
      filtered_data['author'] = filtered_data['user_id'].astype(str).map(usernames).fillna(filtered_data['user_id'].astype(str))
      
      self.df_all = filtered_data[['pt_root_id', 'tag', 'author']].copy()
      self.df_all.columns = ['id', 'label', 'author']
    # Apply initial filtering
    self.current_page = 0
    self._apply_filters()
    self._refresh_table()

  def _apply_filters(self):
    self.df_filtered = self.df_all.copy()
    
    def apply_single_filter(df, column, query_string):
      if not query_string:
        return df

      # Split the query string into tokens, preserving quoted phrases
      # This regex finds either a sequence of non-whitespace characters
      # or a sequence of characters inside double quotes (including spaces)
      # We now extract the actual content directly in the list comprehension.
      raw_tokens_groups = re.findall(r'"([^"]*)"|(\S+)', query_string)
      
      tokens_with_type = []
      for g1, g2 in raw_tokens_groups:
          if g1: # Matched a quoted string
              tokens_with_type.append((g1.strip(), True)) # (content, is_exact_match)
          elif g2: # Matched a non-quoted string
              tokens_with_type.append((g2.strip(), False))
      
      filtered_df = df.copy()

      for token_content, is_exact_match_candidate in tokens_with_type:
        if not token_content:
            continue

        is_exclude = token_content.startswith('-')
        search_term = token_content[1:] if is_exclude else token_content

        if not search_term: # Skip if only '-' was entered without a term
            continue

        # If it was originally a quoted phrase, it's an exact match.
        # If not, but it starts/ends with quotes now (e.g., user typed -"phrase")
        # then treat it as an exact match as well and strip quotes.
        is_actual_exact_match = is_exact_match_candidate or \
                               (search_term.startswith('"') and search_term.endswith('"') and len(search_term) > 1)
        
        if is_actual_exact_match:
            # Strip quotes if they are still present after previous processing (e.g. from - "phrase")
            if search_term.startswith('"') and search_term.endswith('"'):
                search_term = search_term[1:-1]
            if not search_term: # Handle cases like `""` or `-" "` after stripping
                continue
            if is_exclude:
                mask = filtered_df[column].astype(str) != search_term
            else:
                mask = filtered_df[column].astype(str) == search_term
        else:
          # Contains match (case-insensitive)
          if is_exclude:
            mask = ~filtered_df[column].astype(str).str.contains(search_term, case=False, na=False)
          else:
            mask = filtered_df[column].astype(str).str.contains(search_term, case=False, na=False)
        
        filtered_df = filtered_df[mask]
      return filtered_df

    # Apply label filter
    label_query = self.label_search_var.get().strip()
    self.df_filtered = apply_single_filter(self.df_filtered, "label", label_query)
    
    # Apply author filter
    author_query = self.author_search_var.get().strip()
    self.df_filtered = apply_single_filter(self.df_filtered, "author", author_query)

  def _on_search(self):
    """Handle search input changes"""
    self._apply_filters()
    self.current_page = 0
    self._refresh_table()

  def _refresh_table(self):
    """Refresh the table with current data"""
    # Clear table
    for row in self.tree.get_children():
      self.tree.delete(row)
    
    # Paginate
    total = len(self.df_filtered)
    self.page_size = self.page_size_var.get()
    start = self.current_page * self.page_size
    end = start + self.page_size
    page_df = self.df_filtered.iloc[start:end]
    
    for _, row in page_df.iterrows():
      self.tree.insert('', 'end', values=(row["id"], row["label"], row["author"]))
    
    # Update page label
    total_pages = max(1, (total + self.page_size - 1) // self.page_size)
    self.page_label.configure(text=f"Page {self.current_page+1} of {total_pages} ({total} entries)")

  def _prev_page(self):
    if self.current_page > 0:
      self.current_page -= 1
      self._refresh_table()

  def _next_page(self):
    total = len(self.df_filtered)
    if (self.current_page + 1) * self.page_size < total:
      self.current_page += 1
      self._refresh_table()

  def _on_page_size(self):
    self.current_page = 0
    self._refresh_table()

  def _copy_visible(self):
    """Copy all visible IDs to clipboard"""
    visible_ids = []
    for item in self.tree.get_children():
      values = self.tree.item(item, 'values')
      if values:
        visible_ids.append(str(values[0]))  # First column is ID
    
    if visible_ids:
      self.clipboard_clear()
      self.clipboard_append('\n'.join(visible_ids))

def open_blame_window():
  BlameWindow()