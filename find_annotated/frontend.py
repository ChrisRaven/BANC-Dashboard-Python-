from constants import *
from utils.frontend import *
from utils.backend import *
from .backend import *
import json
import os


def create_annotated_section(root):
  frame = ctk.CTkFrame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
  frame.pack(fill='x')

  widgets.spacer(parent=frame, height=20)

  skip_queued = ctk.BooleanVar(value=False)
  skip_queued_checkbox = ctk.CTkCheckBox(
    frame,
    text="skip queued",
    variable=skip_queued
  )
  skip_queued_checkbox.pack(anchor='w', padx=(PADDING_X + 20, 0))

  def get_all_annotations_callback(msg):
    hide_loading_indicator()
    if not msg:
      status_label.configure(text='')
      return

    if isinstance(msg, str) and msg.startswith('ERR:'):
      insert(results, msg.replace('ERR:', ''))
      status_label.configure(text='')
    else:
      status_label.configure(text=f'Found {msg} annotations')

  def get_all_annotations_handler():
    show_loading_indicator(root)
    status_label.configure(text=f'Fetching annotations...')
    get_entries('cell_info', skip_queued.get(), get_all_annotations_callback)

  widgets.button(
    parent=frame,
    label='Get all annotations',
    action=get_all_annotations_handler
  )

  status_label = ctk.CTkLabel(
    frame,
    text='Click "Get all annotations" to start',
    text_color='Yellow'
  )
  status_label.pack(anchor='w', padx=(PADDING_X + 20, 0))

  last_entered_value = None
  if os.path.exists('last_search_entry.json'):
    with open('last_search_entry.json', 'r') as file:
      last_entered_value = json.load(file)

  def save_search_entry():
    value = find_entry.get()
    with open('last_search_entry.json', 'w') as file:
      json.dump(value, file)

  widgets.spacer(parent=frame, height=20)

  find_wrapper = widgets.column_wrapper(parent=frame)
  find_entry_column = widgets.column(parent=find_wrapper)
  find_entry = widgets.labeledEntry(parent=find_entry_column, label='Annotations to search for')

  if last_entered_value:
    find_entry.delete(0, 'end')
    find_entry.insert(0, last_entered_value)

  
  def on_search_entry_change(event=None):
    nonlocal last_entered_value
    new_value = find_entry.get()
    if new_value != last_entered_value:
      last_entered_value = new_value
      save_search_entry()

  find_entry.bind('<KeyRelease>', on_search_entry_change)
  

  def find_button_callback():
    show_loading_indicator(root)
    find_text = find_entry.get().strip()

    def callback(found):
      if isinstance(found, str) and found.startswith('MSG:'):
        insert(results, found[4:])
      elif found:
        insert(results, '\n'.join(str(row_id) for row_id in found))
      else:
        insert(results, 'No matches found')
      hide_loading_indicator()

    find_annotated(find_text, callback)

  find_button_column = widgets.column(parent=find_wrapper, anchor='sw')
  widgets.button(
    parent=find_button_column,
    label='Find',
    action=find_button_callback
  )

  widgets.spacer(parent=frame, height=20)

  results = widgets.countTextbox(parent=frame, label='Results')

  widgets.spacer(parent=frame, height=20)

  # Create frame for the user stats button
  user_stats_wrapper = widgets.column_wrapper(parent=frame)
  user_stats_button_column = widgets.column(parent=user_stats_wrapper)
  
  # Create table frame that will be shown/hidden
  table_frame = widgets.frame(parent=frame)
  table_frame.pack_forget()  # Initially hidden

