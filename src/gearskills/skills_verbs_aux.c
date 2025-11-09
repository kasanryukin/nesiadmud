// ============================================================================
// skills_verbs_aux.c
// ============================================================================

#include "../mud.h"
#include "../utils.h"
#include "../storage.h"
#include "../auxiliary.h"
#include "skills_verbs_aux.h"

//*****************************************************************************
// Auxiliary data handlers (required by auxiliary system)
//*****************************************************************************

//*****************************************************************************
// Skill assignment functions
//*****************************************************************************

void svaux_assign_skill(SKILLS_VERBS_AUX *aux, int slot, const char *skill) {
  if (!aux || slot < 0 || slot > 4)
    return;
  
  // Free old skill if it exists
  if (aux->skills[slot])
    free(aux->skills[slot]);
  
  // Assign new skill (or empty string if clearing)
  aux->skills[slot] = strdupsafe(skill ? skill : "");
}

const char *svaux_get_skill(SKILLS_VERBS_AUX *aux, int slot) {
  if (!aux || slot < 0 || slot > 4)
    return "";
  
  return (aux->skills[slot] ? aux->skills[slot] : "");
}

int svaux_get_active_skill_slot(SKILLS_VERBS_AUX *aux) {
  if (!aux)
    return 0;
  
  return aux->active_skill_slot;
}

void svaux_set_active_skill_slot(SKILLS_VERBS_AUX *aux, int slot) {
  if (!aux || slot < 0 || slot > 4)
    return;
  
  aux->active_skill_slot = slot;
}

/**
 * Create new skills/verbs auxiliary data
 */
void *svaux_new(void) {
  SKILLS_VERBS_AUX *aux = malloc(sizeof(SKILLS_VERBS_AUX));
  
  // Initialize skill slots
  for (int i = 0; i < 5; i++) {
    aux->skills[i] = strdup("");
  }
  aux->active_skill_slot = 0;
  
  // Initialize verb handlers
  aux->verb_handlers = newHashtable();
  
  return aux;
}

/**
 * Delete skills/verbs auxiliary data
 */
void svaux_delete(void *data) {
  if(!data)
    return;
  
  SKILLS_VERBS_AUX *aux = (SKILLS_VERBS_AUX *)data;
  
  // Delete all skill slots
  for (int i = 0; i < 5; i++) {
    if (aux->skills[i])
      free(aux->skills[i]);
  }
  
  // Delete all verb handlers
  if(aux->verb_handlers) {
    HASH_ITERATOR *iter = newHashIterator(aux->verb_handlers);
    const char *verb;
    char *verb_data;
    ITERATE_HASH(verb, verb_data, iter) {
      if(verb_data)
        free(verb_data);
    }
    deleteHashIterator(iter);
    deleteHashtable(aux->verb_handlers);
  }
  
  free(aux);
}


/**
 * Copy skills/verbs auxiliary data
 */
void svaux_copyTo(void *from, void *to) {
  if(!from || !to)
    return;
  
  SKILLS_VERBS_AUX *from_aux = (SKILLS_VERBS_AUX *)from;
  SKILLS_VERBS_AUX *to_aux = (SKILLS_VERBS_AUX *)to;
  
  // Copy skill slots
  for (int i = 0; i < 5; i++) {
    if (to_aux->skills[i])
      free(to_aux->skills[i]);
    to_aux->skills[i] = strdupsafe(from_aux->skills[i]);
  }
  to_aux->active_skill_slot = from_aux->active_skill_slot;
  
  // Copy verb handlers
  HASH_ITERATOR *iter = newHashIterator(from_aux->verb_handlers);
  const char *verb;
  char *verb_data;
  
  ITERATE_HASH(verb, verb_data, iter) {
    hashPut(to_aux->verb_handlers, verb, strdupsafe(verb_data));
  }
  deleteHashIterator(iter);
}

/**
 * Copy (duplicate) skills/verbs auxiliary data
 */
void *svaux_copy(void *data) {
  if(!data)
    return svaux_new();
  
  SKILLS_VERBS_AUX *new_aux = svaux_new();
  svaux_copyTo(data, new_aux);
  return new_aux;
}

/**
 * Store skills/verbs auxiliary data to storage set
 */
