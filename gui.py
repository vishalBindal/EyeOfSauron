from tkinter import *
from tkinter.ttk import *
from pydub import AudioSegment, playback
import os
from config import settings,state

def play_alarm(file_path):
    file_type = file_path.split('.')[-1]
    sound = AudioSegment.from_file(file_path, file_type)
    sound_chunk = playback.make_chunks(sound, 3000)[0]
    playback.play(sound_chunk)

class settingsGui:
    def __init__(self):
        # Process for alarm audio playback
        self.play_process = None

        # Setting up the window
        self.window = Tk()
        self.window.title("The Great Eye's settings")
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

        # -- Setting up general tab --
        self.display_state = BooleanVar()
        self.display_state.set(settings['display_frames'])
        self.chk_display = Checkbutton(self.gen_tab, text='Display webcam video with eye segmentation', var=self.display_state, padding=5, command=self.display_callback)
        self.chk_display.grid(row=0, column=0, sticky='w')

        self.drowsy_state = BooleanVar()
        self.drowsy_state.set(settings['drowsy'])
        self.chk_drowsy = Checkbutton(self.gen_tab, text='Alarm if user is drowsy', var=self.drowsy_state, padding=5, command=self.ftr_drowsy_callback)
        self.chk_drowsy.grid(row=1, column=0, sticky='w')

        self.away_state = BooleanVar()
        self.away_state.set(settings['away'])
        self.chk_away = Checkbutton(self.gen_tab, text='Alarm if user is away', var=self.away_state, padding=5, command=self.ftr_away_callback)
        self.chk_away.grid(row=2, column=0, sticky='w')

        self.stare_state = BooleanVar()
        self.stare_state.set(settings['stare'])
        self.chk_stare = Checkbutton(self.gen_tab, text='Alarm if user is continuosly staring at the screen', var=self.stare_state, padding=5, command=self.ftr_stare_callback)
        self.chk_stare.grid(row=3, column=0, sticky='w')

        self.light_state = BooleanVar()
        self.light_state.set(settings['light'])
        self.chk_light = Checkbutton(self.gen_tab, text='Advise user regarding lighting conditions', var=self.light_state, padding=5, command=self.ftr_light_callback)
        self.chk_light.grid(row=4, column=0, sticky='w')

        brightness_frame = Frame(self.gen_tab)	   
        brightness_frame.grid(row=5, column=0, sticky='w')
        self.value_lbl = Label(brightness_frame, text="Healthy brightness reading threshold for light mode: ", padding=5)
        self.value_lbl.grid(row=0, column=0, sticky='w')	      
        self.value_var = IntVar()	       
        self.value_var.set(settings['brightness_threshold'])	 
        self.spin = Spinbox(brightness_frame, from_=0, to=300, width=5, textvariable=self.value_var, command=self.threshold_change)	     
        self.spin.grid(row=0, column=1, sticky='w')

        self.status_drowsiness = Label(self.gen_tab, text='Status "drowsiness": '+str(state['drowsiness']), padding=5)
        self.status_drowsiness.grid(row=6,column=0,sticky='w')
        self.status_away = Label(self.gen_tab, text='Status "away": '+str(state['away']), padding=5)
        self.status_away.grid(row=7,column=0,sticky='w')
        self.blink_required = Label(self.gen_tab, text='Status "stare": '+str(state['blink_required']), padding=5)
        self.blink_required.grid(row=8,column=0,sticky='w')
        self.night_mode = Label(self.gen_tab, text='Status "night dark mode required": '+str(state['night_dark_mode']), padding=5)
        self.night_mode.grid(row=9,column=0,sticky='w')
        self.bri_label = Label(self.gen_tab, text='Current brightness reading: '+str(int(state['brightness'])), padding=5)
        self.bri_label.grid(row=10,column=0,sticky='w')
        self.update_vals()

        # -- Setting up alarm tab --
        self.alarm_tab.rowconfigure([0,2,3], weight=1, minsize=30)
        self.alarm_tab.rowconfigure([1], weight=2, minsize=80)
        self.alarm_tab.columnconfigure(0, weight=1, minsize=200)

        self.alarm_header = Label(self.alarm_tab, text="Current alarm sound: None", padding=10)
        self.alarm_header.grid(column=0, row=0, sticky='nsew')

        self.alarms_dir = 'alarms'
        self.listbox = Listbox(self.alarm_tab, height = 10, width = 70, bg = "white", activestyle = 'dotbox', fg = "black")

        alarm_files = [f for f in os.listdir(self.alarms_dir) if os.path.isfile(os.path.join(self.alarms_dir, f))]

        if settings['alarm_file'] in alarm_files:
            i = alarm_files.index(settings['alarm_file'])
            alarm_files[0], alarm_files[i] = alarm_files[i], alarm_files[0]

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
    
    def update_vals(self):
        self.status_drowsiness.configure(text='Status "drowsiness": '+str(state['drowsiness']))
        self.status_away.configure(text='Status "away": '+str(state['away']))
        self.blink_required.configure(text='Status "blink required": '+str(state['blink_required']))
        self.night_mode.configure(text='Status "night dark mode required": '+str(state['night_dark_mode']))
        self.bri_label.configure(text='Current brightness reading: '+str(int(state['brightness'])))
        self.window.after(10, self.update_vals)

    def run(self):
        self.window.mainloop()

    def threshold_change(self):
        settings['brightness_threshold'] = self.spin.get()
        print('Brightness threshold changed to:', settings['brightness_threshold'])

    def display_callback(self):
        settings['display_frames'] = self.display_state.get()
        print('Set Display:', settings['display_frames'])

    def ftr_drowsy_callback(self):
        settings['drowsy'] = self.drowsy_state.get()
        print('Set Drowsy:', settings['drowsy'])

    def ftr_away_callback(self):
        settings['away'] = self.away_state.get()
        print('Set away:', settings['away'])

    def ftr_stare_callback(self):
        settings['stare'] = self.stare_state.get()
        print('Set stare:', settings['stare'])

    def ftr_light_callback(self):
        settings['light'] = self.light_state.get()
        print('Set Light:', settings['light'])

    def playcallback(self):
            selection = self.listbox.curselection()
            if selection:
                i = selection[0]
                f = self.file_names[i] + '.' + self.file_extensions[i]
                file_path = os.path.join(self.alarms_dir, f)
                print('Playing:', file_path)
                play_alarm(file_path)


    def selectalarm(self):
        selection = self.listbox.curselection()
        if selection:
            i = selection[0]
            f = self.file_names[i]
            self.alarm_header.configure(text='Current alarm sound: ' + f)
            settings['alarm_file'] = f + '.' + self.file_extensions[i]
            print('Alarm tone set to:', settings['alarm_file'])

if __name__=='__main__':
    gui = settingsGui()
    gui.run()

