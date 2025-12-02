set shell := ["bash", "-c"]

example:
    source ./install/setup.sh && \
    ros2 run example_mode_manual_cpp example_mode_manual

neural-demo:
    source ./install/setup.sh && \
    ros2 launch neural_demo neural_demo.launch.py

fake-network:
    source ./install/setup.sh && \
    ros2 launch neural_demo fake_network_node.launch.py


