import numpy as np
import cv2


# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_threshold_min=(160, 160, 160), rgb_threshold_max=(255, 255, 255)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:, :, 0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:, :, 0] >= rgb_threshold_min[0]) & (img[:, :, 0] <= rgb_threshold_max[0]) & \
                   (img[:, :, 1] >= rgb_threshold_min[1]) & (img[:, :, 1] <= rgb_threshold_max[1]) & \
                   (img[:, :, 2] >= rgb_threshold_min[2]) & (img[:, :, 2] <= rgb_threshold_max[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel ** 2 + y_pixel ** 2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles


# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # TODO
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    # Apply a rotation
    xpix_rotated = xpix * np.cos(yaw_rad) - ypix * np.sin(yaw_rad)
    ypix_rotated = xpix * np.sin(yaw_rad) + ypix * np.cos(yaw_rad)
    # Return the result
    return xpix_rotated, ypix_rotated


# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world


# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))  # keep same size as input image

    return warped


def get_source():
    return np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])


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


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # 1) Define source and destination points for perspective transform
    img = Rover.img
    source = get_source()
    destination = get_destination(img)

    # 2) Apply perspective transform
    warped = perspect_transform(img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rocksamples
    navigable = color_thresh(warped, rgb_threshold_min=(150, 150, 150), rgb_threshold_max=(255, 255, 255))
    rock = color_thresh(warped, rgb_threshold_min=(130, 110, 0), rgb_threshold_max=(255, 230, 60))
    obstacle = color_thresh(warped, rgb_threshold_min=(0, 0, 0), rgb_threshold_max=(90, 90, 90))

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:, :, 0] = obstacle * 255
    Rover.vision_image[:, :, 1] = rock * 255
    Rover.vision_image[:, :, 2] = navigable * 255

    # 5) Convert map image pixel values to rover-centric coords
    x_pix, y_pix = rover_coords(navigable)
    x_pix_rock, y_pix_rock = rover_coords(rock)
    x_pix_obstacle, y_pix_obstacle = rover_coords(obstacle)

    # 6) Convert rover-centric pixel values to world coordinates
    world_size = 200
    scale = 10
    navigable_x_world, navigable_y_world = pix_to_world(x_pix, y_pix, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size,scale)
    rock_x_world, rock_y_world = pix_to_world(x_pix_rock, y_pix_rock, Rover.pos[0], Rover.pos[1], Rover.yaw, world_size,scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(x_pix_obstacle, y_pix_obstacle, Rover.pos[0], Rover.pos[1],
                                                      Rover.yaw, world_size, 15)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 255
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 255
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 255

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    distance, angle = to_polar_coords(x_pix, y_pix)
    Rover.nav_dists = distance
    Rover.nav_angles = angle

    # Update Rocks pixel distances and angles
    distance_rock, angle_rock = to_polar_coords(x_pix_rock, y_pix_rock)
    Rover.rock_dists = distance_rock
    Rover.rock_angles = angle_rock

    return Rover
