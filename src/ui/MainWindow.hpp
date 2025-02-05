#ifndef COSMOS_MAIN_WINDOW_HPP
#define COSMOS_MAIN_WINDOW_HPP

#include <QMainWindow>

namespace Ui { // Namespace for the auto-generated UI class
class MainWindow;
}

namespace UI {

class MainWindow : public QMainWindow {
    Q_OBJECT

  public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

  private:
    Ui::MainWindow *ui; // Corrected type
};

} // namespace UI

#endif // COSMOS_MAIN_WINDOW_HPP
