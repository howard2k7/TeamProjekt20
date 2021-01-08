import numpy as np
import math
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import zmq
from time import sleep

from HexaplotReceiver import HexaplotReceiver


class Hexaplot:

    def __init__(self, ax_limits=[0.6, 0.6, 0.6], plt_pause_value=0.05, dot_color='white', line_color='black', show_lines=False):

        self.hr = HexaplotReceiver()
        self.ax_limits = ax_limits
        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')

        # Setting the axes properties
        self.ax.set_xlim3d([0.0, self.ax_limits[0]])
        self.ax.set_xlabel('X')
        self.ax.set_ylim3d([0.0, self.ax_limits[1]])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([0.0, self.ax_limits[2]])
        self.ax.set_zlabel('Z')

        self.center_x_offset = ax_limits[0] / 2
        self.center_y_offset = ax_limits[1] / 2
        self.center_z_offset = ax_limits[2] / 2

        self.ax.set_title('HexaPlotter')
        self.plt_pause_value = plt_pause_value
        self.show_lines = show_lines

        self.dot_color = dot_color
        self.line_color = line_color

        self.last_scatter_list = []
        self.last_line_list = []
        self.current_points = []
        self.current_lines = []

    def update_points(self, points=None, color='black'):
        if points:
            if self.last_scatter_list:
                for ls in self.last_scatter_list:
                    ls.remove()
                self.last_scatter_list = []

            if self.show_lines:
                self.plot_lines(points)

            for p in points:
                x = p[0]+self.center_x_offset
                y = p[1]+self.center_y_offset
                z = p[2]+self.center_z_offset
                last_scatter = self.ax.scatter(x, y, z, c=self.dot_color)
                self.last_scatter_list.append(last_scatter)

    def show_plot(self):
        while True:
            self.update_points(self.hr.getPoints())
            plt.pause(self.plt_pause_value)

    def plot_lines(self, points):
        self.ax.lines = []
        for i, p in enumerate(points[:-1]):
            p1 = p
            p2 = points[i+1]
            x = [p1[0]+self.center_x_offset, p2[0]+self.center_x_offset]
            y = [p1[1]+self.center_z_offset, p2[1]+self.center_y_offset]
            z = [p1[2]+self.center_y_offset, p2[2]+self.center_z_offset]
            self.last_line_list.append(self.ax.plot(x, y, z, c=self.line_color))


if __name__ == "__main__":
    hp = Hexaplot(dot_color='green', line_color='black', show_lines=False, ax_limits=[2, 2, 2])
    hp.show_plot()
