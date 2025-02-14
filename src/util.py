from loguru import logger
import sys
import OpenGL.GL.shaders as shaders 
import OpenGL.GL as gl
from gaussian_representation import *
import numpy as np
import glm

logger.remove()
logger.add(sys.stderr, level="INFO")


def get_logger():
    return logger

def load_shaders(vs, fs):
    vertex_shader = open(vs, 'r').read()        
    fragment_shader = open(fs, 'r').read()

    active_shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, gl.GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, gl.GL_FRAGMENT_SHADER),
    )
    return active_shader

def compile_shaders(vertex_shader, fragment_shader):
    active_shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, shaders.GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, shaders.GL_FRAGMENT_SHADER)
    )

    return active_shader

def set_attributes(program, keys, values, vao=None, buffer_ids=None):
        gl.glUseProgram(program)
        if vao is None:
            vao = gl.glGenVertexArrays(1)

        gl.glBindVertexArray(vao)

        if buffer_ids is None:
            buffer_ids = [None] * len(keys)
        for i, (key, value, b) in enumerate(zip(keys, values, buffer_ids)):
            if b is None:
                b = gl.glGenBuffers(1)
                buffer_ids[i] = b
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, b)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, value.nbytes, value.reshape(-1), gl.GL_STATIC_DRAW)

            length = value.shape[-1]
            pos = gl.glGetAttribLocation(program, key)
            gl.glVertexAttribPointer(pos, length, gl.GL_FLOAT, False, 0, None)
            gl.glEnableVertexAttribArray(pos)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return vao, buffer_ids

def set_faces_to_vao(vao, faces: np.ndarray):
    gl.glBindVertexArray(vao)
    element_buffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, element_buffer)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, gl.GL_STATIC_DRAW)
    return element_buffer

def set_storage_buffer_data(program, key, value: np.ndarray, bind_idx, vao=None, buffer_id=None):
    gl.glUseProgram(program)
    
    block_index = gl.glGetProgramResourceIndex(program, gl.GL_SHADER_STORAGE_BLOCK, key)
    gl.glShaderStorageBlockBinding(program, block_index, bind_idx)

    if vao is not None:
        gl.glBindVertexArray(vao)
    
    if buffer_id is None:
        buffer_id = gl.glGenBuffers(1)
    
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, buffer_id)
    data = np.ascontiguousarray(value)
    gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
    gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, bind_idx, buffer_id)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)
    return buffer_id

def set_uniform_lf(shader, content, name):
    gl.glUseProgram(shader)
    gl.glUniform1i(gl.glUniformLocation(shader ,name), content)

def set_uniform_1int(shader, content, name):
    gl.glUseProgram(shader)
    gl.glUniform1i(
        gl.glGetUniformLocation(shader, name), 
        content
    )

def set_uniform_mat4(shader, content, name):
    gl.glUseProgram(shader)
    if isinstance(content, glm.mat4):
        content = np.array(content).astype(np.float32)
    else:
        content = content.T
    gl.glUniformMatrix4fv(
        gl.glGetUniformLocation(shader, name),
        1,
        gl.GL_FALSE,
        content.astype(np.float32)
    )

def set_uniform_1f(shader, content, name):
    gl.glUseProgram(shader)
    gl.glUniform1f(
        gl.glGetUniformLocation(shader, name),
        content
    )


def set_uniform_v3(shader, contents, name):
    gl.glUseProgram(shader)
    gl.glUniform3f(
        gl.glGetUniformLocation(shader, name),
        contents[0], contents[1], contents[2]
    )

