"""
CurioLab Stage 6 — Comprehensive Test Suite
===========================================
Automated verification for Research Detective transformation:
- CSV upload and data safety
- Invalid CSV handling (empty, malformed rows, non-existent)
- Missing values handling
- Numerical and categorical column detection
- Statistical calculations (mean, median, variance, std dev, quartiles, IQR)
- IQR outlier detection with configurable threshold k
- Z-score anomaly detection with configurable threshold
- Confusion matrix metrics (accuracy, precision, recall, specificity, F1)
- Bivariate correlation and linear regression (Pearson r, R^2, slope, residuals)
- Detective Map navigation, stage status updating, and notes
- Discovery Journal transfer flow
- UI component instantiation and headless rendering
- Existing application regression tests
"""

import unittest
import os
import tempfile
import tkinter as tk
from tkinter import messagebox
from unittest.mock import patch, MagicMock

# Patch all tkinter messagebox methods so automated tests do not block on modal prompts
messagebox.showinfo = MagicMock(return_value=True)
messagebox.showwarning = MagicMock(return_value=True)
messagebox.showerror = MagicMock(return_value=True)
messagebox.askyesno = MagicMock(return_value=True)

from app_state import AppState
from theme import Theme
from research_detective import (
    DataProcessor,
    SAMPLE_DATASETS,
    PATTERN_DATASETS,
    ResearchDetectiveView,
    DetectiveMapView,
    DataDetectiveWorkspace,
    StatisticalTrapWorkspace,
    PatternMysteryWorkspace
)
from discovery_journal import DiscoveryJournalView
from main import CurioLabApp


