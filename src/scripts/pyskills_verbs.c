// ============================================================================
// pyskills_verbs.c
//
// Python wrapper for skills/verbs auxiliary data on objects.
// Provides Python access to skill assignment and custom verbs on gear items.
//
// ============================================================================

#include "../mud.h"
#include "../utils.h"
#include "../object.h"

#include "scripts.h"
#include "pyobj.h"
#include "pyskills_verbs.h"

// Forward declarations
extern PyTypeObject PyObj_Type;


//*****************************************************************************
// Skill assignment methods
//*****************************************************************************

/**
 * obj.assign_skill(skill_name, slot=0)
 * Assign a skill to one of the 5 skill slots
 */
PyObject *PyObj_assign_skill(PyObject *self, PyObject *args) {
  char *skill = NULL;
  int slot = 0;
  
  if (!PyArg_ParseTuple(args, "s|i", &skill, &slot)) {
    PyErr_Format(PyExc_TypeError, "assign_skill requires skill name and optional slot (0-4)");
    return NULL;
  }
  
  if (slot < 0 || slot > 4) {
    PyErr_Format(PyExc_ValueError, "Skill slot must be 0-4, got %d", slot);
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to assign skill to nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, 
      "Object does not have skills_verbs auxiliary data. Make sure skills_verbs_aux_init() was called at startup.");
    return NULL;
  }
  
  svaux_assign_skill(aux, slot, skill);
  Py_RETURN_TRUE;
}

/**
 * obj.get_skill(slot=None)
 * Get skill at specific slot, or get active skill if slot is None
 */
PyObject *PyObj_get_skill(PyObject *self, PyObject *args) {
  int slot = -1;
  
  if (!PyArg_ParseTuple(args, "|i", &slot)) {
    PyErr_Format(PyExc_TypeError, "get_skill takes optional slot number (0-4)");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get skill from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, 
      "Object does not have skills_verbs auxiliary data");
    return NULL;
  }
  
  // If no slot specified, return active skill
  if (slot == -1) {
    int active_slot = svaux_get_active_skill_slot(aux);
    const char *skill = svaux_get_skill(aux, active_slot);
    if (skill && *skill)
      return Py_BuildValue("s", skill);
    Py_RETURN_NONE;
  }
  
  // Specific slot requested
  if (slot < 0 || slot > 4) {
    PyErr_Format(PyExc_ValueError, "Skill slot must be 0-4, got %d", slot);
    return NULL;
  }
  
  const char *skill = svaux_get_skill(aux, slot);
  if (skill && *skill)
    return Py_BuildValue("s", skill);
  
  Py_RETURN_NONE;
}

/**
 * obj.get_active_skill_slot()
 * Get the index of the currently active skill (0-4)
 */
PyObject *PyObj_get_active_skill_slot(PyObject *self) {
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get active skill slot from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, "Object does not have skills_verbs auxiliary data");
    return NULL;
  }
  
  int slot = svaux_get_active_skill_slot(aux);
  return Py_BuildValue("i", slot);
}

/**
 * obj.set_active_skill_slot(slot)
 * Set which skill slot is currently active (0-4)
 */
PyObject *PyObj_set_active_skill_slot(PyObject *self, PyObject *args) {
  int slot = 0;
  
  if (!PyArg_ParseTuple(args, "i", &slot)) {
    PyErr_Format(PyExc_TypeError, "set_active_skill_slot requires slot number (0-4)");
    return NULL;
  }
  
  if (slot < 0 || slot > 4) {
    PyErr_Format(PyExc_ValueError, "Skill slot must be 0-4, got %d", slot);
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to set active skill slot on nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, "Object does not have skills_verbs auxiliary data");
    return NULL;
  }
  
  svaux_set_active_skill_slot(aux, slot);
  Py_RETURN_TRUE;
}

/**
 * obj.get_all_skills()
 * Get list of all assigned skills (including None for empty slots)
 */
PyObject *PyObj_get_all_skills(PyObject *self) {
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get all skills from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, "Object does not have skills_verbs auxiliary data");
    return NULL;
  }
  
  PyObject *list = PyList_New(5);
  for (int i = 0; i < 5; i++) {
    const char *skill = svaux_get_skill(aux, i);
    if (skill && *skill) {
      PyList_SetItem(list, i, Py_BuildValue("s", skill));
    } else {
      PyList_SetItem(list, i, Py_None);
      Py_INCREF(Py_None);
    }
  }
  
  return list;
}

/**
 * obj.clear_skill(slot)
 * Remove skill from a slot
 */
