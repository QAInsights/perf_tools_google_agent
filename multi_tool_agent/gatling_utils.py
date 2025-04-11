import logging
from dotenv import load_dotenv
from pathlib import Path
import subprocess
import platform
from typing import Optional
import os

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def run_gatling_simulation(directory_name: str, class_name: Optional[str] = None, runner: str = os.getenv("GATLING_RUNNER", "mvn")) -> str:
    """Run a Gatling simulation.

    Args:
        directory_name: Name of the Gatling simulation directory
        class_name: Optional name of the Gatling simulation class (default: None)
        runner: Optional runner to use (default: mvn) other option: gradle

    Returns:
        str: Gatling simulation output
    """
    try:
        # Convert to absolute path
        directory_path = Path(directory_name).resolve()
        
        # Validate directory exists
        if not directory_path.exists():
            return f"Error: Directory not found: {directory_name}"
        if not directory_path.is_dir():
            return f"Error: Invalid directory: {directory_name}"

        # Build command
        if runner == 'mvn':
            mvnw_path = directory_path / ('mvnw.cmd' if platform.system() == 'Windows' else 'mvnw')
            if not mvnw_path.exists():
                return f"Error: mvnw not found in {directory_path}"
                
            cmd = [str(mvnw_path)]
            cmd.append('io.gatling:gatling-maven-plugin:test')
        

            if class_name:
                cmd.append(f'-Dgatling.simulationClass={class_name}')
            if directory_path:
                cmd.append(f'-Dgatling.directory={directory_path}')

            # Print the full command for debugging
            logger.debug(f"Executing command: {' '.join(cmd)}")

        if runner == 'gradle':
            gradlew_path = directory_path / ('gradlew.cmd' if platform.system() == 'Windows' else 'gradlew')
            if not gradlew_path.exists():
                return f"Error: gradlew not found in {directory_path}"
                
            cmd = [str(gradlew_path)]
            cmd.append('gatlingRun')
            
            if class_name:
                cmd.append(f'--simulation={class_name}')

            # Print the full command for debugging
            logger.debug(f"Executing command: {' '.join(cmd)}")
        
        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(directory_path))
        
        # Print output for debugging
        logger.debug(f"\nCommand output:")
        logger.debug(f"Return code: {result.returncode}")
        logger.debug(f"Stdout: {result.stdout}")
        logger.debug(f"Stderr: {result.stderr}")

        if result.returncode != 0:
            return f"Error executing Gatling simulation:\n{result.stderr}"
        
        return result.stdout

    except Exception as e:
        return f"Unexpected error: {str(e)}"