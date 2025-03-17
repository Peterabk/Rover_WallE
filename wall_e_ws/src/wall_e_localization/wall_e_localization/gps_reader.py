#!/usr/bin/env python3

import serial
import struct
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

class GPSNode(Node):
    def __init__(self):
        super().__init__('gps_node')
        self.publisher_ = self.create_publisher(NavSatFix, '/gps/fix', 10)
        self.gps = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=460800,
            timeout=1,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        self.get_logger().info(f"Connected to GPS on {self.gps.portstr}")
        self.buffer = b""
        self.timer = self.create_timer(0.1, self.read_gps)  # 10 Hz read rate

    def parse_ubx_nav_pvt(self, data):
        if len(data) < 6 or data[0] != 0xb5 or data[1] != 0x62:
            return None, None
        if data[2] == 0x01 and data[3] == 0x07:  # NAV-PVT
            length = struct.unpack('<H', data[4:6])[0]
            if len(data) < 6 + length + 2:
                return None, None
            payload = data[6:6 + length]
            if length >= 92:
                lon = struct.unpack('<i', payload[24:28])[0] * 1e-7
                lat = struct.unpack('<i', payload[28:32])[0] * 1e-7
                return lat, lon
        return None, None

    def read_gps(self):
        try:
            data = self.gps.read(100)
            if data:
                self.buffer += data
                while len(self.buffer) >= 6:
                    if self.buffer.startswith(b'\xb5\x62'):
                        lat, lon = self.parse_ubx_nav_pvt(self.buffer)
                        if lat is not None and lon is not None:
                            msg = NavSatFix()
                            msg.header.stamp = self.get_clock().now().to_msg()
                            msg.header.frame_id = "gps"
                            msg.latitude = lat
                            msg.longitude = lon
                            msg.status.status = 0  # Assume fix, adjust if needed
                            msg.status.service = 1  # GPS service
                            self.publisher_.publish(msg)
                            self.get_logger().info(f"Published: Lat {lat:.6f}, Lon {lon:.6f}")
                            self.buffer = b""
                        else:
                            length = struct.unpack('<H', self.buffer[4:6])[0] if len(self.buffer) >= 6 else 0
                            if len(self.buffer) >= 6 + length + 2:
                                self.buffer = self.buffer[6 + length + 2:]
                            else:
                                break
                    else:
                        self.buffer = self.buffer[1:]
        except Exception as e:
            self.get_logger().error(f"Error reading GPS: {e}")
            self.buffer = b""

    def destroy_node(self):
        if self.gps.is_open:
            self.gps.close()
            self.get_logger().info("Serial port closed")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    gps_node = GPSNode()
    try:
        rclpy.spin(gps_node)
    except KeyboardInterrupt:
        gps_node.get_logger().info("Stopped by user")
    finally:
        gps_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()