PyObject *PyObj_clear_skill(PyObject *self, PyObject *args) {
  int slot = 0;
  
  if (!PyArg_ParseTuple(args, "i", &slot)) {
    PyErr_Format(PyExc_TypeError, "clear_skill requires slot number (0-4)");
    return NULL;
  }
  
  if (slot < 0 || slot > 4) {
    PyErr_Format(PyExc_ValueError, "Skill slot must be 0-4, got %d", slot);
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to clear skill on nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, "Object does not have skills_verbs auxiliary data");
    return NULL;
  }
  
  svaux_assign_skill(aux, slot, "");
  Py_RETURN_TRUE;
}


//*****************************************************************************
// Verb handler methods
//*****************************************************************************

/**
 * obj.add_verb(verb, script, charges=-1, cooldown=0)
 * Add a custom verb (action) to an object
 * charges: -1 = unlimited, 0+ = number of uses
 * cooldown: seconds between uses
 */
PyObject *PyObj_add_verb(PyObject *self, PyObject *args) {
  char *verb = NULL;
  char *script = NULL;
  int charges = -1;
  int cooldown = 0;
  
  if (!PyArg_ParseTuple(args, "ss|ii", &verb, &script, &charges, &cooldown)) {
    PyErr_Format(PyExc_TypeError, 
      "add_verb requires verb name, script, and optional charges and cooldown");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to add verb to nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux == NULL) {
    PyErr_Format(PyExc_Exception, 
      "Object does not have skills_verbs auxiliary data. Make sure skills_verbs_aux_init() was called at startup.");
    return NULL;
  }
  
  svaux_add_verb(aux, verb, script, charges, cooldown);
  Py_RETURN_TRUE;
}

/**
 * obj.remove_verb(verb)
 * Remove a custom verb from an object
 */
PyObject *PyObj_remove_verb(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "remove_verb requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to remove verb from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    svaux_remove_verb(aux, verb);
    Py_RETURN_TRUE;
  }
  
  Py_RETURN_FALSE;
}

/**
 * obj.get_verb_script(verb)
 * Get the Python script for a custom verb
 */
PyObject *PyObj_get_verb_script(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "get_verb_script requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get verb script from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    const char *script = svaux_get_verb_script(aux, verb);
    if (script && *script)
      return Py_BuildValue("s", script);
  }
  
  Py_RETURN_NONE;
}

/**
 * obj.get_verb_charges(verb)
 * Get remaining charges for a verb (-1 = unlimited)
 */
PyObject *PyObj_get_verb_charges(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "get_verb_charges requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get verb charges from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    int charges = svaux_get_verb_charges(aux, verb);
    return Py_BuildValue("i", charges);
  }
  
  return Py_BuildValue("i", 0);
}

/**
 * obj.get_verb_cooldown(verb)
 * Get cooldown time in seconds for a verb
 */
PyObject *PyObj_get_verb_cooldown(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "get_verb_cooldown requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get verb cooldown from nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    int cooldown = svaux_get_verb_cooldown(aux, verb);
    return Py_BuildValue("i", cooldown);
  }
  
  return Py_BuildValue("i", 0);
}

/**
 * obj.get_verbs()
 * Get list of all verbs on object
 */
PyObject *PyObj_get_verbs(PyObject *self) {
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to get verbs from nonexistent object");
    return NULL;
  }
  
  PyObject *list = PyList_New(0);
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    LIST *verbs = svaux_get_verb_list(aux);
    LIST_ITERATOR *iter = newListIterator(verbs);
    const char *verb = NULL;
    
    ITERATE_LIST(verb, iter) {
      PyObject *pyverb = Py_BuildValue("s", verb);
      PyList_Append(list, pyverb);
      Py_DECREF(pyverb);
    }
    deleteListIterator(iter);
    deleteListWith(verbs, free);
  }
  
  return list;
}

/**
 * obj.verb_on_cooldown(verb)
 * Check if a verb is currently on cooldown
 */
PyObject *PyObj_verb_on_cooldown(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "verb_on_cooldown requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to check verb cooldown on nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    if (svaux_verb_on_cooldown(aux, verb, current_time)) {
      Py_RETURN_TRUE;
    }
  }
  
  Py_RETURN_FALSE;
}

/**
 * obj.use_verb(verb)
 * Attempt to use a verb (decrements charges, sets cooldown)
 * Returns True if successful, False if on cooldown or out of charges
 */
PyObject *PyObj_use_verb(PyObject *self, PyObject *args) {
  char *verb = NULL;
  
  if (!PyArg_ParseTuple(args, "s", &verb)) {
    PyErr_Format(PyExc_TypeError, "use_verb requires verb name");
    return NULL;
  }
  
  OBJ_DATA *obj = PyObj_AsObj(self);
  if (obj == NULL) {
    PyErr_Format(PyExc_Exception, "Tried to use verb on nonexistent object");
    return NULL;
  }
  
  SKILLS_VERBS_AUX *aux = objGetAuxiliaryData(obj, "skills_verbs");
  if (aux != NULL) {
    if (svaux_use_verb(aux, verb, current_time)) {
      Py_RETURN_TRUE;
    }
  }
  
  Py_RETURN_FALSE;
}