class TestDataProcessor(unittest.TestCase):
    """Unit tests for the standard-library DataProcessor engine."""

    def test_descriptive_stats(self):
        vals = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = DataProcessor.compute_descriptive_stats(vals)
        self.assertEqual(stats["count"], 5)
        self.assertAlmostEqual(stats["mean"], 30.0)
        self.assertAlmostEqual(stats["median"], 30.0)
        self.assertAlmostEqual(stats["min"], 10.0)
        self.assertAlmostEqual(stats["max"], 50.0)
        self.assertAlmostEqual(stats["q1"], 20.0)
        self.assertAlmostEqual(stats["q3"], 40.0)
        self.assertAlmostEqual(stats["iqr"], 20.0)
        self.assertAlmostEqual(stats["stdev"], 15.8113883, places=4)

    def test_descriptive_stats_even_count(self):
        vals = [1.0, 2.0, 3.0, 4.0]
        stats = DataProcessor.compute_descriptive_stats(vals)
        self.assertEqual(stats["count"], 4)
        self.assertAlmostEqual(stats["mean"], 2.5)
        self.assertAlmostEqual(stats["median"], 2.5)

    def test_descriptive_stats_empty(self):
        stats = DataProcessor.compute_descriptive_stats([])
        self.assertEqual(stats["count"], 0)
        self.assertEqual(stats["mean"], 0.0)

    def test_iqr_outlier_detection(self):
        # 10 values around 10, plus one extreme low (-50) and one extreme high (150)
        series = [(i, 10.0 + (i % 3)) for i in range(10)]
        series.append((10, -50.0))
        series.append((11, 150.0))

        low_f, high_f, flagged, det = DataProcessor.detect_iqr_outliers(series, k=1.5)
        self.assertIn(10, flagged)
        self.assertIn(11, flagged)
        self.assertEqual(len(flagged), 2)
        self.assertTrue(det[10]["value"] < low_f)
        self.assertTrue(det[11]["value"] > high_f)

    def test_iqr_configurable_threshold(self):
        series = [(0, 10.0), (1, 12.0), (2, 11.0), (3, 10.5), (4, 18.0)]
        # With tight k=0.5, 18.0 should be flagged
        _, _, flagged_tight, _ = DataProcessor.detect_iqr_outliers(series, k=0.5)
        self.assertIn(4, flagged_tight)
        # With wide k=4.0, 18.0 should not be flagged
        _, _, flagged_wide, _ = DataProcessor.detect_iqr_outliers(series, k=4.0)
        self.assertNotIn(4, flagged_wide)

    def test_zscore_anomaly_detection(self):
        # 20 points around 100 with small sigma, and one point at 250
        series = [(i, 100.0 + (i % 2)) for i in range(20)]
        series.append((20, 250.0))

        mean_v, stdev_v, flagged, det = DataProcessor.detect_zscore_anomalies(series, threshold=2.5)
        self.assertIn(20, flagged)
        self.assertTrue(det[20]["z_score"] >= 2.5)

    def test_confusion_matrix_metrics(self):
        # Imbalanced test: TP=0, FP=0, FN=15, TN=985 (1000 total)
        res = DataProcessor.compute_confusion_matrix_metrics(tp=0, fp=0, fn=15, tn=985)
        self.assertEqual(res["total"], 1000)
        self.assertAlmostEqual(res["accuracy"], 0.985)
        self.assertAlmostEqual(res["precision"], 0.0)
        self.assertAlmostEqual(res["recall"], 0.0)
        self.assertAlmostEqual(res["f1_score"], 0.0)
        self.assertAlmostEqual(res["specificity"], 1.0)

        # Balanced test: TP=80, FP=20, FN=10, TN=90
        res2 = DataProcessor.compute_confusion_matrix_metrics(tp=80, fp=20, fn=10, tn=90)
        self.assertEqual(res2["total"], 200)
        self.assertAlmostEqual(res2["accuracy"], 0.85)
        self.assertAlmostEqual(res2["precision"], 0.80)
        self.assertAlmostEqual(res2["recall"], 80.0 / 90.0)
        self.assertTrue(res2["f1_score"] > 0.8)

    def test_bivariate_regression_and_correlation(self):
        # Perfect positive line: y = 2x + 5
        x_series = [(i, float(i)) for i in range(10)]
        y_series = [(i, 2.0 * float(i) + 5.0) for i in range(10)]
        res = DataProcessor.compute_bivariate_regression(x_series, y_series)
        self.assertAlmostEqual(res["r"], 1.0)
        self.assertAlmostEqual(res["r2"], 1.0)
        self.assertAlmostEqual(res["slope"], 2.0)
        self.assertAlmostEqual(res["intercept"], 5.0)
        self.assertEqual(len(res["unusual_indices"]), 0)

    def test_bivariate_with_residual_outlier(self):
        # Line with one high residual outlier
        x_series = [(i, float(i)) for i in range(20)]
        y_series = [(i, 3.0 * float(i) + 10.0) for i in range(20)]
        # Inject extreme outlier at index 10
        y_series[10] = (10, 150.0)
        res = DataProcessor.compute_bivariate_regression(x_series, y_series)
        self.assertIn(10, res["unusual_indices"])


