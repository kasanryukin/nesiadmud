//*****************************************************************************
//
// races.c
//
// contains all of the information assocciated with different races. If you are
// wanting to add new races to the MUD, it is suggested you do so through the
// add_race() function, and make a new module for your MUD's races.
//
//*****************************************************************************

#include "mud.h"
#include "utils.h"
#include "body.h"

#include "races.h"



//*****************************************************************************
//
// local datastructures, functions, and defines
//
//*****************************************************************************

// how big is hour hashtable for holding race data?
#define RACE_TABLE_SIZE    55
HASHTABLE *race_table = NULL;


typedef struct race_data {
  char      *name;
  char      *abbrev;
  BODY_DATA *body;
  bool       pc_ok;
} RACE_DATA;


RACE_DATA *newRace(const char *name, const char *abbrev, BODY_DATA *body,
		   bool pc_ok) {
  RACE_DATA *data = malloc(sizeof(RACE_DATA));
  data->name   = strdupsafe(name);
  data->abbrev = strdupsafe(abbrev);
  data->body   = bodyCopy(body);
  data->pc_ok  = pc_ok;
  return data;
}



//*****************************************************************************
//
// implementation of race.h
//
//*****************************************************************************
void init_races() {
  // create the table for holding race data
  race_table = newHashtable();

  // make the default human body
  BODY_DATA *body = newBody();
  bodySetSize(body, BODYSIZE_MEDIUM);
  bodyAddPositionByName(body, "right grip",              "held",                0);
  bodyAddPositionByName(body, "left grip",               "held",                0);
  bodyAddPositionByName(body, "right foot",              "right foot",          2);
  bodyAddPositionByName(body, "left foot",               "left foot",           2);
  bodyAddPositionByName(body, "right leg",               "leg",                 9);
  bodyAddPositionByName(body, "left leg",                "leg",                 9);
  bodyAddPositionByName(body, "waist",                   "waist",               1);
  bodyAddPositionByName(body, "right ring finger",       "finger",              1);
  bodyAddPositionByName(body, "left ring finger",        "finger",              1);
  bodyAddPositionByName(body, "left middle finger",      "finger",              0);
  bodyAddPositionByName(body, "right middle finger",     "finger",              0);
  bodyAddPositionByName(body, "right hand",              "right hand",          2);
  bodyAddPositionByName(body, "left hand",               "left hand",           2);
  bodyAddPositionByName(body, "right wrist",             "wrist",               1);
  bodyAddPositionByName(body, "left wrist",              "wrist",               1);
  bodyAddPositionByName(body, "right arm",               "arm",                 7);
  bodyAddPositionByName(body, "left arm",                "arm",                 7);
  bodyAddPositionByName(body, "about body",              "about body",          0);
  bodyAddPositionByName(body, "torso",                   "torso",              50);
  bodyAddPositionByName(body, "neck",                    "neck",                1);
  bodyAddPositionByName(body, "right ear",               "ear",                 0);
  bodyAddPositionByName(body, "left ear",                "ear",                 0);
  bodyAddPositionByName(body, "eyes",                    "eyes",                0);
  bodyAddPositionByName(body, "face",                    "face",                2);
  bodyAddPositionByName(body, "head",                    "head",                2);
  bodyAddPositionByName(body, "floating about head",     "floating about head", 0);
  //                                                                  ------
  //                                                                    100

  // add the basic races
  add_race("human", "hum", body, FALSE);
  //********************************************************************
  // If you are wanting to add new, non-stock races it is suggested
  // you do so through a module and import them with add_race instead
  // of putting them directly into this folder. This will make your life
  // much easier whenever new versions of NakedMud are released and you
  // want to upgrade!
  //********************************************************************
}


void add_race(const char *name, const char *abbrev, BODY_DATA *body, int pc_ok){
  hashPut(race_table, name, newRace(name, abbrev, body, pc_ok));
}

bool remove_race(const char *name) {
  RACE_DATA *race = hashRemove(race_table, name);
  if(race != NULL) {
    if(race->name) free(race->name);
    if(race->abbrev) free(race->abbrev);
    if(race->body) deleteBody(race->body);
    free(race);
    return TRUE;
  }
  return FALSE;
}

int raceCount() {
  return hashSize(race_table);
}

bool isRace(const char *name) {
  return (hashGet(race_table, name) != NULL);
}

BODY_DATA *raceCreateBody(const char *name) {
  RACE_DATA *data = hashGet(race_table, name);
  return (data ? bodyCopy(data->body) : NULL);
}

bool raceIsForPC(const char *name) {
  RACE_DATA *data = hashGet(race_table, name);
  return (data ? data->pc_ok : FALSE);
}

const char *raceGetAbbrev(const char *name) {
  RACE_DATA *data = hashGet(race_table, name);
  return (data ? data->abbrev : NULL);
}

const char *raceDefault() {
  return "human";
}

const char *raceGetList(bool pc_only) {
  static char buf[MAX_BUFFER];
  LIST       *name_list = newList();
  HASH_ITERATOR *race_i = newHashIterator(race_table);
  const char      *name = NULL;
  RACE_DATA       *data = NULL;

  // collect all of our names
  ITERATE_HASH(name, data, race_i) {
    if(pc_only && data->pc_ok == FALSE) continue;
    listPutWith(name_list, strdup(name), strcmp);
  }
  deleteHashIterator(race_i);

  // print all the names to our buffer
  char *new_name = NULL; // gotta use a new name ptr.. can't free const
  int i = 0;
  while( (new_name = listPop(name_list)) != NULL) {
    i += snprintf(buf+i, MAX_BUFFER-i, "%s%s",
		  new_name, (listSize(name_list) > 0 ? ", " : ""));
    free(new_name);
  }

  // delete our list of names and return the buffer
  deleteListWith(name_list, free);
  return buf;
}
