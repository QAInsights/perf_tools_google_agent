import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import subprocess

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_jmeter(test_file: str, duration: int = 30, threads: int = 10, non_gui: bool = True) -> str:
    """Run a JMeter test.

    Args:
        test_file: Path to the JMeter test file (.jmx)
        duration: Duration of the test in seconds (e.g., 30, 60)
        threads: Number of virtual users to simulate
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
        cmd.extend(['-J', f"threads={str(threads)}"])
        cmd.extend(['-J', f"duration={str(duration)}"])

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
