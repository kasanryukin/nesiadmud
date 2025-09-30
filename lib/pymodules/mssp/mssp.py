"""
MSSP (Mud Server Status Protocol) implementation for NakedMud.

This module handles MSSP requests via the receive_iac hook and automatically
responds with server status information.
"""
import mud, char, hooks, mudsys, storage
import time
import struct
import os

# MSSP telnet option codes
MSSP = 70  # MSSP telnet option
IAC = 255  # Interpret As Command
SB = 250   # Subnegotiation Begin
SE = 240   # Subnegotiation End
MSSP_VAR = 1  # Variable marker
MSSP_VAL = 2  # Value marker

class MSSPData:
    """MSSP server data configuration"""
    
    def __init__(self):
        # Initialize with defaults, then pull from mudsettings
        self.data = {
            'NAME': 'NakedMud',
            'PLAYERS': '0',
            'UPTIME': '0',
            'CODEBASE': 'NakedMud 4.0',
            'CONTACT': 'admin@nakedmud.org',
            'CREATED': '2004',
            'LANGUAGE': 'English',
            'LOCATION': 'Canada',
            'MINIMUM_AGE': '13',
            'WEBSITE': 'http://www.nakedmud.org',
            'FAMILY': 'Custom',
            'GENRE': 'Fantasy',
            'GAMEPLAY': 'Roleplaying',
            'STATUS': 'Live',
            'GAMESYSTEM': 'Custom',
            'INTERMUD': '0',
            'SUBGENRE': 'High Fantasy'
        }
        self.start_time = time.time()
        self.load_from_mudsettings()
    
    def load_from_mudsettings(self):
        """Load MSSP data from core mudsettings and config file"""
        try:
            # Pull mud name from settings
            mud_name = mudsys.sys_getval("mud_name")
            if mud_name and mud_name.strip():
                self.data['NAME'] = mud_name.strip()
            
            # Pull listening port for potential use
            listening_port = mudsys.sys_getval("listening_port")
            if listening_port and listening_port.strip():
                self.data['PORT'] = listening_port.strip()
            
            # Pull screen width for client compatibility info
            screen_width = mudsys.sys_getval("screen_width")
            if screen_width and screen_width.strip():
                self.data['SCREENWIDTH'] = screen_width.strip()
            
            # Load additional config from global MSSP config instance
            global mssp_config_data
            if mssp_config_data:
                config_data = mssp_config_data.to_dict()
                self.data.update(config_data)
            
        except Exception as e:
            # Silently ignore errors loading from mudsettings
            pass
    
    def update_dynamic_data(self):
        """Update dynamic MSSP data like player count and uptime"""
        # Get current player count using char.char_list()
        player_count = 0
        for ch in char.char_list():
            # Only count player characters (those with sockets/accounts)
            if ch.is_pc:
                player_count += 1
        
        self.data['PLAYERS'] = str(player_count)
        
        # Calculate uptime in seconds
        uptime = int(time.time() - self.start_time)
        self.data['UPTIME'] = str(uptime)
    
    def generate_mssp_response(self):
        """Generate MSSP response data"""
        self.update_dynamic_data()
        
        response = bytearray()
        response.extend([IAC, SB, MSSP])
        
        for var, val in self.data.items():
            response.append(MSSP_VAR)
            response.extend(var.encode('utf-8'))
            response.append(MSSP_VAL)
            response.extend(val.encode('utf-8'))
        
        response.extend([IAC, SE])
        return bytes(response)

