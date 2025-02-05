#define MODULE_NAME "COSMOS"
#include <QApplication>
#include <QSurfaceFormat>
#include <rclcpp/rclcpp.hpp>
#include <thread>
#include <ui/MainWindow.hpp>

void initRos() {
    while (!rclcpp::ok()) {
        RCLCPP_INFO(rclcpp::get_logger(MODULE_NAME), "Waiting for ROS to start...");
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    RCLCPP_INFO(rclcpp::get_logger(MODULE_NAME), "ROS started!");
}

void initQt() {
    // Request OpenGL 3.3 core profile
    QSurfaceFormat glFormat;
    glFormat.setProfile(QSurfaceFormat::CoreProfile);
    glFormat.setVersion(3, 3);
    QSurfaceFormat::setDefaultFormat(glFormat);
    glFormat.setDepthBufferSize(24);

    QSurfaceFormat::setDefaultFormat(glFormat);
}

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    QApplication a(argc, argv);

    initRos();
    initQt();
    UI::MainWindow w;
    w.show();

    rclcpp::shutdown();
    return a.exec();
}