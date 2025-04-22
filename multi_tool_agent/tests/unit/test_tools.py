import unittest
import os
import asyncio
import subprocess
import tempfile # Added
from unittest.mock import patch, MagicMock, AsyncMock, call # Added AsyncMock, call
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

# Assume google.adk.types.File exists and can be mocked
try:
    from google.adk.types import File
except ImportError:
    # Create a dummy File class for environments where ADK is not installed
    class File:
        def __init__(self, name="mock_file", content=b""):
            self.name = name
            self._content = content
        def save_to(self, path):
            with open(path, 'wb') as f:
                f.write(self._content)
        def __repr__(self):
            return f"MockFile(name='{self.name}')"

# Import agent functions to be tested
from multi_tool_agent.agent import (
    execute_jmeter_test,
    execute_jmeter_test_non_gui,
    execute_k6_test,
    execute_k6_test_with_options,
    execute_locust_test
)

from multi_tool_agent.jmeter_utils import run_jmeter
from multi_tool_agent.locust_utils import run_locust_test
from multi_tool_agent.k6_utils import run_k6_script
from multi_tool_agent.gatling_utils import run_gatling_simulation

class TestJMeterUtils(IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_jmx = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample", "hello.jmx")
        
    async def test_run_jmeter(self):
        """Test running a JMeter test"""
        with patch('multi_tool_agent.jmeter_utils.run_jmeter', return_value="Test completed successfully") as mock_run:
            result = await run_jmeter(self.test_jmx)
            self.assertIn("end of run", result.lower())
            
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.resolve')
    async def test_run_jmeter_file_not_found(self, mock_resolve, mock_exists):
        """Test JMeter with invalid file"""
        mock_exists.return_value = False
        mock_resolve.return_value = Path("/invalid/path/test.jmx")
        result = await run_jmeter("invalid.jmx")
        self.assertIn("Error: Test file not found", result)

class TestLocustUtils(IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample", "hello.py")
    
    async def test_run_locust_test(self):
        """Test running a Locust test"""
        mock_output = "Locust test output"
        mock_result = MagicMock(stdout=mock_output, stderr="", returncode=0)
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            result = await run_locust_test(self.test_file)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["output"], mock_output)
            self.assertEqual(result["error"], "")
    
    async def test_run_locust_test_failure(self):
        """Test Locust test failure"""
        error_msg = None
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd", error_msg)) as mock_run:
            result = await run_locust_test(self.test_file)
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error"], None)  # Changed to expect None
            self.assertIsNone(result["output"])  # Changed to expect None


class TestK6Utils(IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_js = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample", "hello.js")
    
    async def test_run_k6_script(self):
        """Test running a k6 script"""
        mock_output = "k6 test output"
        with patch('subprocess.run', return_value=MagicMock(stdout=mock_output, stderr="", returncode=0)) as mock_run:
            result = await run_k6_script(self.test_js)
            self.assertIsInstance(result, str)
            self.assertIn("output", result.lower())

    async def test_run_k6_script_failure(self):
        """Test k6 script failure"""
        error_msg = "k6 test failed"
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd", error_msg)) as mock_run:
            result = await run_k6_script(self.test_js)
            self.assertIsInstance(result, str)
            self.assertIn("error", result.lower())

class TestGatlingUtils(IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample", "gatling-maven-plugin-demo-java-main")
        self.test_class = "BasicSimulation"
    
    async def test_run_gatling_simulation(self):
        """Test running a Gatling simulation"""
        mock_output = "Gatling simulation output"
        with patch('subprocess.run', return_value=MagicMock(stdout=mock_output, stderr="", returncode=0)) as mock_run:
            result = await run_gatling_simulation(self.test_directory, self.test_class)
            self.assertIsInstance(result, str)
            self.assertIn("output", result.lower())
    
    async def test_run_gatling_simulation_failure(self):
        """Test Gatling simulation failure"""
        error_msg = "Gatling simulation failed"
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd", error_msg)) as mock_run:
            result = await run_gatling_simulation(self.test_directory, self.test_class)
            self.assertIsInstance(result, str)
            self.assertIn("error", result.lower())

# --- Existing Test Classes (TestJMeterUtils, TestLocustUtils, etc.) ---
# --- Should remain above this line ---


# --- New Test Class for File Upload Agent Tools ---
class TestFileUploadAgentTools(IsolatedAsyncioTestCase):

    @patch('multi_tool_agent.agent.run_jmeter', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_jmeter_test_file_upload(self, mock_tempfile, mock_remove, mock_run_jmeter):
        """Test execute_jmeter_test with ADK File upload"""
        # Setup Mocks
        mock_adk_file = MagicMock(spec=File)
        mock_adk_file.name = "test.jmx"

        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_jmeter_file.jmx"
        # Configure the context manager mock
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = "JMeter test finished successfully."
        mock_run_jmeter.return_value = expected_result

        # Call function
        result = await execute_jmeter_test(mock_adk_file, gui_mode=False) # Default non-gui

        # Assertions
        mock_tempfile.assert_called_once_with(suffix=".jmx", delete=False)
        mock_adk_file.save_to.assert_called_once_with(mock_temp_file_obj.name)
        mock_run_jmeter.assert_called_once_with(mock_temp_file_obj.name, non_gui=True)
        mock_remove.assert_called_once_with(mock_temp_file_obj.name)
        self.assertEqual(result, expected_result)

    @patch('multi_tool_agent.agent.run_jmeter', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_jmeter_test_non_gui_file_upload(self, mock_tempfile, mock_remove, mock_run_jmeter):
        """Test execute_jmeter_test_non_gui with ADK File upload"""
        # Setup Mocks
        mock_adk_file = MagicMock(spec=File)
        mock_adk_file.name = "test_non_gui.jmx"

        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_jmeter_non_gui.jmx"
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = "JMeter non-GUI test finished successfully."
        mock_run_jmeter.return_value = expected_result

        # Call function
        result = await execute_jmeter_test_non_gui(mock_adk_file)

        # Assertions
        mock_tempfile.assert_called_once_with(suffix=".jmx", delete=False)
        mock_adk_file.save_to.assert_called_once_with(mock_temp_file_obj.name)
        mock_run_jmeter.assert_called_once_with(mock_temp_file_obj.name, non_gui=True)
        mock_remove.assert_called_once_with(mock_temp_file_obj.name)
        self.assertEqual(result, expected_result)

    @patch('multi_tool_agent.agent.run_k6_script', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_k6_test_file_upload(self, mock_tempfile, mock_remove, mock_run_k6):
        """Test execute_k6_test with ADK File upload"""
        # Setup Mocks
        mock_adk_file = MagicMock(spec=File)
        mock_adk_file.name = "test.js"

        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_k6_script.js"
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = "k6 test finished."
        mock_run_k6.return_value = expected_result
        duration = "10s"
        vus = 5

        # Call function
        result = await execute_k6_test(mock_adk_file, duration=duration, vus=vus)

        # Assertions
        mock_tempfile.assert_called_once_with(suffix=".js", delete=False)
        mock_adk_file.save_to.assert_called_once_with(mock_temp_file_obj.name)
        mock_run_k6.assert_called_once_with(mock_temp_file_obj.name, duration, vus)
        mock_remove.assert_called_once_with(mock_temp_file_obj.name)
        self.assertEqual(result, expected_result)

    @patch('multi_tool_agent.agent.run_k6_script', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_k6_test_with_options_file_upload(self, mock_tempfile, mock_remove, mock_run_k6):
        """Test execute_k6_test_with_options with ADK File upload"""
        # Setup Mocks
        mock_adk_file = MagicMock(spec=File)
        mock_adk_file.name = "test_options.js"

        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_k6_options.js"
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = "k6 options test finished."
        mock_run_k6.return_value = expected_result
        duration = "1m"
        vus = 20

        # Call function
        result = await execute_k6_test_with_options(mock_adk_file, duration=duration, vus=vus)

        # Assertions
        mock_tempfile.assert_called_once_with(suffix=".js", delete=False)
        mock_adk_file.save_to.assert_called_once_with(mock_temp_file_obj.name)
        mock_run_k6.assert_called_once_with(mock_temp_file_obj.name, duration, vus)
        mock_remove.assert_called_once_with(mock_temp_file_obj.name)
        self.assertEqual(result, expected_result)

    @patch('multi_tool_agent.agent.run_locust_test', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_locust_test_file_upload(self, mock_tempfile, mock_remove, mock_run_locust):
        """Test execute_locust_test with ADK File upload"""
        # Setup Mocks
        mock_adk_file = MagicMock(spec=File)
        mock_adk_file.name = "test.py"

        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_locust_file.py"
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = {"status": "success", "output": "Locust finished", "error": ""}
        mock_run_locust.return_value = expected_result
        host = "http://example.com"
        users = 50
        spawn_rate = 5
        runtime = "2m"
        headless = False

        # Call function
        result = await execute_locust_test(mock_adk_file, host=host, users=users, spawn_rate=spawn_rate, runtime=runtime, headless=headless)

        # Assertions
        mock_tempfile.assert_called_once_with(suffix=".py", delete=False)
        mock_adk_file.save_to.assert_called_once_with(mock_temp_file_obj.name)
        mock_run_locust.assert_called_once_with(mock_temp_file_obj.name, host, users, spawn_rate, runtime, headless)
        mock_remove.assert_called_once_with(mock_temp_file_obj.name)
        self.assertEqual(result, expected_result)

    # Example test for cleanup failure (optional but good practice)
    @patch('multi_tool_agent.agent.run_jmeter', new_callable=AsyncMock)
    @patch('multi_tool_agent.agent.os.remove')
    @patch('multi_tool_agent.agent.tempfile.NamedTemporaryFile')
    async def test_execute_jmeter_test_cleanup_failure(self, mock_tempfile, mock_remove, mock_run_jmeter):
        """Test execute_jmeter_test handles os.remove failure gracefully."""
        mock_adk_file = MagicMock(spec=File)
        mock_temp_file_obj = MagicMock()
        mock_temp_file_obj.name = "/tmp/fake_jmeter_cleanup.jmx"
        mock_tempfile_cm = MagicMock()
        mock_tempfile_cm.__enter__.return_value = mock_temp_file_obj
        mock_tempfile.return_value = mock_tempfile_cm

        expected_result = "JMeter test done, cleanup failed."
        mock_run_jmeter.return_value = expected_result
        mock_remove.side_effect = OSError("Permission denied") # Simulate failure

        # Call function
        result = await execute_jmeter_test(mock_adk_file)

        # Assertions
        mock_tempfile.assert_called_once()
        mock_adk_file.save_to.assert_called_once()
        mock_run_jmeter.assert_called_once()
        mock_remove.assert_called_once_with(mock_temp_file_obj.name) # os.remove was called
        self.assertEqual(result, expected_result) # Function should still return result


if __name__ == '__main__':
    unittest.main()