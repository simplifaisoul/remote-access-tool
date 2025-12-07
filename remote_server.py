#!/usr/bin/env python3
"""
Remote Access Server
Runs on the laptop you want to control remotely.
"""

import socket
import subprocess
import os
import json
import base64
import hashlib
import threading
from datetime import datetime

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8888
PASSWORD = 'your_secure_password_here'  # CHANGE THIS!
BUFFER_SIZE = 4096

def hash_password(password):
    """Hash password for secure comparison"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(client_socket):
    """Authenticate client with password"""
    try:
        client_socket.send(b"AUTH_REQUIRED")
        auth_data = client_socket.recv(BUFFER_SIZE).decode()
        auth_info = json.loads(auth_data)
        
        if hash_password(auth_info.get('password', '')) == hash_password(PASSWORD):
            client_socket.send(b"AUTH_SUCCESS")
            return True
        else:
            client_socket.send(b"AUTH_FAILED")
            return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def execute_command(command):
    """Execute shell command and return output"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
        else:  # Linux/Mac
            result = subprocess.run(
                command.split(), 
                capture_output=True, 
                text=True,
                timeout=30
            )
        
        output = result.stdout + result.stderr
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def send_file(file_path, client_socket):
    """Send file to client"""
    try:
        if not os.path.exists(file_path):
            client_socket.send(b"FILE_NOT_FOUND")
            return
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        file_info = {
            'filename': os.path.basename(file_path),
            'size': len(file_data),
            'data': base64.b64encode(file_data).decode()
        }
        
        client_socket.send(json.dumps(file_info).encode())
        return True
    except Exception as e:
        client_socket.send(f"ERROR: {str(e)}".encode())
        return False

def receive_file(file_info, client_socket):
    """Receive file from client"""
    try:
        filename = file_info.get('filename')
        file_data = base64.b64decode(file_info.get('data', ''))
        
        save_path = os.path.join(os.getcwd(), filename)
        with open(save_path, 'wb') as f:
            f.write(file_data)
        
        return f"File saved: {save_path}"
    except Exception as e:
        return f"Error receiving file: {str(e)}"

def handle_client(client_socket, address):
    """Handle client connection"""
    print(f"[{datetime.now()}] Connection from {address}")
    
    # Authenticate
    if not authenticate(client_socket):
        print(f"[{datetime.now()}] Authentication failed from {address}")
        client_socket.close()
        return
    
    print(f"[{datetime.now()}] Authenticated: {address}")
    
    try:
        while True:
            # Receive command
            data = client_socket.recv(BUFFER_SIZE).decode()
            if not data:
                break
            
            command_data = json.loads(data)
            cmd_type = command_data.get('type')
            
            if cmd_type == 'command':
                # Execute command
                command = command_data.get('command', '')
                print(f"[{datetime.now()}] Executing: {command}")
                result = execute_command(command)
                client_socket.send(result.encode())
            
            elif cmd_type == 'download':
                # Send file to client
                file_path = command_data.get('file_path', '')
                send_file(file_path, client_socket)
            
            elif cmd_type == 'upload':
                # Receive file from client
                file_info = command_data.get('file_info', {})
                result = receive_file(file_info, client_socket)
                client_socket.send(result.encode())
            
            elif cmd_type == 'exit':
                break
            
            else:
                client_socket.send(b"Unknown command type")
    
    except Exception as e:
        print(f"[{datetime.now()}] Error with {address}: {e}")
    finally:
        client_socket.close()
        print(f"[{datetime.now()}] Connection closed: {address}")

def main():
    """Main server function"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[{datetime.now()}] Server listening on {HOST}:{PORT}")
        print(f"[{datetime.now()}] Waiting for connections...")
        
        while True:
            client_socket, address = server_socket.accept()
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