//*****************************************************************************
// Registration function
//*****************************************************************************

/**
 * Register all skills/verbs methods with PyObj
 * Call this from PyInit_PyObj or during module initialization
 */
void PySkillsVerbs_registerMethods(void) {
  // Skill assignment methods
  PyObj_addMethod("assign_skill", PyObj_assign_skill, METH_VARARGS,
    "assign_skill(skill_name, slot=0)\n\n"
    "Assign a skill to one of 5 skill slots (0-4). When this item's active skill\n"
    "is used, experience goes to this skill. Example:\n"
    "  obj.assign_skill('melee_combat', 0)\n"
    "  obj.assign_skill('parry', 1)\n"
    "  obj.assign_skill('dodge', 2)");
  
  PyObj_addMethod("get_skill", PyObj_get_skill, METH_VARARGS,
    "get_skill(slot=None)\n\n"
    "Get skill name at specific slot, or get the currently active skill if slot is None.\n"
    "Returns None if the slot is empty.\n"
    "Examples:\n"
    "  obj.get_skill(0)      # Get skill in slot 0\n"
    "  obj.get_skill()       # Get active skill");
  
  PyObj_addMethod("get_active_skill_slot", (PyCFunction)PyObj_get_active_skill_slot, METH_NOARGS,
    "get_active_skill_slot()\n\n"
    "Get the index (0-4) of the currently active skill slot.");
  
  PyObj_addMethod("set_active_skill_slot", PyObj_set_active_skill_slot, METH_VARARGS,
    "set_active_skill_slot(slot)\n\n"
    "Set which skill slot (0-4) is currently active. This determines which skill\n"
    "receives experience when this item is used.");
  
  PyObj_addMethod("get_all_skills", (PyCFunction)PyObj_get_all_skills, METH_NOARGS,
    "get_all_skills()\n\n"
    "Get a list of all 5 skill slots. Empty slots are None, assigned skills are strings.\n"
    "Returns list like: ['melee_combat', 'parry', None, None, None]");
  
  PyObj_addMethod("clear_skill", PyObj_clear_skill, METH_VARARGS,
    "clear_skill(slot)\n\n"
    "Remove the skill from a specific slot (0-4).");
  
  // Verb handler methods
  PyObj_addMethod("add_verb", PyObj_add_verb, METH_VARARGS,
    "add_verb(verb, script, charges=-1, cooldown=0)\n\n"
    "Add a custom verb (action) to this object. When wielded/equipped, the\n"
    "character can use this verb. Examples:\n"
    "  obj.add_verb('swing', code, charges=-1, cooldown=2)\n"
    "  obj.add_verb('stab', code, charges=5, cooldown=1)\n"
    "Args:\n"
    "  verb: Name of the action (lowercase)\n"
    "  script: Python code to execute when used\n"
    "  charges: Max uses (-1 for unlimited, >= 0 for limited)\n"
    "  cooldown: Seconds between uses");
  
  PyObj_addMethod("remove_verb", PyObj_remove_verb, METH_VARARGS,
    "remove_verb(verb)\n\n"
    "Remove a custom verb from this object.");
  
  PyObj_addMethod("get_verb_script", PyObj_get_verb_script, METH_VARARGS,
    "get_verb_script(verb)\n\n"
    "Get the Python script for a verb, or None if not found.");
  
  PyObj_addMethod("get_verb_charges", PyObj_get_verb_charges, METH_VARARGS,
    "get_verb_charges(verb)\n\n"
    "Get remaining charges for a verb (-1 = unlimited, 0+ = limited uses).");
  
  PyObj_addMethod("get_verb_cooldown", PyObj_get_verb_cooldown, METH_VARARGS,
    "get_verb_cooldown(verb)\n\n"
    "Get cooldown time in seconds for a verb.");
  
  PyObj_addMethod("get_verbs", (PyCFunction)PyObj_get_verbs, METH_NOARGS,
    "get_verbs()\n\n"
    "Get list of all custom verbs on this object.");
  
  PyObj_addMethod("verb_on_cooldown", PyObj_verb_on_cooldown, METH_VARARGS,
    "verb_on_cooldown(verb)\n\n"
    "Check if a verb is currently on cooldown. Returns True/False.");
  
  PyObj_addMethod("use_verb", PyObj_use_verb, METH_VARARGS,
    "use_verb(verb)\n\n"
    "Attempt to use a verb. Returns True if successful (verb executed),\n"
    "False if on cooldown or out of charges.");
}