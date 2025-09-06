//*****************************************************************************
//
// body.c
//
// Different creatures are shaped in fundamentally different ways (e.g.
// bipedal humans and quadrapedal bears). Here's our attempt to create a
// structure that captures this idea.
//
//*****************************************************************************
#include "mud.h"
#include "utils.h"
#include "body.h"
#include "items/items.h"


struct bodypart_data {
  char          *name;       // the name of the position
  char          *type;       // what kind of position type is this?
  int            size;       // how big is it, relative to other positions?
  LIST     *equipment;       // list of objects being worn here (for layering)
};

typedef struct bodypart_data   BODYPART;

struct body_data {
  LIST   *parts;             // a list of all the parts on the body
  int      size;             // how big is our body?
};


//*****************************************************************************
//
// Local functions. Mosty concerned with the handling of bodypart_datas, as
// opposed to their container, the body.
//
//*****************************************************************************

// Dynamic lists for body sizes and position types
LIST *bodypos_list = NULL;
LIST *bodysize_list = NULL;

// Removed duplicate body_get_all_position_types - using the one below

static const char *default_bodysize[NUM_BODYSIZES] = {
  "diminuitive",
  "tiny",
  "small",
  "medium",
  "large",
  "huge",
  "gargantuan",
  "collosal"
};

static const char *default_bodypos[] = {
  "floating about head", "about body", "head", "face", "ear", "neck", 
  "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", 
  "waist", "leg", "left foot", "right foot", "hoof", "claw", 
  "tail", "held", "hands", "legs", "feet", "wings", "hooves"
};


/**
 * Create a new bodypart_data
 */
BODYPART *newBodypart(const char *name, const char *type, int size) {
  BODYPART *P = malloc(sizeof(BODYPART));
  P->equipment = newList();
  P->type = strdupsafe(type);
  P->size = MAX(0, size); // parts of size 0 cannot be hit
  P->name = strdup((name ? name : "nothing"));
  return P;
};


/**
 * Delete a bodypart_data, but do not delete the equipment on it
 */
void deleteBodypart(BODYPART *P) {
  if(P->name) free(P->name);
  if(P->type) free(P->type);
  if(P->equipment) deleteList(P->equipment);
  free(P);
};

/**
 * Copy a bodypart
 */
BODYPART *bodypartCopy(BODYPART *P) {
  BODYPART *p_new = malloc(sizeof(BODYPART));
  p_new->equipment = newList();
  p_new->type      = strdupsafe(P->type);
  p_new->size      = P->size;
  p_new->name      = strdup(P->name);
  return p_new;
}



//*****************************************************************************
//
// Functions for body interface. Documentation contained in body.h
//
//*****************************************************************************

char *list_postypes(const BODY_DATA *B, const char *posnames) {
  LIST           *names = parse_keywords(posnames);
  LIST_ITERATOR *name_i = newListIterator(names);
  BUFFER           *buf = newBuffer(100);
  char            *name = NULL;
  char          *retval = NULL;
  int             found = 0;

  ITERATE_LIST(name, name_i) {
    const char *part_type = bodyGetPart(B, name);
    if(part_type != NULL) {
      found++;
      if(found != 1)
	bufferCat(buf, ", ");
      bufferCat(buf, part_type);
    }
  } deleteListIterator(name_i);
  deleteListWith(names, free);

  retval = strdup(bufferString(buf));
  deleteBuffer(buf);
  return retval;
}

const char *bodysizeGetName(int size) {
  init_body_dynamic();
  
  if(size < 0 || size >= listSize(bodysize_list))
    return NULL;
    
  return (const char*)listGet(bodysize_list, size);
}

int bodysizeGetNum(const char *size) {
  init_body_dynamic();
  
  int index = 0;
  LIST_ITERATOR *size_i = newListIterator(bodysize_list);
  char *size_name = NULL;
  ITERATE_LIST(size_name, size_i) {
    if(!strcasecmp(size, size_name)) {
      deleteListIterator(size_i);
      return index;
    }
    index++;
  } deleteListIterator(size_i);
  
  return BODYSIZE_NONE;
}

