import logging
import picar
import cv2
import datetime
from end_to_end_lane_follower import EndToEndLaneFollower
from objects_on_road_processor import ObjectsOnRoadProcessor

_SHOW_IMAGE = True


class Car(object):

    __INITIAL_SPEED = 0
    __SCREEN_WIDTH = 320
    __SCREEN_HEIGHT = 240

    def __init__(self):
        """ Init camera and wheels"""
        logging.info('Creating a DeepPiCar...'     

    def __enter__(self):
        """ Entering a with statement """
        return self

    def __exit__(self, _type, value, traceback):
        """ Exit a with statement"""
        if traceback is not None:
            # Exception occurred:
            logging.error('Exiting with statement with exception %s' % traceback)

        self.cleanup()

    def cleanup(self):
        """ Reset the hardware"""
        logging.info('Stopping the car, resetting hardware.')
        self.back_wheels.speed = 0
        self.front_wheels.turn(90)
        self.camera.release()
        self.video_orig.release()
        self.video_lane.release()
        self.video_objs.release()
        cv2.destroyAllWindows()

    def drive(self, speed=__INITIAL_SPEED):
        """ Main entry point of the car, and put it in drive mode

        Keyword arguments:
        speed -- speed of back wheel, range is 0 (stop) - 100 (fastest)
        """

        logging.info('Starting to drive at speed %s...' % speed)
        self.back_wheels.speed = speed
        i = 0
        while self.camera.isOpened():
            _, image_lane = self.camera.read()
            image_objs = image_lane.copy()
            i += 1
            self.video_orig.write(image_lane)

            image_objs = self.process_objects_on_road(image_objs)
            self.video_objs.write(image_objs)
            show_image('Detected Objects', image_objs)

            image_lane = self.follow_lane(image_lane)
            self.video_lane.write(image_lane)
            show_image('Lane Lines', image_lane)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()
                break

    def process_objects_on_road(self, image):
        image = self.traffic_sign_processor.process_objects_on_road(image)
        return image

    def follow_lane(self, image):
        image = self.lane_follower.follow_lane(image)
        return image


############################
# Utility Functions
############################
def show_image(title, frame, show=_SHOW_IMAGE):
    if show:
        cv2.imshow(title, frame)


def main():
    with DeepPiCar() as car:
        car.drive(40)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5s:%(asctime)s: %(message)s')
    
    main()
