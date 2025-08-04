# Extending NakedMud: An Introduction to Modules, Storage Sets, and Auxiliary Data

## Table of Contents
- [Introduction](#introduction)
- [Modules](#modules)
  - [Preparing to Program](#preparing-to-program)
  - [Programming a Mail Module](#programming-a-mail-module)
- [Storage Sets](#storage-sets)
- [Auxiliary Data](#auxiliary-data)
- [Conclusion](#conclusion)
- [Appendices](#appendices)

## Introduction

There are three aspects of NakedMud's code that must be understood to efficiently build a MUD using the codebase: modules, auxiliary data, and storage sets. 

- **Modules** and **auxiliary data** allow programmers to organize their work by concept (e.g., combat-related functions and variables, magic-related systems, etc.) rather than by data structure.
- **Storage sets** provide a general format for saving and loading data from files, eliminating much of the manual work involved in file I/O.

This manual serves as a tutorial for using these three core components of NakedMud.

## Modules

### Preparing to Program

Before creating a new module, you'll need to set up the basic structure. Here's how to create a mail module:

1. **Create a module directory**:
   ```bash
   mkdir src/mail
   ```

2. **Update the Makefile**:
   Add your module to the `MODULES` variable in `src/Makefile`:
   ```makefile
   MODULES += time socials alias help mail
   ```

3. **Create a module.mk file**:
   In your module directory, create `module.mk`:
   ```makefile
   # include all of the source files contained in this module
   SRC += mail/mail.c
   ```

4. **Create the main source file**:
   Create `mail.c` with the following content:
   ```c
   #include "../mud.h"
   #include "../utils.h"         // for get_time()
   #include "../character.h"     // for handling characters sending mail
   #include "../save.h"          // for char_exists()
   #include "../object.h"        // for creating mail objects
   #include "../handler.h"       // for giving mail to characters
   #include "../editor/editor.h" // for access to sockets' notepads
   #include "mail.h"

   // boot up the mail module
   void init_mail(void) {
     printf("Nothing in the mail module yet!");
   }
   ```

5. **Create the header file**:
   Create `mail.h`:
   ```c
   #ifndef MAIL_H
   #define MAIL_H
   void init_mail(void);
   #endif // MAIL_H
   ```

6. **Update mud.h**:
   Add the module define:
   ```c
   #define MODULE_MAIL
   ```

7. **Update gameloop.c**:
   Add the module initialization:
   ```c
   #ifdef MODULE_MAIL
   #include "mail/mail.h"
   #endif
   ```
   And in the initialization section:
   ```c
   #ifdef MODULE_MAIL
     log_string("Initializing mail system.");
     init_mail();
   #endif
   ```

### Programming a Mail Module

Let's implement a basic mail system. First, define the mail data structure:

```c
typedef struct {
  char *sender;       // name of the char who sent this mail
  char *time;         // the time it was sent at
  BUFFER *mssg;       // the accompanying message
} MAIL_DATA;
```

Now, add functions to create and delete mail:

```c
// create a new piece of mail.
MAIL_DATA *newMail(CHAR_DATA *sender, const char *mssg) {
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->sender = strdup(charGetName(sender));
  mail->time   = strdup(get_time());
  mail->mssg   = newBuffer(strlen(mssg));
  bufferCat(mail->mssg, mssg);
  return mail;
}

// free all of the memory that was allocated to make this piece of mail
void deleteMail(MAIL_DATA *mail) {
  if(mail->sender) free(mail->sender);
  if(mail->time)   free(mail->time);
  if(mail->mssg)   deleteBuffer(mail->mssg);
  free(mail);
}
```

Next, we'll implement the mail command that allows players to send messages using their notepad content:

```c
// mails a message to the specified person. This command must take the 
// following form:
//   mail <person>
//
// The contents of the character's notepad will be used as the body of the
// message. The character's notepad must not be empty.
COMMAND(cmd_mail) {
  // make sure the character exists
  if(!char_exists(arg))
    send_to_char(ch, "Noone named %s is registered on %s.\r\n",
                 arg, "<insert mud name here>");
  // make sure we have a socket - we'll need access to its notepad
  else if(!charGetSocket(ch))
    send_to_char(ch, "Only characters with sockets can send mail!\r\n");
  // make sure our notepad is not empty
  else if(!*bufferString(socketGetNotepad(charGetSocket(ch))))
    send_to_char(ch, "Your notepad is empty. "
                 "First, try writing something with {cwrite{n.\r\n");
  // the character exists. Let's parse the items and send the mail
  else {
    MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));
    
    // if we had some way of storing mail, we'd now do that. But since we
    // don't, let's just delete the mail.
    deleteMail(mail);

    // let the character know we've sent the mail
    send_to_char(ch, "You send a message to %s.\r\n", arg);
  }
}
```

We'll also need to add this command to our module's initialization:

```c
// boot up the mail module
void init_mail(void) {
  // add all of the commands that come with this module
  // initialize our mail table
  mail_table = newHashtable();

  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}

// At the top of mail.c, after includes
HASHTABLE *mail_table = NULL;

// Update cmd_mail to store mail in the hashtable
else {
  MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));
  
  // see if the receiver already has a mail list
  LIST *mssgs = hashGet(mail_table, arg);
  
  // if they don't, create one and add it to the hashtable
  if(mssgs == NULL) {
    mssgs = newList();
    hashPut(mail_table, arg, mssgs);
  }

  // add the new mail to our mail list
  listPut(mssgs, mail);

  // let the character know we've sent the mail
  send_to_char(ch, "You send a message to %s.\r\n", arg);
}

// checks to see if the character has any mail. If they do, convert each piece
// of mail into an object, and transfer them all into the character's inventory.
COMMAND(cmd_receive) {
  // Remove the character's mail list from our mail table
  LIST *mail_list = hashRemove(mail_table, charGetName(ch));

  // make sure the list exists
  if(mail_list == NULL || listSize(mail_list) == 0)
    send_to_char(ch, "You have no new mail.\r\n");
  // hand over all of the mail
  else {
    // go through each piece of mail, make an object for it, 
    // and transfer the new object to us
    LIST_ITERATOR *mail_i = newListIterator(mail_list);
    MAIL_DATA *mail = NULL;
    ITERATE_LIST(mail, mail_i) {
      OBJ_DATA *obj = newObj();
      objSetName(obj, "a letter");
      objSetKeywords(obj, "letter, mail");
      objSetRdesc(obj, "A letter is here.");
      objSetMultiName(obj, "A stack of %d letters");
      objSetMultiRdesc(obj, "A stack of %d letters are here.");
      bprintf(objGetDescBuffer(obj),
             "Sender   : %s\r\n"
             "Date sent: %s\r\n"
             "%s", mail->sender, mail->time, bufferString(mail->mssg));
      
      // give the object to the character
      obj_to_game(obj);
      obj_to_char(obj, ch);
    } deleteListIterator(mail_i);

    // let the character know how much mail they received
    send_to_char(ch, "You receive %d letter%s.\r\n", 
                 listSize(mail_list), (listSize(mail_list) == 1 ? "" : "s"));
  }
  
  // delete the mail list, and all of its contents
  if(mail_list != NULL) deleteListWith(mail_list, deleteMail);
}

## Storage Sets

Storage sets are a big part of NakedMud. They serve a few important purposes: They simplify the process of saving data from files by eliminating your need to come up with formatting schemes for your flatfiles. They also eliminate your need to write file parsers to extract data from files; the process of retrieving information from a file is reduced to querying for the value of some key. As we will learn later, they also play an integral role in the process of saving and loading auxiliary data.

In this section, we will learn the ropes of storage sets. We'll see how to store and read lists and strings. The other data types storage sets can deal with (ints, bools, doubles, longs) are handled in the exact same way as strings, except with different function names. After this tutorial, you should be able to extrapolate how these other data types interact with storage sets. In the next section on auxiliary data, we will examine how storage sets work in conjunction with auxiliary data.

### Getting Up To Speed

If you have not already performed the tutorial on modules, you will need to do a couple things before you can go through the storage set tutorial. If you have already performed the tutorial on modules, disregard this section and move onto the next one.

1. In your `src` directory, make a new directory called `mail`
2. Examine appendix A. For each of the 3 files you see, add it and its contents to the `mail` directory you just created
3. Edit the `Makefile` in your `src` directory. To the line listing off your optional modules, add `mail`
4. Edit `mud.h` and add `#define MODULE_MAIL` to the list of other module defines you have
5. Edit `gameloop.c` and add `#include "mail/mail.h"` to the list of optional module headers in the same fashion it is added for the other module headers
6. Still in `gameloop.c`, search for the init functions of your other modules and add your `init_mail()` function in the same way the init() functions for your other modules is added

### Storage Set Basics

In the section on modules, we designed a 'proof of concept' for a mail system. One feature we did not add was the ability for unreceived mail to be persistent. If the MUD ever crashed or rebooted, all mail not yet received would be lost. This, of course, is highly undesirable. We will now build on our mail module, and demonstrate how to make mail persistent with the aid of storage sets.

The first thing we will need to do is add the header for interacting with storage sets. Let's do this where we include all the other headers we need for interacting with core features of the MUD. We'll add the new header right after we add the `handler.h` header:

```c
#include "../handler.h"       // for giving mail to characters
#include "../storage.h"       // for saving/loading mail
```

Next, we'll define the mail file location and implement the storage set functionality. Add this at the top of `mail.c` where we define the hashtable:

```c
// this is the file we will save all unreceived mail in, when the mud is down
#define MAIL_FILE "../lib/misc/mail"

// maps charName to a list of mail they have received
HASHTABLE *mail_table = NULL;
```

Now, let's add functions to convert between `MAIL_DATA` and `STORAGE_SET`:

```c
// parse a piece of mail from a storage set
MAIL_DATA *mailRead(STORAGE_SET *set) {
  // allocate some memory for the mail
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->mssg      = newBuffer(1);

  // read in all of our values
  mail->sender = strdup(read_string(set, "sender"));
  mail->time   = strdup(read_string(set, "time"));
  bufferCat(mail->mssg, read_string(set, "mssg"));
  return mail;
}

// represent a piece of mail as a storage set
STORAGE_SET *mailStore(MAIL_DATA *mail) {
  // create a new storage set
  STORAGE_SET *set = new_storage_set();
  store_string(set, "sender", mail->sender);
  store_string(set, "time",   mail->time);
  store_string(set, "mssg",   bufferString(mail->mssg));
  return set;
}
```

Now, let's implement the functions to save and load mail using storage sets:

```c
// saves all of our unreceived mail to disk
void save_mail(void) {
  // make a storage set to hold all our mail
  STORAGE_SET *set = new_storage_set();

  // make a list of name:mail pairs, and store it in the set
  STORAGE_SET_LIST *list = new_storage_list();

  // iterate across all of the people who have not received mail, and
  // store their names in the storage list, along with their mail
  HASH_ITERATOR *mail_i = newHashIterator(mail_table);
  const char      *name = NULL;
  LIST            *mail = NULL;
  ITERATE_HASH(name, mail, mail_i) {
    // create a new storage set that holds each name:mail pair,
    // and add it to our list of all name:mail pairs
    STORAGE_SET *one_pair = new_storage_set();
    store_string    (one_pair, "name", name);
    store_list      (one_pair, "mail", gen_store_list(mail, mailStore));
    storage_list_put(list, one_pair);
  } deleteHashIterator(mail_i);

  // make sure we add the list of name:mail pairs we want to save
  store_list(set, "list", list);

  // now, store our set in the mail file, and clean up our mess
  storage_write(set, MAIL_FILE);
  storage_close(set);
}

// loads all of our unreceived mail from disk
void load_mail(void) {
  // parse our storage set
  STORAGE_SET *set = storage_read(MAIL_FILE);

  // make sure the file existed and wasn't empty
  if(set == NULL) return;

  // get the list of all name:mail pairs, and parse each one
  STORAGE_SET_LIST *list = read_list(set, "list");
  STORAGE_SET  *one_pair = NULL;
  while( (one_pair = storage_list_next(list)) != NULL) {
    const char *name = read_string(one_pair, "name");
    LIST       *mail = gen_read_list(read_list(one_pair, "mail"), mailRead);
    hashPut(mail_table, name, mail);
  }

  // Everything is parsed! Now it's time to clean up our mess
  storage_close(set);
}
```

Now, let's update our commands to save mail after sending or receiving:

```c
// In cmd_mail, after sending mail:
send_to_char(ch, "You send a message to %s.\r\n", arg);

// save all unread mail
save_mail();

// In cmd_receive, after receiving mail:
send_to_char(ch, "You receive %d letter%s.\r\n", 
             listSize(mail_list), (listSize(mail_list) == 1 ? "" : "s"));

// update the unread mail in our mail file
save_mail();
```

Finally, update the `init_mail` function to load existing mail:

```c
// boot up the mail module
void init_mail(void) {
  // initialize our mail table
  mail_table = newHashtable();

  // parse any unread mail
  load_mail();

  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}
```

## Auxiliary Data

Auxiliary Data is perhaps the most important part of NakedMud's design. It allows you to add new variables to the various datatypes NakedMud handles within the game (objects, rooms, mobiles, accounts, sockets) without modifying the core data structure files. The biggest advantage is the ability to modularize your code by functionality; all code related to a specific feature - including its variables - can stay in one module. This improves debugging, maintenance, and code distribution.

### Getting Up To Speed

If you've already completed the modules tutorial, you can skip this section.

If you've completed the storage sets tutorial, you'll need to modify your code. The current saving method is inefficient, and we'll address that in this section by using auxiliary data. You'll need to replace your `mail.c` file with the version from appendix A.

### Auxiliary Data Basics

In the storage sets section, we made mail persistent but with an inefficient saving mechanism. Now, we'll attach unread mail directly to character data, allowing us to save only the relevant character data when mail changes.

First, update the headers in `mail.c`:

```c
#include "../handler.h"       // for giving mail to characters
#include "../storage.h"       // for saving/loading auxiliary data
#include "../auxiliary.h"     // for creating new auxiliary data
#include "../world.h"         // for loading offline chars receiving mail
```

Since we'll store mail as auxiliary data, we can remove the mail_table hashtable. Delete these lines from `mail.c`:

```c
// maps charName to a list of mail they have received
HASHTABLE *mail_table = NULL;
```

In `cmd_mail`, replace the mail table handling logic with auxiliary data handling. Here's the updated code for the mail sending functionality:

```c
// create the new piece of mail
MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));

// get a copy of the player, send mail, and save
CHAR_DATA *recv = get_player(arg);
send_to_char(recv, "You have new mail.\r\n");

// let's pull out the character's mail aux data, and add the new piece
MAIL_AUX_DATA *maux = charGetAuxiliaryData(recv, "mail_aux_data");
listPut(maux->mail, mail);
save_player(recv);
  
// get rid of our reference, and extract from game if need be
unreference_player(recv);

// let the character know we've sent the mail
send_to_char(ch, "You send a message to %s.\r\n", arg);
```

And update the `cmd_receive` function to use auxiliary data:

```c
COMMAND(cmd_receive) {
  // Get the character's mail from auxiliary data
  MAIL_AUX_DATA *maux = charGetAuxiliaryData(ch, "mail_aux_data");
  LIST *mail_list = maux->mail;
  
  // Replace the old list with a new one (the old one will be deleted)
  maux->mail = newList();
  
  // Rest of the function remains the same...
```

Now, let's implement the auxiliary data structure and its associated functions. Add this code after the `mailCopy` function:

```c
// Our mail auxiliary data structure.
// Holds a list of all the unreceived mail a person has
typedef struct {
  LIST *mail; // our list of unread mail
} MAIL_AUX_DATA;

// Create a new instance of mail auxiliary data
MAIL_AUX_DATA *newMailAuxData(void) {
  MAIL_AUX_DATA *data = malloc(sizeof(MAIL_AUX_DATA));
  data->mail = newList();
  return data;
}

// Delete a character's mail auxiliary data
void deleteMailAuxData(MAIL_AUX_DATA *data) {
  if(data->mail) deleteListWith(data->mail, deleteMail);
  free(data);
}

// Copy one mail auxiliary data to another
void mailAuxDataCopyTo(MAIL_AUX_DATA *from, MAIL_AUX_DATA *to) {
  if(to->mail)   deleteListWith(to->mail, deleteMail);
  if(from->mail) to->mail = listCopyWith(from->mail, mailCopy);
  else           to->mail = newList();
}

// Return a copy of a mail auxiliary data
MAIL_AUX_DATA *mailAuxDataCopy(MAIL_AUX_DATA *data) {
  MAIL_AUX_DATA *newdata = newMailAuxData();
  mailAuxDataCopyTo(data, newdata);
  return newdata;
}

// Parse a mail auxiliary data from a storage set
MAIL_AUX_DATA *mailAuxDataRead(STORAGE_SET *set) {
  MAIL_AUX_DATA *data = malloc(sizeof(MAIL_AUX_DATA));
  data->mail = gen_read_list(read_list(set, "mail"), mailRead);
  return data;
}

// Represent a mail auxiliary data as a storage set
STORAGE_SET *mailAuxDataStore(MAIL_AUX_DATA *data) {
  STORAGE_SET *set = new_storage_set();
  store_list(set, "mail", gen_store_list(data->mail, mailStore));
  return set;
}
```

Finally, update the `init_mail` function to install the auxiliary data:

```c
// boot up the mail module
void init_mail(void) {
  // install our auxiliary data
  auxiliariesInstall("mail_aux_data",
                     newAuxiliaryFuncs(AUXILIARY_TYPE_CHAR,
                                    newMailAuxData, deleteMailAuxData,
                                    mailAuxDataCopyTo, mailAuxDataCopy,
                                    mailAuxDataStore, mailAuxDataRead));
  
  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}
```

## Summary

In this section, we've learned how to use auxiliary data to efficiently manage character-specific data. By attaching mail directly to characters using auxiliary data, we've made our mail system more efficient and easier to maintain.

## Conclusion

Throughout this manual, we've covered the basics of modules, storage sets, and auxiliary data - three fundamental aspects of NakedMud. With this knowledge, you should be well-equipped to extend NakedMud with new game content.

# Appendices

## Appendix A: Mail Module Code, First Draft

### module.mk
```makefile
# include all of the source files contained in this module
SRC += mail/mail.c
```

### mail.h
```c
#ifndef MAIL_H
#define MAIL_H

#include "mud.h"

// Our mail data structure
typedef struct mail_data MAIL_DATA;
struct mail_data {
  char   *sender;  // name of the character who sent this mail
  char   *time;    // the time it was sent at
  BUFFER *mssg;    // the accompanying message
};

// Function prototypes
void init_mail(void);

// Mail creation and deletion
MAIL_DATA *newMail(CHAR_DATA *sender, const char *mssg);
void deleteMail(MAIL_DATA *mail);

// Command handlers
COMMAND(cmd_mail);
COMMAND(cmd_receive);

#endif // MAIL_H
```

### mail.c
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mud.h"
#include "utils.h"
#include "character.h"
#include "save.h"
#include "object.h"
#include "handler.h"
#include "editor/editor.h"
#include "storage.h"
#include "auxiliary.h"
#include "world.h"
#include "mail.h"

// maps charName to a list of mail they have received
HASHTABLE *mail_table = NULL;

// create a new piece of mail
MAIL_DATA *newMail(CHAR_DATA *sender, const char *mssg) {
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->sender = strdup(charGetName(sender));
  mail->time   = strdup(get_time());
  mail->mssg   = newBuffer(strlen(mssg));
  bufferCat(mail->mssg, mssg);
  return mail;
}

// free all of the memory that was allocated to make this piece of mail
void deleteMail(MAIL_DATA *mail) {
  if(mail->sender) free(mail->sender);
  if(mail->time)   free(mail->time);
  if(mail->mssg)   deleteBuffer(mail->mssg);
  free(mail);
}

// mails a message to the specified person
COMMAND(cmd_mail) {
  // make sure the character exists
  if(!char_exists(arg))
    send_to_char(ch, "No one named %s is registered on %s.\r\n",
                 arg, "<insert mud name here>");
  // make sure we have a socket - we'll need access to its notepad
  else if(!charGetSocket(ch))
    send_to_char(ch, "Only characters with sockets can send mail!\r\n");
  // make sure our notepad is not empty
  else if(!*bufferString(socketGetNotepad(charGetSocket(ch))))
    send_to_char(ch, "Your notepad is empty. "
                 "First, try writing something with {cwrite{n.\r\n");
  // the character exists. Let's parse the items and send the mail
  else {
    MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));
    
    // see if the receiver already has a mail list
    LIST *mssgs = hashGet(mail_table, arg);
    
    // if they don't, create one and add it to the hashtable
    if(mssgs == NULL) {
      mssgs = newList();
      hashPut(mail_table, arg, mssgs);
    }

    // add the new mail to our mail list
    listPut(mssgs, mail);

    // let the character know we've sent the mail
    send_to_char(ch, "You send a message to %s.\r\n", arg);
  }
}

// checks to see if the character has any mail
COMMAND(cmd_receive) {
  // Remove the character's mail list from our mail table
  LIST *mail_list = hashRemove(mail_table, charGetName(ch));

  // make sure the list exists
  if(mail_list == NULL || listSize(mail_list) == 0)
    send_to_char(ch, "You have no new mail.\r\n");
  // hand over all of the mail
  else {
    // go through each piece of mail, make an object for it, 
    // and transfer the new object to us
    LIST_ITERATOR *mail_i = newListIterator(mail_list);
    MAIL_DATA *mail = NULL;
    ITERATE_LIST(mail, mail_i) {
      OBJ_DATA *obj = newObj();
      objSetName(obj, "a letter");
      objSetKeywords(obj, "letter, mail");
      objSetRdesc(obj, "A letter is here.");
      objSetMultiName(obj, "A stack of %d letters");
      objSetMultiRdesc(obj, "A stack of %d letters are here.");
      bprintf(objGetDescBuffer(obj),
             "Sender   : %s\r\n"
             "Date sent: %s\r\n"
             "%s", mail->sender, mail->time, bufferString(mail->mssg));
      
      // give the object to the character
      obj_to_game(obj);
      obj_to_char(obj, ch);
    } deleteListIterator(mail_i);

    // let the character know how much mail they received
    send_to_char(ch, "You receive %d letter%s.\r\n", 
                listSize(mail_list), (listSize(mail_list) == 1 ? "" : "s"));
  }
  
  // delete the mail list, and all of its contents
  if(mail_list != NULL) deleteListWith(mail_list, deleteMail);
}

// boot up the mail module
void init_mail(void) {
  // initialize our mail table
  mail_table = newHashtable();

  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}
```

## Appendix B: Mail Module Code, Second Draft

### module.mk
```makefile
# include all of the source files contained in this module
SRC += mail/mail.c
```

### mail.h
```c
#ifndef MAIL_H
#define MAIL_H
// this function should be called when the MUD first boots up.
// calling it will initialize the mail module for use.
void init_mail(void);
#endif // MAIL_H
```

### mail.c
```c
// include all the header files we will need from the MUD core
#include "../mud.h"
#include "../utils.h"         // for get_time()
#include "../character.h"     // for handling characters sending mail
#include "../save.h"          // for char_exists()
#include "../object.h"        // for creating mail objects
#include "../handler.h"       // for giving mail to characters
#include "../storage.h"       // for saving/loading mail

// include headers from other modules that we require
#include "../editor/editor.h" // for access to sockets' notepads

// include the headers for this module
#include "mail.h"

// this is the file we will save all unreceived mail in, when the mud is down
#define MAIL_FILE "../lib/misc/mail"

// maps charName to a list of mail they have received
HASHTABLE *mail_table = NULL;

typedef struct {
  char   *sender;  // name of the character who sent this mail
  char   *time;    // the time it was sent at
  BUFFER *mssg;    // the accompanying message
} MAIL_DATA;

// create a new piece of mail
MAIL_DATA *newMail(CHAR_DATA *sender, const char *mssg) {
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->sender = strdup(charGetName(sender));
  mail->time   = strdup(get_time());
  mail->mssg   = newBuffer(strlen(mssg));
  bufferCat(mail->mssg, mssg);
  return mail;
}

// free all of the memory that was allocated to make this piece of mail
void deleteMail(MAIL_DATA *mail) {
  if(mail->sender) free(mail->sender);
  if(mail->time)   free(mail->time);
  if(mail->mssg)   deleteBuffer(mail->mssg);
  free(mail);
}

// parse a piece of mail from a storage set
MAIL_DATA *mailRead(STORAGE_SET *set) {
  // allocate some memory for the mail
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->mssg      = newBuffer(1);

  // read in all of our values
  mail->sender = strdup(read_string(set, "sender"));
  mail->time   = strdup(read_string(set, "time"));
  bufferCat(mail->mssg, read_string(set, "mssg"));
  return mail;
}

// represent a piece of mail as a storage set
STORAGE_SET *mailStore(MAIL_DATA *mail) {
  // create a new storage set
  STORAGE_SET *set = new_storage_set();
  store_string(set, "sender", mail->sender);
  store_string(set, "time",   mail->time);
  store_string(set, "mssg",   bufferString(mail->mssg));
  return set;
}

// saves all of our unreceived mail to disk
void save_mail(void) {
  // make a storage set to hold all our mail
  STORAGE_SET *set = new_storage_set();

  // make a list of name:mail pairs, and store it in the set
  STORAGE_SET_LIST *list = new_storage_list();

  // iterate across all of the people who have not received mail, and
  // store their names in the storage list, along with their mail
  HASH_ITERATOR *mail_i = newHashIterator(mail_table);
  const char      *name = NULL;
  LIST            *mail = NULL;
  ITERATE_HASH(name, mail, mail_i) {
    // create a new storage set that holds each name:mail pair,
    // and add it to our list of all name:mail pairs
    STORAGE_SET *one_pair = new_storage_set();
    store_string    (one_pair, "name", name);
    store_list      (one_pair, "mail", gen_store_list(mail, mailStore));
    storage_list_put(list, one_pair);
  } deleteHashIterator(mail_i);

  // make sure we add the list of name:mail pairs we want to save
  store_list(set, "list", list);

  // now, store our set in the mail file, and clean up our mess
  storage_write(set, MAIL_FILE);
  storage_close(set);
}

// loads all of our unreceived mail from disk
void load_mail(void) {
  // parse our storage set
  STORAGE_SET *set = storage_read(MAIL_FILE);

  // make sure the file existed and wasn't empty
  if(set == NULL) return;

  // get the list of all name:mail pairs, and parse each one
  STORAGE_SET_LIST *list = read_list(set, "list");
  STORAGE_SET  *one_pair = NULL;
  while( (one_pair = storage_list_next(list)) != NULL) {
    const char *name = read_string(one_pair, "name");
    LIST       *mail = gen_read_list(read_list(one_pair, "mail"), mailRead);
    hashPut(mail_table, name, mail);
  }

  // Everything is parsed! Now it's time to clean up our mess
  storage_close(set);
}

// mails a message to the specified person
COMMAND(cmd_mail) {
  // make sure the character exists
  if(!char_exists(arg))
    send_to_char(ch, "No one named %s is registered on %s.\r\n",
                 arg, "<insert mud name here>");
  // make sure we have a socket - we'll need access to its notepad
  else if(!charGetSocket(ch))
    send_to_char(ch, "Only characters with sockets can send mail!\r\n");
  // make sure our notepad is not empty
  else if(!*bufferString(socketGetNotepad(charGetSocket(ch))))
    send_to_char(ch, "Your notepad is empty. "
                 "First, try writing something with {cwrite{n.\r\n");
  // the character exists. Let's parse the items and send the mail
  else {
    MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));
    
    // see if the receiver already has a mail list
    LIST *mssgs = hashGet(mail_table, arg);
    
    // if they don't, create one and add it to the hashtable
    if(mssgs == NULL) {
      mssgs = newList();
      hashPut(mail_table, arg, mssgs);
    }

    // add the new mail to our mail list
    listPut(mssgs, mail);

    // let the character know we've sent the mail
    send_to_char(ch, "You send a message to %s.\r\n", arg);
    
    // save all unread mail
    save_mail();
  }
}

// checks to see if the character has any mail
COMMAND(cmd_receive) {
  // Remove the character's mail list from our mail table
  LIST *mail_list = hashRemove(mail_table, charGetName(ch));

  // make sure the list exists
  if(mail_list == NULL || listSize(mail_list) == 0)
    send_to_char(ch, "You have no new mail.\r\n");
  // hand over all of the mail
  else {
    // go through each piece of mail, make an object for it, 
    // and transfer the new object to us
    LIST_ITERATOR *mail_i = newListIterator(mail_list);
    MAIL_DATA *mail = NULL;
    ITERATE_LIST(mail, mail_i) {
      OBJ_DATA *obj = newObj();
      objSetName(obj, "a letter");
      objSetKeywords(obj, "letter, mail");
      objSetRdesc(obj, "A letter is here.");
      objSetMultiName(obj, "A stack of %d letters");
      objSetMultiRdesc(obj, "A stack of %d letters are here.");
      bprintf(objGetDescBuffer(obj),
             "Sender   : %s\r\n"
             "Date sent: %s\r\n"
             "%s", mail->sender, mail->time, bufferString(mail->mssg));
      
      // give the object to the character
      obj_to_game(obj);
      obj_to_char(obj, ch);
    } deleteListIterator(mail_i);

    // let the character know how much mail they received
    send_to_char(ch, "You receive %d letter%s.\r\n", 
                listSize(mail_list), (listSize(mail_list) == 1 ? "" : "s"));
    
    // update the unread mail in our mail file
    save_mail();
  }
  
  // delete the mail list, and all of its contents
  if(mail_list != NULL) deleteListWith(mail_list, deleteMail);
}

// boot up the mail module
void init_mail(void) {
  // initialize our mail table
  mail_table = newHashtable();
  
  // load any existing mail
  load_mail();

  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}
```

## Appendix C: Mail Module Code, Third Draft

### module.mk
```makefile
# include all of the source files contained in this module
SRC += mail/mail.c
```

### mail.h
```c
#ifndef MAIL_H
#define MAIL_H
// this function should be called when the MUD first boots up.
// calling it will initialize the mail module for use.
void init_mail(void);
#endif // MAIL_H
```

### mail.c
```c
// include all the header files we will need from the MUD core
#include "../mud.h"
#include "../utils.h"         // for get_time()
#include "../character.h"     // for handling characters sending mail
#include "../save.h"          // for char_exists()
#include "../object.h"        // for creating mail objects
#include "../handler.h"       // for giving mail to characters
#include "../storage.h"       // for saving/loading auxiliary data
#include "../auxiliary.h"     // for creating new auxiliary data
#include "../world.h"         // for loading offline chars receiving mail

// include headers from other modules that we require
#include "../editor/editor.h" // for access to sockets' notepads

// include the headers for this module
#include "mail.h"

typedef struct {
  char   *sender;  // name of the character who sent this mail
  char   *time;    // the time it was sent at
  BUFFER *mssg;    // the accompanying message
} MAIL_DATA;

// create a new piece of mail
MAIL_DATA *newMail(CHAR_DATA *sender, const char *mssg) {
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->sender = strdup(charGetName(sender));
  mail->time   = strdup(get_time());
  mail->mssg   = newBuffer(strlen(mssg));
  bufferCat(mail->mssg, mssg);
  return mail;
}

// free all of the memory that was allocated to make this piece of mail
void deleteMail(MAIL_DATA *mail) {
  if(mail->sender) free(mail->sender);
  if(mail->time)   free(mail->time);
  if(mail->mssg)   deleteBuffer(mail->mssg);
  free(mail);
}

// parse a piece of mail from a storage set
MAIL_DATA *mailRead(STORAGE_SET *set) {
  // allocate some memory for the mail
  MAIL_DATA *mail = malloc(sizeof(MAIL_DATA));
  mail->mssg      = newBuffer(1);

  // read in all of our values
  mail->sender = strdup(read_string(set, "sender"));
  mail->time   = strdup(read_string(set, "time"));
  bufferCat(mail->mssg, read_string(set, "mssg"));
  return mail;
}

// represent a piece of mail as a storage set
STORAGE_SET *mailStore(MAIL_DATA *mail) {
  // create a new storage set
  STORAGE_SET *set = new_storage_set();
  store_string(set, "sender", mail->sender);
  store_string(set, "time",   mail->time);
  store_string(set, "mssg",   bufferString(mail->mssg));
  return set;
}

// copy a piece of mail. This will be needed by our auxiliary
// data copy functions
MAIL_DATA *mailCopy(MAIL_DATA *mail) {
  MAIL_DATA *newmail = malloc(sizeof(MAIL_DATA));
  newmail->sender = strdup(mail->sender);
  newmail->time   = strdup(mail->time);
  newmail->mssg   = bufferCopy(mail->mssg);
  return newmail;
}

// our mail auxiliary data. 
// Holds a list of all the unreceived mail a person has
typedef struct {
  LIST *mail; // our list of unread mail
} MAIL_AUX_DATA;

// create a new instance of mail aux data, for us to put onto a character
MAIL_AUX_DATA *newMailAuxData(void) {
  MAIL_AUX_DATA *data = malloc(sizeof(MAIL_AUX_DATA));
  data->mail = newList();
  return data;
}

// delete a character's mail aux data
void deleteMailAuxData(MAIL_AUX_DATA *data) {
  if(data->mail) deleteListWith(data->mail, deleteMail);
  free(data);
}

// copy one mail aux data to another
void mailAuxDataCopyTo(MAIL_AUX_DATA *from, MAIL_AUX_DATA *to) {
  if(to->mail)   deleteListWith(to->mail, deleteMail);
  if(from->mail) to->mail = listCopyWith(from->mail, mailCopy);
  else           to->mail = newList();
}

// return a copy of a mail aux data
MAIL_AUX_DATA *mailAuxDataCopy(MAIL_AUX_DATA *data) {
  MAIL_AUX_DATA *newdata = newMailAuxData();
  mailAuxDataCopyTo(data, newdata);
  return newdata;
}

// parse a mail aux data from a storage set
MAIL_AUX_DATA *mailAuxDataRead(STORAGE_SET *set) {
  MAIL_AUX_DATA *data = malloc(sizeof(MAIL_AUX_DATA));
  data->mail          = gen_read_list(read_list(set, "mail"), mailRead);
  return data;
}

// represent a mail aux data as a storage set
STORAGE_SET *mailAuxDataStore(MAIL_AUX_DATA *data) {
  STORAGE_SET *set = new_storage_set();
  store_list(set, "mail", gen_store_list(data->mail, mailStore));
  return set;
}

// mails a message to the specified person
COMMAND(cmd_mail) {
  // make sure the character exists
  if(!char_exists(arg))
    send_to_char(ch, "No one named %s is registered on %s.\r\n",
                 arg, "<insert mud name here>");
  // make sure we have a socket - we'll need access to its notepad
  else if(!charGetSocket(ch))
    send_to_char(ch, "Only characters with sockets can send mail!\r\n");
  // make sure our notepad is not empty
  else if(!*bufferString(socketGetNotepad(charGetSocket(ch))))
    send_to_char(ch, "Your notepad is empty. "
                 "First, try writing something with {cwrite{n.\r\n");
  // the character exists. Let's parse the items and send the mail
  else {
    // create the new piece of mail
    MAIL_DATA *mail = newMail(ch, bufferString(socketGetNotepad(charGetSocket(ch))));

    // get a copy of the player, send mail, and save
    CHAR_DATA *recv = get_player(arg);
    send_to_char(recv, "You have new mail.\r\n");
    
    // let's pull out the character's mail aux data, and add the new piece
    MAIL_AUX_DATA *maux = charGetAuxiliaryData(recv, "mail_aux_data");
    listPut(maux->mail, mail);
    save_player(recv);
      
    // get rid of our reference, and extract from game if need be
    unreference_player(recv);      

    // let the character know we've sent the mail
    send_to_char(ch, "You send a message to %s.\r\n", arg);
  }
}

// checks to see if the character has any mail
COMMAND(cmd_receive) {
  // Remove the character's mail list from our mail table
  MAIL_AUX_DATA *maux = charGetAuxiliaryData(ch, "mail_aux_data");
  LIST *mail_list     = maux->mail;
  // replace our old list with a new one. Our old one will be deleted soon
  maux->mail = newList();

  // make sure the list exists
  if(mail_list == NULL || listSize(mail_list) == 0)
    send_to_char(ch, "You have no new mail.\r\n");
  // hand over all of the mail
  else {
    // go through each piece of mail, make an object for it, 
    // and transfer the new object to us
    LIST_ITERATOR *mail_i = newListIterator(mail_list);
    MAIL_DATA *mail = NULL;
    ITERATE_LIST(mail, mail_i) {
      OBJ_DATA *obj = newObj();
      BUFFER   *desc = newBuffer(1);
      objSetName(obj, "a letter");
      objSetKeywords(obj, "letter, mail");
      objSetRdesc(obj, "A letter is here.");
      objSetMultiName(obj, "A stack of %d letters");
      objSetMultiRdesc(obj, "A stack of %d letters are here.");

      // make our description
      bprintf(desc, 
             "Sender   : %s\r\n"
             "Date sent: %s\r\n"
             "%s", mail->sender, mail->time, bufferString(mail->mssg));
      objSetDesc(obj, bufferString(desc));
      
      // clean up our mess and give the object to the character
      deleteBuffer(desc);
      obj_to_game(obj);
      obj_to_char(obj, ch);
    } deleteListIterator(mail_i);

    // let the character know how much mail they received
    send_to_char(ch, "You receive %d letter%s.\r\n", 
                listSize(mail_list), (listSize(mail_list) == 1 ? "" : "s"));
  }
  
  // delete the mail list, and all of its contents
  if(mail_list != NULL) deleteListWith(mail_list, deleteMail);
}

// boot up the mail module
void init_mail(void) {
  // install our auxiliary data
  auxiliariesInstall("mail_aux_data",
             newAuxiliaryFuncs(AUXILIARY_TYPE_CHAR,
                       newMailAuxData, deleteMailAuxData,
                       mailAuxDataCopyTo, mailAuxDataCopy,
                       mailAuxDataStore, mailAuxDataRead));

  // add all of the commands that come with this module
  add_cmd("mail", NULL, cmd_mail, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
  add_cmd("receive", NULL, cmd_receive, POS_STANDING, POS_FLYING,
          "player", FALSE, TRUE);
}
```