STORAGE_SET *svaux_store(void *data) {
  STORAGE_SET *set = new_storage_set();
  if(!data)
    return set;
  
  SKILLS_VERBS_AUX *aux = (SKILLS_VERBS_AUX *)data;
  
  // Store skill slots as comma-separated list
  BUFFER *skills_buf = newBuffer(1);
  for (int i = 0; i < 5; i++) {
    if (i > 0)
      bufferCat(skills_buf, ",");
    bufferCat(skills_buf, aux->skills[i] ? aux->skills[i] : "");
  }
  store_string(set, "skills", bufferString(skills_buf));
  deleteBuffer(skills_buf);
  
  // Store active skill slot
  char temp_str[32];
  snprintf(temp_str, sizeof(temp_str), "%d", aux->active_skill_slot);
  store_string(set, "active_skill_slot", temp_str);
  
  // Store verb handlers as comma-separated list: "verb|data,verb|data"
  BUFFER *verbs_buf = newBuffer(1);
  HASH_ITERATOR *iter = newHashIterator(aux->verb_handlers);
  const char *verb;
  char *verb_data;
  bool first = TRUE;
  
  ITERATE_HASH(verb, verb_data, iter) {
    if(!first)
      bufferCat(verbs_buf, ",");
    bufferCat(verbs_buf, verb);
    bufferCat(verbs_buf, "|");
    bufferCat(verbs_buf, verb_data);
    first = FALSE;
  }
  deleteHashIterator(iter);
  
  store_string(set, "verb_handlers", bufferString(verbs_buf));
  deleteBuffer(verbs_buf);
  
  return set;
}

/**
 * Read skills/verbs auxiliary data from storage set
 */
void *svaux_read(STORAGE_SET *set) {
  SKILLS_VERBS_AUX *aux = svaux_new();
  
  // Read skill slots
  const char *skills_str = read_string(set, "skills");
  if(skills_str && *skills_str) {
    LIST *skills = parse_strings(skills_str, ',');
    LIST_ITERATOR *iter = newListIterator(skills);
    char *skill = NULL;
    int slot = 0;
    
    ITERATE_LIST(skill, iter) {
      if (slot < 5) {
        svaux_assign_skill(aux, slot, skill);
        slot++;
      }
    }
    deleteListIterator(iter);
    deleteListWith(skills, free);
  }
  
  // Read active skill slot
  const char *active_str = read_string(set, "active_skill_slot");
  if(active_str && *active_str) {
    int active_slot = atoi(active_str);
    if (active_slot >= 0 && active_slot <= 4)
      aux->active_skill_slot = active_slot;
  }
  
  // Read verb handlers
  const char *verbs_str = read_string(set, "verb_handlers");
  if(verbs_str && *verbs_str) {
    LIST *verbs = parse_strings(verbs_str, ',');
    LIST_ITERATOR *iter = newListIterator(verbs);
    char *verb_pair;
    
    ITERATE_LIST(verb_pair, iter) {
      char verb[SMALL_BUFFER];
      char verb_data[MAX_BUFFER];
      if(sscanf(verb_pair, "%[^|]|%[^\n]", verb, verb_data) == 2) {
        hashPut(aux->verb_handlers, verb, strdupsafe(verb_data));
      }
    }
    deleteListIterator(iter);
    deleteListWith(verbs, free);
  }
  
  return aux;
}


//*****************************************************************************
// Verb handler functions
//*****************************************************************************

void svaux_add_verb(SKILLS_VERBS_AUX *aux, const char *verb, const char *script, int charges, int cooldown) {
  if(!aux || !verb || !*verb)
    return;
  
  BUFFER *buf = newBuffer(1);
  char temp_str[32];
  
  bufferCat(buf, script ? script : "");
  bufferCat(buf, "|");
  snprintf(temp_str, sizeof(temp_str), "%d", charges);
  bufferCat(buf, temp_str);
  bufferCat(buf, "|");
  snprintf(temp_str, sizeof(temp_str), "%d", cooldown);
  bufferCat(buf, temp_str);
  bufferCat(buf, "|0"); // last_used = 0
  
  char *verb_data = strdupsafe(bufferString(buf));
  deleteBuffer(buf);
  
  hashPut(aux->verb_handlers, verb, verb_data);
}

void svaux_remove_verb(SKILLS_VERBS_AUX *aux, const char *verb) {
  if(!aux || !verb || !*verb)
    return;
  
  char *verb_data = hashRemove(aux->verb_handlers, verb);
  if(verb_data)
    free(verb_data);
}

