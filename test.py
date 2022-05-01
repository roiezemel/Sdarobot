from tkinter import *
from tkinter.font import Font

import sdarobot
import threading
from tkinter import ttk
import time
import memory
import seasons_lengths

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

comp_bg = _from_rgb((255, 255, 255))
text_color = _from_rgb((255, 255, 255))
text_font = ('ariel', 12, 'bold')
comp_font = ('ariel', 14, 'bold')
adv_font = ('ariel', 10, 'bold')
adv_text_color = _from_rgb((240, 240, 240))
adv_color = _from_rgb((70, 70, 70))
background = _from_rgb((64, 64, 64))
buttons_color = _from_rgb((0, 117, 222))

window = Tk()
window.title("Welcome to Sdarobot")
window.geometry('400x500')
window.iconbitmap('icon.ico')
window['bg'] = background


header = Label(window, text="Welcome to Sdarobot!", bg=background, fg=buttons_color)
f = Font(header, comp_font)
f.configure(underline=True)
header.config(font=f)

url_label = Label(window, text="Series:", bg=background, fg=text_color)
url_label.config(font=text_font)

data_var = StringVar(window)
data_var.set("4 seasons")
data_label = Label(window, textvariable=data_var, bg=background, fg=text_color)

series_var = StringVar(window)
series = ttk.Combobox(window, textvariable=series_var, font=text_font, state='readonly')
# series.bind("<<ComboboxSelected>>", on_select)
# series['values'] = series_names
window.option_add('*TCombobox*Listbox.font', text_font)

season_label = Label(window, text="Season:", bg=background, fg=text_color)
season_label.config(font=text_font)

season_var = StringVar(window)
season = Spinbox(window, from_=1, to=20, width=2, bd=0, textvariable=season_var)
season.config(font=comp_font)

first_episode_label = Label(window, text="First episode:", bg=background, fg=text_color)
first_episode_label.config(font=text_font)

first_episode_var = StringVar(window)
first_episode = Spinbox(window, from_=1, to=100, width=2, bd=0, textvariable=first_episode_var)
first_episode.config(font=comp_font)

episodes_label = Label(window, text="Number of episodes:", bg=background, fg=text_color)
episodes_label.config(font=text_font)

episodes = Spinbox(window, from_=1, to=100, width=2, bd=0)
episodes.config(font=comp_font)

bar_style = ttk.Style(window)
bar_style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
# set initial text
bar_style.configure('text.Horizontal.TProgressbar', text='0 %')
bar = ttk.Progressbar(window, orient=HORIZONTAL, length=300, mode='determinate', style='text.Horizontal.TProgressbar')
bar['value'] = 0

state = 0
start_photo = PhotoImage(file='start_button1.png', width=175, height=55)
start_on_hover_photo = PhotoImage(file='start_button_hover1.png', width=175, height=55)
start_disabled_photo = PhotoImage(file='start_button_disabled1.png', width=175, height=55)
start_label = Label(window, image=start_photo, bg=background)
# start_label.bind("<Enter>", on_hover_out_or_in)
# start_label.bind("<Leave>", on_hover_out_or_in)
# start_label.bind("<Button-1>", on_click)

advanced_text = StringVar(window)
advanced_text.set('Advanced >')
advanced_button = Button(window, textvariable=advanced_text, width=10,
                         command=None, bg=adv_color, fg=text_color)  # advanced_click

error_label = Label(window, text="An error has occurred. Wait just a few more seconds :)", bg=background, fg=text_color)
error_label.config(font=adv_font)

top_y = 70
pad_x = 10
header.place(x=95, y=10)
url_label.place(x=pad_x, y=top_y)
series.place(x=185, y=top_y)
data_label.place(x=185, y=top_y + 30)
season_label.place(x=pad_x, y=top_y + 60)
season.place(x=347, y=top_y + 60)
first_episode_label.place(x=pad_x, y=top_y + 120)
first_episode.place(x=347, y=top_y + 120)
episodes_label.place(x=pad_x, y=top_y + 180)
episodes.place(x=347, y=top_y + 180)
bar.place(x=50, y=top_y + 320)
error_label.place(x=27, y=top_y + 300)
start_label.place(x=112.5, y=top_y + 360)
advanced_button.place(x=312, y=top_y + 395)

window.mainloop()
