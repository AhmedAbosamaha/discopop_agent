# type: ignore
import copy
import os
import pathlib
import subprocess
from typing import Dict, List
import unittest

import jsonpickle

from discopop_library.result_classes.DetectionResult import DetectionResult
from test.utils.sharing_clauses.clauses_utils import check_clauses_for_FN, check_clauses_for_FP
from test.utils.subprocess_wrapper.command_execution_wrapper import run_cmd
from test.utils.validator_classes.DoAllInfoForValidation import DoAllInfoForValidation
from subprocess import DEVNULL
from discopop_library.ConfigProvider.config_provider import run as run_config_provider
from discopop_library.ConfigProvider.ConfigProviderArguments import ConfigProviderArguments
from discopop_library.DependencyComparator.DependencyComparatorArguments import DependencyComparatorArguments
from discopop_library.DependencyComparator.dependency_comparator import run as run_comparator


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
        run_cmd("./prog", src_dir, env_vars)

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
        self.assertIn("do_all", self.test_output.patterns.__dict__)
        doall_patterns = self.test_output.patterns.__dict__["do_all"]
        # the loop nest: the outer loop starts at line 16
        outer = [p for p in doall_patterns if str(p.start_line).split(":")[-1] == "16"]
        self.assertEqual(len(outer), 1, "the outer loop of the nest is no do-all")
        do_all_pattern = outer[0]

        expected_clauses: Dict[str, List[str]] = {"private": ["j"]}

        with self.subTest("check pattern for FN data sharing clauses"):
            res, msg = check_clauses_for_FN(self, expected_clauses, do_all_pattern)
            self.assertTrue(res, msg)
        with self.subTest("the inner counter is in no other clause"):
            for clause_type in ["shared", "first_private", "last_private"]:
                self.assertNotIn("j", [v.name for v in do_all_pattern.__dict__[clause_type]])

    # def test_deps(self) -> None:
    #     # compare detected dependencies to gold standard
    #     current_dir = pathlib.Path(__file__).parent.resolve()
    #     gold_standard_dir = os.path.join(current_dir, "gold_std")
    #     test_output_dir = os.path.join(self.src_dir, ".discopop", "profiler")
    #     dynamic_gold_std = os.path.join(gold_standard_dir, "dynamic_dependencies.txt")
    #     static_gold_std = os.path.join(gold_standard_dir, "dynamic_dependencies.txt")
    #     dynamic_test_result = os.path.join(test_output_dir, "dynamic_dependencies.txt")
    #     static_test_result = os.path.join(test_output_dir, "dynamic_dependencies.txt")
    #     self.assertEqual(
    #         run_comparator(
    #             DependencyComparatorArguments(
    #                 dynamic_gold_std, static_gold_std, dynamic_test_result, static_test_result, "None", False
    #             )
    #         ),
    #         0,
    #     )
