#include <QDebug>

#include <ui/mainview.h>

/**
 * @brief MainView::keyPressEvent Triggered by pressing a key.
 * @param ev Key event.
 */
void MainView::keyPressEvent(QKeyEvent *ev) {
    switch (ev->key()) {
    case 'A':
        qDebug() << "A pressed";
        break;
    default:
        // ev->key() is an integer. For alpha numeric characters keys it
        // equivalent with the char value ('A' == 65, '1' == 49) Alternatively,
        // you could use Qt Key enums, see http://doc.qt.io/qt-6/qt.html#Key-enum
        qDebug() << ev->key() << "pressed";
        break;
    }

    // Used to update the screen after changes
    update();
}

/**
 * @brief MainView::keyReleaseEvent Triggered by releasing a key.
 * @param ev Key event.
 */
void MainView::keyReleaseEvent(QKeyEvent *ev) {
    switch (ev->key()) {
    case 'A':
        qDebug() << "A released";
        break;
    default:
        qDebug() << ev->key() << "released";
        break;
    }

    update();
}

/**
 * @brief MainView::mouseDoubleClickEvent Triggered by clicking two subsequent
 times on any mouse button. It also fires two mousePress and mouseRelease
 events!
 * @param ev Mouse event.
 */
void MainView::mouseDoubleClickEvent(QMouseEvent *ev) {
    qDebug() << "Mouse double clicked:" << ev->button();

    update();
}

// Triggered when moving the mouse inside the window (only when the mouse is
// clicked!)
void MainView::mouseMoveEvent(QMouseEvent *ev) {
    qDebug() << "x" << ev->position().x() << "y" << ev->position().y();

    update();
}

/**
 * @brief MainView::mousePressEvent Triggered when pressing any mouse button.
 * @param ev Mouse event.
 */
void MainView::mousePressEvent(QMouseEvent *ev) {
    qDebug() << "Mouse button pressed:" << ev->button();

    update();
    // Do not remove the line below, clicking must focus on this widget!
    this->setFocus();
}

/**
 * @brief MainView::mouseReleaseEvent Triggered when releasing any mouse button.
 * @param ev Mouse event.
 */
void MainView::mouseReleaseEvent(QMouseEvent *ev) {
    qDebug() << "Mouse button released" << ev->button();

    update();
}

/**
 * @brief MainView::wheelEvent Triggered when clicking scrolling with the scroll
 * wheel on the mouse.
 * @param ev Mouse event.
 */
void MainView::wheelEvent(QWheelEvent *ev) {
    // Implement something
    qDebug() << "Mouse wheel:" << ev->angleDelta();

    update();
}
