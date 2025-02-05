#version 330 core

in vec3 interpolatedColor;
out vec4 color;
void main()
{
    color = vec4(interpolatedColor, 1.0);

}
