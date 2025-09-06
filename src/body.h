#ifndef __BODY_H
#define __BODY_H
//*****************************************************************************
//
// body.h
//
// Different creatures are shaped in fundamentally different ways (e.g.
// bipedal humans and quadrapedal bears). Here's our attempt to create a
// structure that captures this idea.
//
//*****************************************************************************



// Body position constants removed - now using dynamic string-based system

#define BODYSIZE_NONE            -1
#define BODYSIZE_DIMINUITIVE      0
#define BODYSIZE_TINY             1
#define BODYSIZE_SMALL            2
#define BODYSIZE_MEDIUM           3
#define BODYSIZE_LARGE            4
#define BODYSIZE_HUGE             5
#define BODYSIZE_GARGANTUAN       6
#define BODYSIZE_COLLOSAL         7
#define NUM_BODYSIZES             8

/**
 * Return a list of the postypes for a list of posnames (comma-separated)
 */
char *list_postypes(const BODY_DATA *B, const char *posnames);


/**
 * Get the type of position the bodypart is. Return NULL if
 * no such bodypart exists on the body
 */
const char *bodyGetPart(const BODY_DATA *B, const char *pos);


/**
 * return the name of the specified bodysize
 */
const char *bodysizeGetName(int size);


/**
 * return the number assocciated with the bodysize
 */
int bodysizeGetNum(const char *size);


/**
 * Create a new body
 */
BODY_DATA *newBody();


/**
 * Delete a body. Do not delete any pieces of equipment
 * equipped on it.
 */
void deleteBody(BODY_DATA *B);


/**
 * Copy the body (minus equipment)
 */
BODY_DATA *bodyCopy(const BODY_DATA *B);


/**
 * Return the size of the body
 */
int bodyGetSize(const BODY_DATA *B);

/**
 * change the body's size
 */
void bodySetSize(BODY_DATA *B, int size);

/**
 * Add a position to a body. If the position already exists, it will be
 * modified to have the new type and size. Otherwise, a new position will
 * be created.
 */
void bodyAddPosition(BODY_DATA *B, const char *pos, const char *type, int size);

/**
 * Add a position to a body using string type name instead of integer.
 * If the position already exists, it will be modified to have the new type and size.
 * Otherwise, a new position will be created.
 */
void bodyAddPositionByName(BODY_DATA *B, const char *pos, const char *type_name, int size);

/**
 * Remove a position from the body. Return true if the
 * position is removed, and false if it does not exist.
 */
bool bodyRemovePosition(BODY_DATA *B, const char *pos);


// Removed duplicate bodyGetPart declaration - using string-based version above


/**
 * Return the name of a random bodypart, based on the bodypart's size,
 * relative to the other bodyparts. If pos is NULL, all bodyparts are weighted
 * in. If part is not null, it is assumed to be a list that we want to draw from
 */
const char *bodyRandPart(const BODY_DATA *B, const char *pos);


/**
 * Return the ratio of the bodypart(s)'s size the the body's total size.
 * If the part(s) does not exist then, 0 is returned.
 */
double bodyPartRatio(const BODY_DATA *B, const char *pos);


/**
 * get a list of all the bodyparts on the body. If sort is true,
 * order them from top (floating, head, etc) to bottom (legs and feet)
 */
const char **bodyGetParts(const BODY_DATA *B, bool sort, int *num_pos);


/**
 * Equip the object to the first available, valid body positions. If
 * none exist, return false. Otherwise, return true.
 */
bool bodyEquipPostypes(BODY_DATA *B, OBJ_DATA *obj, const char *types);


/**
 * Equip the object to the list of positions on the body. If one or more
 * of the posnames doesn't exist, or already is equipped, return false.
 */
bool bodyEquipPosnames(BODY_DATA *B, OBJ_DATA *obj, const char *positions);

/**
 * Extended version of bodyEquipPosnames with type filtering and force override.
 * equipment_type: only conflicts with equipment of this type (NULL = all types)
 * force: if true, ignores all existing equipment and forces equipping
 */
bool bodyEquipPosnamesEx(BODY_DATA *B, OBJ_DATA *obj, const char *positions, 
                         const char *equipment_type, bool force);

/**
 * Returns a list of places the piece of equipment is equipped on
 * the person's body
 */
const char *bodyEquippedWhere(BODY_DATA *B, OBJ_DATA *obj);


/**
 * Return a list of objects that are equipped at the given bodypart.
 * If nothing is equipped, or the bodypart does not exist, return null.
 */
LIST *bodyGetEquipment(BODY_DATA *B, const char *pos);


/**
 * Remove the object from all of the bodyparts it is equipped at. Return
 * true if successful, and false if the object is not equipped anywhere
 * on the body.
 */
bool bodyUnequip(BODY_DATA *B, const OBJ_DATA *obj);


/**
 * Unequip everything on the body, and return a list of all the
 * objects that were unequipped.
 */
LIST *bodyUnequipAll(BODY_DATA *B);


/**
 * returns a list of all equipment worn on the body. The list must
 * be deleted after use.
 */
LIST *bodyGetAllEq(BODY_DATA *B);


/**
 * Return how many positions are on the body
 */
int numBodyparts(const BODY_DATA *B);

// Dynamic body size and position type management
void init_body_dynamic();
bool body_add_size(const char *size_name);
bool body_remove_size(const char *size_name);
bool body_add_position_type(const char *pos_name);
bool body_remove_position_type(const char *pos_name);
LIST *body_get_all_sizes();
LIST *body_get_all_position_types();

#endif // __BODY_H
