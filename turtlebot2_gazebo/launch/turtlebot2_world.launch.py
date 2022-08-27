import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PythonExpression, Command
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    turtlebot2_gazebo_package = FindPackageShare(
        package="turtlebot2_gazebo").find("turtlebot2_gazebo")

    turtlebot2_description_package = FindPackageShare(
        package="turtlebot2_description").find("turtlebot2_description")

    gazebo_ros_package = FindPackageShare(
        package="gazebo_ros").find("gazebo_ros")

    kobuki_description_package = FindPackageShare(
        package="kobuki_description").find("kobuki_description")

    install_dir1 = get_package_prefix("turtlebot2_description")
    install_dir2 = get_package_prefix("kobuki_description")
    gazebo_models_path1 = os.path.join(
        turtlebot2_description_package, "meshes")
    gazebo_models_path2 = os.path.join(kobuki_description_package, "meshes")

    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]

    if "GAZEBO_MODEL_PATH" in os.environ:
        os.environ["GAZEBO_MODEL_PATH"] = (
            os.environ["GAZEBO_MODEL_PATH"]
            + ":"
            + install_dir2
            + "/share"
            + ":"
            + gazebo_models_path2
        )
    else:
        os.environ["GAZEBO_MODEL_PATH"] = (
            install_dir2 + "/share" + ":" + gazebo_models_path2
        )

    if "GAZEBO_MODEL_PATH" in os.environ:
        os.environ["GAZEBO_MODEL_PATH"] = (
            os.environ["GAZEBO_MODEL_PATH"]
            + ":"
            + install_dir1
            + "/share"
            + ":"
            + gazebo_models_path1
        )
    else:
        os.environ["GAZEBO_MODEL_PATH"] = (
            install_dir1 + "/share" + ":" + gazebo_models_path1
        )

    if "GAZEBO_PLUGIN_PATH" in os.environ:
        os.environ["GAZEBO_PLUGIN_PATH"] = (
            os.environ["GAZEBO_PLUGIN_PATH"] + ":" + install_dir1 + "/lib"
        )
    else:
        os.environ["GAZEBO_PLUGIN_PATH"] = install_dir1 + "/lib"

    print("GAZEBO MODELS PATH==" + str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH==" + str(os.environ["GAZEBO_PLUGIN_PATH"]))

    # ============================================================
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_package, "launch", "gazebo.launch.py"),
        )
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace=namespace,
        remappings=remappings,
        parameters=[
            {
                "robot_description": Command(
                    [
                        "xacro ",
                        os.path.join(
                            turtlebot2_description_package,
                            "robots/kobuki_hexagons_hokuyo.urdf.xacro",
                        ),
                    ]
                )
            },
            {"use_sim_time": use_sim_time},
        ],
    )

    spawn_tb2 = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_entity",
        namespace=namespace,
        output="screen",
        arguments=[
            "-entity",
            "turtlebot2",
            "-topic",
            # TODO - branie namespace z launch configuration
            ("/tb2_5/robot_description"),
            "-x",
            "0",
            "-y",
            "0",
        ],
    )

    # mapping_launch=Node(
    #     parameters=[
    #         {'use_sim_time': use_sim_time},
    #         {get_package_share_directory("turtlebot2_gazebo") + '/config/slam_toolbox_params.yaml'}
    #     ],
    #     package='slam_toolbox',
    #     executable='async_slam_toolbox_node',
    #     name='slam_toolbox',
    #     output='screen'
    # )

    ld = LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=[os.path.join(
                turtlebot2_gazebo_package, 'worlds', 'test2.world'), ''],
            description='SDF world file'),

        DeclareLaunchArgument(
            'namespace',
            default_value='tb2_5',
            description='Top-level namespace'),

        DeclareLaunchArgument(
            'use_namespace',
            default_value='true',
            description='Whether to apply a namespace to the navigation stack'),
    ])

    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(spawn_tb2)

    return ld