from setuptools import setup

package_name = 'isaac_pos_ctrl_neural'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/isaac_pos_ctrl_launch.py']),
        ('share/' + package_name + '/config', ['config/pos_ctrl_params.yaml']),
        ('share/' + package_name + '/models', ['models/isaac_pos_ctrl.onnx']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Isaac Developer',
    maintainer_email='isaac.developer@example.com',
    description='Isaac Position Control Neural Network Inference for PX4',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'isaac_pos_ctrl_node = isaac_pos_ctrl_neural.isaac_pos_ctrl_node:main',
            'set_target_pos = isaac_pos_ctrl_neural.set_target_pos:main',
        ],
    },
)