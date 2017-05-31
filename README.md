[//]: # (Image References)
[image_0]: ./misc/rover_image.jpg
# Search and Sample Return Project
![alt text][image_0] 

This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) and it will give you first hand experience with the three essential elements of robotics, which are perception, decision making and actuation.  You will carry out this project in a simulator environment built with the Unity game engine.  

## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Dependencies
You'll need Python 3 and Jupyter Notebooks installed to do this project.  The best way to get setup with these if you are not already is to use Anaconda following along with the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit). 


Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Recording Data
I've saved some test data for you in the folder called `test_dataset`.  In that folder you'll find a csv file with the output data for steering, throttle position etc. and the pathnames to the images recorded in each run.  I've also saved a few images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, you should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the lesson for performing the various steps of this project.  The notebook should function as is without need for modification at this point.  To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py` and it's your job to fill in the function called `perception_step()` with the appropriate processing steps and update the rover map. `decision.py` includes another function called `decision_step()`, which includes an example of a conditional statement you could use to navigate autonomously.  Here you should implement other conditionals to make driving decisions based on the rover's state and the results of the `perception_step()` analysis.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!  It doesn't drive that well yet, but it's your job to make it better!  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results!  Make a note of your simulator settings in your writeup when you submit the project.**

## Writeup
The goal of this project is to perform autonomous navigation and mapping. With each new image we receive from the rover's camera, we can make decision about sending commands like throttle, brake and steering to rover therefore it becomes autonomous.

### Mapping

#### Color Threshold
The mapping consisted of several steps but the first one had to do with reading images from the rover camera. Training images was acquired from the simulation to calibrate and determine where the rover can drive. The simulation-training environment consists of sand on the ground, which is very light in color and everything else, obstacles, in the environment are dark. Therefore Color Threshold was sets to determine where the rover can drive by figuring out where the areas of lighter color are. The image processing was very simple, an RGB threshold was applied to the image to get it to recognize the different objects in the simulation environment.
Below is Color threshold to identify navigable terrain/obstacles/rock samples applied are:

*	A Threshold of RGB > 160 does a nice job of identifying ground pixels only
*	A Minimum Threshold of RGB (199,174,36) and maximum threshold of RGB (137,111,13) for rock
*	A minimum obstacle threshold of RGB (2,2,2) and maximum obstacle threshold of RGB (45,45,45)

#### Perspective Transform
From the Color Threshold the Rover was able to distinguish between obstacles, where to navigate and what’s a rock. However to know where and obstacle and where a rock is located, the perspective transform was use to each image that is provided from the rover camera to pinpoint the x and y position of each obstacles and rocks.
For the perspective transform to be probably transform a source and destination function was created and use so the image could be properly warped.

#### Rover Centric Coordinates
From the Rover camera all navigable terrain pixel positions are extract and then transform to “rover-centric” coordinates.
Coordinate system allow us to describe the positions of objects in an environment with respect to the robot, in our case the rover’s camera. Meaning a coordinate frame where the rover camera is at (x,y) = (0,0).

#### Pixel to world map
The threshold images pixels values to rover centric cords are done for the terrain, rock and obstacles. The function rover_coords returns the x and y position for each of the white pixel from a threshold image then the function pix_to_world()  converts the rover coordinates to the coordinates of the world, so showing what the rover camera is filming.

### Navigation

#### Main
The main script use for autonomous navigation and mapping is under the code folder, drive_rover.py.

#### Lib
The lib folder contains the `perception.py`, `decision.py` and `supporting_function.py`.

* `perception.py` contains the method `perception_step` which contains all the analyzing tests done from the Jupyter notebook under the `process_image` method.
*  `decision.py` has conditional statements that demonstrate how the rover makes decision about adjusting throttle, brake and steering inputs.
*	`supportings_functions.py` contain 3 main methods:
     * `create_output_images` method is where the `Rover.worldmap` is compared with the ground map and gets converted, along with `Rover.vision_image`, into base64 strings to send back to the rover.
     * `RoverState` class is use to keep track of telemetry values and results from the analyzing test from the Jupyter notebook.
     * `Telemetry`  method runs every time the simulator sends a new batch of data. It updates the Rover() object with new telemetry values.

## Simulation Settings and Results
The simulator was ran on a resolution of 800x600 with the graphics set to Good.
From these settings the rover was able to map most of the map with fidelity from 60% to 70% and find the location of rocks from his navigation path.
