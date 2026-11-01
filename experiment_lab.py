"""
CurioLab — Experiment Lab (Custom Experiment Builder & Research Documentation)
==============================================================================
Stage 7 Transformation:
- Safe Mathematical Expression Engine (Python AST allowlist, no eval/exec)
- Experiment Execution Engine (series evaluation, parameter sweeps, statistical summaries)
- 8 Educational Experiment Templates
- Experiment Creation Wizard (5 structured steps)
- My Experiments Management (create, edit, duplicate, delete, search, filter, sort)
- Results & Visualization (Tkinter Canvas line, scatter, histogram, interactive sliders, CSV export)
- Experiment Discussion & Research Documentation (13 scientific fields, hypothesis verification)
- Experiment Run History & Multi-Run Comparison (overlay plots, parameter diffs)
- Discovery Journal Integration (transfer complete experiment dossiers)
- Built-in Experiments Preserved (Caesar Cipher, Single Neuron, Data Visualization Lab)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ast
import math
import statistics
import csv
import datetime
import random
import sys

from theme import Theme
from app_state import AppState


# =============================================================================
# REUSABLE MODERN BUTTON & SCROLLABLE CONTAINER
# =============================================================================

class ModernButton(tk.Frame):
    """A custom styled button with hover animations and smooth rounded pill feel."""
    def __init__(self, parent, text, command=None, bg_color=Theme.BLUE,
                 hover_color=None, text_color=Theme.TEXT_ON_ACCENT,
                 font=("Segoe UI", 10, "bold"), padx=14, pady=7,
                 icon="", width=None, cursor="hand2"):
        super().__init__(parent, bg=bg_color, cursor=cursor)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color if hover_color else self._adjust_color(bg_color)
        self.text_color = text_color
        self._disabled = False

        self.label = tk.Label(
            self,
            text=f"{icon} {text}".strip() if icon else text,
            font=font,
            bg=bg_color,
            fg=text_color,
            cursor=cursor,
            padx=padx,
            pady=pady
        )
        if width:
            self.label.config(width=width)
        self.label.pack(fill="both", expand=True)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)

    def _adjust_color(self, hex_color):
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                return hex_color
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = min(255, int(r * 1.15) + 12)
            g = min(255, int(g * 1.15) + 12)
            b = min(255, int(b * 1.15) + 12)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _on_enter(self, _):
        if not self._disabled:
            self.config(bg=self.hover_color)
            self.label.config(bg=self.hover_color)

    def _on_leave(self, _):
        if not self._disabled:
            self.config(bg=self.bg_color)
            self.label.config(bg=self.bg_color)

    def _on_click(self, _):
        if not self._disabled and self.command:
            self.command()


class ScrollableFrame(tk.Frame):
    """A smooth scrollable container using Canvas and Scrollbar."""
    def __init__(self, parent, bg=Theme.BG_ROOT, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0, yscrollincrement=1)
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
# 1. SAFE MATHEMATICAL EXPRESSION ENGINE (PYTHON AST-BASED)
# =============================================================================

class MathExpressionEngine:
    """
    Dedicated safe mathematical expression parser and evaluator.
    Strictly forbids eval() and exec().
    Uses an explicit allowlist of Python AST nodes, mathematical operators,
    constants (pi, e, tau), and functions.
    """

    # Allowed math functions
    ALLOWED_FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "radians": math.radians,
        "degrees": math.degrees,
        "round": round,
        "min": min,
        "max": max,
    }

    # Allowed mathematical constants
    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    @classmethod
    def extract_variables_and_equation(cls, equation_str):
        """
        Parses equation string like 'y = m * x + c' or 'f(x) = ...' or 'y = ...'
        Returns (output_variable, expression_string, set_of_input_symbols).
        """
        raw = equation_str.strip()
        output_var = "y"
        expr_str = raw

        if "=" in raw:
            parts = raw.split("=", 1)
            left = parts[0].strip()
            right = parts[1].strip()
            # If left is like 'f(x)', extract 'f' or 'y'
            if "(" in left and left.endswith(")"):
                left = left.split("(", 1)[0].strip()
            if left.isidentifier():
                output_var = left
            expr_str = right

        is_valid, msg, names = cls.validate_expression(expr_str)
        # Exclude constants and functions from variables
        var_symbols = {n for n in names if n not in cls.ALLOWED_CONSTANTS and n not in cls.ALLOWED_FUNCTIONS}
        return output_var, expr_str, var_symbols, is_valid, msg

    @classmethod
    def validate_expression(cls, expr_str):
        """
        Validates an expression using AST.
        Returns (is_valid: bool, error_message: str, extracted_names: set[str]).
        """
        if not expr_str or not expr_str.strip():
            return False, "Expression cannot be empty.", set()

        try:
            tree = ast.parse(expr_str.strip(), mode="eval")
        except SyntaxError as e:
            return False, f"Syntax error in expression: {e.msg} at position {e.offset}", set()
        except Exception as e:
            return False, f"Invalid expression: {str(e)}", set()

        names = set()
        disallowed_error = None

        class Validator(ast.NodeVisitor):
            def generic_visit(self, node):
                nonlocal disallowed_error
                if disallowed_error:
                    return

                # Check allowed node types
                allowed_types = (
                    ast.Expression,
                    ast.BinOp,
                    ast.UnaryOp,
                    ast.Constant,
                    ast.Name,
                    ast.Call,
                    ast.Load,
                    # Operators
                    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                    ast.UAdd, ast.USub
                )

                if not isinstance(node, allowed_types):
                    disallowed_error = (
                        f"Security violation: Disallowed Python syntax construct '{type(node).__name__}'. "
                        "Only mathematical operators and functions are permitted."
                    )
                    return

                if isinstance(node, ast.Name):
                    names.add(node.id)

                elif isinstance(node, ast.Call):
                    if not isinstance(node.func, ast.Name):
                        disallowed_error = "Security violation: Dynamic or attribute function calls are forbidden."
                        return
                    func_name = node.func.id
                    if func_name not in MathExpressionEngine.ALLOWED_FUNCTIONS:
                        disallowed_error = (
                            f"Disallowed or unknown function '{func_name}'. "
                            f"Permitted functions: {', '.join(sorted(MathExpressionEngine.ALLOWED_FUNCTIONS.keys()))}"
                        )
                        return

                super().generic_visit(node)

        v = Validator()
        v.visit(tree)

        if disallowed_error:
            return False, disallowed_error, set()

        return True, "Valid mathematical expression.", names

    @classmethod
    def evaluate(cls, expr_str, context=None):
        """
        Safely evaluates an expression AST with the provided variable dictionary.
        Returns float result.
        Raises ValueError or ZeroDivisionError with understandable messages.
        """
        if context is None:
            context = {}

        # Merge with constants
        ctx = dict(cls.ALLOWED_CONSTANTS)
        ctx.update(context)

        # Parse AST in eval mode
        try:
            tree = ast.parse(expr_str.strip(), mode="eval")
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expr_str}': {str(e)}")

        return cls._eval_node(tree.body, ctx)

    @classmethod
    def _eval_node(cls, node, ctx):
        """Recursive AST evaluator adhering strictly to allowlisted operations."""
        # 1. Constants (Numbers)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported literal type '{type(node.value).__name__}'. Only numbers are permitted.")

        # 2. Identifiers / Variables
        if isinstance(node, ast.Name):
            name = node.id
            if name in ctx:
                return float(ctx[name])
            raise ValueError(f"Undefined variable or symbol: '{name}'. Please configure its value.")

        # 3. Unary operations (+, -)
        if isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand, ctx)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        # 4. Binary operations (+, -, *, /, //, %, **)
        if isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left, ctx)
            right = cls._eval_node(node.right, ctx)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("Division by zero encountered in expression.")
                return left / right
            elif isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise ZeroDivisionError("Floor division by zero encountered in expression.")
                return left // right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ZeroDivisionError("Modulo by zero encountered in expression.")
                return left % right
            elif isinstance(node.op, ast.Pow):
                # Guard against extreme powers causing CPU hang
                if abs(left) > 1e10 and right > 10:
                    raise OverflowError("Exponentiation base and exponent too large.")
                try:
                    res = left ** right
                    if isinstance(res, complex):
                        raise ValueError(f"Complex result ({res}) from {left} ** {right}. Domain requires real numbers.")
                    return float(res)
                except OverflowError:
                    raise OverflowError(f"Numerical overflow during power calculation: {left} ** {right}")
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")

        # 5. Allowlisted Function Calls
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Disallowed function call syntax.")
            func_name = node.func.id
            if func_name not in cls.ALLOWED_FUNCTIONS:
                raise ValueError(f"Disallowed or unknown function '{func_name}'.")

            func = cls.ALLOWED_FUNCTIONS[func_name]
            args = [cls._eval_node(a, ctx) for a in node.args]

            # Domain checking for specific math functions
            if func_name == "sqrt":
                if args[0] < 0:
                    raise ValueError(f"Mathematical domain error: cannot compute sqrt of negative value ({args[0]}).")
            elif func_name in ("log", "log10", "log2"):
                if args[0] <= 0:
                    raise ValueError(f"Mathematical domain error: logarithm undefined for non-positive values ({args[0]}).")
            elif func_name in ("asin", "acos"):
                if args[0] < -1.0 or args[0] > 1.0:
                    raise ValueError(f"Mathematical domain error: {func_name} argument must be in [-1, 1], got {args[0]}.")

            try:
                res = func(*args)
                return float(res)
            except (ValueError, ZeroDivisionError) as e:
                raise e
            except OverflowError:
                raise OverflowError(f"Numerical overflow in function {func_name}({', '.join(map(str, args))}).")
            except Exception as e:
                raise ValueError(f"Error evaluating {func_name}: {str(e)}")

        raise ValueError(f"Disallowed AST construct '{type(node).__name__}'.")


# =============================================================================
# 2. EXPERIMENT EXECUTION ENGINE & STATISTICAL ANALYSIS
# =============================================================================

class ExperimentExecutionEngine:
    """
    Executes an experiment model configuration with input data and parameter snapshots.
    Produces structured results, calculates descriptive statistics, and records
    immutable run records without overwriting history.
    """

    @classmethod
    def calculate_statistics(cls, values):
        """Computes count, min, max, mean, median, stdev, variance, range."""
        if not values:
            return {
                "count": 0, "min": 0.0, "max": 0.0, "mean": 0.0,
                "median": 0.0, "stdev": 0.0, "variance": 0.0, "range": 0.0
            }

        valid_vals = [float(v) for v in values if isinstance(v, (int, float)) and not math.isnan(v)]
        if not valid_vals:
            return {
                "count": 0, "min": 0.0, "max": 0.0, "mean": 0.0,
                "median": 0.0, "stdev": 0.0, "variance": 0.0, "range": 0.0
            }

        n = len(valid_vals)
        v_min = min(valid_vals)
        v_max = max(valid_vals)
        v_mean = statistics.mean(valid_vals)
        v_median = statistics.median(valid_vals)
        v_range = v_max - v_min
        v_var = statistics.variance(valid_vals) if n > 1 else 0.0
        v_stdev = statistics.stdev(valid_vals) if n > 1 else 0.0

        return {
            "count": n,
            "min": round(v_min, 4),
            "max": round(v_max, 4),
            "mean": round(v_mean, 4),
            "median": round(v_median, 4),
            "stdev": round(v_stdev, 4),
            "variance": round(v_var, 4),
            "range": round(v_range, 4)
        }

    @classmethod
    def execute_experiment(cls, experiment, param_overrides=None, input_overrides=None):
        """
        Executes the experiment.
        Returns run record dict:
        {
            "run_id": str,
            "timestamp": str,
            "parameter_values": dict,
            "input_data_summary": dict,
            "calculated_outputs": list,
            "summary_stats": dict,
            "execution_status": "SUCCESS" or "ERROR",
            "error_info": str or None,
            "notes": ""
        }
        """
        run_id = f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract parameters
        active_params = {}
        for p in experiment.get("parameters", []):
            sym = p.get("symbol", "")
            def_val = p.get("default", 0.0)
            active_params[sym] = float(def_val)

        if param_overrides:
            for k, v in param_overrides.items():
                try:
                    active_params[k] = float(v)
                except (ValueError, TypeError):
                    pass

        # Validate parameter bounds
        for p in experiment.get("parameters", []):
            sym = p.get("symbol", "")
            val = active_params.get(sym, 0.0)
            p_min = p.get("min")
            p_max = p.get("max")
            if p_min is not None and val < float(p_min):
                return {
                    "run_id": run_id,
                    "timestamp": timestamp,
                    "parameter_values": active_params,
                    "input_data_summary": {"count": 0},
                    "calculated_outputs": [],
                    "summary_stats": cls.calculate_statistics([]),
                    "execution_status": "ERROR",
                    "error_info": f"Parameter '{p.get('name', sym)}' ({val}) is below minimum limit ({p_min}).",
                    "notes": ""
                }
            if p_max is not None and val > float(p_max):
                return {
                    "run_id": run_id,
                    "timestamp": timestamp,
                    "parameter_values": active_params,
                    "input_data_summary": {"count": 0},
                    "calculated_outputs": [],
                    "summary_stats": cls.calculate_statistics([]),
                    "execution_status": "ERROR",
                    "error_info": f"Parameter '{p.get('name', sym)}' ({val}) exceeds maximum limit ({p_max}).",
                    "notes": ""
                }

        # Equation and variables
        eq_str = experiment.get("equation", "")
        out_var, expr_str, var_symbols, is_valid, msg = MathExpressionEngine.extract_variables_and_equation(eq_str)

        if not is_valid:
            return {
                "run_id": run_id,
                "timestamp": timestamp,
                "parameter_values": active_params,
                "input_data_summary": {"count": 0},
                "calculated_outputs": [],
                "summary_stats": cls.calculate_statistics([]),
                "execution_status": "ERROR",
                "error_info": f"Equation validation failed: {msg}",
                "notes": ""
            }

        # Determine independent variable
        input_var = "x"
        for v in experiment.get("variables", []):
            if v.get("is_independent", True) and v.get("symbol") in var_symbols:
                input_var = v.get("symbol")
                break
        if input_var not in var_symbols and var_symbols:
            remaining = [s for s in var_symbols if s not in active_params]
            if remaining:
                input_var = remaining[0]

        # Input data series
        input_data = input_overrides if input_overrides is not None else experiment.get("input_data", [])
        if not input_data:
            # Fallback default range
            input_data = [float(i) for i in range(11)]

        exec_cfg = experiment.get("execution_config", {})
        exec_mode = exec_cfg.get("mode", "series")  # 'series' or 'iterative'

        calculated_outputs = []
        output_y_values = []
        eval_errors = []

        if exec_mode == "iterative":
            # Iterative simulation: y_{t+1} = f(y_t, t, params)
            init_val = float(exec_cfg.get("initial_condition", 1.0))
            iterations = int(exec_cfg.get("iterations", len(input_data) if input_data else 20))
            current_y = init_val
            calculated_outputs.append({"step": 0, "x": 0.0, "y": round(current_y, 4)})
            output_y_values.append(current_y)

            for step in range(1, iterations + 1):
                ctx = dict(active_params)
                ctx[input_var] = float(step)
                ctx[out_var] = current_y
                try:
                    next_y = MathExpressionEngine.evaluate(expr_str, ctx)
                    current_y = next_y
                    calculated_outputs.append({"step": step, "x": float(step), "y": round(next_y, 4)})
                    output_y_values.append(next_y)
                except Exception as e:
                    eval_errors.append(f"Step {step}: {str(e)}")
                    break
        else:
            # Series evaluation: compute y = f(x, params) for each x in input_data
            for idx, x_val in enumerate(input_data):
                try:
                    fx = float(x_val)
                except (ValueError, TypeError):
                    continue

                ctx = dict(active_params)
                ctx[input_var] = fx

                try:
                    y_res = MathExpressionEngine.evaluate(expr_str, ctx)
                    calculated_outputs.append({
                        "step": idx,
                        "x": fx,
                        "y": round(y_res, 4)
                    })
                    output_y_values.append(y_res)
                except Exception as e:
                    eval_errors.append(f"At {input_var}={fx}: {str(e)}")

        status = "SUCCESS" if output_y_values and not eval_errors else ("PARTIAL" if output_y_values else "ERROR")
        err_msg = "; ".join(eval_errors[:3]) if eval_errors else None

        stats = cls.calculate_statistics(output_y_values)

        return {
            "run_id": run_id,
            "timestamp": timestamp,
            "parameter_values": active_params,
            "input_data_summary": {
                "variable": input_var,
                "count": len(calculated_outputs),
                "min": min(d["x"] for d in calculated_outputs) if calculated_outputs else 0.0,
                "max": max(d["x"] for d in calculated_outputs) if calculated_outputs else 0.0,
            },
            "calculated_outputs": calculated_outputs,
            "summary_stats": stats,
            "execution_status": status,
            "error_info": err_msg,
            "notes": ""
        }


# =============================================================================
# 3. EDUCATIONAL EXPERIMENT TEMPLATES (8 TEMPLATES)
# =============================================================================

EXPERIMENT_TEMPLATES = [
    {
        "id": "tpl_linear",
        "title": "Linear Function & Parameter Sensitivity",
        "domain": "Mathematics",
        "objective": "Investigate how slope (m) and y-intercept (c) govern rate of change and baseline offset.",
        "description": "Standard first-degree polynomial model demonstrating linear proportionality, directional inclination, and translation along coordinate axes.",
        "theoretical_background": "Linear models represent direct proportional relationships. In analytical geometry, y = mx + c characterizes a straight line where m represents the derivative dy/dx and c is the point of intersection on the vertical axis.",
        "expected_outcome": "Higher absolute m values increase steepness; positive m yields monotonic growth while negative m causes monotonic descent.",
        "equation": "y = m * x + c",
        "variables": [
            {"symbol": "x", "name": "Independent Variable", "unit": "dimensionless", "is_independent": True, "description": "Horizontal domain coordinate."},
            {"symbol": "y", "name": "Dependent Variable", "unit": "dimensionless", "is_independent": False, "description": "Calculated vertical coordinate."}
        ],
        "parameters": [
            {"symbol": "m", "name": "Slope (Gradient)", "description": "Rate of change of y with respect to x", "default": 2.0, "min": -10.0, "max": 10.0, "step": 0.1, "unit": "ratio", "control": "slider"},
            {"symbol": "c", "name": "Y-Intercept", "description": "Vertical coordinate where line crosses vertical axis", "default": 5.0, "min": -20.0, "max": 20.0, "step": 0.5, "unit": "units", "control": "slider"}
        ],
        "input_data": [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10],
        "execution_config": {"mode": "series"},
        "tags": ["Linear", "Algebra", "Calculus", "Foundational"]
    },
    {
        "id": "tpl_exponential",
        "title": "Exponential Growth and Decay",
        "domain": "Biology & Physics",
        "objective": "Explore compound continuous expansion and radioactive nuclear half-life decay dynamics.",
        "description": "Examine exponential processes where rate of change is directly proportional to current population or quantity N0.",
        "theoretical_background": "Exponential growth occurs when instantaneous growth rate is proportional to value: dN/dt = rN, yielding N(t) = N0 * exp(r * t). Positive r indicates uninhibited growth; negative r denotes exponential decay.",
        "expected_outcome": "For r > 0, outputs grow rapidly at an accelerating rate; for r < 0, values asymptotically approach 0.",
        "equation": "y = N0 * exp(r * t)",
        "variables": [
            {"symbol": "t", "name": "Time Elapsed", "unit": "seconds", "is_independent": True, "description": "Continuous duration of observation."},
            {"symbol": "y", "name": "Quantity Remaining", "unit": "counts", "is_independent": False, "description": "Current quantity or population magnitude."}
        ],
        "parameters": [
            {"symbol": "N0", "name": "Initial Quantity", "description": "Starting population or mass at t=0", "default": 100.0, "min": 1.0, "max": 1000.0, "step": 10.0, "unit": "units", "control": "slider"},
            {"symbol": "r", "name": "Growth/Decay Rate", "description": "Continuous exponential rate constant", "default": 0.15, "min": -1.5, "max": 1.5, "step": 0.01, "unit": "1/s", "control": "slider"}
        ],
        "input_data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20],
        "execution_config": {"mode": "series"},
        "tags": ["Exponential", "Population", "Radioactivity", "Physics"]
    },
    {
        "id": "tpl_logistic",
        "title": "Logistic Population Growth",
        "domain": "Biology & Ecology",
        "objective": "Model resource-constrained population dynamics with ecological carrying capacity (K).",
        "description": "Verhulst S-shaped sigmoidal logistic curve modeling initial exponential growth followed by environmental resistance saturation.",
        "theoretical_background": "Unlike unconstrained exponential growth, biological environments exhibit finite limits. The differential form dN/dt = r*N*(1 - N/K) produces the logistic function where growth slows as N approaches carrying capacity K.",
        "expected_outcome": "S-shaped sigmoidal curve with inflection point at t = t0; asymptotic stabilization at K without infinite explosion.",
        "equation": "y = K / (1 + exp(-r * (t - t0)))",
        "variables": [
            {"symbol": "t", "name": "Time", "unit": "days", "is_independent": True, "description": "Time elapsed in ecosystem simulation."},
            {"symbol": "y", "name": "Population Size", "unit": "individuals", "is_independent": False, "description": "Number of organisms surviving."}
        ],
        "parameters": [
            {"symbol": "K", "name": "Carrying Capacity", "description": "Maximum sustainable biological population", "default": 1000.0, "min": 100.0, "max": 5000.0, "step": 50.0, "unit": "organisms", "control": "slider"},
            {"symbol": "r", "name": "Intrinsic Growth Rate", "description": "Maximum reproductive rate per capita", "default": 0.4, "min": 0.05, "max": 2.0, "step": 0.05, "unit": "1/day", "control": "slider"},
            {"symbol": "t0", "name": "Inflection Midpoint", "description": "Time point at which maximum growth rate is reached", "default": 12.0, "min": 0.0, "max": 30.0, "step": 1.0, "unit": "days", "control": "slider"}
        ],
        "input_data": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
        "execution_config": {"mode": "series"},
        "tags": ["Ecology", "Logistic", "CarryingCapacity", "Nonlinear"]
    },
    {
        "id": "tpl_sigmoid",
        "title": "Sigmoid Activation Function",
        "domain": "Artificial Intelligence",
        "objective": "Analyze nonlinear threshold squashing and vanishing gradient regions in artificial neurons.",
        "description": "Evaluates standard logistic sigmoid activation σ(z) mapping arbitrary real inputs onto normalized probability domain (0, 1).",
        "theoretical_background": "Artificial neural networks use nonlinear activation functions to approximate complex non-convex decision boundaries. Sigmoid σ(z) = 1 / (1 + exp(-k*z)) squashes inputs to (0, 1) with steepness parameter k.",
        "expected_outcome": "Output approaches 0 for large negative z, 1 for large positive z, and equals exactly 0.5 at z = 0.",
        "equation": "y = 1 / (1 + exp(-k * z))",
        "variables": [
            {"symbol": "z", "name": "Net Input", "unit": "dimensionless", "is_independent": True, "description": "Weighted affine sum w*x + b."},
            {"symbol": "y", "name": "Neuron Activation", "unit": "probability", "is_independent": False, "description": "Fired output probability."}
        ],
        "parameters": [
            {"symbol": "k", "name": "Steepness Scale", "description": "Slope scaling factor at inflection point", "default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "unit": "gain", "control": "slider"}
        ],
        "input_data": [-8, -6, -4, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 4, 6, 8],
        "execution_config": {"mode": "series"},
        "tags": ["MachineLearning", "NeuralNetworks", "Activation", "Sigmoid"]
    },
    {
        "id": "tpl_gradient_descent",
        "title": "Gradient Descent Step Simulation",
        "domain": "Optimization & Machine Learning",
        "objective": "Explore learning rate (alpha) stability, convergence, overshoot, and divergence when minimizing f(x) = x^2.",
        "description": "Simulates 1D gradient descent optimization step updating position along quadratic loss parabola with derivative 2*x.",
        "theoretical_background": "Gradient descent minimizes a loss function L(x) by stepping inversely proportional to the gradient: x_next = x - alpha * dL/dx. For L(x) = x^2, dL/dx = 2*x.",
        "expected_outcome": "If alpha < 0.5: smooth convergence; if 0.5 < alpha < 1.0: oscillating convergence; if alpha = 1.0: stable oscillation; if alpha > 1.0: catastrophic divergence.",
        "equation": "y = x - alpha * (2 * x)",
        "variables": [
            {"symbol": "x", "name": "Current Position", "unit": "parameter space", "is_independent": True, "description": "Current parameter coordinate."},
            {"symbol": "y", "name": "Next Position", "unit": "parameter space", "is_independent": False, "description": "Updated coordinate after gradient step."}
        ],
        "parameters": [
            {"symbol": "alpha", "name": "Learning Rate (α)", "description": "Optimization step size scaling factor", "default": 0.15, "min": 0.01, "max": 1.5, "step": 0.01, "unit": "rate", "control": "slider"}
        ],
        "input_data": [-10, -8, -5, -2, -1, 0, 1, 2, 5, 8, 10],
        "execution_config": {"mode": "series"},
        "tags": ["Optimization", "GradientDescent", "Convergence", "AI"]
    },
    {
        "id": "tpl_neural_sum",
        "title": "Simple Artificial Neuron Weighted Sum",
        "domain": "Artificial Intelligence",
        "objective": "Calculate forward-pass inference of a 2-feature perceptron with weights and bias.",
        "description": "Calculates affine linear combination followed by sigmoid activation for input features x1 and x2.",
        "theoretical_background": "A biological neuron computes dendritic summation before axon threshold firing. The artificial perceptron models this via y = 1 / (1 + exp(-(w1*x + b))).",
        "expected_outcome": "Positive weights cause activation to increase with feature magnitude; bias shifts activation midpoint horizontally.",
        "equation": "y = 1 / (1 + exp(-(w1 * x + b)))",
        "variables": [
            {"symbol": "x", "name": "Input Feature x", "unit": "signal", "is_independent": True, "description": "Incoming dendritic stimulation."},
            {"symbol": "y", "name": "Neuron Activation", "unit": "probability", "is_independent": False, "description": "Axon firing state."}
        ],
        "parameters": [
            {"symbol": "w1", "name": "Synaptic Weight w1", "description": "Excitatory or inhibitory connection strength", "default": 1.8, "min": -5.0, "max": 5.0, "step": 0.1, "unit": "gain", "control": "slider"},
            {"symbol": "b", "name": "Neuron Bias b", "description": "Threshold baseline activation sensitivity", "default": -0.5, "min": -5.0, "max": 5.0, "step": 0.1, "unit": "offset", "control": "slider"}
        ],
        "input_data": [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
        "execution_config": {"mode": "series"},
        "tags": ["Perceptron", "Neuron", "Weights", "AI"]
    },
    {
        "id": "tpl_confusion_matrix",
        "title": "Confusion Matrix Metric Exploration",
        "domain": "Data Science & Statistics",
        "objective": "Analyze harmonic mean behavior of F1-Score under trade-offs between Precision and Recall.",
        "description": "Calculates balanced F1-Score from precision (p) and varying recall (r) to highlight why harmonic mean penalizes extreme imbalances.",
        "theoretical_background": "Arithmetic mean of 0.99 and 0.01 is 0.50, but harmonic mean is 0.0198. The F1-Score: 2 * (p * r) / (p + r) ensures that a classifier must achieve both precision and recall to score high.",
        "expected_outcome": "F1-Score remains close to 0 if either precision or recall drops toward zero, illustrating harmonic mean sensitivity.",
        "equation": "y = 2 * (p * r) / (p + r)",
        "variables": [
            {"symbol": "r", "name": "Recall (Sensitivity)", "unit": "ratio [0,1]", "is_independent": True, "description": "Proportion of actual positives identified."},
            {"symbol": "y", "name": "F1-Score", "unit": "ratio [0,1]", "is_independent": False, "description": "Harmonic balanced metric."}
        ],
        "parameters": [
            {"symbol": "p", "name": "Precision", "description": "Positive predictive value", "default": 0.8, "min": 0.05, "max": 1.0, "step": 0.05, "unit": "ratio", "control": "slider"}
        ],
        "input_data": [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "execution_config": {"mode": "series"},
        "tags": ["Metrics", "F1Score", "Statistics", "MachineLearning"]
    },
    {
        "id": "tpl_image_threshold",
        "title": "Image Intensity Thresholding Demonstration",
        "domain": "Computer Vision & Physics",
        "objective": "Demonstrate smooth sigmoidal vs hard binary pixel intensity thresholding.",
        "description": "Continuous soft-thresholding function mapping grayscale pixel intensities (0-255) to segmented binary states.",
        "theoretical_background": "Thresholding segments foreground from background. Standard hard thresholding produces binary step functions; parameterized soft sigmoid thresholding y = 255 / (1 + exp(-k * (x - T))) allows differentiable segmentation.",
        "expected_outcome": "Pixels below T stay near 0; pixels above T transition toward 255. High k approximates sharp step function.",
        "equation": "y = 255 / (1 + exp(-k * (x - T)))",
        "variables": [
            {"symbol": "x", "name": "Input Pixel Intensity", "unit": "grayscale [0-255]", "is_independent": True, "description": "Raw grayscale value."},
            {"symbol": "y", "name": "Thresholded Output", "unit": "intensity [0-255]", "is_independent": False, "description": "Segmented output pixel value."}
        ],
        "parameters": [
            {"symbol": "T", "name": "Cutoff Threshold (T)", "description": "Intensity centerpoint for segmentation", "default": 128.0, "min": 10.0, "max": 240.0, "step": 1.0, "unit": "val", "control": "slider"},
            {"symbol": "k", "name": "Transition Steepness (k)", "description": "Transition sharpness from 0 to 255", "default": 0.08, "min": 0.01, "max": 0.5, "step": 0.01, "unit": "slope", "control": "slider"}
        ],
        "input_data": [0, 20, 40, 60, 80, 100, 120, 128, 140, 160, 180, 200, 220, 240, 255],
        "execution_config": {"mode": "series"},
        "tags": ["ComputerVision", "Thresholding", "SignalProcessing"]
    }
]


def get_template_dict(template_id):
    """Finds and returns a fresh copy of an experiment template."""
    import copy
    for t in EXPERIMENT_TEMPLATES:
        if t["id"] == template_id:
            return copy.deepcopy(t)
    return copy.deepcopy(EXPERIMENT_TEMPLATES[0])


# =============================================================================
# 4. TKINTER CANVAS PLOTTING ENGINE (LINE, SCATTER, HISTOGRAM, OVERLAYS)
# =============================================================================

class ExperimentCanvasPlotter:
    """
    Renders high-contrast, beautiful scientific graphs on a standard Tkinter Canvas.
    Supports Line plots, Scatter plots, Histograms, and Multi-Run Overlay comparisons.
    """

    PALETTE = [
        Theme.CYAN, Theme.EMERALD, Theme.AMBER, Theme.ROSE, Theme.PURPLE, Theme.BLUE
    ]

    @classmethod
    def plot_line_or_scatter(cls, canvas, x_vals, y_vals, x_label="x", y_label="y",
                             title="", color=Theme.CYAN, is_scatter=False):
        """Plots a single series on canvas as line or scatter."""
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = 600, 320

        # Background
        canvas.create_rectangle(0, 0, w, h, fill=Theme.BG_CARD, outline="")

        if not x_vals or not y_vals or len(x_vals) != len(y_vals):
            canvas.create_text(w / 2, h / 2, text="No numerical data available to plot.",
                               fill=Theme.TEXT_MUTED, font=("Segoe UI", 11))
            return

        pad_left = 65
        pad_right = 30
        pad_top = 45
        pad_bottom = 50

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)

        min_x, max_x = min(x_vals), max(x_vals)
        min_y, max_y = min(y_vals), max(y_vals)

        # Ensure non-zero range
        if min_x == max_x:
            min_x -= 1.0
            max_x += 1.0
        if min_y == max_y:
            min_y -= 1.0
            max_y += 1.0

        # Add 5% padding to y range
        y_span = max_y - min_y
        min_y -= y_span * 0.05
        max_y += y_span * 0.05

        def to_canvas(x, y):
            cx = pad_left + ((x - min_x) / (max_x - min_x)) * plot_w
            cy = pad_top + plot_h - ((y - min_y) / (max_y - min_y)) * plot_h
            return cx, cy

        # Draw Grid & Tick Marks
        num_ticks = 5
        for i in range(num_ticks + 1):
            # Horizontal grid lines (Y)
            frac = i / num_ticks
            y_tick = min_y + frac * (max_y - min_y)
            cy = pad_top + plot_h - frac * plot_h
            canvas.create_line(pad_left, cy, pad_left + plot_w, cy, fill="#1E293B", dash=(2, 4))
            canvas.create_text(pad_left - 8, cy, text=f"{y_tick:.2g}", fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="e")

            # Vertical grid lines (X)
            x_tick = min_x + frac * (max_x - min_x)
            cx = pad_left + frac * plot_w
            canvas.create_line(cx, pad_top, cx, pad_top + plot_h, fill="#1E293B", dash=(2, 4))
            canvas.create_text(cx, pad_top + plot_h + 14, text=f"{x_tick:.2g}", fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="center")

        # Zero lines if in range
        if min_y <= 0 <= max_y:
            _, zero_y = to_canvas(min_x, 0)
            canvas.create_line(pad_left, zero_y, pad_left + plot_w, zero_y, fill="#334155", width=1)

        # Plot Data
        points = [to_canvas(x, y) for x, y in zip(x_vals, y_vals)]

        if not is_scatter and len(points) > 1:
            # Draw line
            flat_coords = [coord for pt in points for coord in pt]
            canvas.create_line(*flat_coords, fill=color, width=2, smooth=True)

        # Draw markers
        r = 3 if not is_scatter else 4
        for cx, cy in points:
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline=Theme.BG_ROOT, width=1)

        # Axes Borders
        canvas.create_rectangle(pad_left, pad_top, pad_left + plot_w, pad_top + plot_h,
                                outline=Theme.BORDER_MUTED, width=1)

        # Labels & Title
        if title:
            canvas.create_text(pad_left + 10, 22, text=title, fill=Theme.TEXT_PRIMARY,
                               font=("Segoe UI", 11, "bold"), anchor="w")
        canvas.create_text(pad_left + plot_w / 2, h - 14, text=x_label, fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center")
        canvas.create_text(18, pad_top + plot_h / 2, text=y_label, fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center", angle=90)


    @classmethod
    def plot_histogram(cls, canvas, y_vals, num_bins=8, color=Theme.EMERALD, title="Output Distribution Histogram"):
        """Plots a histogram of output values."""
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = 600, 320

        canvas.create_rectangle(0, 0, w, h, fill=Theme.BG_CARD, outline="")

        if not y_vals:
            canvas.create_text(w / 2, h / 2, text="No output data available for histogram.",
                               fill=Theme.TEXT_MUTED, font=("Segoe UI", 11))
            return

        valid_vals = [float(v) for v in y_vals if not math.isnan(v)]
        if not valid_vals:
            return

        v_min, v_max = min(valid_vals), max(valid_vals)
        if v_min == v_max:
            v_min -= 1.0
            v_max += 1.0

        bin_width = (v_max - v_min) / num_bins
        bins = [0] * num_bins

        for val in valid_vals:
            idx = int((val - v_min) / bin_width)
            if idx >= num_bins:
                idx = num_bins - 1
            if idx < 0:
                idx = 0
            bins[idx] += 1

        pad_left = 55
        pad_right = 25
        pad_top = 45
        pad_bottom = 50

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)
        max_count = max(bins) if bins else 1
        if max_count == 0:
            max_count = 1

        for i in range(5):
            frac = i / 4.0
            c_tick = int(round(frac * max_count))
            cy = pad_top + plot_h - frac * plot_h
            canvas.create_line(pad_left, cy, pad_left + plot_w, cy, fill="#1E293B", dash=(2, 4))
            canvas.create_text(pad_left - 8, cy, text=str(c_tick), fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="e")

        bar_slot = plot_w / num_bins
        bar_w = max(4, bar_slot * 0.8)

        for i, count in enumerate(bins):
            bx = pad_left + i * bar_slot + (bar_slot - bar_w) / 2
            bar_height = (count / max_count) * plot_h
            by = pad_top + plot_h - bar_height

            canvas.create_rectangle(bx, by, bx + bar_w, pad_top + plot_h,
                                   fill=color, outline=Theme.BORDER_MUTED)

            bin_start = v_min + i * bin_width
            canvas.create_text(bx + bar_w / 2, pad_top + plot_h + 14,
                               text=f"{bin_start:.2g}", fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="center")

            if count > 0:
                canvas.create_text(bx + bar_w / 2, max(pad_top + 10, by - 8),
                                   text=str(count), fill=Theme.TEXT_PRIMARY,
                                   font=("Segoe UI", 8, "bold"))

        canvas.create_rectangle(pad_left, pad_top, pad_left + plot_w, pad_top + plot_h,
                                outline=Theme.BORDER_MUTED, width=1)

        if title:
            canvas.create_text(pad_left + 10, 22, text=title, fill=Theme.TEXT_PRIMARY,
                               font=("Segoe UI", 11, "bold"), anchor="w")
        canvas.create_text(pad_left + plot_w / 2, h - 14, text="Value Intervals", fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center")
        canvas.create_text(18, pad_top + plot_h / 2, text="Frequency", fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center", angle=90)

    @classmethod
    def plot_multi_run_comparison(cls, canvas, run_records, x_label="x", y_label="y", title="Multi-Run Comparison"):
        """Overlays multiple runs on canvas with distinct colors and an on-canvas legend."""
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = 600, 320

        canvas.create_rectangle(0, 0, w, h, fill=Theme.BG_CARD, outline="")

        if not run_records:
            canvas.create_text(w / 2, h / 2, text="Select at least one run from history to compare.",
                               fill=Theme.TEXT_MUTED, font=("Segoe UI", 11))
            return

        all_x, all_y = [], []
        for r in run_records:
            for pt in r.get("calculated_outputs", []):
                all_x.append(pt.get("x", 0.0))
                all_y.append(pt.get("y", 0.0))

        if not all_x or not all_y:
            canvas.create_text(w / 2, h / 2, text="Selected runs contain no numerical data.",
                               fill=Theme.TEXT_MUTED, font=("Segoe UI", 11))
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        if min_x == max_x:
            min_x -= 1.0
            max_x += 1.0
        if min_y == max_y:
            min_y -= 1.0
            max_y += 1.0

        y_span = max_y - min_y
        min_y -= y_span * 0.05
        max_y += y_span * 0.05

        pad_left = 65
        pad_right = 160
        pad_top = 45
        pad_bottom = 50

        plot_w = max(50, w - pad_left - pad_right)
        plot_h = max(50, h - pad_top - pad_bottom)

        def to_canvas(x, y):
            cx = pad_left + ((x - min_x) / (max_x - min_x)) * plot_w
            cy = pad_top + plot_h - ((y - min_y) / (max_y - min_y)) * plot_h
            return cx, cy

        for i in range(5):
            frac = i / 4.0
            cy = pad_top + plot_h - frac * plot_h
            y_tick = min_y + frac * (max_y - min_y)
            canvas.create_line(pad_left, cy, pad_left + plot_w, cy, fill="#1E293B", dash=(2, 4))
            canvas.create_text(pad_left - 8, cy, text=f"{y_tick:.2g}", fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="e")

            cx = pad_left + frac * plot_w
            x_tick = min_x + frac * (max_x - min_x)
            canvas.create_line(cx, pad_top, cx, pad_top + plot_h, fill="#1E293B", dash=(2, 4))
            canvas.create_text(cx, pad_top + plot_h + 14, text=f"{x_tick:.2g}", fill=Theme.TEXT_MUTED,
                               font=("Segoe UI", 8), anchor="center")

        legend_y = pad_top + 10
        for idx, r in enumerate(run_records):
            color = cls.PALETTE[idx % len(cls.PALETTE)]
            outputs = r.get("calculated_outputs", [])
            points = [to_canvas(pt["x"], pt["y"]) for pt in outputs if "x" in pt and "y" in pt]

            if len(points) > 1:
                flat_coords = [coord for pt in points for coord in pt]
                canvas.create_line(*flat_coords, fill=color, width=2, smooth=True)

            for cx, cy in points:
                canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline=Theme.BG_ROOT)

            run_lbl = r.get("run_id", f"Run #{idx+1}")[:14]
            params_str = ", ".join(f"{k}={v:g}" for k, v in list(r.get("parameter_values", {}).items())[:2])
            legend_x = pad_left + plot_w + 12

            canvas.create_line(legend_x, legend_y + 6, legend_x + 18, legend_y + 6, fill=color, width=3)
            canvas.create_oval(legend_x + 7, legend_y + 3, legend_x + 13, legend_y + 9, fill=color, outline="")
            canvas.create_text(legend_x + 24, legend_y + 6, text=run_lbl, fill=Theme.TEXT_PRIMARY,
                               font=("Segoe UI", 8, "bold"), anchor="w")
            if params_str:
                canvas.create_text(legend_x + 24, legend_y + 19, text=params_str, fill=Theme.TEXT_MUTED,
                                   font=("Segoe UI", 7), anchor="w")
            legend_y += 32

        canvas.create_rectangle(pad_left, pad_top, pad_left + plot_w, pad_top + plot_h,
                                outline=Theme.BORDER_MUTED, width=1)

        if title:
            canvas.create_text(pad_left + 10, 22, text=title, fill=Theme.TEXT_PRIMARY,
                               font=("Segoe UI", 11, "bold"), anchor="w")
        canvas.create_text(pad_left + plot_w / 2, h - 14, text=x_label, fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center")
        canvas.create_text(18, pad_top + plot_h / 2, text=y_label, fill=Theme.TEXT_SECONDARY,
                           font=("Segoe UI", 9, "bold"), anchor="center", angle=90)


# =============================================================================
# 5. EXPERIMENT CREATION WIZARD (5 STRUCTURED STEPS)
# =============================================================================

class ExperimentCreationWizard(tk.Frame):
    """
    Structured 5-step experiment creation and configuration interface:
    Step 1: General Information
    Step 2: Mathematical Model (Live AST Syntax Validator)
    Step 3: Parameter Configuration (Sliders, Numeric, Dropdowns)
    Step 4: Input Data (Manual Entry, Range Generator, CSV Upload via stdlib)
    Step 5: Execution Configuration (Series Evaluation vs Iterative Simulation)
    """

    def __init__(self, parent, app, experiment_id=None, on_save_callback=None, on_cancel_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.experiment_id = experiment_id
        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        self.current_step = 1
        self.step_frames = {}

        # Load existing or initialize draft experiment
        if experiment_id and hasattr(self.app, "state") and self.app.state:
            existing = self.app.state.get_custom_experiment(experiment_id)
            if existing:
                import copy
                self.exp_data = copy.deepcopy(existing)
            else:
                self.exp_data = self._init_default_draft()
        else:
            self.exp_data = self._init_default_draft()

        self._build_ui()

    def _init_default_draft(self):
        return {
            "id": f"exp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}",
            "title": "New Research Experiment",
            "domain": "Physics",
            "objective": "Investigate the relationship between independent variables and system response.",
            "description": "Formulate a mathematical model, configure test parameters, and examine outputs.",
            "theoretical_background": "Scientific hypotheses require mathematical formulation and empirical validation under controlled parameters.",
            "expected_outcome": "Observed outputs will conform to the parameterized mathematical function.",
            "tags": ["Simulation", "Custom"],
            "equation": "y = m * x + c",
            "variables": [
                {"symbol": "x", "name": "Independent Variable", "unit": "units", "is_independent": True, "description": "Independent input coordinate."},
                {"symbol": "y", "name": "Dependent Variable", "unit": "units", "is_independent": False, "description": "Calculated output coordinate."}
            ],
            "parameters": [
                {"symbol": "m", "name": "Slope", "description": "Rate of change", "default": 2.0, "min": -10.0, "max": 10.0, "step": 0.1, "unit": "ratio", "control": "slider"},
                {"symbol": "c", "name": "Intercept", "description": "Vertical baseline shift", "default": 1.0, "min": -20.0, "max": 20.0, "step": 0.5, "unit": "units", "control": "slider"}
            ],
            "input_data": [float(i) for i in range(11)],
            "execution_config": {"mode": "series", "iterations": 20, "initial_condition": 1.0},
            "status": "Draft",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modified_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "documentation": {
                "research_question": "How does the independent variable influence system output across varying parameter conditions?",
                "objective": "Investigate the relationship between independent variables and system response.",
                "theoretical_background": "Scientific hypotheses require mathematical formulation and empirical validation under controlled parameters.",
                "hypothesis": "Increasing the primary parameter will produce a proportional change in the calculated output series.",
                "methodology": "Define mathematical model, generate standardized input domain series, and calculate response via AST evaluation engine.",
                "parameters_conditions": "Controlled nominal parameters with varying input series.",
                "observations": "Initial formulation pending empirical execution.",
                "results": "No runs executed yet.",
                "interpretation": "Interpretation will be formulated upon analyzing calculated output series.",
                "unexpected_findings": "None identified at draft stage.",
                "limitations": "Model assumes ideal deterministic conditions with zero experimental noise.",
                "conclusion": "Hypothesis remains under active investigation.",
                "future_investigation": "Conduct sensitivity sweeps across parameter boundaries.",
                "hypothesis_status": "Under Investigation"
            },
            "runs": []
        }

    def _build_ui(self):
        # 1. Top Header Banner
        header = tk.Frame(self, bg=Theme.BG_HEADER, padx=24, pady=14,
                          highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        header.pack(fill="x")

        top_row = tk.Frame(header, bg=Theme.BG_HEADER)
        top_row.pack(fill="x")

        title_lbl = tk.Label(top_row, text="📐 EXPERIMENT BUILDER & CREATION WIZARD",
                             font=("Segoe UI", 12, "bold"), bg=Theme.BG_HEADER, fg=Theme.CYAN_BRIGHT)
        title_lbl.pack(side="left")

        # Load Template Button
        tpl_btn = ModernButton(
            top_row, text="Load Educational Template", icon="📂",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.AMBER, font=("Segoe UI", 8, "bold"),
            padx=10, pady=4, command=self._show_template_picker
        )
        tpl_btn.pack(side="right")

        # Step Tracker Indicator
        self.tracker_frame = tk.Frame(header, bg=Theme.BG_HEADER)
        self.tracker_frame.pack(fill="x", pady=(12, 0))
        self._build_step_tracker()

        # 2. Main Scrollable Container for Steps
        self.scroll = ScrollableFrame(self, bg=Theme.BG_ROOT)
        self.scroll.pack(fill="both", expand=True)
        self.content_box = self.scroll.scrollable_content

        # Build each step frame
        self.step_frames[1] = self._build_step1_general()
        self.step_frames[2] = self._build_step2_math_model()
        self.step_frames[3] = self._build_step3_parameters()
        self.step_frames[4] = self._build_step4_input_data()
        self.step_frames[5] = self._build_step5_execution()

        # 3. Bottom Navigation Bar
        nav_bar = tk.Frame(self, bg=Theme.BG_CARD, padx=24, pady=12,
                           highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        nav_bar.pack(fill="x", side="bottom")

        self.btn_cancel = ModernButton(
            nav_bar, text="Cancel", bg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_MUTED, font=("Segoe UI", 9),
            padx=12, pady=6, command=self._on_cancel
        )
        self.btn_cancel.pack(side="left")

        self.btn_save_run = ModernButton(
            nav_bar, text="Save & Execute Now", icon="🚀",
            bg_color=Theme.EMERALD, hover_color="#059669",
            text_color=Theme.TEXT_ON_ACCENT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=6, command=lambda: self._on_save(run_immediately=True)
        )
        self.btn_save_run.pack(side="right", padx=(8, 0))

        self.btn_save = ModernButton(
            nav_bar, text="Save Experiment", icon="💾",
            bg_color=Theme.BLUE, hover_color="#2563EB",
            text_color=Theme.TEXT_ON_ACCENT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=6, command=lambda: self._on_save(run_immediately=False)
        )
        self.btn_save.pack(side="right", padx=(8, 0))

        self.btn_next = ModernButton(
            nav_bar, text="Next Step →", icon="",
            bg_color=Theme.CYAN, hover_color="#0891B2",
            text_color=Theme.BG_ROOT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=6, command=self._next_step
        )
        self.btn_next.pack(side="right", padx=(8, 0))

        self.btn_back = ModernButton(
            nav_bar, text="← Back", bg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_SECONDARY, font=("Segoe UI", 9),
            padx=12, pady=6, command=self._prev_step
        )
        self.btn_back.pack(side="right", padx=(8, 0))

        self._show_step(1)

    def _build_step_tracker(self):
        for w in self.tracker_frame.winfo_children():
            w.destroy()

        steps_info = [
            (1, "General Info"),
            (2, "Math Model"),
            (3, "Parameters"),
            (4, "Input Data"),
            (5, "Execution Config")
        ]

        for num, label in steps_info:
            is_active = (num == self.current_step)
            is_done = (num < self.current_step)

            bg_c = Theme.CYAN if is_active else (Theme.EMERALD if is_done else Theme.BG_INPUT)
            fg_c = Theme.BG_ROOT if is_active else (Theme.TEXT_ON_ACCENT if is_done else Theme.TEXT_MUTED)

            step_chip = tk.Frame(self.tracker_frame, bg=Theme.BG_HEADER)
            step_chip.pack(side="left", padx=(0, 16))

            badge = tk.Label(step_chip, text=f" {num} " if not is_done else " ✓ ",
                             font=("Segoe UI", 8, "bold"), bg=bg_c, fg=fg_c, padx=4, pady=1)
            badge.pack(side="left")

            name_lbl = tk.Label(step_chip, text=label,
                                font=("Segoe UI", 8, "bold" if is_active else "normal"),
                                bg=Theme.BG_HEADER,
                                fg=Theme.CYAN_BRIGHT if is_active else (Theme.TEXT_PRIMARY if is_done else Theme.TEXT_MUTED))
            name_lbl.pack(side="left", padx=(6, 0))

    def _show_step(self, step_num):
        self.current_step = step_num
        self._build_step_tracker()

        for s_idx, f in self.step_frames.items():
            if s_idx == step_num:
                f.pack(fill="both", expand=True, padx=24, pady=16)
            else:
                f.pack_forget()

        # Update button states
        if step_num == 1:
            self.btn_back.label.config(text="← Back (Disabled)", fg=Theme.TEXT_MUTED)
            self.btn_back._disabled = True
        else:
            self.btn_back.label.config(text="← Back", fg=Theme.TEXT_SECONDARY)
            self.btn_back._disabled = False

        if step_num == 5:
            self.btn_next.label.config(text="Review Complete ✓", fg=Theme.TEXT_MUTED)
            self.btn_next._disabled = True
        else:
            self.btn_next.label.config(text="Next Step →", fg=Theme.BG_ROOT)
            self.btn_next._disabled = False

    def _next_step(self):
        if self._validate_current_step():
            if self.current_step < 5:
                self._show_step(self.current_step + 1)

    def _prev_step(self):
        if self.current_step > 1:
            self._show_step(self.current_step - 1)

    def _validate_current_step(self):
        """Validates fields for the active step before advancing."""
        if self.current_step == 1:
            title = self.step1_title.get().strip()
            if not title:
                messagebox.showwarning("Validation Error", "Experiment Title cannot be empty.")
                return False
            self.exp_data["title"] = title
            self.exp_data["domain"] = self.step1_domain.get().strip()
            self.exp_data["objective"] = self.step1_obj.get("1.0", "end-1c").strip()
            self.exp_data["description"] = self.step1_desc.get("1.0", "end-1c").strip()
            self.exp_data["theoretical_background"] = self.step1_theory.get("1.0", "end-1c").strip()
            self.exp_data["expected_outcome"] = self.step1_outcome.get("1.0", "end-1c").strip()
            tags_raw = self.step1_tags.get().strip()
            self.exp_data["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
            return True

        elif self.current_step == 2:
            eq = self.step2_equation.get().strip()
            if not eq:
                messagebox.showwarning("Validation Error", "Mathematical Equation cannot be empty.")
                return False
            out_var, expr, symbols, is_valid, msg = MathExpressionEngine.extract_variables_and_equation(eq)
            if not is_valid:
                messagebox.showerror("Equation Validation Error", f"Equation is invalid:\n\n{msg}")
                return False
            self.exp_data["equation"] = eq
            self.exp_data["assumptions"] = self.step2_assumptions.get("1.0", "end-1c").strip()
            self.exp_data["boundary_conditions"] = self.step2_boundaries.get("1.0", "end-1c").strip()
            # Synchronize detected symbols with parameter list
            self._sync_symbols_to_parameters(symbols)
            return True

        elif self.current_step == 3:
            params = self.exp_data.get("parameters", [])
            if not params:
                messagebox.showwarning("Parameter Configuration", "At least one parameter must be configured.")
                return False
            return True

        elif self.current_step == 4:
            data = self._parse_input_data_text()
            if not data:
                messagebox.showwarning("Input Data Validation", "Please enter at least two numerical values for input data series.")
                return False
            self.exp_data["input_data"] = data
            return True

        elif self.current_step == 5:
            self.exp_data["execution_config"] = {
                "mode": self.step5_mode.get(),
                "iterations": int(self.step5_iterations.get() or 20),
                "initial_condition": float(self.step5_init_cond.get() or 1.0)
            }
            return True
        return True

    def _sync_symbols_to_parameters(self, detected_symbols):
        """Auto-detects symbols from equation and adds them to parameters list if missing."""
        existing_symbols = {p["symbol"] for p in self.exp_data.get("parameters", [])}
        # Independent variable (e.g. x or t) shouldn't be a parameter
        indep_var = "x"
        for v in self.exp_data.get("variables", []):
            if v.get("is_independent", True):
                indep_var = v.get("symbol", "x")

        for sym in detected_symbols:
            if sym != indep_var and sym not in existing_symbols:
                self.exp_data.setdefault("parameters", []).append({
                    "symbol": sym,
                    "name": f"Parameter {sym.upper()}",
                    "description": f"Model coefficient {sym}",
                    "default": 1.0,
                    "min": -10.0,
                    "max": 10.0,
                    "step": 0.1,
                    "unit": "units",
                    "control": "slider"
                })
        self._refresh_params_table()

    # -------------------------------------------------------------------------
    # STEP 1: GENERAL INFORMATION
    # -------------------------------------------------------------------------
    def _build_step1_general(self):
        f = tk.Frame(self.content_box, bg=Theme.BG_ROOT)

        tk.Label(f, text="Step 1: General Experiment Information",
                 font=("Segoe UI", 14, "bold"), bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(f, text="Define title, scientific domain, objectives, and theoretical background.",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(f, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=16)
        box.pack(fill="x")

        # Row 1: Title & Domain
        r1 = tk.Frame(box, bg=Theme.BG_CARD)
        r1.pack(fill="x", pady=(0, 12))

        tk.Label(r1, text="Experiment Title *", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_title = tk.Entry(r1, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                    font=("Segoe UI", 10), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_title.insert(0, self.exp_data.get("title", ""))
        self.step1_title.pack(fill="x", pady=(4, 0))

        # Row 2: Subject Domain & Tags
        r2 = tk.Frame(box, bg=Theme.BG_CARD)
        r2.pack(fill="x", pady=(0, 12))
        r2.columnconfigure(0, weight=1)
        r2.columnconfigure(1, weight=1)

        c1 = tk.Frame(r2, bg=Theme.BG_CARD)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c1, text="Subject Domain", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_domain = ttk.Combobox(c1, values=[
            "Physics", "Biology", "Chemistry", "Computer Science",
            "Artificial Intelligence", "Mathematics", "Statistics", "Economics"
        ], state="readonly")
        self.step1_domain.set(self.exp_data.get("domain", "Physics"))
        self.step1_domain.pack(fill="x", pady=(4, 0))

        c2 = tk.Frame(r2, bg=Theme.BG_CARD)
        c2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c2, text="Tags (comma-separated)", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_tags = tk.Entry(c2, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                   font=("Segoe UI", 10), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_tags.insert(0, ", ".join(self.exp_data.get("tags", [])))
        self.step1_tags.pack(fill="x", pady=(4, 0))

        # Row 3: Objective / Research Question
        tk.Label(box, text="Research Question / Objective", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 0))
        self.step1_obj = tk.Text(box, height=2, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                 font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_obj.insert("1.0", self.exp_data.get("objective", ""))
        self.step1_obj.pack(fill="x", pady=(4, 12))

        # Row 4: Description
        tk.Label(box, text="Description", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_desc = tk.Text(box, height=3, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                  font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_desc.insert("1.0", self.exp_data.get("description", ""))
        self.step1_desc.pack(fill="x", pady=(4, 12))

        # Row 5: Theoretical Background
        tk.Label(box, text="Theoretical Background", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_theory = tk.Text(box, height=3, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                    font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_theory.insert("1.0", self.exp_data.get("theoretical_background", ""))
        self.step1_theory.pack(fill="x", pady=(4, 12))

        # Row 6: Expected Outcome
        tk.Label(box, text="Expected Outcome", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step1_outcome = tk.Text(box, height=2, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                     font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step1_outcome.insert("1.0", self.exp_data.get("expected_outcome", ""))
        self.step1_outcome.pack(fill="x", pady=(4, 0))

        return f

    # -------------------------------------------------------------------------
    # STEP 2: MATHEMATICAL MODEL
    # -------------------------------------------------------------------------
    def _build_step2_math_model(self):
        f = tk.Frame(self.content_box, bg=Theme.BG_ROOT)

        tk.Label(f, text="Step 2: Mathematical Model & Equation",
                 font=("Segoe UI", 14, "bold"), bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(f, text="Define mathematical model, variables, units, assumptions and boundary conditions.",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(f, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=16)
        box.pack(fill="x")

        # Equation Input
        eq_hdr = tk.Frame(box, bg=Theme.BG_CARD)
        eq_hdr.pack(fill="x")
        tk.Label(eq_hdr, text="Mathematical Equation *", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")
        tk.Label(eq_hdr, text=" (e.g. y = m*x + c, y = N0*exp(r*t), y = K/(1 + exp(-r*(t - t0))))",
                 font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=6)

        eq_row = tk.Frame(box, bg=Theme.BG_CARD)
        eq_row.pack(fill="x", pady=(6, 8))

        self.step2_equation = tk.Entry(eq_row, bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, insertbackground=Theme.CYAN,
                                       font=("Consolas", 12, "bold"), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step2_equation.insert(0, self.exp_data.get("equation", "y = m * x + c"))
        self.step2_equation.pack(side="left", fill="x", expand=True)

        val_btn = ModernButton(
            eq_row, text="Validate Syntax", icon="⚡",
            bg_color=Theme.BLUE, text_color=Theme.TEXT_ON_ACCENT,
            font=("Segoe UI", 8, "bold"), padx=10, pady=5,
            command=self._validate_equation_ui
        )
        val_btn.pack(side="right", padx=(8, 0))

        # Status badge for live syntax checking
        self.eq_status_lbl = tk.Label(box, text="✓ Equation ready for AST validation",
                                      font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.EMERALD,
                                      padx=10, pady=4, anchor="w")
        self.eq_status_lbl.pack(fill="x", pady=(0, 16))

        # Constants and functions notice
        math_docs = tk.Label(
            box,
            text="Supported functions: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, log, log10, log2, sqrt, exp, abs, floor, ceil. "
                 "Constants: pi (3.14159), e (2.71828), tau (6.28318). Arithmetic: +, -, *, /, //, %, **.",
            font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, wraplength=800, justify="left"
        )
        math_docs.pack(anchor="w", pady=(0, 16))

        # Assumptions and Boundary Conditions
        grid_f = tk.Frame(box, bg=Theme.BG_CARD)
        grid_f.pack(fill="x")
        grid_f.columnconfigure(0, weight=1)
        grid_f.columnconfigure(1, weight=1)

        b1 = tk.Frame(grid_f, bg=Theme.BG_CARD)
        b1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(b1, text="Theoretical Assumptions", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step2_assumptions = tk.Text(b1, height=3, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                         font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step2_assumptions.insert("1.0", self.exp_data.get("assumptions", "System operates in deterministic vacuum conditions."))
        self.step2_assumptions.pack(fill="x", pady=(4, 0))

        b2 = tk.Frame(grid_f, bg=Theme.BG_CARD)
        b2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(b2, text="Boundary Conditions & Domain Limits", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step2_boundaries = tk.Text(b2, height=3, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                        font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        self.step2_boundaries.insert("1.0", self.exp_data.get("boundary_conditions", "Inputs constrained to real finite domain."))
        self.step2_boundaries.pack(fill="x", pady=(4, 0))

        return f

    def _validate_equation_ui(self):
        eq = self.step2_equation.get().strip()
        out_var, expr, symbols, is_valid, msg = MathExpressionEngine.extract_variables_and_equation(eq)
        if is_valid:
            self.eq_status_lbl.config(
                text=f"✓ Valid AST Model: Output='{out_var}', Symbols={sorted(list(symbols))}. Expression='{expr}'",
                fg=Theme.EMERALD
            )
        else:
            self.eq_status_lbl.config(text=f"✗ {msg}", fg=Theme.ROSE)

    # -------------------------------------------------------------------------
    # STEP 3: PARAMETER CONFIGURATION
    # -------------------------------------------------------------------------
    def _build_step3_parameters(self):
        f = tk.Frame(self.content_box, bg=Theme.BG_ROOT)

        tk.Label(f, text="Step 3: Parameter Configuration",
                 font=("Segoe UI", 14, "bold"), bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(f, text="Configure parameter boundaries, step sizes, defaults, and GUI slider controls.",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(f, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=16)
        box.pack(fill="x")

        # Top Buttons
        btn_bar = tk.Frame(box, bg=Theme.BG_CARD)
        btn_bar.pack(fill="x", pady=(0, 12))

        tk.Label(btn_bar, text="Defined Parameters", font=("Segoe UI", 11, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        add_p_btn = ModernButton(
            btn_bar, text="Add Parameter", icon="➕",
            bg_color=Theme.BLUE, text_color=Theme.TEXT_ON_ACCENT,
            font=("Segoe UI", 8, "bold"), padx=10, pady=4,
            command=self._show_add_param_dialog
        )
        add_p_btn.pack(side="right")

        # Container for parameter cards
        self.params_container = tk.Frame(box, bg=Theme.BG_CARD)
        self.params_container.pack(fill="x")

        self._refresh_params_table()
        return f

    def _refresh_params_table(self):
        for w in self.params_container.winfo_children():
            w.destroy()

        params = self.exp_data.get("parameters", [])
        if not params:
            tk.Label(self.params_container, text="No parameters configured yet. Click 'Add Parameter' above.",
                     font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(pady=12)
            return

        for idx, p in enumerate(params):
            p_card = tk.Frame(self.params_container, bg=Theme.BG_INPUT,
                              highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=12, pady=10)
            p_card.pack(fill="x", pady=(0, 8))

            top = tk.Frame(p_card, bg=Theme.BG_INPUT)
            top.pack(fill="x")

            sym_badge = tk.Label(top, text=f" {p.get('symbol', '?')} ", font=("Consolas", 10, "bold"),
                                 bg=Theme.BG_CARD, fg=Theme.CYAN_BRIGHT, padx=6, pady=2)
            sym_badge.pack(side="left")

            name_lbl = tk.Label(top, text=f"{p.get('name', 'Param')} ({p.get('unit', 'units')})",
                                font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
            name_lbl.pack(side="left", padx=8)

            del_btn = tk.Label(top, text="🗑 Remove", font=("Segoe UI", 8),
                               bg=Theme.BG_INPUT, fg=Theme.ROSE, cursor="hand2")
            del_btn.pack(side="right")
            del_btn.bind("<Button-1>", lambda _, i=idx: self._remove_param(i))

            # Details
            desc_lbl = tk.Label(p_card, text=p.get("description", ""), font=("Segoe UI", 8),
                                bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, anchor="w")
            desc_lbl.pack(fill="x", pady=(4, 6))

            spec_text = (f"Default: {p.get('default')}  |  Min: {p.get('min')}  |  Max: {p.get('max')}  |  "
                         f"Step: {p.get('step', 0.1)}  |  Control: {p.get('control', 'slider').title()}")
            tk.Label(p_card, text=spec_text, font=("Consolas", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack(anchor="w")

    def _remove_param(self, index):
        params = self.exp_data.get("parameters", [])
        if 0 <= index < len(params):
            del params[index]
            self._refresh_params_table()

    def _show_add_param_dialog(self):
        diag = tk.Toplevel(self)
        diag.title("Add Parameter")
        diag.geometry("420x360")
        diag.configure(bg=Theme.BG_ROOT)
        diag.transient(self)
        diag.grab_set()

        f = tk.Frame(diag, bg=Theme.BG_CARD, padx=18, pady=18)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        fields = {}
        for lbl_text, key, def_val in [
            ("Symbol (e.g. m, k, r)", "symbol", "m"),
            ("Parameter Name", "name", "Slope"),
            ("Description", "desc", "Rate of change parameter"),
            ("Default Value", "default", "2.0"),
            ("Minimum Value", "min", "-10.0"),
            ("Maximum Value", "max", "10.0"),
            ("Step Size", "step", "0.1"),
            ("Unit", "unit", "ratio")
        ]:
            row = tk.Frame(f, bg=Theme.BG_CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl_text, font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, width=18, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                         font=("Segoe UI", 9), highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            e.insert(0, def_val)
            e.pack(side="right", fill="x", expand=True)
            fields[key] = e

        def _save():
            sym = fields["symbol"].get().strip()
            if not sym or not sym.isidentifier():
                messagebox.showerror("Error", "Symbol must be a valid identifier (e.g. m, k, r, alpha).")
                return
            try:
                d = float(fields["default"].get().strip())
                mi = float(fields["min"].get().strip())
                ma = float(fields["max"].get().strip())
                st = float(fields["step"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Default, Min, Max, and Step must be valid numbers.")
                return

            if mi >= ma:
                messagebox.showerror("Error", "Minimum value must be strictly less than Maximum value.")
                return
            if not (mi <= d <= ma):
                messagebox.showerror("Error", f"Default value ({d}) must be between Min ({mi}) and Max ({ma}).")
                return

            self.exp_data.setdefault("parameters", []).append({
                "symbol": sym,
                "name": fields["name"].get().strip() or sym,
                "description": fields["desc"].get().strip(),
                "default": d,
                "min": mi,
                "max": ma,
                "step": st,
                "unit": fields["unit"].get().strip() or "units",
                "control": "slider"
            })
            diag.destroy()
            self._refresh_params_table()

        btn_row = tk.Frame(f, bg=Theme.BG_CARD)
        btn_row.pack(fill="x", pady=(14, 0))
        ModernButton(btn_row, text="Add Parameter", bg_color=Theme.BLUE, command=_save).pack(side="right")
        ModernButton(btn_row, text="Cancel", bg_color=Theme.BG_INPUT, command=diag.destroy).pack(side="right", padx=6)

    # -------------------------------------------------------------------------
    # STEP 4: INPUT DATA
    # -------------------------------------------------------------------------
    def _build_step4_input_data(self):
        f = tk.Frame(self.content_box, bg=Theme.BG_ROOT)

        tk.Label(f, text="Step 4: Input Data Specification",
                 font=("Segoe UI", 14, "bold"), bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(f, text="Enter manual numerical inputs, upload a CSV dataset, or generate range intervals.",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(f, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=16)
        box.pack(fill="x")

        # Action helpers
        top_bar = tk.Frame(box, bg=Theme.BG_CARD)
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Independent Variable Series (x)",
                 font=("Segoe UI", 10, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        csv_btn = ModernButton(
            top_bar, text="Upload CSV", icon="📂",
            bg_color=Theme.PURPLE, text_color=Theme.TEXT_ON_ACCENT,
            font=("Segoe UI", 8, "bold"), padx=10, pady=4,
            command=self._upload_csv_input
        )
        csv_btn.pack(side="right")

        gen_btn = ModernButton(
            top_bar, text="Generate Range", icon="⚡",
            bg_color=Theme.BLUE, text_color=Theme.TEXT_ON_ACCENT,
            font=("Segoe UI", 8, "bold"), padx=10, pady=4,
            command=self._show_range_generator_dialog
        )
        gen_btn.pack(side="right", padx=(0, 8))

        # Text input area
        self.step4_data_text = tk.Text(box, height=6, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                       insertbackground=Theme.CYAN, font=("Consolas", 10),
                                       highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        init_data_str = ", ".join(f"{v:g}" for v in self.exp_data.get("input_data", []))
        self.step4_data_text.insert("1.0", init_data_str)
        self.step4_data_text.pack(fill="x", pady=(0, 8))
        self.step4_data_text.bind("<KeyRelease>", lambda _: self._update_data_preview_stats())

        # Dataset Preview Info
        self.step4_stats_lbl = tk.Label(box, text="Preview: 11 numerical points loaded.",
                                        font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                                        padx=10, pady=6, anchor="w")
        self.step4_stats_lbl.pack(fill="x")

        self._update_data_preview_stats()
        return f

    def _parse_input_data_text(self):
        raw = self.step4_data_text.get("1.0", "end-1c").strip()
        if not raw:
            return []
        tokens = raw.replace(",", " ").replace(";", " ").split()
        nums = []
        for t in tokens:
            try:
                nums.append(float(t))
            except ValueError:
                pass
        return nums

    def _update_data_preview_stats(self):
        data = self._parse_input_data_text()
        if data:
            self.step4_stats_lbl.config(
                text=f"Preview: {len(data)} valid points  |  Range: [{min(data):g}, {max(data):g}]  |  Mean: {statistics.mean(data):.2f}",
                fg=Theme.EMERALD
            )
        else:
            self.step4_stats_lbl.config(
                text="⚠️ No valid numerical input points detected. Enter comma or space-separated numbers.",
                fg=Theme.AMBER
            )

    def _show_range_generator_dialog(self):
        diag = tk.Toplevel(self)
        diag.title("Generate Input Range")
        diag.geometry("380x260")
        diag.configure(bg=Theme.BG_ROOT)
        diag.transient(self)
        diag.grab_set()

        f = tk.Frame(diag, bg=Theme.BG_CARD, padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=10, pady=10)

        fields = {}
        for lbl, key, def_val in [
            ("Start Value", "start", "-10"),
            ("Stop Value", "stop", "10"),
            ("Step Size", "step", "1.0")
        ]:
            row = tk.Frame(f, bg=Theme.BG_CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 9), highlightthickness=1)
            e.insert(0, def_val)
            e.pack(side="right", fill="x", expand=True)
            fields[key] = e

        def _generate():
            try:
                start = float(fields["start"].get().strip())
                stop = float(fields["stop"].get().strip())
                step = float(fields["step"].get().strip())
                if step <= 0:
                    messagebox.showerror("Error", "Step size must be strictly positive.")
                    return
                if start >= stop:
                    messagebox.showerror("Error", "Start must be less than Stop.")
                    return

                vals = []
                cur = start
                while cur <= stop + 1e-9:
                    vals.append(round(cur, 6))
                    cur += step

                self.step4_data_text.delete("1.0", "end")
                self.step4_data_text.insert("1.0", ", ".join(f"{v:g}" for v in vals))
                self._update_data_preview_stats()
                diag.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        btn_row = tk.Frame(f, bg=Theme.BG_CARD)
        btn_row.pack(fill="x", pady=(16, 0))
        ModernButton(btn_row, text="Generate Range", bg_color=Theme.BLUE, command=_generate).pack(side="right")
        ModernButton(btn_row, text="Cancel", bg_color=Theme.BG_INPUT, command=diag.destroy).pack(side="right", padx=6)

    def _upload_csv_input(self):
        """Uses Python standard library csv module to import numerical series."""
        filepath = filedialog.askopenfilename(
            title="Select CSV Dataset",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                messagebox.showwarning("Empty File", "Selected CSV file is empty.")
                return

            headers = rows[0]
            # Try to find numeric column
            col_data = []
            selected_col = 0
            # If multiple columns, look for first numeric column
            for col_idx in range(len(headers)):
                nums = []
                for row in rows[1:]:
                    if col_idx < len(row):
                        try:
                            nums.append(float(row[col_idx].strip()))
                        except ValueError:
                            pass
                if len(nums) > len(col_data):
                    col_data = nums
                    selected_col = col_idx

            if not col_data:
                # Try reading header as numbers
                for row in rows:
                    for item in row:
                        try:
                            col_data.append(float(item.strip()))
                        except ValueError:
                            pass

            if not col_data:
                messagebox.showerror("No Data", "Could not parse any numerical series from the CSV file.")
                return

            self.step4_data_text.delete("1.0", "end")
            self.step4_data_text.insert("1.0", ", ".join(f"{v:g}" for v in col_data[:200]))
            self._update_data_preview_stats()
            messagebox.showinfo("CSV Imported", f"Imported {len(col_data)} numerical values from '{headers[selected_col] if selected_col < len(headers) else 'Column 1'}'.")

        except Exception as e:
            messagebox.showerror("CSV Error", f"Failed to read CSV: {str(e)}")

    # -------------------------------------------------------------------------
    # STEP 5: EXECUTION CONFIGURATION
    # -------------------------------------------------------------------------
    def _build_step5_execution(self):
        f = tk.Frame(self.content_box, bg=Theme.BG_ROOT)

        tk.Label(f, text="Step 5: Execution Configuration",
                 font=("Segoe UI", 14, "bold"), bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(f, text="Configure simulation mode, initial conditions, iteration bounds, and execution telemetry.",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 16))

        box = tk.Frame(f, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=16)
        box.pack(fill="x")

        # Execution Mode
        tk.Label(box, text="Execution Mode", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step5_mode = ttk.Combobox(box, values=["series", "iterative"], state="readonly")
        self.step5_mode.set(self.exp_data.get("execution_config", {}).get("mode", "series"))
        self.step5_mode.pack(fill="x", pady=(4, 12))

        # Iterations & Initial Conditions
        r2 = tk.Frame(box, bg=Theme.BG_CARD)
        r2.pack(fill="x", pady=(0, 12))
        r2.columnconfigure(0, weight=1)
        r2.columnconfigure(1, weight=1)

        c1 = tk.Frame(r2, bg=Theme.BG_CARD)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c1, text="Number of Iterations (for Iterative Mode)", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step5_iterations = tk.Entry(c1, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 9), highlightthickness=1)
        self.step5_iterations.insert(0, str(self.exp_data.get("execution_config", {}).get("iterations", 20)))
        self.step5_iterations.pack(fill="x", pady=(4, 0))

        c2 = tk.Frame(r2, bg=Theme.BG_CARD)
        c2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c2, text="Initial Condition y₀ (for Iterative Mode)", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        self.step5_init_cond = tk.Entry(c2, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 9), highlightthickness=1)
        self.step5_init_cond.insert(0, str(self.exp_data.get("execution_config", {}).get("initial_condition", 1.0)))
        self.step5_init_cond.pack(fill="x", pady=(4, 0))

        # Summary Checklist Card
        summary_card = tk.Frame(box, bg=Theme.BG_INPUT, padx=14, pady=12, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        summary_card.pack(fill="x", pady=(10, 0))
        tk.Label(summary_card, text="Ready to Save Experiment Configuration",
                 font=("Segoe UI", 10, "bold"), bg=Theme.BG_INPUT, fg=Theme.EMERALD).pack(anchor="w")
        tk.Label(summary_card,
                 text="Once saved, this experiment will appear under 'My Experiments'. You can run simulations, "
                      "adjust parameters interactively, view line and scatter plots, and document findings.",
                 font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, wraplength=750, justify="left").pack(anchor="w", pady=(4, 0))

        return f

    # -------------------------------------------------------------------------
    # TEMPLATE PICKER MODAL
    # -------------------------------------------------------------------------
    def _show_template_picker(self):
        diag = tk.Toplevel(self)
        diag.title("Choose Educational Experiment Template")
        diag.geometry("640x500")
        diag.configure(bg=Theme.BG_ROOT)
        diag.transient(self)
        diag.grab_set()

        hdr = tk.Frame(diag, bg=Theme.BG_HEADER, padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📂 Educational Experiment Templates", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_HEADER, fg=Theme.CYAN_BRIGHT).pack(anchor="w")
        tk.Label(hdr, text="Select a template to pre-populate all 5 wizard steps with a proven educational model.",
                 font=("Segoe UI", 8), bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED).pack(anchor="w")

        scroll = ScrollableFrame(diag, bg=Theme.BG_ROOT)
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        c = scroll.scrollable_content

        for tpl in EXPERIMENT_TEMPLATES:
            card = tk.Frame(c, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=14, pady=12)
            card.pack(fill="x", pady=(0, 10))

            top = tk.Frame(card, bg=Theme.BG_CARD)
            top.pack(fill="x")
            tk.Label(top, text=tpl["title"], font=("Segoe UI", 10, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")
            tk.Label(top, text=f" {tpl['domain']} ", font=("Segoe UI", 7, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN, padx=4, pady=1).pack(side="right")

            eq_lbl = tk.Label(card, text=f"Formula:  {tpl['equation']}", font=("Consolas", 9, "bold"),
                              bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, padx=8, pady=3, anchor="w")
            eq_lbl.pack(fill="x", pady=(6, 4))

            tk.Label(card, text=tpl["description"], font=("Segoe UI", 8),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=540, justify="left").pack(anchor="w", pady=(0, 8))

            load_btn = ModernButton(
                card, text="Load This Template", icon="✓",
                bg_color=Theme.BLUE, text_color=Theme.TEXT_ON_ACCENT,
                font=("Segoe UI", 8, "bold"), padx=10, pady=4,
                command=lambda t=tpl: self._apply_template(t, diag)
            )
            load_btn.pack(anchor="e")

    def _apply_template(self, tpl, dialog):
        import copy
        self.exp_data["title"] = tpl["title"]
        self.exp_data["domain"] = tpl["domain"]
        self.exp_data["objective"] = tpl["objective"]
        self.exp_data["description"] = tpl["description"]
        self.exp_data["theoretical_background"] = tpl["theoretical_background"]
        self.exp_data["expected_outcome"] = tpl["expected_outcome"]
        self.exp_data["equation"] = tpl["equation"]
        self.exp_data["variables"] = copy.deepcopy(tpl.get("variables", []))
        self.exp_data["parameters"] = copy.deepcopy(tpl.get("parameters", []))
        self.exp_data["input_data"] = copy.deepcopy(tpl.get("input_data", []))
        self.exp_data["execution_config"] = copy.deepcopy(tpl.get("execution_config", {"mode": "series"}))
        self.exp_data["tags"] = copy.deepcopy(tpl.get("tags", []))

        # Re-populate step widgets
        self.step1_title.delete(0, "end")
        self.step1_title.insert(0, tpl["title"])
        self.step1_domain.set(tpl["domain"])
        self.step1_tags.delete(0, "end")
        self.step1_tags.insert(0, ", ".join(tpl.get("tags", [])))
        self.step1_obj.delete("1.0", "end")
        self.step1_obj.insert("1.0", tpl["objective"])
        self.step1_desc.delete("1.0", "end")
        self.step1_desc.insert("1.0", tpl["description"])
        self.step1_theory.delete("1.0", "end")
        self.step1_theory.insert("1.0", tpl["theoretical_background"])
        self.step1_outcome.delete("1.0", "end")
        self.step1_outcome.insert("1.0", tpl["expected_outcome"])

        self.step2_equation.delete(0, "end")
        self.step2_equation.insert(0, tpl["equation"])
        self._validate_equation_ui()

        self._refresh_params_table()

        self.step4_data_text.delete("1.0", "end")
        self.step4_data_text.insert("1.0", ", ".join(f"{v:g}" for v in tpl.get("input_data", [])))
        self._update_data_preview_stats()

        self.step5_mode.set(tpl.get("execution_config", {}).get("mode", "series"))

        dialog.destroy()
        self._show_step(1)
        messagebox.showinfo("Template Loaded", f"Template '{tpl['title']}' loaded successfully into all 5 wizard steps.")

    # -------------------------------------------------------------------------
    # SAVE & CANCEL HANDLERS
    # -------------------------------------------------------------------------
    def _on_save(self, run_immediately=False):
        if not self._validate_current_step():
            return

        # Ensure all steps data saved
        self.exp_data["title"] = self.step1_title.get().strip() or "Untitled Experiment"
        self.exp_data["domain"] = self.step1_domain.get().strip() or "General Science"
        self.exp_data["objective"] = self.step1_obj.get("1.0", "end-1c").strip()
        self.exp_data["description"] = self.step1_desc.get("1.0", "end-1c").strip()
        self.exp_data["theoretical_background"] = self.step1_theory.get("1.0", "end-1c").strip()
        self.exp_data["expected_outcome"] = self.step1_outcome.get("1.0", "end-1c").strip()
        tags_raw = self.step1_tags.get().strip()
        self.exp_data["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
        self.exp_data["equation"] = self.step2_equation.get().strip()
        self.exp_data["assumptions"] = self.step2_assumptions.get("1.0", "end-1c").strip()
        self.exp_data["boundary_conditions"] = self.step2_boundaries.get("1.0", "end-1c").strip()
        self.exp_data["input_data"] = self._parse_input_data_text()
        self.exp_data["execution_config"] = {
            "mode": self.step5_mode.get(),
            "iterations": int(self.step5_iterations.get() or 20),
            "initial_condition": float(self.step5_init_cond.get() or 1.0)
        }
        self.exp_data["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to AppState
        if hasattr(self.app, "state") and self.app.state:
            exp_id = self.exp_data.get("id")
            existing = self.app.state.get_custom_experiment(exp_id)
            if existing:
                self.app.state.update_custom_experiment(exp_id, self.exp_data)
            else:
                self.app.state.add_custom_experiment(self.exp_data)

            self.app.state.active_custom_experiment_id = exp_id

        if self.on_save_callback:
            self.on_save_callback(self.exp_data.get("id"), run_immediately=run_immediately)

    def _on_cancel(self):
        if self.on_cancel_callback:
            self.on_cancel_callback()

# =============================================================================
# 6. MY EXPERIMENTS MANAGEMENT VIEW
# =============================================================================

class MyExperimentsView(tk.Frame):
    """
    Dedicated view for user-created experiments:
    - Search & filter by subject/domain
    - Sort by creation date, modification date, title, and recorded runs count
    - Responsive cards with equation preview, status badge, run count
    - Create, Open, Edit, Duplicate, Delete (with confirmation), History, Docs
    """
    def __init__(self, parent, app, on_create_callback=None, on_open_callback=None,
                 on_edit_callback=None, on_history_callback=None, on_docs_callback=None,
                 on_load_template_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.on_create_callback = on_create_callback
        self.on_open_callback = on_open_callback
        self.on_edit_callback = on_edit_callback
        self.on_history_callback = on_history_callback
        self.on_docs_callback = on_docs_callback
        self.on_load_template_callback = on_load_template_callback

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg=Theme.BG_HEADER, padx=24, pady=16,
                          highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        header.pack(fill="x")

        top_r = tk.Frame(header, bg=Theme.BG_HEADER)
        top_r.pack(fill="x")

        left_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        left_h.pack(side="left")

        tk.Label(left_h, text="🔬 MY EXPERIMENTS  •  USER RESEARCH WORKSPACE",
                 font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.EMERALD,
                 padx=8, pady=2).pack(anchor="w")

        tk.Label(left_h, text="Custom Experiment Directory",
                 font=("Segoe UI", 18, "bold"), bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(4, 2))

        tk.Label(left_h, text="Create, configure, execute, and analyze your own mathematical models.",
                 font=("Segoe UI", 9), bg=Theme.BG_HEADER, fg=Theme.TEXT_SECONDARY).pack(anchor="w")

        right_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        right_h.pack(side="right")

        new_btn = ModernButton(
            right_h, text="Create New Experiment", icon="➕",
            bg_color=Theme.BLUE, hover_color="#2563EB",
            text_color=Theme.TEXT_ON_ACCENT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=7, command=self._on_create
        )
        new_btn.pack(side="right")

        tpl_btn = ModernButton(
            right_h, text="From Template", icon="📂",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=7, command=self._on_template
        )
        tpl_btn.pack(side="right", padx=(0, 8))

        # 2. Filter & Search Bar
        filter_bar = tk.Frame(self, bg=Theme.BG_CARD, padx=24, pady=10,
                              highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        filter_bar.pack(fill="x")

        # Search input
        tk.Label(filter_bar, text="Search:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var, bg=Theme.BG_INPUT,
                                fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN,
                                font=("Segoe UI", 9), width=26,
                                highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        search_entry.pack(side="left", padx=(0, 16))

        # Domain Filter
        tk.Label(filter_bar, text="Subject:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        self.domain_var = tk.StringVar(value="All Subjects")
        domain_cb = ttk.Combobox(filter_bar, textvariable=self.domain_var, values=[
            "All Subjects", "Physics", "Biology", "Chemistry", "Computer Science",
            "Artificial Intelligence", "Mathematics", "Statistics", "Economics"
        ], state="readonly", width=18)
        domain_cb.pack(side="left", padx=(0, 16))
        domain_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh_list())

        # Sort Dropdown
        tk.Label(filter_bar, text="Sort by:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        self.sort_var = tk.StringVar(value="Newest First")
        sort_cb = ttk.Combobox(filter_bar, textvariable=self.sort_var, values=[
            "Newest First", "Oldest First", "Title (A-Z)", "Most Recorded Runs", "Recently Modified", "Subject"
        ], state="readonly", width=18)
        sort_cb.pack(side="left")
        sort_cb.bind("<<ComboboxSelected>>", lambda _: self.refresh_list())

        # Counts label on right
        self.count_lbl = tk.Label(filter_bar, text="Showing 0 experiments",
                                  font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.count_lbl.pack(side="right")

        # 3. Main Scrollable Container for Experiment Cards
        self.scroll = ScrollableFrame(self, bg=Theme.BG_ROOT)
        self.scroll.pack(fill="both", expand=True)
        self.cards_container = self.scroll.scrollable_content

        self.refresh_list()

    def refresh_list(self):
        for w in self.cards_container.winfo_children():
            w.destroy()

        experiments = []
        if hasattr(self.app, "state") and self.app.state:
            experiments = list(self.app.state.custom_experiments.values()) if isinstance(self.app.state.custom_experiments, dict) else list(self.app.state.custom_experiments)

        # Apply search filter
        query = self.search_var.get().strip().lower()
        if query:
            filtered = []
            for exp in experiments:
                corpus = f"{exp.get('title', '')} {exp.get('domain', '')} {exp.get('equation', '')} {exp.get('description', '')} {' '.join(exp.get('tags', []))}".lower()
                if query in corpus:
                    filtered.append(exp)
            experiments = filtered

        # Apply domain filter
        dom = self.domain_var.get()
        if dom != "All Subjects":
            experiments = [e for e in experiments if dom.lower() in e.get("domain", "").lower()]

        # Apply sorting
        sort_mode = self.sort_var.get()
        if sort_mode == "Newest First":
            experiments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_mode == "Oldest First":
            experiments.sort(key=lambda x: x.get("created_at", ""))
        elif sort_mode == "Title (A-Z)":
            experiments.sort(key=lambda x: x.get("title", "").lower())
        elif sort_mode == "Most Recorded Runs":
            experiments.sort(key=lambda x: len(x.get("runs", [])), reverse=True)
        elif sort_mode == "Recently Modified":
            experiments.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
        elif sort_mode == "Subject":
            experiments.sort(key=lambda x: x.get("domain", "").lower())

        self.count_lbl.config(text=f"Showing {len(experiments)} experiment{'s' if len(experiments) != 1 else ''}")

        if not experiments:
            empty_box = tk.Frame(self.cards_container, bg=Theme.BG_CARD, padx=30, pady=30,
                                 highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            empty_box.pack(fill="x", padx=32, pady=40)
            tk.Label(empty_box, text="🧪 No Experiments Found",
                     font=("Segoe UI", 13, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack()
            tk.Label(empty_box, text="No custom experiments match your search or filter criteria.\nCreate a new experiment or load one of CurioLab's 8 educational templates.",
                     font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, justify="center").pack(pady=8)
            ModernButton(empty_box, text="Create Experiment", icon="➕", bg_color=Theme.BLUE, command=self._on_create).pack(pady=4)
            return

        # Render Experiment Cards
        for exp in experiments:
            self._render_experiment_card(exp)

    def _render_experiment_card(self, exp):
        exp_id = exp.get("id")
        card = tk.Frame(self.cards_container, bg=Theme.BG_CARD, padx=18, pady=14,
                        highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        card.pack(fill="x", padx=32, pady=(0, 14))

        # Top row: Domain, Status, Title, Runs badge
        top_row = tk.Frame(card, bg=Theme.BG_CARD)
        top_row.pack(fill="x")

        dom_badge = tk.Label(top_row, text=f" {exp.get('domain', 'Science').upper()} ",
                             font=("Segoe UI", 7, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN, padx=6, pady=2)
        dom_badge.pack(side="left")

        status = exp.get("status", "Formulated")
        s_color = Theme.EMERALD if status == "Documented" else (Theme.CYAN if status == "Executed" else Theme.AMBER)
        stat_badge = tk.Label(top_row, text=f" {status.upper()} ",
                              font=("Segoe UI", 7, "bold"), bg=Theme.BG_INPUT, fg=s_color, padx=6, pady=2)
        stat_badge.pack(side="left", padx=8)

        runs_count = len(exp.get("runs", []))
        runs_badge = tk.Label(top_row, text=f"📊 {runs_count} Run{'s' if runs_count != 1 else ''} Recorded",
                              font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=8, pady=2)
        runs_badge.pack(side="right")

        # Title
        t_lbl = tk.Label(card, text=exp.get("title", "Untitled"), font=("Segoe UI", 13, "bold"),
                         bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
        t_lbl.pack(fill="x", pady=(6, 4))

        # Equation Preview Box
        eq_box = tk.Label(card, text=f"Model: {exp.get('equation', 'y = f(x)')}",
                          font=("Consolas", 10, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                          padx=10, pady=4, anchor="w")
        eq_box.pack(fill="x", pady=(0, 6))

        # Description
        desc = exp.get("description", "")
        if desc:
            d_lbl = tk.Label(card, text=desc, font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=850, justify="left", anchor="w")
            d_lbl.pack(fill="x", pady=(0, 8))

        # Tags and Timestamps row
        meta_row = tk.Frame(card, bg=Theme.BG_CARD)
        meta_row.pack(fill="x", pady=(0, 10))

        tags = exp.get("tags", [])
        if tags:
            tags_str = " • ".join(f"#{t}" for t in tags)
            tk.Label(meta_row, text=tags_str, font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left")

        time_str = f"Created: {exp.get('created_at', '')[:10]}  |  Modified: {exp.get('modified_at', '')[:10]}"
        tk.Label(meta_row, text=time_str, font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="right")

        # Action Buttons Row
        act_row = tk.Frame(card, bg=Theme.BG_CARD)
        act_row.pack(fill="x")

        # Open / Run Button
        open_btn = ModernButton(
            act_row, text="Run & Visualize", icon="▶",
            bg_color=Theme.CYAN, hover_color="#0891B2",
            text_color=Theme.BG_ROOT, font=("Segoe UI", 8, "bold"),
            padx=10, pady=4, command=lambda eid=exp_id: self._on_open(eid)
        )
        open_btn.pack(side="left", padx=(0, 6))

        # Edit Button
        edit_btn = ModernButton(
            act_row, text="Edit Wizard", icon="✏",
            bg_color=Theme.BG_INPUT, text_color=Theme.TEXT_PRIMARY,
            font=("Segoe UI", 8), padx=10, pady=4,
            command=lambda eid=exp_id: self._on_edit(eid)
        )
        edit_btn.pack(side="left", padx=(0, 6))

        # Duplicate Button
        dup_btn = ModernButton(
            act_row, text="Duplicate", icon="⎘",
            bg_color=Theme.BG_INPUT, text_color=Theme.TEXT_PRIMARY,
            font=("Segoe UI", 8), padx=10, pady=4,
            command=lambda eid=exp_id: self._on_duplicate(eid)
        )
        dup_btn.pack(side="left", padx=(0, 6))

        # History Button
        hist_btn = ModernButton(
            act_row, text="Run History", icon="📜",
            bg_color=Theme.BG_INPUT, text_color=Theme.TEXT_PRIMARY,
            font=("Segoe UI", 8), padx=10, pady=4,
            command=lambda eid=exp_id: self._on_history(eid)
        )
        hist_btn.pack(side="left", padx=(0, 6))

        # Documentation Button
        docs_btn = ModernButton(
            act_row, text="Research Docs", icon="📝",
            bg_color=Theme.BG_INPUT, text_color=Theme.TEXT_PRIMARY,
            font=("Segoe UI", 8), padx=10, pady=4,
            command=lambda eid=exp_id: self._on_docs(eid)
        )
        docs_btn.pack(side="left", padx=(0, 6))

        # Delete Button (Right aligned)
        del_btn = ModernButton(
            act_row, text="Delete", icon="🗑",
            bg_color=Theme.BG_INPUT, hover_color="#7F1D1D",
            text_color=Theme.ROSE, font=("Segoe UI", 8),
            padx=10, pady=4, command=lambda eid=exp_id: self._on_delete(eid)
        )
        del_btn.pack(side="right")

    def _on_create(self):
        if self.on_create_callback:
            self.on_create_callback()

    def _on_template(self):
        if self.on_load_template_callback:
            self.on_load_template_callback()
        elif self.on_create_callback:
            self.on_create_callback()

    def _on_open(self, exp_id):
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.active_custom_experiment_id = exp_id
        if self.on_open_callback:
            self.on_open_callback(exp_id)

    def _on_edit(self, exp_id):
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.active_custom_experiment_id = exp_id
        if self.on_edit_callback:
            self.on_edit_callback(exp_id)

    def _on_duplicate(self, exp_id):
        if hasattr(self.app, "state") and self.app.state:
            new_id = self.app.state.duplicate_custom_experiment(exp_id)
            if new_id:
                self.refresh_list()
                messagebox.showinfo("Duplicated", "Experiment successfully duplicated.")

    def _on_delete(self, exp_id):
        exp = None
        if hasattr(self.app, "state") and self.app.state:
            exp = self.app.state.get_custom_experiment(exp_id)
        title = exp.get("title", "this experiment") if exp else "this experiment"

        confirm = messagebox.askyesno(
            "Confirm Delete Experiment",
            f"Are you sure you want to permanently delete:\n\n'{title}'\n\nThis will also remove all recorded runs and documentation associated with it."
        )
        if confirm:
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.delete_custom_experiment(exp_id)
                self.refresh_list()

    def _on_history(self, exp_id):
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.active_custom_experiment_id = exp_id
        if self.on_history_callback:
            self.on_history_callback(exp_id)

    def _on_docs(self, exp_id):
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.active_custom_experiment_id = exp_id
        if self.on_docs_callback:
            self.on_docs_callback(exp_id)


# =============================================================================
# 7. EXPERIMENT RESULTS & LIVE SIMULATION VIEW
# =============================================================================

class ExperimentResultsView(tk.Frame):
    """
    Interactive results and simulation workspace:
    - Real-time parameter controls (sliders & numeric inputs)
    - Canvas graph visualizer with Line, Scatter, and Histogram plot modes
    - Summary statistics cards (Count, Mean, Median, Min, Max, Std Dev)
    - Numerical data output preview table
    - Save run record (without overwriting previous runs)
    - Export results to CSV
    - Transfer to Discovery Journal
    - Add qualitative observation notes
    """
    def __init__(self, parent, app, on_edit_callback=None, on_history_callback=None, on_docs_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.on_edit_callback = on_edit_callback
        self.on_history_callback = on_history_callback
        self.on_docs_callback = on_docs_callback

        self.plot_mode = "line"  # 'line', 'scatter', 'histogram'
        self.param_vars = {}
        self.last_run_result = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Header Banner
        self.header = tk.Frame(self, bg=Theme.BG_HEADER, padx=24, pady=12,
                               highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        self.header.pack(fill="x")

        top_r = tk.Frame(self.header, bg=Theme.BG_HEADER)
        top_r.pack(fill="x")

        left_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        left_h.pack(side="left")

        self.domain_badge = tk.Label(left_h, text="PHYSICS", font=("Segoe UI", 7, "bold"),
                                     bg=Theme.BG_INPUT, fg=Theme.CYAN, padx=6, pady=2)
        self.domain_badge.pack(anchor="w")

        self.title_lbl = tk.Label(left_h, text="Active Experiment Workspace",
                                  font=("Segoe UI", 16, "bold"), bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY)
        self.title_lbl.pack(anchor="w", pady=(2, 0))

        self.equation_lbl = tk.Label(left_h, text="Model: y = f(x)",
                                     font=("Consolas", 10, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                                     padx=8, pady=2)
        self.equation_lbl.pack(anchor="w", pady=(4, 0))

        right_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        right_h.pack(side="right")

        # Header action buttons
        ModernButton(right_h, text="Edit in Wizard", icon="✏", bg_color=Theme.BG_CARD,
                     font=("Segoe UI", 8), padx=10, pady=5, command=self._on_edit).pack(side="right", padx=(6, 0))
        ModernButton(right_h, text="Run History", icon="📜", bg_color=Theme.BG_CARD,
                     font=("Segoe UI", 8), padx=10, pady=5, command=self._on_history).pack(side="right", padx=(6, 0))
        ModernButton(right_h, text="Research Docs", icon="📝", bg_color=Theme.BG_CARD,
                     font=("Segoe UI", 8), padx=10, pady=5, command=self._on_docs).pack(side="right")

        # 2. Main Workspace Split (Left Controls vs Right Visualizer/Data)
        main_body = tk.Frame(self, bg=Theme.BG_ROOT)
        main_body.pack(fill="both", expand=True, padx=20, pady=12)
        main_body.columnconfigure(0, weight=1)  # Left controls
        main_body.columnconfigure(1, weight=2)  # Right visualizer

        # Left Column: Parameter controls & execution trigger
        self.left_col = tk.Frame(main_body, bg=Theme.BG_CARD, padx=16, pady=16,
                                 highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(self.left_col, text="⚙ Interactive Parameters", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(self.left_col, text="Adjust sliders or numeric entries to observe mathematical response.",
                 font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 12))

        # Scrollable area for parameter sliders
        self.param_scroll = ScrollableFrame(self.left_col, bg=Theme.BG_CARD)
        self.param_scroll.pack(fill="both", expand=True)
        self.param_controls_box = self.param_scroll.scrollable_content

        # Bottom Left: Execution Actions
        left_actions = tk.Frame(self.left_col, bg=Theme.BG_CARD)
        left_actions.pack(fill="x", pady=(12, 0))

        self.btn_run = ModernButton(
            left_actions, text="Recalculate / Run", icon="▶",
            bg_color=Theme.CYAN, hover_color="#0891B2",
            text_color=Theme.BG_ROOT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=8, command=self.execute_and_plot
        )
        self.btn_run.pack(fill="x", pady=(0, 6))

        self.btn_save_run = ModernButton(
            left_actions, text="Save as Run Record", icon="💾",
            bg_color=Theme.EMERALD, hover_color="#059669",
            text_color=Theme.TEXT_ON_ACCENT, font=("Segoe UI", 9, "bold"),
            padx=14, pady=6, command=self._save_run_record
        )
        self.btn_save_run.pack(fill="x")

        self.exec_status_lbl = tk.Label(self.left_col, text="Ready", font=("Segoe UI", 8),
                                        bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.exec_status_lbl.pack(anchor="w", pady=(6, 0))

        # Right Column: Visualization + Stats + Output Table
        self.right_col = tk.Frame(main_body, bg=Theme.BG_ROOT)
        self.right_col.grid(row=0, column=1, sticky="nsew")

        # Visualization Card
        viz_card = tk.Frame(self.right_col, bg=Theme.BG_CARD, padx=14, pady=12,
                            highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        viz_card.pack(fill="both", expand=True, pady=(0, 10))

        viz_top = tk.Frame(viz_card, bg=Theme.BG_CARD)
        viz_top.pack(fill="x", pady=(0, 8))

        tk.Label(viz_top, text="📈 Scientific Plot Visualizer", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        # Plot mode toggles
        self.plot_btn_frame = tk.Frame(viz_top, bg=Theme.BG_CARD)
        self.plot_btn_frame.pack(side="right")

        self.btn_line = tk.Label(self.plot_btn_frame, text=" Line Plot ", font=("Segoe UI", 8, "bold"),
                                 bg=Theme.CYAN, fg=Theme.BG_ROOT, padx=8, pady=3, cursor="hand2")
        self.btn_line.pack(side="left", padx=2)
        self.btn_line.bind("<Button-1>", lambda _: self._set_plot_mode("line"))

        self.btn_scatter = tk.Label(self.plot_btn_frame, text=" Scatter ", font=("Segoe UI", 8),
                                    bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=8, pady=3, cursor="hand2")
        self.btn_scatter.pack(side="left", padx=2)
        self.btn_scatter.bind("<Button-1>", lambda _: self._set_plot_mode("scatter"))

        self.btn_hist = tk.Label(self.plot_btn_frame, text=" Histogram ", font=("Segoe UI", 8),
                                 bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=8, pady=3, cursor="hand2")
        self.btn_hist.pack(side="left", padx=2)
        self.btn_hist.bind("<Button-1>", lambda _: self._set_plot_mode("histogram"))

        # Canvas for plotting
        self.plot_canvas = tk.Canvas(viz_card, bg=Theme.BG_CARD, highlightthickness=0, height=240)
        self.plot_canvas.pack(fill="both", expand=True)

        # Statistics Cards Row
        self.stats_row = tk.Frame(self.right_col, bg=Theme.BG_ROOT)
        self.stats_row.pack(fill="x", pady=(0, 10))
        for col_i in range(6):
            self.stats_row.columnconfigure(col_i, weight=1)

        self.stat_widgets = {}
        stat_names = [("count", "Data Points"), ("mean", "Mean μ"), ("median", "Median"),
                      ("min", "Minimum"), ("max", "Maximum"), ("stdev", "Std Dev σ")]
        for i, (key, label) in enumerate(stat_names):
            sc = tk.Frame(self.stats_row, bg=Theme.BG_CARD, padx=8, pady=6,
                          highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            sc.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 4, 0 if i == 5 else 4))
            tk.Label(sc, text=label, font=("Segoe UI", 7, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")
            val_lbl = tk.Label(sc, text="--", font=("Consolas", 10, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN_BRIGHT)
            val_lbl.pack(anchor="w")
            self.stat_widgets[key] = val_lbl

        # Bottom Data & Actions Bar
        bottom_bar = tk.Frame(self.right_col, bg=Theme.BG_CARD, padx=14, pady=10,
                              highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        bottom_bar.pack(fill="x")

        ModernButton(bottom_bar, text="Export CSV", icon="📥", bg_color=Theme.PURPLE,
                     font=("Segoe UI", 8, "bold"), padx=10, pady=5, command=self._export_csv).pack(side="left", padx=(0, 8))

        ModernButton(bottom_bar, text="Transfer to Discovery Journal", icon="📓", bg_color=Theme.BLUE,
                     font=("Segoe UI", 8, "bold"), padx=10, pady=5, command=self._transfer_to_journal).pack(side="left", padx=(0, 8))

        ModernButton(bottom_bar, text="Add Run Observation", icon="📝", bg_color=Theme.BG_INPUT,
                     font=("Segoe UI", 8), padx=10, pady=5, command=self._add_observation_modal).pack(side="left")

    def refresh_active_experiment(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        self.title_lbl.config(text=exp.get("title", "Untitled"))
        self.domain_badge.config(text=f" {exp.get('domain', 'Science').upper()} ")
        self.equation_lbl.config(text=f"Model: {exp.get('equation', 'y = f(x)')}")

        # Build dynamic sliders for each parameter
        for w in self.param_controls_box.winfo_children():
            w.destroy()
        self.param_vars.clear()

        params = exp.get("parameters", [])
        for p in params:
            sym = p.get("symbol", "")
            d_val = float(p.get("default", 1.0))
            p_min = float(p.get("min", -10.0))
            p_max = float(p.get("max", 10.0))
            p_step = float(p.get("step", 0.1))

            p_box = tk.Frame(self.param_controls_box, bg=Theme.BG_CARD, pady=4)
            p_box.pack(fill="x")

            top_p = tk.Frame(p_box, bg=Theme.BG_CARD)
            top_p.pack(fill="x")

            tk.Label(top_p, text=f"{p.get('name', sym)} ({sym})", font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

            val_var = tk.DoubleVar(value=d_val)
            self.param_vars[sym] = val_var

            val_entry = tk.Entry(top_p, width=7, font=("Consolas", 8, "bold"), bg=Theme.BG_INPUT,
                                 fg=Theme.CYAN_BRIGHT, highlightthickness=1)
            val_entry.insert(0, f"{d_val:g}")
            val_entry.pack(side="right")

            # Slider
            slider = ttk.Scale(p_box, from_=p_min, to=p_max, value=d_val,
                               command=lambda v, s=sym, ve=val_entry: self._on_slider_change(s, v, ve))
            slider.pack(fill="x", pady=(2, 0))

            val_entry.bind("<Return>", lambda _, s=sym, sl=slider, ve=val_entry: self._on_entry_change(s, sl, ve))

        self.after(50, self.execute_and_plot)

    def _on_slider_change(self, sym, val_str, val_entry):
        try:
            val = float(val_str)
            self.param_vars[sym].set(val)
            val_entry.delete(0, "end")
            val_entry.insert(0, f"{val:.3g}")
            # Live recalculate
            self.execute_and_plot()
        except ValueError:
            pass

    def _on_entry_change(self, sym, slider, val_entry):
        try:
            val = float(val_entry.get().strip())
            self.param_vars[sym].set(val)
            slider.set(val)
            self.execute_and_plot()
        except ValueError:
            pass

    def _set_plot_mode(self, mode):
        self.plot_mode = mode
        # Update button highlights
        self.btn_line.config(bg=Theme.CYAN if mode == "line" else Theme.BG_INPUT,
                             fg=Theme.BG_ROOT if mode == "line" else Theme.TEXT_SECONDARY)
        self.btn_scatter.config(bg=Theme.CYAN if mode == "scatter" else Theme.BG_INPUT,
                                fg=Theme.BG_ROOT if mode == "scatter" else Theme.TEXT_SECONDARY)
        self.btn_hist.config(bg=Theme.CYAN if mode == "histogram" else Theme.BG_INPUT,
                             fg=Theme.BG_ROOT if mode == "histogram" else Theme.TEXT_SECONDARY)
        self.execute_and_plot()

    def execute_and_plot(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        param_overrides = {k: v.get() for k, v in self.param_vars.items()}
        result = ExperimentExecutionEngine.execute_experiment(exp, param_overrides=param_overrides)
        self.last_run_result = result

        if result.get("execution_status") == "ERROR":
            self.exec_status_lbl.config(text=f"✗ Error: {result.get('error_info')}", fg=Theme.ROSE)
            return

        self.exec_status_lbl.config(
            text=f"✓ Calculated {len(result.get('calculated_outputs', []))} points successfully at {result.get('timestamp')[-8:]}",
            fg=Theme.EMERALD
        )

        # Update stats cards
        stats = result.get("summary_stats", {})
        for k, lbl in self.stat_widgets.items():
            val = stats.get(k, "--")
            lbl.config(text=f"{val:g}" if isinstance(val, (int, float)) else str(val))

        # Render Plot
        outputs = result.get("calculated_outputs", [])
        x_vals = [pt["x"] for pt in outputs]
        y_vals = [pt["y"] for pt in outputs]

        if self.plot_mode == "line":
            ExperimentCanvasPlotter.plot_line_or_scatter(
                self.plot_canvas, x_vals, y_vals, x_label="Independent Variable (x)",
                y_label="Calculated Output (y)", title=exp.get("title", ""), is_scatter=False
            )
        elif self.plot_mode == "scatter":
            ExperimentCanvasPlotter.plot_line_or_scatter(
                self.plot_canvas, x_vals, y_vals, x_label="Independent Variable (x)",
                y_label="Calculated Output (y)", title=exp.get("title", ""), is_scatter=True
            )
        elif self.plot_mode == "histogram":
            ExperimentCanvasPlotter.plot_histogram(
                self.plot_canvas, y_vals, title=f"Output Distribution ({exp.get('title', '')})"
            )

    def _save_run_record(self):
        if not self.last_run_result:
            self.execute_and_plot()
        if not self.last_run_result or self.last_run_result.get("execution_status") == "ERROR":
            messagebox.showerror("Error", "Cannot save an invalid or failed execution.")
            return

        exp = self._get_active_experiment()
        if not exp:
            return

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_custom_experiment_run(exp.get("id"), self.last_run_result)
            messagebox.showinfo("Run Saved", f"Run successfully recorded!\n\nRun ID: {self.last_run_result.get('run_id')}\nTimestamp: {self.last_run_result.get('timestamp')}")

    def _export_csv(self):
        if not self.last_run_result or not self.last_run_result.get("calculated_outputs"):
            messagebox.showwarning("No Data", "No execution output data to export. Click 'Recalculate / Run' first.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export Experiment Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["# CurioLab Experiment Lab Export"])
                writer.writerow(["# Experiment", self._get_active_experiment().get("title", "")])
                writer.writerow(["# Run ID", self.last_run_result.get("run_id")])
                writer.writerow(["# Timestamp", self.last_run_result.get("timestamp")])
                writer.writerow([])
                writer.writerow(["step", "x", "y"])
                for pt in self.last_run_result.get("calculated_outputs", []):
                    writer.writerow([pt.get("step", 0), pt.get("x", 0.0), pt.get("y", 0.0)])

            messagebox.showinfo("Export Successful", f"Experiment results successfully exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save CSV: {str(e)}")

    def _transfer_to_journal(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        # Prepare rich journal draft
        docs = exp.get("documentation", {})
        draft = {
            "source_type": "experiment_lab",
            "title": f"Empirical Investigation: {exp.get('title', 'Experiment')}",
            "domain": exp.get("domain", "Mathematics"),
            "research_question": docs.get("research_question") or exp.get("objective", ""),
            "objective": exp.get("objective", ""),
            "theoretical_background": docs.get("theoretical_background") or exp.get("theoretical_background", ""),
            "hypothesis": docs.get("hypothesis", ""),
            "methodology": docs.get("methodology", f"Calculated series using model: {exp.get('equation', '')}"),
            "parameter_configurations": ", ".join(f"{k}={v:g}" for k, v in self.last_run_result.get("parameter_values", {}).items()) if self.last_run_result else "",
            "observations": docs.get("observations", "Executed controlled parameter run."),
            "results": (f"Count: {self.last_run_result.get('summary_stats', {}).get('count')}, "
                        f"Mean: {self.last_run_result.get('summary_stats', {}).get('mean')}, "
                        f"Range: [{self.last_run_result.get('summary_stats', {}).get('min')}, {self.last_run_result.get('summary_stats', {}).get('max')}]") if self.last_run_result else "",
            "interpretation": docs.get("interpretation", ""),
            "limitations": docs.get("limitations", "Deterministic simulated model assuming zero measurement friction."),
            "conclusion": docs.get("conclusion", ""),
            "tags": exp.get("tags", []) + ["ExperimentLab", "Simulation"],
            "status": docs.get("hypothesis_status", "Under Investigation")
        }

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.pending_journal_draft = draft

        # Navigate to Discovery Journal
        if hasattr(self.app, "navigate_to"):
            self.app.navigate_to("Discovery Journal")
            messagebox.showinfo("Draft Transferred", "Experiment transferred into Discovery Journal draft review. Review and save your journal entry.")
        elif hasattr(self.app, "switch_page"):
            self.app.switch_page("Discovery Journal")
            messagebox.showinfo("Draft Transferred", "Experiment transferred into Discovery Journal draft review. Review and save your journal entry.")

    def _add_observation_modal(self):
        diag = tk.Toplevel(self)
        diag.title("Add Run Observation")
        diag.geometry("450x260")
        diag.configure(bg=Theme.BG_ROOT)
        diag.transient(self)
        diag.grab_set()

        f = tk.Frame(diag, bg=Theme.BG_CARD, padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(f, text="Add Observation to Current Execution", font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        tk.Label(f, text="Record qualitative insights or unexpected behaviors observed in this run.",
                 font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 8))

        txt = tk.Text(f, height=5, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 9))
        txt.pack(fill="both", expand=True)

        def _save():
            note = txt.get("1.0", "end-1c").strip()
            if self.last_run_result:
                self.last_run_result["notes"] = note
            diag.destroy()
            messagebox.showinfo("Note Recorded", "Observation attached to current run configuration.")

        btn_r = tk.Frame(f, bg=Theme.BG_CARD)
        btn_r.pack(fill="x", pady=(10, 0))
        ModernButton(btn_r, text="Save Note", bg_color=Theme.BLUE, command=_save).pack(side="right")
        ModernButton(btn_r, text="Cancel", bg_color=Theme.BG_INPUT, command=diag.destroy).pack(side="right", padx=6)

    def _get_active_experiment(self):
        if hasattr(self.app, "state") and self.app.state:
            eid = getattr(self.app.state, "active_custom_experiment_id", None)
            if eid:
                return self.app.state.get_custom_experiment(eid)
            # Default to first custom experiment
            if self.app.state.custom_experiments:
                first_exp = list(self.app.state.custom_experiments.values())[0] if isinstance(self.app.state.custom_experiments, dict) else self.app.state.custom_experiments[0]
                self.app.state.active_custom_experiment_id = first_exp.get("id")
                return first_exp
        return None

    def _on_edit(self):
        exp = self._get_active_experiment()
        if exp and self.on_edit_callback:
            self.on_edit_callback(exp.get("id"))

    def _on_history(self):
        exp = self._get_active_experiment()
        if exp and self.on_history_callback:
            self.on_history_callback(exp.get("id"))

    def _on_docs(self):
        exp = self._get_active_experiment()
        if exp and self.on_docs_callback:
            self.on_docs_callback(exp.get("id"))


# =============================================================================
# 8. EXPERIMENT DISCUSSION & RESEARCH DOCUMENTATION (13 FIELDS)
# =============================================================================

class ExperimentDiscussionView(tk.Frame):
    """
    Dedicated scientific research documentation and discussion section:
    - 13 scientific research documentation fields:
      1. Research Question, 2. Objective, 3. Theoretical Background,
      4. Hypothesis, 5. Methodology, 6. Parameters and Conditions,
      7. Observations, 8. Results, 9. Interpretation, 10. Unexpected Findings,
      11. Limitations, 12. Conclusion, 13. Future Investigation
    - Hypothesis verification status selector:
      `Under Investigation`, `Supported by Evidence`, `Inconclusive / Needs Replication`, `Refuted`
    - Scientific Rigor Notice disclaimer banner
    - Run Association: import parameter snapshot and summary stats into documentation
    - Save Documentation to AppState
    - Transfer to Discovery Journal draft review
    """
    FIELDS = [
        ("research_question", "1. Research Question", 2),
        ("objective", "2. Objective", 2),
        ("theoretical_background", "3. Theoretical Background", 3),
        ("hypothesis", "4. Hypothesis", 2),
        ("methodology", "5. Methodology", 3),
        ("parameters_conditions", "6. Parameters and Conditions", 2),
        ("observations", "7. Observations", 3),
        ("results", "8. Results", 3),
        ("interpretation", "9. Interpretation", 3),
        ("unexpected_findings", "10. Unexpected Findings", 2),
        ("limitations", "11. Limitations", 3),
        ("conclusion", "12. Conclusion", 3),
        ("future_investigation", "13. Future Investigation", 2)
    ]

    def __init__(self, parent, app, on_back_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.on_back_callback = on_back_callback
        self.text_widgets = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg=Theme.BG_HEADER, padx=24, pady=14,
                          highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        header.pack(fill="x")

        top_r = tk.Frame(header, bg=Theme.BG_HEADER)
        top_r.pack(fill="x")

        left_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        left_h.pack(side="left")

        tk.Label(left_h, text="📝 RESEARCH DOCUMENTATION  •  13 SCIENTIFIC FIELDS",
                 font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.AMBER,
                 padx=8, pady=2).pack(anchor="w")

        self.title_lbl = tk.Label(left_h, text="Experiment Discussion & Scientific Analysis",
                                  font=("Segoe UI", 16, "bold"), bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY)
        self.title_lbl.pack(anchor="w", pady=(2, 0))

        right_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        right_h.pack(side="right")

        ModernButton(right_h, text="Save Documentation", icon="💾", bg_color=Theme.EMERALD,
                     font=("Segoe UI", 9, "bold"), padx=12, pady=6, command=self._save_docs).pack(side="right", padx=(6, 0))
        ModernButton(right_h, text="Transfer to Journal", icon="📓", bg_color=Theme.BLUE,
                     font=("Segoe UI", 9, "bold"), padx=12, pady=6, command=self._transfer_to_journal).pack(side="right")

        # 2. Scientific Rigor Notice (Mandatory Requirement)
        rigor_box = tk.Frame(self, bg="#1E1B4B", padx=18, pady=10,
                             highlightbackground=Theme.PURPLE, highlightthickness=1)
        rigor_box.pack(fill="x", padx=24, pady=(10, 6))

        tk.Label(rigor_box,
                 text="⚠️ Scientific Rigor Notice: Executing an experiment verifies computational correctness, "
                      "NOT scientific truth. Scientific validation requires empirical replication, methodological rigor, "
                      "and critical interpretation of limitations. Do not mark a hypothesis as verified simply because code ran.",
                 font=("Segoe UI", 8, "bold"), bg="#1E1B4B", fg="#E0E7FF", wraplength=950, justify="left").pack(anchor="w")

        # 3. Hypothesis Status & Run Association Bar
        ctrl_bar = tk.Frame(self, bg=Theme.BG_CARD, padx=24, pady=10,
                            highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        ctrl_bar.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(ctrl_bar, text="Hypothesis Verification Status:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 8))

        self.status_var = tk.StringVar(value="Under Investigation")
        status_cb = ttk.Combobox(ctrl_bar, textvariable=self.status_var, values=[
            "Under Investigation",
            "Supported by Evidence",
            "Inconclusive / Needs Replication",
            "Refuted / Counter-Evidence Found"
        ], state="readonly", width=32)
        status_cb.pack(side="left", padx=(0, 24))

        # Import Run Data helper
        tk.Label(ctrl_bar, text="Import Run Data:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        self.run_select_var = tk.StringVar(value="Select Run...")
        self.run_cb = ttk.Combobox(ctrl_bar, textvariable=self.run_select_var, state="readonly", width=22)
        self.run_cb.pack(side="left", padx=(0, 8))

        ModernButton(ctrl_bar, text="Import Run", icon="📥", bg_color=Theme.BG_INPUT,
                     font=("Segoe UI", 8), padx=8, pady=3, command=self._import_run_snapshot).pack(side="left")

        # 4. Scrollable Container for the 13 fields
        self.scroll = ScrollableFrame(self, bg=Theme.BG_ROOT)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 14))
        c = self.scroll.scrollable_content

        for key, title, height in self.FIELDS:
            f_box = tk.Frame(c, bg=Theme.BG_CARD, padx=14, pady=10,
                             highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
            f_box.pack(fill="x", pady=(0, 10))

            tk.Label(f_box, text=title, font=("Segoe UI", 9, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.CYAN_BRIGHT).pack(anchor="w", pady=(0, 4))

            txt = tk.Text(f_box, height=height, bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                          insertbackground=Theme.CYAN, font=("Segoe UI", 9),
                          highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            txt.pack(fill="x")
            self.text_widgets[key] = txt

    def refresh_active_experiment(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        self.title_lbl.config(text=f"Discussion: {exp.get('title', 'Untitled')}")

        docs = exp.get("documentation", {})
        for key, _, _ in self.FIELDS:
            txt_w = self.text_widgets.get(key)
            if txt_w:
                txt_w.delete("1.0", "end")
                txt_w.insert("1.0", docs.get(key, ""))

        self.status_var.set(docs.get("hypothesis_status", "Under Investigation"))

        # Update run dropdown
        runs = exp.get("runs", [])
        run_ids = [r.get("run_id") for r in runs]
        if run_ids:
            self.run_cb.config(values=run_ids)
            self.run_select_var.set(run_ids[-1])
        else:
            self.run_cb.config(values=["No runs recorded"])
            self.run_select_var.set("No runs recorded")

    def _import_run_snapshot(self):
        rid = self.run_select_var.get()
        exp = self._get_active_experiment()
        if not exp or rid == "No runs recorded":
            return

        target_run = None
        for r in exp.get("runs", []):
            if r.get("run_id") == rid:
                target_run = r
                break
        if not target_run:
            return

        # Format into observations and results fields
        p_str = ", ".join(f"{k}={v:g}" for k, v in target_run.get("parameter_values", {}).items())
        stats = target_run.get("summary_stats", {})
        stats_str = f"Count={stats.get('count')}, Mean={stats.get('mean')}, Min={stats.get('min')}, Max={stats.get('max')}, StdDev={stats.get('stdev')}"

        res_txt = self.text_widgets.get("results")
        if res_txt:
            res_txt.insert("end", f"\n[Run {rid}]: {stats_str}")

        param_txt = self.text_widgets.get("parameters_conditions")
        if param_txt:
            param_txt.insert("end", f"\n[Run {rid} parameters]: {p_str}")

        messagebox.showinfo("Imported", f"Appended snapshot of run '{rid}' to Parameters and Results fields.")

    def _save_docs(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        docs = {}
        for key, _, _ in self.FIELDS:
            txt_w = self.text_widgets.get(key)
            if txt_w:
                docs[key] = txt_w.get("1.0", "end-1c").strip()

        docs["hypothesis_status"] = self.status_var.get()

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.update_experiment_documentation(exp.get("id"), docs, self.status_var.get())
            messagebox.showinfo("Documentation Saved", "Scientific research documentation successfully saved.")

    def _transfer_to_journal(self):
        self._save_docs()
        exp = self._get_active_experiment()
        if not exp:
            return

        docs = exp.get("documentation", {})
        draft = {
            "source_type": "experiment_lab",
            "title": f"Scientific Investigation: {exp.get('title', 'Experiment')}",
            "domain": exp.get("domain", "Mathematics"),
            "research_question": docs.get("research_question", ""),
            "objective": docs.get("objective", ""),
            "theoretical_background": docs.get("theoretical_background", ""),
            "hypothesis": docs.get("hypothesis", ""),
            "methodology": docs.get("methodology", ""),
            "parameter_configurations": docs.get("parameters_conditions", ""),
            "observations": docs.get("observations", ""),
            "results": docs.get("results", ""),
            "interpretation": docs.get("interpretation", ""),
            "limitations": docs.get("limitations", ""),
            "conclusion": docs.get("conclusion", ""),
            "tags": exp.get("tags", []) + ["ExperimentLab", "ResearchDoc"],
            "status": docs.get("hypothesis_status", "Under Investigation")
        }

        if hasattr(self.app, "state") and self.app.state:
            self.app.state.pending_journal_draft = draft

        if hasattr(self.app, "navigate_to"):
            self.app.navigate_to("Discovery Journal")
            messagebox.showinfo("Draft Transferred", "Full 13-field experiment dossier transferred to Discovery Journal draft.")
        elif hasattr(self.app, "switch_page"):
            self.app.switch_page("Discovery Journal")
            messagebox.showinfo("Draft Transferred", "Full 13-field experiment dossier transferred to Discovery Journal draft.")

    def _get_active_experiment(self):
        if hasattr(self.app, "state") and self.app.state:
            eid = getattr(self.app.state, "active_custom_experiment_id", None)
            if eid:
                return self.app.state.get_custom_experiment(eid)
            if self.app.state.custom_experiments:
                first_exp = list(self.app.state.custom_experiments.values())[0] if isinstance(self.app.state.custom_experiments, dict) else self.app.state.custom_experiments[0]
                self.app.state.active_custom_experiment_id = first_exp.get("id")
                return first_exp
        return None


# =============================================================================
# 9. EXPERIMENT RUN HISTORY & MULTI-RUN COMPARISON
# =============================================================================

class ExperimentRunHistoryView(tk.Frame):
    """
    Run history exploration, inspection, and multi-run comparative analysis:
    - Run history table with checkbox selection
    - Multi-run parameter difference table
    - Comparative metrics (Delta Mean, Delta Min, Delta Max, Std Dev diff)
    - Multi-run overlay Canvas plot with distinct colors and legend
    - Run-specific notes editor
    - Export run results to CSV
    - Delete individual run with confirmation
    """
    def __init__(self, parent, app, on_back_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.on_back_callback = on_back_callback

        self.selected_runs = {}  # run_id -> tk.BooleanVar

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg=Theme.BG_HEADER, padx=24, pady=14,
                          highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        header.pack(fill="x")

        top_r = tk.Frame(header, bg=Theme.BG_HEADER)
        top_r.pack(fill="x")

        left_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        left_h.pack(side="left")

        tk.Label(left_h, text="📜 RUN HISTORY & COMPARATIVE ANALYSIS",
                 font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN,
                 padx=8, pady=2).pack(anchor="w")

        self.title_lbl = tk.Label(left_h, text="Experiment Runs History",
                                  font=("Segoe UI", 16, "bold"), bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY)
        self.title_lbl.pack(anchor="w", pady=(2, 0))

        right_h = tk.Frame(top_r, bg=Theme.BG_HEADER)
        right_h.pack(side="right")

        ModernButton(right_h, text="Select All", bg_color=Theme.BG_CARD,
                     font=("Segoe UI", 8), padx=8, pady=4, command=self._select_all_runs).pack(side="right", padx=(6, 0))
        ModernButton(right_h, text="Deselect All", bg_color=Theme.BG_CARD,
                     font=("Segoe UI", 8), padx=8, pady=4, command=self._deselect_all_runs).pack(side="right")

        # 2. Split Workspace: Left Run Table vs Right Comparison
        main_split = tk.Frame(self, bg=Theme.BG_ROOT)
        main_split.pack(fill="both", expand=True, padx=24, pady=12)
        main_split.columnconfigure(0, weight=1)
        main_split.columnconfigure(1, weight=1)

        # Left Column: Runs List
        left_box = tk.Frame(main_split, bg=Theme.BG_CARD, padx=14, pady=12,
                            highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left_box, text="Recorded Runs (Check to Compare)", font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        self.runs_scroll = ScrollableFrame(left_box, bg=Theme.BG_CARD)
        self.runs_scroll.pack(fill="both", expand=True)
        self.runs_list_box = self.runs_scroll.scrollable_content

        # Right Column: Comparative Analysis & Overlay Plot
        self.right_box = tk.Frame(main_split, bg=Theme.BG_CARD, padx=14, pady=12,
                                  highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        self.right_box.grid(row=0, column=1, sticky="nsew")

        tk.Label(self.right_box, text="Multi-Run Comparison & Overlay", font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        # Comparison Canvas
        self.comp_canvas = tk.Canvas(self.right_box, bg=Theme.BG_CARD, highlightthickness=0, height=220)
        self.comp_canvas.pack(fill="x", pady=(0, 10))

        # Comparison Parameter Diff & Delta Table
        self.diff_scroll = ScrollableFrame(self.right_box, bg=Theme.BG_CARD)
        self.diff_scroll.pack(fill="both", expand=True)
        self.diff_box = self.diff_scroll.scrollable_content

    def refresh_active_experiment(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        self.title_lbl.config(text=f"Runs History: {exp.get('title', 'Untitled')}")
        self.selected_runs.clear()

        for w in self.runs_list_box.winfo_children():
            w.destroy()

        runs = exp.get("runs", [])
        if not runs:
            tk.Label(self.runs_list_box, text="No runs recorded yet for this experiment.\nExecute a run from the Results view to save history.",
                     font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, justify="center").pack(pady=20)
            self._update_comparison()
            return

        for idx, r in enumerate(reversed(runs)):
            rid = r.get("run_id")
            card = tk.Frame(self.runs_list_box, bg=Theme.BG_INPUT, padx=10, pady=8,
                            highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            card.pack(fill="x", pady=(0, 6))

            top = tk.Frame(card, bg=Theme.BG_INPUT)
            top.pack(fill="x")

            # Checkbox
            var = tk.BooleanVar(value=True if idx < 3 else False)
            self.selected_runs[rid] = var
            cb = tk.Checkbutton(top, variable=var, bg=Theme.BG_INPUT, activebackground=Theme.BG_INPUT,
                                selectcolor=Theme.BG_CARD, command=self._update_comparison)
            cb.pack(side="left")

            tk.Label(top, text=rid, font=("Consolas", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT).pack(side="left", padx=4)

            status = r.get("execution_status", "SUCCESS")
            tk.Label(top, text=f" {status} ", font=("Segoe UI", 7, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.EMERALD if status == "SUCCESS" else Theme.ROSE).pack(side="left", padx=4)

            del_btn = tk.Label(top, text="🗑", font=("Segoe UI", 9), bg=Theme.BG_INPUT, fg=Theme.ROSE, cursor="hand2")
            del_btn.pack(side="right", padx=(6, 0))
            del_btn.bind("<Button-1>", lambda _, rid=rid: self._delete_run(rid))

            csv_btn = tk.Label(top, text="📥", font=("Segoe UI", 9), bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT, cursor="hand2")
            csv_btn.pack(side="right")
            csv_btn.bind("<Button-1>", lambda _, r=r: self._export_run_csv(r))

            # Details
            t_str = r.get("timestamp", "")
            p_str = ", ".join(f"{k}={v:g}" for k, v in list(r.get("parameter_values", {}).items())[:3])
            stats = r.get("summary_stats", {})
            st_str = f"Mean: {stats.get('mean')}, Range: [{stats.get('min')}, {stats.get('max')}]"

            tk.Label(card, text=f"{t_str}  |  {p_str}", font=("Segoe UI", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(2, 0))
            tk.Label(card, text=st_str, font=("Consolas", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 0))

            if r.get("notes"):
                tk.Label(card, text=f"Note: {r.get('notes')}", font=("Segoe UI", 8, "italic"),
                         bg=Theme.BG_INPUT, fg=Theme.AMBER, anchor="w").pack(fill="x", pady=(2, 0))

        self._update_comparison()

    def _select_all_runs(self):
        for v in self.selected_runs.values():
            v.set(True)
        self._update_comparison()

    def _deselect_all_runs(self):
        for v in self.selected_runs.values():
            v.set(False)
        self._update_comparison()

    def _update_comparison(self):
        exp = self._get_active_experiment()
        if not exp:
            return

        selected_records = []
        for r in exp.get("runs", []):
            rid = r.get("run_id")
            if self.selected_runs.get(rid, tk.BooleanVar(value=False)).get():
                selected_records.append(r)

        # Render Canvas Overlay
        ExperimentCanvasPlotter.plot_multi_run_comparison(
            self.comp_canvas, selected_records,
            x_label="x", y_label="Output y",
            title=f"Overlay Comparison ({len(selected_records)} Runs)"
        )

        # Render Diff Table
        for w in self.diff_box.winfo_children():
            w.destroy()

        if not selected_records:
            tk.Label(self.diff_box, text="Check at least one run on the left to inspect parameters and outputs.",
                     font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(pady=10)
            return

        # Comparative Metrics Table
        table_frame = tk.Frame(self.diff_box, bg=Theme.BG_INPUT, padx=10, pady=8,
                               highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        table_frame.pack(fill="x", pady=(0, 10))

        tk.Label(table_frame, text="Comparative Run Metrics", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT).pack(anchor="w", pady=(0, 6))

        for idx, r in enumerate(selected_records):
            stats = r.get("summary_stats", {})
            params = r.get("parameter_values", {})
            p_desc = ", ".join(f"{k}={v:g}" for k, v in params.items())

            row = tk.Frame(table_frame, bg=Theme.BG_CARD, padx=8, pady=6)
            row.pack(fill="x", pady=2)

            color = ExperimentCanvasPlotter.PALETTE[idx % len(ExperimentCanvasPlotter.PALETTE)]
            c_tag = tk.Label(row, text="  ", bg=color, font=("Segoe UI", 8))
            c_tag.pack(side="left", padx=(0, 6))

            tk.Label(row, text=r.get("run_id", "")[:15], font=("Consolas", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

            tk.Label(row, text=f"Params: {p_desc}", font=("Segoe UI", 8),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=8)

            metrics_s = f"Mean: {stats.get('mean')}  |  Min: {stats.get('min')}  |  Max: {stats.get('max')}  |  σ: {stats.get('stdev')}"
            tk.Label(row, text=metrics_s, font=("Consolas", 8),
                     bg=Theme.BG_CARD, fg=Theme.EMERALD).pack(side="right")

    def _delete_run(self, run_id):
        confirm = messagebox.askyesno("Delete Run Record", f"Are you sure you want to delete run record '{run_id}'?")
        if confirm:
            exp = self._get_active_experiment()
            if exp and hasattr(self.app, "state") and self.app.state:
                self.app.state.delete_custom_experiment_run(exp.get("id"), run_id)
                self.refresh_active_experiment()

    def _export_run_csv(self, run_record):
        filepath = filedialog.asksaveasfilename(
            title=f"Export Run {run_record.get('run_id')} to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["# Run ID", run_record.get("run_id")])
                writer.writerow(["# Timestamp", run_record.get("timestamp")])
                writer.writerow(["step", "x", "y"])
                for pt in run_record.get("calculated_outputs", []):
                    writer.writerow([pt.get("step", 0), pt.get("x", 0.0), pt.get("y", 0.0)])
            messagebox.showinfo("Export Successful", f"Run exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save CSV: {str(e)}")

    def _get_active_experiment(self):
        if hasattr(self.app, "state") and self.app.state:
            eid = getattr(self.app.state, "active_custom_experiment_id", None)
            if eid:
                return self.app.state.get_custom_experiment(eid)
            if self.app.state.custom_experiments:
                first_exp = list(self.app.state.custom_experiments.values())[0] if isinstance(self.app.state.custom_experiments, dict) else self.app.state.custom_experiments[0]
                self.app.state.active_custom_experiment_id = first_exp.get("id")
                return first_exp
        return None


# =============================================================================
# 10. BUILT-IN EXPERIMENTS VIEW (CAESAR, NEURAL, DATAVIZ)
# =============================================================================

class BuiltInExperimentsView(tk.Frame):
    """
    Houses the 3 original built-in interactive experiments:
    1. Caesar Cipher (Encryption Playground)
    2. Single Artificial Neuron (Neural Network Playground)
    3. Data Visualization Lab (Dynamic Canvas Bar Chart)
    Preserves 100% of existing functionality, diagrams, charts, and calculations.
    """
    def __init__(self, parent, app, on_back_callback=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app
        self.on_back_callback = on_back_callback

        self.current_sub_view = "encryption"
        self.sub_views = {}
        self.subnav_buttons = {}

        # 1. Top Subnav Bar
        self._build_subnav()

        # 2. Content container
        self.content_box = tk.Frame(self, bg=Theme.BG_ROOT)
        self.content_box.pack(fill="both", expand=True)

        # 3. Instantiate original views
        self.sub_views["encryption"] = self._create_encryption_view()
        self.sub_views["neural"] = self._create_neural_view()
        self.sub_views["dataviz"] = self._create_dataviz_view()

        self.switch_builtin("encryption")

    def _build_subnav(self):
        bar = tk.Frame(self, bg=Theme.BG_HEADER,
                       highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=24, pady=8)
        bar.pack(fill="x", side="top")

        lbl = tk.Label(bar, text="BUILT-IN EXPERIMENTS:", font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        lbl.pack(side="left", padx=(0, 12))

        tabs = [
            ("encryption", "🔐 Encryption Playground (Caesar)", Theme.PURPLE),
            ("neural", "🧠 Single Artificial Neuron", Theme.CYAN),
            ("dataviz", "📊 Data Visualization Lab", Theme.TEAL),
        ]

        for key, title, accent in tabs:
            btn_frame = tk.Frame(bar, bg=Theme.BG_INPUT,
                                 highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, cursor="hand2")
            btn_frame.pack(side="left", padx=(0, 8))

            btn_lbl = tk.Label(btn_frame, text=title, font=("Segoe UI", 9, "bold"),
                               bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=12, pady=5, cursor="hand2")
            btn_lbl.pack()

            for w in (btn_frame, btn_lbl):
                w.bind("<Button-1>", lambda _, k=key: self.switch_builtin(k))

            self.subnav_buttons[key] = {
                "frame": btn_frame,
                "label": btn_lbl,
                "accent": accent
            }

    def switch_builtin(self, exp_key):
        if exp_key not in self.sub_views:
            return

        prev = self.current_sub_view
        self.current_sub_view = exp_key

        for k, item in self.subnav_buttons.items():
            if k == exp_key:
                item["frame"].config(bg=Theme.BG_CARD_HOVER, highlightbackground=item["accent"])
                item["label"].config(bg=Theme.BG_CARD_HOVER, fg=item["accent"])
            else:
                item["frame"].config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
                item["label"].config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

        self.sub_views[exp_key].pack(fill="both", expand=True)
        if prev and prev != exp_key and prev in self.sub_views:
            self.sub_views[prev].pack_forget()

        if exp_key == "neural":
            self.after(50, self._calculate_neuron)
        elif exp_key == "dataviz":
            self.after(50, self._generate_chart)

    def switch_to_experiment(self, exp_key):
        if exp_key in ("encryption", "neural", "dataviz"):
            self.switch_builtin(exp_key)
        elif self.on_back_callback:
            self.on_back_callback()

    def _create_encryption_view(self):
        """Builds the Caesar Cipher interactive encryption & decryption laboratory."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Action Bar: Back to Experiments
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Experiments Overview", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_experiment("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Experiment Lab > Cryptography > Caesar Cipher Playground",
                              font=("Segoe UI", 9),
                              bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.PURPLE,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="🔐 CLASSICAL CRYPTOGRAPHY",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="Encryption Playground: Caesar Cipher Engine",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="The Caesar Cipher is a classic modular substitution cipher where each letter in the plaintext "
                 "is shifted by a fixed key k. Julius Caesar famously used this technique with a shift of 3 (A ➔ D) "
                 "to protect military communications.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        formula_box = tk.Label(
            hero,
            text="Mathematical Transformation:  C = (P + k) mod 26    |    P = (C - k) mod 26",
            font=("Consolas", 9, "bold"),
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
            padx=10, pady=4
        )
        formula_box.pack(anchor="w", pady=(10, 0))

        # Educational Panel: How Caesar Cipher Works & Visual Example
        edu_card = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=22, pady=16)
        edu_card.pack(fill="x", padx=32, pady=(0, 20))

        tk.Label(edu_card, text="📖 How Caesar Cipher Works",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        # 4 concepts in a responsive row
        concepts_frame = tk.Frame(edu_card, bg=Theme.BG_CARD)
        concepts_frame.pack(fill="x", pady=(0, 12))
        concepts_frame.columnconfigure(0, weight=1)
        concepts_frame.columnconfigure(1, weight=1)
        concepts_frame.columnconfigure(2, weight=1)
        concepts_frame.columnconfigure(3, weight=1)

        c_data = [
            ("Fixed Position Shift", "Each letter in the message is shifted by a fixed number of positions along the alphabet.", Theme.CYAN),
            ("The Shift Key (k)", "The shift key determines exactly how many alphabetical positions to move.", Theme.PURPLE_LIGHT),
            ("Encryption (Forward)", "Encryption shifts letters forward (e.g. A ➔ D when shift key k = 3).", Theme.TEAL),
            ("Decryption (Backward)", "Decryption shifts letters backward by the same key to recover the original text.", Theme.EMERALD),
        ]

        for i, (ct, cd, cc) in enumerate(c_data):
            box = tk.Frame(concepts_frame, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=12, pady=10)
            box.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0 if i == 3 else 6), sticky="nsew")

            tk.Label(box, text=f"◈ {ct}", font=("Segoe UI", 9, "bold"),
                     bg=Theme.BG_INPUT, fg=cc).pack(anchor="w")
            tk.Label(box, text=cd, font=("Segoe UI", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                     wraplength=190, justify="left").pack(anchor="w", pady=(3, 0))

        # Visual Example Box & Did You Know Row
        extra_row = tk.Frame(edu_card, bg=Theme.BG_CARD)
        extra_row.pack(fill="x")
        extra_row.columnconfigure(0, weight=5)
        extra_row.columnconfigure(1, weight=5)

        # Left: Visual Example (as requested: HELLO with shift 3 -> KHOOR)
        ex_box = tk.Frame(extra_row, bg=Theme.BG_INPUT,
                          highlightbackground=Theme.BORDER_MUTED,
                          highlightthickness=1, padx=14, pady=10)
        ex_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        tk.Label(ex_box, text="VISUAL STEP-BY-STEP EXAMPLE (Shift k = 3):",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(anchor="w")

        ex_display = (
            "Original  :  H   E   L   L   O\n"
            "Shift     : +3  +3  +3  +3  +3\n"
            "Encrypted :  K   H   O   O   R"
        )
        tk.Label(ex_box, text=ex_display, font=("Consolas", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, justify="left").pack(anchor="w", pady=(4, 0))

        # Right: Did You Know?
        dyk_box = tk.Frame(extra_row, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_MUTED,
                           highlightthickness=1, padx=14, pady=10)
        dyk_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        tk.Label(dyk_box, text="💡 Did You Know?",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.AMBER).pack(anchor="w")

        tk.Label(
            dyk_box,
            text="Julius Caesar used this cipher over 2,000 years ago for confidential military dispatches. "
                 "Because the English alphabet has only 26 letters, there are only 25 unique non-trivial shifts, "
                 "making it easy for modern computers to break with a brute-force search!",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED,
            wraplength=380, justify="left"
        ).pack(anchor="w", pady=(4, 0))

        # Main Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        # 1. Presets Bar
        presets_bar = tk.Frame(workspace, bg=Theme.BG_CARD)
        presets_bar.pack(fill="x", pady=(0, 14))

        tk.Label(presets_bar, text="Sample Presets:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 8))

        presets = [
            ("Quantum Postulate", "CurioLab Protocol Alpha: Quantum superposition allows simultaneous computation of basis states.", 3),
            ("Caesar Quote", "Alea iacta est — The die is cast.", 7),
            ("ROT13 Standard", "Scientific discovery requires unyielding curiosity and empirical verification.", 13),
        ]

        for p_name, p_text, p_shift in presets:
            p_btn = tk.Label(presets_bar, text=f"◈ {p_name}",
                             font=("Segoe UI", 8, "underline"),
                             bg=Theme.BG_CARD, fg=Theme.CYAN, cursor="hand2")
            p_btn.pack(side="left", padx=(0, 12))
            p_btn.bind("<Button-1>", lambda _, t=p_text, s=p_shift: self._load_caesar_preset(t, s))

        # 2. Input Section
        in_hdr = tk.Frame(workspace, bg=Theme.BG_CARD)
        in_hdr.pack(fill="x", pady=(0, 6))

        tk.Label(in_hdr, text="Original Message (Plaintext / Ciphertext):",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        self.cipher_char_count = tk.Label(in_hdr, text="Length: 0 chars",
                                          font=("Segoe UI", 8),
                                          bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.cipher_char_count.pack(side="right")

        self.cipher_input = tk.Text(
            workspace, height=4,
            bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Segoe UI", 10),
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1, bd=0, padx=12, pady=10,
            wrap="word"
        )
        self.cipher_input.pack(fill="x", pady=(0, 16))
        self.cipher_input.insert("1.0", "CurioLab Protocol Alpha: Quantum superposition allows simultaneous computation of basis states.")
        self.cipher_input.bind("<KeyRelease>", lambda _: self._update_caesar_char_count())

        # 3. Shift Controls & Action Buttons Row
        ctrl_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        ctrl_row.pack(fill="x", pady=(0, 16))

        # Shift input box
        shift_box = tk.Frame(ctrl_row, bg=Theme.BG_INPUT,
                             highlightbackground=Theme.BORDER_MUTED,
                             highlightthickness=1, padx=8, pady=4)
        shift_box.pack(side="left", padx=(0, 16))

        tk.Label(shift_box, text="Shift Key (k):", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(2, 6))

        # Decrement button
        dec_btn = tk.Label(shift_box, text=" − ", font=("Segoe UI", 10, "bold"),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, cursor="hand2", padx=4)
        dec_btn.pack(side="left")
        dec_btn.bind("<Button-1>", lambda _: self._nudge_shift(-1))

        self.shift_var = tk.StringVar(value="3")
        self.shift_entry = tk.Entry(
            shift_box, textvariable=self.shift_var, width=5,
            font=("Consolas", 10, "bold"), justify="center",
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, bd=0, relief="flat"
        )
        self.shift_entry.pack(side="left", padx=4)
        self.shift_entry.bind("<KeyRelease>", lambda _: self._on_shift_edited())

        # Increment button
        inc_btn = tk.Label(shift_box, text=" + ", font=("Segoe UI", 10, "bold"),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, cursor="hand2", padx=4)
        inc_btn.pack(side="left")
        inc_btn.bind("<Button-1>", lambda _: self._nudge_shift(1))

        # Action Buttons
        ModernButton(ctrl_row, text="Encrypt Message", icon="🔒",
                     bg_color=Theme.PURPLE,
                     command=self._caesar_encrypt).pack(side="left", padx=(0, 8))

        ModernButton(ctrl_row, text="Decrypt Message", icon="🔓",
                     bg_color=Theme.CYAN, text_color=Theme.BG_ROOT,
                     command=self._caesar_decrypt).pack(side="left", padx=(0, 8))

        ModernButton(ctrl_row, text="Swap In/Out", icon="⇄",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._caesar_swap).pack(side="left", padx=(0, 8))

        ModernButton(ctrl_row, text="Clear", icon="🗑️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.ROSE,
                     command=self._caesar_clear).pack(side="left")

        # 4. Status Banner
        self.cipher_status = tk.Label(
            workspace,
            text="Ready. Enter text and select Encrypt or Decrypt.",
            font=("Segoe UI", 8),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED
        )
        self.cipher_status.pack(anchor="w", pady=(0, 12))

        # 5. Output Section
        out_hdr = tk.Frame(workspace, bg=Theme.BG_CARD)
        out_hdr.pack(fill="x", pady=(0, 6))

        tk.Label(out_hdr, text="Transformed Output Result:",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        # Copy Result Button
        self.cipher_copy_btn = ModernButton(
            out_hdr, text="Copy Result", icon="📋",
            bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 8, "bold"),
            padx=10, pady=4,
            command=self._caesar_copy
        )
        self.cipher_copy_btn.pack(side="right")

        self.cipher_output = tk.Text(
            workspace, height=4,
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN_BRIGHT,
            insertbackground=Theme.CYAN,
            font=("Consolas", 10),
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1, bd=0, padx=12, pady=10,
            wrap="word"
        )
        self.cipher_output.pack(fill="x", pady=(0, 16))

        # 6. Live Alphabet Mapping Visualizer
        map_card = tk.Frame(workspace, bg=Theme.BG_INPUT,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=16, pady=12)
        map_card.pack(fill="x")

        tk.Label(map_card, text="Live Alphabet Substitution Mapping:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 4))

        self.cipher_mapping_display = tk.Label(
            map_card,
            text="",
            font=("Consolas", 9),
            bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
            justify="left"
        )
        self.cipher_mapping_display.pack(anchor="w")

        # Initialize displays
        self._update_caesar_char_count()
        self._update_mapping_table(3)
        self._caesar_encrypt()

        scroll.bind_mousewheel(content)
        return scroll

    def _nudge_shift(self, delta):
        """Increments or decrements shift key."""
        try:
            curr = int(self.shift_var.get().strip())
        except ValueError:
            curr = 3
        new_val = curr + delta
        self.shift_var.set(str(new_val))
        self._on_shift_edited()

    def _on_shift_edited(self):
        try:
            s = int(self.shift_var.get().strip())
            self._update_mapping_table(s)
        except ValueError:
            pass

    def _update_mapping_table(self, shift):
        """Updates the visual alphabet mapping display."""
        norm_shift = shift % 26
        plain = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
        shifted_letters = [chr((i + norm_shift) % 26 + ord('A')) for i in range(26)]
        cipher = " ".join(shifted_letters)
        self.cipher_mapping_display.config(
            text=f"Plain : {plain}\nCipher: {cipher}  (k = {shift} ➔ +{norm_shift})"
        )

    def _update_caesar_char_count(self):
        text = self.cipher_input.get("1.0", "end-1c")
        self.cipher_char_count.config(text=f"Length: {len(text)} chars")

    def _load_caesar_preset(self, text, shift):
        self.cipher_input.delete("1.0", "end")
        self.cipher_input.insert("1.0", text)
        self.shift_var.set(str(shift))
        self._update_caesar_char_count()
        self._update_mapping_table(shift)
        self._caesar_encrypt()

    def _caesar_transform(self, text, shift, decrypt=False):
        """Actual Caesar cipher transformation preserving case and symbols."""
        if decrypt:
            shift = -shift
        shift = shift % 26
        res = []
        for char in text:
            if 'a' <= char <= 'z':
                res.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                res.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                res.append(char)
        return "".join(res)

    def _caesar_encrypt(self):
        """Performs encryption with comprehensive status reporting."""
        raw_text = self.cipher_input.get("1.0", "end-1c")
        if not raw_text.strip():
            self.cipher_status.config(
                text="⚠️ Warning: Input message is empty. Please enter text to encrypt.",
                fg=Theme.AMBER
            )
            return

        try:
            shift = int(self.shift_var.get().strip())
        except ValueError:
            self.cipher_status.config(
                text="⚠️ Error: Shift key must be an integer (e.g. 3, 5, 26, -3).",
                fg=Theme.ROSE
            )
            return

        result = self._caesar_transform(raw_text, shift, decrypt=False)
        self.cipher_output.delete("1.0", "end")
        self.cipher_output.insert("1.0", result)
        self._update_mapping_table(shift)

        norm_shift = shift % 26
        self.cipher_status.config(
            text=f"✓ Success: Encrypted {len(raw_text)} characters using shift k = {shift} (normalized: +{norm_shift}). Preserved case, spaces, and symbols.",
            fg=Theme.EMERALD
        )
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_experiment_run("caesar")

    def _caesar_decrypt(self):
        """Performs decryption with comprehensive status reporting."""
        raw_text = self.cipher_input.get("1.0", "end-1c")
        if not raw_text.strip():
            self.cipher_status.config(
                text="⚠️ Warning: Input message is empty. Please enter text to decrypt.",
                fg=Theme.AMBER
            )
            return

        try:
            shift = int(self.shift_var.get().strip())
        except ValueError:
            self.cipher_status.config(
                text="⚠️ Error: Shift key must be an integer (e.g. 3, 5, 26, -3).",
                fg=Theme.ROSE
            )
            return

        result = self._caesar_transform(raw_text, shift, decrypt=True)
        self.cipher_output.delete("1.0", "end")
        self.cipher_output.insert("1.0", result)
        self._update_mapping_table(shift)

        norm_shift = shift % 26
        rev_shift = (-shift) % 26
        self.cipher_status.config(
            text=f"✓ Success: Decrypted {len(raw_text)} characters using shift k = {shift} (reversed: -{norm_shift} ➔ +{rev_shift}). Recovered original text.",
            fg=Theme.CYAN_BRIGHT
        )
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_experiment_run("caesar")

    def _caesar_clear(self):
        """Clears text fields and resets status."""
        self.cipher_input.delete("1.0", "end")
        self.cipher_output.delete("1.0", "end")
        self._update_caesar_char_count()
        self.cipher_status.config(text="Fields cleared. Enter new text to begin.", fg=Theme.TEXT_MUTED)

    def _caesar_swap(self):
        """Swaps input and output text correctly in both directions."""
        in_text = self.cipher_input.get("1.0", "end-1c")
        out_text = self.cipher_output.get("1.0", "end-1c")
        if not in_text.strip() and not out_text.strip():
            self.cipher_status.config(
                text="⚠️ Warning: Both input and output fields are empty. Nothing to swap.",
                fg=Theme.AMBER
            )
            return

        self.cipher_input.delete("1.0", "end")
        self.cipher_input.insert("1.0", out_text)
        self.cipher_output.delete("1.0", "end")
        self.cipher_output.insert("1.0", in_text)
        self._update_caesar_char_count()
        self.cipher_status.config(
            text="⇄ Success: Swapped input and output text in both directions.",
            fg=Theme.CYAN_BRIGHT
        )

    def _caesar_copy(self):
        """Copies output text to clipboard."""
        out_text = self.cipher_output.get("1.0", "end-1c")
        if out_text:
            self.clipboard_clear()
            self.clipboard_append(out_text)
            self.cipher_copy_btn.label.config(text="✓ Copied!")
            self.after(2000, lambda: self.cipher_copy_btn.label.config(text="📋  Copy Result"))

    # =========================================================================
    # SUB-VIEW 3: NEURAL NETWORK PLAYGROUND (ARTIFICIAL NEURON)
    # =========================================================================
    def _create_neural_view(self):
        """Builds the single artificial neuron simulator with Canvas visualization."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Action Bar: Back to Experiments
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Experiments Overview", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_experiment("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Experiment Lab > Machine Learning > Single Artificial Neuron",
                              font=("Segoe UI", 9),
                              bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.CYAN,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="🧠 ARTIFICIAL INTELLIGENCE & NEUROMORPHIC COMPUTING",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="Neural Network Playground: Single Artificial Neuron",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="Simulate a biological perceptron. The artificial neuron computes the weighted sum "
                 "of its synaptic inputs plus a bias: z = (x₁·w₁ + x₂·w₂ + b), and passes the result "
                 "through a non-linear Sigmoid activation function: σ(z) = 1 / (1 + e⁻ᶻ).",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        formula_box = tk.Label(
            hero,
            text="Core Activation Pipeline:   z = (x₁·w₁ + x₂·w₂ + b)   ➔   σ(z) = 1 / (1 + e⁻ᶻ)",
            font=("Consolas", 9, "bold"),
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
            padx=10, pady=4
        )
        formula_box.pack(anchor="w", pady=(10, 0))

        # Educational Panel: How an Artificial Neuron Computes
        edu_card = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=22, pady=16)
        edu_card.pack(fill="x", padx=32, pady=(0, 20))

        tk.Label(edu_card, text="📖 How an Artificial Neuron Works",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        # 4 concept cards
        concepts_frame = tk.Frame(edu_card, bg=Theme.BG_CARD)
        concepts_frame.pack(fill="x", pady=(0, 12))
        concepts_frame.columnconfigure(0, weight=1)
        concepts_frame.columnconfigure(1, weight=1)
        concepts_frame.columnconfigure(2, weight=1)
        concepts_frame.columnconfigure(3, weight=1)

        c_data = [
            ("Artificial Neuron", "A mathematical model inspired by biological brain cells (neurons) that processes incoming signals into an activation decision.", Theme.CYAN),
            ("Synaptic Weights", "Represent connection strength. Positive weights amplify signals (excitatory); negative weights suppress them (inhibitory).", Theme.PURPLE_LIGHT),
            ("Neuron Bias", "An adjustable threshold offset added to the sum, allowing the neuron to activate even when all inputs are zero.", Theme.AMBER),
            ("Sigmoid Function", "An S-shaped non-linear activation curve mapping any real number from -∞ to +∞ into a clean 0.0 to 1.0 probability.", Theme.EMERALD),
        ]

        for i, (ct, cd, cc) in enumerate(c_data):
            box = tk.Frame(concepts_frame, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=12, pady=10)
            box.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0 if i == 3 else 6), sticky="nsew")

            tk.Label(box, text=f"◈ {ct}", font=("Segoe UI", 9, "bold"),
                     bg=Theme.BG_INPUT, fg=cc).pack(anchor="w")
            tk.Label(box, text=cd, font=("Segoe UI", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                     wraplength=190, justify="left").pack(anchor="w", pady=(3, 0))

        # Formulas Banner & Did You Know Row
        formula_dyk_row = tk.Frame(edu_card, bg=Theme.BG_CARD)
        formula_dyk_row.pack(fill="x")
        formula_dyk_row.columnconfigure(0, weight=5)
        formula_dyk_row.columnconfigure(1, weight=5)

        # Left: Required Exact Formulas Display
        f_box = tk.Frame(formula_dyk_row, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED,
                         highlightthickness=1, padx=14, pady=10)
        f_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        tk.Label(f_box, text="MATHEMATICAL FORMULAS:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(anchor="w")

        f_display = (
            "z = (Input A × Weight A) + (Input B × Weight B) + Bias\n"
            "Output = 1 / (1 + e^(-z))"
        )
        tk.Label(f_box, text=f_display, font=("Consolas", 9, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, justify="left").pack(anchor="w", pady=(4, 0))

        # Right: Did You Know?
        dyk_box = tk.Frame(formula_dyk_row, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_MUTED,
                           highlightthickness=1, padx=14, pady=10)
        dyk_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        tk.Label(dyk_box, text="💡 Did You Know?",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.AMBER).pack(anchor="w")

        tk.Label(
            dyk_box,
            text="The human brain contains approximately 86 billion biological neurons. "
                 "Modern deep neural networks chain thousands of artificial neurons across layers "
                 "to perform complex tasks like image synthesis, speech recognition, and scientific discovery!",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED,
            wraplength=380, justify="left"
        ).pack(anchor="w", pady=(4, 0))

        # Main Two-Column Layout
        two_col = tk.Frame(content, bg=Theme.BG_ROOT)
        two_col.pack(fill="x", padx=32, pady=(0, 24))

        two_col.columnconfigure(0, weight=5, uniform="neu") # Left 50%
        two_col.columnconfigure(1, weight=5, uniform="neu") # Right 50%

        left_col = tk.Frame(two_col, bg=Theme.BG_ROOT)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right_col = tk.Frame(two_col, bg=Theme.BG_ROOT)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- LEFT COLUMN: Parameters & Controls ---
        params_card = tk.Frame(left_col, bg=Theme.BG_CARD,
                               highlightbackground=Theme.BORDER_SUBTLE,
                               highlightthickness=1, padx=20, pady=18)
        params_card.pack(fill="both", expand=True)

        tk.Label(params_card, text="⚙️ Synaptic Parameters & Inputs",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        # Presets
        p_row = tk.Frame(params_card, bg=Theme.BG_CARD)
        p_row.pack(fill="x", pady=(0, 12))

        tk.Label(p_row, text="Presets:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 6))

        neural_presets = [
            ("AND Gate", 1.0, 2.0, 1.0, 2.0, -3.0),
            ("OR Gate", 1.0, 2.0, 0.0, 2.0, -1.0),
            ("Inhibitor", 1.0, 2.5, 1.0, -3.5, -0.5),
            ("Balanced", 0.8, 1.5, 0.6, -1.0, 0.2),
        ]

        for p_name, x1, w1, x2, w2, b in neural_presets:
            lbl_btn = tk.Label(p_row, text=f"◈ {p_name}", font=("Segoe UI", 8, "underline"),
                               bg=Theme.BG_CARD, fg=Theme.CYAN, cursor="hand2")
            lbl_btn.pack(side="left", padx=(0, 8))
            lbl_btn.bind("<Button-1>", lambda _, a1=x1, b1=w1, a2=x2, b2=w2, bs=b: self._load_neural_preset(a1, b1, a2, b2, bs))

        # Variables
        self.x1_var = tk.DoubleVar(value=0.80)
        self.w1_var = tk.DoubleVar(value=1.50)
        self.x2_var = tk.DoubleVar(value=0.60)
        self.w2_var = tk.DoubleVar(value=-1.00)
        self.bias_var = tk.DoubleVar(value=0.20)

        # Build Parameter Slider Rows
        self._build_slider_row(params_card, "Input A (x₁)", self.x1_var, -2.0, 2.0, Theme.CYAN)
        self._build_slider_row(params_card, "Weight A (w₁)", self.w1_var, -5.0, 5.0, Theme.PURPLE)
        self._build_slider_row(params_card, "Input B (x₂)", self.x2_var, -2.0, 2.0, Theme.CYAN)
        self._build_slider_row(params_card, "Weight B (w₂)", self.w2_var, -5.0, 5.0, Theme.PURPLE)
        self._build_slider_row(params_card, "Neuron Bias (b)", self.bias_var, -5.0, 5.0, Theme.AMBER)

        # Button Row
        btn_box = tk.Frame(params_card, bg=Theme.BG_CARD)
        btn_box.pack(fill="x", pady=(14, 0))

        ModernButton(btn_box, text="Calculate Output", icon="⚡",
                     bg_color=Theme.CYAN, text_color=Theme.BG_ROOT,
                     command=self._on_calculate_neuron_clicked).pack(side="left", padx=(0, 10))

        ModernButton(btn_box, text="Reset Defaults", icon="↺",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._reset_neural_defaults).pack(side="left")

        self.neural_status = tk.Label(params_card, text="Parameters synchronized.",
                                      font=("Segoe UI", 8),
                                      bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.neural_status.pack(anchor="w", pady=(10, 0))

        # --- RIGHT COLUMN: Metrics & Canvas Diagram ---
        diag_card = tk.Frame(right_col, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=20, pady=18)
        diag_card.pack(fill="both", expand=True)

        tk.Label(diag_card, text="📊 Live Output & Visual Architecture",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 12))

        # 3 Result Metric Boxes
        res_row = tk.Frame(diag_card, bg=Theme.BG_CARD)
        res_row.pack(fill="x", pady=(0, 14))

        res_row.columnconfigure(0, weight=1)
        res_row.columnconfigure(1, weight=1)
        res_row.columnconfigure(2, weight=1)

        # 1. Weighted Sum Box
        b1 = tk.Frame(res_row, bg=Theme.BG_INPUT, padx=10, pady=8,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        b1.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        tk.Label(b1, text="Weighted Sum (z)", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")
        self.neural_z_display = tk.Label(b1, text="+0.8000", font=("Consolas", 12, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        self.neural_z_display.pack(anchor="w", pady=(2, 0))

        # 2. Sigmoid Output Box
        b2 = tk.Frame(res_row, bg=Theme.BG_INPUT, padx=10, pady=8,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        b2.grid(row=0, column=1, padx=(6, 6), sticky="nsew")
        tk.Label(b2, text="Sigmoid σ(z)", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")
        self.neural_sig_display = tk.Label(b2, text="0.6900", font=("Consolas", 12, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT)
        self.neural_sig_display.pack(anchor="w", pady=(2, 0))

        # 3. Activation State Box
        b3 = tk.Frame(res_row, bg=Theme.BG_INPUT, padx=10, pady=8,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        b3.grid(row=0, column=2, padx=(6, 0), sticky="nsew")
        tk.Label(b3, text="Neuron State", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")
        self.neural_state_display = tk.Label(b3, text="● FIRING", font=("Segoe UI", 10, "bold"), bg=Theme.BG_INPUT, fg=Theme.EMERALD)
        self.neural_state_display.pack(anchor="w", pady=(2, 0))

        # Canvas Diagram Area
        self.neuron_canvas = tk.Canvas(
            diag_card, width=480, height=230,
            bg=Theme.BG_INPUT, highlightthickness=0
        )
        self.neuron_canvas.pack(fill="x", pady=(0, 10))

        # Insight footnote
        tk.Label(
            diag_card,
            text="Insight: The Sigmoid function compresses the linear sum into a probability between 0.0 and 1.0. "
                 "When σ(z) ≥ 0.5, the neuron activates and fires an action potential down its axon.",
            font=("Segoe UI", 8),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED,
            wraplength=460, justify="left"
        ).pack(anchor="w")

        # Initial calculation
        self._calculate_neuron()

        scroll.bind_mousewheel(content)
        return scroll

    def _build_slider_row(self, parent, label_text, var, min_val, max_val, accent_color):
        """Constructs an aligned slider control row with live value label."""
        row = tk.Frame(parent, bg=Theme.BG_CARD)
        row.pack(fill="x", pady=4)

        top_r = tk.Frame(row, bg=Theme.BG_CARD)
        top_r.pack(fill="x")

        tk.Label(top_r, text=label_text, font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        val_lbl = tk.Label(top_r, text=f"{var.get():+.2f}",
                           font=("Consolas", 9, "bold"),
                           bg=Theme.BG_CARD, fg=accent_color)
        val_lbl.pack(side="right")

        def _on_slide(val_str):
            v = float(val_str)
            val_lbl.config(text=f"{v:+.2f}")
            self._calculate_neuron()

        slider = tk.Scale(
            row, from_=min_val, to=max_val, resolution=0.05,
            orient="horizontal", variable=var,
            bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
            troughcolor=Theme.BG_ROOT, activebackground=accent_color,
            highlightthickness=0, bd=0, showvalue=False,
            command=_on_slide
        )
        slider.pack(fill="x", pady=(2, 2))

    def _on_calculate_neuron_clicked(self):
        """Calculates neuron outputs and records execution in AppState."""
        self._calculate_neuron()
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_experiment_run("neural")

    def _load_neural_preset(self, x1, w1, x2, w2, bias):
        self.x1_var.set(x1)
        self.w1_var.set(w1)
        self.x2_var.set(x2)
        self.w2_var.set(w2)
        self.bias_var.set(bias)
        self._calculate_neuron()
        self.neural_status.config(text="Loaded preset parameters.", fg=Theme.CYAN)
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_experiment_run("neural")

    def _reset_neural_defaults(self):
        self._load_neural_preset(0.80, 1.50, 0.60, -1.00, 0.20)
        self.neural_status.config(text="Reset to default baseline parameters.", fg=Theme.TEXT_MUTED)

    def _calculate_neuron(self):
        """Calculates weighted sum and sigmoid output, updating UI & canvas."""
        try:
            x1 = float(self.x1_var.get())
            w1 = float(self.w1_var.get())
            x2 = float(self.x2_var.get())
            w2 = float(self.w2_var.get())
            bias = float(self.bias_var.get())
        except Exception:
            return

        # Linear combination: z = x1*w1 + x2*w2 + b
        z = (x1 * w1) + (x2 * w2) + bias

        # Non-linear activation: sigmoid with overflow guard
        if z < -60.0:
            sig = 0.0
        elif z > 60.0:
            sig = 1.0
        else:
            sig = 1.0 / (1.0 + math.exp(-z))

        is_firing = sig >= 0.5

        # Update text metrics
        self.neural_z_display.config(text=f"{z:+.4f}")
        self.neural_sig_display.config(text=f"{sig:.4f} ({sig*100:.1f}%)")
        if is_firing:
            self.neural_state_display.config(text="● FIRING", fg=Theme.EMERALD)
        else:
            self.neural_state_display.config(text="○ RESTING", fg=Theme.TEXT_MUTED)

        # Update Canvas Diagram
        self._draw_neuron_canvas(x1, w1, x2, w2, bias, z, sig, is_firing)

    def _draw_neuron_canvas(self, x1, w1, x2, w2, bias, z, sig, is_firing):
        """Draws visual architecture of the artificial neuron."""
        c = self.neuron_canvas
        c.delete("all")

        # Dimensions & Coordinates
        w = 480
        h = 230

        # Input Node Positions
        in_a = (65, 65)
        in_b = (65, 165)
        soma = (245, 115)
        axon = (415, 115)

        # 1. Synaptic Lines (Connections from inputs to soma)
        w1_color = Theme.CYAN if w1 >= 0 else Theme.ROSE
        w2_color = Theme.CYAN if w2 >= 0 else Theme.ROSE
        w1_thick = max(1.5, min(5.0, abs(w1)))
        w2_thick = max(1.5, min(5.0, abs(w2)))

        c.create_line(in_a[0] + 24, in_a[1], soma[0] - 42, soma[1] - 12,
                      fill=w1_color, width=w1_thick, smooth=True)
        c.create_line(in_b[0] + 24, in_b[1], soma[0] - 42, soma[1] + 12,
                      fill=w2_color, width=w2_thick, smooth=True)

        # Synapse Weight Pills (labels on wires)
        c.create_rectangle(140, 72, 185, 90, fill=Theme.BG_CARD, outline=Theme.BORDER_MUTED)
        c.create_text(162, 81, text=f"w₁={w1:+.1f}", fill=w1_color, font=("Consolas", 8, "bold"))

        c.create_rectangle(140, 140, 185, 158, fill=Theme.BG_CARD, outline=Theme.BORDER_MUTED)
        c.create_text(162, 149, text=f"w₂={w2:+.1f}", fill=w2_color, font=("Consolas", 8, "bold"))

        # 2. Bias Input Arrow (entering from top)
        c.create_line(soma[0], 25, soma[0], soma[1] - 44, fill=Theme.AMBER, width=2.0, arrow="last")
        c.create_text(soma[0], 15, text=f"Bias b = {bias:+.2f}", fill=Theme.AMBER, font=("Segoe UI", 8, "bold"))

        # 3. Soma (Cell Body / Central Neuron)
        soma_r = 44
        glow_color = Theme.CYAN_BRIGHT if is_firing else Theme.BORDER_MUTED
        fill_color = "#152238" if is_firing else Theme.BG_CARD

        # Outer glowing halo
        if is_firing:
            c.create_oval(soma[0] - soma_r - 4, soma[1] - soma_r - 4,
                          soma[0] + soma_r + 4, soma[1] + soma_r + 4,
                          outline=Theme.CYAN, width=1.5)

        c.create_oval(soma[0] - soma_r, soma[1] - soma_r,
                      soma[0] + soma_r, soma[1] + soma_r,
                      fill=fill_color, outline=glow_color, width=2.5)

        c.create_text(soma[0], soma[1] - 12, text="Σ (Sum)", fill=Theme.TEXT_SECONDARY, font=("Segoe UI", 8, "bold"))
        c.create_text(soma[0], soma[1] + 3, text=f"{z:+.2f}", fill=Theme.TEXT_PRIMARY, font=("Consolas", 10, "bold"))
        c.create_text(soma[0], soma[1] + 20, text="σ(z)", fill=Theme.CYAN_BRIGHT if is_firing else Theme.TEXT_MUTED, font=("Segoe UI", 8, "bold"))

        # 4. Axon Output Wire
        out_thick = 3.5 if is_firing else 1.5
        c.create_line(soma[0] + soma_r, soma[1], axon[0] - 22, axon[1],
                      fill=Theme.EMERALD if is_firing else Theme.TEXT_MUTED, width=out_thick)

        # 5. Input Nodes (Circles on left)
        for (nx, ny), label_title, sym, val in [
            (in_a, "Input A", "x₁", x1),
            (in_b, "Input B", "x₂", x2)
        ]:
            nr = 24
            c.create_oval(nx - nr, ny - nr, nx + nr, ny + nr,
                          fill=Theme.BG_CARD, outline=Theme.CYAN, width=2)
            c.create_text(nx, ny - 6, text=sym, fill=Theme.CYAN_BRIGHT, font=("Segoe UI", 9, "bold"))
            c.create_text(nx, ny + 8, text=f"{val:+.1f}", fill=Theme.TEXT_PRIMARY, font=("Consolas", 8, "bold"))
            c.create_text(nx, ny - nr - 8, text=label_title, fill=Theme.TEXT_MUTED, font=("Segoe UI", 7, "bold"))

        # 6. Output Node (Circle on right)
        ar = 24
        out_color = Theme.EMERALD if is_firing else Theme.BORDER_MUTED
        c.create_oval(axon[0] - ar, axon[1] - ar, axon[0] + ar, axon[1] + ar,
                      fill="#0C251C" if is_firing else Theme.BG_CARD,
                      outline=out_color, width=2.5)
        c.create_text(axon[0], axon[1] - 6, text="Output", fill=Theme.TEXT_PRIMARY, font=("Segoe UI", 8, "bold"))
        c.create_text(axon[0], axon[1] + 8, text=f"{sig:.2f}",
                      fill=Theme.EMERALD if is_firing else Theme.TEXT_MUTED,
                      font=("Consolas", 9, "bold"))
        c.create_text(axon[0], axon[1] - ar - 8, text="σ(z)", fill=Theme.CYAN_BRIGHT if is_firing else Theme.TEXT_MUTED, font=("Segoe UI", 7, "bold"))

    # =========================================================================
    # SUB-VIEW 4: DATA VISUALIZATION LAB (DYNAMIC CANVAS BAR CHART)
    # =========================================================================
    def _create_dataviz_view(self):
        """Builds interactive bar chart data visualization laboratory."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Action Bar: Back to Experiments
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Experiments Overview", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_experiment("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Experiment Lab > Data Science > Interactive Bar Chart",
                              font=("Segoe UI", 9),
                              bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.TEAL,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="📊 DATA SCIENCE & TELEMETRY",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.TEAL,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="Data Visualization Lab: Dynamic Canvas Bar Chart",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="Enter comma-separated numerical values to generate dynamic visual bar charts. "
                 "The Canvas rendering engine dynamically scales the coordinate space and extracts "
                 "foundational statistical metrics: maximum, minimum, average (mean), and sample count.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        # Educational Panel: Bar Charts & Descriptive Statistics
        edu_card = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=22, pady=16)
        edu_card.pack(fill="x", padx=32, pady=(0, 20))

        tk.Label(edu_card, text="📖 Understanding Bar Charts & Descriptive Statistics",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        # 4 concept cards
        concepts_frame = tk.Frame(edu_card, bg=Theme.BG_CARD)
        concepts_frame.pack(fill="x", pady=(0, 12))
        concepts_frame.columnconfigure(0, weight=1)
        concepts_frame.columnconfigure(1, weight=1)
        concepts_frame.columnconfigure(2, weight=1)
        concepts_frame.columnconfigure(3, weight=1)

        c_data = [
            ("What a Bar Chart Is", "A visual display representing numerical data using rectangular bars with heights proportional to values for direct comparison.", Theme.TEAL),
            ("Maximum Value", "The greatest single numerical number in the dataset (max(X)), indicating upper limits and peak performance.", Theme.CYAN_BRIGHT),
            ("Minimum Value", "The smallest single numerical number in the dataset (min(X)), indicating baseline floors and troughs.", Theme.PURPLE_LIGHT),
            ("Average (Mean)", "The arithmetic sum of all numbers divided by count: x̄ = (Σx) / N, revealing the dataset's central tendency.", Theme.EMERALD),
        ]

        for i, (ct, cd, cc) in enumerate(c_data):
            box = tk.Frame(concepts_frame, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=12, pady=10)
            box.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0 if i == 3 else 6), sticky="nsew")

            tk.Label(box, text=f"◈ {ct}", font=("Segoe UI", 9, "bold"),
                     bg=Theme.BG_INPUT, fg=cc).pack(anchor="w")
            tk.Label(box, text=cd, font=("Segoe UI", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                     wraplength=190, justify="left").pack(anchor="w", pady=(3, 0))

        # Formulas & Did You Know Row
        extra_row = tk.Frame(edu_card, bg=Theme.BG_CARD)
        extra_row.pack(fill="x")
        extra_row.columnconfigure(0, weight=5)
        extra_row.columnconfigure(1, weight=5)

        # Left: Statistical Formulas
        stat_box = tk.Frame(extra_row, bg=Theme.BG_INPUT,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=14, pady=10)
        stat_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        tk.Label(stat_box, text="HOW METRICS ARE COMPUTED:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEAL).pack(anchor="w")

        stat_display = (
            "• Maximum = max(x₁, x₂, ..., xₙ)\n"
            "• Minimum = min(x₁, x₂, ..., xₙ)\n"
            "• Average = (x₁ + x₂ + ... + xₙ) / N"
        )
        tk.Label(stat_box, text=stat_display, font=("Consolas", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, justify="left").pack(anchor="w", pady=(4, 0))

        # Right: Did You Know?
        dyk_box = tk.Frame(extra_row, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_MUTED,
                           highlightthickness=1, padx=14, pady=10)
        dyk_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        tk.Label(dyk_box, text="💡 Did You Know?",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.AMBER).pack(anchor="w")

        tk.Label(
            dyk_box,
            text="Scottish engineer William Playfair invented the bar chart and line graph in 1786. "
                 "He discovered that human visual cognition absorbs comparative relationships "
                 "far faster through geometric bar heights than through dense tabular data!",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED,
            wraplength=380, justify="left"
        ).pack(anchor="w", pady=(4, 0))

        # Main Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        # 1. Presets Bar
        presets_bar = tk.Frame(workspace, bg=Theme.BG_CARD)
        presets_bar.pack(fill="x", pady=(0, 12))

        tk.Label(presets_bar, text="Sample Datasets:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 8))

        data_presets = [
            ("Weekly Discoveries", "14, 28, 45, 62, 38, 85, 92"),
            ("Thermal Variance", "18, -12, 35, -24, 48, -15, 62, 5"),
            ("Fibonacci Series", "1, 2, 3, 5, 8, 13, 21, 34, 55"),
            ("Sensor Telemetry", "42, 58, 51, 67, 83, 79, 94, 60, 72"),
            ("Exponential Curve", "2, 4, 8, 16, 32, 64, 128"),
        ]

        for p_name, p_data in data_presets:
            p_lbl = tk.Label(presets_bar, text=f"◈ {p_name}",
                             font=("Segoe UI", 8, "underline"),
                             bg=Theme.BG_CARD, fg=Theme.CYAN, cursor="hand2")
            p_lbl.pack(side="left", padx=(0, 10))
            p_lbl.bind("<Button-1>", lambda _, d=p_data: self._load_dataviz_preset(d))

        # 2. Input Field & Action Buttons
        tk.Label(workspace, text="Enter Comma-Separated Numerical Values:",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        in_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        in_row.pack(fill="x", pady=(0, 14))

        self.dataviz_var = tk.StringVar(value="15, 42, 68, 29, 85, 53, 94, 38, 72")
        self.dataviz_entry = tk.Entry(
            in_row, textvariable=self.dataviz_var,
            bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Consolas", 10),
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1, bd=0, relief="flat"
        )
        self.dataviz_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.dataviz_entry.bind("<Return>", lambda _: self._generate_chart())

        ModernButton(in_row, text="Generate Chart", icon="📊",
                     bg_color=Theme.TEAL,
                     command=self._generate_chart).pack(side="left", padx=(0, 8))

        ModernButton(in_row, text="Add Random Point", icon="➕",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.CYAN,
                     command=self._add_random_point).pack(side="left", padx=(0, 8))

        ModernButton(in_row, text="Clear", icon="🗑️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.ROSE,
                     command=self._clear_chart_data).pack(side="left")

        self.dataviz_status = tk.Label(workspace, text="Ready. Enter values to plot.",
                                       font=("Segoe UI", 8),
                                       bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.dataviz_status.pack(anchor="w", pady=(0, 14))

        # 3. Four Statistics Metric Cards
        stats_frame = tk.Frame(workspace, bg=Theme.BG_CARD)
        stats_frame.pack(fill="x", pady=(0, 18))

        stats_frame.columnconfigure(0, weight=1, uniform="viz")
        stats_frame.columnconfigure(1, weight=1, uniform="viz")
        stats_frame.columnconfigure(2, weight=1, uniform="viz")
        stats_frame.columnconfigure(3, weight=1, uniform="viz")

        # Max Value Card
        m1 = tk.Frame(stats_frame, bg=Theme.BG_INPUT, padx=12, pady=10,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        m1.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        tk.Label(m1, text="▲ Maximum Value", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT).pack(anchor="w")
        self.viz_max_lbl = tk.Label(m1, text="94.0", font=("Consolas", 15, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        self.viz_max_lbl.pack(anchor="w", pady=(4, 0))

        # Min Value Card
        m2 = tk.Frame(stats_frame, bg=Theme.BG_INPUT, padx=12, pady=10,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        m2.grid(row=0, column=1, padx=(6, 6), sticky="nsew")
        tk.Label(m2, text="▼ Minimum Value", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT).pack(anchor="w")
        self.viz_min_lbl = tk.Label(m2, text="15.0", font=("Consolas", 15, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        self.viz_min_lbl.pack(anchor="w", pady=(4, 0))

        # Average Value Card
        m3 = tk.Frame(stats_frame, bg=Theme.BG_INPUT, padx=12, pady=10,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        m3.grid(row=0, column=2, padx=(6, 6), sticky="nsew")
        tk.Label(m3, text="⌀ Average (Mean)", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEAL).pack(anchor="w")
        self.viz_avg_lbl = tk.Label(m3, text="55.11", font=("Consolas", 15, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        self.viz_avg_lbl.pack(anchor="w", pady=(4, 0))

        # Sample Count Card
        m4 = tk.Frame(stats_frame, bg=Theme.BG_INPUT, padx=12, pady=10,
                      highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
        m4.grid(row=0, column=3, padx=(6, 0), sticky="nsew")
        tk.Label(m4, text="◈ Sample Count", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.EMERALD).pack(anchor="w")
        self.viz_count_lbl = tk.Label(m4, text="9 items", font=("Consolas", 15, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        self.viz_count_lbl.pack(anchor="w", pady=(4, 0))

        # 4. Canvas Bar Chart Area
        self.dataviz_canvas = tk.Canvas(
            workspace, height=270,
            bg=Theme.BG_INPUT, highlightthickness=0
        )
        self.dataviz_canvas.pack(fill="x", pady=(0, 10))

        # Generate initial chart
        self.after(50, self._generate_chart)

        scroll.bind_mousewheel(content)
        return scroll

    def _load_dataviz_preset(self, data_str):
        self.dataviz_var.set(data_str)
        self._generate_chart()

    def _clear_chart_data(self):
        """Clears chart data and resets canvas."""
        self.dataviz_var.set("")
        self.viz_max_lbl.config(text="—")
        self.viz_min_lbl.config(text="—")
        self.viz_avg_lbl.config(text="—")
        self.viz_count_lbl.config(text="0 items")
        self.dataviz_status.config(text="Dataset cleared.", fg=Theme.TEXT_MUTED)

        # Clear canvas
        c = self.dataviz_canvas
        c.delete("all")
        w = max(400, c.winfo_width())
        h = max(200, c.winfo_height())
        c.create_text(w / 2, h / 2,
                      text="No data plotted. Enter comma-separated values above and click Generate Chart.",
                      fill=Theme.TEXT_MUTED, font=("Segoe UI", 9))

    def _add_random_point(self):
        """Appends a new random integer to the dataset."""
        new_val = random.randint(10, 100)
        curr = self.dataviz_var.get().strip()
        if curr:
            self.dataviz_var.set(f"{curr}, {new_val}")
        else:
            self.dataviz_var.set(str(new_val))
        self._generate_chart()

    def _generate_chart(self):
        """Parses comma-separated input, calculates statistics, and renders bar chart."""
        raw = self.dataviz_var.get().strip()
        if not raw:
            self.dataviz_status.config(
                text="⚠️ Warning: Input dataset is empty. Please enter comma-separated numbers (e.g. 15, -8, 42).",
                fg=Theme.AMBER
            )
            return

        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        if not tokens:
            self.dataviz_status.config(
                text="⚠️ Warning: No valid numerical items found. Please enter numbers separated by commas.",
                fg=Theme.AMBER
            )
            return

        values = []
        for t in tokens:
            try:
                values.append(float(t))
            except ValueError:
                self.dataviz_status.config(
                    text=f"⚠️ Error: Invalid numerical value '{t}'. Please enter only numbers separated by commas.",
                    fg=Theme.ROSE
                )
                return

        # Calculate Statistics
        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)
        count_val = len(values)

        # Update Statistics Display Cards
        self.viz_max_lbl.config(text=f"{max_val:g}")
        self.viz_min_lbl.config(text=f"{min_val:g}")
        self.viz_avg_lbl.config(text=f"{avg_val:.2f}")
        self.viz_count_lbl.config(text=f"{count_val} items")

        self.dataviz_status.config(
            text=f"✓ Success: Rendered {count_val} data points. Range: [{min_val:g} ... {max_val:g}], Mean: {avg_val:.2f}",
            fg=Theme.EMERALD
        )

        # Render Bar Chart on Canvas
        self._draw_bar_chart(values, max_val, min_val)

        # Record execution in centralized AppState
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.record_experiment_run("dataviz")

    def _draw_bar_chart(self, values, max_val, min_val):
        """Renders responsive bar chart on Canvas with full positive and negative value support."""
        c = self.dataviz_canvas
        c.delete("all")

        # Get canvas dimensions
        w = c.winfo_width()
        if w < 200:
            w = 700
        h = c.winfo_height()
        if h < 150:
            h = 280

        # Margins & Dimensions
        pad_left = 70
        pad_right = 35
        pad_top = 40
        pad_bottom = 45

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Determine Y scale bounds handling positive and negative values
        if min_val >= 0:
            # All positive or zero
            top_y = max_val * 1.18 if max_val > 0 else 10.0
            bottom_y = 0.0
        elif max_val <= 0:
            # All negative
            top_y = 0.0
            bottom_y = min_val * 1.18
        else:
            # Mixed positive and negative
            top_y = max_val * 1.18
            bottom_y = min_val * 1.18

        total_span = top_y - bottom_y
        if total_span <= 0:
            total_span = 10.0

        def val_to_y(v):
            ratio = (top_y - v) / total_span
            return pad_top + ratio * chart_h

        zero_y = val_to_y(0.0)

        # 1. Horizontal Gridlines & Y-Axis Scale Labels
        num_gridlines = 4
        for i in range(num_gridlines + 1):
            ratio = i / num_gridlines
            v_grid = bottom_y + ratio * total_span
            y_pos = val_to_y(v_grid)

            c.create_line(pad_left, y_pos, w - pad_right, y_pos,
                          fill=Theme.BORDER_MUTED, dash=(3, 3))
            c.create_text(pad_left - 8, y_pos,
                          text=f"{v_grid:.1f}",
                          fill=Theme.TEXT_MUTED, font=("Consolas", 8), anchor="e")

        # Draw zero baseline axis line
        c.create_line(pad_left, zero_y, w - pad_right, zero_y,
                      fill=Theme.CYAN if min_val < 0 else Theme.TEXT_MUTED,
                      width=2 if min_val < 0 else 1.5)

        # 2. Draw Bars
        n = len(values)
        slot_width = chart_w / n
        bar_width = max(8.0, min(50.0, slot_width * 0.65))

        for i, val in enumerate(values):
            x_center = pad_left + (i + 0.5) * slot_width
            x1 = x_center - (bar_width / 2)
            x2 = x_center + (bar_width / 2)

            y_val = val_to_y(val)

            if val >= 0:
                y1 = y_val
                y2 = zero_y
                if val == max_val:
                    bar_fill = Theme.CYAN_BRIGHT
                    bar_border = Theme.CYAN
                else:
                    bar_fill = Theme.TEAL if i % 2 == 0 else Theme.BLUE
                    bar_border = Theme.BORDER_GLOW

                c.create_rectangle(x1, y1, x2, y2, fill=bar_fill, outline=bar_border, width=1)
                # Value label above bar
                c.create_text(x_center, max(14, y1 - 10),
                              text=f"{val:g}",
                              fill=Theme.TEXT_PRIMARY if val == max_val else Theme.CYAN_BRIGHT,
                              font=("Segoe UI", 8, "bold"))
            else:
                # Negative bar goes down from zero_y to y_val
                y1 = zero_y
                y2 = y_val
                bar_fill = Theme.ROSE
                bar_border = "#FB7185"

                c.create_rectangle(x1, y1, x2, y2, fill=bar_fill, outline=bar_border, width=1)
                # Value label below bar
                c.create_text(x_center, min(h - 18, y2 + 10),
                              text=f"{val:g}",
                              fill="#FDA4AF",
                              font=("Segoe UI", 8, "bold"))

            # Bottom Index Label
            label_bottom_y = pad_top + chart_h + 16
            c.create_text(x_center, label_bottom_y,
                          text=f"#{i+1}",
                          fill=Theme.TEXT_MUTED, font=("Segoe UI", 8))



# =============================================================================
# 11. MAIN CONTAINER: EXPERIMENT LAB VIEW
# =============================================================================

class ExperimentLabView(tk.Frame):
    """
    Main Experiment Lab container with persistent top sub-navigation bar:
    - ◈ All Experiments (Hub overview)
    - 🔬 My Experiments (User-created experiments directory)
    - 📐 Experiment Builder (5-Step Wizard & Templates)
    - 📈 Results & Visualizer (Interactive sliders, Canvas plots, stats, CSV export)
    - 📜 Run History & Comparison (Multi-run diff table, overlay canvas plot)
    - 📝 Research Discussion & Docs (13 scientific fields, hypothesis verification)
    - ⚡ Built-in Experiments (Caesar Cipher, Single Neuron, DataViz)
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        self.current_tab = "overview"
        self.views = {}
        self.subnav_items = {}

        # 1. Top Sub-navigation Bar
        self._build_top_navbar()

        # 2. View container
        self.content_box = tk.Frame(self, bg=Theme.BG_ROOT)
        self.content_box.pack(fill="both", expand=True)

        # 3. Instantiate Views
        self.views["overview"] = self._build_overview_view()
        self.views["my_experiments"] = MyExperimentsView(
            self.content_box, self.app,
            on_create_callback=lambda: self.switch_tab("builder", new_exp=True),
            on_open_callback=lambda eid: self.switch_tab("results"),
            on_edit_callback=lambda eid: self.switch_tab("builder", edit_id=eid),
            on_history_callback=lambda eid: self.switch_tab("history"),
            on_docs_callback=lambda eid: self.switch_tab("discussion"),
            on_load_template_callback=lambda: self.switch_tab("builder", new_exp=True)
        )
        self.views["builder"] = ExperimentCreationWizard(
            self.content_box, self.app,
            on_save_callback=self._on_builder_save,
            on_cancel_callback=lambda: self.switch_tab("my_experiments")
        )
        self.views["results"] = ExperimentResultsView(
            self.content_box, self.app,
            on_edit_callback=lambda eid: self.switch_tab("builder", edit_id=eid),
            on_history_callback=lambda eid: self.switch_tab("history"),
            on_docs_callback=lambda eid: self.switch_tab("discussion")
        )
        self.views["discussion"] = ExperimentDiscussionView(
            self.content_box, self.app,
            on_back_callback=lambda: self.switch_tab("results")
        )
        self.views["history"] = ExperimentRunHistoryView(
            self.content_box, self.app,
            on_back_callback=lambda: self.switch_tab("results")
        )
        self.views["builtins"] = BuiltInExperimentsView(
            self.content_box, self.app,
            on_back_callback=lambda: self.switch_tab("overview")
        )

        self.switch_tab("overview")

    def _build_top_navbar(self):
        bar = tk.Frame(self, bg=Theme.BG_HEADER,
                       highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1, padx=20, pady=8)
        bar.pack(fill="x", side="top")

        lbl = tk.Label(bar, text="EXPERIMENT LAB:", font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        lbl.pack(side="left", padx=(0, 10))

        tabs = [
            ("overview", "◈ Overview", Theme.BLUE),
            ("my_experiments", "🔬 My Experiments", Theme.EMERALD),
            ("builder", "📐 Experiment Builder", Theme.CYAN),
            ("results", "📈 Results & Visualizer", Theme.BLUE),
            ("history", "📜 Run History", Theme.CYAN),
            ("discussion", "📝 Research Docs", Theme.AMBER),
            ("builtins", "⚡ Built-in Experiments", Theme.PURPLE),
        ]

        for key, title, accent in tabs:
            btn_frame = tk.Frame(bar, bg=Theme.BG_INPUT,
                                 highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, cursor="hand2")
            btn_frame.pack(side="left", padx=(0, 6))

            btn_lbl = tk.Label(btn_frame, text=title, font=("Segoe UI", 9, "bold"),
                               bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=10, pady=5, cursor="hand2")
            btn_lbl.pack()

            for w in (btn_frame, btn_lbl):
                w.bind("<Button-1>", lambda _, k=key: self.switch_tab(k))

            self.subnav_items[key] = {
                "frame": btn_frame,
                "label": btn_lbl,
                "accent": accent
            }

    def switch_tab(self, tab_key, new_exp=False, edit_id=None):
        if tab_key not in self.views and tab_key not in ("encryption", "neural", "dataviz"):
            return

        # Special routing for built-in shortcuts
        if tab_key in ("encryption", "neural", "dataviz"):
            self.views["builtins"].switch_builtin(tab_key)
            tab_key = "builtins"

        # Rebuild builder if needed
        if tab_key == "builder":
            if new_exp:
                self.views["builder"].pack_forget()
                self.views["builder"].destroy()
                self.views["builder"] = ExperimentCreationWizard(
                    self.content_box, self.app, experiment_id=None,
                    on_save_callback=self._on_builder_save,
                    on_cancel_callback=lambda: self.switch_tab("my_experiments")
                )
            elif edit_id:
                self.views["builder"].pack_forget()
                self.views["builder"].destroy()
                self.views["builder"] = ExperimentCreationWizard(
                    self.content_box, self.app, experiment_id=edit_id,
                    on_save_callback=self._on_builder_save,
                    on_cancel_callback=lambda: self.switch_tab("my_experiments")
                )

        prev = self.current_tab
        self.current_tab = tab_key

        # Update styling
        for k, item in self.subnav_items.items():
            if k == tab_key:
                item["frame"].config(bg=Theme.BG_CARD_HOVER, highlightbackground=item["accent"])
                item["label"].config(bg=Theme.BG_CARD_HOVER, fg=item["accent"])
            else:
                item["frame"].config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
                item["label"].config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

        # Show view
        self.views[tab_key].pack(fill="both", expand=True)
        if prev and prev != tab_key and prev in self.views:
            self.views[prev].pack_forget()

        # Refresh state on tab switch
        if tab_key == "my_experiments":
            self.views["my_experiments"].refresh_list()
        elif tab_key == "results":
            self.views["results"].refresh_active_experiment()
        elif tab_key == "discussion":
            self.views["discussion"].refresh_active_experiment()
        elif tab_key == "history":
            self.views["history"].refresh_active_experiment()

    def _on_builder_save(self, exp_id, run_immediately=False):
        if run_immediately:
            self.switch_tab("results")
        else:
            self.switch_tab("my_experiments")

    def _build_overview_view(self):
        """Builds the comprehensive Experiment Lab overview hub."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        c = scroll.scrollable_content

        # 1. Hero Banner
        hero = tk.Frame(c, bg=Theme.BG_CARD_ELEVATED, highlightbackground=Theme.BORDER_MUTED,
                        highlightthickness=1, padx=30, pady=22)
        hero.pack(fill="x", padx=32, pady=(20, 16))

        tk.Label(hero, text="◈  EXPERIMENT LAB  •  ALGORITHMIC SANDBOX & CUSTOM BUILDER",
                 font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                 padx=8, pady=3).pack(anchor="w")

        tk.Label(hero, text="Experiment Lab & Research Sandbox",
                 font=("Segoe UI", 24, "bold"), bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(10, 4))

        tk.Label(hero,
                 text="Design mathematical models, execute simulations, analyze results, compare historical runs, and document research findings.",
                 font=("Segoe UI", 11), bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY).pack(anchor="w")

        tk.Label(
            hero,
            text="Stage 7 transforms the Experiment Lab into a full scientific creation environment. "
                 "In addition to preserving the Caesar Cipher, Artificial Neuron, and Data Visualization tools, "
                 "you can now construct custom experiments using our secure AST mathematical engine (no eval/exec), "
                 "interactively adjust parameters with live sliders, compare run divergence, and document 13-field research logs.",
            font=("Segoe UI", 9), bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED,
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 14))

        # Quick action buttons inside hero
        act_row = tk.Frame(hero, bg=Theme.BG_CARD_ELEVATED)
        act_row.pack(anchor="w")

        ModernButton(act_row, text="Create Experiment", icon="➕", bg_color=Theme.BLUE,
                     font=("Segoe UI", 9, "bold"), padx=12, pady=6,
                     command=lambda: self.switch_tab("builder", new_exp=True)).pack(side="left", padx=(0, 8))

        ModernButton(act_row, text="Explore My Experiments", icon="🔬", bg_color=Theme.BG_INPUT,
                     text_color=Theme.EMERALD, font=("Segoe UI", 9, "bold"), padx=12, pady=6,
                     command=lambda: self.switch_tab("my_experiments")).pack(side="left", padx=(0, 8))

        ModernButton(act_row, text="Built-in Demonstrations", icon="⚡", bg_color=Theme.BG_INPUT,
                     text_color=Theme.PURPLE_LIGHT, font=("Segoe UI", 9, "bold"), padx=12, pady=6,
                     command=lambda: self.switch_tab("builtins")).pack(side="left")

        # 2. Section: Two Main Hub Columns (My Experiments vs Built-in)
        grid_sec = tk.Frame(c, bg=Theme.BG_ROOT)
        grid_sec.pack(fill="x", padx=32, pady=(0, 20))
        grid_sec.columnconfigure(0, weight=1, uniform="hub")
        grid_sec.columnconfigure(1, weight=1, uniform="hub")

        # Column A: My Experiments Section
        card_a = tk.Frame(grid_sec, bg=Theme.BG_CARD, padx=20, pady=18,
                          highlightbackground=Theme.EMERALD, highlightthickness=1)
        card_a.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(card_a, text="🔬 MY EXPERIMENTS (CUSTOM BUILDER)", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.EMERALD, padx=6, pady=2).pack(anchor="w")
        tk.Label(card_a, text="User Experiment Environment", font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))
        tk.Label(card_a,
                 text="Formulate custom mathematical equations (AST parsed, zero eval/exec), configure parameter ranges, "
                      "upload CSV datasets, execute simulations, view line and scatter plots, and draft 13-field scientific documentation.",
                 font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=380, justify="left").pack(anchor="w", pady=(0, 12))

        ModernButton(card_a, text="Open My Experiments", icon="🔬", bg_color=Theme.EMERALD,
                     hover_color="#059669", font=("Segoe UI", 9, "bold"),
                     command=lambda: self.switch_tab("my_experiments")).pack(fill="x")

        # Column B: Built-in Experiments Section
        card_b = tk.Frame(grid_sec, bg=Theme.BG_CARD, padx=20, pady=18,
                          highlightbackground=Theme.PURPLE, highlightthickness=1)
        card_b.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(card_b, text="⚡ BUILT-IN EXPERIMENTS (PRESERVED)", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT, padx=6, pady=2).pack(anchor="w")
        tk.Label(card_b, text="Algorithmic Demonstrations", font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))
        tk.Label(card_b,
                 text="Explore the 3 original CurioLab interactive demonstrations: Caesar Cipher modular encryption, "
                      "Single Artificial Neuron perceptron activation, and Dynamic Data Visualization bar chart.",
                 font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=380, justify="left").pack(anchor="w", pady=(0, 12))

        ModernButton(card_b, text="Launch Built-in Demonstrations", icon="⚡", bg_color=Theme.PURPLE,
                     hover_color="#7C3AED", font=("Segoe UI", 9, "bold"),
                     command=lambda: self.switch_tab("builtins")).pack(fill="x")

        # 3. Educational Templates Spotlight
        tpl_sec = tk.Frame(c, bg=Theme.BG_CARD, padx=20, pady=16,
                           highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        tpl_sec.pack(fill="x", padx=32, pady=(0, 24))

        tk.Label(tpl_sec, text="📚 8 Pre-Engineered Educational Templates Available",
                 font=("Segoe UI", 11, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))
        tk.Label(tpl_sec,
                 text="Includes Linear Sensitivity, Exponential Growth, Logistic Carrying Capacity, Sigmoid Activation, "
                      "Gradient Descent Steps, Perceptron Sums, F1-Score Harmonic Trade-offs, and Image Thresholding.",
                 font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))

        tpl_row = tk.Frame(tpl_sec, bg=Theme.BG_CARD)
        tpl_row.pack(fill="x")

        for t_name, t_eq in [
            ("Linear Function", "y = m*x + c"),
            ("Logistic Growth", "y = K/(1 + exp(-r*(t-t0)))"),
            ("Sigmoid Unit", "y = 1/(1 + exp(-z))"),
            ("Gradient Step", "y = x - alpha*(2*x)")
        ]:
            chip = tk.Frame(tpl_row, bg=Theme.BG_INPUT, padx=10, pady=6,
                            highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            chip.pack(side="left", padx=(0, 8))
            tk.Label(chip, text=t_name, font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(anchor="w")
            tk.Label(chip, text=t_eq, font=("Consolas", 7), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(anchor="w")

        return scroll
