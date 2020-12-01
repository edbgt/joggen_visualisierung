import tkinter as tk
import tkinter.ttk as ttk
import os
import gpxpy
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator
import datetime as dt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle
from tkinter import filedialog

from Run import Run


class Main:
    def __init__(self):
        # units
        self.time_units = ['Seconds', 'Minutes', 'Hours']
        self.distance_units = ['Meters', 'Kilometers']
        self.speed_units = ['Meters per Second', 'Kilometers per Hour']

        if not self.load_from_file():
            self.chosen_time_unit = 'Seconds'
            self.chosen_distance_unit = 'Meters'
            self.chosen_speed_unit = 'Meters per Second'
            self.runs_directory = 'C:/Users/etienne/OneDrive/gpx_data'

        self.runs = list()
        self.read_gpx_files(self.runs_directory)
        self.build_gui()

    def build_gui(self):
        self.root = tk.Tk()
        self.root.title('MUSS MIR NOCH 1 NAMEN ÜBERLEGEN')
        self.root.geometry('1000x700')

        # dimensions
        widget_width = 20
        pad_in = 5

        # main content frame
        main_content = ttk.Frame(self.root)
        main_content.pack(expand=1, fill='both')

        # parent for tabs
        tab_control = ttk.Notebook(main_content)

        # tabs
        overview_tab = ttk.Frame(tab_control)
        progress_tab = ttk.Frame(tab_control)
        map_tab = ttk.Frame(tab_control)
        heatmap_tab = ttk.Frame(tab_control)
        settings_tab = ttk.Frame(tab_control)

        tab_control.add(overview_tab, text='Overview')
        tab_control.add(progress_tab, text='Progress')
        tab_control.add(map_tab, text='Map')
        tab_control.add(heatmap_tab, text='Heatmap')
        tab_control.add(settings_tab, text='Settings')

        tab_control.pack(expand=1, fill='both', side='left')

        # progress tab
        # duration frame
        duration_frame = ttk.Labelframe(progress_tab, text='Duration')
        duration_frame.pack(expand=1, fill='both')
        duration_canvas = FigureCanvasTkAgg(self.plot_progress('duration'), duration_frame)
        duration_canvas.get_tk_widget().pack(side='left', fill='both')

        # distance frame
        distance_frame = ttk.Labelframe(progress_tab, text='Distance')
        distance_frame.pack(expand=1, fill='both')
        distance_canvas = FigureCanvasTkAgg(self.plot_progress('distance'), distance_frame)
        distance_canvas.get_tk_widget().pack(side='left', fill='both')

        # speed frame
        speed_frame = ttk.Labelframe(progress_tab, text='Average Speed')
        speed_frame.pack(expand=1, fill='both')
        speed_canvas = FigureCanvasTkAgg(self.plot_progress('speed'), speed_frame)
        speed_canvas.get_tk_widget().pack(side='left', fill='both')

        # settings tab
        info_label = ttk.Label(settings_tab, text='Changes are only applied after restart.')
        info_label.pack(fill='x', padx=pad_in, pady=pad_in)

        # units frame
        units_frame = ttk.Labelframe(settings_tab, text='Units')
        units_frame.pack(expand=1, fill='both')
        units_frame.grid_columnconfigure(0, weight=1)

        time_label = ttk.Label(units_frame, text='Time')
        time_label.grid(column=0, row=0, sticky='w', padx=pad_in, pady=pad_in)
        self.time_combobox = ttk.Combobox(units_frame, textvariable=self.chosen_time_unit, width=widget_width, state='readonly')
        self.time_combobox['values'] = self.time_units
        self.time_combobox.current(self.time_units.index(self.chosen_time_unit))
        self.time_combobox.grid(column=2, row=0, sticky='e', padx=pad_in, pady=pad_in)

        distance_label = ttk.Label(units_frame, text='Distance')
        distance_label.grid(column=0, row=1, sticky='w', padx=pad_in, pady=pad_in)
        self.distance_combobox = ttk.Combobox(units_frame, textvariable=self.chosen_distance_unit, width=widget_width, state='readonly')
        self.distance_combobox['values'] = self.distance_units
        self.distance_combobox.current(self.distance_units.index(self.chosen_distance_unit))
        self.distance_combobox.grid(column=2, row=1, sticky='e', padx=pad_in, pady=pad_in)

        speed_label = ttk.Label(units_frame, text='Speed')
        speed_label.grid(column=0, row=2, sticky='w', padx=pad_in, pady=pad_in)
        self.speed_combobox = ttk.Combobox(units_frame, textvariable=self.chosen_speed_unit, width=widget_width, state='readonly')
        self.speed_combobox['values'] = self.speed_units
        self.speed_combobox.current(self.speed_units.index(self.chosen_speed_unit))
        self.speed_combobox.grid(column=2, row=2, sticky='e', padx=pad_in, pady=pad_in)

        # general settings frame
        general_frame = ttk.Labelframe(settings_tab, text='General Settings')
        general_frame.pack(expand=1, fill='both')
        general_frame.grid_columnconfigure(0, weight=1)

        # set gpx data directory
        directory_label = ttk.Label(general_frame, text='Choose folder with GPX files to analyze:')
        directory_label.grid(column=0, row=0, sticky='w', padx=pad_in, pady=pad_in)
        directory_button = ttk.Button(general_frame, text='Browse', width=widget_width, command=self.get_directory)
        directory_button.grid(column=1, row=0, sticky='e', padx=pad_in, pady=pad_in)

        # display current directory
        current_directory_label = ttk.Label(general_frame, text='Currently chosen folder is:')
        current_directory_label.grid(column=0, row=1, sticky='w', padx=pad_in, pady=pad_in)
        current_directory_path_label = ttk.Label(general_frame, text=self.runs_directory)
        current_directory_path_label.grid(column=1, row=1, sticky='e', padx=pad_in, pady=pad_in)

        # save button
        save_button = ttk.Button(settings_tab, text='Save', command=self.save_to_file, width=widget_width)
        save_button.pack(padx=pad_in, pady=pad_in, anchor='e')

    def read_gpx_files(self, runs_directory):
        filenames = os.listdir(runs_directory)

        for filename in filenames:
            gpx_data = gpxpy.parse(open(runs_directory + '/' + filename))

            date = gpx_data.name[0:10]
            time = gpx_data.name[11:20]
            distance = gpx_data.length_3d()
            duration = gpx_data.get_duration()
            coordinates = [[point.latitude, point.longitude, point.elevation]
                           for track in gpx_data.tracks
                           for segment in track.segments
                           for point in segment.points]

            self.runs.append(Run(date, time, distance, duration, coordinates))

    def plot_progress(self, data_flag):
        fig = plt.figure(figsize=(10, 1))

        dates = [run.date for run in self.runs]
        x = [dt.datetime.strptime(d, '%d.%m.%Y').date() for d in dates]

        if self.chosen_time_unit == 'Seconds':
            time_factor = 1
        elif self.chosen_time_unit == 'Minutes':
            time_factor = 60
        elif self.chosen_time_unit == 'Hours':
            time_factor = 3600
        else:
            raise RuntimeError

        if self.chosen_distance_unit == 'Meters':
            distance_factor = 1
        elif self.chosen_distance_unit == 'Kilometers':
            distance_factor = 1000
        else:
            raise RuntimeError

        if self.chosen_speed_unit == 'Meters per Second':
            speed_factor = 1
        elif self.chosen_speed_unit == 'Kilometers per Hour':
            speed_factor = 3.6
        else:
            raise RuntimeError

        if data_flag == 'distance':
            y = [run.distance / distance_factor for run in self.runs]
        elif data_flag == 'duration':
            y = [run.duration / time_factor for run in self.runs]
        elif data_flag == 'speed':
            y = [run.average_speed * speed_factor for run in self.runs]
        else:
            raise RuntimeError

        plt.gca().xaxis.set_major_formatter(DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(YearLocator())
        plt.gca().xaxis.set_minor_locator(MonthLocator())
        plt.gca().xaxis.set_ticklabels([])

        plt.scatter(x, y)
        plt.gcf().autofmt_xdate()

        return fig

    def save_to_file(self):
        self.chosen_time_unit = self.time_units[self.time_combobox.current()]
        self.chosen_distance_unit = self.distance_units[self.distance_combobox.current()]
        self.chosen_speed_unit = self.speed_units[self.speed_combobox.current()]

        pickle.dump([self.chosen_time_unit,
                     self.chosen_distance_unit,
                     self.chosen_speed_unit,
                     self.runs_directory], open('settings.p', 'wb'))

    def load_from_file(self):
        try:
            settings_list = pickle.load(open('settings.p', 'rb'))
        except FileNotFoundError:
            return False

        self.chosen_time_unit = settings_list[0]
        self.chosen_distance_unit = settings_list[1]
        self.chosen_speed_unit = settings_list[2]
        self.runs_directory = settings_list[3]

        return True

    def get_directory(self):
        self.runs_directory = tk.filedialog.askdirectory()


if __name__ == "__main__":
    main = Main()
    main.root.mainloop()
