#!/usr/bin/env python3
"""
Simple OSC connectivity test to verify communication with Ardour
This will help determine if the issue is with sending, receiving, or parsing
"""

import time
import logging
from pythonosc import udp_client, dispatcher, osc_server
import threading

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OSCDebugger:
    def __init__(self, listen_port=3820, send_port=3819):  # Manual port mode: separate send/receive ports
        self.listen_port = listen_port
        self.send_port = send_port
        self.received_messages = []
        self.server = None
        self.server_thread = None
        
        # Setup listener
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.set_default_handler(self._handle_any_message)
        
    def _handle_any_message(self, address, *args):
        """Catch ALL incoming OSC messages"""
        msg_info = {
            'timestamp': time.time(),
            'address': address,
            'args': args,
            'arg_types': [type(arg).__name__ for arg in args]
        }
        self.received_messages.append(msg_info)
        logger.info(f"[RECEIVED] {address} {args} (types: {msg_info['arg_types']})")
        
        # Check if this looks like strip data
        if len(args) >= 7 and isinstance(args[0], int) and isinstance(args[1], str):
            logger.info(f"[POTENTIAL STRIP] SSID={args[0]}, Type='{args[1]}', Name='{args[2]}'")
            
    def start_listener(self):
        """Start OSC listener"""
        try:
            self.server = osc_server.ThreadingOSCUDPServer(
                ("127.0.0.1", self.listen_port), 
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.info(f"OSC listener started on port {self.listen_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start OSC listener: {e}")
            return False
            
    def stop_listener(self):
        """Stop OSC listener"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("OSC listener stopped")
            
    def send_message(self, address, *args):
        """Send OSC message to Ardour"""
        try:
            client = udp_client.SimpleUDPClient("127.0.0.1", self.send_port)
            if args:
                if len(args) == 1:
                    client.send_message(address, args[0])
                else:
                    client.send_message(address, list(args))
            else:
                client.send_message(address, [])
            logger.info(f"[SENT] {address} {args}")
            return True
        except Exception as e:
            logger.error(f"Failed to send {address}: {e}")
            return False
            
    def test_basic_connection(self):
        """Test basic OSC connectivity"""
        logger.info("=== BASIC CONNECTION TEST ===")
        
        # Clear previous messages
        self.received_messages.clear()
        
        # Send some basic commands that should work
        test_commands = [
            ("/transport_stop", 1),
            ("/goto_start", 1),
            ("/session_name", 1),  # Query session name
        ]
        
        for address, arg in test_commands:
            logger.info(f"Testing: {address}")
            self.send_message(address, arg)
            time.sleep(0.5)
            
        logger.info(f"Basic test complete. Received {len(self.received_messages)} messages")
        
    def test_strip_list_protocol(self):
        """Test the exact strip list protocol"""
        logger.info("=== STRIP LIST PROTOCOL TEST ===")
        
        # Clear previous messages
        self.received_messages.clear()
        
        # Step 1: Setup surface (CRITICAL) - with feedback enabled for manual port mode
        logger.info("Step 1: Setting up OSC surface with feedback=7 for manual port mode")
        success = self.send_message("/set_surface", 0, 3, 7)  # bank_size=0, strip_types=3 (AT+MT), feedback=7
        if not success:
            logger.error("Failed to setup surface!")
            return
            
        time.sleep(0.5)
        
        # Step 2: Request strip list
        logger.info("Step 2: Requesting strip list")
        success = self.send_message("/strip/list", 1)
        if not success:
            logger.error("Failed to send strip list request!")
            return
            
        # Step 3: Wait for responses
        logger.info("Step 3: Waiting for responses...")
        start_time = time.time()
        initial_count = len(self.received_messages)
        
        while time.time() - start_time < 5.0:  # Wait 5 seconds
            time.sleep(0.1)
            
        final_count = len(self.received_messages)
        new_messages = final_count - initial_count
        
        logger.info(f"Strip list test complete. Received {new_messages} new messages")
        
        # Analyze responses
        if new_messages > 0:
            logger.info("=== ANALYSIS OF RECEIVED MESSAGES ===")
            for i, msg in enumerate(self.received_messages[initial_count:]):
                logger.info(f"Message {i+1}: {msg['address']} {msg['args']}")
        else:
            logger.warning("NO MESSAGES RECEIVED - This indicates a communication problem!")
            
    def run_full_test(self):
        """Run complete OSC debug test"""
        logger.info("🎯 STARTING FULL OSC DEBUG TEST")
        logger.info("=" * 60)
        
        # Start listener
        if not self.start_listener():
            logger.error("❌ Cannot start listener - test aborted")
            return
            
        logger.info(f"✅ OSC Listener running on port {self.listen_port}")
        logger.info(f"📡 Will send commands to Ardour on port {self.send_port}")
        
        try:
            # Test 1: Basic connectivity
            self.test_basic_connection()
            
            time.sleep(2)
            
            # Test 2: Strip list protocol
            self.test_strip_list_protocol()
            
            # Summary
            logger.info("=" * 60)
            logger.info("🎯 TEST SUMMARY")
            logger.info(f"Total messages received: {len(self.received_messages)}")
            
            if len(self.received_messages) == 0:
                logger.error("❌ NO MESSAGES RECEIVED")
                logger.error("Possible issues:")
                logger.error("1. Ardour OSC not enabled (Window > Preferences > Control Surfaces)")
                logger.error("2. Wrong ports (check Ardour OSC settings)")
                logger.error("3. Firewall blocking UDP traffic")
                logger.error("4. Ardour not running or no session loaded")
            else:
                logger.info("✅ COMMUNICATION WORKING")
                logger.info("Messages by address:")
                addresses = {}
                for msg in self.received_messages:
                    addr = msg['address']
                    addresses[addr] = addresses.get(addr, 0) + 1
                    
                for addr, count in addresses.items():
                    logger.info(f"  {addr}: {count} messages")
                    
        finally:
            self.stop_listener()

def main():
    """Run OSC debug test"""
    print("🔍 OSC Communication Debug Tool")
    print("This will test if we can communicate with Ardour at all")
    print("Make sure Ardour is running with a session loaded!")
    print()
    
    # Get port configuration - for manual port mode, use separate send/receive ports
    try:
        from mcp_server.config import get_osc_config
        config = get_osc_config()
        send_port = config["port"]  # Send to Ardour on this port
        listen_port = config.get("listen_port", 3820)  # Listen for replies on this port
        print(f"Using manual port mode: send={send_port}, listen={listen_port}")
    except:
        send_port = 3819  # Send to Ardour
        listen_port = 3820  # Listen for replies
        print(f"Using default manual port mode: send={send_port}, listen={listen_port}")
        
    debugger = OSCDebugger(listen_port=listen_port, send_port=send_port)
    debugger.run_full_test()
    
    print()
    print("🎯 Next steps:")
    print("1. Check the log output above")
    print("2. If no messages received, check Ardour OSC settings")
    print("3. If messages received but no strip data, restart MCP server")

if __name__ == "__main__":
    main()