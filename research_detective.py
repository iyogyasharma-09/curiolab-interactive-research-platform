"""
CurioLab — Research Detective Module
====================================
Interactive scientific investigation environment for empirical dataset analysis,
anomaly detection, statistical interpretation, pattern discovery, and hypothesis tracking.

Frontend-only desktop application utilizing Python's standard library (csv, math, statistics)
and the centralized AppState architecture.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import math
import statistics
import datetime
import sys
from theme import Theme


# =============================================================================
# DATA PROCESSING & STATISTICAL UTILITIES (STANDARD LIBRARY ONLY)
# =============================================================================

class DataProcessor:
    """
    Standard-library CSV parsing, validation, column detection,
    and descriptive statistical calculation engine.
    """

    MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "?", "-", "nil"}

    @classmethod
    def parse_csv_file(cls, filepath):
        """
        Safely reads a CSV file from disk using utf-8-sig (BOM support) or latin-1 fallback.
        Validates structure and returns (headers, rows, metadata).
        """
        try:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                content = f.read()
        except Exception:
            with open(filepath, "r", encoding="latin-1", errors="replace") as f:
                content = f.read()

        return cls.parse_csv_text(content, filename=filepath.split("/")[-1].split("\\")[-1])

    @classmethod
    def parse_csv_text(cls, content, filename="Custom Dataset"):
        """
        Parses CSV string content, sniffs delimiter, handles malformed rows,
        detects column types, and computes metadata.
        """
        content = content.strip()
        if not content:
            return None, None, {
                "success": False,
                "error": "The uploaded file is empty. Please select a CSV file containing headers and data rows."
            }

        lines = [line for line in content.splitlines() if line.strip()]
        if not lines:
            return None, None, {
                "success": False,
                "error": "The file contains no readable non-empty lines."
            }

        # Sniff delimiter
        first_few = "\n".join(lines[:10])
        delimiter = ","
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(first_few, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except Exception:
            # Fallback heuristic
            for d in [",", "\t", ";", "|"]:
                if d in lines[0]:
                    delimiter = d
                    break

        reader = csv.reader(lines, delimiter=delimiter)
        raw_rows = []
        try:
            for r in reader:
                raw_rows.append(r)
        except Exception as e:
            return None, None, {
                "success": False,
                "error": f"Failed to parse CSV structure: {str(e)}"
            }

        if not raw_rows:
            return None, None, {
                "success": False,
                "error": "No CSV records found."
            }

        raw_headers = raw_rows[0]
        # Sanitize headers
        headers = []
        seen = {}
        for i, h in enumerate(raw_headers):
            clean_h = str(h).strip() or f"Column_{i+1}"
            if clean_h in seen:
                seen[clean_h] += 1
                clean_h = f"{clean_h}_{seen[clean_h]}"
            else:
                seen[clean_h] = 1
            headers.append(clean_h)

        data_rows = raw_rows[1:]
        if not data_rows:
            return headers, [], {
                "success": False,
                "error": "The CSV file contains column headers but zero data rows."
            }

        expected_cols = len(headers)
        cleaned_rows = []
        malformed_count = 0
        missing_values_count = 0

        for r_idx, row in enumerate(data_rows):
            # Normalize row length
            if len(row) < expected_cols:
                padded = row + [""] * (expected_cols - len(row))
                cleaned_rows.append(padded)
                malformed_count += 1
            elif len(row) > expected_cols:
                truncated = row[:expected_cols]
                cleaned_rows.append(truncated)
                malformed_count += 1
            else:
                cleaned_rows.append(row)

            # Count missing tokens
            for val in cleaned_rows[-1]:
                if str(val).strip().lower() in cls.MISSING_TOKENS:
                    missing_values_count += 1

        # Detect column types
        col_types = cls.detect_column_types(headers, cleaned_rows)

        metadata = {
            "success": True,
            "filename": filename,
            "row_count": len(cleaned_rows),
            "col_count": expected_cols,
            "delimiter": delimiter,
            "missing_values_count": missing_values_count,
            "malformed_rows_adjusted": malformed_count,
            "column_types": col_types,
            "numeric_columns": [h for h in headers if col_types.get(h) == "numeric"],
            "categorical_columns": [h for h in headers if col_types.get(h) == "categorical"],
        }

        return headers, cleaned_rows, metadata

    @classmethod
    def detect_column_types(cls, headers, rows):
        """
        Inspects each column to determine whether it is numeric or categorical.
        If >= 75% of non-empty values can be cast to float, classifies as numeric.
        """
        col_types = {}
        for col_idx, h in enumerate(headers):
            valid_num_count = 0
            non_empty_count = 0
            for r in rows:
                if col_idx < len(r):
                    val_str = str(r[col_idx]).strip()
                    if val_str.lower() not in cls.MISSING_TOKENS:
                        non_empty_count += 1
                        try:
                            float(val_str)
                            valid_num_count += 1
                        except ValueError:
                            pass

            if non_empty_count > 0 and (valid_num_count / non_empty_count) >= 0.75:
                col_types[h] = "numeric"
            else:
                col_types[h] = "categorical"
        return col_types

    @classmethod
    def extract_numeric_series(cls, headers, rows, col_name):
        """
        Extracts numeric values for a specified column along with original 0-indexed row numbers.
        Returns list of (row_index, float_value).
        """
        if col_name not in headers:
            return []
        c_idx = headers.index(col_name)
        series = []
        for r_idx, r in enumerate(rows):
            if c_idx < len(r):
                val_str = str(r[c_idx]).strip()
                if val_str.lower() not in cls.MISSING_TOKENS:
                    try:
                        f_val = float(val_str)
                        series.append((r_idx, f_val))
                    except ValueError:
                        pass
        return series

    @classmethod
    def compute_descriptive_stats(cls, values):
        """
        Calculates mean, median, variance, std dev, min, max, quartiles (Q1, Q2, Q3), and IQR.
        Takes a list of float numbers.
        """
        if not values:
            return {
                "count": 0, "mean": 0.0, "median": 0.0, "variance": 0.0,
                "stdev": 0.0, "min": 0.0, "max": 0.0,
                "q1": 0.0, "q2": 0.0, "q3": 0.0, "iqr": 0.0
            }

        n = len(values)
        s_vals = sorted(values)
        mean_val = sum(s_vals) / n

        # Median
        if n % 2 == 1:
            median_val = s_vals[n // 2]
        else:
            median_val = (s_vals[n // 2 - 1] + s_vals[n // 2]) / 2.0

        # Variance & Stdev
        if n > 1:
            var_val = sum((x - mean_val) ** 2 for x in s_vals) / (n - 1)
            stdev_val = math.sqrt(var_val)
        else:
            var_val = 0.0
            stdev_val = 0.0

        min_val = s_vals[0]
        max_val = s_vals[-1]

        # Quartiles
        def get_percentile(data, p):
            if not data:
                return 0.0
            k = (len(data) - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return data[int(k)]
            return data[f] * (c - k) + data[c] * (k - f)

        q1 = get_percentile(s_vals, 0.25)
        q2 = median_val
        q3 = get_percentile(s_vals, 0.75)
        iqr = q3 - q1

        return {
            "count": n,
            "mean": mean_val,
            "median": median_val,
            "variance": var_val,
            "stdev": stdev_val,
            "min": min_val,
            "max": max_val,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "iqr": iqr
        }

    @classmethod
    def detect_iqr_outliers(cls, indexed_series, k=1.5):
        """
        Detects outliers using Tukey's IQR fences:
        Lower fence = Q1 - k * IQR
        Upper fence = Q3 + k * IQR
        Returns:
            low_fence, high_fence, flagged_indices (set of row_idx), details (dict mapping row_idx to info)
        """
        if not indexed_series:
            return 0.0, 0.0, set(), {}

        values = [v for _, v in indexed_series]
        stats = cls.compute_descriptive_stats(values)
        q1 = stats["q1"]
        q3 = stats["q3"]
        iqr = stats["iqr"]

        low_fence = q1 - k * iqr
        high_fence = q3 + k * iqr

        flagged_indices = set()
        details = {}

        for r_idx, val in indexed_series:
            if val < low_fence:
                flagged_indices.add(r_idx)
                diff = low_fence - val
                details[r_idx] = {
                    "value": val,
                    "reason": f"Below lower fence ({low_fence:.2f}) by {diff:.2f}",
                    "severity": "Low Outlier",
                    "delta": diff
                }
            elif val > high_fence:
                flagged_indices.add(r_idx)
                diff = val - high_fence
                details[r_idx] = {
                    "value": val,
                    "reason": f"Above upper fence ({high_fence:.2f}) by {diff:.2f}",
                    "severity": "High Outlier",
                    "delta": diff
                }

        return low_fence, high_fence, flagged_indices, details

    @classmethod
    def detect_zscore_anomalies(cls, indexed_series, threshold=2.5):
        """
        Detects anomalies using Z-score: |z| = |(x - mean) / stdev| > threshold.
        Returns:
            mean, stdev, flagged_indices (set of row_idx), details (dict mapping row_idx to info)
        """
        if not indexed_series:
            return 0.0, 0.0, set(), {}

        values = [v for _, v in indexed_series]
        stats = cls.compute_descriptive_stats(values)
        mean_val = stats["mean"]
        stdev_val = stats["stdev"]

        flagged_indices = set()
        details = {}

        if stdev_val == 0.0:
            return mean_val, stdev_val, flagged_indices, details

        for r_idx, val in indexed_series:
            z = (val - mean_val) / stdev_val
            if abs(z) >= threshold:
                flagged_indices.add(r_idx)
                details[r_idx] = {
                    "value": val,
                    "z_score": z,
                    "reason": f"|Z| = {abs(z):.2f} >= threshold ({threshold:.2f})",
                    "severity": "Positive Anomaly" if z > 0 else "Negative Anomaly",
                    "delta": abs(val - mean_val)
                }

        return mean_val, stdev_val, flagged_indices, details

    @classmethod
    def compute_bivariate_regression(cls, x_series, y_series):
        """
        Calculates Pearson correlation (r), R^2, slope (m), intercept (b),
        and residual standard error for matched pairs (same row_idx).
        """
        # Match by row index
        x_map = dict(x_series)
        y_map = dict(y_series)
        common_indices = sorted(set(x_map.keys()) & set(y_map.keys()))

        if len(common_indices) < 2:
            return {
                "n": len(common_indices), "r": 0.0, "r2": 0.0,
                "slope": 0.0, "intercept": 0.0, "residual_se": 0.0,
                "residuals": {}, "unusual_indices": set(), "pairs": []
            }

        pairs = [(idx, x_map[idx], y_map[idx]) for idx in common_indices]
        xs = [p[1] for p in pairs]
        ys = [p[2] for p in pairs]
        n = len(pairs)

        mean_x = sum(xs) / n
        mean_y = sum(ys) / n

        ss_xx = sum((x - mean_x) ** 2 for x in xs)
        ss_yy = sum((y - mean_y) ** 2 for y in ys)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))

        if ss_xx == 0.0 or ss_yy == 0.0:
            r = 0.0
            slope = 0.0
            intercept = mean_y
        else:
            r = ss_xy / math.sqrt(ss_xx * ss_yy)
            slope = ss_xy / ss_xx
            intercept = mean_y - slope * mean_x

        r2 = r ** 2

        # Residuals
        residuals = {}
        res_list = []
        for idx, x, y in pairs:
            y_pred = slope * x + intercept
            res = y - y_pred
            residuals[idx] = res
            res_list.append(res)

        if n > 2:
            residual_se = math.sqrt(sum(e ** 2 for e in res_list) / (n - 2))
        else:
            residual_se = 0.0

        # Unusual observations: |residual| > 2 * residual_se
        unusual_indices = set()
        if residual_se > 0:
            for idx, res in residuals.items():
                if abs(res) >= 2.0 * residual_se:
                    unusual_indices.add(idx)

        return {
            "n": n,
            "r": r,
            "r2": r2,
            "slope": slope,
            "intercept": intercept,
            "residual_se": residual_se,
            "residuals": residuals,
            "unusual_indices": unusual_indices,
            "pairs": pairs
        }

    @classmethod
    def compute_confusion_matrix_metrics(cls, tp, fp, fn, tn):
        """
        Calculates Accuracy, Precision, Recall, Specificity, and F1-score from confusion matrix counts.
        """
        total = tp + fp + fn + tn
        acc = (tp + tn) / total if total > 0 else 0.0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        return {
            "total": total,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "specificity": spec,
            "f1_score": f1
        }


# =============================================================================
# BUILT-IN EDUCATIONAL SAMPLE DATASETS
# =============================================================================

SAMPLE_DATASETS = {
    "cryo_sensor": {
        "title": "Cryogenic Resonator Temperature Array",
        "domain": "Physics & Instrumentation",
        "description": "30 sequential telemetry frames measuring superconducting cavity temperatures (Kelvin) during liquid helium cooling.",
        "text": """timestamp,temperature_kelvin,chamber_pressure_torr,sensor_voltage_mv
2026-11-01 00:00:01,4.21,0.00012,142.1
2026-11-01 00:00:05,4.19,0.00011,141.8
2026-11-01 00:00:10,4.22,0.00012,142.3
2026-11-01 00:00:15,4.20,0.00013,142.0
2026-11-01 00:00:20,4.23,0.00011,142.4
2026-11-01 00:00:25,4.18,0.00012,141.7
2026-11-01 00:00:30,4.25,0.00014,142.6
2026-11-01 00:00:35,12.85,0.00085,210.4
2026-11-01 00:00:40,4.22,0.00012,142.2
2026-11-01 00:00:45,4.19,0.00011,141.9
2026-11-01 00:00:50,4.21,0.00012,142.1
2026-11-01 00:00:55,4.24,0.00013,142.5
2026-11-01 00:01:00,4.20,0.00012,142.0
2026-11-01 00:01:05,-0.45,0.00000,-12.0
2026-11-01 00:01:10,4.22,0.00012,142.3
2026-11-01 00:01:15,4.18,0.00011,141.8
2026-11-01 00:01:20,4.23,0.00013,142.4
2026-11-01 00:01:25,4.21,0.00012,142.1
2026-11-01 00:01:30,4.19,0.00012,141.9
2026-11-01 00:01:35,4.25,0.00014,142.7
2026-11-01 00:01:40,4.20,0.00012,142.0
2026-11-01 00:01:45,4.22,0.00012,142.2
2026-11-01 00:01:50,4.24,0.00013,142.5
2026-11-01 00:01:55,4.18,0.00011,141.7
2026-11-01 00:02:00,4.21,0.00012,142.1
2026-11-01 00:02:05,4.23,0.00013,142.4
2026-11-01 00:02:10,4.20,0.00012,142.0
2026-11-01 00:02:15,4.22,0.00012,142.2
2026-11-01 00:02:20,4.19,0.00011,141.8
2026-11-01 00:02:25,4.21,0.00012,142.1"""
    },
    "particle_velocity": {
        "title": "Relativistic Particle Beam Telemetry",
        "domain": "High Energy Physics",
        "description": "32 vacuum chamber velocity readings in units of 10^7 m/s (c = 3.00 × 10^8 m/s = 30.0 units).",
        "text": """run_id,velocity_10e7_ms,beam_current_ua,vacuum_mbar
RUN_101,18.42,45.2,1.2e-9
RUN_102,18.55,45.6,1.1e-9
RUN_103,18.38,44.9,1.3e-9
RUN_104,18.49,45.3,1.2e-9
RUN_105,18.62,45.8,1.2e-9
RUN_106,18.44,45.1,1.1e-9
RUN_107,18.51,45.4,1.2e-9
RUN_108,34.82,45.0,1.2e-9
RUN_109,18.40,45.2,1.3e-9
RUN_110,18.58,45.7,1.2e-9
RUN_111,18.46,45.3,1.1e-9
RUN_112,18.53,45.5,1.2e-9
RUN_113,0.00,0.2,8.4e-6
RUN_114,18.48,45.2,1.2e-9
RUN_115,18.60,45.8,1.2e-9
RUN_116,18.41,45.0,1.1e-9
RUN_117,18.54,45.6,1.2e-9
RUN_118,18.47,45.3,1.2e-9
RUN_119,18.52,45.4,1.1e-9
RUN_120,18.43,45.1,1.3e-9
RUN_121,18.59,45.7,1.2e-9
RUN_122,18.45,45.2,1.2e-9
RUN_123,18.50,45.5,1.1e-9
RUN_124,18.48,45.3,1.2e-9
RUN_125,18.61,45.9,1.2e-9
RUN_126,18.42,45.1,1.1e-9
RUN_127,18.56,45.6,1.2e-9
RUN_128,18.49,45.4,1.3e-9
RUN_129,18.53,45.5,1.2e-9
RUN_130,18.46,45.2,1.1e-9
RUN_131,18.57,45.7,1.2e-9
RUN_132,18.51,45.3,1.2e-9"""
    },
    "microbial_density": {
        "title": "Bioreactor Microbial Optical Density",
        "domain": "Microbiology & Bioengineering",
        "description": "26 timed optical density (OD600) growth measurements in bacterial culture containing a decimal typo.",
        "text": """sample_hour,od600_absorbance,ph_level,dissolved_o2_pct
