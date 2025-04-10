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