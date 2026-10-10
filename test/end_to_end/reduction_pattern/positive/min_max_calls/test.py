# type: ignore
import copy
import os
import pathlib
import unittest

import jsonpickle

from discopop_library.result_classes.DetectionResult import DetectionResult
from test.utils.existence.existence_utils import check_patterns_for_FN, check_patterns_for_FP
from test.utils.subprocess_wrapper.command_execution_wrapper import run_cmd
from discopop_library.ConfigProvider.config_provider import run as run_config_provider
from discopop_library.ConfigProvider.ConfigProviderArguments import ConfigProviderArguments


class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        current_dir = pathlib.Path(__file__).parent.resolve()
        dp_build_dir = run_config_provider(
            ConfigProviderArguments(
                return_dp_build_dir=True,
                return_llvm_bin_dir=False,
                return_full_config=False,
                return_version_string=False,
            )
        )
        env_vars = dict(os.environ)

        src_dir = os.path.join(current_dir, "src")

        # build
        env_vars["CC"] = "discopop_cc"
        env_vars["CXX"] = "discopop_cxx"
        env_vars["DP_PROJECT_ROOT_DIR"] = src_dir
        cmd = "make"
        run_cmd(cmd, src_dir, env_vars)
        # execute instrumented program
        cmd = "./prog"
        run_cmd(cmd, src_dir, env_vars)
        # execute DiscoPoP analysis
        cmd = "discopop_explorer --enable-patterns doall,reduction"
        run_cmd(cmd, os.path.join(src_dir, ".discopop"), env_vars)

        self.src_dir = src_dir
        self.env_vars = env_vars

        test_output_file = os.path.join(self.src_dir, ".discopop", "explorer", "detection_result_dump.json")
        # load detection results
        with open(test_output_file, "r") as f:
            tmp_str = f.read()
        self.test_output: DetectionResult = jsonpickle.decode(tmp_str, keys=True)

    @classmethod
    def tearDownClass(self):
        run_cmd("make veryclean", self.src_dir, self.env_vars)

    def test(self):
        for pattern_type in self.test_output.patterns.__dict__:
            amount_of_identified_patterns = len(self.test_output.patterns.__dict__[pattern_type])
            if pattern_type == "do_all":
                expected_lines = ["1:9"]
                with self.subTest("check for FP"):
                    res, msg = check_patterns_for_FP(
                        self,
                        pattern_type,
                        copy.deepcopy(expected_lines),
                        self.test_output.patterns.__dict__[pattern_type],
                    )
                    self.assertTrue(res, msg)
                with self.subTest("check for FN"):
                    res, msg = check_patterns_for_FN(
                        self,
                        pattern_type,
                        copy.deepcopy(expected_lines),
                        self.test_output.patterns.__dict__[pattern_type],
                    )
                    self.assertTrue(res, msg)
            elif pattern_type == "reduction":
                expected_lines = ["1:14", "1:19", "1:24"]
                with self.subTest("check for FP"):
                    res, msg = check_patterns_for_FP(
                        self,
                        pattern_type,
                        copy.deepcopy(expected_lines),
                        self.test_output.patterns.__dict__[pattern_type],
                    )
                    self.assertTrue(res, msg)
                with self.subTest("check for FN"):
                    res, msg = check_patterns_for_FN(
                        self,
                        pattern_type,
                        copy.deepcopy(expected_lines),
                        self.test_output.patterns.__dict__[pattern_type],
                    )
                    self.assertTrue(res, msg)
                # B23 (discopop_agent/docs/DISCOPOP_BUG_REPORTS.md, 10 Oct 2026): the profiler reported every
                # reduction it found by its minimum / maximum heuristic as a maximum, so `x = fmin(x, a[i])` was
                # given reduction(max:x). The OPERATION is what this test is for: the line alone was right before.
                expected_operations = {
                    "1:14": ["max:largest"],
                    "1:19": ["min:smallest"],
                    "1:24": ["min:smallest_f"],
                }
                found_operations = {
                    pattern.start_line: sorted(str(v.operation) + ":" + v.name for v in pattern.reduction)
                    for pattern in self.test_output.patterns.__dict__[pattern_type]
                }
                with self.subTest("check the reduction operations"):
                    self.assertEqual(found_operations, expected_operations)
            else:
                self.assertEqual(amount_of_identified_patterns, 0)
