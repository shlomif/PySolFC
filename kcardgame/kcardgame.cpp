/* A file to test imorting C modules for handling arrays to Python */

#include "Python.h"
#include "arrayobject.h"
#include "kcardgame.hpp"
#include <QPixmap>
#include "QtGui/pyside2_qtgui_python.h"
#include <math.h>

/* #### Globals #################################### */

/* ==== Set up the methods table ====================== */
static struct PyMethodDef _kcardgameMethods[] = {
	{"np_kcardgame", np_kcardgame, METH_VARARGS, "kcardgame"},
	{NULL, NULL, 0, NULL}     /* Sentinel - marks the end of this structure */
};

static struct PyModuleDef _kcardgame_mod = {
            PyModuleDef_HEAD_INIT,
            "_kcardgame",
            NULL,
            -1,
            _kcardgameMethods
        };


/* ==== Initialize the C_test functions ====================== */
// Module name must be _kcardgame in compile and linked
PyMODINIT_FUNC
PyInit_kcardgame()  {
	PyObject* ret = PyModule_Create(&_kcardgame_mod);
	import_array();  // Must be present for NumPy.  Called first after above line.
    return ret;
}

/* ==== Create 1D Carray from PyArray ======================
    Assumes PyArray is contiguous in memory.             */
static inline uint64_t *pyvector_to_Carrayptrs(PyArrayObject *arrayin)  {
	return (uint64_t *) arrayin->data;  /* pointer to arrayin data as double */
}

int my_kcardgame(
	const uint64_t *const cin,
    const size_t n)
{
    unsigned __int128 sum = 0;
	/* Operate on the vectors  */
	for ( size_t i=0; i<n; i++)  {
			sum += cin[i];
	}
    return (int)(sum % 1000000007);
}

#include "KCardDeck"
#include "KCardTheme"
static void del_kcardgame(PyObject * obj)
{
    delete (KCardDeck *)PyCapsule_GetPointer(obj, "KCardDeck");
}
static PyObject *np_kcardgame(PyObject *self, PyObject *args)
{
    auto ret = new KCardDeck( KCardTheme(), nullptr);
	return PyCapsule_New(ret, "KCardDeck", del_kcardgame);
}
static PyObject *get_card_pixmap(PyObject *self, PyObject *args)
{
    PyObject * kcard;
    int i;
    if (! PyArg_ParseTuple(args, "Oi", &kcard, &i))
    {
        return NULL;
    }
    auto deck = (KCardDeck *)PyCapsule_GetPointer(kcard, "KCardDeck");
    auto ret = new QPixmap(deck->cardPixmap(i, true));
    return PyType_GenericNew(Shiboken::SbkType<QPixmap>, ret, NULL);
}

/* ==== Square vector components & multiply by a float =========================
/* #### Vector Utility functions ######################### */

/* ==== Make a Python Array Obj. from a PyObject, ================
     generates a double vector w/ contiguous memory which may be a new allocation if
     the original was not a double type or contiguous
  !! Must DECREF the object returned from this routine unless it is returned to the
     caller of this routines caller using return PyArray_Return(obj) or
     PyArray_BuildValue with the "N" construct   !!!
*/
PyArrayObject *pyvector(PyObject *objin)  {
	return (PyArrayObject *) PyArray_ContiguousFromObject(objin,
		NPY_DOUBLE, 1,1);
}
/* ==== Check that PyArrayObject is a double (Float) type and a vector ==============
    return 1 if an error and raise exception */
int  not_doublevector(PyArrayObject *vec)  {
	if (vec->descr->type_num != NPY_UINT64 || vec->nd != 1)  {
		PyErr_SetString(PyExc_ValueError,
			"In not_doublevector: array must be of type uint644 and 1 dimensional (n).");
		return 1;  }
	return 0;
}

/* #### Matrix Extensions ############################## */