class MSSPConfig:
    """MSSP Configuration class using StorageSet"""
    
    def __init__(self, storeSet=None):
        # Default values
        self.contact = "admin@nakedmud.org"
        self.website = "http://www.nakedmud.org"
        self.family = "Custom"
        self.genre = "Fantasy"
        self.gameplay = "Roleplaying"
        self.status = "Live"
        self.gamesystem = "Custom"
        self.subgenre = "High Fantasy"
        self.language = "English"
        self.location = "Canada"
        self.created = "2004"
        self.minimum_age = 13
        self.intermud = False
        
        # Load from StorageSet if provided
        if storeSet is not None:
            self.contact = storeSet.readString("contact")
            self.website = storeSet.readString("website")
            self.family = storeSet.readString("family")
            self.genre = storeSet.readString("genre")
            self.gameplay = storeSet.readString("gameplay")
            self.status = storeSet.readString("status")
            self.gamesystem = storeSet.readString("gamesystem")
            self.subgenre = storeSet.readString("subgenre")
            self.language = storeSet.readString("language")
            self.location = storeSet.readString("location")
            self.created = storeSet.readString("created")
            self.minimum_age = storeSet.readInt("minimum_age")
            self.intermud = storeSet.readBool("intermud")
    
    def store(self):
        """Store configuration to StorageSet"""
        set = storage.StorageSet()
        set.storeString("contact", self.contact)
        set.storeString("website", self.website)
        set.storeString("family", self.family)
        set.storeString("genre", self.genre)
        set.storeString("gameplay", self.gameplay)
        set.storeString("status", self.status)
        set.storeString("gamesystem", self.gamesystem)
        set.storeString("subgenre", self.subgenre)
        set.storeString("language", self.language)
        set.storeString("location", self.location)
        set.storeString("created", self.created)
        set.storeInt("minimum_age", self.minimum_age)
        set.storeBool("intermud", self.intermud)
        return set
    
    def to_dict(self):
        """Convert to dictionary for MSSP response"""
        return {
            'CONTACT': self.contact,
            'WEBSITE': self.website,
            'FAMILY': self.family,
            'GENRE': self.genre,
            'GAMEPLAY': self.gameplay,
            'STATUS': self.status,
            'GAMESYSTEM': self.gamesystem,
            'SUBGENRE': self.subgenre,
            'LANGUAGE': self.language,
            'LOCATION': self.location,
            'CREATED': self.created,
            'MINIMUM_AGE': str(self.minimum_age),
            'INTERMUD': '1' if self.intermud else '0'
        }

def load_mssp_config():
    """Load MSSP configuration from StorageSet file - similar to load_socials()"""
    global mssp_config_data
    try:
        if os.path.exists(__mssp_config_file__):
            storeSet = storage.StorageSet(__mssp_config_file__)
            mssp_config_data = MSSPConfig(storeSet=storeSet)
            storeSet.close()
        else:
            # Use defaults if no config file exists
            mssp_config_data = MSSPConfig()
    except Exception as e:
        print(f"Error loading MSSP config: {e}")
        # Use defaults on error
        mssp_config_data = MSSPConfig()

def save_mssp_config():
    """Save MSSP configuration to StorageSet file - similar to save_socials()"""
    global mssp_config_data, mssp_data
    if mssp_config_data:
        config_set = mssp_config_data.store()
        config_set.write(__mssp_config_file__)
        config_set.close()
        # Reload the MSSP data to pick up changes
        mssp_data.load_from_mudsettings()

# Configuration file path
__mssp_config_file__ = "misc/mssp-config"

def ensure_mssp_config_file():
    """Ensure MSSP config file exists, copy from default if not"""
    if not os.path.exists(__mssp_config_file__):
        # Get the directory where this module is located
        module_dir = os.path.dirname(__file__)
        default_mssp = os.path.join(module_dir, "default.mssp")
        
        if os.path.exists(default_mssp):
            # Create misc directory if it doesn't exist
            os.makedirs(os.path.dirname(__mssp_config_file__), exist_ok=True)
            
            # Manual file copy
            try:
                with open(default_mssp, 'r') as src:
                    content = src.read()
                # Write directly to file - we're already in mudlib directory
                with open(__mssp_config_file__, 'w') as dst:
                    dst.write(content)
                print(f"Created {__mssp_config_file__} from default template")
            except Exception as e:
                print(f"Error creating MSSP config file: {e}")
        else:
            print(f"Warning: Neither {__mssp_config_file__} nor {default_mssp} exists")

