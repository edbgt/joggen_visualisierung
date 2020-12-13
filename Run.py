import matplotlib.pyplot as plt
import numpy as np


class Run:
    def __init__(self, new_date, new_time, new_distance, new_duration, new_coordinates):
        self.date = new_date
        self.time = new_time
        self.distance = new_distance
        self.duration = new_duration
        self.average_speed = self.distance / self.duration
        self.coordinates = new_coordinates

    def print(self):
        print('Run from {} at {}:\t{} kms in {} mins with an average speed of {} m/s'.format(self.date, self.time,
                np.round(self.distance / 1000, 2), np.round(self.duration / 60, 2), np.round(self.average_speed, 2)))

