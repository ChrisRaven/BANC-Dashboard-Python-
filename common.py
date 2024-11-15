import customtkinter as ctk
import re
import pyperclip
import platform

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


def copy(source):
  """Copy text to clipboard"""
  content = source.get('1.0', 'end').strip()
  if content:
    newline = '\r\n' if platform.system() == 'Windows' else '\n'
    formatted_content = newline.join(content.split('\n'))
    pyperclip.copy(formatted_content)

def copytext(text):
  """Copy text to clipboard"""
  pyperclip.copy(text)


def clean_input(input_string, output_type=int):
    parts = re.split(r'[ \t\r\n,;]+', input_string.strip())
    return [output_type(part) for part in parts if part]
