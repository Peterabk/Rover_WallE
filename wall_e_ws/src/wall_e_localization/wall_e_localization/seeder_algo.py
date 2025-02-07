#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import String
import serial
import time
import math


class SeederAlgo(Node):

    def __init__(self):
        super().__init__("seeder_algo")
        self.odom_sub_ = self.create_subscription(Odometry, "odom", self.odomCallback, 10)
     

        # Initialize parameters and variables
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value

        self.esp32 = None
        self.connect_to_esp32()

        self.distance_traveled = 0.0
        self.last_position = None

    def connect_to_esp32(self):
        try:
            self.esp32 = serial.Serial(self.port, self.baudrate, timeout=1)
            self.get_logger().info(f"Connected to ESP32 on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to connect to ESP32: {e}")
            
    def flash_led(self, angle):
        if self.esp32 and self.esp32.is_open:
            command = f"{angle}\n"  # Send angle command as a string
            self.esp32.write(command.encode('utf-8'))
            self.get_logger().info(f"Sent angle {angle} to ESP32")
    def odomCallback(self, odom):
        

        # Compute distance using odometry, not IMU acceleration
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y

        if self.last_position is None:
            self.last_position = (x, y)
            return

        # Calculate distance traveled
        distance = math.sqrt((x - self.last_position[0]) ** 2 + (y - self.last_position[1]) ** 2)
        self.distance_traveled += distance
        self.last_position = (x, y)

        # Check if distance threshold is reached
        if self.distance_traveled >= 1.0:
            self.flash_led(90)  # Move servo to 90 degrees
            time.sleep(1)
            self.flash_led(0)  # Move servo back to 0 degrees
            self.distance_traveled = 0.0




def main():
    rclpy.init()

    seeder_algo = SeederAlgo()
    rclpy.spin(seeder_algo)
    
    seeder_algo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()