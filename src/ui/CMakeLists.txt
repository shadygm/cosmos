find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenGL REQUIRED)

add_library(ui_lib
  MainWindow.cpp
  mainview.cpp
  userinput.cpp
)

target_include_directories(ui_lib
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}    
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${EIGEN3_INCLUDE_DIRS}
)

target_link_libraries(ui_lib   Eigen3::Eigen
  OpenGL::GL
  Qt${QT_VERSION_MAJOR}::Widgets
  Qt${QT_VERSION_MAJOR}::OpenGL
  Qt${QT_VERSION_MAJOR}::OpenGLWidgets
)

qt_add_resources(RESOURCES resources.qrc)

ament_target_dependencies(ui_lib
    rclcpp
    sensor_msgs
    geometry_msgs
    visualization_msgs
)

install(TARGETS ui_lib
    DESTINATION lib
)
