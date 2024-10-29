from functionalities.get_synaptic_partners import get_synaptic_partners
from functionalities.update_outdated import update_outdated
from functionalities.get_all_annotations import get_all_annotations
from tkinter import LabelFrame, Label, Text, Button, Entry, Frame, LEFT, RIGHT, X, W, Y, Tk
from tkinter import ttk

# Style constants
BUTTON_BG_COLOR = '#FF8C00'  # Orange color currently used
BUTTON_FG_COLOR = 'white'    # White text color currently used
BUTTON_PADDING = 5           # Standard padding for buttons
FRAME_PADDING_X = 10         # Frame padding x currently used
FRAME_PADDING_Y = 5          # Frame padding y currently used
TEXT_HEIGHT_SMALL = 8        # Height for smaller text areas
TEXT_HEIGHT_LARGE = 12       # Height for larger text areas
FRAME_WIDTH = 300           # Standard frame width
FRAME_HEIGHT = 800          # Standard frame height
FONT_SIZE = 12             # Font size for labels and buttons


def create_annotated_section(root, x, y):
    frame = LabelFrame(root, text="Find annotated", padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y, font=("TkDefaultFont", FONT_SIZE))
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    # Get Annotations button at top
    get_ann_btn = Button(frame, text="Get Annotations", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    get_ann_btn.pack(pady=(BUTTON_PADDING,10))
    
    # Search section
    search_frame = Frame(frame)
    search_frame.pack(fill=X, pady=BUTTON_PADDING)
    search_entry = Entry(search_frame)
    search_entry.pack(side=LEFT, expand=True, fill=X, padx=(0,BUTTON_PADDING))
    find_button = Button(search_frame, text="Find", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    find_button.pack(side=RIGHT)
    
    # Results label
    Label(frame, text="results", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Results text area
    results = Text(frame, height=TEXT_HEIGHT_LARGE)
    results.pack(pady=BUTTON_PADDING, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn.pack(pady=BUTTON_PADDING)

def create_synaptic_section(root, x, y):
    frame = LabelFrame(root, text="Find synaptic partners", padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y, font=("TkDefaultFont", FONT_SIZE))
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    # Source label
    Label(frame, text="source", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=TEXT_HEIGHT_SMALL)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    # Get Partners button
    get_partners_btn = Button(frame, text="Get Partners", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    get_partners_btn.pack(pady=BUTTON_PADDING)
    
    # Partners label
    Label(frame, text="partners", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Partners text area
    partners = Text(frame, height=TEXT_HEIGHT_SMALL)
    partners.pack(pady=BUTTON_PADDING, fill=X)
    
    # Button row with entry
    button_frame = Frame(frame)
    button_frame.pack(fill=X, pady=BUTTON_PADDING)
    copy_btn = Button(button_frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn.pack(side=LEFT, padx=(0,BUTTON_PADDING))
    partners_btn = Button(button_frame, text="Get Partners of Partners", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    partners_btn.pack(side=LEFT, padx=(0,BUTTON_PADDING))
    entry = Entry(button_frame, width=5)
    entry.pack(side=LEFT)
    
    # Partners of most common partners label
    Label(frame, text="partners of most common partners", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Final text area
    common_partners = Text(frame, height=TEXT_HEIGHT_SMALL)
    common_partners.pack(pady=BUTTON_PADDING, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn2.pack(pady=BUTTON_PADDING)

def create_outdated_section(root, x, y):
    frame = LabelFrame(root, text="Find potentially outdated", padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y, font=("TkDefaultFont", FONT_SIZE))
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    # Source label
    Label(frame, text="source", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=TEXT_HEIGHT_LARGE)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    # Update button
    update_btn = Button(frame, text="Update", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    update_btn.pack(pady=BUTTON_PADDING)
    
    # Source without outdated label
    Label(frame, text="source without outdated", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Results text area
    results = Text(frame, height=TEXT_HEIGHT_LARGE)
    results.pack(pady=BUTTON_PADDING, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn.pack(pady=BUTTON_PADDING)
    
    # Updated label
    Label(frame, text="updated", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Updated text area
    updated = Text(frame, height=TEXT_HEIGHT_SMALL)
    updated.pack(pady=BUTTON_PADDING, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn2.pack(pady=BUTTON_PADDING)

def create_proofread_section(root, x, y):
    frame = LabelFrame(root, text="Find proofread", padx=FRAME_PADDING_X, pady=FRAME_PADDING_Y, font=("TkDefaultFont", FONT_SIZE))
    frame.place(x=x, y=y, width=FRAME_WIDTH, height=FRAME_HEIGHT)
    
    # Source label
    Label(frame, text="source", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=TEXT_HEIGHT_LARGE)
    source.pack(pady=BUTTON_PADDING, fill=X)
    
    # Get button
    get_btn = Button(frame, text="Get", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    get_btn.pack(pady=BUTTON_PADDING)
    
    # Proofread label
    Label(frame, text="proofread", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Proofread text area
    proofread = Text(frame, height=TEXT_HEIGHT_LARGE)
    proofread.pack(pady=BUTTON_PADDING, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn.pack(pady=BUTTON_PADDING)
    
    # Not proofread label
    Label(frame, text="not proofread", font=("TkDefaultFont", FONT_SIZE)).pack(anchor=W)
    
    # Not proofread text area
    not_proofread = Text(frame, height=TEXT_HEIGHT_SMALL)
    not_proofread.pack(pady=BUTTON_PADDING, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=("TkDefaultFont", FONT_SIZE))
    copy_btn2.pack(pady=BUTTON_PADDING)

def main():
    root = Tk()
    root.geometry('1300x850')
    root.title('Dashboard')
    
    # Create all sections
    create_annotated_section(root, 20, 20)
    create_synaptic_section(root, 340, 20)
    create_outdated_section(root, 660, 20)
    create_proofread_section(root, 980, 20)
    
    root.mainloop()

def helloCallBack():
  a = 5

main()

#get_synaptic_partners([720575941536100318,720575941338817903,720575941605725549])