# OpenCat: Improving Interoperability of ADS Testing

OpenCat serves as a converter that transforms road network data from the OpenDRIVE format into Catmull-Rom splines. OpenDRIVE is a standard format used to describe road networks, particularly in simulations and ADS development. Catmull-Rom splines are a type of interpolating spline used to create smooth curves through a given set of points, which can be beneficial in modeling continuous paths for vehicle navigation and simulation.

Developed as part of research at the University of Milano-Bicocca and the Technical University of Munich, OpenCat enhances the interoperability of Advanced Driver Assistance Systems (ADAS) across various simulation platforms. By making ADAS test cases independent of specific frameworks like BeamNG.tech and Udacity, it improves the reusability of road scenarios for testing lane-keeping and other autonomous driving functions.

# How It Works

OpenCat extracts road geometry data from OpenDRIVE computes the centerline, and then generates a smooth Catmull-Rom spline representation. This allows ADAS models to be tested on realistic and transferable road topologies.

# Conversion Pipeline

- Extract road topology from OpenDRIVE (.xodr)
- Compute lane centerline based on road geometry.
- Generate smooth Catmull-Rom splines.
- Save & Evaluate converted roads in a format compatible with multiple simulators.

# Installation

To use OpenCat, clone the repository and install the required dependencies:

Clone the repository 
```sh
git clone https://github.com/lakhanqurban/OpenCat.git

cd OpenCat
```
Install dependencies
```sh
pip install -r requirements.txt
```
# Usage

1. Convert JSON back to OpenDRIVE (Optional): If you have a containerized (docker-based) dataset, you have to convert it to the original OpenDRIVE XML (.xodr) format.
   ```sh
   python json2xodr.py --input path/to/road.json --output path/to/output.xodr
   ```
2. Convert OpenDRIVE to Catmull-Rom Spline: Pass your input file to the opendrive_converter.py or manually change the input path inside the opendrive_converter.py file.
   ```sh
   python opendrive_converter.py --input path/to/road.xodr --output path/to/output.json
   ```
3. Measure Accuracy of Conversion: Run this script after generating splines to analyze accuracy and visualize the results.
   ```sh
   python accuracy_measurement.py --input path/to/original.xodr --converted path/to/output.json
   ```

# Citation

If you use OpenCat in your research, please cite the following paper:

 ```bibtex
@article{ali2025opencat,
  author    = {Qurban Ali and Andrea Stocco and Leonardo Mariani and Oliviero Riganelli},
  title     = {OpenCat: Improving Interoperability of ADS Testing},
  journal   = {arXiv preprint arXiv:2502.07719},
  year      = {2025},
  url       = {https://arxiv.org/abs/2502.07719}
}
 ```
# License

This project is licensed under the GPL-3.0 license. See the LICENSE file for details.
