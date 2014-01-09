/*
 This library is free software; you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as
 published by the Free Software Foundation; either version 3 of the
 License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License along with this library; if not, see
 <http://www.gnu.org/licenses/>.
*/


/**
   Here we have a transparent (as much as is possible, anyway) proxy
   type. A lot of this is "borrowed" from CPython's own weakref proxy.

   author: Christopher O'Brien  <obriencj@gmail.com>
   license: LGPL v.3
*/


#include <Python.h>


typedef struct _PyProxyPromise {
  PyObject_HEAD

  PyObject *work;
  PyObject *answer;

} PyProxyPromise;


PyTypeObject PyProxyPromiseType;


#define PyProxyPromise_Check(obj) \
  (Py_TYPE(obj) == &PyProxyPromiseType)


PyObject *PyProxyPromise_IsDelivered(PyProxyPromise *proxy);
PyObject *PyProxyPromise_Deliver(PyProxyPromise *proxy);

static PyObject *proxy_promise_deliver(PyProxyPromise *proxy);


#define DELIVERX(proxy, fail)						\
  {									\
    if (proxy && PyProxyPromise_Check(proxy)) {				\
      proxy = proxy_promise_deliver((PyProxyPromise *) proxy);		\
      if (! proxy) {							\
	return (fail);							\
      }									\
    }									\
  }


#define DELIVER(proxy) DELIVERX(proxy, NULL)


#define VALUE(o)						\
  (PyProxyPromise_Check(o)? ((PyProxyPromise *)(o))->answer: (o))


#define WRAP_UNARY(name, actual)	   \
  static PyObject *name(PyObject *proxy) { \
    DELIVER(proxy);			   \
    return actual(proxy);		   \
  }


#define WRAP_BINARY(name, actual)			\
  static PyObject *name(PyObject *proxy, PyObject *a) { \
    DELIVER(proxy);					\
    DELIVER(a);						\
    return actual(proxy, a);				\
  }


#define WRAP_TERNARY(name, actual)				     \
  static PyObject *name(PyObject *proxy, PyObject *a, PyObject *b) { \
    DELIVER(proxy);						     \
    DELIVER(a);							     \
    DELIVER(b);							     \
    return actual(proxy, a, b);					     \
  }


static PyObject *proxy_unicode(PyObject *proxy) {
  DELIVER(proxy);
  return PyObject_CallMethod(VALUE(proxy), "__unicode__", "");
}


static PyMethodDef proxy_methods[] = {
  {"__unicode__", (PyCFunction)proxy_unicode, METH_NOARGS},
  {NULL, NULL}
};


WRAP_BINARY(proxy_add, PyNumber_Add)
WRAP_BINARY(proxy_sub, PyNumber_Subtract)
WRAP_BINARY(proxy_mul, PyNumber_Multiply)
WRAP_BINARY(proxy_div, PyNumber_Divide)
WRAP_BINARY(proxy_mod, PyNumber_Remainder)
WRAP_BINARY(proxy_divmod, PyNumber_Divmod)
WRAP_TERNARY(proxy_pow, PyNumber_Power)
WRAP_UNARY(proxy_neg, PyNumber_Negative)
WRAP_UNARY(proxy_pos, PyNumber_Positive)
WRAP_UNARY(proxy_abs, PyNumber_Absolute)
WRAP_UNARY(proxy_invert, PyNumber_Invert)
WRAP_BINARY(proxy_lshift, PyNumber_Lshift)
WRAP_BINARY(proxy_rshift, PyNumber_Rshift)
WRAP_BINARY(proxy_and, PyNumber_And)
WRAP_BINARY(proxy_xor, PyNumber_Xor)
WRAP_BINARY(proxy_or, PyNumber_Or)
WRAP_UNARY(proxy_int, PyNumber_Int)
WRAP_UNARY(proxy_long, PyNumber_Long)
WRAP_UNARY(proxy_float, PyNumber_Float)
WRAP_BINARY(proxy_iadd, PyNumber_InPlaceAdd)
WRAP_BINARY(proxy_isub, PyNumber_InPlaceSubtract)
WRAP_BINARY(proxy_imul, PyNumber_InPlaceMultiply)
WRAP_BINARY(proxy_idiv, PyNumber_InPlaceDivide)
WRAP_BINARY(proxy_imod, PyNumber_InPlaceRemainder)
WRAP_TERNARY(proxy_ipow, PyNumber_InPlacePower)
WRAP_BINARY(proxy_ilshift, PyNumber_InPlaceLshift)
WRAP_BINARY(proxy_irshift, PyNumber_InPlaceRshift)
WRAP_BINARY(proxy_iand, PyNumber_InPlaceAnd)
WRAP_BINARY(proxy_ixor, PyNumber_InPlaceXor)
WRAP_BINARY(proxy_ior, PyNumber_InPlaceOr)
WRAP_BINARY(proxy_floor_div, PyNumber_FloorDivide)
WRAP_BINARY(proxy_true_div, PyNumber_TrueDivide)
WRAP_BINARY(proxy_ifloor_div, PyNumber_InPlaceFloorDivide)
WRAP_BINARY(proxy_itrue_div, PyNumber_InPlaceTrueDivide)
WRAP_UNARY(proxy_index, PyNumber_Index)