class TestCsvSafetyAndParsing(unittest.TestCase):
    """Tests CSV upload, missing values, malformed rows, and empty file handling."""

    def test_valid_csv_parsing(self):
        content = "col_a,col_b,col_c\n1.2,3.4,hello\n5.6,7.8,world\n"
        headers, rows, meta = DataProcessor.parse_csv_text(content)
        self.assertTrue(meta["success"])
        self.assertEqual(headers, ["col_a", "col_b", "col_c"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(meta["column_types"]["col_a"], "numeric")
        self.assertEqual(meta["column_types"]["col_b"], "numeric")
        self.assertEqual(meta["column_types"]["col_c"], "categorical")

    def test_empty_file_handling(self):
        headers, rows, meta = DataProcessor.parse_csv_text("")
        self.assertFalse(meta["success"])
        self.assertIn("empty", meta["error"].lower())

    def test_missing_values_detection(self):
        content = "idx,val,notes\n1,10.5,normal\n2,NA,missing\n3,,blank\n4,14.2,null\n"
        headers, rows, meta = DataProcessor.parse_csv_text(content)
        self.assertTrue(meta["success"])
        self.assertTrue(meta["missing_values_count"] >= 3)
        self.assertEqual(meta["column_types"]["val"], "numeric")
        series = DataProcessor.extract_numeric_series(headers, rows, "val")
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0], (0, 10.5))
        self.assertEqual(series[1], (3, 14.2))

    def test_malformed_rows_handling(self):
        # Row 2 has 2 cols, row 3 has 4 cols
        content = "col1,col2,col3\n1,2,3\n4,5\n7,8,9,10\n"
        headers, rows, meta = DataProcessor.parse_csv_text(content)
        self.assertTrue(meta["success"])
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[1]), 3)  # Padded
        self.assertEqual(len(rows[2]), 3)  # Truncated
        self.assertEqual(meta["malformed_rows_adjusted"], 2)

    def test_sample_datasets_validity(self):
        for k, sample in SAMPLE_DATASETS.items():
            headers, rows, meta = DataProcessor.parse_csv_text(sample["text"])
            self.assertTrue(meta["success"], f"Sample dataset '{k}' failed parsing.")
            self.assertTrue(len(rows) > 0)
            self.assertTrue(len(meta["numeric_columns"]) > 0)

        for k, sample in PATTERN_DATASETS.items():
            headers, rows, meta = DataProcessor.parse_csv_text(sample["text"])
            self.assertTrue(meta["success"], f"Pattern dataset '{k}' failed parsing.")
            self.assertTrue(len(rows) > 0)
            self.assertTrue(sample["x_col"] in headers)
            self.assertTrue(sample["y_col"] in headers)


