# PX4 ROS 2 Interface Library
## TODOs
1. 将px4_msgs的独立出来，作为该代码的submodules引用
2. 研究官网提供的CI/CD的流程，规范化 lint/formatter的工具与规范
3. 应当去除workflow/doxygen 的调用
4. python的linter/formatter 要使用ruff的工具（as in drone_racer, 你可以不使用pyproject.toml)
5. 标记好所索引的px4-gazebo中px4的版本/commit hash.



## Development
For development, install the pre-commit scripts:
```shell
pre-commit install
```

### CI
CI runs a number of checks which can be executed locally with the following commands.
Make sure you have the ROS workspace sourced.

#### clang-tidy
```shell
./scripts/run-clang-tidy-on-project.sh
```

#### Unit tests (目前需要忽略这一部分)
You can either run the unit tests through colcon:
```shell
colcon test --packages-select px4_ros2_cpp --ctest-args -R unit_tests
colcon test-result --verbose
```
Or directly from the build directory, which allows to filter by individual tests:
```shell
./build/px4_ros2_cpp/px4_ros2_cpp_unit_tests --gtest_filter='xy*'
```

#### Linters (code formatting etc)
These run automatically when committing code. To manually run them, use:
```shell
pre-commit run -a
```
