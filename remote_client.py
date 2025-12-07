#!/usr/bin/env python3
"""
Remote Access Client
Runs on the laptop you're using to control the other laptop.
"""

import socket
import json
import base64
import os
import sys

# Configuration
SERVER_HOST = '192.168.1.100'  # CHANGE THIS to your server's IP address
SERVER_PORT = 8888
PASSWORD = 'your_secure_password_here'  # CHANGE THIS to match server password
BUFFER_SIZE = 4096

class RemoteClient:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
    
    def connect(self):
        """Connect to remote server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Authenticate
            auth_msg = self.socket.recv(BUFFER_SIZE)
            if auth_msg == b"AUTH_REQUIRED":
                auth_data = json.dumps({'password': self.password})
                self.socket.send(auth_data.encode())
                
                response = self.socket.recv(BUFFER_SIZE)
                if response == b"AUTH_SUCCESS":
                    print("[+] Connected and authenticated!")
                    return True
                else:
                    print("[-] Authentication failed!")
                    return False
            return True
        except Exception as e:
            print(f"[-] Connection error: {e}")
            return False
    
    def send_command(self, command):
        """Send command to server"""
        try:
            command_data = {
                'type': 'command',
                'command': command
            }
            self.socket.send(json.dumps(command_data).encode())
            
            # Receive response
            response = self.socket.recv(BUFFER_SIZE * 10)  # Larger buffer for long outputs
            return response.decode()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def download_file(self, remote_path, local_path=None):
        """Download file from server"""
        try:
            command_data = {
                'type': 'download',
                'file_path': remote_path
            }
            self.socket.send(json.dumps(command_data).encode())
            
            # Receive file data
            response = self.socket.recv(BUFFER_SIZE * 100)  # Large buffer for files
            file_info = json.loads(response.decode())
            
            if 'data' in file_info:
                file_data = base64.b64decode(file_info['data'])
                filename = local_path or file_info.get('filename', 'downloaded_file')
                
                with open(filename, 'wb') as f:
                    f.write(file_data)
                
                return f"File downloaded: {filename}"
            else:
                return response.decode()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def upload_file(self, local_path, remote_filename=None):
        """Upload file to server"""
        try:
            if not os.path.exists(local_path):
                return "Error: File not found"
            
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            file_info = {
                'filename': remote_filename or os.path.basename(local_path),
                'data': base64.b64encode(file_data).decode()
            }
            
            command_data = {
                'type': 'upload',
                'file_info': file_info
            }
            self.socket.send(json.dumps(command_data).encode())
            
            response = self.socket.recv(BUFFER_SIZE)
            return response.decode()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def interactive_shell(self):
        """Start interactive shell session"""
        print("\n[+] Interactive shell started. Type 'exit' to quit, 'help' for commands")
        print("[+] Commands:")
        print("    - Any shell command")
        print("    - download <remote_path> [local_path] - Download file")
        print("    - upload <local_path> [remote_name] - Upload file")
        print("    - exit - Close connection\n")
        
        while True:
            try:
                command = input("remote> ").strip()
                
                if not command:
                    continue
                
                if command == 'exit':
                    self.send_command('exit')
                    break
                
                elif command.startswith('download '):
                    parts = command.split(' ', 1)
                    if len(parts) == 2:
                        remote_path = parts[1].split()[0]
                        local_path = parts[1].split()[1] if len(parts[1].split()) > 1 else None
                        result = self.download_file(remote_path, local_path)
                        print(result)
                    else:
                        print("Usage: download <remote_path> [local_path]")
                
                elif command.startswith('upload '):
                    parts = command.split(' ', 1)
                    if len(parts) == 2:
                        local_path = parts[1].split()[0]
                        remote_name = parts[1].split()[1] if len(parts[1].split()) > 1 else None
                        result = self.upload_file(local_path, remote_name)
                        print(result)
                    else:
                        print("Usage: upload <local_path> [remote_name]")
                
                elif command == 'help':
                    print("\nAvailable commands:")
                    print("  <command> - Execute shell command on remote machine")
                    print("  download <remote_path> [local_path] - Download file")
                    print("  upload <local_path> [remote_name] - Upload file")
                    print("  exit - Close connection\n")
                
                else:
                    result = self.send_command(command)
                    print(result)
            
            except KeyboardInterrupt:
                print("\n[!] Closing connection...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()

def main():
    """Main client function"""
    print("=" * 50)
    print("Remote Access Client")
    print("=" * 50)
    
    # Check configuration
    if PASSWORD == 'your_secure_password_here':
        print("[!] WARNING: Please change the PASSWORD in remote_client.py!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    if SERVER_HOST == '192.168.1.100':
        print("[!] WARNING: Please set SERVER_HOST to your server's IP address!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Connect to server
    client = RemoteClient(SERVER_HOST, SERVER_PORT, PASSWORD)
    
    if client.connect():
        try:
            client.interactive_shell()
        finally:
            client.close()
            print("[+] Connection closed")
    else:
        print("[-] Failed to connect")

if __name__ == '__main__':
    main()
