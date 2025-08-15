//*****************************************************************************
//
// pyworld.c
//
// A set of world-building and configuration functions for managing body types,
// races, and worn item types from Python. These are system-wide functions
// that affect the game world globally.
//
//*****************************************************************************
#include <Python.h>
#include <structmember.h>

#include "../mud.h"
#include "../utils.h"
#include "../character.h"
#include "../body.h"
#include "../races.h"
#include "../handler.h"
#include "../storage.h"
#include "../world.h"

#include "pyworld.h"
#include "scripts.h"
#include "pyplugs.h"

//******************************************************************************
// mandatory modules
//******************************************************************************
#include "../items/worn.h"

//*****************************************************************************
// local variables and functions
//*****************************************************************************

// a list of methods to add to the world module
LIST *pyworld_methods = NULL;

//*****************************************************************************
// Body System Functions
//*****************************************************************************

PyObject *pyworld_add_bodysize(PyObject *self, PyObject *args) {
  char *size_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &size_name)) {
    PyErr_Format(PyExc_TypeError, "add_bodysize requires size name");
    return NULL;
  }
  
  bool success = body_add_size(size_name);
  if(!success) {
    PyErr_Format(PyExc_ValueError, "Body size '%s' already exists", size_name);
    return NULL;
  }
  
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_remove_bodysize(PyObject *self, PyObject *args) {
  char *size_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &size_name)) {
    PyErr_Format(PyExc_TypeError, "remove_bodysize requires size name");
    return NULL;
  }
  
  bool success = body_remove_size(size_name);
  if(!success) {
    PyErr_Format(PyExc_ValueError, "Body size '%s' not found in custom sizes", size_name);
    return NULL;
  }
  
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_get_bodysizes(PyObject *self, PyObject *args) {
  LIST *all_sizes = body_get_all_sizes();
  PyObject *list = PyList_New(0);
  LIST_ITERATOR *size_i = newListIterator(all_sizes);
  char *size = NULL;
  
  ITERATE_LIST(size, size_i) {
    PyObject *size_name = Py_BuildValue("s", size);
    PyList_Append(list, size_name);
    Py_DECREF(size_name);
  } deleteListIterator(size_i);
  
  deleteListWith(all_sizes, free);
  return list;
}

PyObject *pyworld_add_bodypos_type(PyObject *self, PyObject *args) {
  char *pos_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &pos_name)) {
    PyErr_Format(PyExc_TypeError, "add_bodypos_type requires position type name");
    return NULL;
  }
  
  bool success = body_add_position_type(pos_name);
  if(!success) {
    PyErr_Format(PyExc_ValueError, "Body position type '%s' already exists", pos_name);
    return NULL;
  }
  
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_remove_bodypos_type(PyObject *self, PyObject *args) {
  char *pos_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &pos_name)) {
    PyErr_Format(PyExc_TypeError, "remove_bodypos_type requires position type name");
    return NULL;
  }
  
  bool success = body_remove_position_type(pos_name);
  if(!success) {
    PyErr_Format(PyExc_ValueError, "Body position type '%s' not found in custom types", pos_name);
    return NULL;
  }
  
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_get_bodypos_types(PyObject *self, PyObject *args) {
  LIST *all_types = body_get_all_position_types();
  PyObject *list = PyList_New(0);
  LIST_ITERATOR *type_i = newListIterator(all_types);
  char *type = NULL;
  
  ITERATE_LIST(type, type_i) {
    PyObject *type_name = Py_BuildValue("s", type);
    PyList_Append(list, type_name);
    Py_DECREF(type_name);
  } deleteListIterator(type_i);
  
  deleteListWith(all_types, free);
  return list;
}

//*****************************************************************************
// Race System Functions
//*****************************************************************************

