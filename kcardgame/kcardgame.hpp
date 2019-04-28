/* Header to test of C modules for arrays for Python: C_test.c */

/* ==== Prototypes =================================== */

// .... Python callable Vector functions ..................
static PyObject *np_kcardgame(PyObject *self, PyObject *args);

/* .... C vector utility functions ..................*/
PyArrayObject *pyvector(PyObject *objin);
int  not_doublevector(PyArrayObject *vec);
