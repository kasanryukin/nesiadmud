//*****************************************************************************
//
// pymud_movement.c
//
// Python wrapper for mob movement functions. Provides access to autonomous
// NPC wandering logic from Python trigger code.
//
//*****************************************************************************

#include "../mud.h"
#include "../utils.h"
#include "../character.h"
#include "../room.h"
#include "../exit.h"
#include "../world.h"
#include "../handler.h"
#include "scripts.h"
#include "pychar.h"
#include "pyroom.h"
#include "pyexit.h"


//*****************************************************************************
// Configuration
//*****************************************************************************

#define WANDER_CHANCE 40
#define NUM_NO_WANDER_PROTOS 3
static const char *NO_WANDER_PROTOTYPES[] = {
  "statue",
  "immobile", 
  "shopkeeper"
};


//*****************************************************************************
// Helper Functions (C implementations)
//*****************************************************************************

/**
 * Extract zone name from a room's prototype key (format: name@zone)
 * Returns dynamically allocated string that must be freed, or NULL
 */
const char *get_mob_zone(CHAR_DATA *mob) {
  if(!mob || !charGetRoom(mob))
    return NULL;
  
  const char *room_proto = roomGetClass(charGetRoom(mob));
  if(!room_proto || !*room_proto || !strchr(room_proto, '@'))
    return NULL;
  
  // Extract zone part after @
  const char *at_pos = strchr(room_proto, '@');
  return strdupsafe(at_pos + 1);
}


/**
 * Get the destination zone of an exit
 * Returns dynamically allocated string that must be freed, or NULL
 */
const char *get_exit_destination_zone(EXIT_DATA *exit_obj, ROOM_DATA *room) {
  if(!exit_obj || !room)
    return NULL;
  
  const char *dest_full = exitGetToFull(exit_obj);
  if(!dest_full || !*dest_full)
    return NULL;
  
  const char *at_sign = strchr(dest_full, '@');
  if(at_sign)
    return strdupsafe(at_sign + 1);
  
  const char *room_proto = roomGetClass(room);
  if(room_proto) {
    at_sign = strchr(room_proto, '@');
    if(at_sign)
      return strdupsafe(at_sign + 1);
  }
  
  return NULL;
}


/**
 * Check if mob has a no-wander prototype
 */
bool has_no_wander_prototype(CHAR_DATA *mob) {
  int i;
  for(i = 0; i < NUM_NO_WANDER_PROTOS; i++) {
    if(charIsInstance(mob, NO_WANDER_PROTOTYPES[i]))
      return TRUE;
  }
  return FALSE;
}


/**
 * Determine if mob should attempt to wander this heartbeat
 */
bool should_mob_wander(CHAR_DATA *mob) {
  if(!mob)
    return FALSE;
  
  log_string("DEBUG: Should mob wander?");
  
  // Chance check
  if(rand_number(1, 100) > WANDER_CHANCE)
    return FALSE;
  
  // Don't wander if player character
  if(!charIsNPC(mob))
    return FALSE;
  
  // Don't wander if has no-wander prototype
  if(has_no_wander_prototype(mob))
    return FALSE;
  
  // Don't wander if not in a room
  if(!charGetRoom(mob))
    return FALSE;
  
  return TRUE;
}


/**
 * Get all valid exits that keep mob in its home zone
 * Returns a LIST of exit direction names that must be deleted
 */
LIST *get_valid_exits(CHAR_DATA *mob) {
  LIST *valid = newList();
  
  if(!mob || !charGetRoom(mob))
    return valid;
  
  log_string("DEBUG: Get valid exits");
  
  const char *home_zone = get_mob_zone(mob);
  if(!home_zone || !*home_zone) {
    if(home_zone) free((char *)home_zone);
    return valid;
  }
  
  // Get all exit names from room
  LIST *exit_names = roomGetExitNames(charGetRoom(mob));
  LIST_ITERATOR *ex_i = newListIterator(exit_names);
  char *exit_dir = NULL;
  
  ITERATE_LIST(exit_dir, ex_i) {
    EXIT_DATA *exit_obj = roomGetExit(charGetRoom(mob), exit_dir);
    if(exit_obj) {
      const char *dest_zone = get_exit_destination_zone(exit_obj, charGetRoom(mob));
      if(dest_zone && !strcasecmp(dest_zone, home_zone)) {
        listPut(valid, strdupsafe(exit_dir));
      }
      if(dest_zone) free((char *)dest_zone);
    }
  }
  deleteListIterator(ex_i);
  deleteListWith(exit_names, free);
  
  if(home_zone) free((char *)home_zone);
  return valid;
}


//*****************************************************************************
// Python Interface Functions
//*****************************************************************************

