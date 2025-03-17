import os
import subprocess
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    hardware_interface = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("wall_e_firmware"),
            "launch",
            "hardware_interface.launch.py"
        ),
    )
    
    controller = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("wall_e_controller"),
            "launch",
            "controller.launch.py"
        ),
        launch_arguments={
            "use_simple_controller": "False",
            "use_python": "False"
        }.items(),
    )
    
    joystick = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("wall_e_controller"),
            "launch",
            "joystick_teleop.launch.py"
        ),
        launch_arguments={
            "use_sim_time": "False"
        }.items()
    )

    # Command to run the node in a new terminal
    command = "ros2 run wall_e_firmware imu_serial_receiver"

    # Open a new terminal and execute the command
    subprocess.Popen(["xterm", "-e", f"bash -c '{command}; exec bash'"])

    # Command to run the node in a new terminal
    command_two = "ros2 run wall_e_localization gps_reader.py"

    # Open a new terminal and execute the command
    subprocess.Popen(["xterm", "-e", f"bash -c '{command_two}; exec bash'"])

    return LaunchDescription([
        hardware_interface,
        controller,
        joystick,
    ])