// Removed bodyposGetName() and bodyposGetNum() - using direct string storage now

BODY_DATA *newBody() {
  struct body_data*B = malloc(sizeof(BODY_DATA));
  B->parts = newList();

  return B;
}

void deleteBody(BODY_DATA *B) {
  // delete all of the bodyparts
  deleteListWith(B->parts, deleteBodypart);
  // free us
  free(B);
}

BODY_DATA *bodyCopy(const BODY_DATA *B) {
  BODY_DATA *Bnew = newBody();
  deleteListWith(Bnew->parts, deleteBodypart);
  Bnew->parts = listCopyWith(B->parts, bodypartCopy);
  Bnew->size  = B->size;

  return Bnew;
}

int bodyGetSize(const BODY_DATA *B) {
  return B->size;
}

void bodySetSize(BODY_DATA *B, int size) {
  B->size = size;
}

//
// Find a bodypart on the body with the given name
//
BODYPART *findBodypart(const BODY_DATA *B, const char *pos) {
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;

  ITERATE_LIST(part, part_i)
    if(!strcasecmp(part->name, pos))
      break;
  deleteListIterator(part_i);

  return part;
}

//
// Find a bodypart on the body with of the specified type that
// is not yet equipped with an item
//
BODYPART *findFreeBodypart(BODY_DATA *B, const char *type) {
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;
  ITERATE_LIST(part, part_i)
    if(part->type && !strcasecmp(part->type, type) && listSize(part->equipment) == 0)
      break;
  deleteListIterator(part_i);

  return part;
}

void bodyAddPosition(BODY_DATA *B, const char *pos, const char *type, int size) {
  BODYPART *part = findBodypart(B, pos);

  // if we've already found the part, just modify it
  if(part) {
    if(part->type) free(part->type);
    part->type = strdupsafe(type);
    part->size = size;
  }
  // otherwise, create a new one
  else {
    part = newBodypart(pos, type, size);
    listPut(B->parts, part);
  }
}

void bodyAddPositionByName(BODY_DATA *B, const char *pos, const char *type_name, int size) {
  bodyAddPosition(B, pos, type_name, size);
}

bool bodyRemovePosition(BODY_DATA *B, const char *pos) {
  BODYPART *part = findBodypart(B, pos);

  if(!part)
    return FALSE;

  listRemove(B->parts, part);
  deleteBodypart(part);
  return TRUE;
}

const char *bodyGetPart(const BODY_DATA *B, const char *pos) {
  BODYPART *part = findBodypart(B, pos);
  if(part) return part->type;
  else     return NULL;
}


double bodyPartRatio(const BODY_DATA *B, const char *pos) {
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART        *part = NULL;
  double      part_size = 0.0;
  double      body_size = 0.0;

  // add up all of the weights, and find the weight of our pos
  ITERATE_LIST(part, part_i) {
    body_size += part->size;
    if(is_keyword(pos, part->name, FALSE))
      part_size += part->size;
  }
  deleteListIterator(part_i);

  // to prevent div0, albeit an unlikely event
  return (body_size == 0.0 ? 0 : (part_size / body_size));
}


const char *bodyRandPart(const BODY_DATA *B, const char *pos) {
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;
  char     *name = NULL;
  int   size_sum = 0;
  int   pos_roll = 0;

  // add up all of the weights
  ITERATE_LIST(part, part_i) {
    // if we have a list of positions to draw from, only factor in those
    if(pos && *pos && !is_keyword(pos, part->name, FALSE))
      continue;
    size_sum += part->size;
  } deleteListIterator(part_i);

  // nothing that can be hit was found
  if(size_sum <= 1) {
    deleteListIterator(part_i);
    return NULL;
  }

  pos_roll = rand_number(1, size_sum);
  
  // find the position the roll corresponds to
  part_i = newListIterator(B->parts);
  ITERATE_LIST(part, part_i) {
    // if we have a list of positions to draw from, only factor in those
    if(pos && *pos && !is_keyword(pos, part->name, FALSE))
      continue;
    pos_roll -= part->size;
    if(pos_roll <= 0) {
      name = part->name;
      break;
    }
  } deleteListIterator(part_i);
  return name;
}