/**
 * attempt_wander(mob)
 * Main function called from heartbeat trigger
 */
static PyObject *PyMud_attempt_wander(PyObject *self, PyObject *args) {
  PyObject *pymob = NULL;
  
  if(!PyArg_ParseTuple(args, "O", &pymob)) {
    PyErr_SetString(PyExc_TypeError, "attempt_wander requires a mob object");
    return NULL;
  }
  
  // Convert Python object to C character
  CHAR_DATA *mob = PyChar_AsChar(pymob);
  if(!mob) {
    PyErr_SetString(PyExc_TypeError, "Invalid mob object");
    return NULL;
  }
  
  log_string("DEBUG: attempt_wander called on mob");
  
  // Check if should wander
  if(!should_mob_wander(mob))
    Py_RETURN_FALSE;
  
  // Get valid exits
  LIST *valid_exits = get_valid_exits(mob);
  log_string("List size: %d", listSize(valid_exits));
  
  if(listSize(valid_exits) == 0) {
    deleteListWith(valid_exits, free);
    Py_RETURN_FALSE;
  }
  
  // Pick random exit
  int random_idx = rand_number(0, listSize(valid_exits) - 1);
  log_string("Random index: %d", random_idx);
  
  char *chosen_exit_dir = listGet(valid_exits, random_idx);
  log_string("Chosen exit dir length: %d", strlen(chosen_exit_dir));
  log_string("Chosen exit dir hex: %02x %02x %02x %02x", chosen_exit_dir[0], chosen_exit_dir[1], chosen_exit_dir[2], chosen_exit_dir[3]);
  log_string("Chosen exit dir: %s", chosen_exit_dir ? chosen_exit_dir : "NULL");

  // Get exit object and destination room
  EXIT_DATA *exit_obj = roomGetExit(charGetRoom(mob), chosen_exit_dir);
  log_string("exit_obj pointer: %p", exit_obj);
  EXIT_DATA *test_exit = roomGetExit(charGetRoom(mob), "northwest");
  log_string("Direct northwest exit: %p vs gotten exit: %p", test_exit, exit_obj);
  if(!exit_obj) {
	log_string("DEBUG: exit_obj is NULL!");
    deleteListWith(valid_exits, free);
    Py_RETURN_FALSE;
  }
  
  log_string("exit_obj->to: %s", exitGetTo(exit_obj) ? exitGetTo(exit_obj) : "NULL");
  log_string("exit_obj->room: %p", exitGetRoom(exit_obj));
  
  // Get full destination key
  const char *full_dest = exitGetToFull(exit_obj);
  log_string("exitGetToFull destination: %s", full_dest ? full_dest : "NULL");
  log_string("gameworld pointer: %p", gameworld);
  
  if(!full_dest || strlen(full_dest) == 0) {
    log_string("full_dest is empty or NULL");
    deleteListWith(valid_exits, free);
    Py_RETURN_FALSE;
  }
  
  if(!gameworld) {
    log_string("gameworld is NULL!");
    deleteListWith(valid_exits, free);
    Py_RETURN_FALSE;
  }
  
  log_string("About to call worldGetRoom with %s", full_dest);
//  ROOM_DATA *dest_room = worldGetRoom(gameworld, full_dest);
  const char *room_name = exitGetTo(exit_obj);  // Just "hallway4"
  ROOM_DATA *dest_room = worldGetRoom(gameworld, room_name);
  log_string("Room-only lookup result: %p", dest_room);
  log_string("Back from worldGetRoom: %p", dest_room);
  
  if((dest_room = worldGetRoom(gameworld, full_dest)) == NULL) {
  log_string("worldGetRoom returned NULL");
  deleteListWith(valid_exits, free);
  Py_RETURN_FALSE;
  }
  
  log_string("Found destination room: %p", dest_room);
  
  // Move the mob
  char_to_room(mob, dest_room);
  log_string("Mob moved successfully");
  
  // Cleanup
  deleteListWith(valid_exits, free);
  
  Py_RETURN_TRUE;
}


//*****************************************************************************
// Module Definition
//*****************************************************************************

static PyMethodDef mud_movement_methods[] = {
  {"attempt_wander", PyMud_attempt_wander, METH_VARARGS,
   "attempt_wander(mob)\n\n"
   "Attempt to move a mob to a random valid exit within its home zone.\n"
   "Returns True if movement successful, False otherwise.\n"
   "Called from heartbeat trigger: attempt_wander(me)"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mud_movement_module = {
  PyModuleDef_HEAD_INIT,
  "mud_movement",
  "NPC autonomous movement system for zone-bounded wandering.",
  -1,
  mud_movement_methods
};

PyMODINIT_FUNC PyInit_mud_movement(void) {
  return PyModule_Create(&mud_movement_module);
}