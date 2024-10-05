from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory, get_package_prefix
import os
from os import pathsep

def generate_launch_description():

    wall_e_description = get_package_share_directory("wall_e_description")
    wall_e_description_prefix = get_package_prefix("wall_e_description")

    model_path = os.path.join(wall_e_description, "models")
    model_path += pathsep + os.path.join(wall_e_description_prefix, "share")

    env_varibale = SetEnvironmentVariable("GAZEBO_MODEL_PATH", model_path)

    #This model arg will contain the model we want to visualize in Rviz
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value= os.path.join(wall_e_description, "urdf", "wall_e.urdf.xacro"),
        description= "Absolute path to robot URDF file"
    )

    #The command cme from the class launch.substitutions it runs a normal command.
    # in our case the command is to transorm the xacro file into a normal urdf file to be read by the robot_state_publisher
    #The "model" is the saame model_arg we created before with it's values passed to the command to be ran
    robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]), value_type=str)

    robot_state_publisher = Node(
        package= "robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    #start the gazebo server
    start_gazebo_server = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory("gazebo_ros"),
        "launch",
        "gzserver.launch.py"
    )))

    #start the gazebo client
    start_gzebo_client = IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
        get_package_share_directory("gazebo_ros"),
        "launch",
        "gzclient.launch.py"
    )))

    #the gazebo once started will contain no object, so we need to include the object inside it
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-entity", "wall_e", "-topic", "robot_description"],
        output="screen"
    )

    return LaunchDescription([
        env_varibale,
        model_arg,
        robot_state_publisher,
        start_gazebo_server,
        start_gzebo_client,
        spawn_robot
    ])