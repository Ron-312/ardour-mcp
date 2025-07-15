#!/usr/bin/env python3
"""
Mock OSC server for testing message formatting and delivery
"""

import threading
import time
from pythonosc import dispatcher
from pythonosc import osc_server
from mcp_server.osc_client import OSCClient

class MockOSCServer:
    """Mock OSC server to capture and log messages"""
    
    def __init__(self, ip="127.0.0.1", port=3819):
        self.ip = ip
        self.port = port
        self.received_messages = []
        self.server = None
        self.server_thread = None
        
        # Create dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        
        # Map all possible handlers
        self.dispatcher.map("/ardour/transport_play", self.handle_transport_play)
        self.dispatcher.map("/ardour/transport_stop", self.handle_transport_stop)
        self.dispatcher.map("/strip/*/gain", self.handle_strip_gain)
        self.dispatcher.map("/strip/*/fader", self.handle_strip_fader)
        self.dispatcher.map("/strip/*/mute", self.handle_strip_mute)
        self.dispatcher.map("/strip/*/solo", self.handle_strip_solo)
        
        # Catch-all handler
        self.dispatcher.set_default_handler(self.handle_default)
    
    def handle_transport_play(self, unused_addr, *args):
        """Handle transport play message"""
        message = {
            "address": "/ardour/transport_play",
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_transport_stop(self, unused_addr, *args):
        """Handle transport stop message"""
        message = {
            "address": "/ardour/transport_stop",
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_strip_gain(self, unused_addr, *args):
        """Handle strip gain message"""
        message = {
            "address": unused_addr,
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_strip_fader(self, unused_addr, *args):
        """Handle strip fader message"""
        message = {
            "address": unused_addr,
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_strip_mute(self, unused_addr, *args):
        """Handle strip mute message"""
        message = {
            "address": unused_addr,
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_strip_solo(self, unused_addr, *args):
        """Handle strip solo message"""
        message = {
            "address": unused_addr,
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received: {message}")
    
    def handle_default(self, unused_addr, *args):
        """Handle any other messages"""
        message = {
            "address": unused_addr,
            "args": args,
            "timestamp": time.time()
        }
        self.received_messages.append(message)
        print(f"Received (default): {message}")
    
    def start(self):
        """Start the mock server"""
        self.server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"Mock OSC server started on {self.ip}:{self.port}")
    
    def stop(self):
        """Stop the mock server"""
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
            print("Mock OSC server stopped")
    
    def get_received_messages(self):
        """Get all received messages"""
        return self.received_messages
    
    def clear_messages(self):
        """Clear received messages"""
        self.received_messages.clear()

def test_osc_client():
    """Test OSC client with mock server"""
    print("Starting mock OSC server...")
    mock_server = MockOSCServer()
    mock_server.start()
    
    try:
        # Give server time to start
        time.sleep(0.1)
        
        print("Testing OSC client...")
        osc_client = OSCClient()
        
        # Test transport commands
        print("Testing transport play...")
        osc_client.transport_play()
        time.sleep(0.1)
        
        print("Testing transport stop...")
        osc_client.transport_stop()
        time.sleep(0.1)
        
        # Test strip commands
        print("Testing strip gain...")
        osc_client.set_strip_gain(1, -10.0)
        time.sleep(0.1)
        
        print("Testing strip fader...")
        osc_client.set_strip_fader(2, 0.75)
        time.sleep(0.1)
        
        print("Testing strip mute...")
        osc_client.strip_mute(3, True)
        time.sleep(0.1)
        
        print("Testing strip solo...")
        osc_client.strip_solo(4, True)
        time.sleep(0.1)
        
        # Print results
        messages = mock_server.get_received_messages()
        print(f"\nReceived {len(messages)} messages:")
        for msg in messages:
            print(f"  {msg['address']} {msg['args']}")
            
    finally:
        mock_server.stop()

if __name__ == "__main__":
    test_osc_client()