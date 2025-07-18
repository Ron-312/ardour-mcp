<div align="center">

# 🎵 Ardour MCP Server

<img src="https://img.shields.io/badge/Ardour-DAW_Control-ff6b35?style=for-the-badge&logo=ardour&logoColor=white" alt="Ardour DAW Control">

**Professional MCP Server for Ardour DAW Remote Control**

[![Python](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Cursor](https://img.shields.io/badge/Cursor-AI_Ready-6366f1?style=flat-square&logo=cursor&logoColor=white)](https://cursor.sh)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![OSC](https://img.shields.io/badge/OSC-Protocol-orange?style=flat-square)](https://opensoundcontrol.org)
[![License](https://img.shields.io/badge/License-Personal%2FCommercial-blue?style=flat-square)](#-license)
[![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=flat-square)](https://github.com/your-repo/issues)

*A powerful FastAPI-based MCP (Model Context Protocol) server that bridges MCP clients with Ardour DAW, enabling comprehensive remote control through HTTP API endpoints that seamlessly translate to OSC messages.*

</div>

> **⚠️ DEVELOPMENT STATUS**: This project is actively under development. While core features are functional, some functionalities may not work perfectly or may be incomplete. We welcome feedback, bug reports, and contributions!

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📖 Usage](#-usage)
- [🔧 Configuration](#-configuration)
- [📚 API Reference](#-api-reference)
- [🐳 Docker Deployment](#-docker-deployment)
- [🧪 Testing](#-testing)
- [📁 Project Structure](#-project-structure)
- [🔍 Troubleshooting](#-troubleshooting)

---

## ✨ Features

<details>
<summary><b>🎛️ Core DAW Control</b></summary>

- **🎵 Transport Control**: Play, stop, rewind, fast-forward, record
- **🎚️ Track Management**: Fader levels, mute, solo, record-enable for individual tracks
- **🔌 Plugin Control**: Comprehensive plugin discovery, parameter mapping, and real-time control
- **📼 Recording Features**: Master recording, punch recording, input monitoring
- **🎯 Selection Management**: Advanced track selection and group operations

</details>

<details>
<summary><b>🔗 Integration & Communication</b></summary>

- **📡 OSC Integration**: Direct bi-directional communication with Ardour via UDP
- **🌐 HTTP API**: RESTful endpoints with comprehensive OpenAPI documentation
- **🤖 MCP Protocol**: Full Model Context Protocol implementation with client tools
- **🎯 Cursor AI Ready**: Instant integration with Cursor's AI agent - no setup required
- **📊 Real-time Feedback**: Live parameter updates and status monitoring

</details>

<details>
<summary><b>🏗️ Architecture & Deployment</b></summary>

- **⚡ FastAPI Framework**: High-performance async web framework
- **🐳 Docker Support**: Complete containerized deployment with Docker Compose
- **📝 Comprehensive Logging**: Structured logging with configurable levels
- **🛡️ Error Handling**: Robust error handling with proper HTTP status codes
- **🔧 Flexible Configuration**: Environment-based configuration management

</details>

---

## 🚧 Development Status & Roadmap

<div align="center">
<img src="https://img.shields.io/badge/Phase-Active_Development-orange?style=for-the-badge" alt="Development Phase">
</div>

### ✅ Working Features
- ✅ **Core Transport Control** - Play, stop, rewind, fast-forward
- ✅ **Basic Track Operations** - Fader, mute, solo controls
- ✅ **MCP Integration** - Cursor AI ready functionality
- ✅ **Docker Support** - Containerized deployment

### 🔄 In Progress
- 🔄 **Plugin Control** - Advanced parameter mapping and discovery
- 🔄 **Recording Features** - Per-track recording and monitoring
- 🔄 **Selection Management** - Multi-track selection operations
- 🔄 **Real-time Feedback** - Live parameter updates from Ardour

### 🎯 Planned Features
- 🎯 **Advanced Plugin Control** - Smart parameter conversion
- 🎯 **Sends & Routing** - Aux send and bus management
- 🎯 **Session Management** - Load, save, and manage Ardour sessions
- 🎯 **Performance Optimization** - Enhanced OSC communication

> **💡 Want to contribute?** Check out [PLUGIN_IMPLEMENTATION_PLAN.md](PLUGIN_IMPLEMENTATION_PLAN.md) for detailed development roadmap!

## 🚀 Quick Start

### 🎯 Instant Setup with Cursor AI

<div align="center">
<img src="https://img.shields.io/badge/Cursor-AI_Ready-6366f1?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor AI Ready">
</div>

**Fastest way to get started!** If you're using [Cursor](https://cursor.sh/), you can immediately access Ardour MCP functionality:

1. **🚀 Clone & Open:**
   ```bash
   git clone <repository-url>
   cd ardour-mcp
   cursor .
   ```

2. **🤖 Activate Cursor Agent:**
   - Open Cursor's AI chat panel (`Cmd/Ctrl + L`)
   - The MCP client is automatically available to the AI agent
   - Start controlling Ardour directly through natural language!

3. **🎵 Example Cursor Commands:**
   ```
   "Start playback in Ardour"
   "Set track 1 fader to -6dB" 
   "Mute track 2 and solo track 3"
   "List all plugins on track 1"
   "Enable recording on track 4"
   ```

> **💡 Pro Tip:** Cursor's AI agent automatically discovers and uses the MCP tools defined in `mcp_client/mcp_ardour.json` - no additional setup required!

---

### 📦 Traditional Installation

#### Prerequisites

- Python 3.7+
- Ardour DAW with OSC support enabled
- Node.js (for standalone MCP client usage)

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

### 🤖 Using with Cursor AI (Recommended)

Once you have the project open in Cursor and the server running:

1. **🎵 Natural Language Control:**
   ```
   "Start playback"
   "Stop recording" 
   "Set track 1 volume to -10dB"
   "Mute tracks 2 and 3"
   "Solo track 4"
   "List all plugins on track 1"
   "Bypass the compressor on track 2"
   ```

2. **🔧 Advanced Operations:**
   ```
   "Enable recording on track 5 and start playback"
   "Set all tracks to -6dB except track 1"
   "Show me the current transport status"
   "What plugins are active on track 3?"
   ```

3. **🎛️ Plugin Control:**
   ```
   "Adjust the compressor threshold on track 1 to -12dB"
   "Turn off the reverb on track 2" 
   "Show me all EQ parameters on track 3"
   ```

> **💡 Why Cursor?** The AI automatically understands the MCP protocol and can execute complex DAW operations through natural conversation!

### 🛠️ Using the Standalone MCP Client

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

<details>
<summary><b>🎵 Transport Control</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/transport/play` | Start playback | None |
| POST | `/transport/stop` | Stop playback | None |
| POST | `/transport/rewind` | Rewind to beginning | None |
| POST | `/transport/fast_forward` | Fast forward | None |
| GET | `/transport/status` | Get transport status | None |

</details>

<details>
<summary><b>🎚️ Track Control</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/track/{n}/fader` | Set track fader | `{"gain_db": -10.0}` |
| POST | `/track/{n}/mute` | Mute/unmute track | `{"mute": true}` |
| POST | `/track/{n}/solo` | Solo/unsolo track | `{"solo": true}` |
| POST | `/track/{n}/record_enable` | Enable/disable recording | `{"enabled": true}` |
| POST | `/track/{n}/input_monitoring` | Set input monitoring | `{"enabled": true}` |

</details>

<details>
<summary><b>🔌 Plugin Control</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/plugins/track/{n}/plugins` | List track plugins | None |
| GET | `/plugins/track/{n}/plugin/{id}/parameters` | Get plugin parameters | None |
| POST | `/plugins/track/{n}/plugin/{id}/parameter/{param}` | Set plugin parameter | `{"value": 0.5}` |
| POST | `/plugins/track/{n}/plugin/{id}/bypass` | Bypass plugin | `{"bypassed": true}` |

</details>

<details>
<summary><b>📼 Recording Control</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/recording/enable` | Enable/disable global recording | `{"enabled": true}` |
| POST | `/recording/punch` | Enable/disable punch recording | `{"enabled": true}` |
| GET | `/recording/status` | Get recording status | None |

</details>

<details>
<summary><b>🎯 Selection Management</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/selection/track/{n}` | Select track | None |
| POST | `/selection/clear` | Clear selection | None |
| GET | `/selection/current` | Get current selection | None |

</details>

<details>
<summary><b>🔄 Session & Sends</b></summary>

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/session/info` | Get session information | None |
| POST | `/sends/track/{n}/send/{id}` | Control track send | `{"level": 0.8}` |
| GET | `/` | Server info | None |
| GET | `/health` | Health check | None |

</details>

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

<details>
<summary><b>🏗️ Core Architecture</b></summary>

```
ardour-mcp/
├── 🎛️ mcp_server/                 # FastAPI server implementation
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── osc_client.py            # OSC client for Ardour communication
│   ├── osc_listener.py          # OSC feedback listener
│   ├── parameter_conversion.py   # Smart parameter conversion
│   ├── plugin_parameter_mapper.py # Plugin parameter mapping
│   ├── selection_manager.py     # Track selection management
│   └── 🌐 api/                   # API endpoints by feature
│       ├── __init__.py
│       ├── transport.py         # Transport control endpoints
│       ├── track.py            # Track control endpoints
│       ├── plugins.py          # Plugin control endpoints
│       ├── recording.py        # Recording control endpoints
│       ├── selection.py        # Selection management endpoints
│       ├── sends.py            # Sends/routing endpoints
│       └── session.py          # Session management endpoints
```

</details>

<details>
<summary><b>🤖 Client & Tools</b></summary>

```
├── 🤖 mcp_client/                # MCP client implementation
│   ├── ardour_mcp_client.py     # Main MCP client script
│   └── mcp_ardour.json          # MCP manifest file
├── mcp_wrapper.py               # MCP wrapper utilities
```

</details>

<details>
<summary><b>🧪 Testing & Quality</b></summary>

```
├── 🧪 tests/                     # Comprehensive test suite
│   ├── __init__.py
│   ├── test_config.py           # Configuration tests
│   ├── test_osc_client.py       # OSC client tests
│   ├── test_transport_api.py    # Transport API tests
│   ├── test_plugin_control.py   # Plugin control tests
│   ├── test_recording_controls.py # Recording feature tests
│   ├── test_selection_operations.py # Selection management tests
│   ├── test_phase2_features.py  # Advanced feature tests
│   ├── test_phase3_sends.py     # Sends/routing tests
│   ├── debug_*.py              # Debug utilities
│   ├── diagnose_server.py      # Server diagnostics
│   ├── run_all_tests.py        # Test runner
│   └── README.md               # Testing documentation
```

</details>

<details>
<summary><b>🐳 Deployment & Config</b></summary>

```
├── 🐳 Docker & Configuration
│   ├── Dockerfile              # Docker container configuration
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment configuration template
│   └── .env                   # Environment configuration (local)
├── 📚 Documentation
│   ├── docs/                  # Additional documentation
│   ├── PLUGIN_IMPLEMENTATION_PLAN.md # Feature roadmap
│   ├── README_TESTING.md      # Testing documentation
│   └── README.md              # This file
└── 📝 Logs & Utilities
    └── ardour_mcp.log         # Application logs
```

</details>

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

---

<div align="center">

## 🤝 Contributing

We welcome contributions! Here's how to get started:

</div>

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **✨ Make** your changes with proper tests
4. **✅ Test** your changes (`python -m pytest tests/`)
5. **📝 Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **🚀 Push** to the branch (`git push origin feature/amazing-feature`)
7. **📬 Open** a Pull Request

---

<div align="center">

## 📄 License

<img src="https://img.shields.io/badge/License-Dual_License-4a90e2?style=for-the-badge" alt="Dual License">

This project is available under a **dual licensing model**:

### 🏠 Personal Use License
**✅ FREE for personal, educational, and non-commercial use**

- ✅ Personal music production and audio engineering
- ✅ Educational purposes and learning
- ✅ Non-profit organizations and community projects
- ✅ Research and academic use
- ✅ Open source contributions and modifications

### 💼 Commercial Use License
**📧 Permission required for commercial applications**

For commercial use, including but not limited to:
- 🏢 Commercial music production facilities
- 🎬 Professional audio/video production companies
- 🎵 Commercial plugin or software development
- 💰 Revenue-generating services or products
- 🏭 Integration into commercial products

**Please contact the project maintainer for commercial licensing terms.**

---

**📧 Commercial License Inquiries:** [Contact for commercial licensing](ron9hm1@gmail.com)

> **💡 Note:** Contributing to this project does not grant commercial usage rights. Commercial usage requires explicit written permission regardless of contribution status.

## 🙏 Acknowledgments

<table>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/Ardour-DAW-ff6b35?style=flat&logo=ardour" alt="Ardour"/>
<br><b>Ardour DAW Team</b><br>
<sub>OSC Protocol Support</sub>
</td>
<td align="center">
<img src="https://img.shields.io/badge/FastAPI-Framework-009688?style=flat&logo=fastapi" alt="FastAPI"/>
<br><b>FastAPI Team</b><br>
<sub>Excellent Web Framework</sub>
</td>
<td align="center">
<img src="https://img.shields.io/badge/Python-OSC-blue?style=flat&logo=python" alt="Python OSC"/>
<br><b>python-osc</b><br>
<sub>OSC Communication Library</sub>
</td>
</tr>
</table>

## 📞 Support & Community

<img src="https://img.shields.io/badge/Status-Active_Development-orange?style=flat-square" alt="Project Status">

**🚧 This project is under active development!** Some features may not work as expected.

### 🐛 Found a Bug or Issue?

**We want to hear from you!** Your feedback helps improve the project:

1. **🔍 Check Existing Issues** - Search [GitHub Issues](https://github.com/your-repo/issues) first
2. **📝 Create New Issue** - If not found, [open a new issue](https://github.com/your-repo/issues/new) with:
   - 🎯 Clear description of the problem
   - 🔄 Steps to reproduce
   - 💻 Your environment (OS, Python version, Ardour version)
   - 📊 Relevant log output from `ardour_mcp.log`
   - 📋 Expected vs actual behavior

### 💡 Need Help?

**Before reporting issues, try these steps:**

1. 📖 **Check Documentation** - Review this README and `/docs`
2. 🌐 **API Docs** - Visit `http://localhost:8000/docs` for interactive API documentation
3. 📝 **Check Logs** - Review `ardour_mcp.log` for detailed error information
4. 🧪 **Run Tests** - Try `python -m pytest tests/` to identify issues

### 🎯 Feature Requests

Have ideas for new features? We'd love to hear them! Please [create a feature request](https://github.com/Ron-312/ardour-mcp/issues/new) with:
- 🎵 Your use case and workflow
- 🎛️ Detailed description of the desired functionality
- 🎯 How it would improve your DAW control experience

---

<div align="center">

### 🎵 **Happy Music Making with Ardour MCP Server!** 🎵

<img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="Made with Love">

*Empowering musicians and audio engineers with seamless DAW control*

</div>

</div>