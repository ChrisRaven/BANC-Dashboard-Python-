import customtkinter as ctk

from find_annotated.frontend import *
from get_synaptic_partners.frontend import *
from update_outdated.frontend import *
from find_proofread.frontend import *
from find_differences.frontend import *
from check_coords.frontend import *
from connectivity.frontend import *


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.geometry('750x830')
root.title('BANC Dashboard')
root.resizable(False, False)

tabview = ctk.CTkTabview(root)
tabview.pack(expand=True, fill='both', padx=10, pady=10)

# Create tabs
tabs = {
  'annotated': tabview.add('Find Annotated'),
  'synaptic': tabview.add('Synaptic Partners'),
  'outdated': tabview.add('Update Outdated'),
  'proofread': tabview.add('Find Proofread'),
  'differences': tabview.add('Differences'),
  'coords': tabview.add('Check coords'),
  'connectivity': tabview.add('Connectivity'),
}

# Create sections
create_annotated_section(tabs['annotated'], 0, 0)
create_synaptic_partners_section(tabs['synaptic'], 0, 0)
create_update_outdated_section(tabs['outdated'], 0, 0)
create_proofread_section(tabs['proofread'], 0, 0)
create_differences_section(tabs['differences'], 0, 0)
create_coords_section(tabs['coords'], 0, 0)
create_connectivity_section(tabs['connectivity'], 0, 0)

root.mainloop()
