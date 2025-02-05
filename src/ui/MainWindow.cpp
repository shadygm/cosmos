#include <ui/MainWindow.hpp>
#include <ui_mainwindow.h> // Ensure this file exists and is correctly generated

namespace UI {

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent), ui(new Ui::MainWindow) { // Correct type
    ui->setupUi(this);
}

MainWindow::~MainWindow() { delete ui; }

} // namespace UI
