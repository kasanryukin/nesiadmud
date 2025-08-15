#ifndef __PYWORLD_H
#define __PYWORLD_H
//*****************************************************************************
//
// pyworld.h
//
// A set of world-building and configuration functions for managing body types,
// races, and worn item types from Python. These are system-wide functions
// that affect the game world globally.
//
//*****************************************************************************

/* initialize world module for use */
PyMODINIT_FUNC
PyInit_PyWorld(void);

//
// Adds a new method function (i.e. void *f) to the world module. Name is the name
// of the function, f is the PyCFunction implementing the new method, flags is
// the type of method beings used (almost always METH_VARARGS), and doc is an
// (optional) description of what the method does.
void PyWorld_addMethod(const char *name, void *f, int flags, const char *doc);

#endif //__PYWORLD_H
