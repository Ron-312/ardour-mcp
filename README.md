# Ardour MCP Server

A FastAPI-based MCP (Model Context Protocol) server for controlling Ardour DAW via OSC messages. This project provides a bridge between MCP clients and Ardour DAW, allowing remote control of transport and track functions through HTTP API endpoints that translate to OSC messages.

## 🎯 Features

- **Transport Control**: Play, stop, rewind, fast-forward
- **Track Control**: Fader levels, mute, solo for individual tracks
- **OSC Integration**: Direct communication with Ardour via UDP port 3819
- **HTTP API**: RESTful endpoints for all DAW functions
- **MCP Client**: Command-line tool with manifest generation
- **Robust Logging**: Comprehensive request/response logging
- **Error Handling**: Proper HTTP status codes and error responses
- **Docker Support**: Containerized deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Ardour DAW with OSC support enabled
- Node.js (for MCP client usage)

### Installation

1. **Clone and setup project:**
   ```bash
   git clone <repository-url>
   cd ardour-mcp
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if needed - default values work for local setup
   ```

4. **Start the server:**
   ```bash
   uvicorn mcp_server.main:app --reload
   ```

The server will start on `http://localhost:8000` and be ready to communicate with Ardour on `127.0.0.1:3819`.

## 📖 Usage

### Configuring Ardour

1. **Enable OSC in Ardour:**
   - Go to `Edit > Preferences > Control Surfaces`
   - Add "Open Sound Control (OSC)"
   - Set port to `3819` (default)
   - **Important**: Enable "Debug = On" for troubleshooting
   - Enable the surface

2. **Start Ardour:**
   ```bash
   # For headless operation
   ardour --no-gui --osc-port=3819
   
   # Or with GUI
   ardour
   ```

3. **Test OSC Connection:**
   ```bash
   # Run the connection test script
   python test_ardour_connection.py
   ```
   
   This will send test OSC messages directly to Ardour. Check `Window > Log` in Ardour for entries like:
   ```
   OSC: /ardour/transport_play i:1
   OSC: /ardour/transport_stop i:1
   ```

**Important for Ardour 7+**: Transport commands require an integer argument:
- `/ardour/transport_play` needs `1` argument to start
- `/ardour/transport_stop` needs `1` argument to stop
- The server automatically includes these required arguments

### Using the HTTP API

#### Transport Control

```bash
# Start playback
curl -X POST http://localhost:8000/transport/play

# Stop playback
curl -X POST http://localhost:8000/transport/stop
```

#### Track Control

```bash
# Set track 1 fader to -10dB
curl -X POST "http://localhost:8000/track/1/fader" \
  -H "Content-Type: application/json" \
  -d '{"gain_db": -10.0}'

# Mute track 2
curl -X POST "http://localhost:8000/track/2/mute" \
  -H "Content-Type: application/json" \
  -d '{"mute": true}'

# Solo track 3
curl -X POST "http://localhost:8000/track/3/solo" \
  -H "Content-Type: application/json" \
  -d '{"solo": true}'
```

### Using the MCP Client

```bash
# View available tools and manifest
python mcp_client/ardour_mcp_client.py --describe

# List all available tools
python mcp_client/ardour_mcp_client.py --list-tools

# Get information about a specific tool
python mcp_client/ardour_mcp_client.py --tool-info transport_play

# Validate input for a tool
python mcp_client/ardour_mcp_client.py --validate set_track_fader '{"track_number": 1, "gain_db": -10.0}'
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file to customize configuration:

```bash
# OSC Configuration
OSC_TARGET_IP=127.0.0.1      # Ardour's IP address
OSC_TARGET_PORT=3819         # OSC port (must match Ardour)

# FastAPI Server Configuration
HTTP_PORT=8000               # Server port
HTTP_HOST=0.0.0.0           # Server host

# Application Configuration
DEBUG=false                  # Debug mode
LOG_LEVEL=info              # Logging level (debug, info, warning, error)
```

### Advanced Configuration

For custom setups, you can modify `mcp_server/config.py` to add additional settings or validation.

## 📚 API Reference

### Transport Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/transport/play` | Start playback | None |
| POST | `/transport/stop` | Stop playback | None |
| GET | `/` | Server info | None |
| GET | `/health` | Health check | None |