const char **bodyGetParts(const BODY_DATA *B, bool sort, int *num_pos) {
  *num_pos = listSize(B->parts);

  const char **parts = malloc(sizeof(char *) * *num_pos);
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;
  int i = 0;

  // Simple implementation - just return part names without complex sorting
  // since we no longer have integer-based position ordering
  ITERATE_LIST(part, part_i) {
    parts[i] = part->name;
    i++;
  } deleteListIterator(part_i);

  return parts;
}


bool bodyEquipPostypes(BODY_DATA *B, OBJ_DATA *obj, const char *types) {
  LIST  *pos_list = parse_keywords(types);
  LIST     *parts = NULL;
  BODYPART  *part = NULL;
  bool    success = TRUE;

  // make sure we have more than zero positions
  if(listSize(pos_list) == 0) {
    deleteList(pos_list);
    return FALSE;
  }

  // create our list of parts
  parts = newList();

  // get a list of all open slots in the list provided ...
  // equip them as we go along, incase we more than one of a piece.
  // if we don't do it this way, findFreeBodypart might find the same
  // piece multiple times (e.g. the same ear when it's looking for two ears)
  LIST_ITERATOR *pos_i = newListIterator(pos_list);
  char            *pos = NULL;

  ITERATE_LIST(pos, pos_i) {
    part = findFreeBodypart(B, pos);
    if(part && listSize(part->equipment) == 0) {
      listPut(part->equipment, obj);
      listPut(parts, part);
    }
  } deleteListIterator(pos_i);

  // make sure we supplied a valid number of empty positions
  if(listSize(pos_list) != listSize(parts)) {
    // remove equipment for every part we put it on
    while((part = listPop(parts)) != NULL)
      listRemove(part->equipment, obj);
    success = FALSE;
  }

  // garbage collection
  deleteListWith(pos_list, free);
  deleteList(parts);

  return success;
}


bool bodyEquipPosnames(BODY_DATA *B, OBJ_DATA *obj, const char *positions) {
  LIST *pos_list = parse_keywords(positions);
  LIST    *parts = NULL;
  BODYPART *part = NULL;
  bool   success = TRUE;

  // make sure we have more than zero positions
  if(listSize(pos_list) == 0) {
    deleteList(pos_list);
    return FALSE;
  }

  // create our list of parts
  parts = newList();

  // get a list of all open slots in the list provided
  LIST_ITERATOR *pos_i = newListIterator(pos_list);
  char            *pos = NULL;
  ITERATE_LIST(pos, pos_i) {
    part = findBodypart(B, pos);
    if(part && listSize(part->equipment) == 0 && !listIn(parts, part))
      listPut(parts, part);
  } deleteListIterator(pos_i);

  // make sure we found the right amount of parts
  if(listSize(parts) != listSize(pos_list) || listSize(parts) == 0)
    success = FALSE;

  // fill in all of the parts that need to be filled
  while( (part = listPop(parts)) != NULL)
    listPut(part->equipment, obj);

  // clean up our garbage
  deleteListWith(pos_list, free);
  deleteList(parts);

  return success;
}

