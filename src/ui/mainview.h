#ifndef MAINVIEW_H
#define MAINVIEW_H

#include <QKeyEvent>
#include <QMouseEvent>
#include <QOpenGLDebugLogger>
#include <QOpenGLFunctions_3_3_Core>
#include <QOpenGLShaderProgram>
#include <QOpenGLWidget>

/**
 * @brief The MainView class is resonsible for the actual content of the main
 * window. It inherits from QOpenGLWidget and QOpenGLFunctions_3_3_Core.
 */
class MainView : public QOpenGLWidget, protected QOpenGLFunctions_3_3_Core {
    Q_OBJECT

  public:
    MainView(QWidget *parent = nullptr);
    ~MainView() override;

  protected:
    void initializeGL() override;
    void resizeGL(int newWidth, int newHeight) override;
    void paintGL() override;

    // Functions for keyboard input events
    void keyPressEvent(QKeyEvent *ev) override;
    void keyReleaseEvent(QKeyEvent *ev) override;

    // Function for mouse input events
    void mouseDoubleClickEvent(QMouseEvent *ev) override;
    void mouseMoveEvent(QMouseEvent *ev) override;
    void mousePressEvent(QMouseEvent *ev) override;
    void mouseReleaseEvent(QMouseEvent *ev) override;
    void wheelEvent(QWheelEvent *ev) override;

  private:
    QOpenGLDebugLogger debugLogger;
    QOpenGLShaderProgram shaderProgram;
    GLuint vbo, vao;

  private slots:
    void onMessageLogged(QOpenGLDebugMessage Message);
};

#endif // MAINVIEW_H