const char *svaux_get_verb_script(SKILLS_VERBS_AUX *aux, const char *verb) {
  if(!aux || !verb || !*verb)
    return "";
  
  char *verb_data = hashGet(aux->verb_handlers, verb);
  if(!verb_data)
    return "";
  
  static char script[SMALL_BUFFER];
  int charges, cooldown, last_used;
  sscanf(verb_data, "%[^|]|%d|%d|%d", script, &charges, &cooldown, &last_used);
  return script;
}

int svaux_get_verb_charges(SKILLS_VERBS_AUX *aux, const char *verb) {
  if(!aux || !verb || !*verb)
    return 0;
  
  char *verb_data = hashGet(aux->verb_handlers, verb);
  if(!verb_data)
    return 0;
  
  char script[SMALL_BUFFER];
  int charges, cooldown, last_used;
  sscanf(verb_data, "%[^|]|%d|%d|%d", script, &charges, &cooldown, &last_used);
  return charges;
}

int svaux_get_verb_cooldown(SKILLS_VERBS_AUX *aux, const char *verb) {
  if(!aux || !verb || !*verb)
    return 0;
  
  char *verb_data = hashGet(aux->verb_handlers, verb);
  if(!verb_data)
    return 0;
  
  char script[SMALL_BUFFER];
  int charges, cooldown, last_used;
  sscanf(verb_data, "%[^|]|%d|%d|%d", script, &charges, &cooldown, &last_used);
  return cooldown;
}

LIST *svaux_get_verb_list(SKILLS_VERBS_AUX *aux) {
  LIST *list = newList();
  if(!aux || !aux->verb_handlers)
    return list;
  
  HASH_ITERATOR *iter = newHashIterator(aux->verb_handlers);
  const char *verb;
  char *verb_data;  // This is required by ITERATE_HASH macro
  ITERATE_HASH(verb, verb_data, iter) {
    listPut(list, strdupsafe(verb));
  }
  deleteHashIterator(iter);
  return list;
}

bool svaux_verb_on_cooldown(SKILLS_VERBS_AUX *aux, const char *verb, time_t current_time) {
  if(!aux || !verb || !*verb)
    return FALSE;
  
  char *verb_data = hashGet(aux->verb_handlers, verb);
  if(!verb_data)
    return FALSE;
  
  char script[SMALL_BUFFER];
  int charges, cooldown, last_used;
  sscanf(verb_data, "%[^|]|%d|%d|%d", script, &charges, &cooldown, &last_used);
  
  if(cooldown <= 0)
    return FALSE;
  
  return (current_time - last_used) < cooldown;
}

bool svaux_use_verb(SKILLS_VERBS_AUX *aux, const char *verb, time_t current_time) {
  if(!aux || !verb || !*verb)
    return FALSE;
  
  char *verb_data = hashGet(aux->verb_handlers, verb);
  if(!verb_data)
    return FALSE;
  
  char script[SMALL_BUFFER];
  int charges, cooldown, last_used;
  sscanf(verb_data, "%[^|]|%d|%d|%d", script, &charges, &cooldown, &last_used);
  
  // Check charges
  if(charges >= 0) {
    if(charges <= 0)
      return FALSE;
    charges--;
  }
  
  // Update verb data
  BUFFER *buf = newBuffer(1);
  char temp_str[32];
  
  bufferCat(buf, script);
  bufferCat(buf, "|");
  snprintf(temp_str, sizeof(temp_str), "%d", charges);
  bufferCat(buf, temp_str);
  bufferCat(buf, "|");
  snprintf(temp_str, sizeof(temp_str), "%d", cooldown);
  bufferCat(buf, temp_str);
  bufferCat(buf, "|");
  snprintf(temp_str, sizeof(temp_str), "%ld", (long)current_time);
  bufferCat(buf, temp_str);
  
  char *new_data = strdupsafe(bufferString(buf));
  deleteBuffer(buf);
  
  free(verb_data);
  hashPut(aux->verb_handlers, verb, new_data);
  
  return TRUE;
}

//*****************************************************************************
// Module initialization
//*****************************************************************************

void skills_verbs_aux_init(void) {
  AUXILIARY_FUNCS *funcs = newAuxiliaryFuncs(
    AUXILIARY_TYPE_OBJ,  // Only for objects
    svaux_new,
    svaux_delete,
    svaux_copyTo,
    svaux_copy,
    svaux_store,
    svaux_read
  );
  
  auxiliariesInstall("skills_verbs", funcs);
  log_string("Skills and Verbs auxiliary data system initialized");
}