class TestResearchDetectiveIntegration(unittest.TestCase):
    """UI integration and end-to-end tests for Research Detective module."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()  # Headless execution

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def setUp(self):
        self.state = AppState()
        # Mock minimal app container
        class MockApp:
            def __init__(self, state):
                self.state = state
                self.navigated_to = None
            def navigate_to(self, page):
                self.navigated_to = page

        self.mock_app = MockApp(self.state)
        self.detective_view = ResearchDetectiveView(self.root, self.mock_app)

    def tearDown(self):
        self.detective_view.destroy()

    def test_detective_suite_subviews_present(self):
        """Verifies Cipher Room is removed and the 4 scientific workspaces are active."""
        self.assertIn("overview", self.detective_view.sub_views)
        self.assertIn("data", self.detective_view.sub_views)
        self.assertIn("stat", self.detective_view.sub_views)
        self.assertIn("pattern", self.detective_view.sub_views)
        # Verify Cipher Room is NOT present
        self.assertNotIn("cipher", self.detective_view.sub_views)

    def test_detective_map_navigation_and_stages(self):
        """Tests 7 connected stages in Detective Map and stage updates."""
        map_view = self.detective_view.sub_views["overview"]
        self.assertEqual(len(map_view.STAGE_KEYS), 7)
        self.assertEqual(map_view.STAGE_KEYS, [
            "question", "evidence", "exploration",
            "analysis", "observations", "hypothesis", "conclusion"
        ])

        # Test selecting a stage and saving updates
        map_view.selected_stage_key = "hypothesis"
        map_view._load_stage_into_inspector("hypothesis")
        map_view.notes_text.delete("1.0", "end")
        map_view.notes_text.insert("1.0", "Sensor spike is caused by thermal switch bounce.")
        map_view.status_var.set("Completed")
        map_view._save_current_stage()

        # Check state synchronization
        self.assertEqual(self.state.investigation_stages["hypothesis"]["status"], "Completed")
        self.assertIn("thermal switch bounce", self.state.investigation_stages["hypothesis"]["notes"])

    def test_data_detective_anomaly_audit(self):
        """Tests Data Detective workspace outlier detection and observation saving."""
        data_view = self.detective_view.sub_views["data"]
        # Load cryogenic dataset
        data_view._load_sample("cryo_sensor")
        self.assertTrue(len(data_view.current_rows) > 0)
        self.assertEqual(data_view.selected_col_var.get(), "temperature_kelvin")

        # Run IQR audit
        data_view.detection_method_var.set("IQR Outlier (Tukey)")
        data_view.iqr_k_var.set(1.5)
        data_view._run_detection()

        # Row 8 (12.85 K) and Row 14 (-0.45 K) must be flagged
        flagged = data_view.flagged_row_indices
        self.assertTrue(len(flagged) >= 2)
        self.assertIn(7, flagged)  # 0-indexed row 8
        self.assertIn(13, flagged) # 0-indexed row 14

        # Save observations to board
        data_view.obs_input.delete("1.0", "end")
        data_view.obs_input.insert("1.0", "Flagged thermal switch spike at 12.85 K and sub-zero error.")
        data_view._save_observations_to_board()

        # Check AppState updated
        obs_notes = self.state.investigation_stages["observations"]["notes"]
        self.assertIn("thermal switch spike", obs_notes)
        self.assertEqual(self.state.investigation_stages["exploration"]["status"], "Completed")

    def test_statistical_trap_confusion_matrix(self):
        """Tests Statistical Trap class imbalance and confusion matrix calculation."""
        stat_view = self.detective_view.sub_views["stat"]
        stat_view.switch_mode("imbalance")

        # Set 0 TP, 0 FP, 15 FN, 985 TN
        stat_view._set_cm_values(0, 0, 15, 985)
        self.assertIn("98.50%", stat_view.m_acc_lbl.cget("text"))
        self.assertIn("0.00%", stat_view.m_rec_lbl.cget("text"))

        # Save deductions
        stat_view.stat_obs_text.delete("1.0", "end")
        stat_view.stat_obs_text.insert("1.0", "Accuracy is deceptive under 98.5% class imbalance; recall is 0.")
        stat_view._save_stat_obs()

        analysis_notes = self.state.investigation_stages["analysis"]["notes"]
        self.assertIn("Accuracy is deceptive", analysis_notes)
        self.assertEqual(self.state.investigation_stages["analysis"]["status"], "Completed")

    def test_pattern_mystery_regression(self):
        """Tests Pattern Mystery bivariate regression and residual discovery."""
        pattern_view = self.detective_view.sub_views["pattern"]
        pattern_view._load_pattern_preset("study_vs_exam")

        self.assertEqual(pattern_view.x_col_var.get(), "hours_studied")
        self.assertEqual(pattern_view.y_col_var.get(), "exam_score")

        res = pattern_view.bivariate_results
        self.assertTrue(res["r"] > 0.8)
        self.assertTrue(len(res["unusual_indices"]) > 0)  # Sickness outlier flagged

        # Save pattern notes
        pattern_view.pattern_notes.delete("1.0", "end")
        pattern_view.pattern_notes.insert("1.0", "Linear positive trend with r > 0.8; point #20 deviates heavily.")
        pattern_view._save_pattern_notes()

        obs_notes = self.state.investigation_stages["observations"]["notes"]
        self.assertIn("Linear positive trend", obs_notes)

    def test_discovery_journal_transfer_flow(self):
        """Tests transferring completed investigation dossier into Discovery Journal."""
        map_view = self.detective_view.sub_views["overview"]
        map_view.inv_title_var.set("Deep Space Signal Investigation")

        # Set stage notes
        self.state.investigation_stages["question"]["notes"] = "Is flux density modulation periodic?"
        self.state.investigation_stages["observations"]["notes"] = "Identified 2 solar flares exceeding 95 mJy."
        self.state.investigation_stages["conclusion"]["notes"] = "Modulation is solar interference, not deep space signal."

        # Trigger transfer
        map_view._transfer_to_discovery_journal()

        # Verify draft staged in AppState
        draft = self.state.pending_journal_draft
        self.assertIsNotNone(draft)
        self.assertEqual(draft["source_type"], "research_detective")
        self.assertEqual(draft["title"], "Investigation: Deep Space Signal Investigation")
        self.assertEqual(draft["research_question"], "Is flux density modulation periodic?")
        self.assertIn("solar flares", draft["observations"])
        self.assertIn("solar interference", draft["conclusion"])
        self.assertIn("limitations", draft)
        self.assertIn("dataset_description", draft)

        # Verify navigation called
        self.assertEqual(self.mock_app.navigated_to, "Discovery Journal")

        # Now test that DiscoveryJournalView properly accepts this draft
        journal_view = DiscoveryJournalView(self.root, self.mock_app)
        journal_view.load_pending_draft(draft)
        self.assertEqual(journal_view.form_title_var.get(), "Investigation: Deep Space Signal Investigation")
        self.assertEqual(journal_view.text_widgets["research_question"].get("1.0", "end-1c"), "Is flux density modulation periodic?")
        self.assertIn("solar flares", journal_view.text_widgets["observations"].get("1.0", "end-1c"))
        self.assertIn("solar interference", journal_view.text_widgets["conclusion"].get("1.0", "end-1c"))
        journal_view.destroy()

    def test_reset_detective_progress(self):
        """Tests resetting detective progress restores initial state and updates metrics."""
        self.state.investigation_stages["conclusion"]["status"] = "Completed"
        self.state.investigation_stages["analysis"]["status"] = "Completed"
        m_before = self.state.get_metrics()
        self.assertTrue(m_before["solved_challenges_count"] >= 2)

        self.state.reset_detective_progress()
        m_after = self.state.get_metrics()
        self.assertEqual(m_after["solved_challenges_count"], 0)
        self.assertEqual(m_after["curriculum_pct"], 0.0)
        self.assertEqual(self.state.investigation_stages["conclusion"]["status"], "Not Started")

    def test_csv_tempfile_upload(self):
        """Tests loading a CSV file from disk via DataDetectiveWorkspace."""
        data_view = self.detective_view.sub_views["data"]
        csv_lines = [
            "sensor_id,voltage_mv,pressure_kpa",
            "S1,120.4,101.3",
            "S2,122.1,101.5",
            "S3,121.0,101.4",
            "S4,120.8,101.2",
            "S5,121.5,101.4",
            "S6,120.9,101.3",
            "S7,999.9,101.4"
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("\n".join(csv_lines) + "\n")
            temp_path = f.name

        try:
            headers, rows, meta = DataProcessor.parse_csv_file(temp_path)
            self.assertTrue(meta["success"])
            self.assertEqual(len(rows), 7)
            data_view._load_dataset_data(headers, rows, meta)
            self.assertEqual(data_view.selected_col_var.get(), "voltage_mv")
            self.assertIn(6, data_view.flagged_row_indices) # Row 7 (index 6) 999.9 outlier flagged
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_canvas_drawings(self):
        """Verifies visualization canvases update cleanly across all subviews without exceptions."""
        map_view = self.detective_view.sub_views["overview"]
        map_view._draw_pipeline_graph()

        data_view = self.detective_view.sub_views["data"]
        data_view._draw_visualization()

        stat_view = self.detective_view.sub_views["stat"]
        stat_view.switch_mode("skew")
        stat_view._update_skew_sim()
        stat_view.switch_mode("correlation")
        stat_view.switch_mode("samplesize")
        stat_view._update_sample_sim()

        pattern_view = self.detective_view.sub_views["pattern"]
        pattern_view._draw_pattern_canvas()

    def test_statistical_trap_custom_data_mode(self):
        """Tests Statistical Trap custom numerical input, histogram, and box plot calculations."""
        stat_view = self.detective_view.sub_views["stat"]
        stat_view.switch_mode("custom_data")
        stat_view.custom_data_input.delete("1.0", "end")
        stat_view.custom_data_input.insert("1.0", "10.0, 11.0, 12.0, 10.5, 11.5, 150.0")
        stat_view._update_custom_data_analysis()

        # Mean should be pulled far above median by 150.0 outlier
        stats = DataProcessor.compute_descriptive_stats(stat_view.custom_series_values)
        self.assertEqual(stats["count"], 6)
        self.assertTrue(stats["mean"] > stats["median"])
        self.assertIn("Right-Skewed", stat_view.custom_metrics_lbl.cget("text"))
        # Test canvas redraw
        stat_view._draw_custom_canvas()

    def test_pattern_mystery_manual_data_entry(self):
        """Tests Pattern Mystery manual coordinate entry and bivariate model."""
        pattern_view = self.detective_view.sub_views["pattern"]
        # Manually assign points
        pattern_view.current_headers = ["variable_x", "variable_y"]
        pattern_view.current_rows = [
            ["1.0", "3.0"],
            ["2.0", "5.0"],
            ["3.0", "7.0"],
            ["4.0", "9.0"],
            ["5.0", "11.0"]
        ]
        pattern_view.x_col_var.set("variable_x")
        pattern_view.y_col_var.set("variable_y")
        pattern_view._update_pattern()

        res = pattern_view.bivariate_results
        self.assertEqual(res["n"], 5)
        self.assertAlmostEqual(res["r"], 1.0)
        self.assertAlmostEqual(res["slope"], 2.0)
        self.assertAlmostEqual(res["intercept"], 1.0)


class TestCurioLabAppRegression(unittest.TestCase):
    """Verifies that full CurioLabApp boots with all pages including transformed Research Detective."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = CurioLabApp(cls.root)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_all_pages_initialized(self):
        pages = self.app.pages
        self.assertIn("Discovery Hub", pages)
        self.assertIn("Experiment Lab", pages)
        self.assertIn("Research Detective", pages)
        self.assertIn("Knowledge Library", pages)
        self.assertIn("Research Galaxy", pages)
        self.assertIn("Discovery Journal", pages)
        self.assertIn("Settings", pages)
        self.assertIn("Help & About", pages)

    def test_navigation_to_research_detective(self):
        self.app.navigate_to("Research Detective")
        self.assertEqual(self.app.current_page_name, "Research Detective")
        det_view = self.app.pages["Research Detective"]
        self.assertIsInstance(det_view, ResearchDetectiveView)

    def test_navigation_to_other_modules(self):
        for page in ["Discovery Hub", "Experiment Lab", "Knowledge Library", "Research Galaxy", "Discovery Journal", "Settings", "Help & About"]:
            self.app.navigate_to(page)
            self.assertEqual(self.app.current_page_name, page)