static int proxy_nonzero(PyObject *proxy) {
  DELIVERX(proxy, -1);
  return PyObject_IsTrue(proxy);
}


static PyNumberMethods proxy_as_number = {
  .nb_add = proxy_add,
  .nb_subtract = proxy_sub,
  .nb_multiply = proxy_mul,
  .nb_divide = proxy_div,
  .nb_remainder = proxy_mod,
  .nb_divmod = proxy_divmod,
  .nb_power = proxy_pow,
  .nb_negative = proxy_neg,
  .nb_positive = proxy_pos,
  .nb_absolute = proxy_abs,
  .nb_nonzero = proxy_nonzero,
  .nb_invert = proxy_invert,
  .nb_lshift = proxy_lshift,
  .nb_rshift = proxy_rshift,
  .nb_and = proxy_and,
  .nb_xor = proxy_xor,
  .nb_or = proxy_or,
  .nb_coerce = NULL,
  .nb_int = proxy_int,
  .nb_long = proxy_long,
  .nb_float = proxy_float,
  .nb_oct = NULL,
  .nb_hex = NULL,
  .nb_inplace_add = proxy_iadd,
  .nb_inplace_subtract = proxy_isub,
  .nb_inplace_multiply = proxy_imul,
  .nb_inplace_divide = proxy_idiv,
  .nb_inplace_remainder = proxy_imod,
  .nb_inplace_power = proxy_ipow,
  .nb_inplace_lshift = proxy_ilshift,
  .nb_inplace_rshift = proxy_irshift,
  .nb_inplace_and = proxy_iand,
  .nb_inplace_xor = proxy_ixor,
  .nb_inplace_or = proxy_ior,
  .nb_floor_divide = proxy_floor_div,
  .nb_true_divide = proxy_true_div,
  .nb_inplace_floor_divide = proxy_ifloor_div,
  .nb_inplace_true_divide = proxy_itrue_div,
  .nb_index = proxy_index,
};


static Py_ssize_t proxy_length(PyObject *proxy) {
  DELIVERX(proxy, -1);
  return PyObject_Length(proxy);
}


static PyObject *proxy_get_slice(PyObject *proxy,
				 Py_ssize_t i, Py_ssize_t j) {
  DELIVER(proxy);
  return PySequence_GetSlice(proxy, i, j);
}


static int proxy_set_slice(PyObject *proxy,
			   Py_ssize_t i, Py_ssize_t j,
			   PyObject *val) {
  DELIVERX(proxy, -1);
  return PySequence_SetSlice(proxy, i, j, val);
}