PyObject *pyworld_add_race(PyObject *self, PyObject *args) {
  char *name = NULL;
  char *abbrev = NULL;
  PyObject *body_template = NULL;
  int pc_ok = 0;
  
  if(!PyArg_ParseTuple(args, "ssOi", &name, &abbrev, &body_template, &pc_ok)) {
    PyErr_Format(PyExc_TypeError, 
                 "add_race requires name, abbrev, body_template, and pc_ok flag");
    return NULL;
  }
  
  // For now, we'll create a basic human-like body template
  // TODO: Parse body_template parameter to create custom body
  BODY_DATA *body = raceCreateBody("human");
  if(body == NULL) {
    PyErr_Format(PyExc_RuntimeError, "Failed to create body template");
    return NULL;
  }
  
  add_race(name, abbrev, body, pc_ok);
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_remove_race(PyObject *self, PyObject *args) {
  char *race_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &race_name)) {
    PyErr_Format(PyExc_TypeError, "remove_race requires race name");
    return NULL;
  }
  
  bool success = remove_race(race_name);
  if(!success) {
    PyErr_Format(PyExc_ValueError, "Race '%s' not found", race_name);
    return NULL;
  }
  
  return Py_BuildValue("i", 1);
}

PyObject *pyworld_get_races(PyObject *self, PyObject *args) {
  const char *race_list = raceGetList(FALSE); // Get all races, not just PC races
  if(race_list == NULL) {
    return PyList_New(0);
  }
  
  // Parse comma-separated race list into Python list
  PyObject *list = PyList_New(0);
  char *races_copy = strdup(race_list);
  char *race = strtok(races_copy, ", ");
  
  while(race != NULL) {
    PyObject *race_name = Py_BuildValue("s", race);
    PyList_Append(list, race_name);
    Py_DECREF(race_name);
    race = strtok(NULL, ", ");
  }
  
  free(races_copy);
  return list;
}

PyObject *pyworld_get_race_info(PyObject *self, PyObject *args) {
  char *race_name = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &race_name)) {
    PyErr_Format(PyExc_TypeError, "get_race_info requires race name");
    return NULL;
  }
  
  if(!isRace(race_name)) {
    PyErr_Format(PyExc_ValueError, "Race '%s' does not exist", race_name);
    return NULL;
  }
  
  PyObject *info = PyDict_New();
  PyDict_SetItemString(info, "name", Py_BuildValue("s", race_name));
  PyDict_SetItemString(info, "abbrev", Py_BuildValue("s", raceGetAbbrev(race_name)));
  PyDict_SetItemString(info, "pc_ok", Py_BuildValue("i", raceIsForPC(race_name)));
  
  return info;
}

//*****************************************************************************
// Worn System Functions
//*****************************************************************************

PyObject *pyworld_get_worn_types(PyObject *self, PyObject *args) {
  LIST *types = worn_get_all_types();
  PyObject *list = PyList_New(0);
  LIST_ITERATOR *type_i = newListIterator(types);
  char *type = NULL;
  
  ITERATE_LIST(type, type_i) {
    PyObject *type_name = Py_BuildValue("s", type);
    PyList_Append(list, type_name);
    Py_DECREF(type_name);
  } deleteListIterator(type_i);
  
  deleteList(types);
  return list;
}

PyObject *pyworld_get_worn_type_positions(PyObject *self, PyObject *args) {
  char *type = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &type)) {
    PyErr_Format(PyExc_TypeError, "get_worn_type_positions requires worn type name");
    return NULL;
  }
  
  if(!worn_type_exists(type)) {
    PyErr_Format(PyExc_ValueError, "Worn type '%s' does not exist", type);
    return NULL;
  }
  
  const char *positions = wornTypeGetPositions(type);
  return Py_BuildValue("s", positions);
}

PyObject *pyworld_remove_worn_type(PyObject *self, PyObject *args) {
  char *type = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &type)) {
    PyErr_Format(PyExc_TypeError, "remove_worn_type requires worn type name");
    return NULL;
  }
  
  bool success = worn_remove_type(type);
  return Py_BuildValue("i", success);
}

PyObject *pyworld_worn_type_exists(PyObject *self, PyObject *args) {
  char *type = NULL;
  
  if(!PyArg_ParseTuple(args, "s", &type)) {
    PyErr_Format(PyExc_TypeError, "worn_type_exists requires worn type name");
    return NULL;
  }
  
  bool exists = worn_type_exists(type);
  return Py_BuildValue("i", exists);
}

PyObject *pyworld_get_worn_type_count(PyObject *self, PyObject *args) {
  int count = worn_get_type_count();
  return Py_BuildValue("i", count);
}

//*****************************************************************************
// Module setup and initialization
//*****************************************************************************

