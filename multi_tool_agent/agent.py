from google.adk.agents import Agent
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import subprocess


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
def run_jmeter(test_file: str, non_gui: bool = True) -> str:
    """Run a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        non_gui: Run in non-GUI mode (default: True)
    """
    try:
        # Enhanced file validation
        try:
            test_file_path = Path(test_file).resolve()
            if not test_file_path.exists():
                raise FileNotFoundError(f"Test file not found: {test_file}")
            if not test_file_path.is_file():
                raise ValueError(f"Path is not a file: {test_file}")
            if test_file_path.suffix != '.jmx':
                raise ValueError(f"Invalid file type. Expected .jmx file: {test_file}")
            
            # Verify JMeter binary exists
            jmeter_bin = os.getenv('JMETER_BIN', 'jmeter.bat')
            jmeter_bin_path = Path(jmeter_bin).resolve()
            if not jmeter_bin_path.exists():
                raise FileNotFoundError(f"JMeter binary not found: {jmeter_bin}")
                
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return f"Error: {str(e)}"

        # Get Java options from environment
        java_opts = os.getenv('JMETER_JAVA_OPTS', '')

        # Log the JMeter binary path and Java options
        logger.info(f"JMeter binary path: {jmeter_bin}")
        logger.info(f"Java options: {java_opts}")

        # Build command
        cmd = [str(jmeter_bin_path)]
        
        
        if non_gui:
            cmd.extend(['-n'])
        cmd.extend(['-t', str(test_file_path)])

        # Log the full command for debugging
        logger.info(f"Executing command: {' '.join(cmd)}")
        logger.info(f"Full command list: {cmd}")
        logger.info(f"Working directory: {os.path.dirname(jmeter_bin)}")
        
        if non_gui:
            logger.info("Running JMeter in non-GUI mode")
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(jmeter_bin),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Get return code
            return_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
            
            # Log output for debugging
            logger.info("JMeter test completed")
            logger.info(f"Test completed with return code: {return_code}")
            logger.debug(f"Stdout preview: {stdout[:200]}")
            logger.debug(f"Stderr preview: {stderr[:200]}")

            if return_code != 0:
                return f"Error executing JMeter test:\n{stderr}"
            
            return stdout
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Unexpected error executing JMeter:\n{error_details}")
        return f"Unexpected error executing JMeter: {str(e)}\nFull error details have been logged"

def execute_jmeter_test(test_file: str, gui_mode: bool = False) -> str:
    """Execute a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        gui_mode: Whether to run in GUI mode (default: False)
    """
    return run_jmeter(test_file, non_gui=not gui_mode)  # Run in non-GUI mode by default



root_agent = Agent(
    name="jmeter_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent to execute JMeter tests."
    ),
    instruction=(
        "I can execute JMeter tests."
    ),
    tools=[execute_jmeter_test],
)