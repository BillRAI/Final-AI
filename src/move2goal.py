#!/usr/bin/python3
import rospy
import tf.transformations
import time
import numpy as np
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Pose, Point, Quaternion
from actionlib_msgs.msg import GoalStatus
import actionlib
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from actionlib import SimpleActionClient
from move_base_msgs.msg import MoveBaseAction
import glob
import os
with open('/home/bill/Downloads/coordinates.txt', 'r') as file:
    lines = file.readlines()

move_base_client = SimpleActionClient('move_base', MoveBaseAction)

class moveBaseAction():
    def __init__(self):
        self.move_base_action = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        self.move_base_action.wait_for_server(rospy.Duration(5))

    def createGoal(self, x, y, theta):
        quat = tf.transformations.quaternion_from_euler(0, 0, theta)

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(x, y, 0.0), Quaternion(quat[0], quat[1], quat[2], quat[3]))

        return goal

    def moveToPoint(self, x, y, theta):
        target_point = self.createGoal(x, y, theta)
        self.moveToGoal(target_point)

    def moveToGoal(self, goal):
        self.move_base_action.send_goal(goal)
        success = self.move_base_action.wait_for_result()
        state = self.move_base_action.get_state()
        rospy.loginfo("Move to (%f, %f, %f) ->" % (goal.target_pose.pose.position.x, goal.target_pose.pose.position.y, goal.target_pose.pose.orientation.z))
        if success and state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Complete")
            return True
        else:
            rospy.logwarn("Failed to reach goal")
            return False
        
def find_latest_coordinates_file(directory):
    files = glob.glob(os.path.join(directory, 'coordinates(*).txt'))

    if files:
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    else:
        return None

def obstacle_detected(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 100, 100])  # Lower HSV values for red
    upper_red = np.array([10, 255, 255])  # Upper HSV values for red

    mask = cv2.inRange(hsv_image, lower_red, upper_red)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        return True

    return False


def image_callback(msg):
    bridge = CvBridge()
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError as e:
        rospy.logerr("CvBridge Error: %s", e)
        return

    if obstacle_detected(cv_image):
        rospy.logwarn("Obstacle detected! Stopping robot...")
        move_base_client.cancel_all_goals()
    else:
        rospy.loginfo("No obstacles detected. Continuing...")
        
        next_waypoint()

def next_waypoint():
    global current_index, lines, move_base_client

    if current_index < len(lines):
        x, y = map(float, lines[current_index].split())
        mba = moveBaseAction()
        mba.moveToPoint(x, y, 0.0)
        current_index += 1
    else:
        rospy.loginfo("All waypoints reached. Navigation complete.")


def main():
    rospy.init_node('Group6', anonymous=True)
    rospy.Subscriber('/usb_cam/image_raw', Image, image_callback)

    coordinates_directory = '/home/bill/Downloads/'

    latest_file = find_latest_coordinates_file(coordinates_directory)

    if latest_file:
        rospy.loginfo("Using coordinates file: %s" % latest_file)

        lines = [line.strip() for line in open(latest_file, 'r')]

        mba = moveBaseAction()
        for line in lines:
            x, y = map(float, line.split())
            mba.moveToPoint(x, y, 0.0)
            rospy.sleep(1) 

        rospy.loginfo("All waypoints reached. Navigation complete.")
    else:
        rospy.logerr("No coordinates file found in directory: %s" % coordinates_directory)

    rospy.spin()  # Keeps the node running


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

