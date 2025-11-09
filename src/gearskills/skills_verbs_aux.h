// ============================================================================
// skills_verbs_aux.h
// ============================================================================

#ifndef __SKILLS_VERBS_AUX_H
#define __SKILLS_VERBS_AUX_H

//*****************************************************************************
// Skills and Verbs Auxiliary Data
//
// Provides skill assignment (5 slots per item) and custom verbs for objects.
// Skills track which skill should receive XP when item is used.
// Verbs provide custom actions on items.
//*****************************************************************************

typedef struct {
  char *skills[5];            // 5 skill slots (skill names, or empty strings)
  int active_skill_slot;      // currently active skill slot (0-4)
  HASHTABLE *verb_handlers;   // verb_name -> verb_data string
} SKILLS_VERBS_AUX;

// Initialize the auxiliary data module (call once at startup)
void skills_verbs_aux_init();

// Skill assignment functions
void         svaux_assign_skill            (SKILLS_VERBS_AUX *aux, int slot, const char *skill);
const char  *svaux_get_skill               (SKILLS_VERBS_AUX *aux, int slot);
int          svaux_get_active_skill_slot   (SKILLS_VERBS_AUX *aux);
void         svaux_set_active_skill_slot   (SKILLS_VERBS_AUX *aux, int slot);

// Verb handler functions
void         svaux_add_verb                (SKILLS_VERBS_AUX *aux, const char *verb, const char *script, int charges, int cooldown);
void         svaux_remove_verb             (SKILLS_VERBS_AUX *aux, const char *verb);
const char  *svaux_get_verb_script         (SKILLS_VERBS_AUX *aux, const char *verb);
int          svaux_get_verb_charges        (SKILLS_VERBS_AUX *aux, const char *verb);
int          svaux_get_verb_cooldown       (SKILLS_VERBS_AUX *aux, const char *verb);
LIST        *svaux_get_verb_list           (SKILLS_VERBS_AUX *aux);
bool         svaux_verb_on_cooldown        (SKILLS_VERBS_AUX *aux, const char *verb, time_t current_time);
bool         svaux_use_verb                (SKILLS_VERBS_AUX *aux, const char *verb, time_t current_time);

#endif // __SKILLS_VERBS_AUX_H