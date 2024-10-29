from functionalities.get_synaptic_partners import get_synaptic_partners
# import get_all_annotations

from tkinter import *
top = Tk()
top.geometry('1280x800')
# Code to add widgets will go here...

def helloCallBack():
    a = 5

B = Button(top, text ="Hello", command = helloCallBack)
B.place(x=50,y=50)

top.mainloop()

#get_synaptic_partners([720575941536100318,720575941338817903,720575941605725549])