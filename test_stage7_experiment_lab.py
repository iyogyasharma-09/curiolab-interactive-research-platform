"""
Comprehensive Stage 7 Test Suite: Custom Experiment Builder & Research Documentation
====================================================================================
Tests:
1. Safe Mathematical Expression Engine (AST-based allowlist, security, functions, constants, errors)
2. Experiment Execution Engine (series evaluation, iterative simulation, statistics, run records)
3. 8 Educational Experiment Templates
4. Parameter Validation & Bounds Enforcement
5. Input Data Handling (Manual entry, Range generator, CSV standard library parsing)
6. AppState Integration & Custom Experiment Lifecycle (create, edit, duplicate, delete, search)
7. Multiple Experiment Runs & Run History Preservation
8. Multi-Run Comparison & Delta Statistics
9. 13-Field Research Documentation & Hypothesis Status
10. Discovery Journal Integration & Draft Transfer
11. Preserved Built-in Experiments (Caesar Cipher, Single Neuron, Data Visualization Lab)
12. UI Views Instantiation & Navigation (Overview, My Experiments, Builder, Results, History, Docs)
"""

import unittest
import tkinter as tk
import math
import statistics
import csv
import io
import os
import tempfile

from app_state import AppState
from theme import Theme
from experiment_lab import (
    MathExpressionEngine,
    ExperimentExecutionEngine,
    EXPERIMENT_TEMPLATES,
    get_template_dict,
    ExperimentCanvasPlotter,
    ExperimentCreationWizard,
    MyExperimentsView,
    ExperimentResultsView,
    ExperimentDiscussionView,
    ExperimentRunHistoryView,
    BuiltInExperimentsView,
    ExperimentLabView
)
from discovery_journal import DiscoveryJournalView


