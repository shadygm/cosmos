#include <QFile>
#include <ui/mainview.h>
#include <ui/vertex.hpp>
/**
 * @brief MainView::MainView Mainview constructor. The ": QOpenGLWidget(parent)"
 * notation means calling the super class constructor of QOpenGLWidget with the
 * parameter "parent".
 * @param parent Parent widget.
 */
MainView::MainView(QWidget *parent) : QOpenGLWidget(parent) { qDebug() << "MainView constructor"; }

/**
 * @brief MainView::~MainView Destructor. Can be used to free memory.
 */
MainView::~MainView() {
    qDebug() << "MainView destructor";

    glDeleteBuffers(1, &vbo);
    glDeleteVertexArrays(1, &vao);

    makeCurrent();
}

/**
 * @brief MainView::initializeGL Initialize the necessary OpenGL context.
 */
void MainView::initializeGL() {
    qDebug() << ":: Initializing OpenGL";
    initializeOpenGLFunctions();

    connect(&debugLogger, SIGNAL(messageLogged(QOpenGLDebugMessage)), this, SLOT(onMessageLogged(QOpenGLDebugMessage)),
            Qt::DirectConnection);

    if (debugLogger.initialize()) {
        qDebug() << ":: Logging initialized";
        debugLogger.startLogging(QOpenGLDebugLogger::SynchronousLogging);
    }

    QString glVersion{reinterpret_cast<const char *>(glGetString(GL_VERSION))};
    qDebug() << ":: Using OpenGL" << qPrintable(glVersion);

    // Create 3 vertices
    Vertex v0 = {0.0f, 1.0f, 1.0f, 0.0f, 0.0f};
    Vertex v1 = {-1.0f, -1.0f, 0.0f, 1.0f, 0.0f};
    Vertex v2 = {1.0f, -1.0f, 0.0f, 0.0f, 1.0f};

    std::vector<Vertex> vertices;
    vertices.push_back(v0);
    vertices.push_back(v1);
    vertices.push_back(v2);

    glGenBuffers(1, &vbo);
    glGenVertexArrays(1, &vao);

    // Add shader using QOpenGLShaderProgram

    qDebug() << "Checking shader file existence:";
    qDebug() << "Vertex shader exists:" << QFile::exists(":/shaders/vertshader.glsl");
    qDebug() << "Fragment shader exists:" << QFile::exists(":/shaders/fragshader.glsl");

    shaderProgram.addShaderFromSourceFile(QOpenGLShader::Vertex, ":/shaders/vertshader.glsl");
    shaderProgram.addShaderFromSourceFile(QOpenGLShader::Fragment, ":/shaders/fragshader.glsl");

    // Link shader pipeline
    shaderProgram.link();

    // Bind buffers
    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);

    // Add data to buffer
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Vertex), vertices.data(), GL_STATIC_DRAW);

    // Set up vertex attributes
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), reinterpret_cast<void *>(offsetof(Vertex, x)));

    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), reinterpret_cast<void *>(offsetof(Vertex, r)));
}

/**
 * @brief MainView::resizeGL Called when the window is resized.
 * @param newWidth The new width of the window.
 * @param newHeight The new height of the window.
 */
void MainView::resizeGL(int newWidth, int newHeight) {
    Q_UNUSED(newWidth)
    Q_UNUSED(newHeight)
}

/**
 * @brief MainView::paintGL Draw function. TODO.
 */
void MainView::paintGL() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    // make background blue
    glClearColor(0.0f, 0.0f, 1.0f, 1.0f);
    // Bind and Draw
    shaderProgram.bind();
    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLES, 0, 3);
}

/**
 * @brief MainView::onMessageLogged Debug utility method.
 * @param Message The message to be logged.
 */
void MainView::onMessageLogged(QOpenGLDebugMessage Message) { qDebug() << " → Log:" << Message; }
