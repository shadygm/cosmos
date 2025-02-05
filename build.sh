#!/bin/bash
set -e

if [ -f .env ]; then
    source .env
fi

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUILD_PATH="$SCRIPT_PATH/build/desktop"
NUM_JOBS="$(nproc)"
SHOULD_CLEAN="false"
SHOULD_BUILD="false"
SHOULD_RUN="false"
PACKAGE_NAME="cosmos"

printHelp()
{
   echo "ROS 2 Build Script"
   echo
   echo "Usage: ./build.sh [args ...]"
   echo "Examples:"
   echo "       ./build.sh -b "
   echo "       ./build.sh --clean"
   echo
   echo "Options:"
   echo "-h or --help"
   echo "        This help menu."
   echo
   echo "-b or --build "
   echo "        Build the specified ROS 2 package using colcon."
   echo
   echo "-r or --run"
   echo "        Run the specified ROS 2 package."
   echo
   echo "-c or --clean"
   echo "        Clean build. Remove build/ folder."
   exit
}

build() {
    echo "---------- Building ROS 2 Package: $PACKAGE_NAME ----------"
    if [[ "$SHOULD_CLEAN" == "true" ]]; then
        echo "Cleaning build, install, and log directories..."
        rm -rf build/ install/ log/
    fi

    if [[ "$SHOULD_BUILD" == "true" ]]; then
        echo "Building package: $PACKAGE_NAME with $NUM_JOBS parallel jobs"
        colcon build --parallel-workers "$NUM_JOBS" --cmake-args -DCMAKE_UNITY_BUILD=ON -DCMAKE_VERBOSE_MAKEFILE=OFF --event-handlers console_direct+
    fi

    if [[ "$SHOULD_RUN" == "true" ]]; then
        echo "Running package: $PACKAGE_NAME"
        source install/setup.bash
        ros2 run $PACKAGE_NAME $PACKAGE_NAME
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      printHelp
      ;;
    -b|--build)
      SHOULD_BUILD="true"
      shift
      ;;

    -c|--clean)
      SHOULD_CLEAN="true"
      shift
      ;;
    -r|--run)
      SHOULD_RUN="true"
      shift
      ;;
    -*|--*)
      echo "Unknown option: $1"
      printHelp
      exit 1
      ;;
  esac
done
# Only proceed to build if a build is requested
if [[ "$SHOULD_BUILD" == "true" || "$SHOULD_CLEAN" == "true" || "$SHOULD_RUN" == "true" ]]; then
    build
else
    help
fi