#import banc
#client = banc.auth.CAVEclient()
#print(client.auth.get_user_information([392]))


  usernames = {
    "2": "Sven Dorkenwald",
    "4": "Claire McKellar",
    "8": "Szi-chieh Yu",
    "10": "Lucas Encarnacion-Rivera",
    "12": "Christa Baker",
    "13": "Jay Gager",
    "14": "James Hebditch",
    "16": "Sandeep Kumar",
    "17": "Austin T Burke",
    "19": "Edna Normand",
    "20": "Diego A Pacheco Pinedo",
    "22": "Dudi Deutsch",
    "25": "Kisuk Lee",
    "26": "Sarah Morejohn",
    "27": "Kyle Patrick Willie",
    "28": "Celia D",
    "29": "M Sorek",
    "36": "Rachel Wilson",
    "54": "Claire McKellar",
    "60": "Greg Jefferis",
    "62": "Philipp Schlegel",
    "74": "Markus Pleijzier",
    "82": "Quinn Vanderbeck",
    "84": "Merlin Moore",
    "92": "Katharina Eichler",
    "94": "Gizem Sancer",
    "95": "Emil Kind",
    "96": "Doug Bland",
    "98": "Ibrahim Taştekin",
    "100": "Dustin Garner",
    "103": "Ben Silverman",
    "104": "Ryan Willie",
    "108": "A. Javier",
    "116": "Mert Erginkaya",
    "119": "Zhihao Zheng",
    "122": "Amy R. Sterling",
    "125": "Stefanie Hampel",
    "129": "Gerit Linneweber",
    "146": "shuo cao",
    "153": "Amalia Braun",
    "184": "Steven Calle",
    "185": "Lucia Kmecova",
    "196": "Megan Wang",
    "257": "Xinyue Cui",
    "259": "Haein Kim",
    "260": "Jennifer Malin",
    "277": "Gabriella Rose Sterne PhD",
    "283": "Laia Serratosa Capdevila",
    "301": "Yuta Mabuchi",
    "306": "Joseph Hsu",
    "307": "Joanna Eckhardt",
    "308": "Imaan Tamimi",
    "352": "Amanda González-Segarra",
    "355": "Alexander Bates",
    "372": "Yijie Yin",
    "392": "Krzysztof Kruk",
    "392": "KrzysztofKruk",
    "397": "Marlon Blanquart",
    "427": "Tansy Yang",
    "468": "Mehmet F Keles",
    "531": "Jinfang Li",
    "700": "a5hm0r",
    "703": "Arthur Zhao",
    "814": "Mavil",
    "839": "Carolyn Elya",
    "856": "Irene Salgarella",
    "867": "Paul Brooks",
    "888": "Alvaro Sanz Diez",
    "957": "Varun Sane",
    "960": "Wolf Huetteroth",
    "986": "Matt Collie",
    "1000": "Salil Bidaye",
    "1007": "Nils Reinhard",
    "1012": "AzureJay",
    "1019": "Farzaan Salman",
    "1022": "Jonas Ch",
    "1034": "Benjamin Bargeron",
    "1044": "Serene Dhawan",
    "1050": "GIOVANNI FRIGHETTO",
    "1062": "Mareike Selcho",
    "1063": "Lab Members",
    "1081": "Arie Matsliah",
    "1093": "Laia Serratosa",
    "1097": "laia pons",
    "1152": "Damian Demarest",
    "1156": "Philip Shiu",
    "1185": "Marion Silies",
    "1205": "Zepeng Yao",
    "1211": "Arti Yadav",
    "1230": "Ben Gorko",
    "1232": "Minsik Yun",
    "1238": "salil bidaye",
    "1257": "Andrea Sandoval",
    "1288": "Sheetal Potdar",
    "1313": "Amanda Abusaif",
    "1321": "J. Dolorosa",
    "1322": "Shirleyjoy Serona",
    "1323": "J. Anthony Ocho",
    "1324": "Zairene Lenizo",
    "1326": "Mendell Lopez",
    "1329": "Nash Hadjerol",
    "1342": "fred wolf",
    "1357": "Maggie Robertson",
    "1417": "Rashmita Rana",
    "1491": "Lucy Houghton",
    "1526": "Márcia Santos",
    "1542": "Kate Maier",
    "1673": "Caro Md",
    "1701": "Alexander Del Toro",
    "1737": "Tjalda Falt",
    "1764": "Haley Croke",
    "1774": "Su-Yee Lee",
    "1776": "Chris Dallmann",
    "1781": "Neha Sapakal",
    "1926": "Shaina Mae Monungolh",
    "1927": "Ariel Dagohoy",
    "1928": "remer tancontian",
    "1929": "regine salem",
    "1930": "Darrel Jay Akiatan",
    "1931": "Rey Adrian Candilada",
    "1932": "Kendrick Joules Vinson",
    "1933": "Joshua Bañez",
    "1934": "Miguel Albero",
    "1946": "Anthony Moreno-Sanchez",
    "2080": "Christopher Dunne",
    "2102": "Maria Ioannidou",
    "2115": "Dharini Sapkal",
    "2121": "Nino Mancini",
    "2261": "Zongwei Chen",
    "2338": "Feng Li",
    "2356": "Kaiyu Wang",
    "2357": "Osama AHmed",
    "2374": "Zeba Vohra",
    "2390": "Chitra Nair",
    "2395": "Sebastian Mauricio Molina Obando",
    "2401": "Marina Gkantia",
    "2455": "annkri",
    "2462": "Dhwani Patel",
    "2463": "Arzoo Diwan",
    "2474": "Yixiong Liu",
    "2482": "Eva Munnelly",
    "2565": "Itisha Joshi",
    "2626": "SL_CS",
    "2630": "st0ck53y",
    "2660": "Jasper Phelps",
    "2654": "Burak Gur",
    "2673": "Junjie Yi",
    "2689": "Dhara Kakadiya",
    "2753": "johnclyde saguimpa",
    "2754": "Cathy Pilapil",
    "2757": "Chereb Martinez",
    "2758": "Jacquilyn Laude",
    "2759": "John David Asis",
    "2760": "Alvin Josh Mandahay",
    "2761": "Daril Bautista",
    "2762": "Nelsie Panes",
    "2763": "Janice Salocot",
    "2765": "Philip",
    "2766": "marchan manaytay",
    "2767": "Allien Mae Gogo",
    "2768": "Clyde",
    "2769": "Mark Lloyd Pielago",
    "2770": "Jansen Seguido",
    "2815": "Nseraf",
    "2830": "Hewhoamareismyself",
    "2842": "Yashvi Patel",
    "2843": "TR77",
    "2917": "István Taisz",
    "2926": "Gianna Vitelli",
    "2927": "hailiang li",
    "2935": "Lena Lörsch",
    "3083": "Gao Yiqin",
    "3153": "Meet Zandawala",
    "3409": "Annika Bast",
    "3431": "juan felipe vargas fique",
    "3504": "Jenna Joroff",
    "3666": "Timothy Currier",
    "3732": "Stéphane noselli",
    "3887": "Dorfam Rastgarmoghaddam",
    "3993": "Azusa Kamikouchi",
    "4280": "Emily Kophs",
    "4287": "Kangrui Leng",
    "6818": "Ben Jourdan",
    "6830": "Gregory Schwartzman"
  }

  def show_user_stats():
    show_loading_indicator(root)
    
    def callback(stats_text):
      
      hide_loading_indicator()
      # Clear previous content
      for widget in table_frame.winfo_children():
        widget.destroy()
      
      if stats_text.startswith('ERR:'):
        results.insert('1.0', stats_text.replace('ERR:', ''))
        results.insert('1.0', '')
        return
        
      # Create headers
      header_frame = ctk.CTkFrame(table_frame)
      header_frame.pack(fill='x', padx=5, pady=(5,0))
      
      ctk.CTkLabel(
        header_frame, 
        text="User",
        font=(FONT_FAMILY, 11, "bold"),
        width=150
      ).pack(side='left', padx=5)
      
      ctk.CTkLabel(
        header_frame,
        text="Annotations",
        font=(FONT_FAMILY, 11, "bold"),
        width=100
      ).pack(side='left', padx=5)
      
      # Create scrollable frame for results
      scroll_frame = ctk.CTkScrollableFrame(table_frame, height=200)
      scroll_frame.pack(fill='x', padx=5, pady=5)
      
      # Parse and display results
      for i, line in enumerate(stats_text.split('\n'), 1):
        if line:
          user_id = line.split(':')[0].replace('User ', '').strip()
          count = line.split(':')[1].strip().replace(' annotations', '')
          row = ctk.CTkFrame(scroll_frame)
          row.pack(fill='x', pady=2)
          ctk.CTkLabel(
            row,
            text=f"{i}.",
            width=30
          ).pack(side='left', padx=5)
          display_name = usernames.get(user_id, user_id)
          # Make the username label clickable
          user_label = ctk.CTkLabel(
            row,
            text=display_name,
            width=150,
            cursor="hand2",
            text_color="#1E90FF"
          )
          user_label.pack(side='left', padx=5)
          ctk.CTkLabel(
            row,
            text=count,
            width=100
          ).pack(side='left', padx=5)
          # Import and bind the user annotation window
          from .user_annotations_window import open_user_annotations_window
          user_label.bind("<Button-1>", lambda e, uid=user_id, uname=display_name: open_user_annotations_window(uid, uname))
      table_frame.pack(fill='x', padx=10, pady=5)

    get_user_annotation_counts(callback)

  widgets.button(
    parent=user_stats_button_column,
    label='Show User Statistics',
    action=show_user_stats
  )
