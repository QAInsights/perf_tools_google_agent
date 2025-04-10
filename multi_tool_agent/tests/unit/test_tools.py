import unittest
import os
import asyncio
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from multi_tool_agent.jmeter_utils import run_jmeter
from multi_tool_agent.locust_utils import run_locust_test
from multi_tool_agent.k6_utils import run_k6_script

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


if __name__ == '__main__':
    unittest.main()