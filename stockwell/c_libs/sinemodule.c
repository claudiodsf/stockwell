/*
 * sinemodule.c
 *
 * Original version downloaded from
 * http://kurage.nimh.nih.gov/meglab/Meg/Stockwell
 *
 * The contents of this file is free and unencumbered software released
 * into the public domain. For more information, please refer to
 * https://unlicense.org
 *
 * Modified for Python3 compatibility
 */

/* Riedel & Sidorenko sine tapers. */

// the following two defines are for Windows
#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <Python.h>
#include <numpy/ndarrayobject.h>

/* Compute the kth sine taper. d is an array of length N. */

static void sine_taper(int k, int N, double *d)
{
    int i;
    double s;

    s = sqrt(2. / (N + 1));
    for (i = 0; i < N; i++) {
        d[i] = s * sin(M_PI * (k + 1) * (i + 1) / (N + 1));
    }
}

static char Doc_sine_taper[] =
"sine_taper(k, N)\n--\n\n\
Returns the kth sine taper of length N.";

static PyObject *sine_taper_wrap(PyObject *self, PyObject *args)
{
    int k, N;
    npy_intp dim[1];
    PyArrayObject *r;

    if (!PyArg_ParseTuple(args, "ii", &k, &N)) {
        return NULL;
    }

    dim[0] = N;
    r = (PyArrayObject *)PyArray_SimpleNew(1, dim, NPY_DOUBLE);
    if (r == NULL) {
        return NULL;
    }

    sine_taper(k, N, (double *)r->data);

    return PyArray_Return(r);
}

static PyMethodDef Methods[] = {
    { "sine_taper", sine_taper_wrap, METH_VARARGS, Doc_sine_taper },
    { NULL, NULL, 0, NULL }
};

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

#if PY_MAJOR_VERSION >= 3

static int sine_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int sine_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "sine",
        NULL,
        sizeof(struct module_state),
        Methods,
        NULL,
        sine_traverse,
        sine_clear,
        NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_sine(void)

#else
#define INITERROR return

void initsine()
#endif
{
#if PY_MAJOR_VERSION >= 3
	PyObject *module = PyModule_Create(&moduledef);
#else
	Py_InitModule("sine", Methods);
#endif
	import_array();

#if PY_MAJOR_VERSION >= 3
	return module;
#endif
}
