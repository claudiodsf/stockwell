/*
 * sinemodule.c
 *
 * Downloaded from http://kurage.nimh.nih.gov/meglab/Meg/Stockwell
 */

/* Riedel & Sidorenko sine tapers. */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <Python.h>
#include <numpy/arrayobject.h>

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
"sine_taper(k, N) returns the kth sine taper of length N.";

static PyObject *sine_taper_wrap(PyObject *self, PyObject *args)
{
    int k, N;
    int dim[1];
    PyArrayObject *r;

    if (!PyArg_ParseTuple(args, "ii", &k, &N)) {
        return NULL;
    }

    dim[0] = N;
    r = (PyArrayObject *)PyArray_FromDims(1, dim, PyArray_DOUBLE);
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

void initsine()
{
    Py_InitModule("sine", Methods);
    import_array();
}