bool bodyEquipPosnamesEx(BODY_DATA *B, OBJ_DATA *obj, const char *positions, 
                         const char *equipment_type, bool force) {
  LIST *pos_list = parse_keywords(positions);
  LIST    *parts = NULL;
  BODYPART *part = NULL;
  bool   success = TRUE;


  // make sure we have more than zero positions
  if(listSize(pos_list) == 0) {
    deleteList(pos_list);
    return FALSE;
  }

  // create our list of parts
  parts = newList();

  // get a list of all open slots in the list provided
  LIST_ITERATOR *pos_i = newListIterator(pos_list);
  char            *pos = NULL;
  ITERATE_LIST(pos, pos_i) {
    part = findBodypart(B, pos);
    if(!part) {
      continue;
    }
    if(listIn(parts, part)) {
      continue;
    }
    
    bool can_equip = FALSE;
    
    if(force) {
      // Force mode: always allow equipping
      can_equip = TRUE;
    } else if(listSize(part->equipment) == 0) {
      // No equipment: always allow
      can_equip = TRUE;
    } else if(equipment_type) {
      // Type filtering: check if existing equipment matches our type
      // If no existing equipment of this type, we can layer over it
      bool has_same_type = FALSE;
      LIST_ITERATOR *eq_i = newListIterator(part->equipment);
      OBJ_DATA *existing_obj = NULL;
      ITERATE_LIST(existing_obj, eq_i) {
        if(objIsType(existing_obj, equipment_type)) {
          has_same_type = TRUE;
          break;
        }
      } deleteListIterator(eq_i);
      
      if(!has_same_type) {
        can_equip = TRUE;
      }
    } else {
      // No equipment type specified: use old behavior (allow layering)
      can_equip = TRUE;
    }
    
    if(can_equip) {
      listPut(parts, part);
    }
  } deleteListIterator(pos_i);

  // make sure we found the right amount of parts
  if(listSize(parts) != listSize(pos_list) || listSize(parts) == 0)
    success = FALSE;

  // fill in all of the parts that need to be filled
  while( (part = listPop(parts)) != NULL)
    listPut(part->equipment, obj);

  // clean up our garbage
  deleteListWith(pos_list, free);
  deleteList(parts);

  return success;
}

const char *bodyEquippedWhere(BODY_DATA *B, OBJ_DATA *obj) {
  static char buf[SMALL_BUFFER];
  *buf = '\0';

  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;
  // go through the list of all parts, and print the name of any one
  // with the piece of equipment on it, onto the buf
  ITERATE_LIST(part, part_i) {
    if(listIn(part->equipment, obj)) {
      // if we've already printed something, add a comma
      if(*buf)
	strcat(buf, ", ");
      strcat(buf, part->name);
    }
  } deleteListIterator(part_i);
  return buf;
}

LIST *bodyGetEquipment(BODY_DATA *B, const char *pos) {
  BODYPART *part = findBodypart(B, pos);
  return (part ? part->equipment : NULL);
}

bool bodyUnequip(BODY_DATA *B, const OBJ_DATA *obj) {
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART      *part   = NULL;
  bool           found  = FALSE;

  ITERATE_LIST(part, part_i) {
    if(listIn(part->equipment, obj)) {
      listRemove(part->equipment, obj);
      found = TRUE;
    }
  } deleteListIterator(part_i);
  return found;
}

LIST *bodyGetAllEq(BODY_DATA *B) {
  LIST *equipment = newList();
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;

  ITERATE_LIST(part, part_i) {
    if(listSize(part->equipment) > 0) {
      LIST_ITERATOR *eq_i = newListIterator(part->equipment);
      OBJ_DATA *obj = NULL;
      ITERATE_LIST(obj, eq_i) {
        if(!listIn(equipment, obj))
          listPut(equipment, obj);
      } deleteListIterator(eq_i);
    }
  } deleteListIterator(part_i);
  return equipment;
}

LIST *bodyUnequipAll(BODY_DATA *B) {
  LIST *equipment = newList();
  LIST_ITERATOR *part_i = newListIterator(B->parts);
  BODYPART *part = NULL;

  ITERATE_LIST(part, part_i) {
    if(listSize(part->equipment) > 0) {
      LIST_ITERATOR *eq_i = newListIterator(part->equipment);
      OBJ_DATA *obj = NULL;
      ITERATE_LIST(obj, eq_i) {
        if(!listIn(equipment, obj))
          listPut(equipment, obj);
      } deleteListIterator(eq_i);
      // Clear the equipment list for this part
      deleteList(part->equipment);
      part->equipment = newList();
    }
  } deleteListIterator(part_i);
  return equipment;
}