static int proxy_contains(PyObject *proxy, PyObject *val) {
  DELIVERX(proxy, -1);
  return PySequence_Contains(proxy, val);
}


static PySequenceMethods proxy_as_sequence = {
  .sq_length = (lenfunc)proxy_length,
  .sq_concat = NULL,
  .sq_repeat = NULL,
  .sq_item = NULL,
  .sq_slice = (ssizessizeargfunc)proxy_get_slice,
  .sq_ass_item = NULL,
  .sq_ass_slice = (ssizessizeobjargproc)proxy_set_slice,
  .sq_contains = (objobjproc)proxy_contains,
};


WRAP_BINARY(proxy_getitem, PyObject_GetItem)


static int proxy_setitem(PyObject *proxy, PyObject *key, PyObject *val) {
  DELIVERX(proxy, -1);
  DELIVERX(key, -1);
  if (val == NULL) {
    return PyObject_DelItem(proxy, key);
  } else {
    return PyObject_SetItem(proxy, key, val);
  }
}


static PyMappingMethods proxy_as_mapping = {
  .mp_length = (lenfunc)proxy_length,
  .mp_subscript = proxy_getitem,
  .mp_ass_subscript = (objobjargproc)proxy_setitem,
};


static PyObject *proxy_richcompare(PyObject *proxy, PyObject *comp, int op) {
  DELIVER(proxy);
  DELIVER(comp);
  return PyObject_RichCompare(proxy, comp, op);
}


WRAP_UNARY(proxy_iter, PyObject_GetIter)
WRAP_UNARY(proxy_iternext, PyIter_Next)


static int promise_clear(PyProxyPromise *proxy) {
  if (proxy->work) {
    Py_DECREF(proxy->work);
    proxy->work = NULL;
  }
  if (proxy->answer) {
    Py_DECREF(proxy->answer);
    proxy->answer = NULL;
  }
  return 0;
}


static long proxy_hash(PyObject *proxy) {
  DELIVERX(proxy, -1);
  return PyObject_Hash(proxy);
}


static int proxy_compare(PyObject *proxy, PyObject *val) {
  DELIVERX(proxy, -1);
  DELIVERX(val, -1);
  return PyObject_Compare(proxy, val);
}


WRAP_UNARY(proxy_repr, PyObject_Repr)
WRAP_UNARY(proxy_str, PyObject_Str)
WRAP_BINARY(proxy_getattr, PyObject_GetAttr)


static PyObject *proxy_call(PyObject *proxy,
			    PyObject *args, PyObject *kwds) {
  DELIVER(proxy);
  return PyObject_Call(proxy, args, kwds);
}


static int proxy_setattr(PyObject *proxy,
			 PyObject *name, PyObject *val) {
  DELIVERX(proxy, -1);
  return PyObject_SetAttr(proxy, name, val);
}


static void promise_dealloc(PyProxyPromise *self) {
  promise_clear(self);
  Py_TYPE(self)->tp_free((PyObject*)self);
}


static PyObject *promise_new(PyTypeObject *type,
			     PyObject *args, PyObject *kwds) {

  PyProxyPromise *self;

  self = (PyProxyPromise *) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->work = NULL;
    self->answer = NULL;
  }

  return (PyObject *) self;
}


static int promise_init(PyProxyPromise *self,
			PyObject *args, PyObject *kwds) {

  PyObject *work = NULL;

  if (! PyArg_ParseTuple(args, "O", &work))
    return -1;

  promise_clear(self);

  if (PyCallable_Check(work)) {
    self->work = work;
    Py_INCREF(work);

  } else {
    self->answer = work;
    Py_INCREF(work);
  }

  return 0;
}


