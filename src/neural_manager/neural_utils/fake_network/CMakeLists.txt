cmake_minimum_required(VERSION 3.8)
project(fake_network)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies using ament_cmake_auto
find_package(ament_cmake_auto REQUIRED)
find_package(yaml-cpp REQUIRED)

# Auto-discover dependencies
ament_auto_find_build_dependencies()

# Add executable with auto-discovered dependencies
ament_auto_add_executable(fake_network_node src/fake_network_node.cpp)

# Link yaml-cpp library
target_link_libraries(fake_network_node yaml-cpp)

# Set include directories
target_include_directories(fake_network_node PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Install targets
install(TARGETS
  fake_network_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}/
)

# Use ament_auto_package to automatically handle dependencies
ament_auto_package()