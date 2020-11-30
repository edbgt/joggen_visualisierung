import tkinter as tk
import tkinter.ttk as ttk
import os
import gpxpy

from Run import Run


class Main:
    def __init__(self, new_runs_directory):
        self.runs_directory = new_runs_directory
        self.runs = list()
        self.read_gpx_files(self.runs_directory)
        self.build_gui()

    def build_gui(self):
        self.root = tk.Tk()
        self.root.title('MUSS MIR NOCH 1 NAMEN ÜBERLEGEN')
        self.root.geometry('1000x700')
        # main content frame
        main_content = ttk.Frame(self.root)
        main_content.pack(expand=1, fill='both')
        # parent for tabs
        tab_control = ttk.Notebook(main_content)
        # tabs
        overview_tab = ttk.Frame(tab_control)
        progress_tab = ttk.Frame(tab_control)
        map_tab = ttk.Frame(tab_control)
        # add tabs
        tab_control.add(overview_tab, text='Overview')
        tab_control.add(progress_tab, text='Progress')
        tab_control.add(map_tab, text='Map')

        tab_control.pack(expand=1, fill='both', side='left')

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


if __name__ == "__main__":
    main = Main('C:/Users/etienne/OneDrive/gpx_data')

    for run in main.runs:
        run.print()

    main.root.mainloop()
