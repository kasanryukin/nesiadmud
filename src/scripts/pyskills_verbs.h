// ============================================================================
// pyskills_verbs.h
//
// Python wrapper for skills/verbs auxiliary data on objects.
//
// ============================================================================

#ifndef __PYSKILLS_VERBS_H
#define __PYSKILLS_VERBS_H

#include "../gearskills/skills_verbs_aux.h"

//
// Register all skills/verbs methods with the PyObj class.
// Call this during PyObj initialization (from PyInit_PyObj or similar).
void PySkillsVerbs_registerMethods(void);

#endif // __PYSKILLS_VERBS_H