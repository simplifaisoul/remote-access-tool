# Remote Access Tool

A simple Python-based remote access tool for controlling one laptop from another. **For personal use only on your own devices.**

## ⚠️ Important Security Notes

- **Only use this on devices you own and have permission to access**
- **Change the default password immediately**
- **Use on trusted networks only** (or set up proper firewall rules)
- **This tool has basic security - consider using VPN or SSH tunnel for production use**

## Features

- Remote command execution
- File upload/download
- Interactive shell session
- Password authentication
- Cross-platform (Windows, Linux, macOS)

## Setup

### 1. Install Python

Make sure you have Python 3.6+ installed on both machines.

### 2. Clone the Repository

```bash
git clone https://github.com/simplifaisoul/remote-access-tool.git
cd remote-access-tool
```

### 3. Configure the Server (Laptop to be Controlled)

Edit `remote_server.py`:

```python
PORT = 8888  # Change if needed
PASSWORD = 'your_secure_password_here'  # CHANGE THIS!
```

### 4. Configure the Client (Controlling Laptop)

Edit `remote_client.py`:

```python
SERVER_HOST = '192.168.1.100'  # IP address of the server laptop
SERVER_PORT = 8888  # Must match server port
PASSWORD = 'your_secure_password_here'  # Must match server password
```

## Usage

### On the Server (Laptop to be Controlled)

```bash
python remote_server.py
```

The server will start listening on port 8888. You'll see:
```
[2024-01-01 12:00:00] Server listening on 0.0.0.0:8888
[2024-01-01 12:00:00] Waiting for connections...
```

### On the Client (Controlling Laptop)

```bash
python remote_client.py
```

Once connected, you'll enter an interactive shell. You can:

- Execute commands: `dir` (Windows) or `ls` (Linux/Mac)
- Download files: `download C:\path\to\file.txt`
- Upload files: `upload local_file.txt`
- Exit: `exit`

## Example Commands

```
remote> dir
remote> ipconfig
remote> download C:\Users\YourName\Documents\file.txt
remote> upload myfile.txt
remote> exit
```

## Finding Your Server's IP Address

### Windows:
```bash
ipconfig
```
Look for "IPv4 Address" under your network adapter.

### Linux/Mac:
```bash
ifconfig
# or
ip addr show
```

## Firewall Configuration

You may need to allow the port through your firewall:

### Windows:
1. Open Windows Defender Firewall
2. Advanced Settings
3. Inbound Rules → New Rule
4. Port → TCP → 8888 → Allow

### Linux:
```bash
sudo ufw allow 8888/tcp
```

## Security Recommendations

1. **Use a strong password** - Don't use the default!
2. **Use on local network only** - Or set up a VPN
3. **Consider using SSH tunnel** for additional security:
   ```bash
   ssh -L 8888:localhost:8888 user@server-ip
   ```
4. **Firewall rules** - Only allow connections from trusted IPs
5. **Change default port** - Use a non-standard port

## Troubleshooting

### Connection Refused
- Check if server is running
- Verify IP address is correct
- Check firewall settings
- Ensure both devices are on the same network

### Authentication Failed
- Verify passwords match in both files
- Check for typos

### Port Already in Use
- Change PORT in `remote_server.py` to a different number
- Update SERVER_PORT in `remote_client.py` to match

## License

This tool is provided as-is for personal use. Use responsibly and only on devices you own.

## Disclaimer

This tool is for legitimate remote access of your own devices only. Unauthorized access to computer systems is illegal. The authors are not responsible for misuse of this software.
