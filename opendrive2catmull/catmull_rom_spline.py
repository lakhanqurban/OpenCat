"""
This module defines a Catmull-Rom spline class and functions to generate splines from given points.

:param points: List of control points (x, y, [z, width]). At least 4 points are required.
:param num_spline_points: Number of points to generate per segment, default is 1.
:return: Generated Catmull-Rom spline points with optional z and width values.
"""
import numpy as np

class CatmullRomSpline:
    def __init__(self, points, alpha=0.5, num_spline_points=1):
        # Initialize the spline with given points, alpha, and number of spline points
        self.points = np.array(points)
        self.alpha = alpha
        self.num_spline_points = num_spline_points
        self.tangents = self.calculate_tangents()
        
    def tj(self, ti, p_i, p_j):
        # Calculate the parameter t for the given points
        xi, yi = p_i[:2]
        xj, yj = p_j[:2]
        return (((xj - xi) ** 2 + (yj - yi) ** 2) ** 0.5) ** self.alpha + ti
    
    def calculate_tangents(self):
        # Calculate tangents for the spline points
        tangents = []
        for i in range(1, len(self.points) - 1):
            t0 = 0
            t1 = self.tj(t0, self.points[i-1][:2], self.points[i][:2])
            t2 = self.tj(t1, self.points[i][:2], self.points[i+1][:2])
            tangent = (t2 - t0) * (self.points[i+1][:2] - self.points[i-1][:2])
            if np.linalg.norm(tangent) == 0:
                tangent = np.array([1e-6, 1e-6])
            tangents.append(tangent)
        tangents = np.array(tangents)
        tangents = np.concatenate([np.array([tangents[0]]), tangents, np.array([tangents[-1]])])
        return tangents

    def generate_spline(self):
        # Generate the Catmull-Rom spline
        spline = []
        for i in range(len(self.points) - 3):
            p0, p1, p2, p3 = self.points[i], self.points[i+1], self.points[i+2], self.points[i+3]
            t0, t1, t2, t3 = 0, self.tj(0, p0, p1), self.tj(self.tj(0, p0, p1), p1, p2), self.tj(self.tj(self.tj(0, p0, p1), p1, p2), p2, p3)
            t = np.linspace(t1, t2, self.num_spline_points).reshape(self.num_spline_points, 1)
            
            t1 = max(t1, t0 + 1e-6)
            t2 = max(t2, t1 + 1e-6)
            t3 = max(t3, t2 + 1e-6)

            # Calculate intermediate points
            a1 = (t1 - t) / (t1 - t0) * p0[:2] + (t - t0) / (t1 - t0) * p1[:2]
            a2 = (t2 - t) / (t2 - t1) * p1[:2] + (t - t1) / (t2 - t1) * p2[:2]
            a3 = (t3 - t) / (t3 - t2) * p2[:2] + (t - t2) / (t3 - t2) * p3[:2]

            # Calculate intermediate points
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3

            # Calculate final point
            c = (t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2

            # Interpolate z and width values
            z_values = np.linspace(p1[2], p2[2], self.num_spline_points)
            width_values = np.linspace(p1[3], p2[3], self.num_spline_points)

            # Append the calculated points to the spline
            for j, p in enumerate(c):
                spline.append((p[0], p[1], z_values[j], width_values[j]))

        return np.array(spline)

def catmull_rom_chain(points, num_spline_points=1):
    # Generate a Catmull-Rom spline chain from the given points
    if len(points) < 4:
        raise ValueError("At least 4 points are required")
    
    spline_generator = CatmullRomSpline(points, num_spline_points=num_spline_points)
    return spline_generator.generate_spline()

def catmull_rom(points, num_spline_points=1):
    # Generate a Catmull-Rom spline with default z and width values if not provided
    if len(points) < 4:
        raise ValueError("At least 4 points are required")
    
    complete_points = [(p[0], p[1], p[2] if len(p) > 2 else 0.0, p[3] if len(p) > 3 else 8.0) for p in points]

    spline_points = catmull_rom_chain(complete_points, num_spline_points)
    
    return spline_points
