from google.adk.agents import Agent
from typing import Any
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import subprocess
from . import prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
async def run_jmeter(test_file: str, non_gui: bool = True) -> str:
    """Run a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        non_gui: Run in non-GUI mode (default: True)

    Returns:
        str: JMeter execution output
    """
    try:
        # Convert to absolute path
        test_file_path = Path(test_file).resolve()
        
        # Validate file exists and is a .jmx file
        if not test_file_path.exists():
            return f"Error: Test file not found: {test_file}"
        if not test_file_path.suffix == '.jmx':
            return f"Error: Invalid file type. Expected .jmx file: {test_file}"

        # Get JMeter binary path from environment
        jmeter_bin = os.getenv('JMETER_BIN', 'jmeter')
        java_opts = os.getenv('JMETER_JAVA_OPTS', '')

        # Log the JMeter binary path and Java options
        logger.info(f"JMeter binary path: {jmeter_bin}")
        logger.debug(f"Java options: {java_opts}")
        
        # Get JMETER_JAVA_OPTS if set
        jmeter_java_opts = os.getenv('JMETER_JAVA_OPTS', '')
        if jmeter_java_opts:
            logger.debug(f"JMETER_JAVA_OPTS: {jmeter_java_opts}")

        # Build command
        cmd = [str(Path(jmeter_bin).resolve())]
        
        if non_gui:
            cmd.extend(['-n'])
        cmd.extend(['-t', str(test_file_path)])

        # Log the full command for debugging
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        if non_gui:
            # For non-GUI mode, capture output
            env = os.environ.copy()
            if jmeter_java_opts:
                env['JAVA_OPTS'] = f"{java_opts} {jmeter_java_opts}".strip()
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            # Log output for debugging
            logger.debug("Command output:")
            logger.debug(f"Return code: {result.returncode}")
            logger.debug(f"Stdout: {result.stdout}")
            logger.debug(f"Stderr: {result.stderr}")

            if result.returncode != 0:
                return f"Error executing JMeter test:\n{result.stderr}"
            
            return result.stdout
        else:
            # For GUI mode, start process without capturing output
            subprocess.Popen(cmd)
            return "JMeter GUI launched successfully"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

async def execute_jmeter_test(test_file: str, gui_mode: bool = False) -> str:
    """Execute a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        gui_mode: Whether to run in GUI mode (default: False)
    """
    return await run_jmeter(test_file, non_gui=not gui_mode)  # Run in non-GUI mode by default

async def execute_jmeter_test_non_gui(test_file: str) -> str:
    """Execute a JMeter test in non-GUI mode.

    Args:
        test_file: Path to the JMeter test file (.jmx)
    """
    return await run_jmeter(test_file, non_gui=True)

async def run_k6_script(script_file: str, duration: str = "30s", vus: int = 10) -> str:
    """Run a k6 load test script.

    Args:
        script_file: Path to the k6 test script (.js)
        duration: Duration of the test (e.g., "30s", "1m", "5m")
        vus: Number of virtual users to simulate

    Returns:
        str: k6 execution output
    """
    try:
        # Convert to absolute path
        script_file_path = Path(script_file).resolve()
        
        # Validate file exists and is a .js file
        if not script_file_path.exists():
            return f"Error: Script file not found: {script_file}"
        if not script_file_path.suffix == '.js':
            return f"Error: Invalid file type. Expected .js file: {script_file}"

        # Get k6 binary path from environment
        k6_bin = os.getenv('K6_BIN', 'k6')
        
        # Print the k6 binary path for debugging
        logger.debug(f"k6 binary path: {k6_bin}")

        # Build command
        cmd = [str(Path(k6_bin).resolve())]
        cmd.extend(['run'])
        cmd.extend(['-d', duration])
        cmd.extend(['-u', str(vus)])
        cmd.extend([str(script_file_path)])

        # Print the full command for debugging
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output for debugging
        logger.debug(f"\nCommand output:")
        logger.debug(f"Return code: {result.returncode}")
        logger.debug(f"Stdout: {result.stdout}")
        logger.debug(f"Stderr: {result.stderr}")

        if result.returncode != 0:
            return f"Error executing k6 test:\n{result.stderr}"
        
        return result.stdout

    except Exception as e:
        return f"Unexpected error: {str(e)}"

async def execute_k6_test(script_file: str, duration: str = "30s", vus: int = 10) -> str:
    """Execute a k6 load test.

    Args:
        script_file: Path to the k6 test script (.js)
        duration: Duration of the test (e.g., "30s", "1m", "5m")
        vus: Number of virtual users to simulate
    """
    return await run_k6_script(script_file, duration, vus)

async def execute_k6_test_with_options(script_file: str, duration: str, vus: int) -> str:
    """Execute a k6 load test with custom duration and VUs.

    Args:
        script_file: Path to the k6 test script (.js)
        duration: Duration of the test (e.g., "30s", "1m", "5m")
        vus: Number of virtual users to simulate
    """
    return await run_k6_script(script_file, duration, vus)

async def execute_locust_test(test_file: str, host: str = os.getenv("LOCUST_HOST", "http://localhost:8089"), 
                    users: int = int(os.getenv("LOCUST_USERS", "100")), 
                    spawn_rate: int = int(os.getenv("LOCUST_SPAWN_RATE", "10")), 
                    runtime: str = os.getenv("LOCUST_RUNTIME", "30s"), 
                    headless: bool = os.getenv("LOCUST_HEADLESS", "true").lower() == "true") -> Any:
    """
    Run Locust with the given configuration.
    
    Args:
        test_file: Path to the Locust test file
        host: Target host URL to load test
        users: Number of concurrent users to simulate
        spawn_rate: Rate at which users are spawned per second
        runtime: Duration of the test (e.g., "30s", "1m", "5m")
        headless: Whether to run in headless mode (no web UI)
    """
    locust_bin = os.getenv("LOCUST_BIN", "locust")
    cmd = [locust_bin, "-f", test_file, "--host", host]
    
    if headless:
        cmd.extend(["--headless"])
        cmd.extend(["-u", str(users)])
        cmd.extend(["-r", str(spawn_rate)])
        cmd.extend(["-t", runtime])

    logging.debug(f"Executing command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "output": e.stdout,
            "error": e.stderr
        }

root_agent = Agent(
    name=os.getenv('FEATHERWAND_NAME', 'featherwand_agent'),
    model=os.getenv('FEATHERWAND_MODEL', 'gemini-2.0-flash-exp'),
    description=(
        os.getenv('FEATHERWAND_DESCRIPTION', 'Agent to execute JMeter, k6, and Locust tests.')
    ),
    instruction=(
        prompt.ROOT_PROMPT 
    ),
    tools=[execute_jmeter_test, execute_jmeter_test_non_gui, execute_k6_test, execute_k6_test_with_options, execute_locust_test],
)