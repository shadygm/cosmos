#ifndef COSMOS_CAMERA_HPP
#define COSMOS_CAMERA_HPP
#include <eigen3/Eigen/Core>
namespace UI {

class Camera {
  public:
    Camera();

  private:
    Eigen::Vector3f position;
}

} // namespace UI

#endif // COSMOS_CAMERA_HPP