1.0,0.12,6.95,95.2
2.0,0.18,6.94,94.0
3.0,0.26,6.92,92.5
4.0,0.39,6.90,89.4
5.0,0.58,6.88,85.1
6.0,0.85,6.85,79.2
7.0,1.18,6.82,71.4
8.0,1.45,6.79,64.0
9.0,14.80,6.76,58.2
10.0,1.82,6.74,52.1
11.0,1.96,6.72,48.0
12.0,2.05,6.70,45.2
13.0,2.11,6.69,43.5
14.0,2.15,6.68,42.1
15.0,2.18,6.68,41.4
16.0,2.20,6.67,40.8
17.0,2.21,6.67,40.5
18.0,2.22,6.66,40.2
19.0,2.22,6.66,40.1
20.0,2.23,6.66,40.0
21.0,2.23,6.65,39.9
22.0,2.22,6.65,39.9
23.0,2.21,6.65,39.8
24.0,2.20,6.65,39.8
25.0,2.19,6.64,39.7
26.0,2.18,6.64,39.7"""
    },
    "deep_space_flux": {
        "title": "Deep Space Radio Flux Density",
        "domain": "Radio Astronomy",
        "description": "36 observational frames measuring radio flux density (mJy) with sporadic solar interference bursts.",
        "text": """frame_id,flux_density_mjy,antenna_elevation_deg,system_noise_temp_k
FR_01,51.2,42.5,22.1
FR_02,52.4,42.8,22.3
FR_03,49.8,43.1,22.0
FR_04,50.6,43.4,22.2
FR_05,53.1,43.7,22.4
FR_06,51.8,44.0,22.1
FR_07,48.9,44.3,22.0
FR_08,52.7,44.6,22.3
FR_09,98.4,44.9,28.6
FR_10,50.3,45.2,22.1
FR_11,51.5,45.5,22.2
FR_12,52.9,45.8,22.4
FR_13,49.4,46.1,22.0
FR_14,50.8,46.4,22.1
FR_15,53.6,46.7,22.5
FR_16,51.1,47.0,22.1
FR_17,104.2,47.3,31.2
FR_18,52.3,47.6,22.3
FR_19,49.7,47.9,22.0
FR_20,50.5,48.2,22.1
FR_21,52.8,48.5,22.4
FR_22,51.4,48.8,22.2
FR_23,49.1,49.1,22.0
FR_24,53.0,49.4,22.3
FR_25,50.2,49.7,22.1
FR_26,51.7,50.0,22.2
FR_27,52.5,50.3,22.4
FR_28,48.8,50.6,21.9
FR_29,50.9,50.9,22.1
FR_30,53.3,51.2,22.5
FR_31,51.6,51.5,22.2
FR_32,49.5,51.8,22.0
FR_33,52.1,52.1,22.3
FR_34,50.4,52.4,22.1
FR_35,51.9,52.7,22.2
FR_36,52.6,53.0,22.4"""
    }
}

PATTERN_DATASETS = {
    "study_vs_exam": {
        "title": "Study Duration vs Examination Score",
        "x_col": "hours_studied",
        "y_col": "exam_score",
        "description": "25 students tracking weekly revision hours versus empirical examination score. Shows strong linear trend with one unusual sickness outlier.",
        "text": """student_id,hours_studied,exam_score,attendance_pct
ST_01,2.0,48,82
ST_02,2.5,54,85
ST_03,3.0,52,80
ST_04,3.5,60,88
ST_05,4.0,62,86
ST_06,4.2,65,90
ST_07,4.8,68,92
ST_08,5.0,72,91
ST_09,5.5,70,89
ST_10,5.8,76,94
ST_11,6.0,78,95
ST_12,6.5,82,93
ST_13,6.8,80,92
ST_14,7.0,85,96
ST_15,7.5,89,97
ST_16,7.8,87,95
ST_17,8.0,91,98
ST_18,8.5,94,99
ST_19,8.8,92,97
ST_20,9.0,52,94
ST_21,9.2,96,99
ST_22,9.5,95,98
ST_23,9.8,98,100
ST_24,10.0,99,100
ST_25,1.5,42,75"""
    },
    "temperature_vs_enzyme": {
        "title": "Temperature vs Enzymatic Catalysis Rate",
        "x_col": "temperature_celsius",
        "y_col": "reaction_rate_umol_s",
        "description": "20 observations showing non-linear inverted-U behavior. Catalysis increases to optimal 42°C before thermal denaturation collapses the rate.",
        "text": """test_run,temperature_celsius,reaction_rate_umol_s,ph
RUN_01,10.0,1.2,7.4
RUN_02,15.0,2.1,7.4
RUN_03,20.0,3.5,7.4
RUN_04,25.0,5.4,7.4
RUN_05,30.0,7.8,7.4
RUN_06,33.0,9.6,7.4
RUN_07,36.0,11.8,7.4
RUN_08,38.0,13.2,7.4
RUN_09,40.0,14.5,7.4
RUN_10,42.0,15.1,7.4
RUN_11,44.0,14.6,7.4
RUN_12,46.0,12.4,7.4
RUN_13,48.0,8.7,7.4
RUN_14,50.0,5.1,7.4
RUN_15,52.0,2.8,7.4
RUN_16,55.0,1.1,7.4
RUN_17,58.0,0.4,7.4
RUN_18,60.0,0.1,7.4
RUN_19,65.0,0.0,7.4
RUN_20,70.0,0.0,7.4"""
    },
    "planetary_kepler": {
        "title": "Planetary Distance vs Orbital Period (Kepler's Law)",
        "x_col": "semi_major_axis_au",
        "y_col": "orbital_period_years",
        "description": "8 solar system planets showing power-law scaling (T^2 = a^3). Demonstrates non-linear scaling across astronomical distance.",
        "text": """planet,semi_major_axis_au,orbital_period_years,eccentricity
Mercury,0.387,0.241,0.206
Venus,0.723,0.615,0.007
Earth,1.000,1.000,0.017
Mars,1.524,1.881,0.093
Jupiter,5.204,11.862,0.048
Saturn,9.582,29.457,0.056
Uranus,19.201,84.011,0.046
Neptune,30.047,164.790,0.010"""
    },
    "damped_oscillation": {
        "title": "Mechanical Damped Harmonic Oscillator",
        "x_col": "time_seconds",
        "y_col": "displacement_mm",
        "description": "24 time-series measurements of a spring-mass shock absorber displaying exponentially decaying sinusoidal oscillation.",
        "text": """index,time_seconds,displacement_mm,damping_ratio