# Global MSSP config instance
mssp_config_data = None

# Initialize config file and load configuration on module load
ensure_mssp_config_file()
load_mssp_config()

# Global MSSP data instance
mssp_data = MSSPData()

def handle_receive_iac(info):
    """Hook handler for receive_iac - detects and responds to MSSP requests"""
    try:
        # Parse the hook info to get socket and IAC sequence
        sock, iac_bytes = hooks.parse_info(info)
        
        # Check for MSSP negotiation: IAC WILL MSSP (255 251 70)
        if (len(iac_bytes) >= 3 and 
            iac_bytes[0] == IAC and 
            iac_bytes[1] == 251 and  # WILL
            iac_bytes[2] == MSSP):
            
            # Send IAC DO MSSP (255 253 70)
            response = bytes([IAC, 253, MSSP])  # DO MSSP
            sock.send_binary(response)
            sock.bust_prompt()
            return
            
        # Check for MSSP request: IAC DO MSSP (255 253 70)
        if (len(iac_bytes) >= 3 and 
            iac_bytes[0] == IAC and 
            iac_bytes[1] == 253 and  # DO
            iac_bytes[2] == MSSP):

            # Update dynamic data before sending
            mssp_data.update_dynamic_data()
            # Generate and send full MSSP response
            response = mssp_data.generate_mssp_response()
            sock.send_binary(response)
            sock.bust_prompt()
            return
            
        # Check if this is an MSSP subnegotiation: IAC SB MSSP IAC SE
        if (len(iac_bytes) >= 5 and 
            iac_bytes[0] == IAC and 
            iac_bytes[1] == SB and 
            iac_bytes[2] == MSSP and 
            iac_bytes[-2] == IAC and 
            iac_bytes[-1] == SE):
            
            print("MSSP subnegotiation received, sending response")
            
            # Generate and send MSSP response
            response = mssp_data.generate_mssp_response()
            
            # Send response back to client
            # Convert bytes to string for socket output
            response_str = response.decode('latin1')
            sock.send_raw(response_str)
            
            
    except Exception as e:
        pass  # Silently ignore MSSP errors to avoid spam

def configure_mssp(name=None, contact=None, website=None, **kwargs):
    """Configure MSSP data - can be called from startup scripts or to reload from mudsettings"""
    global mssp_data
    
    # Reload from mudsettings first
    mssp_data.load_from_mudsettings()
    
    # Then apply any direct overrides
    if name:
        mssp_data.data['NAME'] = name
    if contact:
        mssp_data.data['CONTACT'] = contact
    if website:
        mssp_data.data['WEBSITE'] = website
    
    # Update any additional fields
    for key, value in kwargs.items():
        if key.upper() in mssp_data.data:
            mssp_data.data[key.upper()] = str(value)

def heartbeat_update(info):
    """Heartbeat hook handler to update dynamic MSSP data"""
    global mssp_data
    mssp_data.update_dynamic_data()

def cmd_mssp(ch, cmd, arg):
    """MSSP test command - sends MSSP data to the character's client"""
    if not ch.socket:
        ch.send("No socket available.")
        return
    
    ch.send("Sending MSSP data to your client...")
    
    # Generate and send MSSP response directly
    global mssp_data
    response = mssp_data.generate_mssp_response()
    
    # Send response back to client using socket's send_raw method
    # Convert bytes to string for socket output
    response_str = response.decode('latin1')
    ch.socket.send_raw(response_str)
    
    ch.send("MSSP data sent. Check your client for MSSP support.")
    print("MSSP test command used by %s" % ch.name)


# Register the hook handlers
hooks.add("receive_iac", handle_receive_iac)
hooks.add("heartbeat", heartbeat_update)
mudsys.add_cmd("mssp", None, cmd_mssp, "admin", False)
