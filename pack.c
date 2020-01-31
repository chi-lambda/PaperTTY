#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "pack_map.h"

void pack_image_bw(PyObject *frame_buffer, char* packed_buffer);
void pack_image(PyObject *frame_buffer, char* packed_buffer);

void pack_image_bw(PyObject *frame_buffer, char* packed_buffer) {
    Py_ssize_t size = PySequence_Length(frame_buffer);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *pixels = PySequence_ITEM(frame_buffer, i);
        unsigned char *entry = pack_map[PyLong_AsLong(pixels)];
        packed_buffer[i * 4] = entry[0];
        packed_buffer[i * 4 + 1] = entry[1];
        packed_buffer[i * 4 + 2] = entry[2];
        packed_buffer[i * 4 + 3] = entry[3];
        Py_DECREF(pixels);
    }
}
void pack_image(PyObject *frame_buffer, char* packed_buffer) {
    Py_ssize_t size = PySequence_Length(frame_buffer);
    for (Py_ssize_t i = 0; i < size; i += 4) {
        PyObject *pixel0 = PySequence_ITEM(frame_buffer, i);
        PyObject *pixel1 = PySequence_ITEM(frame_buffer, i + 1);
        PyObject *pixel2 = PySequence_ITEM(frame_buffer, i + 2);
        PyObject *pixel3 = PySequence_ITEM(frame_buffer, i + 3);
        packed_buffer[i / 2] = (PyLong_AsLong(pixel2) >> 4) | (PyLong_AsLong(pixel3) & 0xF0);
        packed_buffer[i / 2 + 1] = (PyLong_AsLong(pixel0) >> 4) | (PyLong_AsLong(pixel1) & 0xF0);
        Py_DECREF(pixel0);
        Py_DECREF(pixel1);
        Py_DECREF(pixel2);
        Py_DECREF(pixel3);
    }
}

