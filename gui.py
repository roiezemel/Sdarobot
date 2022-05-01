from tkinter import *
from tkinter.font import Font

import sdarobot
import threading
from tkinter import ttk
import time
import memory
import seasons_lengths

stop_counting = False

alphabet = 'אבגדהוזחטיכלמנסעפצקרשת'


def is_english(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def rounded_rect(canvas, x, y, w, h, c):
    canvas.create_arc(x,   y,   x+2*c,   y+2*c,   start= 90, extent=90, style="arc")
    canvas.create_arc(x+w-2*c, y+h-2*c, x+w, y+h, start=270, extent=90, style="arc")
    canvas.create_arc(x+w-2*c, y,   x+w, y+2*c,   start=  0, extent=90, style="arc")
    canvas.create_arc(x,   y+h-2*c, x+2*c,   y+h, start=180, extent=90, style="arc")
    canvas.create_line(x+c, y,   x+w-c, y)
    canvas.create_line(x+c, y+h, x+w-c, y+h)
    canvas.create_line(x,   y+c, x,     y+h-c)
    canvas.create_line(x+w, y+c, x+w,   y+h-c)


def clock_number(num):
    return '0' * (2 - len(str(num))) + str(num)


def start_viewing():
    sdarobot.pause = stop_var.get()
    sdarobot.start(series.get(), int(season_var.get()),
                   int(first_episode_var.get()), int(episodes.get()), load_all_var.get())
    window.wm_state('normal')
    window.attributes('-topmost', 1)
    s, e = memory.get_next_episode(series.get())
    season_var.set(s)
    first_episode_var.set(e)


def show_time():
    global stop_counting
    global state
    start_label.config(image=start_disabled_photo)
    state = 2
    time.sleep(2)
    bar.place(x=50, y=top_y + 320)
    mul = 5
    bar['maximum'] = 100 * mul
    bar['value'] = 0
    bar_style.configure('text.Horizontal.TProgressbar', text='0 %')
    wait = sdarobot.wait_time / (100. * mul)
    window.attributes('-topmost', 1)

    while not sdarobot.page_loaded and not stop_counting:
        time.sleep(0.01)

    while not sdarobot.finished and not stop_counting:
        if bar['value'] != 0:
            error_label.place(x=27, y=top_y + 300)
        value = 0
        bar['value'] = 0
        for i in range(bar['maximum']):
            bar['value'] = int(value)
            bar.update()
            bar_style.configure('text.Horizontal.TProgressbar', text='{} %'
                                .format(round(value / mul)))
            time.sleep(wait)
            value += 1

    if stop_var.get():
        play_label.place(x=112.5, y=top_y + 310)
    else:
        window.attributes('-topmost', 0)
        window.wm_state('iconic')
        state = 0
        start_label.config(image=start_photo)
    error_label.place_forget()
    bar.place_forget()


def on_click(event):
    if state != 2 and series.get() and season_var.get() and first_episode_var.get() and episodes.get():
        global stop_counting
        stop_counting = False
        threading.Thread(target=start_viewing).start()
        threading.Thread(target=show_time).start()


def on_select(event):
    global stop_counting
    stop_counting = True
    s, e = memory.get_next_episode(series.get())
    season_var.set(s)
    first_episode_var.set(e)
    data_var.set(str(seasons_lengths.scan(series.get())[::3][-1]) + " seasons")


def advanced_click():
    if window.winfo_width() == 400:
        window.geometry('800x500')
        advanced_text.set('< Normal')
    else:
        window.geometry('400x500')
        advanced_text.set('Advanced >')


def on_adv_select(event):
    sdarobot.webdriver_path = webdrivers[web_driver_op.get()]
    settings = open('settings.txt', 'r')
    content = settings.readlines()
    content[0] = sdarobot.webdriver_path + "\n"
    settings.close()
    with open('settings.txt', 'w') as settings:
        settings.write(''.join(content))


def on_play_clicked(event):
    global state
    play_label.place_forget()
    sdarobot.pause = False
    window.attributes('-topmost', 0)
    window.wm_state('iconic')
    state = 0
    start_label.config(image=start_photo)


def update_series(series_to_rep, new_url, delete):
    file = open('series.csv', 'r')
    content = file.readlines()
    for i in range(len(content)):
        line = content[i].split(',')
        if series_to_rep == line[0]:
            content[i] = ''
    file.close()
    if not delete:
        if content[-1] and content[-1][-1] != '\n':
            content.append('\n')
        url = new_url if new_url.startswith('https://') else 'https://' + new_url
        content.append(series_to_rep + ',' + url)
    with open('series.csv', 'w') as series_file:
        series_file.write(''.join(content))
    memory.update_series_dict()
    global series_names
    series_names = sorted(list(memory.series_dict.keys()))
    series['values'] = series_names
    remove_options['values'] = series_names


def on_add_series():
    if name_entry.get() and url_entry.get():
        add_series_label.config(fg='grey')
        name_label.config(fg='grey')
        url_label.config(fg='grey')
        add_button.state(["disabled"])
        window.update_idletasks()
        update_series(name_entry.get(), url_entry.get(), False)
        seasons_lengths.delete_entry(name_entry.get())
        if seasons_lengths.scan(name_entry.get()) is None:
            update_series(name_entry.get(), url_entry.get(), True)
            add_series_label.config(fg='red')
            name_label.config(fg='red')
            url_label.config(fg='red')
        else:
            add_series_label.config(fg='green')
            name_label.config(fg='green')
            url_label.config(fg='green')

        add_button.state(["!disabled"])
        name_entry.delete(0, END)
        url_entry.delete(0, END)
        window.update_idletasks()


def on_remove_series():
    if remove_options.get():
        remove_series_label.config(fg='grey')
        remove_name_label.config(fg='grey')
        remove_button.state(["disabled"])
        window.update_idletasks()
        file = open('series.csv', 'r')
        content = file.readlines()
        for i in range(len(content)):
            line = content[i].split(',')
            if line[0] == remove_options.get():
                content[i] = ''
        file.close()
        with open('series.csv', 'w') as series_file:
            series_file.write(''.join(content))
        seasons_lengths.delete_entry(remove_options.get())
        memory.update_series_dict()
        global series_names
        series_names = sorted(list(memory.series_dict.keys()), key=sort_key)
        series['values'] = series_names
        remove_options['values'] = series_names
        prev_name_options['values'] = series_names
        remove_series_label.config(fg='green')
        remove_name_label.config(fg='green')
        remove_button.state(["!disabled"])
        window.update_idletasks()


def update_name(file_name):
    s_file = open(file_name, 'r')
    content = s_file.readlines()
    for i in range(len(content)):
        line = content[i].split(',')
        if line[0] == prev_name_options.get():
            line[0] = new_name_entry.get()
            content[i] = ','.join(line)
    s_file.close()
    with open(file_name, 'w') as series_file:
        series_file.write(''.join(content))


def on_rename_series():
    global series_names
    if not prev_name_options.get() or not new_name_entry.get():
        return
    update_name('series.csv')
    update_name('seasons.csv')
    memory.update_series_dict()
    series_names = sorted(list(memory.series_dict.keys()), key=sort_key)
    series['values'] = series_names
    remove_options['values'] = series_names
    prev_name_options['values'] = series_names
    rename_label.config(fg='green')
    prev_name_label.config(fg='green')
    new_name_label.config(fg='green')


def on_hover_out_or_in(event):
    global state
    if state == 0:
        start_label.config(image=start_on_hover_photo)
        state = 1
    elif state == 1:
        start_label.config(image=start_photo)
        state = 0


def on_play_hover(event):
    global play_state
    if not play_state:
        play_label.config(image=play_on_hover_photo)
        play_state = 1
    elif play_state == 1:
        play_label.config(image=play_photo)
        play_state = 0


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


def update_settings(var, index):
    file = open('settings.txt', 'r')
    content = file.readlines()
    content[index] = '1\n' if var.get() else '0\n'
    file.close()
    with open('settings.txt', 'w') as s_file:
        s_file.write(''.join(content))


def on_stop_checked():
    update_settings(stop_var, 1)


def on_load_all_checked():
    update_settings(load_all_var, 2)


def sort_key(word):
    if is_english(word):
        return word
    new_word = ""
    for l in word:
        new_word += chr(alphabet.find(l) + 97)
    return new_word.capitalize()


pad_y = (30, 0)

comp_bg = _from_rgb((255, 255, 255))
text_color = _from_rgb((255, 255, 255))
text_font = ('ariel', 12, 'bold')
comp_font = ('ariel', 14, 'bold')
adv_font = ('ariel', 10, 'bold')
adv_text_color = _from_rgb((240, 240, 240))
adv_color = _from_rgb((70, 70, 70))
background = _from_rgb((64, 64, 64))
buttons_color = _from_rgb((0, 117, 222))
series_names = sorted(list(memory.series_dict.keys()), key=sort_key)
webdrivers = {"ChromeDriver v 80": '80/chromedriver.exe',
              "ChromeDriver v 81": '81/chromedriver.exe',
              "ChromeDriver v 83": '83/chromedriver.exe',
              "ChromeDriver v 85": '85/chromedriver.exe',
              "ChromeDriver v 87": '87/chromedriver.exe',
              "ChromeDriver v 88": '88/chromedriver.exe',
              "ChromeDriver v 90": '90/chromedriver.exe'}

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
data_var.set("")
data_label = Label(window, textvariable=data_var, bg=background, fg=text_color)

series_var = StringVar(window)
series = ttk.Combobox(window, textvariable=series_var, font=text_font, state='readonly')
series.bind("<<ComboboxSelected>>", on_select)
series['values'] = series_names
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

stop_var = BooleanVar(window)
with open('settings.txt', 'r') as settings:
    stop_var.set(bool(int(settings.readlines()[1].replace('\n', ''))))
stop_style = ttk.Style()
stop_style.configure("Blue.TCheckbutton", background=background, foreground=text_color, font=adv_font)
stop_before_playing = ttk.Checkbutton(window, text='Pause before playing', takefocus=0, command=on_stop_checked,
                                      var=stop_var, style='Blue.TCheckbutton')

load_all_var = BooleanVar(window)
with open('settings.txt', 'r') as settings:
    load_all_var.set(bool(int(settings.readlines()[2].replace('\n', ''))))
load_all = ttk.Checkbutton(window, text='Load all at once', takefocus=0, command=on_load_all_checked,
                           var=load_all_var, style='Blue.TCheckbutton')


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
start_label.bind("<Enter>", on_hover_out_or_in)
start_label.bind("<Leave>", on_hover_out_or_in)
start_label.bind("<Button-1>", on_click)

play_state = 0
play_photo = PhotoImage(file='play.png', width=175, height=55)
play_on_hover_photo = PhotoImage(file='play_on_hover.png', width=175, height=55)
play_label = Label(window, image=play_photo, bg=background)
play_label.bind("<Enter>", on_play_hover)
play_label.bind("<Leave>", on_play_hover)
play_label.bind("<Button-1>", on_play_clicked)

advanced_text = StringVar(window)
advanced_text.set('Advanced >')
advanced_button = Button(window, textvariable=advanced_text, width=10,
                         command=advanced_click, bg=adv_color, fg=text_color)

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
load_all.place(x=pad_x, y=top_y + 240)
stop_before_playing.place(x=pad_x, y=top_y + 270)
start_label.place(x=112.5, y=top_y + 360)
advanced_button.place(x=312, y=top_y + 395)

# Advanced:
adv_frame = Frame(window, width=380, height=480, background=adv_color)
adv_frame.place(x=415, y=10)
adv_frame.grid_propagate(0)

web_driver_label = Label(adv_frame, text="Choose webdriver version: ", bg=adv_color, fg=adv_text_color)
web_driver_label.config(font=adv_font)

options = StringVar(adv_frame)
web_driver_op = ttk.Combobox(adv_frame, textvariable=options, font=adv_font, state='readonly')
web_driver_op.bind("<<ComboboxSelected>>", on_adv_select)
web_driver_op['values'] = list(webdrivers.keys())
web_driver_op.current(list(webdrivers.values()).index(sdarobot.webdriver_path))

add_series_label = Label(adv_frame, text="Add a new series: ", bg=adv_color, fg=adv_text_color)
add_series_label.config(font=adv_font)

name_label = Label(adv_frame, text="Name:", bg=adv_color, fg=adv_text_color)
name_label.config(font=adv_font)

url_label = Label(adv_frame, text="URL:", bg=adv_color, fg=adv_text_color)
url_label.config(font=adv_font)

name_entry = ttk.Entry(adv_frame)
name_entry.config(font=adv_font)

url_entry = ttk.Entry(adv_frame)
url_entry.config(font=adv_font)

add_button = ttk.Button(adv_frame, text="Add Series", command=on_add_series)

remove_series_label = Label(adv_frame, text="Remove a series: ", bg=adv_color, fg=adv_text_color)
remove_series_label.config(font=adv_font)

remove_name_label = Label(adv_frame, text="Name:", bg=adv_color, fg=adv_text_color)
remove_name_label.config(font=adv_font)

remove_var = StringVar(adv_frame)
remove_options = ttk.Combobox(adv_frame, textvariable=remove_var, font=adv_font, state='readonly', width=39)
remove_options['values'] = series_names

remove_button = ttk.Button(adv_frame, text="Remove Series", command=on_remove_series)

rename_label = Label(adv_frame, text="Rename a series:", bg=adv_color, fg=adv_text_color)
rename_label.config(font=adv_font)

prev_name_label = Label(adv_frame, text="Series:", bg=adv_color, fg=adv_text_color)
prev_name_label.config(font=adv_font)

new_name_label = Label(adv_frame, text="Rename:", bg=adv_color, fg=adv_text_color)
new_name_label.config(font=adv_font)

prev_name_var = StringVar(adv_frame)
prev_name_options = ttk.Combobox(adv_frame, textvariable=prev_name_var, font=adv_font, state='readonly', width=39)
prev_name_options['values'] = series_names

new_name_entry = ttk.Entry(adv_frame)
new_name_entry.config(font=adv_font)

rename_button = ttk.Button(adv_frame, text="Rename Series", command=on_rename_series)

web_driver_label.place(x=10, y=10)
web_driver_op.place(x=210, y=10)
add_series_label.place(x=10, y=60)
name_label.place(x=10, y=90)
name_entry.place(x=80, y=90, width=296)
url_label.place(x=10, y=120)
url_entry.place(x=80, y=120, width=296)
add_button.place(x=299, y=150)
remove_series_label.place(x=10, y=200)
remove_name_label.place(x=10, y=230)
remove_options.place(x=80, y=230)
remove_button.place(x=289, y=260)
rename_label.place(x=10, y=310)
prev_name_label.place(x=10, y=340)
prev_name_options.place(x=80, y=340)
new_name_label.place(x=10, y=370)
new_name_entry.place(x=80, y=370, width=296)
rename_button.place(x=289, y=400)

window.mainloop()
