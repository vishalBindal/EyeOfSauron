from tkinter import *
from tkinter.ttk import *
from pydub import AudioSegment, playback
import os

def play_alarm(file_path):
    sound = AudioSegment.from_mp3(file_path)
    sound_chunk = playback.make_chunks(sound, 3000)[0]
    playback.play(sound_chunk)

class settingsGui:
    def __init__(self):
        # Process for alarm audio playback
        self.play_process = None

        # Setting up the window
        self.window = Tk()
        self.window.title("Settings")
        self.window.geometry('600x400')
        
        # Setting window icon
        photo = PhotoImage(file = 'icons/img4.png')
        self.window.iconphoto(False, photo)

        # Setting up tabs
        tab_control = Notebook(self.window)
        self.alarm_tab = Frame(tab_control)
        self.gen_tab = Frame(tab_control)
        tab_control.add(self.gen_tab, text='General')
        tab_control.add(self.alarm_tab, text='Alarm')
        tab_control.pack(expand=1, fill='both')

        # -- Setting up features tab --
        self.drowsy_state = BooleanVar()
        self.drowsy_state.set(1)
        self.chk_drowsy = Checkbutton(self.gen_tab, text='Alarm if user is drowsy', var=self.drowsy_state, padding=5, command=self.ftr_drowsy_callback)
        self.chk_drowsy.grid(row=0, column=0, sticky='w')

        self.away_state = BooleanVar()
        self.away_state.set(1)
        self.chk_away = Checkbutton(self.gen_tab, text='Alarm if user is away', var=self.away_state, padding=5, command=self.ftr_away_callback)
        self.chk_away.grid(row=1, column=0, sticky='w')

        self.stare_state = BooleanVar()
        self.stare_state.set(1)
        self.chk_stare = Checkbutton(self.gen_tab, text='Alarm if user is continuosly staring at the screen', var=self.stare_state, padding=5, command=self.ftr_stare_callback)
        self.chk_stare.grid(row=2, column=0, sticky='w')

        self.light_state = BooleanVar()
        self.light_state.set(1)
        self.chk_light = Checkbutton(self.gen_tab, text='Advise user regarding lighting conditions', var=self.light_state, padding=5, command=self.ftr_light_callback)
        self.chk_light.grid(row=3, column=0, sticky='w')

        frame = Frame(self.gen_tab)
        frame.grid(row=4, column=0, sticky='w')
        self.time_lbl = Label(frame, text="Notification time before alarm (in seconds)", padding=5)
        self.time_lbl.grid(row=0, column=0, sticky='w')
        self.time_var = IntVar()
        self.time_var.set(10)
        self.spin = Spinbox(frame, from_=0, to=100, width=5, textvariable=self.time_var, command=self.time_val_change)
        self.spin.grid(row=0, column=1, sticky='w')

        # -- Setting up alarm tab --
        self.alarm_tab.rowconfigure([0,2,3], weight=1, minsize=30)
        self.alarm_tab.rowconfigure([1], weight=2, minsize=80)
        self.alarm_tab.columnconfigure(0, weight=1, minsize=200)

        self.alarm_header = Label(self.alarm_tab, text="Current alarm sound: None", padding=10)
        self.alarm_header.grid(column=0, row=0, sticky='nsew')

        self.alarms_dir = 'alarms'
        self.listbox = Listbox(self.alarm_tab, height = 10, width = 70, bg = "white", activestyle = 'dotbox', fg = "black")

        alarm_files = [f for f in os.listdir(self.alarms_dir) if os.path.isfile(os.path.join(self.alarms_dir, f))]
        self.file_names = [f.split('.')[0] for f in alarm_files]
        self.file_extensions = [f.split('.')[1] for f in alarm_files]

        for i,f in enumerate(self.file_names):
            self.listbox.insert(i+1, f)

        self.listbox.grid(column=0, row=1, sticky='nsew')
        self.listbox.select_set(0)
        self.selectalarm()

        self.listbox.configure(justify='center')

        
        self.btn_play = Button(self.alarm_tab, text='Play selected sound', command=self.playcallback)
        self.btn_select = Button(self.alarm_tab, text='Choose selected sound', command=self.selectalarm)
        self.btn_play.grid(column=0, row=2, sticky='nsew')
        self.btn_select.grid(column=0, row=3, sticky='nsew')
    
    def run(self):
        self.window.mainloop()

    def time_val_change(self):
        print(self.spin.get())

    def ftr_drowsy_callback(self):
        print(self.drowsy_state.get())

    def ftr_away_callback(self):
        print(self.away_state.get())

    def ftr_stare_callback(self):
        print(self.stare_state.get())

    def ftr_light_callback(self):
        print(self.light_state.get())

    def playcallback(self):
            selection = self.listbox.curselection()
            if selection:
                i = selection[0]
                f = self.file_names[i] + '.' + self.file_extensions[i]
                file_path = os.path.join(self.alarms_dir, f)
                print(file_path)
                play_alarm(file_path)


    def selectalarm(self):
        # global listbox
        selection = self.listbox.curselection()
        if selection:
            i = selection[0]
            f = self.file_names[i]
            self.alarm_header.configure(text='Current alarm sound: ' + f)
            print('Alarm tone set to:', f)

if __name__=='__main__':
    gui = settingsGui()
    gui.run()

