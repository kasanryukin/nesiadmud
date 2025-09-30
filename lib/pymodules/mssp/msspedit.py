"""
msspedit is a set of tools for editing MSSP configuration online. Msspedit requires that
olc2 be installed.
"""
import olc
from enum import Enum
from mudsys import add_cmd

class Msspedit(Enum):
    """
    Enumeration class for holding the menu selections for the OLC MSSP
    configuration editor.
    """
    contact = 1
    website = 2
    family = 3
    genre = 4
    gameplay = 5
    status = 6
    gamesystem = 7
    subgenre = 8
    language = 9
    location = 10
    created = 11
    minimum_age = 12
    intermud = 13

def msspedit_menu(sock, mssp_config):
    """
    Creates the menu for the OLC for MSSP configuration editing.

    :param sock: the player socket editing the MSSP config
    :param mssp_config: the MSSPConfig object being edited
    :return: None
    """
    sock.send("{y[{cMSSP Configuration{y]\r\n"
              "{g 1) Contact      : {c%s\r\n"
              "{g 2) Website      : {c%s\r\n"
              "{g 3) Family       : {c%s\r\n"
              "{g 4) Genre        : {c%s\r\n"
              "{g 5) Gameplay     : {c%s\r\n"
              "{g 6) Status       : {c%s\r\n"
              "{g 7) Game System  : {c%s\r\n"
              "{g 8) Sub-genre    : {c%s\r\n"
              "{g 9) Language     : {c%s\r\n"
              "{g10) Location     : {c%s\r\n"
              "{g11) Created      : {c%s\r\n"
              "{g12) Minimum Age  : {c%d\r\n"
              "{g13) Intermud     : {c%s\r\n"
              "\r\n"
              "{gCore settings (NAME, PORT, SCREENWIDTH) are pulled from mudsettings"
              % (mssp_config.contact, mssp_config.website, mssp_config.family,
                 mssp_config.genre, mssp_config.gameplay, mssp_config.status,
                 mssp_config.gamesystem, mssp_config.subgenre, mssp_config.language,
                 mssp_config.location, mssp_config.created, mssp_config.minimum_age,
                 "yes" if mssp_config.intermud else "no"))

def msspedit_chooser(sock, mssp_config, option):
    if option == '1':
        sock.send("Contact email address: ")
        return Msspedit.contact.value
    elif option == '2':
        sock.send("Website URL: ")
        return Msspedit.website.value
    elif option == '3':
        sock.send("MUD family (Custom, LP, Diku, etc.): ")
        return Msspedit.family.value
    elif option == '4':
        sock.send("Primary genre (Fantasy, Sci-Fi, Modern, etc.): ")
        return Msspedit.genre.value
    elif option == '5':
        sock.send("Gameplay style (Roleplaying, Hack and Slash, etc.): ")
        return Msspedit.gameplay.value
    elif option == '6':
        sock.send("MUD status (Live, Beta, Alpha, etc.): ")
        return Msspedit.status.value
    elif option == '7':
        sock.send("Game system (Custom, D&D, etc.): ")
        return Msspedit.gamesystem.value
    elif option == '8':
        sock.send("Sub-genre (High Fantasy, Space Opera, etc.): ")
        return Msspedit.subgenre.value
    elif option == '9':
        sock.send("Primary language: ")
        return Msspedit.language.value
    elif option == '10':
        sock.send("Server location (country/region): ")
        return Msspedit.location.value
    elif option == '11':
        sock.send("Year MUD was created: ")
        return Msspedit.created.value
    elif option == '12':
        sock.send("Minimum player age: ")
        return Msspedit.minimum_age.value
    elif option == '13':
        sock.send("Intermud support (yes/no): ")
        return Msspedit.intermud.value
    else:
        return -1

def msspedit_parser(sock, mssp_config, choice, arg):
    if choice == Msspedit.contact.value:
        mssp_config.contact = arg
        return True
    elif choice == Msspedit.website.value:
        mssp_config.website = arg
        return True
    elif choice == Msspedit.family.value:
        mssp_config.family = arg
        return True
    elif choice == Msspedit.genre.value:
        mssp_config.genre = arg
        return True
    elif choice == Msspedit.gameplay.value:
        mssp_config.gameplay = arg
        return True
    elif choice == Msspedit.status.value:
        mssp_config.status = arg
        return True
    elif choice == Msspedit.gamesystem.value:
        mssp_config.gamesystem = arg
        return True
    elif choice == Msspedit.subgenre.value:
        mssp_config.subgenre = arg
        return True
    elif choice == Msspedit.language.value:
        mssp_config.language = arg
        return True
    elif choice == Msspedit.location.value:
        mssp_config.location = arg
        return True
    elif choice == Msspedit.created.value:
        mssp_config.created = arg
        return True
    elif choice == Msspedit.minimum_age.value:
        try:
            age = int(arg)
            if age > 0:
                mssp_config.minimum_age = age
                return True
        except:
            pass
        return False
    elif choice == Msspedit.intermud.value:
        if arg.lower() in ['yes', 'y', '1', 'true', 'on']:
            mssp_config.intermud = True
            return True
        elif arg.lower() in ['no', 'n', '0', 'false', 'off']:
            mssp_config.intermud = False
            return True
        return False
    else:
        return False

def cmd_msspedit(ch, cmd, arg):
    """
    This starts the MSSP configuration editor OLC process, allowing you to edit
    MSSP server information for the mud. The minimum permissions required for this is admin.

    syntax: msspedit
    """
    from .mssp import mssp_config_data, save_mssp_config
    
    if mssp_config_data is None:
        ch.send("MSSP configuration not loaded. Please contact an administrator.")
        return
    
    ch.send("Editing MSSP Configuration")
    olc.do_olc(ch.sock, msspedit_menu, msspedit_chooser, msspedit_parser, 
               lambda config: save_mssp_config(), mssp_config_data)

add_cmd("msspedit", None, cmd_msspedit, "admin", False)
