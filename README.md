# AI-NOC-Assistant

## Overview
This project demonstrates how to use MCP (Model Context Protocol) servers and agents to automate real-world IT operations tasks. It features a modular, multi-agent system that orchestrates ServiceNow incident management and Cisco network troubleshooting, making it a practical reference for anyone interested in scalable automation and AI-driven workflows.

## Features
- **ServiceNow Incident Analysis**: Fetch and summarize incident details using an MCP agent.
- **Cisco Diagnostics**: Run safe, read-only troubleshooting commands on Cisco devices via an agent.
- **Multi-Agent Orchestration**: Coordinate between ITSM and network agents for end-to-end workflows.
- **Streamlit UI**: Simple web interface for interactive troubleshooting and RCA (Root Cause Analysis).
- **Secure Configuration**: All secrets and credentials are managed via environment variables.

## Project Structure
```
MCP-test/final-version/
├── executeMasterAgent.py      # CLI entry for master agent
├── masterAgent.py            # Orchestrator agent (ServiceNow + Cisco)
├── NAA2.py                   # Cisco troubleshooting agent
├── snowAgent2.py             # ServiceNow incident agent
├── streamlit_app.py          # Streamlit web UI
```

## How It Works
- **Agents** are built using LangChain and MCP, each with a clear system prompt and toolset.
- **masterAgent** coordinates between the ServiceNow and Cisco agents, combining their outputs for comprehensive responses.
- **Streamlit UI** provides a chat-like interface for users to interact with the system.

## Getting Started
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables** (see `.env.example`):
   - `Model`, `GROQ_API_KEY`, `SN_INSTANCE`, `SN_USER`, `SN_PASS`, etc.
4. **Run the Streamlit app**:
   ```bash
   streamlit run MCP-test/final-version/streamlit_app.py
   ```
5. **Or use the CLI**:
   ```bash
   python MCP-test/final-version/executeMasterAgent.py
   ```

## Example Use Cases
- Investigate a ServiceNow incident (e.g., "Investigate INC0976270")
- Diagnose a router CPU issue
- Analyze interface flapping
- Fetch incident details and correlate with live diagnostics

## Contributing
Pull requests and suggestions are welcome! If you have questions or want to collaborate, feel free to connect.

## License
This project is open source and available under the MIT License.