void PyWorld_addMethod(const char *name, void *f, int flags, const char *doc) {
  // add the method to our list of methods
  PyMethodDef *method = calloc(1, sizeof(PyMethodDef));
  method->ml_name  = strdup(name);
  method->ml_meth  = (PyCFunction)f;
  method->ml_flags = flags;
  method->ml_doc   = (doc ? strdup(doc) : NULL);
  listPut(pyworld_methods, method);
}

static PyModuleDef world_moduledef = {
  PyModuleDef_HEAD_INIT,
  "world",                    // module name
  "World building and configuration functions for NakedMud", // module documentation
  -1,                         // size of per-interpreter state
  NULL                        // methods table (set dynamically)
};

PyMODINIT_FUNC PyInit_PyWorld(void) {
  // initialize our list of methods
  if(pyworld_methods == NULL)
    pyworld_methods = newList();

  // Body system methods
  PyWorld_addMethod("add_bodysize", pyworld_add_bodysize, METH_VARARGS,
    "add_bodysize(name)\n\n"
    "Register a new body size. Adds to custom list alongside hardcoded sizes.");
  PyWorld_addMethod("remove_bodysize", pyworld_remove_bodysize, METH_VARARGS,
    "remove_bodysize(name)\n\n"
    "Remove a body size from the custom list. Cannot remove hardcoded sizes.");
  PyWorld_addMethod("get_bodysizes", pyworld_get_bodysizes, METH_NOARGS,
    "get_bodysizes()\n\n"
    "Return a list of all available body sizes (hardcoded + custom).");
  PyWorld_addMethod("add_bodypos_type", pyworld_add_bodypos_type, METH_VARARGS,
    "add_bodypos_type(name)\n\n"
    "Register a new body position type. Adds to custom list alongside hardcoded types.");
  PyWorld_addMethod("remove_bodypos_type", pyworld_remove_bodypos_type, METH_VARARGS,
    "remove_bodypos_type(name)\n\n"
    "Remove a body position type from the custom list. Cannot remove hardcoded types.");
  PyWorld_addMethod("get_bodypos_types", pyworld_get_bodypos_types, METH_NOARGS,
    "get_bodypos_types()\n\n"
    "Return a list of all available body position types (hardcoded + custom).");

  // Race system methods
  PyWorld_addMethod("add_race", pyworld_add_race, METH_VARARGS,
    "add_race(name, abbrev, body_template, pc_ok)\n\n"
    "Register a new race with the given name, abbreviation, body template, and PC flag.");
  PyWorld_addMethod("remove_race", pyworld_remove_race, METH_VARARGS,
    "remove_race(name)\n\n"
    "Remove a race from the system.");
  PyWorld_addMethod("get_races", pyworld_get_races, METH_NOARGS,
    "get_races()\n\n"
    "Return a list of all available races.");
  PyWorld_addMethod("get_race_info", pyworld_get_race_info, METH_VARARGS,
    "get_race_info(name)\n\n"
    "Return a dictionary with information about the specified race.");

  // Worn system methods
  PyWorld_addMethod("get_worn_types", pyworld_get_worn_types, METH_NOARGS,
    "get_worn_types()\n\n"
    "Return a list of all available worn types.");
  PyWorld_addMethod("get_worn_type_positions", pyworld_get_worn_type_positions, METH_VARARGS,
    "get_worn_type_positions(type)\n\n"
    "Return the required positions for a worn type.");
  PyWorld_addMethod("remove_worn_type", pyworld_remove_worn_type, METH_VARARGS,
    "remove_worn_type(type)\n\n"
    "Remove a worn type from the system.");
  PyWorld_addMethod("worn_type_exists", pyworld_worn_type_exists, METH_VARARGS,
    "worn_type_exists(type)\n\n"
    "Check if a worn type exists.");
  PyWorld_addMethod("get_worn_type_count", pyworld_get_worn_type_count, METH_NOARGS,
    "get_worn_type_count()\n\n"
    "Return the total number of worn types.");

  world_moduledef.m_methods = makePyMethods(pyworld_methods);

  PyObject *module = PyModule_Create(&world_moduledef);
  if (module == NULL)
    return NULL;

  return module;
}