1,0.0,10.0,0.15
2,0.5,7.2,0.15
3,1.0,1.8,0.15
4,1.5,-3.6,0.15
5,2.0,-6.1,0.15
6,2.5,-4.8,0.15
7,3.0,-1.4,0.15
8,3.5,2.2,0.15
9,4.0,3.9,0.15
10,4.5,3.2,0.15
11,5.0,1.1,0.15
12,5.5,-1.3,0.15
13,6.0,-2.5,0.15
14,6.5,-2.1,0.15
15,7.0,-0.8,0.15
16,7.5,0.8,0.15
17,8.0,1.6,0.15
18,8.5,1.4,0.15
19,9.0,0.5,0.15
20,9.5,-0.5,0.15
21,10.0,-1.0,0.15
22,10.5,-0.9,0.15
23,11.0,-0.3,0.15
24,11.5,0.3,0.15"""
    }
}


# =============================================================================
# REUSABLE SCROLLABLE CONTAINER
# =============================================================================

class SmoothScrollableFrame(tk.Frame):
    """
    Self-contained cross-platform scrollable canvas container
    matching CurioLab's obsidian theme with smooth mousewheel response.
    """
    def __init__(self, parent, bg=Theme.BG_ROOT, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0, yscrollincrement=1)
        self.canvas._is_curiolab_scroll_canvas = True
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=bg)

        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_mousewheel(self)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        if sys.platform == "darwin":
            if abs(event.delta) < 120:
                step = int(-1 * event.delta * 16)
                if step == 0 and event.delta != 0:
                    step = -2 if event.delta > 0 else 2
            else:
                step = int(-1 * (event.delta / 120.0) * 36)
        else:
            step = int(-1 * (event.delta / 120.0) * 36)
        self.canvas.yview_scroll(step, "units")
        return "break"

    def bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-32, "units"))
        widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(32, "units"))


# =============================================================================
# SUBVIEW 1: DETECTIVE MAP (INVESTIGATION BOARD)
# =============================================================================

class DetectiveMapView(tk.Frame):
    """
    Investigation Board: Central visual map connecting the 7 scientific stages:
    1. Research Question
    2. Evidence Collection
    3. Dataset Exploration
    4. Analysis
    5. Observations
    6. Hypothesis
    7. Conclusion
    """

    STAGE_KEYS = [
        "question", "evidence", "exploration",
        "analysis", "observations", "hypothesis", "conclusion"
    ]

    STAGE_METADATA = {
        "question": {
            "title": "1. Research Question",
            "icon": "❓",
            "short_desc": "Define empirical query & parameters",
            "full_desc": "Formulate a focused, testable research inquiry. Define the boundary conditions and expected baselines.",
            "target_view": None
        },
        "evidence": {
            "title": "2. Evidence Collection",
            "icon": "📁",
            "short_desc": "Gather datasets, signals & literature",
            "full_desc": "Acquire telemetry logs, empirical CSV records, and experimental sensor frames for examination.",
            "target_view": "data"
        },
        "exploration": {
            "title": "3. Dataset Exploration",
            "icon": "🔍",
            "short_desc": "Audit rows, columns & distributions",
            "full_desc": "Inspect data completeness, evaluate missing tokens, calculate quartile baselines, and detect potential anomalies.",
            "target_view": "data"
        },
        "analysis": {
            "title": "4. Analysis",
            "icon": "📊",
            "short_desc": "Perform statistical tests & modeling",
            "full_desc": "Evaluate mean vs median distortions, compute confusion metrics, and model linear vs non-linear trends.",
            "target_view": "stat"
        },
        "observations": {
            "title": "5. Observations",
            "icon": "📝",
            "short_desc": "Document empirical findings & residuals",
            "full_desc": "Record flagged outliers, residual deviations, and counter-intuitive correlations without premature closure.",
            "target_view": "pattern"
        },
        "hypothesis": {
            "title": "6. Hypothesis",
            "icon": "💡",
            "short_desc": "Synthesize candidate physical explanations",
            "full_desc": "Synthesize mechanistic explanations (e.g. sensor drift, decimal typo, quantum quenching, or true physical anomalies).",
            "target_view": None
        },
        "conclusion": {
            "title": "7. Conclusion",
            "icon": "🏁",
            "short_desc": "Synthesize results & identify limitations",
            "full_desc": "Synthesize conclusions, state boundary limitations, identify confounding variables, and stage discovery journal entry.",
            "target_view": "journal"
        }
    }

    def __init__(self, parent, parent_suite):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.suite = parent_suite
        self.app = parent_suite.app

        self.selected_stage_key = "question"

        # State cache for stages
        self.stages_data = {}
        self._load_state_from_app()

        self._build_ui()

    def _load_state_from_app(self):
        """Loads or initializes investigation stages in AppState."""
        if hasattr(self.app, "state") and self.app.state:
            if not hasattr(self.app.state, "investigation_stages") or not self.app.state.investigation_stages:
                self.app.state.investigation_stages = {
                    "question": {
                        "title": "1. Research Question",
                        "status": "In Progress",
                        "notes": "Investigate potential sensor drift and anomalous temperature excursions in the cryogenic resonator telemetry array.",
                        "evidence": "Liquid helium baseline expected around 4.2 K."
                    },
                    "evidence": {
                        "title": "2. Evidence Collection",
                        "status": "In Progress",
                        "notes": "Acquired 30 telemetry frames from Cryo Sensor Bank B during the liquid helium circulation test.",
                        "evidence": "Dataset: Cryogenic Resonator Baseline (30 observations, 4 features)."
                    },
                    "exploration": {
                        "title": "3. Dataset Exploration",
                        "status": "Not Started",
                        "notes": "Audit temperature readings using IQR fences and Z-score thresholding to identify corrupt telemetry frames.",
                        "evidence": "Pending Data Detective inspection."
                    },
                    "analysis": {
                        "title": "4. Analysis",
                        "status": "Not Started",
                        "notes": "Evaluate mean vs median skewness and check whether high accuracy masks false negatives.",
                        "evidence": "Pending Statistical Trap investigation."
                    },
                    "observations": {
                        "title": "5. Observations",
                        "status": "Not Started",
                        "notes": "Document any anomalous observations, residuals, and physical constraints.",
                        "evidence": ""
                    },
                    "hypothesis": {
                        "title": "6. Hypothesis",
                        "status": "Not Started",
                        "notes": "Evaluate whether extreme points reflect physical state transitions (e.g. cavity quench) or hardware measurement glitches.",
                        "evidence": ""
                    },
                    "conclusion": {
                        "title": "7. Conclusion",
                        "status": "Not Started",
                        "notes": "Synthesize conclusions regarding sensor array health and report limitations of the sample size.",
                        "evidence": ""
                    }
                }
            if not hasattr(self.app.state, "active_investigation") or not self.app.state.active_investigation:
                self.app.state.active_investigation = {
                    "title": "Cryogenic Sensor Anomaly Investigation",
                    "domain": "Data Science",
                    "dataset_name": "Cryogenic Resonator Temperature Array",
                    "dataset_description": "30 sequential telemetry frames measuring superconducting cavity temperatures (Kelvin) during liquid helium cooling.",
                    "methodology": "Standardized IQR outlier fencing (k=1.5) and Z-score anomaly thresholding (|Z| >= 2.5).",
                    "limitations": "Small sample size (N=30); single sensor channel; extreme thermal excursions may represent true localized quenching rather than electrical sensor faults.",
                    "tags": "Research Detective, Data Science, Anomaly Audit, Outliers"
                }
            self.stages_data = self.app.state.investigation_stages
        else:
            # Fallback local dict
            self.stages_data = {k: {"title": self.STAGE_METADATA[k]["title"], "status": "Not Started", "notes": "", "evidence": ""} for k in self.STAGE_KEYS}

    def _build_ui(self):
        # Top Header Banner
        header = tk.Frame(self, bg=Theme.BG_CARD_ELEVATED,
                          highlightbackground=Theme.PURPLE,
                          highlightthickness=1, padx=24, pady=16)
        header.pack(fill="x", padx=24, pady=(16, 12))

        tag_row = tk.Frame(header, bg=Theme.BG_CARD_ELEVATED)
        tag_row.pack(fill="x")

        tk.Label(tag_row, text="🗺️ INVESTIGATION BOARD • SCIENTIFIC METHOD WORKFLOW",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT,
                 padx=8, pady=3).pack(side="left")

        self.progress_lbl = tk.Label(tag_row, text="Progress: 2 of 7 Stages Complete (29%)",
                                     font=("Segoe UI", 9, "bold"),
                                     bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN_BRIGHT)
        self.progress_lbl.pack(side="right")

        title_row = tk.Frame(header, bg=Theme.BG_CARD_ELEVATED)
        title_row.pack(fill="x", pady=(8, 2))

        self.inv_title_var = tk.StringVar(value="Cryogenic Sensor Anomaly Investigation")
        if hasattr(self.app, "state") and self.app.state and hasattr(self.app.state, "active_investigation"):
            self.inv_title_var.set(self.app.state.active_investigation.get("title", "Cryogenic Sensor Anomaly Investigation"))

        tk.Label(title_row, text="Case Dossier:", font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        self.title_entry = tk.Entry(title_row, textvariable=self.inv_title_var,
                                    font=("Segoe UI", 14, "bold"),
                                    bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                    insertbackground=Theme.CYAN, relief="flat", width=42)
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 16))
        self.title_entry.bind("<FocusOut>", lambda _: self._save_investigation_meta())

        # Transfer to Journal Button
        journal_btn = tk.Label(title_row, text=" 📓 Transfer to Journal ➔ ",
                               font=("Segoe UI", 9, "bold"),
                               bg=Theme.EMERALD, fg=Theme.BG_ROOT,
                               padx=14, pady=6, cursor="hand2")
        journal_btn.pack(side="right")
        journal_btn.bind("<Button-1>", lambda _: self._transfer_to_discovery_journal())

        # Subtitle
        tk.Label(header,
                 text="Navigate the connected nodes of scientific inquiry. Record hypotheses, log evidence references, "
                      "and audit data across specialized analytical workspaces.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # Main Split Body: Left Node Graph Canvas, Right Stage Inspector
        body = tk.Frame(self, bg=Theme.BG_ROOT)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Left: Interactive Workflow Canvas
        canvas_box = tk.Frame(body, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_SUBTLE,
                              highlightthickness=1, padx=12, pady=12)
        canvas_box.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        c_header = tk.Frame(canvas_box, bg=Theme.BG_CARD)
        c_header.pack(fill="x", pady=(0, 8))
        tk.Label(c_header, text="CONNECTED INVESTIGATION PIPELINE",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")
        tk.Label(c_header, text="Click any node to inspect & edit",
                 font=("Segoe UI", 8),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="right")

        self.graph_canvas = tk.Canvas(canvas_box, bg=Theme.BG_INPUT,
                                      highlightthickness=0, borderwidth=0)
        self.graph_canvas.pack(fill="both", expand=True)
        self.graph_canvas.bind("<Configure>", lambda _: self._draw_pipeline_graph())
        self.graph_canvas.bind("<Button-1>", self._on_canvas_click)

        # Right: Stage Inspector & Notes Editor
        inspector_box = tk.Frame(body, bg=Theme.BG_CARD,
                                 highlightbackground=Theme.BORDER_SUBTLE,
                                 highlightthickness=1, padx=20, pady=16)
        inspector_box.grid(row=0, column=1, sticky="nsew")

        self._build_stage_inspector(inspector_box)

        # Initial graph draw
        self.after(50, self._draw_pipeline_graph)
        self._update_progress_summary()

    def _build_stage_inspector(self, parent):
        """Inspector panel for the currently selected stage."""
        self.insp_icon_lbl = tk.Label(parent, text="❓", font=("Segoe UI", 22),
                                      bg=Theme.BG_CARD, fg=Theme.CYAN)
        self.insp_icon_lbl.pack(anchor="w")

        self.insp_title_lbl = tk.Label(parent, text="1. Research Question",
                                       font=("Segoe UI", 14, "bold"),
                                       bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.insp_title_lbl.pack(anchor="w", pady=(2, 2))

        self.insp_desc_lbl = tk.Label(parent, text="Formulate a testable inquiry.",
                                      font=("Segoe UI", 9),
                                      bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                                      wraplength=340, justify="left")
        self.insp_desc_lbl.pack(anchor="w", pady=(0, 10))

        # Status row
        st_row = tk.Frame(parent, bg=Theme.BG_CARD)
        st_row.pack(fill="x", pady=(0, 10))

        tk.Label(st_row, text="Stage Status:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 8))

        self.status_var = tk.StringVar(value="In Progress")
        self.status_combo = ttk.Combobox(st_row, textvariable=self.status_var,
                                         values=["Not Started", "In Progress", "Completed"],
                                         state="readonly", width=14)
        self.status_combo.pack(side="left")
        self.status_combo.bind("<<ComboboxSelected>>", lambda _: self._on_status_change())

        # Jump to relevant workspace button
        self.jump_btn = tk.Label(parent, text="🔍 Jump to Data Detective Workspace ➔",
                                 font=("Segoe UI", 8, "bold"),
                                 bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                                 padx=10, pady=5, cursor="hand2",
                                 highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.jump_btn.pack(fill="x", pady=(0, 12))
        self.jump_btn.bind("<Button-1>", lambda _: self._on_jump_clicked())

        # Stage Notes
        tk.Label(parent, text="Stage Notes & Scientific Formulation:",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))

        n_box = tk.Frame(parent, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        n_box.pack(fill="both", expand=True, pady=(0, 8))

        self.notes_text = tk.Text(n_box, font=("Segoe UI", 9),
                                  bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                  insertbackground=Theme.CYAN, relief="flat", wrap="word",
                                  padx=8, pady=8, height=6)
        self.notes_text.pack(fill="both", expand=True)

        # Evidence References
        tk.Label(parent, text="Evidence References & Flagged Clues:",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))

        e_box = tk.Frame(parent, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        e_box.pack(fill="x", pady=(0, 12))

        self.evidence_text = tk.Text(e_box, font=("Segoe UI", 9),
                                     bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                     insertbackground=Theme.CYAN, relief="flat", wrap="word",
                                     padx=8, pady=6, height=3)
        self.evidence_text.pack(fill="x")

        # Save Button
        save_btn = tk.Label(parent, text=" 💾 Save Stage Progress ",
                            font=("Segoe UI", 9, "bold"),
                            bg=Theme.BLUE, fg=Theme.TEXT_ON_ACCENT,
                            padx=14, pady=7, cursor="hand2")
        save_btn.pack(fill="x")
        save_btn.bind("<Button-1>", lambda _: self._save_current_stage())

        # Populate with selected stage
        self._load_stage_into_inspector(self.selected_stage_key)

    def _load_stage_into_inspector(self, stage_key):
        """Loads data for stage_key into the inspector controls."""
        meta = self.STAGE_METADATA.get(stage_key, {})
        stage_state = self.stages_data.get(stage_key, {})

        self.insp_icon_lbl.config(text=meta.get("icon", "◈"))
        self.insp_title_lbl.config(text=meta.get("title", stage_key.title()))
        self.insp_desc_lbl.config(text=meta.get("full_desc", ""))

        self.status_var.set(stage_state.get("status", "Not Started"))

        target = meta.get("target_view")
        if target == "data":
            self.jump_btn.config(text="🔍 Open Data Detective Workspace ➔", state="normal")
            self.jump_btn.pack(fill="x", pady=(0, 12))
        elif target == "stat":
            self.jump_btn.config(text="⚠️ Open Statistical Trap Workspace ➔", state="normal")
            self.jump_btn.pack(fill="x", pady=(0, 12))
        elif target == "pattern":
            self.jump_btn.config(text="🧩 Open Pattern Discovery Workspace ➔", state="normal")
            self.jump_btn.pack(fill="x", pady=(0, 12))
        elif target == "journal":
            self.jump_btn.config(text="📓 Transfer Investigation to Discovery Journal ➔", state="normal")
            self.jump_btn.pack(fill="x", pady=(0, 12))
        else:
            self.jump_btn.pack_forget()

        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", stage_state.get("notes", ""))

        self.evidence_text.delete("1.0", "end")
        self.evidence_text.insert("1.0", stage_state.get("evidence", ""))

    def _save_current_stage(self):
        """Saves current inspector inputs to memory and AppState."""
        stage_key = self.selected_stage_key
        notes = self.notes_text.get("1.0", "end-1c").strip()
        evidence = self.evidence_text.get("1.0", "end-1c").strip()
        status = self.status_var.get()

        if stage_key not in self.stages_data:
            self.stages_data[stage_key] = {}
        self.stages_data[stage_key]["notes"] = notes
        self.stages_data[stage_key]["evidence"] = evidence
        self.stages_data[stage_key]["status"] = status

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.investigation_stages = self.stages_data
            if hasattr(self.app.state, "notify"):
                self.app.state.notify()

        self._draw_pipeline_graph()
        self._update_progress_summary()

    def _on_status_change(self):
        self._save_current_stage()

    def _on_jump_clicked(self):
        meta = self.STAGE_METADATA.get(self.selected_stage_key, {})
        target = meta.get("target_view")
        if target in ["data", "stat", "pattern"]:
            self.suite.switch_to_subview(target)
        elif target == "journal":
            self._transfer_to_discovery_journal()

    def _save_investigation_meta(self):
        if hasattr(self.app, "state") and self.app.state:
            if not hasattr(self.app.state, "active_investigation"):
                self.app.state.active_investigation = {}
            self.app.state.active_investigation["title"] = self.inv_title_var.get().strip()
            self.app.state.notify()

    def _update_progress_summary(self):
        completed = sum(1 for s in self.stages_data.values() if s.get("status") == "Completed")
        in_prog = sum(1 for s in self.stages_data.values() if s.get("status") == "In Progress")
        pct = (completed / 7.0) * 100.0
        self.progress_lbl.config(
            text=f"Progress: {completed} of 7 Completed ({pct:.0f}%) • {in_prog} In Progress"
        )

    def _draw_pipeline_graph(self):
        """Renders the 7 stages as a connected scientific pipeline on the canvas."""
        self.graph_canvas.delete("all")
        w = self.graph_canvas.winfo_width()
        h = self.graph_canvas.winfo_height()
        if w < 100 or h < 100:
            return

        # Coordinates for 7 nodes laid out along an S-curve or vertical/horizontal tree
        # 2 rows layout: Row 1 (stages 1 to 4 left-to-right), Row 2 (stages 5 to 7 right-to-left)
        margin_x = 70
        margin_y = 55
        usable_w = w - (margin_x * 2)
        usable_h = h - (margin_y * 2)

        # 4 columns on top, 3 columns on bottom
        row1_y = margin_y + usable_h * 0.28
        row2_y = margin_y + usable_h * 0.72

        coords = {}
        # Stage 0,1,2,3 along row 1
        for i in range(4):
            cx = margin_x + (usable_w * i / 3.0)
            coords[self.STAGE_KEYS[i]] = (cx, row1_y)

        # Stage 4,5,6 along row 2 (spread out)
        for i, k in enumerate(["observations", "hypothesis", "conclusion"]):
            # align backwards or aligned with columns 3, 2, 1
            cx = margin_x + (usable_w * (3 - i) / 3.0)
            coords[k] = (cx, row2_y)

        self.node_hitboxes = {}

        # 1. Draw Connecting Lines / Arrows
        for i in range(len(self.STAGE_KEYS) - 1):
            k1 = self.STAGE_KEYS[i]
            k2 = self.STAGE_KEYS[i+1]
            x1, y1 = coords[k1]
            x2, y2 = coords[k2]

            st1 = self.stages_data.get(k1, {}).get("status", "Not Started")
            st2 = self.stages_data.get(k2, {}).get("status", "Not Started")

            line_color = Theme.BORDER_MUTED
            if st1 == "Completed":
                line_color = Theme.EMERALD if st2 == "Completed" else Theme.CYAN
            elif st1 == "In Progress":
                line_color = Theme.AMBER

            if i == 3:
                # Turn from Row 1 end to Row 2 start
                mid_x = x1 + 25
                self.graph_canvas.create_line(x1, y1, mid_x, y1, mid_x, y2, x2, y2,
                                              fill=line_color, width=3, smooth=True)
            else:
                self.graph_canvas.create_line(x1, y1, x2, y2, fill=line_color, width=3, arrow="last", arrowshape=(10, 12, 5))

        # 2. Draw Nodes
        for k in self.STAGE_KEYS:
            cx, cy = coords[k]
            meta = self.STAGE_METADATA[k]
            stage_info = self.stages_data.get(k, {})
            status = stage_info.get("status", "Not Started")
            is_selected = (k == self.selected_stage_key)

            # Color scheme based on status
            if status == "Completed":
                badge_bg = "#0B2E1E"
                accent_col = Theme.EMERALD
                status_icon = "✓"
            elif status == "In Progress":
                badge_bg = "#1A2E3B"
                accent_col = Theme.CYAN
                status_icon = "⚡"
            else:
                badge_bg = Theme.BG_CARD
                accent_col = Theme.TEXT_MUTED
                status_icon = "○"

            nw = 65
            nh = 42

            # Highlight ring if selected
            if is_selected:
                self.graph_canvas.create_oval(cx - nw - 4, cy - nh - 4, cx + nw + 4, cy + nh + 4,
                                              outline=Theme.CYAN_BRIGHT, width=2)

            # Node card background
            card_id = self.graph_canvas.create_oval(cx - nw, cy - nh, cx + nw, cy + nh,
                                                    fill=badge_bg, outline=accent_col, width=2)

            # Text inside node
            icon_str = f"{meta['icon']} {status_icon}"
            self.graph_canvas.create_text(cx, cy - 12, text=icon_str,
                                          font=("Segoe UI", 12, "bold"), fill=accent_col)

            title_clean = meta["title"].split(". ")[-1]
            self.graph_canvas.create_text(cx, cy + 8, text=title_clean,
                                          font=("Segoe UI", 8, "bold"), fill=Theme.TEXT_PRIMARY)

            self.graph_canvas.create_text(cx, cy + 22, text=status,
                                          font=("Segoe UI", 7), fill=accent_col)

            self.node_hitboxes[k] = (cx - nw, cy - nh, cx + nw, cy + nh)

    def _on_canvas_click(self, event):
        x = event.x
        y = event.y
        for k, (x1, y1, x2, y2) in self.node_hitboxes.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.selected_stage_key = k
                self._load_stage_into_inspector(k)
                self._draw_pipeline_graph()
                break

    def _transfer_to_discovery_journal(self):
        """Compiles the full investigation dossier into a Discovery Journal draft and navigates there."""
        inv_title = self.inv_title_var.get().strip() or "Scientific Investigation"
        meta = {}
        if hasattr(self.app, "state") and self.app.state and hasattr(self.app.state, "active_investigation"):
            meta = self.app.state.active_investigation

        rq = self.stages_data.get("question", {}).get("notes", "")
        dataset_desc = meta.get("dataset_description", "Imported / Preset scientific dataset")
        methodology = meta.get("methodology", "IQR and Z-score outlier detection, descriptive metrics, bivariate regression analysis.")
        obs = self.stages_data.get("observations", {}).get("notes", "")
        if not obs:
            obs = f"Empirical investigation observations from {inv_title}."

        results = f"Analysis Notes: {self.stages_data.get('analysis', {}).get('notes', 'Completed empirical auditing.')}\nEvidence References: {self.stages_data.get('evidence', {}).get('notes', '')}"
        hyp = self.stages_data.get("hypothesis", {}).get("notes", "")
        conclusion = self.stages_data.get("conclusion", {}).get("notes", "")
        limitations = meta.get("limitations", "Observations are limited by sample size and sensor array baselines. Potential confounding factors should be investigated.")
        tags = meta.get("tags", "Research Detective, Data Science, Scientific Investigation")

        draft = {
            "source_type": "research_detective",
            "title": f"Investigation: {inv_title}",
            "domain": meta.get("domain", "Data Science"),
            "entry_type": "Finding",
            "status": "Formulated",
            "tags": tags,
            "research_question": rq,
            "hypothesis": hyp,
            "observations": obs,
            "methodology": f"Dataset: {dataset_desc}\n\nMethodology & Statistical Protocol:\n{methodology}",
            "results": results,
            "conclusion": f"{conclusion}\n\nLimitations & Potential Confounders:\n{limitations}",
            "dataset_description": dataset_desc,
            "limitations": limitations
        }

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.pending_journal_draft = draft
            self.app.state.notifications.insert(0, {
                "id": f"notif_journal_transfer_{datetime.datetime.now().microsecond}",
                "title": f"📓 Investigation Staged to Journal",
                "desc": f"Dossier '{inv_title}' staged for review in Discovery Journal.",
                "timestamp": "Just now",
                "accent": Theme.EMERALD,
                "read": False
            })
            self.app.state.notify()

        if hasattr(self.app, "navigate_to"):
            self.app.navigate_to("Discovery Journal")


# =============================================================================
# SUBVIEW 2: DATA DETECTIVE (DATASET ANOMALY INVESTIGATION WORKSPACE)
# =============================================================================

class DataDetectiveWorkspace(tk.Frame):
    """
    Data Detective workspace:
    - CSV import dialog & validation
    - Pre-loaded educational sample datasets
    - Preview in scrollable ttk.Treeview
    - Numerical column selection & descriptive statistics
    - Configurable IQR and Z-score outlier detection
    - Highlighting detected anomalies in table
    - Normal vs Flagged Tkinter Canvas visualization
    - Discussion prompts and observations recording
    """
    def __init__(self, parent, parent_suite):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.suite = parent_suite
        self.app = parent_suite.app

        self.current_headers = []
        self.current_rows = []
        self.dataset_meta = {}
        self.selected_col_var = tk.StringVar()
        self.detection_method_var = tk.StringVar(value="IQR Outlier (Tukey)")
        self.iqr_k_var = tk.DoubleVar(value=1.5)
        self.z_thresh_var = tk.DoubleVar(value=2.5)

        self.flagged_row_indices = set()
        self.flagged_details = {}
        self.numeric_series = []

        self._build_ui()
        # Load default sample
        self._load_sample("cryo_sensor")

    def _build_ui(self):
        scroll = SmoothScrollableFrame(self, bg=Theme.BG_ROOT)
        scroll.pack(fill="both", expand=True)
        content = scroll.scrollable_content

        # 1. Header Banner
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.CYAN,
                        highlightthickness=1, padx=24, pady=16)
        hero.pack(fill="x", padx=24, pady=(16, 12))

        tag = tk.Label(hero, text="🔍 THE DATA DETECTIVE • DATASET ANOMALY INVESTIGATION WORKSPACE",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="Empirical Anomaly & Outlier Auditing",
                 font=("Segoe UI", 18, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))

        tk.Label(hero,
                 text="Import experimental datasets or inspect built-in sensor telemetry. Configure IQR and Z-score "
                      "detection bounds, audit corrupt values, visualize normal vs flagged observations, and formulate explanations.\n"
                      "Important: Flagged observations are potential anomalies that warrant investigation, not automatically errors.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
                 wraplength=850, justify="left").pack(anchor="w")

        # 2. Dataset Import & Preset Bar
        action_bar = tk.Frame(content, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_SUBTLE,
                              highlightthickness=1, padx=16, pady=10)
        action_bar.pack(fill="x", padx=24, pady=(0, 12))

        import_btn = tk.Label(action_bar, text=" 📁 Import CSV File... ",
                              font=("Segoe UI", 9, "bold"),
                              bg=Theme.CYAN, fg=Theme.BG_ROOT,
                              padx=14, pady=6, cursor="hand2")
        import_btn.pack(side="left", padx=(0, 16))
        import_btn.bind("<Button-1>", lambda _: self._import_csv_dialog())

        tk.Label(action_bar, text="Or Load Educational Sample:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 8))

        self.sample_combo = ttk.Combobox(action_bar,
                                         values=[
                                             "Cryogenic Resonator Temperature",
                                             "Relativistic Particle Velocity",
                                             "Bioreactor Microbial Density",
                                             "Deep Space Radio Flux"
                                         ],
                                         state="readonly", width=32)
        self.sample_combo.current(0)
        self.sample_combo.pack(side="left", padx=(0, 12))
        self.sample_combo.bind("<<ComboboxSelected>>", self._on_sample_selected)

        self.file_info_lbl = tk.Label(action_bar, text="Active: Cryogenic Resonator (30 rows)",
                                      font=("Segoe UI", 9, "italic"),
                                      bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY)
        self.file_info_lbl.pack(side="right")

        # 3. Dataset Summary Metrics Bar
        self.summary_box = tk.Frame(content, bg=Theme.BG_ROOT)
        self.summary_box.pack(fill="x", padx=24, pady=(0, 12))
        self._build_metric_cards()

        # 4. Interactive Detection Configuration Bar
        config_bar = tk.Frame(content, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_MUTED,
                              highlightthickness=1, padx=16, pady=12)
        config_bar.pack(fill="x", padx=24, pady=(0, 14))

        # Column Selector
        tk.Label(config_bar, text="Target Variable:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))
        self.col_combo = ttk.Combobox(config_bar, textvariable=self.selected_col_var,
                                      state="readonly", width=22)
        self.col_combo.pack(side="left", padx=(0, 20))
        self.col_combo.bind("<<ComboboxSelected>>", lambda _: self._run_detection())

        # Method Selector
        tk.Label(config_bar, text="Detection Method:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))
        method_combo = ttk.Combobox(config_bar, textvariable=self.detection_method_var,
                                    values=["IQR Outlier (Tukey)", "Z-Score Anomaly", "Combined (Both)"],
                                    state="readonly", width=18)
        method_combo.pack(side="left", padx=(0, 20))
        method_combo.bind("<<ComboboxSelected>>", lambda _: self._run_detection())

        # Threshold controls
        self.thresh_frame = tk.Frame(config_bar, bg=Theme.BG_CARD)
        self.thresh_frame.pack(side="left")
        self._build_threshold_controls()

        run_btn = tk.Label(config_bar, text=" ⚡ Run Audit ",
                           font=("Segoe UI", 9, "bold"),
                           bg=Theme.PURPLE, fg=Theme.TEXT_ON_ACCENT,
                           padx=14, pady=5, cursor="hand2")
        run_btn.pack(side="right")
        run_btn.bind("<Button-1>", lambda _: self._run_detection())

        # 5. Split Main Panel: Left Table Preview, Right Descriptive Stats & Anomaly List
        split_frame = tk.Frame(content, bg=Theme.BG_ROOT)
        split_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        split_frame.columnconfigure(0, weight=3)
        split_frame.columnconfigure(1, weight=2)

        # Left: Table preview
        table_container = tk.Frame(split_frame, bg=Theme.BG_CARD,
                                   highlightbackground=Theme.BORDER_SUBTLE,
                                   highlightthickness=1, padx=12, pady=12)
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        t_hdr = tk.Frame(table_container, bg=Theme.BG_CARD)
        t_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(t_hdr, text="DATASET PREVIEW & ANOMALY HIGHLIGHTS",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.table_count_lbl = tk.Label(t_hdr, text="Showing 0 rows",
                                        font=("Segoe UI", 8),
                                        bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.table_count_lbl.pack(side="right")

        # Treeview with scrollbars
        tree_frame = tk.Frame(table_container, bg=Theme.BG_CARD)
        tree_frame.pack(fill="both", expand=True)

        self.tree_vscroll = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree_hscroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        self.tree = ttk.Treeview(tree_frame, show="headings",
                                 yscrollcommand=self.tree_vscroll.set,
                                 xscrollcommand=self.tree_hscroll.set,
                                 height=14)
        self.tree_vscroll.config(command=self.tree.yview)
        self.tree_hscroll.config(command=self.tree.xview)

        self.tree_vscroll.pack(side="right", fill="y")
        self.tree_hscroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Style tags for anomalies
        self.tree.tag_configure("anomaly", background="#3B121E", foreground="#FCA5A5")
        self.tree.tag_configure("normal", background=Theme.BG_INPUT, foreground=Theme.TEXT_PRIMARY)

        # Right: Descriptive Stats Card & Flagged Anomalies
        stats_container = tk.Frame(split_frame, bg=Theme.BG_CARD,
                                   highlightbackground=Theme.BORDER_SUBTLE,
                                   highlightthickness=1, padx=16, pady=14)
        stats_container.grid(row=0, column=1, sticky="nsew")

        tk.Label(stats_container, text="STATISTICAL PROFILE",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 6))

        self.stats_grid = tk.Frame(stats_container, bg=Theme.BG_INPUT,
                                   highlightbackground=Theme.BORDER_MUTED,
                                   highlightthickness=1, padx=10, pady=8)
        self.stats_grid.pack(fill="x", pady=(0, 10))
        self._build_stats_grid()

        # Flagged Observations List
        tk.Label(stats_container, text="FLAGGED ANOMALIES & AUDIT REASON:",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.AMBER).pack(anchor="w", pady=(4, 4))

        self.flagged_listbox = tk.Listbox(stats_container, font=("Segoe UI", 8),
                                          bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                          highlightbackground=Theme.BORDER_MUTED,
                                          highlightthickness=1, relief="flat", height=7)
        self.flagged_listbox.pack(fill="both", expand=True, pady=(0, 6))

        # 6. Visualization Canvas: Normal vs Flagged Observations
        vis_box = tk.Frame(content, bg=Theme.BG_CARD,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=16, pady=14)
        vis_box.pack(fill="x", padx=24, pady=(0, 16))

        v_hdr = tk.Frame(vis_box, bg=Theme.BG_CARD)
        v_hdr.pack(fill="x", pady=(0, 8))
        tk.Label(v_hdr, text="📈 OBSERVATION DISTRIBUTION & THRESHOLD FENCES",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.legend_lbl = tk.Label(v_hdr,
                                   text="● Normal Observation (Cyan)   ◆ Flagged Potential Anomaly (Rose)   --- Threshold Boundary",
                                   font=("Segoe UI", 8),
                                   bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.legend_lbl.pack(side="right")

        self.vis_canvas = tk.Canvas(vis_box, bg=Theme.BG_INPUT,
                                    height=200, highlightthickness=0, borderwidth=0)
        self.vis_canvas.pack(fill="x", expand=True)
        self.vis_canvas.bind("<Configure>", lambda _: self._draw_visualization())

        # 7. Discussion & Investigator Notes Panel
        disc_box = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=20, pady=16)
        disc_box.pack(fill="x", padx=24, pady=(0, 24))

        tk.Label(disc_box, text="💡 INVESTIGATOR OBSERVATIONS & POSSIBLE EXPLANATIONS",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.PURPLE_LIGHT).pack(anchor="w", pady=(0, 4))

        prompts = [
            "• What do you notice in this dataset's baseline and deviations?",
            "• Which observations appear unusual, and what physical or recording mechanisms might explain them?",
            "• Are flagged points true experimental errors, sensor dropouts, or genuine extreme physical phenomena?",
            "• What additional diagnostic tests or calibrations are needed to verify these anomalies?"
        ]
        tk.Label(disc_box, text="\n".join(prompts),
                 font=("Segoe UI", 8, "italic"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED,
                 justify="left").pack(anchor="w", pady=(0, 8))

        d_text_box = tk.Frame(disc_box, bg=Theme.BG_INPUT,
                              highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        d_text_box.pack(fill="x", pady=(0, 10))

        self.obs_input = tk.Text(d_text_box, height=4, font=("Segoe UI", 9),
                                 bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                 insertbackground=Theme.CYAN, relief="flat", wrap="word",
                                 padx=8, pady=6)
        self.obs_input.pack(fill="x")
        self.obs_input.insert("1.0", "Sensor observations exhibit baseline stability around 4.2 K. Observation #8 (12.85 K) reflects a substantial thermal excursion that exceeds Tukey upper fence and 3-sigma bound. Observation #14 (-0.45 K) violates absolute zero, confirming sensor calibration dropout.")

        save_obs_btn = tk.Label(disc_box, text=" 💾 Save Observations to Investigation Board ",
                                font=("Segoe UI", 9, "bold"),
                                bg=Theme.CYAN, fg=Theme.BG_ROOT,
                                padx=14, pady=6, cursor="hand2")
        save_obs_btn.pack(side="left")
        save_obs_btn.bind("<Button-1>", lambda _: self._save_observations_to_board())

    def _build_metric_cards(self):
        """Top row of 4 dataset summary stat cards."""
        self.summary_box.columnconfigure(0, weight=1, uniform="sum")
        self.summary_box.columnconfigure(1, weight=1, uniform="sum")
        self.summary_box.columnconfigure(2, weight=1, uniform="sum")
        self.summary_box.columnconfigure(3, weight=1, uniform="sum")

        def make_card(col, title, default_val, subtitle, accent):
            c = tk.Frame(self.summary_box, bg=Theme.BG_CARD,
                         highlightbackground=Theme.BORDER_SUBTLE,
                         highlightthickness=1, padx=14, pady=10)
            c.grid(row=0, column=col, padx=(0 if col == 0 else 6, 0 if col == 3 else 6), sticky="nsew")
            tk.Label(c, text=title, font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=accent).pack(anchor="w")
            val_lbl = tk.Label(c, text=default_val, font=("Segoe UI", 16, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
            val_lbl.pack(anchor="w")
            sub_lbl = tk.Label(c, text=subtitle, font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            sub_lbl.pack(anchor="w")
            return val_lbl, sub_lbl

        self.m_rows_lbl, self.m_rows_sub = make_card(0, "Total Rows", "0", "Records imported", Theme.CYAN)
        self.m_cols_lbl, self.m_cols_sub = make_card(1, "Columns", "0", "Features detected", Theme.PURPLE)
        self.m_missing_lbl, self.m_missing_sub = make_card(2, "Missing Values", "0", "Missing or empty cells", Theme.AMBER)
        self.m_flagged_lbl, self.m_flagged_sub = make_card(3, "Potential Anomalies", "0", "Observations flagged", Theme.ROSE)

    def _build_threshold_controls(self):
        for child in self.thresh_frame.winfo_children():
            child.destroy()

        method = self.detection_method_var.get()
        if "IQR" in method or "Combined" in method:
            tk.Label(self.thresh_frame, text="IQR k-Factor:", font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 4))
            iqr_spin = ttk.Combobox(self.thresh_frame, textvariable=self.iqr_k_var,
                                    values=[1.0, 1.5, 2.0, 2.5, 3.0], width=5, state="readonly")
            iqr_spin.pack(side="left", padx=(0, 12))
            iqr_spin.bind("<<ComboboxSelected>>", lambda _: self._run_detection())

        if "Z-Score" in method or "Combined" in method:
            tk.Label(self.thresh_frame, text="|Z| Threshold:", font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 4))
            z_spin = ttk.Combobox(self.thresh_frame, textvariable=self.z_thresh_var,
                                  values=[1.5, 2.0, 2.5, 3.0, 3.5], width=5, state="readonly")
            z_spin.pack(side="left", padx=(0, 12))
            z_spin.bind("<<ComboboxSelected>>", lambda _: self._run_detection())

    def _build_stats_grid(self):
        labels = [
            ("Mean (x̄):", "mean_val"),
            ("Median:", "median_val"),
            ("Std Dev (σ):", "stdev_val"),
            ("Min / Max:", "minmax_val"),
            ("Q1 (25%):", "q1_val"),
            ("Q3 (75%):", "q3_val"),
            ("IQR:", "iqr_val"),
            ("Bounds:", "bounds_val")
        ]
        self.stat_val_labels = {}
        for idx, (txt, key) in enumerate(labels):
            r = idx // 2
            c = (idx % 2) * 2
            tk.Label(self.stats_grid, text=txt, font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).grid(row=r, column=c, sticky="w", padx=(4, 6), pady=2)
            v_lbl = tk.Label(self.stats_grid, text="—", font=("Segoe UI", 8),
                             bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
            v_lbl.grid(row=r, column=c+1, sticky="w", padx=(0, 12), pady=2)
            self.stat_val_labels[key] = v_lbl

    def _import_csv_dialog(self):
        filetypes = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select CSV Dataset", filetypes=filetypes)
        if not filepath:
            return

        headers, rows, meta = DataProcessor.parse_csv_file(filepath)
        if not meta.get("success"):
            messagebox.showerror("Validation Error", meta.get("error", "Failed to parse CSV file."), parent=self)
            return

        self._load_dataset_data(headers, rows, meta)

    def _on_sample_selected(self, event=None):
        idx = self.sample_combo.current()
        keys = ["cryo_sensor", "particle_velocity", "microbial_density", "deep_space_flux"]
        if 0 <= idx < len(keys):
            self._load_sample(keys[idx])

    def _load_sample(self, sample_key):
        sample = SAMPLE_DATASETS.get(sample_key)
        if not sample:
            return
        headers, rows, meta = DataProcessor.parse_csv_text(sample["text"], filename=sample["title"])
        self._load_dataset_data(headers, rows, meta)

    def _load_dataset_data(self, headers, rows, meta):
        self.current_headers = headers
        self.current_rows = rows
        self.dataset_meta = meta

        # Update file info label
        fname = meta.get("filename", "Dataset")
        self.file_info_lbl.config(text=f"Active: {fname} ({len(rows)} rows, {len(headers)} cols)")

        # Update metric cards
        self.m_rows_lbl.config(text=str(len(rows)))
        self.m_cols_lbl.config(text=str(len(headers)))
        self.m_cols_sub.config(text=f"{len(meta.get('numeric_columns', []))} numeric cols")
        self.m_missing_lbl.config(text=str(meta.get("missing_values_count", 0)))

        # Populate target column combobox
        num_cols = meta.get("numeric_columns", [])
        if num_cols:
            self.col_combo.config(values=num_cols)
            if self.selected_col_var.get() not in num_cols:
                self.selected_col_var.set(num_cols[0])
        else:
            self.col_combo.config(values=headers)
            if headers:
                self.selected_col_var.set(headers[0])

        self._run_detection()

    def _run_detection(self):
        self._build_threshold_controls()
        target_col = self.selected_col_var.get()
        if not target_col or not self.current_rows:
            return

        # Extract numeric series
        self.numeric_series = DataProcessor.extract_numeric_series(self.current_headers, self.current_rows, target_col)
        if not self.numeric_series:
            messagebox.showwarning("Non-Numeric Column", f"Column '{target_col}' has no valid numeric entries.", parent=self)
            return

        values = [v for _, v in self.numeric_series]
        stats = DataProcessor.compute_descriptive_stats(values)

        # Update descriptive stats UI
        self.stat_val_labels["mean_val"].config(text=f"{stats['mean']:.3f}")
        self.stat_val_labels["median_val"].config(text=f"{stats['median']:.3f}")
        self.stat_val_labels["stdev_val"].config(text=f"{stats['stdev']:.3f}")
        self.stat_val_labels["minmax_val"].config(text=f"{stats['min']:.2f} / {stats['max']:.2f}")
        self.stat_val_labels["q1_val"].config(text=f"{stats['q1']:.3f}")
        self.stat_val_labels["q3_val"].config(text=f"{stats['q3']:.3f}")
        self.stat_val_labels["iqr_val"].config(text=f"{stats['iqr']:.3f}")

        # Detection logic
        method = self.detection_method_var.get()
        self.flagged_row_indices = set()
        self.flagged_details = {}

        iqr_k = float(self.iqr_k_var.get())
        z_th = float(self.z_thresh_var.get())

        low_f = stats["q1"] - iqr_k * stats["iqr"]
        high_f = stats["q3"] + iqr_k * stats["iqr"]

        if "IQR" in method:
            low_f, high_f, iqr_flagged, iqr_det = DataProcessor.detect_iqr_outliers(self.numeric_series, k=iqr_k)
            self.flagged_row_indices = iqr_flagged
            self.flagged_details = iqr_det
            self.stat_val_labels["bounds_val"].config(text=f"[{low_f:.2f}, {high_f:.2f}]")
        elif "Z-Score" in method:
            m_v, s_v, z_flagged, z_det = DataProcessor.detect_zscore_anomalies(self.numeric_series, threshold=z_th)
            self.flagged_row_indices = z_flagged
            self.flagged_details = z_det
            z_low = m_v - z_th * s_v
            z_high = m_v + z_th * s_v
            self.stat_val_labels["bounds_val"].config(text=f"[{z_low:.2f}, {z_high:.2f}]")
        else: # Combined
            _, _, iqr_flagged, iqr_det = DataProcessor.detect_iqr_outliers(self.numeric_series, k=iqr_k)
            _, _, z_flagged, z_det = DataProcessor.detect_zscore_anomalies(self.numeric_series, threshold=z_th)
            self.flagged_row_indices = iqr_flagged | z_flagged
            self.flagged_details = {**iqr_det, **z_det}
            self.stat_val_labels["bounds_val"].config(text=f"IQR & Z-Score")

        # Update flagged metric card
        self.m_flagged_lbl.config(text=str(len(self.flagged_row_indices)))
        pct = (len(self.flagged_row_indices) / float(len(self.current_rows))) * 100.0 if self.current_rows else 0
        self.m_flagged_sub.config(text=f"{pct:.1f}% of observations")

        # Update Treeview
        self._populate_treeview()

        # Update Flagged listbox
        self.flagged_listbox.delete(0, "end")
        if not self.flagged_row_indices:
            self.flagged_listbox.insert("end", "✓ No observations exceeded detection thresholds.")
        else:
            for r_idx in sorted(self.flagged_row_indices):
                det = self.flagged_details.get(r_idx, {})
                v = det.get("value", 0.0)
                reason = det.get("reason", "Threshold exceeded")
                self.flagged_listbox.insert("end", f"Row #{r_idx+1}: {v:.2f} — {reason}")

        # Update visualization canvas
        self._draw_visualization()

    def _populate_treeview(self):
        # Configure columns
        all_cols = ["_row_id", "_audit_status"] + self.current_headers
        self.tree["columns"] = all_cols
        self.tree.heading("_row_id", text="#")
        self.tree.column("_row_id", width=45, anchor="center")
        self.tree.heading("_audit_status", text="Audit Status")
        self.tree.column("_audit_status", width=110, anchor="center")

        for h in self.current_headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=120, anchor="w")

        self.tree.delete(*self.tree.get_children())

        for r_idx, r in enumerate(self.current_rows):
            is_anomaly = (r_idx in self.flagged_row_indices)
            tag = "anomaly" if is_anomaly else "normal"
            status_txt = "⚠️ ANOMALY" if is_anomaly else "NORMAL"
            row_data = [str(r_idx + 1), status_txt] + [str(v) for v in r]
            self.tree.insert("", "end", values=row_data, tags=(tag,))

        self.table_count_lbl.config(text=f"Showing {len(self.current_rows)} records ({len(self.flagged_row_indices)} flagged)")

    def _draw_visualization(self):
        """Draws strip/index-vs-value plot with mean line and fences on canvas."""
        self.vis_canvas.delete("all")
        w = self.vis_canvas.winfo_width()
        h = self.vis_canvas.winfo_height()
        if w < 50 or h < 50 or not self.numeric_series:
            return

        pad_x = 55
        pad_y = 30
        usable_w = w - pad_x * 2
        usable_h = h - pad_y * 2

        values = [v for _, v in self.numeric_series]
        min_v = min(values)
        max_v = max(values)
        if min_v == max_v:
            min_v -= 1.0
            max_v += 1.0
        v_span = max_v - min_v

        n_pts = len(self.numeric_series)
        x_step = usable_w / max(n_pts - 1, 1)

        def to_y(val):
            norm = (val - min_v) / v_span
            return pad_y + usable_h - (norm * usable_h)

        # Baseline axis line
        self.vis_canvas.create_line(pad_x, pad_y + usable_h, pad_x + usable_w, pad_y + usable_h, fill=Theme.BORDER_MUTED, width=1)
        self.vis_canvas.create_line(pad_x, pad_y, pad_x, pad_y + usable_h, fill=Theme.BORDER_MUTED, width=1)

        # Y-axis labels
        self.vis_canvas.create_text(pad_x - 8, pad_y, text=f"{max_v:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED, anchor="e")
        self.vis_canvas.create_text(pad_x - 8, pad_y + usable_h, text=f"{min_v:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED, anchor="e")

        # Mean line
        mean_v = sum(values) / len(values)
        mean_y = to_y(mean_v)
        self.vis_canvas.create_line(pad_x, mean_y, pad_x + usable_w, mean_y, fill=Theme.CYAN, dash=(4, 4), width=1)
        self.vis_canvas.create_text(pad_x + usable_w + 4, mean_y, text=f"x̄={mean_v:.1f}", font=("Segoe UI", 7), fill=Theme.CYAN, anchor="w")

        # Plot points
        for i, (r_idx, val) in enumerate(self.numeric_series):
            cx = pad_x + i * x_step
            cy = to_y(val)
            is_flagged = (r_idx in self.flagged_row_indices)

            if is_flagged:
                # Flagged anomaly marker (diamond with halo)
                self.vis_canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="", outline="#F43F5E", width=1)
                self.vis_canvas.create_polygon(cx, cy - 6, cx + 6, cy, cx, cy + 6, cx - 6, cy, fill="#F43F5E", outline="#FFFFFF")
                self.vis_canvas.create_text(cx, cy - 12, text=f"#{r_idx+1}", font=("Segoe UI", 7, "bold"), fill="#FCA5A5")
            else:
                # Normal point (cyan circle)
                self.vis_canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=Theme.CYAN, outline="")

    def _save_observations_to_board(self):
        text = self.obs_input.get("1.0", "end-1c").strip()
        if hasattr(self.app, "state") and self.app.state:
            if hasattr(self.app.state, "investigation_stages"):
                stages = self.app.state.investigation_stages
                if "observations" in stages:
                    existing = stages["observations"].get("notes", "")
                    updated = f"{existing}\n\n[Data Detective Audit]:\n{text}".strip() if existing else f"[Data Detective Audit]:\n{text}"
                    stages["observations"]["notes"] = updated
                    stages["observations"]["status"] = "In Progress"
                if "exploration" in stages:
                    stages["exploration"]["status"] = "Completed"
                    stages["exploration"]["notes"] = f"Audited {len(self.current_rows)} records. Flagged {len(self.flagged_row_indices)} anomalies in column '{self.selected_col_var.get()}'."

            # Update active investigation metadata
            if hasattr(self.app.state, "active_investigation"):
                meta = self.app.state.active_investigation
                meta["dataset_name"] = self.dataset_meta.get("filename", "Imported Dataset")
                meta["selected_column"] = self.selected_col_var.get()

            self.app.state.notify()
            messagebox.showinfo("Saved", "Observations successfully recorded to Investigation Board (Stages 3 & 5).", parent=self)


# =============================================================================
# SUBVIEW 3: STATISTICAL TRAP (STATISTICAL INTERPRETATION WORKSPACE)
# =============================================================================

class StatisticalTrapWorkspace(tk.Frame):
    """
    Statistical Trap workspace:
    Investigating deceptive statistics, accuracy paradox in imbalanced classes,
    confusion matrix calculation (Accuracy, Precision, Recall, F1),
    mean vs median skewness and outlier sensitivity, sample size exploration,
    and correlation vs causation analysis.
    """
    def __init__(self, parent, parent_suite):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.suite = parent_suite
        self.app = parent_suite.app

        self.current_mode = "imbalance"

        self._build_ui()

    def _build_ui(self):
        scroll = SmoothScrollableFrame(self, bg=Theme.BG_ROOT)
        scroll.pack(fill="both", expand=True)
        content = scroll.scrollable_content

        # 1. Header Hero
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.AMBER,
                        highlightthickness=1, padx=24, pady=16)
        hero.pack(fill="x", padx=24, pady=(16, 12))

        tk.Label(hero, text="⚠️ THE STATISTICAL TRAP • DECEPTIVE METRICS & CAUSAL INTERPRETATION WORKSPACE",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.AMBER,
                 padx=8, pady=3).pack(anchor="w")

        tk.Label(hero, text="Statistical Interpretation & Fallacy Investigation",
                 font=("Segoe UI", 18, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))

        tk.Label(hero,
                 text="Uncover misleading statistical conclusions. Investigate how class imbalance generates high accuracy "
                      "without diagnostic value, compare mean versus median resistance to extreme leverage, and audit "
                      "spurious correlations without conflating correlation with causation.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
                 wraplength=850, justify="left").pack(anchor="w")

        # 2. Mode Selector Bar
        mode_bar = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=16, pady=8)
        mode_bar.pack(fill="x", padx=24, pady=(0, 14))

        tk.Label(mode_bar, text="EXPLORATION MODULE:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 12))

        self.mode_buttons = {}
        modes = [
            ("imbalance", "⚠️ Class Imbalance & Confusion Matrix"),
            ("skew", "📊 Mean vs Median Skew & Outlier Pull"),
            ("correlation", "🔗 Correlation vs Causation Warning"),
            ("samplesize", "🎲 Sample Size Variance & Law of Large Numbers"),
            ("custom_data", "✏️ Custom Dataset & Manual Entry")
        ]

        for m_key, m_title in modes:
            btn = tk.Label(mode_bar, text=m_title, font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                           padx=12, pady=5, cursor="hand2",
                           highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda _, k=m_key: self.switch_mode(k))
            self.mode_buttons[m_key] = btn

        # 3. Dynamic Module Workspace Container
        self.module_container = tk.Frame(content, bg=Theme.BG_ROOT)
        self.module_container.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 4. Guided Discussion & Note Taking
        disc_box = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=20, pady=16)
        disc_box.pack(fill="x", padx=24, pady=(0, 24))

        tk.Label(disc_box, text="💡 STATISTICAL DEDUCTION & CRITICAL INTERPRETATION",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.AMBER).pack(anchor="w", pady=(0, 4))

        self.prompt_lbl = tk.Label(disc_box,
                                   text="Prompt: A diagnostic screening model achieves 98.5% accuracy on an imbalanced dataset. Investigate whether its performance is reliable.",
                                   font=("Segoe UI", 9, "italic"),
                                   bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.prompt_lbl.pack(anchor="w", pady=(0, 8))

        t_box = tk.Frame(disc_box, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        t_box.pack(fill="x", pady=(0, 10))

        self.stat_obs_text = tk.Text(t_box, height=4, font=("Segoe UI", 9),
                                     bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                     insertbackground=Theme.CYAN, relief="flat", wrap="word",
                                     padx=8, pady=6)
        self.stat_obs_text.pack(fill="x")
        self.stat_obs_text.insert("1.0", "When prevalence is 1.5%, a naive zero-positive predictor yields 98.5% accuracy. However, Recall is 0.0% and F1-score is 0.0, failing to catch all true positive pathogen carriers. Accuracy alone is an untrustworthy metric under class imbalance.")

        save_btn = tk.Label(disc_box, text=" 💾 Save Statistical Interpretation to Investigation Board ",
                            font=("Segoe UI", 9, "bold"),
                            bg=Theme.AMBER, fg=Theme.BG_ROOT,
                            padx=14, pady=6, cursor="hand2")
        save_btn.pack(side="left")
        save_btn.bind("<Button-1>", lambda _: self._save_stat_obs())

        # Render default mode
        self.switch_mode("imbalance")

    def switch_mode(self, mode_key):
        self.current_mode = mode_key
        for k, b in self.mode_buttons.items():
            if k == mode_key:
                b.config(bg=Theme.BG_CARD_HOVER, fg=Theme.AMBER, highlightbackground=Theme.AMBER)
            else:
                b.config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, highlightbackground=Theme.BORDER_MUTED)

        for child in self.module_container.winfo_children():
            child.destroy()

        if mode_key == "imbalance":
            self._render_imbalance_mode(self.module_container)
            self.prompt_lbl.config(
                text="Prompt: A model achieves 98.5% accuracy on an imbalanced dataset. Investigate whether its performance is reliable by inspecting precision and recall."
            )
        elif mode_key == "skew":
            self._render_skew_mode(self.module_container)
            self.prompt_lbl.config(
                text="Prompt: Compare how the mean and median react to extreme outlier values. Which metric best captures the central tendency of skewed distributions?"
            )
        elif mode_key == "correlation":
            self._render_correlation_mode(self.module_container)
            self.prompt_lbl.config(
                text="Prompt: Two variables exhibit strong positive correlation (r = 0.88). What hidden confounding factor could explain this relationship without causation?"
            )
        elif mode_key == "samplesize":
            self._render_samplesize_mode(self.module_container)
            self.prompt_lbl.config(
                text="Prompt: Observe how small sample sizes create severe sampling noise and apparent anomalies that disappear as sample size increases."
            )
        elif mode_key == "custom_data":
            self._render_custom_data_mode(self.module_container)
            self.prompt_lbl.config(
                text="Prompt: Enter or upload a custom numerical dataset. Analyze its histogram, box plot, and skewness to investigate potential outliers."
            )

    # -------------------------------------------------------------------------
    # MODE 1: CLASS IMBALANCE & CONFUSION MATRIX
    # -------------------------------------------------------------------------
    def _render_imbalance_mode(self, parent):
        box = tk.Frame(parent, bg=Theme.BG_CARD,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=20, pady=16)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="THE ACCURACY PARADOX: CONFUSION MATRIX EVALUATOR",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")

        tk.Label(box,
                 text="In datasets with rare events (e.g. medical diagnosis, fraud detection), a trivial classifier that always "
                      "predicts the majority negative class scores high accuracy despite having zero diagnostic ability.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(2, 12))

        # Presets row
        p_row = tk.Frame(box, bg=Theme.BG_CARD)
        p_row.pack(fill="x", pady=(0, 14))

        tk.Label(p_row, text="Test Scenario Presets:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        presets = [
            ("Rare Pathogen (98.5% Neg, 0% Recall)", 0, 0, 15, 985),
            ("Balanced Classifier (50/50)", 420, 80, 70, 430),
            ("High Sensitivity Screening", 14, 45, 1, 940)
        ]
        for p_name, tp, fp, fn, tn in presets:
            b = tk.Label(p_row, text=p_name, font=("Segoe UI", 8),
                         bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                         padx=8, pady=3, cursor="hand2",
                         highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda _, t=tp, f=fp, n=fn, tn_=tn: self._set_cm_values(t, f, n, tn_))

        # Split: Left Matrix inputs, Right Metric Cards
        split = tk.Frame(box, bg=Theme.BG_CARD)
        split.pack(fill="x")
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=1)

        # Confusion Matrix Grid
        cm_box = tk.Frame(split, bg=Theme.BG_INPUT,
                          highlightbackground=Theme.BORDER_MUTED,
                          highlightthickness=1, padx=14, pady=12)
        cm_box.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(cm_box, text="CONFUSION MATRIX COUNTS", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).grid(row=0, column=0, columnspan=3, pady=(0, 8))

        tk.Label(cm_box, text="", bg=Theme.BG_INPUT).grid(row=1, column=0)
        tk.Label(cm_box, text="Actual Positive (+)", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN).grid(row=1, column=1, padx=6)
        tk.Label(cm_box, text="Actual Negative (-)", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT).grid(row=1, column=2, padx=6)

        tk.Label(cm_box, text="Predicted (+)", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN).grid(row=2, column=0, pady=4, sticky="e")
        tk.Label(cm_box, text="Predicted (-)", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT).grid(row=3, column=0, pady=4, sticky="e")

        self.tp_var = tk.IntVar(value=0)
        self.fp_var = tk.IntVar(value=0)
        self.fn_var = tk.IntVar(value=15)
        self.tn_var = tk.IntVar(value=985)

        def make_cm_cell(r, c, var, label):
            cell = tk.Frame(cm_box, bg=Theme.BG_CARD, padx=6, pady=4)
            cell.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            tk.Label(cell, text=label, font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack()
            e = tk.Spinbox(cell, from_=0, to=100000, textvariable=var, width=8,
                           font=("Segoe UI", 11, "bold"), justify="center",
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                           command=self._calc_cm_metrics)
            e.pack()
            e.bind("<KeyRelease>", lambda _: self._calc_cm_metrics())

        make_cm_cell(2, 1, self.tp_var, "True Positives (TP)")
        make_cm_cell(2, 2, self.fp_var, "False Positives (FP)")
        make_cm_cell(3, 1, self.fn_var, "False Negatives (FN)")
        make_cm_cell(3, 2, self.tn_var, "True Negatives (TN)")

        # Right: Output Metric Cards
        self.metrics_col = tk.Frame(split, bg=Theme.BG_CARD)
        self.metrics_col.grid(row=0, column=1, sticky="nsew")

        self.m_acc_lbl = self._create_cm_card(self.metrics_col, "Accuracy: (TP + TN) / Total", "0.0%", Theme.AMBER)
        self.m_prec_lbl = self._create_cm_card(self.metrics_col, "Precision: TP / (TP + FP)", "0.0%", Theme.CYAN)
        self.m_rec_lbl = self._create_cm_card(self.metrics_col, "Recall (Sensitivity): TP / (TP + FN)", "0.0%", Theme.EMERALD)
        self.m_f1_lbl = self._create_cm_card(self.metrics_col, "F1-Score: Harmonic Mean of P & R", "0.0", Theme.PURPLE_LIGHT)

        self._calc_cm_metrics()

    def _create_cm_card(self, parent, title, val, color):
        f = tk.Frame(parent, bg=Theme.BG_INPUT,
                     highlightbackground=Theme.BORDER_MUTED,
                     highlightthickness=1, padx=12, pady=6)
        f.pack(fill="x", pady=2)
        tk.Label(f, text=title, font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")
        v_lbl = tk.Label(f, text=val, font=("Segoe UI", 14, "bold"), bg=Theme.BG_INPUT, fg=color)
        v_lbl.pack(anchor="w")
        return v_lbl

    def _set_cm_values(self, tp, fp, fn, tn):
        self.tp_var.set(tp)
        self.fp_var.set(fp)
        self.fn_var.set(fn)
        self.tn_var.set(tn)
        self._calc_cm_metrics()

    def _calc_cm_metrics(self):
        try:
            tp = self.tp_var.get()
            fp = self.fp_var.get()
            fn = self.fn_var.get()
            tn = self.tn_var.get()
        except Exception:
            return

        res = DataProcessor.compute_confusion_matrix_metrics(tp, fp, fn, tn)
        self.m_acc_lbl.config(text=f"{res['accuracy'] * 100:.2f}% (Total N={res['total']})")
        self.m_prec_lbl.config(text=f"{res['precision'] * 100:.2f}%")
        self.m_rec_lbl.config(text=f"{res['recall'] * 100:.2f}%")
        self.m_f1_lbl.config(text=f"{res['f1_score']:.3f}")

    # -------------------------------------------------------------------------
    # MODE 2: MEAN VS MEDIAN SKEW & OUTLIER PULL
    # -------------------------------------------------------------------------
    def _render_skew_mode(self, parent):
        box = tk.Frame(parent, bg=Theme.BG_CARD,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=20, pady=16)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="MEAN VS MEDIAN SENSITIVITY TO OUTLIERS",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")

        tk.Label(box,
                 text="The arithmetic mean is pulled towards extreme observations (high leverage), while the median "
                      "remains resilient. Notice how a single high earner distorts the 'average' salary.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(2, 10))

        # Slider to inject outlier
        slider_frame = tk.Frame(box, bg=Theme.BG_INPUT,
                                highlightbackground=Theme.BORDER_MUTED,
                                highlightthickness=1, padx=14, pady=10)
        slider_frame.pack(fill="x", pady=(0, 12))

        tk.Label(slider_frame, text="Executive Salary Outlier Value ($k):",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.AMBER).pack(side="left", padx=(0, 12))

        self.outlier_slider = tk.Scale(slider_frame, from_=50, to=2000, orient="horizontal",
                                       length=350, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                       highlightthickness=0, command=lambda _: self._update_skew_sim())
        self.outlier_slider.set(1200)
        self.outlier_slider.pack(side="left", padx=(0, 16))

        # Output readouts
        self.skew_mean_lbl = tk.Label(slider_frame, text="Mean: $0k", font=("Segoe UI", 11, "bold"),
                                      bg=Theme.BG_INPUT, fg=Theme.AMBER)
        self.skew_mean_lbl.pack(side="left", padx=(0, 16))

        self.skew_med_lbl = tk.Label(slider_frame, text="Median: $0k", font=("Segoe UI", 11, "bold"),
                                     bg=Theme.BG_INPUT, fg=Theme.EMERALD)
        self.skew_med_lbl.pack(side="left")

        # Visual Canvas showing Box Plot / Dot Plot
        self.skew_canvas = tk.Canvas(box, bg=Theme.BG_INPUT, height=180,
                                     highlightthickness=0, borderwidth=0)
        self.skew_canvas.pack(fill="x", expand=True)
        self.skew_canvas.bind("<Configure>", lambda _: self._update_skew_sim())

        self._update_skew_sim()

    def _update_skew_sim(self):
        # Base salaries for 19 workers ($k)
        base = [45, 48, 50, 52, 54, 55, 56, 58, 60, 62, 63, 65, 66, 68, 70, 72, 75, 78, 80]
        outlier = self.outlier_slider.get()
        all_vals = sorted(base + [outlier])

        stats = DataProcessor.compute_descriptive_stats(all_vals)
        mean_v = stats["mean"]
        med_v = stats["median"]

        self.skew_mean_lbl.config(text=f"Mean: ${mean_v:.1f}k")
        self.skew_med_lbl.config(text=f"Median: ${med_v:.1f}k")

        # Draw distribution on canvas
        self.skew_canvas.delete("all")
        w = self.skew_canvas.winfo_width()
        h = self.skew_canvas.winfo_height()
        if w < 50 or h < 50:
            return

        pad_x = 50
        usable_w = w - pad_x * 2
        max_scale = 2100.0

        def to_x(val):
            return pad_x + (val / max_scale) * usable_w

        axis_y = h * 0.65
        self.skew_canvas.create_line(pad_x, axis_y, pad_x + usable_w, axis_y, fill=Theme.BORDER_MUTED, width=1)

        # Draw points
        for v in base:
            cx = to_x(v)
            self.skew_canvas.create_oval(cx - 3, axis_y - 3, cx + 3, axis_y + 3, fill=Theme.CYAN, outline="")

        # Draw outlier point
        ox = to_x(outlier)
        self.skew_canvas.create_polygon(ox, axis_y - 7, ox + 7, axis_y, ox, axis_y + 7, ox - 7, axis_y, fill="#F43F5E")
        self.skew_canvas.create_text(ox, axis_y - 14, text=f"${outlier}k", font=("Segoe UI", 7, "bold"), fill="#FCA5A5")

        # Mean vertical indicator (dashed amber)
        mx = to_x(mean_v)
        self.skew_canvas.create_line(mx, axis_y - 45, mx, axis_y + 20, fill=Theme.AMBER, width=2, dash=(4, 3))
        self.skew_canvas.create_text(mx, axis_y - 50, text=f"Mean: ${mean_v:.0f}k", font=("Segoe UI", 8, "bold"), fill=Theme.AMBER)

        # Median vertical indicator (solid emerald)
        med_x = to_x(med_v)
        self.skew_canvas.create_line(med_x, axis_y - 30, med_x, axis_y + 20, fill=Theme.EMERALD, width=2)
        self.skew_canvas.create_text(med_x, axis_y - 35, text=f"Median: ${med_v:.0f}k", font=("Segoe UI", 8, "bold"), fill=Theme.EMERALD)

    # -------------------------------------------------------------------------
    # MODE 3: CORRELATION VS CAUSATION WARNING
    # -------------------------------------------------------------------------
    def _render_correlation_mode(self, parent):
        box = tk.Frame(parent, bg=Theme.BG_CARD,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=20, pady=16)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="CORRELATION VS CAUSATION & CONFOUNDING FACTORS",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")

        warn_banner = tk.Frame(box, bg="#331A05", highlightbackground=Theme.AMBER, highlightthickness=1, padx=12, pady=8)
        warn_banner.pack(fill="x", pady=(6, 12))
        tk.Label(warn_banner,
                 text="⚠️ CAUTION: High correlation does not establish causation! Two variables can strongly correlate "
                      "due to a common third confounding variable, reverse directionality, or coincidence.",
                 font=("Segoe UI", 9, "bold"),
                 bg="#331A05", fg=Theme.AMBER).pack(anchor="w")

        # Scenario: Ice Cream Sales vs Swimming Drownings
        desc = (
            "Scenario: Monthly tracking of Ice Cream Sales ($k) and Swimming Drowning Incidents across 12 months.\n"
            "Calculated Pearson's r = 0.88 (Strong Positive Correlation).\n"
            "Confounding Variable: Summer Ambient Temperature. Both variables surge in hot summer months and fall in winter."
        )
        tk.Label(box, text=desc, font=("Segoe UI", 9),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, justify="left").pack(anchor="w", pady=(0, 10))

        # Mini Canvas scatter plot
        c = tk.Canvas(box, bg=Theme.BG_INPUT, height=160, highlightthickness=0, borderwidth=0)
        c.pack(fill="x", expand=True)

        data = [
            (12, 2), (14, 3), (18, 4), (25, 6), (38, 12), (52, 18),
            (56, 22), (50, 19), (35, 11), (22, 5), (15, 3), (11, 1)
        ]
        # Draw scatter on c
        w = 400
        h = 160
        pad_x = 40
        pad_y = 25
        for x, y in data:
            px = pad_x + (x / 60.0) * (w - pad_x * 2)
            py = h - pad_y - (y / 25.0) * (h - pad_y * 2)
            c.create_oval(px - 4, py - 4, px + 4, py + 4, fill=Theme.CYAN, outline="")

        # Fitted line
        c.create_line(pad_x, h - pad_y - (0 / 25.0) * (h - pad_y * 2),
                      w - pad_x, h - pad_y - (22 / 25.0) * (h - pad_y * 2),
                      fill=Theme.AMBER, width=2, dash=(4, 3))
        c.create_text(w - 60, 20, text="r = +0.88", font=("Segoe UI", 9, "bold"), fill=Theme.AMBER)

    # -------------------------------------------------------------------------
    # MODE 4: SAMPLE SIZE & VARIANCE
    # -------------------------------------------------------------------------
    def _render_samplesize_mode(self, parent):
        box = tk.Frame(parent, bg=Theme.BG_CARD,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=20, pady=16)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="SAMPLE SIZE EXPLORATION & SAMPLING NOISE",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")

        tk.Label(box,
                 text="Small sample sizes are susceptible to extreme sampling error (Law of Small Numbers). "
                      "As sample size N increases, sample means converge reliably toward true population parameters.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(2, 10))

        # Sample Size slider
        s_frame = tk.Frame(box, bg=Theme.BG_INPUT, padx=12, pady=8)
        s_frame.pack(fill="x", pady=(0, 10))

        tk.Label(s_frame, text="Sample Size (N):", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 10))

        self.sample_n_slider = tk.Scale(s_frame, from_=5, to=500, orient="horizontal",
                                        length=300, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                        highlightthickness=0, command=lambda _: self._update_sample_sim())
        self.sample_n_slider.set(10)
        self.sample_n_slider.pack(side="left", padx=(0, 16))

        self.sample_res_lbl = tk.Label(s_frame, text="Estimated Mean: —", font=("Segoe UI", 10, "bold"),
                                       bg=Theme.BG_INPUT, fg=Theme.CYAN)
        self.sample_res_lbl.pack(side="left")

        self.sample_canvas = tk.Canvas(box, bg=Theme.BG_INPUT, height=150, highlightthickness=0, borderwidth=0)
        self.sample_canvas.pack(fill="x", expand=True)

        self._update_sample_sim()

    def _update_sample_sim(self):
        n = self.sample_n_slider.get()
        # Simulated draws from population with true mean = 50.0, sigma = 15.0
        # Deterministic pseudo-random generation based on index
        draws = [50.0 + 15.0 * math.sin(i * 1.7 + 0.3) for i in range(1, n + 1)]
        sample_mean = sum(draws) / n
        self.sample_res_lbl.config(text=f"Estimated Mean: {sample_mean:.2f} (True: 50.00)")

        self.sample_canvas.delete("all")
        w = self.sample_canvas.winfo_width()
        h = self.sample_canvas.winfo_height()
        if w < 50 or h < 50:
            return

        pad_x = 40
        pad_y = 20
        usable_w = w - pad_x * 2
        usable_h = h - pad_y * 2

        # True mean line
        true_y = pad_y + usable_h * 0.5
        self.sample_canvas.create_line(pad_x, true_y, pad_x + usable_w, true_y, fill=Theme.EMERALD, width=2)
        self.sample_canvas.create_text(pad_x + usable_w + 4, true_y, text="True (50.0)", font=("Segoe UI", 7), fill=Theme.EMERALD, anchor="w")

        # Plot individual points
        step = usable_w / max(n - 1, 1)
        for i, val in enumerate(draws):
            px = pad_x + i * step
            norm = (val - 20.0) / 60.0
            py = pad_y + usable_h - (norm * usable_h)
            self.sample_canvas.create_oval(px - 2, py - 2, px + 2, py + 2, fill=Theme.CYAN, outline="")

    # -------------------------------------------------------------------------
    # MODE 5: CUSTOM DATASET & MANUAL DATA ENTRY
    # -------------------------------------------------------------------------
    def _render_custom_data_mode(self, parent):
        box = tk.Frame(parent, bg=Theme.BG_CARD,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=20, pady=16)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="CUSTOM DATASET INTERPRETATION & MANUAL ENTRY",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")

        tk.Label(box,
                 text="Enter or paste numbers separated by commas, spaces, or lines, or import a CSV file. "
                      "Explore empirical distributions with live Histogram and Box Plot visualizations.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(2, 10))

        # Input Bar
        in_bar = tk.Frame(box, bg=Theme.BG_INPUT,
                          highlightbackground=Theme.BORDER_MUTED,
                          highlightthickness=1, padx=12, pady=10)
        in_bar.pack(fill="x", pady=(0, 10))

        tk.Label(in_bar, text="Enter / Paste Values:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

        self.custom_data_input = tk.Text(in_bar, height=3, font=("Segoe UI", 9),
                                         bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                                         insertbackground=Theme.CYAN, relief="flat")
        self.custom_data_input.pack(fill="x", pady=(0, 8))
        self.custom_data_input.insert("1.0", "12.5, 14.2, 13.8, 15.1, 14.9, 13.2, 15.8, 14.0, 95.5, 14.4, 13.7, 15.2")

        btn_row = tk.Frame(in_bar, bg=Theme.BG_INPUT)
        btn_row.pack(fill="x")

        calc_btn = tk.Label(btn_row, text=" ⚡ Calculate & Plot ", font=("Segoe UI", 9, "bold"),
                            bg=Theme.AMBER, fg=Theme.BG_ROOT, padx=12, pady=5, cursor="hand2")
        calc_btn.pack(side="left", padx=(0, 10))
        calc_btn.bind("<Button-1>", lambda _: self._update_custom_data_analysis())

        upload_btn = tk.Label(btn_row, text=" 📁 Upload CSV... ", font=("Segoe UI", 8, "bold"),
                              bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, padx=10, pady=5, cursor="hand2",
                              highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        upload_btn.pack(side="left", padx=(0, 10))
        upload_btn.bind("<Button-1>", lambda _: self._upload_custom_csv())

        # Descriptive metrics readouts
        self.custom_metrics_lbl = tk.Label(btn_row, text="Mean: — | Median: — | Std Dev: — | Skew: —",
                                           font=("Segoe UI", 9, "bold"),
                                           bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT)
        self.custom_metrics_lbl.pack(side="right")

        # Canvas showing Histogram (left) and Box Plot (right)
        self.custom_canvas = tk.Canvas(box, bg=Theme.BG_INPUT, height=200,
                                       highlightthickness=0, borderwidth=0)
        self.custom_canvas.pack(fill="x", expand=True)
        self.custom_canvas.bind("<Configure>", lambda _: self._draw_custom_canvas())

        self.custom_series_values = []
        self._update_custom_data_analysis()

    def _update_custom_data_analysis(self):
        raw = self.custom_data_input.get("1.0", "end-1c")
        tokens = raw.replace(",", " ").replace(";", " ").split()
        vals = []
        for t in tokens:
            try:
                vals.append(float(t))
            except ValueError:
                pass

        if not vals:
            self.custom_metrics_lbl.config(text="Please enter at least one valid number.")
            return

        self.custom_series_values = vals
        stats = DataProcessor.compute_descriptive_stats(vals)
        mean_v = stats["mean"]
        med_v = stats["median"]
        std_v = stats["stdev"]

        diff = mean_v - med_v
        if std_v > 0 and abs(diff) / std_v > 0.15:
            skew_str = "Right-Skewed (Mean > Median)" if diff > 0 else "Left-Skewed (Mean < Median)"
        else:
            skew_str = "Symmetric (Mean ≈ Median)"

        self.custom_metrics_lbl.config(
            text=f"N={stats['count']} | Mean: {mean_v:.2f} | Median: {med_v:.2f} | σ: {std_v:.2f} | {skew_str}"
        )
        self._draw_custom_canvas()

    def _upload_custom_csv(self):
        filetypes = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select CSV Dataset", filetypes=filetypes)
        if not filepath:
            return
        headers, rows, meta = DataProcessor.parse_csv_file(filepath)
        if not meta.get("success"):
            messagebox.showerror("Error", meta.get("error", "Failed to parse CSV file."), parent=self)
            return

        num_cols = meta.get("numeric_columns", [])
        if not num_cols:
            messagebox.showwarning("No Numeric Columns", "No numerical columns found in this CSV.", parent=self)
            return

        col = num_cols[0]
        series = DataProcessor.extract_numeric_series(headers, rows, col)
        vals = [v for _, v in series]
        self.custom_data_input.delete("1.0", "end")
        self.custom_data_input.insert("1.0", ", ".join(f"{v:.2f}" for v in vals[:200]))
        self._update_custom_data_analysis()

    def _draw_custom_canvas(self):
        self.custom_canvas.delete("all")
        w = self.custom_canvas.winfo_width()
        h = self.custom_canvas.winfo_height()
        if w < 100 or h < 80 or not self.custom_series_values:
            return

        vals = sorted(self.custom_series_values)
        stats = DataProcessor.compute_descriptive_stats(vals)
        min_v = stats["min"]
        max_v = stats["max"]
        if min_v == max_v: min_v -= 1; max_v += 1
        span_v = max_v - min_v

        pad_x = 45
        pad_y = 25
        mid_x = w * 0.52

        # 1. Left Half: Histogram
        usable_hist_w = (mid_x - 30) - pad_x
        usable_h = h - pad_y * 2

        num_bins = 6
        bin_width = span_v / num_bins
        bins = [0] * num_bins
        for v in vals:
            b_idx = min(int((v - min_v) / bin_width), num_bins - 1)
            bins[b_idx] += 1
        max_freq = max(bins) if max(bins) > 0 else 1

        self.custom_canvas.create_text(pad_x + usable_hist_w * 0.5, 12,
                                       text="FREQUENCY HISTOGRAM", font=("Segoe UI", 8, "bold"),
                                       fill=Theme.TEXT_SECONDARY)

        bar_slot = usable_hist_w / num_bins
        for i, count in enumerate(bins):
            bx = pad_x + i * bar_slot
            bar_h = (count / max_freq) * (usable_h - 20)
            by = pad_y + usable_h - bar_h
            self.custom_canvas.create_rectangle(bx + 2, by, bx + bar_slot - 4, pad_y + usable_h,
                                                fill="#1A344A", outline=Theme.CYAN, width=1)
            if count > 0:
                self.custom_canvas.create_text(bx + bar_slot * 0.5, by - 6,
                                               text=str(count), font=("Segoe UI", 7), fill=Theme.CYAN_BRIGHT)

        self.custom_canvas.create_line(pad_x, pad_y + usable_h, pad_x + usable_hist_w, pad_y + usable_h,
                                       fill=Theme.BORDER_MUTED, width=1)

        # 2. Divider line between Histogram and Box Plot
        self.custom_canvas.create_line(mid_x, 15, mid_x, h - 15, fill=Theme.BORDER_SUBTLE, width=1)

        # 3. Right Half: Box Plot
        box_start_x = mid_x + 30
        usable_box_w = (w - pad_x) - box_start_x

        self.custom_canvas.create_text(box_start_x + usable_box_w * 0.5, 12,
                                       text="BOX & WHISKER PLOT", font=("Segoe UI", 8, "bold"),
                                       fill=Theme.TEXT_SECONDARY)

        def to_box_x(val):
            return box_start_x + ((val - min_v) / span_v) * usable_box_w

        axis_y = pad_y + usable_h * 0.55
        self.custom_canvas.create_line(box_start_x, axis_y, box_start_x + usable_box_w, axis_y,
                                       fill=Theme.BORDER_MUTED, width=1)

        q1_x = to_box_x(stats["q1"])
        q2_x = to_box_x(stats["median"])
        q3_x = to_box_x(stats["q3"])
        low_f_x = to_box_x(max(min_v, stats["q1"] - 1.5 * stats["iqr"]))
        high_f_x = to_box_x(min(max_v, stats["q3"] + 1.5 * stats["iqr"]))

        # Whiskers
        self.custom_canvas.create_line(low_f_x, axis_y, q1_x, axis_y, fill=Theme.TEXT_MUTED, width=2)
        self.custom_canvas.create_line(q3_x, axis_y, high_f_x, axis_y, fill=Theme.TEXT_MUTED, width=2)
        self.custom_canvas.create_line(low_f_x, axis_y - 10, low_f_x, axis_y + 10, fill=Theme.TEXT_MUTED, width=2)
        self.custom_canvas.create_line(high_f_x, axis_y - 10, high_f_x, axis_y + 10, fill=Theme.TEXT_MUTED, width=2)

        # IQR Box
        self.custom_canvas.create_rectangle(q1_x, axis_y - 20, q3_x, axis_y + 20,
                                            fill="#221C38", outline=Theme.PURPLE_LIGHT, width=2)

        # Median Line (Emerald)
        self.custom_canvas.create_line(q2_x, axis_y - 20, q2_x, axis_y + 20,
                                       fill=Theme.EMERALD, width=3)
        self.custom_canvas.create_text(q2_x, axis_y + 28, text=f"Med:{stats['median']:.1f}",
                                       font=("Segoe UI", 7, "bold"), fill=Theme.EMERALD)

        # Mean Line (Amber dashed)
        mean_x = to_box_x(stats["mean"])
        self.custom_canvas.create_line(mean_x, axis_y - 30, mean_x, axis_y + 30,
                                       fill=Theme.AMBER, width=2, dash=(3, 3))
        self.custom_canvas.create_text(mean_x, axis_y - 36, text=f"Mean:{stats['mean']:.1f}",
                                       font=("Segoe UI", 7, "bold"), fill=Theme.AMBER)

        # Outlier points outside fences
        low_fence_val = stats["q1"] - 1.5 * stats["iqr"]
        high_fence_val = stats["q3"] + 1.5 * stats["iqr"]
        for v in vals:
            if v < low_fence_val or v > high_fence_val:
                ox = to_box_x(v)
                self.custom_canvas.create_oval(ox - 4, axis_y - 4, ox + 4, axis_y + 4,
                                               fill="#F43F5E", outline="#FFFFFF")
                self.custom_canvas.create_text(ox, axis_y - 12, text=f"{v:.1f}",
                                               font=("Segoe UI", 7, "bold"), fill="#FCA5A5")

    def _save_stat_obs(self):
        text = self.stat_obs_text.get("1.0", "end-1c").strip()
        if hasattr(self.app, "state") and self.app.state:
            if hasattr(self.app.state, "investigation_stages"):
                stages = self.app.state.investigation_stages
                if "analysis" in stages:
                    existing = stages["analysis"].get("notes", "")
                    updated = f"{existing}\n\n[Statistical Trap Audit]:\n{text}".strip() if existing else f"[Statistical Trap Audit]:\n{text}"
                    stages["analysis"]["notes"] = updated
                    stages["analysis"]["status"] = "Completed"
            self.app.state.notify()
            messagebox.showinfo("Saved", "Statistical deductions recorded to Investigation Board (Stage 4).", parent=self)


# =============================================================================
# SUBVIEW 4: PATTERN MYSTERY (PATTERN DISCOVERY WORKSPACE)
# =============================================================================

class PatternMysteryWorkspace(tk.Frame):
    """
    Pattern Mystery workspace:
    - Variable X and Y selection
    - Scatter plots, line plots, regression fit
    - Pearson correlation r and R^2 calculation
    - Residual outlier / unusual observation discovery
    - Comparison across multiple educational datasets
    - Guided pattern deduction recording
    """
    def __init__(self, parent, parent_suite):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.suite = parent_suite
        self.app = parent_suite.app

        self.current_headers = []
        self.current_rows = []
        self.dataset_meta = {}

        self.x_col_var = tk.StringVar()
        self.y_col_var = tk.StringVar()
        self.plot_type_var = tk.StringVar(value="Scatter + Trendline")
        self.show_trendline_var = tk.BooleanVar(value=True)
        self.highlight_residuals_var = tk.BooleanVar(value=True)

        self.bivariate_results = {}

        self._build_ui()
        self._load_pattern_preset("study_vs_exam")

    def _build_ui(self):
        scroll = SmoothScrollableFrame(self, bg=Theme.BG_ROOT)
        scroll.pack(fill="both", expand=True)
        content = scroll.scrollable_content

        # 1. Header Banner
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.TEAL,
                        highlightthickness=1, padx=24, pady=16)
        hero.pack(fill="x", padx=24, pady=(16, 12))

        tk.Label(hero, text="🧩 THE PATTERN MYSTERY • INTERACTIVE PATTERN DISCOVERY WORKSPACE",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEAL,
                 padx=8, pady=3).pack(anchor="w")

        tk.Label(hero, text="Bivariate Pattern Exploration & Trend Discovery",
                 font=("Segoe UI", 18, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))

        tk.Label(hero,
                 text="Select independent and dependent variables, plot empirical relationships, calculate Pearson's r "
                      "and linear trendlines, and discover unusual observations. Note: Linear correlation measures linear "
                      "association only; it does not prove causal mechanisms or non-linear dynamics.",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
                 wraplength=850, justify="left").pack(anchor="w")

        # 2. Controls & Preset Bar
        c_bar = tk.Frame(content, bg=Theme.BG_CARD,
                         highlightbackground=Theme.BORDER_SUBTLE,
                         highlightthickness=1, padx=16, pady=10)
        c_bar.pack(fill="x", padx=24, pady=(0, 12))

        # Import CSV
        import_btn = tk.Label(c_bar, text=" 📁 Import CSV... ",
                              font=("Segoe UI", 8, "bold"),
                              bg=Theme.BG_INPUT, fg=Theme.TEAL,
                              padx=8, pady=4, cursor="hand2",
                              highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        import_btn.pack(side="left", padx=(0, 6))
        import_btn.bind("<Button-1>", lambda _: self._import_csv_dialog())

        # Manual Entry
        manual_btn = tk.Label(c_bar, text=" ✏️ Manual (X,Y) Entry ",
                              font=("Segoe UI", 8, "bold"),
                              bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                              padx=8, pady=4, cursor="hand2",
                              highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        manual_btn.pack(side="left", padx=(0, 12))
        manual_btn.bind("<Button-1>", lambda _: self._open_manual_entry_modal())

        tk.Label(c_bar, text="Or Presets:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 6))

        self.preset_combo = ttk.Combobox(c_bar,
                                         values=[
                                             "Study Duration vs Exam Score (Linear)",
                                             "Temperature vs Catalysis Rate (Inverted-U)",
                                             "Planetary Distance vs Period (Power Law)",
                                             "Damped Harmonic Oscillation (Decay)"
                                         ],
                                         state="readonly", width=32)
        self.preset_combo.current(0)
        self.preset_combo.pack(side="left", padx=(0, 14))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        # X & Y selectors
        tk.Label(c_bar, text="X Variable:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.x_combo = ttk.Combobox(c_bar, textvariable=self.x_col_var, state="readonly", width=16)
        self.x_combo.pack(side="left", padx=(0, 12))
        self.x_combo.bind("<<ComboboxSelected>>", lambda _: self._update_pattern())

        tk.Label(c_bar, text="Y Variable:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        self.y_combo = ttk.Combobox(c_bar, textvariable=self.y_col_var, state="readonly", width=16)
        self.y_combo.pack(side="left", padx=(0, 16))
        self.y_combo.bind("<<ComboboxSelected>>", lambda _: self._update_pattern())

        # 3. Canvas & Trend Results Split View
        main_split = tk.Frame(content, bg=Theme.BG_ROOT)
        main_split.pack(fill="both", expand=True, padx=24, pady=(0, 14))
        main_split.columnconfigure(0, weight=3)
        main_split.columnconfigure(1, weight=2)

        # Left: Canvas
        canvas_box = tk.Frame(main_split, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_SUBTLE,
                              highlightthickness=1, padx=14, pady=12)
        canvas_box.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        cv_hdr = tk.Frame(canvas_box, bg=Theme.BG_CARD)
        cv_hdr.pack(fill="x", pady=(0, 6))
        tk.Label(cv_hdr, text="BIVARIATE PATTERN VISUALIZER",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")
        self.canvas_pts_lbl = tk.Label(cv_hdr, text="25 observations",
                                       font=("Segoe UI", 8),
                                       bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.canvas_pts_lbl.pack(side="right")

        self.pattern_canvas = tk.Canvas(canvas_box, bg=Theme.BG_INPUT, height=260,
                                        highlightthickness=0, borderwidth=0)
        self.pattern_canvas.pack(fill="both", expand=True)
        self.pattern_canvas.bind("<Configure>", lambda _: self._draw_pattern_canvas())

        # Right: Statistical Trend Metrics
        trend_box = tk.Frame(main_split, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=16, pady=14)
        trend_box.grid(row=0, column=1, sticky="nsew")

        tk.Label(trend_box, text="STATISTICAL TREND PROFILE",
                 font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 8))

        self.m_r_lbl = self._create_trend_card(trend_box, "Pearson Correlation (r)", "0.00", Theme.TEAL)
        self.m_r2_lbl = self._create_trend_card(trend_box, "Coefficient of Determination (R²)", "0.00", Theme.CYAN)
        self.m_eqn_lbl = self._create_trend_card(trend_box, "Regression Trend: y = mx + b", "y = 0x + 0", Theme.PURPLE_LIGHT)
        self.m_unusual_lbl = self._create_trend_card(trend_box, "Unusual Observations (|Residual| > 2σ)", "0 points", Theme.AMBER)

        # 4. Pattern Observations & Explanations Panel
        disc_box = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=20, pady=16)
        disc_box.pack(fill="x", padx=24, pady=(0, 24))

        tk.Label(disc_box, text="💡 PATTERN INTERPRETATION & EXPLANATION",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEAL).pack(anchor="w", pady=(0, 4))

        prompts = [
            "• What functional relationship is visible between X and Y (linear, inverted-U, periodic, or clustered)?",
            "• Do any points deviate dramatically from the trendline (high residual outlier)?",
            "• What physical, biological, or behavioral mechanism accounts for this observed pattern?"
        ]
        tk.Label(disc_box, text="\n".join(prompts),
                 font=("Segoe UI", 8, "italic"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED,
                 justify="left").pack(anchor="w", pady=(0, 8))

        t_box = tk.Frame(disc_box, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        t_box.pack(fill="x", pady=(0, 10))

        self.pattern_notes = tk.Text(t_box, height=4, font=("Segoe UI", 9),
                                     bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                     insertbackground=Theme.CYAN, relief="flat", wrap="word",
                                     padx=8, pady=6)
        self.pattern_notes.pack(fill="x")
        self.pattern_notes.insert("1.0", "Strong positive linear correlation (r = +0.89) between study hours and exam scores. Observation #20 (9.0 hrs, 52%) is a high-residual negative outlier, likely reflecting acute fatigue or illness during the examination.")

        save_btn = tk.Label(disc_box, text=" 💾 Save Pattern Deductions to Investigation Board ",
                            font=("Segoe UI", 9, "bold"),
                            bg=Theme.TEAL, fg=Theme.BG_ROOT,
                            padx=14, pady=6, cursor="hand2")
        save_btn.pack(side="left")
        save_btn.bind("<Button-1>", lambda _: self._save_pattern_notes())

    def _create_trend_card(self, parent, title, val, color):
        f = tk.Frame(parent, bg=Theme.BG_INPUT,
                     highlightbackground=Theme.BORDER_MUTED,
                     highlightthickness=1, padx=12, pady=6)
        f.pack(fill="x", pady=2)
        tk.Label(f, text=title, font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")
        v_lbl = tk.Label(f, text=val, font=("Segoe UI", 12, "bold"), bg=Theme.BG_INPUT, fg=color)
        v_lbl.pack(anchor="w")
        return v_lbl

    def _on_preset_selected(self, event=None):
        idx = self.preset_combo.current()
        keys = ["study_vs_exam", "temperature_vs_enzyme", "planetary_kepler", "damped_oscillation"]
        if 0 <= idx < len(keys):
            self._load_pattern_preset(keys[idx])

    def _load_pattern_preset(self, key):
        p = PATTERN_DATASETS.get(key)
        if not p:
            return
        headers, rows, meta = DataProcessor.parse_csv_text(p["text"], filename=p["title"])
        self.current_headers = headers
        self.current_rows = rows
        self.dataset_meta = meta

        num_cols = meta.get("numeric_columns", headers)
        self.x_combo.config(values=num_cols)
        self.y_combo.config(values=num_cols)

        if p.get("x_col") in num_cols:
            self.x_col_var.set(p["x_col"])
        elif len(num_cols) > 0:
            self.x_col_var.set(num_cols[0])

        if p.get("y_col") in num_cols:
            self.y_col_var.set(p["y_col"])
        elif len(num_cols) > 1:
            self.y_col_var.set(num_cols[1])

        self._update_pattern()

    def _update_pattern(self):
        x_col = self.x_col_var.get()
        y_col = self.y_col_var.get()
        if not x_col or not y_col or not self.current_rows:
            return

        x_series = DataProcessor.extract_numeric_series(self.current_headers, self.current_rows, x_col)
        y_series = DataProcessor.extract_numeric_series(self.current_headers, self.current_rows, y_col)

        self.bivariate_results = DataProcessor.compute_bivariate_regression(x_series, y_series)
        res = self.bivariate_results

        # Update labels
        r = res["r"]
        r_desc = "Strong Positive" if r > 0.7 else ("Moderate Positive" if r > 0.3 else ("Weak / None" if abs(r) <= 0.3 else ("Moderate Negative" if r > -0.7 else "Strong Negative")))
        self.m_r_lbl.config(text=f"r = {r:+.3f} ({r_desc})")
        self.m_r2_lbl.config(text=f"R² = {res['r2']:.3f} (Explains {res['r2']*100:.1f}% variance)")

        slope = res["slope"]
        inter = res["intercept"]
        self.m_eqn_lbl.config(text=f"y = {slope:.3f}x + {inter:.2f}")

        unusual = res["unusual_indices"]
        self.m_unusual_lbl.config(text=f"{len(unusual)} point(s) flagged")

        self.canvas_pts_lbl.config(text=f"{res['n']} paired observations")
        self._draw_pattern_canvas()

    def _draw_pattern_canvas(self):
        self.pattern_canvas.delete("all")
        w = self.pattern_canvas.winfo_width()
        h = self.pattern_canvas.winfo_height()
        pairs = self.bivariate_results.get("pairs", [])
        if w < 50 or h < 50 or not pairs:
            return

        pad_x = 55
        pad_y = 35
        usable_w = w - pad_x * 2
        usable_h = h - pad_y * 2

        xs = [p[1] for p in pairs]
        ys = [p[2] for p in pairs]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        if min_x == max_x: min_x -= 1; max_x += 1
        if min_y == max_y: min_y -= 1; max_y += 1

        def to_canvas(x, y):
            cx = pad_x + ((x - min_x) / (max_x - min_x)) * usable_w
            cy = pad_y + usable_h - (((y - min_y) / (max_y - min_y)) * usable_h)
            return cx, cy

        # Axes
        self.pattern_canvas.create_line(pad_x, pad_y + usable_h, pad_x + usable_w, pad_y + usable_h, fill=Theme.BORDER_MUTED, width=1)
        self.pattern_canvas.create_line(pad_x, pad_y, pad_x, pad_y + usable_h, fill=Theme.BORDER_MUTED, width=1)

        # Axis tick marks and labels
        self.pattern_canvas.create_text(pad_x, pad_y + usable_h + 12, text=f"{min_x:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED)
        self.pattern_canvas.create_text(pad_x + usable_w, pad_y + usable_h + 12, text=f"{max_x:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED)
        self.pattern_canvas.create_text(pad_x - 8, pad_y + usable_h, text=f"{min_y:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED, anchor="e")
        self.pattern_canvas.create_text(pad_x - 8, pad_y, text=f"{max_y:.1f}", font=("Segoe UI", 7), fill=Theme.TEXT_MUTED, anchor="e")

        # Linear regression trendline
        slope = self.bivariate_results.get("slope", 0)
        inter = self.bivariate_results.get("intercept", 0)
        y_start = slope * min_x + inter
        y_end = slope * max_x + inter
        x1_c, y1_c = to_canvas(min_x, y_start)
        x2_c, y2_c = to_canvas(max_x, y_end)
        self.pattern_canvas.create_line(x1_c, y1_c, x2_c, y2_c, fill=Theme.TEAL, width=2, dash=(5, 3))

        # Plot data points
        unusual_set = self.bivariate_results.get("unusual_indices", set())
        for idx, x, y in pairs:
            cx, cy = to_canvas(x, y)
            is_unusual = (idx in unusual_set)
            if is_unusual:
                # Halo around unusual observation
                self.pattern_canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="", outline=Theme.AMBER, width=2)
                self.pattern_canvas.create_polygon(cx, cy - 5, cx + 5, cy, cx, cy + 5, cx - 5, cy, fill="#F59E0B")
                self.pattern_canvas.create_text(cx, cy - 12, text=f"#{idx+1}", font=("Segoe UI", 7, "bold"), fill=Theme.AMBER)
            else:
                self.pattern_canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=Theme.CYAN, outline="")

    def _save_pattern_notes(self):
        text = self.pattern_notes.get("1.0", "end-1c").strip()
        if hasattr(self.app, "state") and self.app.state:
            if hasattr(self.app.state, "investigation_stages"):
                stages = self.app.state.investigation_stages
                if "observations" in stages:
                    existing = stages["observations"].get("notes", "")
                    updated = f"{existing}\n\n[Pattern Mystery Deductions]:\n{text}".strip() if existing else f"[Pattern Mystery Deductions]:\n{text}"
                    stages["observations"]["notes"] = updated
                    stages["observations"]["status"] = "Completed"
                if "analysis" in stages:
                    stages["analysis"]["status"] = "Completed"
            self.app.state.notify()
            messagebox.showinfo("Saved", "Pattern deductions recorded to Investigation Board (Stages 4 & 5).", parent=self)

    def _import_csv_dialog(self):
        filetypes = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        filepath = filedialog.askopenfilename(title="Import Pattern Dataset", filetypes=filetypes)
        if not filepath:
            return
        headers, rows, meta = DataProcessor.parse_csv_file(filepath)
        if not meta.get("success"):
            messagebox.showerror("Error", meta.get("error", "Failed to parse CSV file."), parent=self)
            return

        self.current_headers = headers
        self.current_rows = rows
        self.dataset_meta = meta
        num_cols = meta.get("numeric_columns", headers)
        self.x_combo.config(values=num_cols)
        self.y_combo.config(values=num_cols)
        if len(num_cols) > 0: self.x_col_var.set(num_cols[0])
        if len(num_cols) > 1: self.y_col_var.set(num_cols[1])
        self._update_pattern()

    def _open_manual_entry_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Manual Data Entry: (X, Y) Pairs")
        modal.geometry("450x380")
        modal.configure(bg=Theme.BG_ROOT)
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="Enter / Paste (X, Y) Data Pairs", font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(modal, text="Format: X, Y (one coordinate pair per line)", font=("Segoe UI", 8),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 10))

        txt = tk.Text(modal, font=("Segoe UI", 10), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                      insertbackground=Theme.CYAN, relief="flat", padx=8, pady=8)
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        txt.insert("1.0", "1.0, 2.5\n2.0, 5.1\n3.0, 7.8\n4.0, 10.2\n5.0, 12.6\n6.0, 28.0\n7.0, 17.5\n8.0, 20.1\n")

        def apply_manual_pairs():
            raw = txt.get("1.0", "end-1c").strip()
            if not raw:
                modal.destroy()
                return
            rows = []
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.replace(";", ",").replace("\t", ",").split(",")
                if len(parts) >= 2:
                    try:
                        x = float(parts[0].strip())
                        y = float(parts[1].strip())
                        rows.append([str(x), str(y)])
                    except ValueError:
                        pass

            if len(rows) < 2:
                messagebox.showwarning("Insufficient Points", "Please enter at least 2 valid numeric (X, Y) pairs.", parent=modal)
                return

            self.current_headers = ["variable_x", "variable_y"]
            self.current_rows = rows
            self.dataset_meta = {"filename": "Manual Entry (X, Y)", "numeric_columns": self.current_headers}
            self.x_combo.config(values=self.current_headers)
            self.y_combo.config(values=self.current_headers)
            self.x_col_var.set("variable_x")
            self.y_col_var.set("variable_y")
            self._update_pattern()
            modal.destroy()

        b_row = tk.Frame(modal, bg=Theme.BG_ROOT)
        b_row.pack(fill="x", padx=20, pady=(0, 16))
        load_btn = tk.Label(b_row, text=" Apply (X, Y) Points ", font=("Segoe UI", 9, "bold"),
                            bg=Theme.TEAL, fg=Theme.BG_ROOT, padx=14, pady=6, cursor="hand2")
        load_btn.pack(side="left")
        load_btn.bind("<Button-1>", lambda _: apply_manual_pairs())

        cancel_btn = tk.Label(b_row, text=" Cancel ", font=("Segoe UI", 9),
                              bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, padx=12, pady=6, cursor="hand2")
        cancel_btn.pack(side="left", padx=(10, 0))
        cancel_btn.bind("<Button-1>", lambda _: modal.destroy())


# =============================================================================
# MAIN RESEARCH DETECTIVE VIEW CONTAINER
# =============================================================================

class ResearchDetectiveView(tk.Frame):
    """
    Main Research Detective Container:
    - 4 Interactive Investigation Workspaces:
      1. overview: Detective Map (Investigation Board)
      2. data: Data Detective (Dataset Anomaly Investigation)
      3. stat: Statistical Trap (Statistical Interpretation Workspace)
      4. pattern: Pattern Mystery (Pattern Discovery Workspace)
    - Cipher Room removed cleanly without quiz mechanisms.
    - Synchronized with centralized AppState.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        self.current_sub_view = "overview"
        self.sub_views = {}
        self.subnav_buttons = {}

        # 1. Top Sub-Navigation Bar
        self._build_sub_navbar()

        # 2. Sub-views Container
        self.content_box = tk.Frame(self, bg=Theme.BG_ROOT)
        self.content_box.pack(fill="both", expand=True)

        # 3. Instantiate Sub-Views
        self.sub_views["overview"] = DetectiveMapView(self.content_box, self)
        self.sub_views["data"] = DataDetectiveWorkspace(self.content_box, self)
        self.sub_views["stat"] = StatisticalTrapWorkspace(self.content_box, self)
        self.sub_views["pattern"] = PatternMysteryWorkspace(self.content_box, self)

        # Backward compatibility alias
        self.sub_views["map"] = self.sub_views["overview"]

        # Default subview
        self.switch_to_subview("overview")

        # Subscribe to AppState observer
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

    def _build_sub_navbar(self):
        bar = tk.Frame(self, bg=Theme.BG_HEADER,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=24, pady=8)
        bar.pack(fill="x", side="top")

        lbl = tk.Label(bar, text="INVESTIGATION SUITE:", font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        lbl.pack(side="left", padx=(0, 12))

        tabs = [
            ("overview", "🗺️ Detective Map", Theme.PURPLE),
            ("data", "🔍 Data Detective", Theme.CYAN),
            ("stat", "⚠️ Statistical Trap", Theme.AMBER),
            ("pattern", "🧩 Pattern Mystery", Theme.TEAL),
        ]

        for key, title, accent in tabs:
            btn_frame = tk.Frame(bar, bg=Theme.BG_INPUT,
                                 highlightbackground=Theme.BORDER_MUTED,
                                 highlightthickness=1, cursor="hand2")
            btn_frame.pack(side="left", padx=(0, 8))

            btn_lbl = tk.Label(btn_frame, text=title, font=("Segoe UI", 9, "bold"),
                               bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                               padx=12, pady=5, cursor="hand2")
            btn_lbl.pack()

            for w in (btn_frame, btn_lbl):
                w.bind("<Button-1>", lambda _, k=key: self.switch_to_subview(k))
                w.bind("<Enter>", lambda _, bf=btn_frame, bl=btn_lbl, k=key: self._on_tab_hover(bf, bl, k, True))
                w.bind("<Leave>", lambda _, bf=btn_frame, bl=btn_lbl, k=key: self._on_tab_hover(bf, bl, k, False))

            self.subnav_buttons[key] = {
                "frame": btn_frame,
                "label": btn_lbl,
                "accent": accent,
                "title": title
            }

    def _on_tab_hover(self, frame, label, key, entering):
        if key != self.current_sub_view:
            if entering:
                frame.config(bg=Theme.BG_CARD)
                label.config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
            else:
                frame.config(bg=Theme.BG_INPUT)
                label.config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

    def switch_to_subview(self, key):
        if key == "map":
            key = "overview"
        if key not in self.sub_views:
            return

        prev = self.current_sub_view
        self.current_sub_view = key

        # Update styling
        for k, item in self.subnav_buttons.items():
            if k == key:
                item["frame"].config(bg=Theme.BG_CARD_HOVER, highlightbackground=item["accent"])
                item["label"].config(bg=Theme.BG_CARD_HOVER, fg=item["accent"])
            else:
                item["frame"].config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
                item["label"].config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

        self.sub_views[key].pack(fill="both", expand=True)
        if prev and prev != key and prev in self.sub_views:
            self.sub_views[prev].pack_forget()
        for k, v in self.sub_views.items():
            if k != key and k != prev:
                v.pack_forget()

    # Legacy method compatibility
    def switch_to_challenge(self, key):
        self.switch_to_subview(key)

    def _on_app_state_changed(self):
        # Refresh any active views if needed
        pass