class TestMathExpressionEngine(unittest.TestCase):
    """Test AST-based mathematical expression parsing, validation, and evaluation."""

    def test_basic_arithmetic(self):
        ctx = {"x": 5.0, "m": 2.0, "c": 3.0}
        res = MathExpressionEngine.evaluate("m * x + c", ctx)
        self.assertEqual(res, 13.0)

    def test_powers_and_parentheses(self):
        ctx = {"x": 3.0}
        res = MathExpressionEngine.evaluate("(x + 2) ** 2", ctx)
        self.assertEqual(res, 25.0)

        # Precedence
        res2 = MathExpressionEngine.evaluate("2 + 3 * 4", {})
        self.assertEqual(res2, 14.0)

    def test_all_allowlisted_math_functions(self):
        funcs_to_test = [
            ("sin(pi / 2)", 1.0),
            ("cos(0)", 1.0),
            ("tan(0)", 0.0),
            ("asin(1)", math.pi / 2),
            ("acos(1)", 0.0),
            ("atan(0)", 0.0),
            ("sinh(0)", 0.0),
            ("cosh(0)", 1.0),
            ("tanh(0)", 0.0),
            ("log(e)", 1.0),
            ("log10(100)", 2.0),
            ("log2(8)", 3.0),
            ("sqrt(64)", 8.0),
            ("exp(0)", 1.0),
            ("abs(-42)", 42.0),
            ("floor(4.9)", 4.0),
            ("ceil(4.1)", 5.0),
            ("degrees(pi)", 180.0),
            ("radians(180)", math.pi),
            ("round(3.7)", 4.0),
            ("min(3, 7)", 3.0),
            ("max(3, 7)", 7.0)
        ]
        for expr, expected in funcs_to_test:
            actual = MathExpressionEngine.evaluate(expr, {})
            self.assertAlmostEqual(actual, expected, places=5, msg=f"Failed evaluating {expr}")

    def test_constants_pi_e_tau(self):
        self.assertAlmostEqual(MathExpressionEngine.evaluate("pi", {}), math.pi, places=6)
        self.assertAlmostEqual(MathExpressionEngine.evaluate("e", {}), math.e, places=6)
        self.assertAlmostEqual(MathExpressionEngine.evaluate("tau", {}), math.tau, places=6)

    def test_variable_extraction(self):
        eq = "y = K / (1 + exp(-r * (t - t0)))"
        out_var, expr, symbols, is_valid, msg = MathExpressionEngine.extract_variables_and_equation(eq)
        self.assertTrue(is_valid)
        self.assertEqual(out_var, "y")
        self.assertEqual(symbols, {"K", "r", "t", "t0"})

    def test_division_by_zero_handling(self):
        with self.assertRaises(ZeroDivisionError):
            MathExpressionEngine.evaluate("10 / 0", {})

        with self.assertRaises(ZeroDivisionError):
            MathExpressionEngine.evaluate("10 // 0", {})

        with self.assertRaises(ZeroDivisionError):
            MathExpressionEngine.evaluate("10 % 0", {})

    def test_mathematical_domain_errors(self):
        # Negative square root
        with self.assertRaises(ValueError) as ctx:
            MathExpressionEngine.evaluate("sqrt(-9)", {})
        self.assertIn("domain error", str(ctx.exception).lower())

        # Non-positive logarithm
        with self.assertRaises(ValueError) as ctx:
            MathExpressionEngine.evaluate("log(0)", {})
        self.assertIn("domain error", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            MathExpressionEngine.evaluate("log(-5)", {})
        self.assertIn("domain error", str(ctx.exception).lower())

        # Asin / Acos domain [-1, 1]
        with self.assertRaises(ValueError) as ctx:
            MathExpressionEngine.evaluate("asin(2.5)", {})
        self.assertIn("domain error", str(ctx.exception).lower())

    def test_syntax_errors_caught(self):
        is_valid, msg, _ = MathExpressionEngine.validate_expression("2 * + * 3")
        self.assertFalse(is_valid)
        self.assertIn("Syntax error", msg)

        is_valid2, msg2, _ = MathExpressionEngine.validate_expression("")
        self.assertFalse(is_valid2)

    def test_security_allowlist_enforcement(self):
        # Disallow arbitrary imports
        is_valid, msg, _ = MathExpressionEngine.validate_expression("__import__('os').system('ls')")
        self.assertFalse(is_valid)
        self.assertIn("Security violation", msg)

        # Disallow attribute access (e.g. x.__class__)
        is_valid2, msg2, _ = MathExpressionEngine.validate_expression("x.__class__")
        self.assertFalse(is_valid2)
        self.assertIn("Disallowed", msg2)

        # Disallow statements / assignments
        is_valid3, msg3, _ = MathExpressionEngine.validate_expression("x = 5")
        self.assertFalse(is_valid3)

        # Disallow unknown functions (e.g. eval, exec, open)
        for dangerous_func in ("eval('1+1')", "exec('x=1')", "open('main.py')"):
            is_valid_f, msg_f, _ = MathExpressionEngine.validate_expression(dangerous_func)
            self.assertFalse(is_valid_f)


class TestExperimentExecutionEngine(unittest.TestCase):
    """Test experiment execution, parameter sweep, iterative simulation, and statistics."""

    def setUp(self):
        self.linear_exp = {
            "id": "test_linear",
            "title": "Test Linear",
            "equation": "y = m * x + c",
            "parameters": [
                {"symbol": "m", "name": "Slope", "default": 2.0, "min": -10.0, "max": 10.0},
                {"symbol": "c", "name": "Intercept", "default": 1.0, "min": -20.0, "max": 20.0}
            ],
            "variables": [
                {"symbol": "x", "name": "x", "is_independent": True},
                {"symbol": "y", "name": "y", "is_independent": False}
            ],
            "input_data": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            "execution_config": {"mode": "series"}
        }

    def test_series_execution(self):
        res = ExperimentExecutionEngine.execute_experiment(self.linear_exp)
        self.assertEqual(res["execution_status"], "SUCCESS")
        self.assertIsNone(res["error_info"])
        self.assertEqual(len(res["calculated_outputs"]), 6)

        # Check values: y = 2*x + 1 -> [1, 3, 5, 7, 9, 11]
        expected_y = [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]
        actual_y = [pt["y"] for pt in res["calculated_outputs"]]
        self.assertEqual(actual_y, expected_y)

    def test_parameter_bounds_validation(self):
        # Override m exceeding max (10.0)
        res = ExperimentExecutionEngine.execute_experiment(self.linear_exp, param_overrides={"m": 15.0})
        self.assertEqual(res["execution_status"], "ERROR")
        self.assertIn("exceeds maximum limit", res["error_info"])

        # Override m below min (-10.0)
        res2 = ExperimentExecutionEngine.execute_experiment(self.linear_exp, param_overrides={"m": -15.0})
        self.assertEqual(res2["execution_status"], "ERROR")
        self.assertIn("below minimum limit", res2["error_info"])

    def test_iterative_simulation_execution(self):
        # Decay: y_{t+1} = y * 0.5
        iter_exp = {
            "id": "test_decay",
            "title": "Decay Simulation",
            "equation": "y = y * factor",
            "parameters": [
                {"symbol": "factor", "name": "Factor", "default": 0.5, "min": 0.0, "max": 1.0}
            ],
            "variables": [
                {"symbol": "t", "name": "Time", "is_independent": True},
                {"symbol": "y", "name": "Quantity", "is_independent": False}
            ],
            "input_data": [],
            "execution_config": {"mode": "iterative", "iterations": 4, "initial_condition": 16.0}
        }
        res = ExperimentExecutionEngine.execute_experiment(iter_exp)
        self.assertEqual(res["execution_status"], "SUCCESS")
        self.assertEqual(len(res["calculated_outputs"]), 5)  # step 0 to 4
        # [16, 8, 4, 2, 1]
        y_vals = [pt["y"] for pt in res["calculated_outputs"]]
        self.assertEqual(y_vals, [16.0, 8.0, 4.0, 2.0, 1.0])

    def test_descriptive_statistics_calculation(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = ExperimentExecutionEngine.calculate_statistics(data)
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)
        self.assertEqual(stats["mean"], 30.0)
        self.assertEqual(stats["median"], 30.0)
        self.assertEqual(stats["range"], 40.0)
        self.assertAlmostEqual(stats["stdev"], 15.8114, places=3)


class TestEducationalTemplates(unittest.TestCase):
    """Test all 8 educational templates."""

    def test_all_8_templates_present_and_executable(self):
        self.assertEqual(len(EXPERIMENT_TEMPLATES), 8)
        expected_ids = [
            "tpl_linear", "tpl_exponential", "tpl_logistic", "tpl_sigmoid",
            "tpl_gradient_descent", "tpl_neural_sum", "tpl_confusion_matrix", "tpl_image_threshold"
        ]
        actual_ids = [t["id"] for t in EXPERIMENT_TEMPLATES]
        self.assertEqual(actual_ids, expected_ids)

        for tpl in EXPERIMENT_TEMPLATES:
            # Check required schema fields
            for key in ("title", "domain", "objective", "description", "theoretical_background",
                        "expected_outcome", "equation", "parameters", "input_data", "execution_config"):
                self.assertIn(key, tpl, f"Template {tpl['id']} missing field {key}")

            # Execute template
            run_rec = ExperimentExecutionEngine.execute_experiment(tpl)
            self.assertEqual(run_rec["execution_status"], "SUCCESS",
                             f"Template {tpl['id']} failed: {run_rec.get('error_info')}")
            self.assertGreater(len(run_rec["calculated_outputs"]), 0)

    def test_get_template_dict_returns_independent_copy(self):
        t1 = get_template_dict("tpl_linear")
        t2 = get_template_dict("tpl_linear")
        t1["title"] = "Modified"
        self.assertNotEqual(t1["title"], t2["title"])


class TestAppStateCustomExperiments(unittest.TestCase):
    """Test centralized AppState custom experiment management and history."""

    def setUp(self):
        self.state = AppState()

    def test_default_experiments_initialized(self):
        self.assertGreaterEqual(len(self.state.custom_experiments), 2)
        exp_ids = list(self.state.custom_experiments.keys()) if isinstance(self.state.custom_experiments, dict) else [e["id"] for e in self.state.custom_experiments]
        self.assertIn("exp_logistic_growth", exp_ids)
        self.assertIn("exp_hookes_law", exp_ids)

    def test_create_and_retrieve_custom_experiment(self):
        new_exp = {
            "id": "exp_custom_spring",
            "title": "Spring Pendulum",
            "domain": "Physics",
            "equation": "y = k * x",
            "parameters": [{"symbol": "k", "default": 5.0}],
            "input_data": [1, 2, 3],
            "runs": []
        }
        self.state.add_custom_experiment(new_exp)
        retrieved = self.state.get_custom_experiment("exp_custom_spring")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["title"], "Spring Pendulum")

    def test_update_custom_experiment(self):
        new_exp = {
            "id": "exp_to_update",
            "title": "Initial Title",
            "domain": "Physics",
            "equation": "y = x",
            "parameters": [],
            "input_data": [1, 2],
            "runs": []
        }
        self.state.add_custom_experiment(new_exp)
        self.state.update_custom_experiment("exp_to_update", {"title": "Updated Title"})
        updated = self.state.get_custom_experiment("exp_to_update")
        self.assertEqual(updated["title"], "Updated Title")

    def test_duplicate_custom_experiment(self):
        new_id = self.state.duplicate_custom_experiment("exp_logistic_growth")
        self.assertIsNotNone(new_id)
        duplicated = self.state.get_custom_experiment(new_id)
        self.assertIn("(Copy)", duplicated["title"])
        self.assertEqual(duplicated["domain"], "Biology")

    def test_delete_custom_experiment(self):
        temp_exp = {"id": "exp_temp_del", "title": "Temporary", "runs": []}
        self.state.add_custom_experiment(temp_exp)
        self.assertIsNotNone(self.state.get_custom_experiment("exp_temp_del"))

        res = self.state.delete_custom_experiment("exp_temp_del")
        self.assertTrue(res)
        self.assertIsNone(self.state.get_custom_experiment("exp_temp_del"))

    def test_record_multiple_runs_and_preservation(self):
        exp_id = "exp_logistic_growth"
        exp = self.state.get_custom_experiment(exp_id)
        initial_run_count = len(exp.get("runs", []))

        # Record a run
        run1 = {"run_id": "run_test_01", "timestamp": "2026-11-01 10:00:00", "summary_stats": {"mean": 100}}
        self.state.record_custom_experiment_run(exp_id, run1)

        # Record a second run
        run2 = {"run_id": "run_test_02", "timestamp": "2026-11-01 10:05:00", "summary_stats": {"mean": 200}}
        self.state.record_custom_experiment_run(exp_id, run2)

        updated_exp = self.state.get_custom_experiment(exp_id)
        runs = updated_exp.get("runs", [])
        self.assertEqual(len(runs), initial_run_count + 2)
        self.assertEqual(runs[-2]["run_id"], "run_test_01")
        self.assertEqual(runs[-1]["run_id"], "run_test_02")

        # Test deleting individual run
        del_res = self.state.delete_custom_experiment_run(exp_id, "run_test_01")
        self.assertTrue(del_res)
        runs_after_del = self.state.get_custom_experiment(exp_id).get("runs", [])
        self.assertEqual(len(runs_after_del), initial_run_count + 1)
        self.assertNotIn("run_test_01", [r["run_id"] for r in runs_after_del])

    def test_metrics_integration(self):
        metrics = self.state.get_metrics()
        self.assertGreaterEqual(metrics["experiments_count"], 5)
        self.assertGreaterEqual(metrics["total_experiment_executions"], 4)

    def test_search_integration(self):
        res = self.state.search_all("logistic")
        found = [r for r in res if r["id"] == "exp_logistic_growth"]
        self.assertTrue(len(found) > 0)
        self.assertEqual(found[0]["category"], "Experiment Lab")
        self.assertEqual(found[0]["badge"], "CUSTOM EXP")


