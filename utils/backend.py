import re
import pyperclip
import platform

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
