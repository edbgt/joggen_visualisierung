import tkinter as tk
import tkinter.ttk as ttk
import os
import gpxpy
import matplotlib.pyplot as plt
import tilemapbase
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator
import datetime as dt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle
from tkinter import filedialog

from Map import Map
from Run import Run


class Main:
    def __init__(self):
        self.root = tk.Tk()

        # units
        self.time_units = ['Seconds', 'Minutes', 'Hours']
        self.distance_units = ['Meters', 'Kilometers']
        self.speed_units = ['Meters per Second', 'Kilometers per Hour']
        self.time_factor, self.distance_factor, self.speed_factor = 0, 0, 0.
        self.time_abreviation, self.distance_abreviation, self.speed_abreviation = '', '', ''

        if not self.load_from_file():
            self.chosen_time_unit = 'Seconds'
            self.chosen_distance_unit = 'Meters'
            self.chosen_speed_unit = 'Meters per Second'
            self.runs_directory = 'C:/Users/etienne/OneDrive/gpx_data'

        self.set_units()

        # gui elements init
        self.time_combobox = ttk.Combobox
        self.distance_combobox = ttk.Combobox
        self.speed_combobox = ttk.Combobox
        self.selection_combobox = ttk.Combobox
        self.map_frame = ttk.Frame

        self.rename_gpx_files(self.runs_directory)
        self.runs = list()
        self.read_gpx_files(self.runs_directory)
        self.chosen_run = self.runs[-1]
        self.build_gui()

    def build_gui(self):
        self.root.title('MUSS MIR NOCH 1 NAMEN ÜBERLEGEN')
        self.root.geometry('1000x700')

        # dimensions
        widget_width = 20
        pad_in = 5
        cell_height, cell_width = 1, 21

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

        # overview tab
        table_canvas = tk.Canvas(overview_tab)
        table_canvas.pack(expand=1, fill='both')
        scrollbar = tk.Scrollbar(overview_tab, orient='vertical', command=table_canvas.yview)
        scrollable_table = tk.Frame(table_canvas)
        scrollable_table.bind('<Configure>', lambda e: table_canvas.configure(scrollregion=table_canvas.bbox('all')))
        table_canvas.create_window((0, 0), window=scrollable_table, anchor='nw')
        table_canvas.configure(yscrollcommand=scrollbar.set)
        table_canvas.pack(expand=1, fill='both', side='left')
        scrollbar.pack(side='right', fill='y')

        # row 0
        for col, name in enumerate(['Date', 'Time', '', 'Distance [' + self.distance_abreviation + ']', 'Duration [' + self.time_abreviation + ']', 'Speed [' + self.speed_abreviation + ']']):
            tk.Label(scrollable_table, text=name, height=cell_height, width=cell_width, relief='groove',
                     font='Helvetica 9 bold').grid(column=col, row=0)
            if col == 2:
                tk.Label(scrollable_table, text=name, height=cell_height, width=cell_width + 8, relief='groove') \
                    .grid(column=col, row=0)
                continue
        # data
        for idx, run in enumerate(self.runs):
            tk.Label(scrollable_table, text=run.date, height=cell_height, width=cell_width, relief='groove').grid(column=0, row=idx + 1)
            tk.Label(scrollable_table, text=run.time[0:5], height=cell_height, width=cell_width, relief='groove').grid(column=1, row=idx + 1)
            tk.Label(scrollable_table, text='', height=cell_height, width=cell_width + 8, relief='groove').grid(column=2, row=idx + 1)
            tk.Label(scrollable_table, text=round(run.distance / self.distance_factor, 2), height=cell_height, width=cell_width, relief='groove').grid(column=3, row=idx + 1)
            tk.Label(scrollable_table, text=round(run.duration / self.time_factor, 2), height=cell_height, width=cell_width, relief='groove').grid(column=4, row=idx + 1)
            tk.Label(scrollable_table, text=round(run.average_speed * self.speed_factor, 2), height=cell_height, width=cell_width, relief='groove').grid(column=5, row=idx + 1)

        scrollable_table.columnconfigure(2, weight=1)

        # progress tab
        # distance frame
        distance_frame = ttk.Labelframe(progress_tab, text='Distance [' + self.distance_abreviation + ']')
        distance_frame.pack(expand=1, fill='both')
        distance_canvas = FigureCanvasTkAgg(self.plot_progress('distance'), distance_frame)
        distance_canvas.get_tk_widget().pack(side='left', fill='both')
        # duration frame
        duration_frame = ttk.Labelframe(progress_tab, text='Duration [' + self.time_abreviation + ']')
        duration_frame.pack(expand=1, fill='both')
        duration_canvas = FigureCanvasTkAgg(self.plot_progress('duration'), duration_frame)
        duration_canvas.get_tk_widget().pack(side='left', fill='both')
        # speed frame
        speed_frame = ttk.Labelframe(progress_tab, text='Average Speed [' + self.speed_abreviation + ']')
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

        # map tab
        # selection frame
        selection_frame = ttk.Labelframe(map_tab, text='Select run to display on map')
        selection_frame.pack(expand=0, fill='x')
        selection_frame.grid_columnconfigure(0, weight=1)

        # selection combobox
        self.selection_combobox = ttk.Combobox(selection_frame, textvariable=self.chosen_run, width=widget_width, state='readonly')
        self.selection_combobox['values'] = [run.date for run in self.runs]
        self.selection_combobox.current(self.runs.index(self.chosen_run))
        self.selection_combobox.grid(column=0, row=0, sticky='w', padx=pad_in, pady=pad_in)

        # generate button
        generate_button = ttk.Button(selection_frame, text='Generate', command=self.generate_map, width=widget_width)
        generate_button.grid(column=1, row=0, sticky='e', padx=pad_in, pady=pad_in)

        # map frame
        self.map_frame = ttk.Frame(map_tab)
        self.map_frame.pack(expand=0, fill='both')

        # map canvas
        # added in method generate_map()

    def generate_map(self):
        print('generating map')
        map = Map(self.runs[self.selection_combobox.current()])
        self.map_canvas = FigureCanvasTkAgg(map.get_plot(), self.map_frame)
        self.map_canvas.get_tk_widget().pack(side='left', fill='both')

    def rename_gpx_files(self, runs_directory):
        filenames = os.listdir(runs_directory)

        for file_to_eventually_rename in filenames:
            if file_to_eventually_rename[2] == ".":
                os.rename(runs_directory+ '/' + file_to_eventually_rename,
                          runs_directory + '/' + file_to_eventually_rename[6:10]
                          + "_"
                          + file_to_eventually_rename[3:5]
                          + "_"
                          + file_to_eventually_rename[0:2]
                          + file_to_eventually_rename[10:19]
                          + ".gpx")

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

    def set_units(self):
        if self.chosen_time_unit == 'Seconds':
            self.time_factor = 1
            self.time_abreviation = 's'
        elif self.chosen_time_unit == 'Minutes':
            self.time_factor = 60
            self.time_abreviation = 'min'
        elif self.chosen_time_unit == 'Hours':
            self.time_factor = 3600
            self.time_abreviation = 'h'
        else:
            raise RuntimeError

        if self.chosen_distance_unit == 'Meters':
            self.distance_factor = 1
            self.distance_abreviation = 'm'
        elif self.chosen_distance_unit == 'Kilometers':
            self.distance_factor = 1000
            self.distance_abreviation = 'km'
        else:
            raise RuntimeError

        if self.chosen_speed_unit == 'Meters per Second':
            self.speed_factor = 1
            self.speed_abreviation = 'm/s'
        elif self.chosen_speed_unit == 'Kilometers per Hour':
            self.speed_factor = 3.6
            self.speed_abreviation = 'km/h'
        else:
            raise RuntimeError

    def plot_progress(self, data_flag):
        fig = plt.figure(figsize=(10, 1))

        dates = [run.date for run in self.runs]
        x = [dt.datetime.strptime(d, '%d.%m.%Y').date() for d in dates]

        if data_flag == 'distance':
            y = [run.distance / self.distance_factor for run in self.runs]
        elif data_flag == 'duration':
            y = [run.duration / self.time_factor for run in self.runs]
        elif data_flag == 'speed':
            y = [run.average_speed * self.speed_factor for run in self.runs]
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
