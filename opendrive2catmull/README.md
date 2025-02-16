# json2xodr.py
Converts road network data from JSON format to OpenDRIVE (.xodr) XML format. Provide a JSON file containing road data, and the script will generate OpenDRIVE files that can be used for simulations.
# opendrive_converter.py
This script processes OpenDRIVE (.xodr) files, extracts road geometry data, generates spline points using Catmull Rom splines, and saves the processed data to JSON files. Run the script with an OpenDRIVE file to generate and save road splines in JSON format.

# accuracy_measurement.py
Evaluates the accuracy of generated splines compared to the original OpenDRIVE road geometry. Run this script after generating splines to analyze accuracy and visualize the results.
