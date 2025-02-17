import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import os
import csv
import time
import sys

class AMRNav(Node):
    def __init__(self, home):
        super().__init__('amr_nav')
        self.navigator = BasicNavigator()

        base_path = '/home/thanawat/amr_ws/src/follow_person/csv'
        self.csv_filename_B = os.path.join(base_path, home)
        
        self.get_logger().info('Waiting Navigation2')
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('Navigation2 Ready!!')
        
        self.estimate_home = self.load_home_position()
        self.initial_pose()
    
    def load_home_position(self):
        if not os.path.exists(self.csv_filename_B):
            self.get_logger().error(f'ไม่พบไฟล์ {self.csv_filename_B}!')
            return None
        
        with open(self.csv_filename_B, 'r') as csvfile_B:
            reader = csv.reader(csvfile_B)
            next(reader) 
            for row in reader:
                try:
                    x, y, ox, oy, oz, ow = map(float, row[1:7])
                    return (x, y, ox, oy, oz, ow)
                except ValueError:
                    self.get_logger().error(f'ข้อมูลใน CSV ไฟล์ไม่ถูกต้อง: {row}')
        return None
    
    def initial_pose(self):
        if self.estimate_home is None:
            self.get_logger().error('ไม่พบข้อมูลตำแหน่งเริ่มต้น!')
            return

        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = "map"
        
        pose_msg.pose.position.x = self.estimate_home[0]
        pose_msg.pose.position.y = self.estimate_home[1]
        pose_msg.pose.orientation.x = self.estimate_home[2]
        pose_msg.pose.orientation.y = self.estimate_home[3]
        pose_msg.pose.orientation.z = self.estimate_home[4]
        pose_msg.pose.orientation.w = self.estimate_home[5]
        
        self.navigator.setInitialPose(pose_msg)
        self.get_logger().info('ตั้งค่าตำแหน่งเริ่มต้นจาก AMCL แล้ว')
        time.sleep(3)

def main():
    rclpy.init()
    home = sys.argv[1]
    node = AMRNav(home)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
