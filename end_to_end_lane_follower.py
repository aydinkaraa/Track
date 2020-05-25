import cv2
import numpy as np
import logging
import math
from keras.models import load_model
from hard_coded_lane_follower import HardCodedLaneFollower

_SHOW_IMAGE = False


class EndToEndLaneFollower(object):

    def __init__(self,
                 car=None,
                 model_path='/home/pi/Car/model/lanenavigation/data/model/lane_navigation.h5'):
        logging.info('Creating a LaneFollower...')

        self.car = car
        self.curr_steering_angle = 90
        self.model = load_model(model_path)
    def compute_steering_angle(self, frame):
        """ Find the steering angle directly based on video frame
            We assume that camera is calibrated to point to dead center
        """
        preprocessed = img_preprocess(frame)
        X = np.asarray([preprocessed])
        steering_angle = self.model.predict(X)[0]

        logging.debug('new steering angle: %s' % steering_angle)
        return int(steering_angle + 0.5) # round the nearest integer

    def follow_lane(self, frame):
        # Main entry point of the lane follower
        show_image("orig", frame)

        self.curr_steering_angle = self.compute_steering_angle(frame)
        logging.debug("curr_steering_angle = %d" % self.curr_steering_angle)

        if self.car is not None:
            self.car.front_wheels.turn(self.curr_steering_angle)
        final_frame = display_heading_line(frame, self.curr_steering_angle)

        return final_frame

    def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

    def img_preprocess(image):
    height, _, _ = image.shape
    image = image[int(height/2):,:,:]  # remove top half of the image, as it is not relevant for lane following
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)  # Nvidia model said it is best to use YUV color space
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
    image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
    return image






############################
# Test Functions
############################


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    test_video('/home/pi/DeepPiCar/models/lane_navigation/data/images/video01')
    #test_photo('/home/pi/DeepPiCar/models/lane_navigation/data/images/video01_100_084.png')
    # test_photo(sys.argv[1])
    # test_video(sys.argv[1])
