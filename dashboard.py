from functionalities.get_synaptic_partners import get_synaptic_partners
from functionalities.update_outdated import update_outdated
from functionalities.get_all_annotations import get_all_annotations

from tkinter import LabelFrame, Label, Text, Button, Entry, Frame, LEFT, RIGHT, X, W, Y, Tk
from tkinter import ttk

def create_annotated_section(root, x, y):
    frame = LabelFrame(root, text="Find annotated", padx=10, pady=5)
    frame.place(x=x, y=y, width=300, height=800)
    
    # Get Annotations button at top
    get_ann_btn = Button(frame, text="Get Annotations", bg='#FF8C00', fg='white')
    get_ann_btn.pack(pady=(5,10))
    
    # Search section
    search_frame = Frame(frame)
    search_frame.pack(fill=X, pady=5)
    search_entry = Entry(search_frame)
    search_entry.pack(side=LEFT, expand=True, fill=X, padx=(0,5))
    find_button = Button(search_frame, text="Find", bg='#FF8C00', fg='white')
    find_button.pack(side=RIGHT)
    
    # Results label
    Label(frame, text="results").pack(anchor=W)
    
    # Results text area
    results = Text(frame, height=12)
    results.pack(pady=5, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn.pack(pady=5)

def create_synaptic_section(root, x, y):
    frame = LabelFrame(root, text="Find synaptic partners", padx=10, pady=5)
    frame.place(x=x, y=y, width=300, height=800)
    
    # Source label
    Label(frame, text="source").pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=8)
    source.pack(pady=5, fill=X)
    
    # Get Partners button
    get_partners_btn = Button(frame, text="Get Partners", bg='#FF8C00', fg='white')
    get_partners_btn.pack(pady=5)
    
    # Partners label
    Label(frame, text="partners").pack(anchor=W)
    
    # Partners text area
    partners = Text(frame, height=8)
    partners.pack(pady=5, fill=X)
    
    # Button row with entry
    button_frame = Frame(frame)
    button_frame.pack(fill=X, pady=5)
    copy_btn = Button(button_frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn.pack(side=LEFT, padx=(0,5))
    partners_btn = Button(button_frame, text="Get Partners of Partners", bg='#FF8C00', fg='white')
    partners_btn.pack(side=LEFT, padx=(0,5))
    entry = Entry(button_frame, width=5)
    entry.pack(side=LEFT)
    
    # Partners of most common partners label
    Label(frame, text="partners of most common partners").pack(anchor=W)
    
    # Final text area
    common_partners = Text(frame, height=8)
    common_partners.pack(pady=5, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn2.pack(pady=5)

def create_outdated_section(root, x, y):
    frame = LabelFrame(root, text="Find potentially outdated", padx=10, pady=5)
    frame.place(x=x, y=y, width=300, height=800)
    
    # Source label
    Label(frame, text="source").pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=12)
    source.pack(pady=5, fill=X)
    
    # Update button
    update_btn = Button(frame, text="Update", bg='#FF8C00', fg='white')
    update_btn.pack(pady=5)
    
    # Source without outdated label
    Label(frame, text="source without outdated").pack(anchor=W)
    
    # Results text area
    results = Text(frame, height=12)
    results.pack(pady=5, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn.pack(pady=5)
    
    # Updated label
    Label(frame, text="updated").pack(anchor=W)
    
    # Updated text area
    updated = Text(frame, height=8)
    updated.pack(pady=5, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn2.pack(pady=5)

def create_proofread_section(root, x, y):
    frame = LabelFrame(root, text="Find proofread", padx=10, pady=5)
    frame.place(x=x, y=y, width=300, height=800)
    
    # Source label
    Label(frame, text="source").pack(anchor=W)
    
    # Source text area
    source = Text(frame, height=12)
    source.pack(pady=5, fill=X)
    
    # Get button
    get_btn = Button(frame, text="Get", bg='#FF8C00', fg='white')
    get_btn.pack(pady=5)
    
    # Proofread label
    Label(frame, text="proofread").pack(anchor=W)
    
    # Proofread text area
    proofread = Text(frame, height=12)
    proofread.pack(pady=5, fill=X)
    
    # Copy button
    copy_btn = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn.pack(pady=5)
    
    # Not proofread label
    Label(frame, text="not proofread").pack(anchor=W)
    
    # Not proofread text area
    not_proofread = Text(frame, height=8)
    not_proofread.pack(pady=5, fill=X)
    
    # Final copy button
    copy_btn2 = Button(frame, text="Copy", bg='#FF8C00', fg='white')
    copy_btn2.pack(pady=5)

def main():
    root = Tk()
    root.geometry('1440x900')
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
#B = Button(top, text ="Hello", command = helloCallBack)
#B.place(x=50,y=50)

#top.mainloop()

#get_synaptic_partners([720575941536100318,720575941338817903,720575941605725549])