### Track Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/track/{n}/fader` | Set track fader | `{"gain_db": -10.0}` |
| POST | `/track/{n}/mute` | Mute/unmute track | `{"mute": true}` |
| POST | `/track/{n}/solo` | Solo/unsolo track | `{"solo": true}` |

### Request/Response Examples

#### Set Fader Example
```bash
# Request
POST /track/1/fader
Content-Type: application/json
{
  "gain_db": -10.0
}

# Response
{
  "status": "success",
  "action": "set_fader",
  "track": 1,
  "gain_db": -10.0,
  "message": "Fader set to -10.0dB for track 1",
  "osc_address": "/strip/0/gain"
}
```

#### Error Response
```json
{
  "detail": "Failed to send transport play command to Ardour",
  "status_code": 500
}
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t ardour-mcp .

# Run container
docker run -p 8000:8000 -p 3819:3819/udp ardour-mcp
```

## 🧪 Testing

### Manual Testing

1. **Start the server:**
   ```bash
   uvicorn mcp_server.main:app --reload
   ```

2. **Test endpoints:**
   ```bash
   # Test server health
   curl http://localhost:8000/health
   
   # Test transport
   curl -X POST http://localhost:8000/transport/play
   curl -X POST http://localhost:8000/transport/stop
   
   # Test track controls
   curl -X POST "http://localhost:8000/track/1/fader" \
     -H "Content-Type: application/json" \
     -d '{"gain_db": -6.0}'
   ```

3. **View API documentation:**
   - Open `http://localhost:8000/docs` in your browser
   - Interactive Swagger UI with all endpoints

### Testing with Mock OSC Server

```bash
# Run the mock OSC server for testing
python test_osc_mock.py
```

### Unit Tests

```bash
# Run configuration tests
python -m pytest tests/test_config.py -v

# Run OSC client tests
python -m pytest tests/test_osc_client.py -v

# Run API tests
python -m pytest tests/test_transport_api.py -v
```

## 📁 Project Structure

```
ardour-mcp/
├── mcp_server/                  # FastAPI server implementation
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── osc_client.py           # OSC client for Ardour communication
│   └── api/                    # API endpoints
│       ├── __init__.py
│       ├── transport.py        # Transport control endpoints
│       └── track.py            # Track control endpoints
├── mcp_client/                  # MCP client implementation
│   ├── ardour_mcp_client.py    # Main MCP client script
│   └── mcp_ardour.json         # MCP manifest file
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_config.py          # Configuration tests
│   ├── test_osc_client.py      # OSC client tests
│   └── test_transport_api.py   # API endpoint tests
├── docs/                        # Documentation
├── .env.example                 # Environment configuration template
├── .env                         # Environment configuration (local)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml          # Docker Compose configuration
├── test_osc_mock.py            # Mock OSC server for testing
├── test_env.py                 # Environment testing script
└── README.md                   # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **Server won't start:**
   ```bash
   # Check if port is already in use
   lsof -i :8000
   
   # Try different port
   uvicorn mcp_server.main:app --port 8001
   ```

2. **OSC communication fails:**
   - Run `python test_ardour_connection.py` to test direct connection
   - Verify Ardour has OSC enabled on port 3819
   - Enable "Debug = On" in Ardour OSC settings
   - Check `Window > Log` in Ardour for OSC message entries
   - Check firewall settings (allow UDP port 3819)
   - Ensure IP address is correct in `.env`
   - For Ardour 7+: Transport commands need integer arguments (automatically handled)

3. **Import errors:**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   
   # For development
   pip install pydantic-settings python-osc fastapi uvicorn
   ```

4. **Permission errors:**
   ```bash
   # Make scripts executable (Linux/Mac)
   chmod +x mcp_client/ardour_mcp_client.py
   ```

### Debug Mode

Enable debug logging:
```bash
# Set in .env file
DEBUG=true
LOG_LEVEL=debug

# Or set environment variable
export LOG_LEVEL=debug
uvicorn mcp_server.main:app --reload
```

### Logs

View server logs:
```bash
# Console output shows all requests
# File logs written to: ardour_mcp.log

# View log file
tail -f ardour_mcp.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Ardour DAW team for OSC support
- FastAPI team for the excellent web framework
- python-osc library for OSC communication

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `http://localhost:8000/docs`
3. Check server logs in `ardour_mcp.log`
4. Open an issue in the repository

---

**Happy music making with Ardour MCP Server! 🎵**