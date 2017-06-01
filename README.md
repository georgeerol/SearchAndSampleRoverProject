[//]: # (Image References)
[image_0]: ./misc/rover_image.gif
# Search and Sample Return Project
![alt text][image_0] 

This [Udacity clone project](https://github.com/udacity/RoboND-Rover-Project) is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html), and provides first hand experience with the three essential elements of robotics:
*   Perception
*   Decision Making
*   Actuation

## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  
One can test out the simulator by opening it up and choosing "Training Mode".

## Dependencies
Python 3.5 and Jupyter Notebooks is needed for this project.  The best way to get setup with these is to use Anaconda and the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit) and use [PyCharm IDE](https://www.jetbrains.com/pycharm/) for coding and debugging.
Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the methods needed to perform autonomous navigation and mapping.
To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.
Run the cells in the notebook from top to bottom to see the various data analysis steps.
The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!

## Writeup
### Mapping

#### Color Threshold
The mapping consisted of several steps but the first one had to do with reading images from the rover camera. Training images was acquired from the simulation to calibrate and determine where the rover can drive. The simulation-training environment consists of sand on the ground, which is very light in color and everything else, obstacles, in the environment are dark. Therefore Color Threshold was sets to determine where the rover can drive by figuring out where the areas of lighter color are. The image processing was very simple, an RGB threshold was applied to the image to get it to recognize the different objects in the simulation environment.
Below is one samples of Color threshold use to identify navigable terrain/obstacles/rock.

*	A Threshold of RGB > 150 does a nice job of identifying ground pixels only
*	A Minimum Threshold of RGB (199,174,36) and maximum threshold of RGB (137,111,13) for rock
*	A minimum obstacle threshold of RGB (2,2,2) and maximum obstacle threshold of RGB (45,45,45)
###### Color Threshold method:
```python
def color_thresh(img, rgb_threshold_min=(160, 160, 160), rgb_threshold_max=(255, 255, 255)):
    color_select = np.zeros_like(img[:, :, 0])
    above_thresh = (img[:, :, 0] >= rgb_threshold_min[0]) & (img[:, :, 0] <= rgb_threshold_max[0]) & \
                   (img[:, :, 1] >= rgb_threshold_min[1]) & (img[:, :, 1] <= rgb_threshold_max[1]) & \
                   (img[:, :, 2] >= rgb_threshold_min[2]) & (img[:, :, 2] <= rgb_threshold_max[2])
    color_select[above_thresh] = 1
    return color_select
```

#### Perspective Transform
From the Color Threshold the Rover was able to distinguish between obstacles, where to navigate and what’s a rock. However to know where and obstacle and where a rock is located, the perspective transform was use to each image that is provided from the rover camera to pinpoint the x and y position of each obstacles and rocks.
For the perspective transform to be probably transform a source and destination function was created and use so the image could be properly warped.
###### Perspective Transform method:
```python
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
    return warped
```
###### Source
```python
def get_source():
    return np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
```
###### Destination
```python
def get_destination(img):
    dst_size = 5
    bottom_offset = 6
    img_size = (img.shape[1], img.shape[0])
    destination = np.float32([[img_size[0] / 2 - dst_size, img_size[1] - bottom_offset],
                              [img_size[0] / 2 + dst_size, img_size[1] - bottom_offset],
                              [img_size[0] / 2 + dst_size, img_size[1] - 2 * dst_size - bottom_offset],
                              [img_size[0] / 2 - dst_size, img_size[1] - 2 * dst_size - bottom_offset],
                              ])
    return destination
```

#### Rover Centric Coordinates
From the Rover camera all navigable terrain pixel positions are extract and then transform to “rover-centric” coordinates.
Coordinate system allow us to describe the positions of objects in an environment with respect to the robot, in our case the rover’s camera. Meaning a coordinate frame where the rover camera is at (x,y) = (0,0).
###### Rover Centric Coordinates method:
```python
def rover_coords(binary_img):
    ypos, xpos = binary_img.nonzero() 
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel
```

#### Pixel to World Map
The threshold images pixels values to rover centric cords are done for the terrain, rock and obstacles.
The method `rover_coords` returns the x and y position for each of the white pixel from a threshold image then the function `pix_to_world` which converts the rover coordinates to the coordinates of the world, so showing what the rover camera is filming.
###### Pixel to world map method:
```python
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return x_pix_world, y_pix_world
```

**See the [Rover Project Test Notebook](https://github.com/fouliex/SearchAndSampleRoverProject/blob/master/code/Rover_Project_Test_Notebook.ipynb)  for all the mapping source code**
### Navigation

#### Main
###### [Main Folder](https://github.com/fouliex/SearchAndSampleRoverProject/tree/master/code)
The main script use for autonomous navigation and mapping is under the code folder, `drive_rover.py`.

#### Libaries
###### [Lib Folder](https://github.com/fouliex/SearchAndSampleRoverProject/tree/master/lib)
The lib folder contains the `perception.py`, `decision.py` and `supporting_function.py`.

* `perception.py` contains the method `perception_step` which contains all the analyzing tests done from the Jupyter notebook under the `process_image` method.
*  `decision.py` has conditional statements that demonstrate how the rover makes decision about adjusting throttle, brake and steering inputs.
*	`supportings_functions.py` contain 3 main methods:
     * `create_output_images` method is where the `Rover.worldmap` is compared with the ground map and gets converted, along with `Rover.vision_image`, into base64 strings to send back to the rover.
     * `RoverState` class is use to keep track of telemetry values and results from the analyzing test from the Jupyter notebook.
     * `telemetry`  method runs every time the simulator sends a new batch of data. It updates the Rover() object with new telemetry values.

## Simulation Settings and Results
The simulator was ran on a resolution of 800x600 with the graphics set to Good.
From these settings the rover was able to map most of the map with fidelity from 60% to 70% and find the location of rocks from his navigation path.
###### Simulation settings and result image
![Result Image](https://github.com/fouliex/SearchAndSampleRoverProject/blob/master/misc/result_image.png)

**Note: running the simulator with different choices of resolution and graphics quality may produce different results!**

## Rover project test Video
The videos are located in the [output folder](https://github.com/fouliex/SearchAndSampleRoverProject/tree/master/output)

## Rover Capture images
The images are located in the [calibration_image folder](https://github.com/fouliex/SearchAndSampleRoverProject/tree/master/calibration_images)

## Sample logs
The sample logs are located in the [test_dataset folder](https://github.com/fouliex/SearchAndSampleRoverProject/tree/master/test_dataset)

## Future work
* Make the Rover pick up the rocks when it sees them.
* After mapping the entire map the Rover should return to his initial position by saving it's starting x and y position.
* Fix the simulation so it doesn't crash often.
* Add Unit Test for each methods from the perception.py so one can see how each methods work and not spend too much time on manual regression test.
* Merge this project mapping with the [BlueBot project](https://github.com/fouliex/BlueBot)
