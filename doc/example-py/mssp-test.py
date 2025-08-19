#!/usr/bin/env python3
"""
MSSP (Mud Server Status Protocol) Test Script
Tests MSSP response from localhost:5000
"""

import socket
import time
import sys

# MSSP and Telnet constants
IAC = 255  # Interpret As Command
WILL = 251
WONT = 252
DO = 253
DONT = 254
SB = 250   # Subnegotiation Begin
SE = 240   # Subnegotiation End

TELOPT_MSSP = 70  # MSSP telnet option
MSSP_VAR = 1      # Variable marker
MSSP_VAL = 2      # Value marker

def connect_to_mud(host="localhost", port=5000, timeout=10):
    """Connect to the MUD server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print(f"✓ Connected to {host}:{port}")
        return sock
    except Exception as e:
        print(f"✗ Failed to connect to {host}:{port}: {e}")
        return None

def send_mssp_request(sock):
    """Send MSSP negotiation request"""
    # Send IAC WILL MSSP (tell server we support MSSP)
    will_mssp = bytes([IAC, WILL, TELOPT_MSSP])
    sock.send(will_mssp)
    print(f"→ Sent IAC WILL MSSP: {' '.join(f'{b:02x}' for b in will_mssp)}")
    
    # Also send IAC DO MSSP (ask server to send MSSP data)
    do_mssp = bytes([IAC, DO, TELOPT_MSSP])
    sock.send(do_mssp)
    print(f"→ Sent IAC DO MSSP: {' '.join(f'{b:02x}' for b in do_mssp)}")

def parse_mssp_response(data):
    """Parse MSSP subnegotiation data"""
    mssp_vars = {}
    i = 0
    
    while i < len(data):
        if data[i] == MSSP_VAR:
            # Found variable marker
            i += 1
            var_start = i
            
            # Find next marker
            while i < len(data) and data[i] not in [MSSP_VAR, MSSP_VAL]:
                i += 1
            
            if i < len(data) and data[i] == MSSP_VAL:
                variable = data[var_start:i].decode('utf-8', errors='ignore')
                i += 1  # Skip MSSP_VAL marker
                val_start = i
                
                # Find next marker or end
                while i < len(data) and data[i] not in [MSSP_VAR, MSSP_VAL]:
                    i += 1
                
                value = data[val_start:i].decode('utf-8', errors='ignore')
                mssp_vars[variable] = value
            else:
                i += 1
        else:
            i += 1
    
    return mssp_vars

def process_telnet_data(data):
    """Process received telnet data, looking for MSSP responses"""
    print(f"\n🔍 Processing {len(data)} bytes of telnet data...")
    print(f"Raw bytes: {' '.join(['%02x' % b for b in data[:50]])}{'...' if len(data) > 50 else ''}")
    
    responses = []
    i = 0
    
    while i < len(data):
        if i + 2 < len(data) and data[i] == IAC:
            print(f"🔧 IAC sequence at byte {i}: {data[i]:02x} {data[i+1]:02x} {data[i+2]:02x}")
            
            if data[i + 1] == SB and data[i + 2] == TELOPT_MSSP:
                # Found MSSP subnegotiation
                print(f"✓ Found MSSP subnegotiation at byte {i}")
                
                # Find the end (IAC SE)
                sub_start = i + 3
                sub_end = sub_start
                
                print(f"🔍 Looking for IAC SE starting at byte {sub_start}...")
                while sub_end + 1 < len(data):
                    if data[sub_end] == IAC and data[sub_end + 1] == SE:
                        print(f"✓ Found IAC SE at byte {sub_end}")
                        break
                    sub_end += 1
                
                if sub_end + 1 < len(data):
                    # Extract MSSP data
                    mssp_data = data[sub_start:sub_end]
                    print(f"📊 Extracting MSSP data ({len(mssp_data)} bytes): {' '.join(['%02x' % b for b in mssp_data[:20]])}{'...' if len(mssp_data) > 20 else ''}")
                    mssp_vars = parse_mssp_response(mssp_data)
                    responses.append(mssp_vars)
                    i = sub_end + 2
                else:
                    print("⚠️  No IAC SE found - incomplete MSSP subnegotiation")
                    i += 1
            
            elif data[i + 1] in [WILL, WONT, DO, DONT] and i + 2 < len(data):
                # Standard 3-byte telnet negotiation
                cmd = data[i + 1]
                opt = data[i + 2]
                
                cmd_name = {WILL: "WILL", WONT: "WONT", DO: "DO", DONT: "DONT"}[cmd]
                
                if opt == TELOPT_MSSP:
                    print(f"← Received IAC {cmd_name} MSSP")
                else:
                    print(f"← Received IAC {cmd_name} {opt}")
                
                i += 3
            else:
                print(f"🔧 Other IAC sequence: {data[i+1]:02x}")
                i += 1
        else:
            i += 1
    
    print(f"📋 Found {len(responses)} MSSP response(s)")
    return responses

def display_mssp_data(mssp_vars):
    """Display MSSP data in a nice format"""
    print("\n" + "="*50)
    print("MSSP DATA RECEIVED")
    print("="*50)
    
    if not mssp_vars:
        print("No MSSP data found!")
        return
    
    # Order the variables nicely
    var_order = [
        'NAME', 'PLAYERS', 'UPTIME', 'CODEBASE', 'CONTACT', 
        'CREATED', 'ICON', 'LANGUAGE', 'LOCATION', 'MINIMUM_AGE', 'WEBSITE'
    ]
    
    for var in var_order:
        if var in mssp_vars:
            value = mssp_vars[var]
            
            # Format some variables nicely
            if var == 'UPTIME' and value.isdigit():
                uptime_sec = int(value)
                hours = uptime_sec // 3600
                minutes = (uptime_sec % 3600) // 60
                value = f"{value} seconds ({hours}h {minutes}m)"
            
            print(f"{var:12}: {value}")
    
    # Show any extra variables not in the standard list
    extra_vars = {k: v for k, v in mssp_vars.items() if k not in var_order}
    if extra_vars:
        print("\nAdditional variables:")
        for var, value in extra_vars.items():
            print(f"{var:12}: {value}")
    
    print("="*50)

def test_mssp(host="localhost", port=5000):
    """Main MSSP test function"""
    print(f"Testing MSSP support on {host}:{port}")
    print("-" * 40)
    
    # Connect to MUD
    sock = connect_to_mud(host, port)
    if not sock:
        return False
    
    try:
        # Send MSSP request
        send_mssp_request(sock)
        
        # Wait for MSSP response with multiple reads
        print("\n⏳ Waiting for MSSP response...")
        all_data = b''
        mssp_found = False
        
        # Read data in chunks over several seconds
        for attempt in range(10):  # Try for up to 5 seconds
            try:
                sock.settimeout(0.5)  # Short timeout per read
                data = sock.recv(4096)
                if data:
                    all_data += data
                    print(f"← Received {len(data)} bytes (total: {len(all_data)})")
                    
                    # Check if we have MSSP data
                    if b'\xff\xfa\x46' in all_data:  # IAC SB MSSP
                        print("← MSSP subnegotiation detected!")
                        mssp_found = True
                        
                    # Check if we have complete MSSP response (ends with IAC SE)
                    if mssp_found and b'\xff\xf0' in all_data:
                        print("← Complete MSSP response received!")
                        break
                else:
                    break
                    
            except socket.timeout:
                # Continue trying
                pass
            
            time.sleep(0.1)
        
        if all_data:
            print(f"\nTotal data received ({len(all_data)} bytes)")
            
            # Process the data
            mssp_responses = process_telnet_data(all_data)
            
            if mssp_responses:
                print(f"\n✓ MSSP response received!")
                for i, response in enumerate(mssp_responses):
                    print(f"\nMSSP Data Set {i+1}:")
                    for var, val in response.items():
                        print(f"  {var}: {val}")
                return True
            else:
                print("\n⚠️  No MSSP response received")
                print("Possible reasons:")
                print("- Server doesn't support MSSP")
                print("- MSSP not properly implemented") 
                print("- Network issues")
                
                print(f"\nRaw data received ({len(all_data)} bytes):")
                hex_output = ' '.join([f'{b:02x}' for b in all_data])
                print(hex_output)
                return False
        else:
            print("⚠️  No data received")
            return False
        
        print("\n✓ MSSP test completed successfully!")
    
    finally:
        sock.close()
        print(f"✓ Connection closed")
    return mssp_found

def main():
    """Main function"""
    host = "localhost"
    port = 5000
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port: {sys.argv[2]}")
            sys.exit(1)
    
    print("MSSP Test Script")
    print("================")
    print("This script tests MSSP (Mud Server Status Protocol) support")
    print(f"Target: {host}:{port}")
    print()
    
    success = test_mssp(host, port)
    
    if success:
        print("\n🎉 MSSP support confirmed!")
        sys.exit(0)
    else:
        print("\n❌ MSSP support not detected")
        sys.exit(1)

if __name__ == "__main__":
    main()