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
   license: LGPL
*/


#include <Python.h>


static PyObject *is_proxy(PyObject *self, PyObject *args) {
  /* PyObject *proxy = NULL; */
  
  /* if (! PyArg_ParseTuple(args, "O!", &Proxy_Type, &proxy)) { */
  /*   Py_RETURN_FALSE; */

  /* } else { */
  /*   Py_RETURN_TRUE; */
  /* } */

  Py_RETURN_FALSE;
}


static PyObject *is_proxy_delivered(PyObject *self, PyObject *args) {
  /* PyObject *proxy = NULL; */
  
  /* if (! PyArg_ParseTuple(args, "O!", &Proxy_Type, &proxy)) */
  /*   return NULL; */

  Py_RETURN_FALSE;
}


static PyObject *deliver_proxy(PyObject *self, PyObject *args) {
  /* PyObject *proxy = NULL; */
  
  /* if (! PyArg_ParseTuple(args, "O!", &Proxy_Type, &proxy)) */
  /*   return NULL; */

  Py_RETURN_NONE;
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
  //PyObject *proxytype;

  mod = Py_InitModule("promises._proxy", methods);

  //proxytype = (PyObject *) &Proxy_Type;
  //Py_INCREF(proxytype);
  //PyModule_AddObject(mod, "ProxyType", proxytype);
}


/* The end. */
