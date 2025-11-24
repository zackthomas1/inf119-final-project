import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import run_generated_tests
from agents.coder_agent import CoderAgent
from orchestrator import run_pipeline
from mcp_client import MCPClient

class TestUtilsRunTests(unittest.TestCase):
    @patch('subprocess.run')
    def test_run_generated_tests_pass(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Tests passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, output = run_generated_tests("dummy_path")
        self.assertTrue(success)
        self.assertIn("Tests passed", output)

    @patch('subprocess.run')
    def test_run_generated_tests_fail(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Tests failed"
        mock_run.return_value = mock_result

        success, output = run_generated_tests("dummy_path")
        self.assertFalse(success)
        self.assertIn("Tests failed", output)

class TestCoderAgentFixCode(unittest.TestCase):
    def setUp(self):
        self.mock_mcp_client = MagicMock(spec=MCPClient)
        self.coder_agent = CoderAgent(self.mock_mcp_client)

    def test_fix_code_calls_model(self):
        self.mock_mcp_client.call_model.return_value = "def fixed(): pass"
        
        result = self.coder_agent.fix_code("original", "error", "reqs")
        
        self.assertEqual(result, "def fixed(): pass")
        # Check if error output is in the prompt
        call_args = self.mock_mcp_client.call_model.call_args
        messages = call_args[0][1]
        user_content = messages[1]['content']
        self.assertIn("error", user_content)
        self.assertIn("original", user_content)

class TestOrchestratorSelfHealing(unittest.TestCase):
    @patch('orchestrator.PlannerAgent')
    @patch('orchestrator.CoderAgent')
    @patch('orchestrator.TesterAgent')
    @patch('orchestrator.MCPClient')
    @patch('orchestrator.UsageTracker')
    @patch('orchestrator.run_generated_tests')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_pipeline_self_healing_success(self, mock_makedirs, mock_file, mock_run_tests, 
                                           mock_usage, mock_mcp, mock_tester_cls, mock_coder_cls, mock_planner_cls):
        # Setup mocks
        mock_coder = mock_coder_cls.return_value
        mock_coder.generate_code.return_value = "code_v1"
        mock_coder.fix_code.return_value = "code_fixed"
        
        mock_tester = mock_tester_cls.return_value
        mock_tester.generate_tests.return_value = "tests"
        
        mock_planner = mock_planner_cls.return_value
        mock_planner.create_plan.return_value = {}

        # run_tests returns False (fail) first, then True (pass)
        mock_run_tests.side_effect = [(False, "error"), (True, "success")]

        run_pipeline("requirements")

        # Verify fix_code was called
        mock_coder.fix_code.assert_called_once()
        
        # Verify file was written with fixed code
        # We expect open to be called for generated_app.py (initial), test_generated_app.py, generated_app.py (fixed)
        # Checking if write was called with "code_fixed"
        handle = mock_file()
        handle.write.assert_any_call("code_fixed")

    @patch('orchestrator.PlannerAgent')
    @patch('orchestrator.CoderAgent')
    @patch('orchestrator.TesterAgent')
    @patch('orchestrator.MCPClient')
    @patch('orchestrator.UsageTracker')
    @patch('orchestrator.run_generated_tests')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_pipeline_self_healing_max_retries(self, mock_makedirs, mock_file, mock_run_tests, 
                                               mock_usage, mock_mcp, mock_tester_cls, mock_coder_cls, mock_planner_cls):
        # Setup mocks
        mock_coder = mock_coder_cls.return_value
        mock_coder.generate_code.return_value = "code_v1"
        mock_coder.fix_code.return_value = "code_fixed"
        
        mock_tester = mock_tester_cls.return_value
        mock_tester.generate_tests.return_value = "tests"
        
        mock_planner = mock_planner_cls.return_value
        mock_planner.create_plan.return_value = {}

        # run_tests always fails
        mock_run_tests.return_value = (False, "error")

        run_pipeline("requirements")

        # Logic in orchestrator:
        # for attempt in range(MAX_FIX_RETRIES): # 3
        #    success = run_tests()
        #    if success: break
        #    if attempt < MAX_FIX_RETRIES - 1:
        #        fix_code()
        
        # i=0: fail, fix
        # i=1: fail, fix
        # i=2: fail, no fix
        
        self.assertEqual(mock_coder.fix_code.call_count, 2)

if __name__ == '__main__':
    unittest.main()