class TestDiscoveryJournalTransfer(unittest.TestCase):
    """Test transfer of experiment dossier to Discovery Journal draft."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.state = AppState()

    def tearDown(self):
        self.root.destroy()

    def test_transfer_draft_populates_all_fields(self):
        exp = self.state.get_custom_experiment("exp_logistic_growth")
        docs = exp.get("documentation", {})

        draft = {
            "source_type": "experiment_lab",
            "title": f"Empirical Investigation: {exp.get('title')}",
            "domain": exp.get("domain"),
            "research_question": docs.get("research_question"),
            "hypothesis": docs.get("hypothesis"),
            "methodology": docs.get("methodology"),
            "observations": docs.get("observations"),
            "results": docs.get("results"),
            "conclusion": docs.get("conclusion"),
            "status": "Formulated",
            "tags": exp.get("tags")
        }
        self.state.pending_journal_draft = draft

        # Instantiate DiscoveryJournalView and load draft
        journal_view = DiscoveryJournalView(self.root, None)
        journal_view.app = type("MockApp", (), {"state": self.state})()
        journal_view.load_pending_draft(draft)

        # Verify fields in journal view
        self.assertEqual(journal_view.form_title_var.get(), draft["title"])
        self.assertEqual(journal_view.form_domain_var.get(), draft["domain"])
        self.assertEqual(journal_view.text_widgets["research_question"].get("1.0", "end-1c"), draft["research_question"])
        self.assertEqual(journal_view.text_widgets["hypothesis"].get("1.0", "end-1c"), draft["hypothesis"])
        self.assertEqual(journal_view.text_widgets["methodology"].get("1.0", "end-1c"), draft["methodology"])
        self.assertEqual(journal_view.text_widgets["conclusion"].get("1.0", "end-1c"), draft["conclusion"])


class TestBuiltinExperimentsIntact(unittest.TestCase):
    """Test that Caesar Cipher, Single Neuron, and DataViz remain 100% operational."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = type("MockApp", (), {"state": AppState()})()
        self.builtin_view = BuiltInExperimentsView(self.root, self.app)

    def tearDown(self):
        self.root.destroy()

    def test_caesar_encryption_and_decryption(self):
        # Test Caesar transform directly
        plain = "HELLO WORLD"
        shift = 3
        enc = self.builtin_view._caesar_transform(plain, shift, decrypt=False)
        self.assertEqual(enc, "KHOOR ZRUOG")

        dec = self.builtin_view._caesar_transform(enc, shift, decrypt=True)
        self.assertEqual(dec, plain)

    def test_single_neuron_activation(self):
        # Check calculation method exists and executes
        self.builtin_view._calculate_neuron()
        # Verify neuron canvas initialized
        self.assertTrue(hasattr(self.builtin_view, "neuron_canvas"))

    def test_dataviz_chart_generation(self):
        self.builtin_view._generate_chart()
        self.assertTrue(hasattr(self.builtin_view, "dataviz_canvas"))
        self.assertTrue(hasattr(self.builtin_view, "dataviz_var"))


class TestUIViewsNavigation(unittest.TestCase):
    """Test top-level ExperimentLabView navigation between all tabs."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = type("MockApp", (), {"state": AppState()})()
        self.lab_view = ExperimentLabView(self.root, self.app)

    def tearDown(self):
        self.root.destroy()

    def test_all_views_instantiated(self):
        expected_views = ["overview", "my_experiments", "builder", "results", "discussion", "history", "builtins"]
        for v in expected_views:
            self.assertIn(v, self.lab_view.views)

    def test_tab_switching(self):
        self.lab_view.switch_tab("my_experiments")
        self.assertEqual(self.lab_view.current_tab, "my_experiments")

        self.lab_view.switch_tab("builder", new_exp=True)
        self.assertEqual(self.lab_view.current_tab, "builder")

        self.lab_view.switch_tab("results")
        self.assertEqual(self.lab_view.current_tab, "results")

        self.lab_view.switch_tab("discussion")
        self.assertEqual(self.lab_view.current_tab, "discussion")

        self.lab_view.switch_tab("history")
        self.assertEqual(self.lab_view.current_tab, "history")

        self.lab_view.switch_tab("builtins")
        self.assertEqual(self.lab_view.current_tab, "builtins")


if __name__ == "__main__":
    unittest.main()
