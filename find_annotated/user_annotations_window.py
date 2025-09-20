import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import pandas as pd
from find_annotated.backend import entries_result

# Helper for date parsing
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default page size
DEFAULT_PAGE_SIZE = 100
PAGE_SIZE_OPTIONS = [50, 100, 200, 500, 1000]

# Helper: get all user entries (root_id, tag/tag2, timestamp)
def get_user_entries(user_id):
  if entries_result is None or not isinstance(entries_result, pd.DataFrame):
    return pd.DataFrame(columns=["pt_root_id", "tag", "created"])
  if 'user_id' not in entries_result.columns or 'pt_root_id' not in entries_result.columns or 'created' not in entries_result.columns:
    return pd.DataFrame(columns=["pt_root_id", "tag", "created"])
  df = entries_result[entries_result['user_id'].astype(str) == str(user_id)].copy()
  rows = []
  for _, row in df.iterrows():
    # Add tag if present
    if pd.notnull(row.get('tag')) and str(row['tag']).strip():
      rows.append({'pt_root_id': row['pt_root_id'], 'tag': row['tag'], 'created': row['created']})
  result_df = pd.DataFrame(rows, columns=['pt_root_id', 'tag', 'created'])
  if not result_df.empty:
    result_df['created'] = pd.to_datetime(result_df['created'], utc=True, errors='coerce')
  result_df.columns = ['root_id', 'tag', 'created']
  return result_df

