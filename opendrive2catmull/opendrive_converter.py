"""
    This script processes OpenDRIVE files to extract road geometry data, generate spline points,
    and save the processed data to JSON files.
    
    :param geometry: Attributes defining the geometric properties of a road segment, including `x`, `y`,
    `length`, `hdg`, and `s`.
    :return: Functions for processing OpenDRIVE road data and generating spline points. The main function
    `process_and_save_road_data` extracts control points, generates spline points, and saves the data to a JSON file.
"""
import xml.etree.ElementTree as ET
import numpy as np
import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from opendrive2catmull.catmull_rom_spline import CatmullRomSpline
import matplotlib.pyplot as plt
import json
import logging
# logging.basicConfig(level=logging.INFO)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

def parse_geometry(geometry):
    """
    Extract geometric attributes from the geometry element.
    """
    x = float(geometry.get('x'))
    y = float(geometry.get('y'))
    length = float(geometry.get('length'))
    hdg = float(geometry.get('hdg'))
    s = float(geometry.get('s'))
    return x, y, length, hdg, s

def get_elevation_and_width(road, s):
    """
    Extract elevation and width of the road at a given position 's'.
    """
    z = 0.0  # Default elevation
    width = 0.0  # Default width

    # Extract elevation using the polynomial coefficients
    elevationProfile = road.find('elevationProfile')
    if elevationProfile is not None:
        for elevation in elevationProfile.findall('elevation'):
            s_elev = float(elevation.get('s', 0))
            length = float(elevation.get('length', float('inf')))
            if s_elev <= s < s_elev + length:
                a = float(elevation.get('a', 0.0))
                b = float(elevation.get('b', 0.0))
                c = float(elevation.get('c', 0.0))
                d = float(elevation.get('d', 0.0))
                ds = s - s_elev
                z = a + b * ds + c * ds**2 + d * ds**3
                break  # Found the correct segment

    # Width extraction
    lanes = road.find('lanes')
    if lanes is not None:
        for laneSection in lanes.findall('laneSection'):
            s_section = float(laneSection.get('s'))
            if s_section <= s:
                lanes_side = laneSection.find('right')  # Assuming 'right' lanes for width
                if lanes_side is not None:
                    for lane in lanes_side.findall('lane'):
                        lane_id = int(lane.get('id'))
                        for width_elem in lane.findall('width'):
                            s_offset = float(width_elem.get('sOffset', 0))
                            length = float(width_elem.get('length', float('inf')))
                            if s_offset <= s < s_offset + length:
                                a = float(width_elem.get('a', 0.0))
                                b = float(width_elem.get('b', 0.0))
                                c = float(width_elem.get('c', 0.0))
                                d = float(width_elem.get('d', 0.0))
                                ds = s - s_offset
                                lane_width = a + b * ds + c * ds**2 + d * ds**3
                                width += lane_width
    return z, width

def compute_lane_offset(road, s, lane_side):
    """
    Calculate the lane offset for a given side of the road.
    """
    lane_offset = 0.0
    lanes = road.find('lanes')
    if lanes is None:
        return lane_offset

    lane_sections = lanes.findall('laneSection')
    for lane_section in lane_sections:
        s_section = float(lane_section.get('s'))
        if s_section <= s:
            lanes_side = lane_section.find(lane_side)
            if lanes_side is not None:
                for lane in lanes_side.findall('lane'):
                    lane_id = int(lane.get('id'))
                    # Skip the center lane (id=0)
                    if lane_id == 0:
                        continue
                    for width_elem in lane.findall('width'):
                        s_offset = float(width_elem.get('sOffset', 0))
                        length = float(width_elem.get('length', float('inf')))
                        if s_offset <= s < s_offset + length:
                            a = float(width_elem.get('a', 0.0))
                            b = float(width_elem.get('b', 0.0))
                            c = float(width_elem.get('c', 0.0))
                            d = float(width_elem.get('d', 0.0))
                            ds = s - s_offset
                            width = a + b * ds + c * ds**2 + d * ds**3
                            lane_offset += width
                            break  # Width found for this lane
    return lane_offset