PyTypeObject PyProxyPromiseType = {
  PyVarObject_HEAD_INIT(&PyType_Type, 0)

  "promises.ProxyPromise",
  sizeof(PyProxyPromise),
  0,

  .tp_dealloc = (destructor)promise_dealloc,
  .tp_print = NULL,
  .tp_getattr = NULL,
  .tp_setattr = NULL,
  .tp_compare = proxy_compare,
  .tp_repr = (reprfunc)proxy_repr,
  .tp_as_number = &proxy_as_number,
  .tp_as_sequence = &proxy_as_sequence,
  .tp_as_mapping = &proxy_as_mapping,
  .tp_hash = proxy_hash,
  .tp_call = proxy_call,
  .tp_str = proxy_str,
  .tp_getattro = proxy_getattr,
  .tp_setattro = (setattrofunc)proxy_setattr,
  .tp_as_buffer = NULL,
  .tp_flags = (Py_TPFLAGS_DEFAULT |
	       Py_TPFLAGS_CHECKTYPES),
  .tp_doc = NULL,
  .tp_traverse = NULL,
  .tp_clear = (inquiry)promise_clear,
  .tp_richcompare = proxy_richcompare,
  .tp_weaklistoffset = 0,
  .tp_iter = (getiterfunc)proxy_iter,
  .tp_iternext = (iternextfunc)proxy_iternext,
  .tp_methods = proxy_methods,

  .tp_new = promise_new,
  .tp_init = (initproc)promise_init,
};


#define proxy_promise_is_delivered(proxy) \
  ((proxy)->work == NULL)


static PyObject *proxy_promise_deliver(PyProxyPromise *proxy) {
  PyObject *work;
  PyObject *answer = NULL;

  if(proxy_promise_is_delivered(proxy)) {
    answer = proxy->answer;

  } else {
    work = proxy->work;

    if (PyCallable_Check(work)) {
      answer = PyObject_CallObject(work, NULL);

      if (answer != NULL) {
	proxy->work = NULL;
	Py_DECREF(work);
      }
    } else{
      answer = work;
    }

    proxy->answer = answer;
  }

  return answer;
}


PyObject *PyProxyPromise_IsDelivered(PyProxyPromise *proxy) {
  if (proxy_promise_is_delivered(proxy)) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}


PyObject *PyProxyPromise_Deliver(PyProxyPromise *proxy) {
  PyObject *answer;

  answer = proxy_promise_deliver(proxy);
  if (answer) {
    Py_INCREF(answer);
  }
  return answer;
}


static PyObject *is_proxy(PyObject *module, PyObject *args) {
  PyObject *obj = NULL;

  if (! PyArg_ParseTuple(args, "O", &obj))
    return NULL;

  if (PyProxyPromise_Check(obj)) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}


static PyObject *is_proxy_delivered(PyObject *module, PyObject *args) {
  PyProxyPromise *proxy = NULL;

  if (! PyArg_ParseTuple(args, "O!", &PyProxyPromiseType, &proxy))
    return NULL;

  return PyProxyPromise_IsDelivered(proxy);
}


static PyObject *deliver_proxy(PyObject *module, PyObject *args) {
  PyProxyPromise *proxy = NULL;

  if (! PyArg_ParseTuple(args, "O!", &PyProxyPromiseType, &proxy))
    return NULL;

  return PyProxyPromise_Deliver(proxy);
}


static PyMethodDef methods[] = {

  { "is_proxy", is_proxy, METH_VARARGS,
    "True if an object is a proxy promise" },

  { "is_proxy_delivered", is_proxy_delivered, METH_VARARGS,
    "True if the proxy has delivered on its promise" },

  { "deliver_proxy", deliver_proxy, METH_VARARGS,
    "Deliver on a proxy promise if it isn't delivered already" },

  { NULL, NULL, 0, NULL },
};


PyMODINIT_FUNC init_proxy() {
  PyObject *mod;
  PyObject *proxytype;

  proxytype = (PyObject *) &PyProxyPromiseType;

  if (PyType_Ready(&PyProxyPromiseType) < 0)
    return;

  mod = Py_InitModule("promises._proxy", methods);

  Py_INCREF(proxytype);
  PyModule_AddObject(mod, "ProxyPromise", proxytype);
}


/* The end. */