int numBodyparts(const BODY_DATA *B) {
  return listSize(B->parts);
}

//*****************************************************************************
// Dynamic body size and position type management
//*****************************************************************************

void init_body_dynamic() {
  if(bodysize_list == NULL) {
    bodysize_list = newList();
    // Initialize with default hardcoded values
    for(int i = 0; i < NUM_BODYSIZES; i++) {
      listPut(bodysize_list, strdup(default_bodysize[i]));
    }
  }
  if(bodypos_list == NULL) {
    bodypos_list = newList();
    // Initialize with standard body position types
    int num_types = sizeof(default_bodypos) / sizeof(default_bodypos[0]);
    for(int i = 0; i < num_types; i++) {
      listPut(bodypos_list, strdup(default_bodypos[i]));
    }
  }
}

bool body_add_size(const char *size_name) {
  init_body_dynamic();
  
  // Check if already exists in dynamic list
  LIST_ITERATOR *size_i = newListIterator(bodysize_list);
  char *existing = NULL;
  ITERATE_LIST(existing, size_i) {
    if(!strcasecmp(existing, size_name)) {
      deleteListIterator(size_i);
      return FALSE; // Already exists
    }
  } deleteListIterator(size_i);
  
  listPut(bodysize_list, strdup(size_name));
  return TRUE;
}

bool body_remove_size(const char *size_name) {
  init_body_dynamic();
  
  LIST_ITERATOR *size_i = newListIterator(bodysize_list);
  char *existing = NULL;
  ITERATE_LIST(existing, size_i) {
    if(!strcasecmp(existing, size_name)) {
      listRemove(bodysize_list, existing);
      free(existing);
      deleteListIterator(size_i);
      return TRUE;
    }
  } deleteListIterator(size_i);
  
  return FALSE; // Not found
}

LIST *body_get_all_sizes() {
  init_body_dynamic();
  LIST *all_sizes = newList();
  
  // Copy all sizes from dynamic list
  LIST_ITERATOR *size_i = newListIterator(bodysize_list);
  char *size = NULL;
  ITERATE_LIST(size, size_i) {
    listPut(all_sizes, strdup(size));
  } deleteListIterator(size_i);
  
  return all_sizes;
}

LIST *body_get_all_position_types() {
  init_body_dynamic();
  LIST *all_types = newList();
  
  // Copy all position types from dynamic list
  LIST_ITERATOR *pos_i = newListIterator(bodypos_list);
  char *pos = NULL;
  ITERATE_LIST(pos, pos_i) {
    listPut(all_types, strdup(pos));
  } deleteListIterator(pos_i);
  
  return all_types;
}

bool body_add_position_type(const char *pos_name) {
  init_body_dynamic();
  
  // Check if already exists in dynamic list
  LIST_ITERATOR *pos_i = newListIterator(bodypos_list);
  char *existing = NULL;
  ITERATE_LIST(existing, pos_i) {
    if(!strcasecmp(existing, pos_name)) {
      deleteListIterator(pos_i);
      return FALSE; // Already exists
    }
  } deleteListIterator(pos_i);
  
  listPut(bodypos_list, strdup(pos_name));
  return TRUE;
}

bool body_remove_position_type(const char *pos_name) {
  init_body_dynamic();
  
  LIST_ITERATOR *pos_i = newListIterator(bodypos_list);
  char *existing = NULL;
  ITERATE_LIST(existing, pos_i) {
    if(!strcasecmp(existing, pos_name)) {
      deleteListIterator(pos_i);
      listRemove(bodypos_list, existing);
      free(existing);
      return TRUE;
    }
  } deleteListIterator(pos_i);
  return FALSE;
}