class TestDetectiveMapViewVisibilityAndInteractivity(unittest.TestCase):
    """
    Stage 6.1 Verification: Verifies Detective Map visibility, mounting, screen space,
    responsive non-overlapping layout of all seven stages, inspector synchronization,
    and bi-directional workspace navigation.
    """

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.geometry("1400x850")
        cls.app = CurioLabApp(cls.root)
        cls.root.update()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def setUp(self):
        self.app.navigate_to("Research Detective")
        self.root.update()
        self.rd_view = self.app.pages["Research Detective"]
        self.map_view = self.rd_view.sub_views["overview"]

    def test_detective_map_immediately_visible(self):
        """1. Detective Map is primary, immediately visible interface on opening Research Detective."""
        self.assertEqual(self.rd_view.current_sub_view, "overview")
        self.assertTrue(self.rd_view.winfo_ismapped())
        self.assertTrue(self.map_view.winfo_ismapped())
        self.assertTrue(self.map_view.graph_canvas.winfo_ismapped())

        # Sufficient screen space allocation
        canvas_w = self.map_view.graph_canvas.winfo_width()
        canvas_h = self.map_view.graph_canvas.winfo_height()
        self.assertTrue(canvas_w >= 500, f"Canvas width {canvas_w} should be >= 500")
        self.assertTrue(canvas_h >= 350, f"Canvas height {canvas_h} should be >= 350")
        self.assertTrue(len(self.map_view.graph_canvas.find_all()) >= 30)

    def test_all_seven_stages_rendered_without_overlap(self):
        """2 & 7. All seven stages displayed with connecting conduits and zero overlaps."""
        self.map_view._draw_pipeline_graph()
        self.root.update()

        hitboxes = self.map_view.node_hitboxes
        for k in DetectiveMapView.STAGE_KEYS:
            self.assertIn(k, hitboxes, f"Stage key '{k}' must be present in canvas hitboxes")

        canvas_w = self.map_view.graph_canvas.winfo_width()
        canvas_h = self.map_view.graph_canvas.winfo_height()

        # Check all hitboxes are within canvas boundaries
        for k, (x1, y1, x2, y2) in hitboxes.items():
            self.assertTrue(x1 >= 0, f"Node {k} left {x1} out of bounds (< 0)")
            self.assertTrue(x2 <= canvas_w, f"Node {k} right {x2} out of bounds (> {canvas_w})")
            self.assertTrue(y1 >= 0, f"Node {k} top {y1} out of bounds (< 0)")
            self.assertTrue(y2 <= canvas_h, f"Node {k} bottom {y2} out of bounds (> {canvas_h})")

        # Verify zero overlap between any pair of nodes
        all_keys = list(hitboxes.keys())
        for i in range(len(all_keys)):
            for j in range(i + 1, len(all_keys)):
                k1, k2 = all_keys[i], all_keys[j]
                b1, b2 = hitboxes[k1], hitboxes[k2]
                ox = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
                oy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
                self.assertFalse(ox > 0 and oy > 0, f"Overlap detected between {k1} and {k2}: ox={ox}, oy={oy}")

    def test_inspector_updates_on_node_click(self):
        """5. Clicking a node updates inspector with description, status, notes, and evidence."""
        class EventMock:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # Click Analysis stage
        b_ana = self.map_view.node_hitboxes["analysis"]
        cx_ana = int((b_ana[0] + b_ana[2]) / 2)
        cy_ana = int((b_ana[1] + b_ana[3]) / 2)
        self.map_view._on_canvas_click(EventMock(cx_ana, cy_ana))

        self.assertEqual(self.map_view.selected_stage_key, "analysis")
        self.assertIn("Analysis", self.map_view.insp_title_lbl.cget("text"))
        self.assertIn("Statistical Trap", self.map_view.jump_btn.cget("text"))

        # Click Exploration stage
        b_exp = self.map_view.node_hitboxes["exploration"]
        cx_exp = int((b_exp[0] + b_exp[2]) / 2)
        cy_exp = int((b_exp[1] + b_exp[3]) / 2)
        self.map_view._on_canvas_click(EventMock(cx_exp, cy_exp))

        self.assertEqual(self.map_view.selected_stage_key, "exploration")
        self.assertIn("Exploration", self.map_view.insp_title_lbl.cget("text"))
        self.assertIn("Data Detective", self.map_view.jump_btn.cget("text"))

    def test_workspace_navigation(self):
        """6. Working navigation from relevant stages into Data Detective, Statistical Trap and Pattern Mystery."""
        class EventMock:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # 1. Evidence -> Data Detective via double click
        b_ev = self.map_view.node_hitboxes["evidence"]
        self.map_view._on_canvas_double_click(EventMock(int((b_ev[0] + b_ev[2]) / 2), int((b_ev[1] + b_ev[3]) / 2)))
        self.root.update()
        self.assertEqual(self.rd_view.current_sub_view, "data")
        self.assertTrue(self.rd_view.sub_views["data"].winfo_ismapped())

        # 2. Return to map and test Analysis -> Statistical Trap via jump button
        self.rd_view.switch_to_subview("overview")
        self.root.update()
        self.map_view.selected_stage_key = "analysis"
        self.map_view._on_jump_clicked()
        self.root.update()
        self.assertEqual(self.rd_view.current_sub_view, "stat")
        self.assertTrue(self.rd_view.sub_views["stat"].winfo_ismapped())

        # 3. Return to map and test Observations -> Pattern Mystery via double click
        self.rd_view.switch_to_subview("overview")
        self.root.update()
        b_obs = self.map_view.node_hitboxes["observations"]
        self.map_view._on_canvas_double_click(EventMock(int((b_obs[0] + b_obs[2]) / 2), int((b_obs[1] + b_obs[3]) / 2)))
        self.root.update()
        self.assertEqual(self.rd_view.current_sub_view, "pattern")
        self.assertTrue(self.rd_view.sub_views["pattern"].winfo_ismapped())

        # Reset back to overview
        self.rd_view.switch_to_subview("overview")
        self.root.update()


if __name__ == "__main__":
    unittest.main()
