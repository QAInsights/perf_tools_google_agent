from google.adk.agents import Agent
from typing import Any, Awaitable, Optional
import os
import logging
from .jmeter_utils import run_jmeter
from .k6_utils import run_k6_script
from .locust_utils import run_locust_test
from .gatling_utils import run_gatling_simulation
from dotenv import load_dotenv
from . import prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def execute_jmeter_test(test_file: str, duration: int = 30, threads: int = 10, gui_mode: bool = False) -> str:
    """Execute a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        duration: Duration of the test in seconds (e.g., 30, 60)
        threads: Number of virtual users to simulate
        gui_mode: Whether to run in GUI mode (default: False)
    """
    return await run_jmeter(test_file, duration, threads, non_gui=not gui_mode) # Run in non-GUI mode by default

async def execute_jmeter_test_non_gui(test_file: str, duration: int = 30, threads: int = 10) -> str:
    """Execute a JMeter test in non-GUI mode.

    Args:
        test_file: Path to the JMeter test file (.jmx)
    """
    return await run_jmeter(test_file, duration , threads, non_gui=True)

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
                    headless: bool = os.getenv("LOCUST_HEADLESS", "true").lower() == "true") -> dict:
    """
    Run Locust with the given configuration.
    
    Args:
        test_file: Path to the Locust test file
        host: Target host URL to load test
        users: Number of concurrent users to simulate
        spawn_rate: Rate at which users are spawned per second
        runtime: Duration of the test (e.g., "30s", "1m", "5m")
        headless: Whether to run in headless mode (no web UI)
        
    Returns:
        dict: A dictionary containing status, output, and error information
    """
    return await run_locust_test(test_file, host, users, spawn_rate, runtime, headless)

async def execute_gatling_test(directory_name: str, class_name: Optional[str] = None, runner: str = os.getenv("GATLING_RUNNER", "mvn")) -> str:
    """Run a Gatling simulation.

    Args:
        directory_name: Name of the Gatling simulation directory
        class_name: Optional name of the Gatling simulation class (default: None)
        runner: Optional runner to use (default: mvn) other option: gradle

    Returns:
        str: Gatling simulation output
    """
    return await run_gatling_simulation(directory_name, class_name, runner)

root_agent = Agent(
    name=os.getenv('FEATHERWAND_NAME', 'featherwand_agent'),
    model=os.getenv('FEATHERWAND_MODEL', 'gemini-1.5-pro'),
    description=(
        os.getenv('FEATHERWAND_DESCRIPTION', 'Agent to execute JMeter, k6, Gatling and Locust tests.')
    ),
    instruction=(
        prompt.ROOT_PROMPT 
    ),
    tools=[
        execute_jmeter_test, 
        execute_jmeter_test_non_gui, 
        execute_k6_test, 
        execute_k6_test_with_options, 
        execute_locust_test, 
        execute_gatling_test
    ],
)
