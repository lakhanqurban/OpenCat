
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from opendrive2catmull.opendrive_converter import extract_road_geometry
from opendrive2catmull.catmull_rom_spline import CatmullRomSpline

def plot_spline_with_lanes(spline, points=None, spline_color='skyblue', points_color='green', ax=None):
    spline = np.array(spline)
    
    if ax is None:
        ax = plt.gca()
        
    # Plot the original points if provided
    if points is not None:
        points = np.array(points)
        ax.scatter(points[:, 0], points[:, 1], color=points_color, label='Original Points')

    # Plot the spline
    ax.plot(spline[:, 0], spline[:, 1], color=spline_color, label='Spline')

    # Optionally plot the lanes based on width (if desired)
    # Uncomment the following code if you want to visualize lane boundaries

    # for i in range(len(spline) - 1):
    #     x, y, z, width = spline[i]
    #     angle = np.arctan2(spline[i+1][1] - y, spline[i+1][0] - x)
        
    #     x_left = x - (width / 2) * np.sin(angle)
    #     y_left = y + (width / 2) * np.cos(angle)
        
    #     x_right = x + (width / 2) * np.sin(angle)
    #     y_right = y - (width / 2) * np.cos(angle)
        
    #     ax.plot([x, x_left], [y, y_left], 'r--')
    #     ax.plot([x, x_right], [y, y_right], 'b--')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    ax.grid(True)

