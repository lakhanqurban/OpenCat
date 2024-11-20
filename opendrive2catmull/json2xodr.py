"""
The `convert_json_to_opendrive` function reads OpenDRIVE data from a JSON file, converts it to XML format,
and saves each road section as a separate XML file in the specified output folder.

:param json_file: Path to the input JSON file containing OpenDRIVE data.
:param output_folder: Path to the folder where the output XML files will be saved.
"""
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')  # Convert the Element to a string
    reparsed = minidom.parseString(rough_string)  # Parse the string using minidom
    return reparsed.toprettyxml(indent="    ")  # Return the pretty-printed XML string with indentation

def convert_json_to_opendrive(json_file, output_folder):
    # Open and read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over each 'OpenDRIVE' section in the JSON data
    for opendrive_section in data:
        roads = opendrive_section['OpenDRIVE']['road']

        # Check if roads is a list or a single dictionary
        if isinstance(roads, dict):
            roads = [roads]

        # Debugging: Print the number of roads found in this section
        print(f"Number of roads found in this section: {len(roads)}")

        # Iterate over each road in the JSON data
        for road_data in roads:
            # Debugging: Print the road ID being processed
            print(f"Processing road ID: {road_data['@id']}")

            # Create the root element of the XML
            root = ET.Element('OpenDRIVE')
            # Create the road element with its attributes
            road = ET.SubElement(root, 'road', id=road_data['@id'], length=road_data['@length'])
            
            # Create the planView element
            planView = ET.SubElement(road, 'planView')
            # Iterate over each geometry in the planView
            for geom in road_data['planView']['geometry']:
                # Create the geometry element with its attributes
                geometry = ET.SubElement(planView, 'geometry', s=geom['@s'], x=geom['@x'], y=geom['@y'], hdg=geom['@hdg'], length=geom['@length'])
                # Create the paramPoly3 element with its attributes
                paramPoly3 = ET.SubElement(geometry, 'paramPoly3', pRange=geom['paramPoly3']['@pRange'], 
                                           aU=geom['paramPoly3']['@aU'], bU=geom['paramPoly3']['@bU'], 
                                           cU=geom['paramPoly3']['@cU'], dU=geom['paramPoly3']['@dU'], 
                                           aV=geom['paramPoly3']['@aV'], bV=geom['paramPoly3']['@bV'], 
                                           cV=geom['paramPoly3']['@cV'], dV=geom['paramPoly3']['@dV'])
            
            # Create the lanes element
            lanes = ET.SubElement(road, 'lanes')
            # Create the laneSection element with its attributes
            laneSection = ET.SubElement(lanes, 'laneSection', s=road_data['lanes']['laneSection']['@s'])
            
            # Iterate over each side (left, center, right) in the laneSection
            for side in ['left', 'center', 'right']:
                if side in road_data['lanes']['laneSection']:
                    lane_data = road_data['lanes']['laneSection'][side]['lane']
                    # Create the side element (left, center, or right)
                    lane = ET.SubElement(laneSection, side)
                    # Create the lane element with its attributes
                    lane_elem = ET.SubElement(lane, 'lane', id=lane_data['@id'], type=lane_data['@type'], level=lane_data['@level'])
                    # Create the width element with its attribute
                    width = ET.SubElement(lane_elem, 'width', a=lane_data['width']['@a'])
                    # Create the roadMark element with its attributes
                    roadMark = ET.SubElement(lane_elem, 'roadMark', type=lane_data['roadMark']['@type'], width=lane_data['roadMark']['@width'])
            
            # Pretty-print the XML
            pretty_xml = prettify_xml(root)
            
            # Write the pretty-printed XML to the output file named with the road ID
            xodr_file = os.path.join(output_folder, f"{road_data['@id']}.xodr")
            with open(xodr_file, 'w') as f:
                f.write(pretty_xml)


# Example usage
convert_json_to_opendrive(r'C:\\Users\\Qurban\\Documents\\GitHub\\Sensodat\\sdc_sim_data.campaign_2_ambiegen.json', r'C:\Users\Qurban\Documents\campaign_2_ambiegen')
