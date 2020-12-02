import tilemapbase
import matplotlib.pyplot as plt

class Map:
    def __init__(self, new_run):
        tilemapbase.start_logging()
        tilemapbase.init(create=True)

        self.tiles = tilemapbase.tiles.build_OSM()
        self.run = new_run
        self.lat, self.lon = list(), list()
        self.extent = tilemapbase.Extent
        self.set_lat_and_lon(self.run.coordinates)
        self.set_extent(self.lat, self.lon)

    def set_extent(self, lat, lon):
        self.extent = tilemapbase.Extent.from_lonlat(min(lon), max(lon), min(lat), max(lat))
        self.extent = self.extent.to_aspect(1.0)

    def set_lat_and_lon(self, coordinates):
        for i in range(len(coordinates)):
            self.lat.append(coordinates[i][0])
            self.lon.append(coordinates[i][1])

    def get_image(self):
        fig, ax = plt.subplots(figsize=(10, 10), dpi=500)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        plotter = tilemapbase.Plotter(self.extent, self.tiles, width=1000)
        plotter.plot(ax, self.tiles)

        return plotter.as_one_image()

    def get_plot(self):
        fig, ax = plt.subplots(figsize=(10, 10), dpi=500)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        ax.imshow(self.get_image())
        ax.plot(5, 5)

        return fig