class UserAnnotationsWindow(ctk.CTkToplevel):
  def __init__(self, user_id, user_name):
    super().__init__()
    self.title(user_name)
    self.geometry("700x700")
    self.user_id = user_id
    self.user_name = user_name
    self.df_all = get_user_entries(user_id)
    self.df_filtered = self.df_all.copy()
    self.page_size = DEFAULT_PAGE_SIZE
    self.current_page = 0
    self.search_var = tk.StringVar()
    self.page_size_var = tk.IntVar(value=self.page_size)
    self.start_date = None
    self.end_date = None
    self._build_ui()
    self._refresh_table()
    # Bring window to front and focus
    self.lift()
    self.focus_force()
    self.grab_set()

  def _build_ui(self):
    # Top controls: search, copy, date range
    top_frame = ctk.CTkFrame(self)
    top_frame.pack(fill='x', padx=10, pady=5)
    ctk.CTkLabel(top_frame, text=f"Annotations for {self.user_name}", font=("Arial", 14, "bold")).pack(side='left', padx=5)
    ctk.CTkLabel(top_frame, text="Search:").pack(side='left', padx=(20,2))
    search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var, width=180)
    search_entry.pack(side='left', padx=2)
    search_entry.bind('<KeyRelease>', lambda e: self._on_search())
    ctk.CTkButton(top_frame, text="Copy IDs", command=self._copy_ids).pack(side='left', padx=10)
    # Date range controls
    date_frame = ctk.CTkFrame(self)
    date_frame.pack(fill='x', padx=10, pady=2)
    ctk.CTkLabel(date_frame, text="Date range:").pack(side='left', padx=2)
    self.start_entry = ctk.CTkEntry(date_frame, width=120)
    self.start_entry.pack(side='left', padx=2)
    ctk.CTkLabel(date_frame, text="to").pack(side='left')
    self.end_entry = ctk.CTkEntry(date_frame, width=120)
    self.end_entry.pack(side='left', padx=2)
    ctk.CTkButton(date_frame, text="Apply", command=self._on_date_filter).pack(side='left', padx=5)
    ctk.CTkButton(date_frame, text="Last week", command=self._last_week).pack(side='left', padx=2)
    ctk.CTkButton(date_frame, text="All", command=self._all_dates).pack(side='left', padx=2)
    # Table
    self.table_frame = ctk.CTkFrame(self)
    self.table_frame.pack(fill='both', expand=True, padx=10, pady=5)
    self.tree = ttk.Treeview(self.table_frame, columns=("root_id", "tag"), show='headings', height=20)
    self.tree.heading("root_id", text="Root ID")
    self.tree.heading("tag", text="Tag")
    self.tree.column("root_id", width=180)
    self.tree.column("tag", width=420)
    self.tree.pack(fill='both', expand=True, side='left')
    # Scrollbar
    scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    # Pagination controls
    bottom_frame = ctk.CTkFrame(self)
    bottom_frame.pack(fill='x', padx=10, pady=5)
    ctk.CTkButton(bottom_frame, text="< Prev", command=self._prev_page).pack(side='left', padx=2)
    ctk.CTkButton(bottom_frame, text="Next >", command=self._next_page).pack(side='left', padx=2)
    ctk.CTkLabel(bottom_frame, text="Page size:").pack(side='left', padx=(20,2))
    page_size_menu = ttk.Combobox(bottom_frame, textvariable=self.page_size_var, values=PAGE_SIZE_OPTIONS, width=5, state="readonly")
    page_size_menu.pack(side='left', padx=2)
    page_size_menu.bind('<<ComboboxSelected>>', lambda e: self._on_page_size())
    self.page_label = ctk.CTkLabel(bottom_frame, text="")
    self.page_label.pack(side='left', padx=10)
    # After table creation in _build_ui
    self.tree.bind('<Control-c>', self._on_copy_selected)
    self.tree.bind('<Control-C>', self._on_copy_selected)
    # Style the Treeview to match CTk theme
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

  def _refresh_table(self):
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
      self.tree.insert('', 'end', values=(row["root_id"], row["tag"]))
    # Update page label
    total_pages = max(1, (total + self.page_size - 1) // self.page_size)
    self.page_label.configure(text=f"Page {self.current_page+1} of {total_pages} ({total} entries)")

  def _on_search(self):
    query = self.search_var.get().strip()
    if query:
      # Check if query is wrapped in double quotes for exact match
      if query.startswith('"') and query.endswith('"') and len(query) > 2:
        # Extract text inside quotes and perform exact match
        exact_query = query[1:-1].lower()
        mask = self.df_all["tag"].astype(str).str.lower() == exact_query
      else:
        # Perform substring search (current behavior)
        query_lower = query.lower()
        mask = self.df_all["tag"].astype(str).str.lower().str.contains(query_lower, na=False)
      self.df_filtered = self.df_all[mask].copy()
    else:
      self.df_filtered = self.df_all.copy()
    self.current_page = 0
    self._refresh_table()

  def _on_page_size(self):
    self.current_page = 0
    self._refresh_table()

  def _prev_page(self):
    if self.current_page > 0:
      self.current_page -= 1
      self._refresh_table()

  def _next_page(self):
    total = len(self.df_filtered)
    if (self.current_page + 1) * self.page_size < total:
      self.current_page += 1
      self._refresh_table()

  def _copy_ids(self):
    ids = self.df_filtered["root_id"].astype(str).tolist()
    self.clipboard_clear()
    self.clipboard_append("\n".join(ids))

  def _on_date_filter(self):
    start_str = self.start_entry.get().strip()
    end_str = self.end_entry.get().strip()
    try:
      start_dt = pd.to_datetime(start_str) if start_str else None
      end_dt = pd.to_datetime(end_str) if end_str else None
      # Make both timezone-aware (UTC) if not already
      if start_dt is not None and start_dt.tzinfo is None:
        start_dt = start_dt.tz_localize('UTC')
      if end_dt is not None and end_dt.tzinfo is None:
        end_dt = end_dt.tz_localize('UTC')
    except Exception:
      start_dt = end_dt = None
    if start_dt is not None or end_dt is not None:
      mask = pd.Series([True] * len(self.df_all), index=self.df_all.index)
      if start_dt is not None:
        mask &= (self.df_all["created"] >= start_dt)
      if end_dt is not None:
        mask &= (self.df_all["created"] <= end_dt)
      self.df_filtered = self.df_all[mask].copy()
    else:
      self.df_filtered = self.df_all.copy()
    self.current_page = 0
    self._refresh_table()

  def _last_week(self):
    now = pd.Timestamp.now()
    last_week = now - pd.Timedelta(days=7)
    self.start_entry.delete(0, 'end')
    self.start_entry.insert(0, last_week.strftime("%Y-%m-%d %H:%M:%S"))
    self.end_entry.delete(0, 'end')
    self.end_entry.insert(0, now.strftime("%Y-%m-%d %H:%M:%S"))
    self._on_date_filter()

  def _all_dates(self):
    self.start_entry.delete(0, 'end')
    self.end_entry.delete(0, 'end')
    self.df_filtered = self.df_all.copy()
    self.current_page = 0
    self._refresh_table()

  def _on_copy_selected(self, event=None):
    selected = self.tree.selection()
    if selected:
      item = selected[0]
      root_id = self.tree.item(item, 'values')[0]
      self.clipboard_clear()
      self.clipboard_append(str(root_id))

def open_user_annotations_window(user_id, user_name):
  UserAnnotationsWindow(user_id, user_name) 