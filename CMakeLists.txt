cmake_minimum_required(VERSION 3.16)

project(cosmos)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# Compiler options for GNU and Clang
if(CMAKE_COMPILER_IS_GNUCXX)
  add_compile_options(-Wall -Wextra -Wpedantic -O3)
endif()

# Find ROS 2 packages
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

# Find other required packages
find_package(Eigen3 REQUIRED)
find_package(OpenGL REQUIRED)

# Find Qt packages (tries Qt6 first, then Qt5)
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} COMPONENTS Widgets OpenGL OpenGLWidgets REQUIRED)

# Setup Qt automatically
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)



# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${EIGEN3_INCLUDE_DIRS}
)
    
# Add subdirectories (if you have additional dependencies)
add_subdirectory(dependencies)
add_subdirectory(src/ui)

qt_add_executable(cosmos
    src/main.cpp
    src/ui/resources.qrc
)

# Link necessary libraries
target_link_libraries(cosmos PUBLIC
    ui_lib 
    Eigen3::Eigen
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::OpenGL
    Qt${QT_VERSION_MAJOR}::OpenGLWidgets
)
    
    
# Link ROS 2 dependencies
set(AMENT_TARGET_DEPENDENCIES_USE_KEYWORDS ON)
# ament_target_dependencies(cosmos
# )


# Installation
install(TARGETS cosmos
    DESTINATION lib/${PROJECT_NAME}
)

ament_package()
