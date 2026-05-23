
from fastmcp import FastMCP
import subprocess
import os
from netmiko import ConnectHandler
import psutil
from netmiko import ConnectHandler
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SN_INSTANCE = os.getenv("SN_INSTANCE")
SN_API = os.getenv("SN_API", "/api/now/table/incident")
SN_USER = os.getenv("SN_USER")
SN_PASS = os.getenv("SN_PASS")


mcp = FastMCP("Local Security MCP")

# =====================================================
# GET INCIDENT DETAILS
# =====================================================

@mcp.tool
def get_incident_details(incident_number: str) -> dict:
    """
    Fetch ServiceNow incident details using incident number.

    Example:
    - INC0012345
    """

    print(f"FETCHING INCIDENT -> {incident_number}")

    if not incident_number:

        return {
            "status": "failure",
            "message": "incident_number is required"
        }

    url = (
        f"{SN_INSTANCE}{SN_API}"
        f"?sysparm_query=number={incident_number}"
    )

    headers = {
        "Accept": "application/json"
    }

    try:

        response = requests.get(
            url,
            auth=HTTPBasicAuth(SN_USER, SN_PASS),
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        results = response.json().get("result", [])

        if not results:

            return {
                "status": "failure",
                "message": f"No incident found for {incident_number}"
            }

        incident = results[0]

        return {

            "status": "success",

            "incident_number": incident.get("number"),

            "short_description": incident.get("short_description"),

            "description": incident.get("description"),

            "state": incident.get("state"),

            "priority": incident.get("priority"),

            "assigned_to": incident.get(
                "assigned_to",
                {}
            ).get("display_value"),

            "assignment_group": incident.get(
                "assignment_group",
                {}
            ).get("display_value"),

            "sys_id": incident.get("sys_id"),

            "opened_at": incident.get("opened_at")
        }

    except requests.exceptions.RequestException as e:

        return {
            "status": "failure",
            "message": str(e)
        }


@mcp.tool
def cpu_usage() -> str:
    """
    Get current CPU utilization percentage (overall and per core).
    """
    overall = psutil.cpu_percent(interval=1)
    per_core = psutil.cpu_percent(interval=0, percpu=True)
    cores_info = ", ".join(f"Core {i}: {p}%" for i, p in enumerate(per_core))
    return f"Overall CPU: {overall}%\n{cores_info}"


@mcp.tool
def memory_usage() -> str:
    """
    Get current memory (RAM) utilization details.
    """
    mem = psutil.virtual_memory()
    return (
        f"Total: {mem.total / (1024**3):.2f} GB\n"
        f"Used: {mem.used / (1024**3):.2f} GB\n"
        f"Available: {mem.available / (1024**3):.2f} GB\n"
        f"Usage: {mem.percent}%"
    )

import paramiko
PASSWORD=os.getenv("Device_PASSWORD")
CISCO_USER_NAME=os.getenv("CISCO_USER_NAME")

'''
@mcp.tool
def ping_device(host_ip: str, count: int = 4, timeout: int = 4) -> str:
    """
    Use this tool ONLY when the user wants to test network reachability or ping a device.
    Example:
    - ping 10.1.1.1
    - check if device is reachable
    """
    try:
        # Construct the ping command based on the operating system
            # Windows: -n for count, -w for timeout in milliseconds
        command = ['ping', '-n', str(count), '-w', str(timeout * 1000), host_ip]
        
        output = subprocess.run(command, capture_output=True, text=True, timeout=count * timeout + 5)
        return output.stdout.strip() if output.returncode == 0 else output.stderr.strip() or output.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"Ping to {host_ip} timed out after {count * timeout + 5} seconds"
    except Exception as e:
        return f"An error occurred while trying to ping {host_ip}: {e}"
'''
from pythonping import ping

@mcp.tool
def ping_device(host_ip: str) -> str:
    """
    Use this tool ONLY when the user wants to test network reachability or ping a device.
    Example:
    - ping 10.1.1.1
    - check if device is reachable
    """
    print("PING TOOL CALLED")
    try:
        response = ping(host_ip, count=2, timeout=1)

        return str(response)

    except Exception as e:
        return f"Ping failed: {e}"

@mcp.tool(
    name="ssh_connect",
    description="""
    Use this tool ONLY when the user explicitly asks to SSH into a device
    or run commands remotely.

    REQUIRED:
    - host_ip
    - command

    Examples:
    - show ip interface brief
    - run show version on router
    """
)
def ssh_connect(
    host_ip: str,
    command: str,
    username: str = "admin",
    password: str = "bgp007"
) -> str:
    """
    SSH to a network device and run a command. All parameters are required.
    """
    missing = []
    if not host_ip:
        missing.append("host_ip")
    if not command:
        missing.append("command")
    if not username:
        missing.append("username")
    if not password:
        missing.append("password")
    if missing:
        return f"Missing required parameter(s): {', '.join(missing)}. Please provide all connection details."
    device = {
        "device_type": "cisco_ios",
        "host": host_ip,
        "username": username,
        "password": password,
    }
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command, read_timeout=30)
        return output
    except Exception as e:
        return f"SSH connection or command failed: {e}"

if __name__ == "__main__":
    mcp.run()