def get_road_geometry(opendrive_file: str, lane_side='right'): 
    """
    Extract road geometry data from an OpenDRIVE file.
    """
    try:
        tree = ET.parse(opendrive_file)
        root = tree.getroot()
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file: {e}")
        return []
    points = []
    for road in root.findall('road'):
        try:
            planView = road.find('planView')
            if planView is None:
                continue

            for geometry in planView.findall('geometry'):
                try:
                    x, y, length, hdg, s = parse_geometry(geometry)
                    z, width = get_elevation_and_width(road, s)
                    lane_offset = compute_lane_offset(road, s, lane_side)
                    offset_x = lane_offset * np.cos(hdg + np.pi / 2)
                    offset_y = lane_offset * np.sin(hdg + np.pi / 2)
                    point_x = x + offset_x
                    point_y = y + offset_y
                    points.append((point_x, point_y, z, width))
                except Exception as e:
                    logger.error(f"Error processing geometry data: {e}")
        except Exception as e:
            logger.error(f"Error processing road data: {e}")

    return points

def compute_centerline(right_lane_points, left_lane_points):
    """
    Calculate the center points between right and left lane points to create a reference line.
    """
    control_points = []
    for right, left in zip(right_lane_points, left_lane_points):
        center_x = (right[0] + left[0]) / 2
        center_y = (right[1] + left[1]) / 2
        center_z = (right[2] + left[2]) / 2
        center_width = (right[3] + left[3]) / 2
        control_points.append((center_x, center_y, center_z, center_width))
    return control_points

def generate_spline(opendrive_file: str):
    """
    Generate spline data from an OpenDRIVE file.
    """
    # Extract right and left lane points
    right_lane_points = get_road_geometry(opendrive_file, lane_side='right')
    left_lane_points = get_road_geometry(opendrive_file, lane_side='left')

    if len(right_lane_points) < 4 or len(left_lane_points) < 4:
        logger.error(f"Not enough points for Catmull-Rom Spline in file {opendrive_file}. At least 4 points are required.")
        return [], []

    # Calculate centerline points
    control_points = compute_centerline(right_lane_points, left_lane_points)

    # Generate spline using centerline points
    spline_generator = CatmullRomSpline(control_points, alpha=0.5, num_spline_points=1)
    spline_points = spline_generator.generate_spline()
    
    return control_points, spline_points

def save_road_data(opendrive_file, output_file):
    """
    Extract control points from the OpenDRIVE file, generate spline points, and save them to a JSON file.
    """
    # Generate spline data for the road from the OpenDRIVE file
    control_points, spline_points = generate_spline(opendrive_file)

    # Check if there are enough points for a valid spline
    if len(control_points) < 4 or len(spline_points) < 4:
        logger.error(
            f"Not enough points for Catmull-Rom Spline in file {opendrive_file}. "
            f"At least 4 spline points are required."
        )
        return  # Exit the function if not enough points are available

    # Ensure JSON compatibility for numpy arrays
    points_serializable = [point.tolist() if isinstance(point, np.ndarray) else point for point in spline_points]

    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the processed road data to the specified JSON file
    with open(output_file, 'w') as f:
        json.dump(points_serializable, f)
    
    print(f"Saved road data to {output_file}")

if __name__ == "__main__":
    from plot_spline import plot_spline_with_lanes  # Importing the plot function
    opendrive_dir = '/Users/ali/Documents/GitHub/udacity-test-generation/SensoDat/Opendrive_Files/campaign_2_frenetic'
    opendrive_files = [os.path.join(opendrive_dir, f"{i}.xodr") for i in range(10)]
    opendrive_files = [f for f in opendrive_files if os.path.exists(f)]
    logger.debug(f"Found {len(opendrive_files)} .xodr files in the directory {opendrive_dir}")

    output_dir = '/Users/ali/Documents/GitHub/udacity-test-generation/SensoDat/Roads/campaign_2_frenetic_road_data'
    
    plot_dir = '/Users/ali/Documents/GitHub/udacity-test-generation/SensoDat/Plots/campaign_2_frenetic_plots'

    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    for i, opendrive_file in enumerate(opendrive_files):
        output_file = os.path.join(output_dir, f"{i}.json")
        logger.debug(f"Processing file: {opendrive_file}")
        
        # Process and save the spline points directly
        save_road_data(opendrive_file, output_file)
        
        # Load spline data to plot (optional)
        control_points, spline_points = generate_spline(opendrive_file)
        if len(spline_points) > 0:
            original_points = get_road_geometry(opendrive_file)
            original_points = original_points[1:]  # Adjusting to plot without the first point if needed
            plt.figure()  # Create a new figure for each plot
            plot_spline_with_lanes(spline_points, original_points, spline_color='yellow', points_color='red')
            plt.close()
        else:
            logger.error("Failed to generate spline data.")
    print("Done processing all files.")
