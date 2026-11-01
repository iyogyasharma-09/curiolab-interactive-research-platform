#!/usr/bin/env python3
"""
Visual verification script for CurioLab Stage 7 Experiment Lab.
Launches the full GUI application, switches through all Experiment Lab tabs,
triggers execution and plotting, and captures visual canvas outputs to artifacts.
"""

import tkinter as tk
import time
import os
import subprocess
from main import CurioLabApp

artifact_dir = "/Users/yogyasharma/.gemini/antigravity-ide/brain/65f6e117-4953-431b-ad84-a29d0f4e8df1"

root = tk.Tk()
root.title("CurioLab Stage 7 Visual Verification")
root.geometry("1400x900")
root.update_idletasks()

app = CurioLabApp(root)
root.update()

# 1. Navigate to Experiment Lab
app.navigate_to("Experiment Lab")
root.update()

exp_lab = app.pages["Experiment Lab"]

results_log = []

# 2. Inspect Overview
exp_lab.switch_tab("overview")
root.update()
time.sleep(0.1)
results_log.append("✓ Overview Tab loaded and rendered")

# 3. Inspect My Experiments
exp_lab.switch_tab("my_experiments")
root.update()
time.sleep(0.1)
cards_count = len(exp_lab.views["my_experiments"].cards_container.winfo_children())
results_log.append(f"✓ My Experiments Tab rendered with {cards_count} experiment cards")

# 4. Inspect Experiment Builder (Wizard)
exp_lab.switch_tab("builder", new_exp=True)
root.update()
time.sleep(0.1)
results_log.append("✓ Experiment Builder Step 1 rendered")

# Advance through wizard steps
wizard = exp_lab.views["builder"]
wizard._show_step(2)
root.update()
results_log.append("✓ Experiment Builder Step 2 (Math Model & Equation Validator) rendered")

wizard._show_step(3)
root.update()
results_log.append("✓ Experiment Builder Step 3 (Parameter Configuration) rendered")

wizard._show_step(4)
root.update()
results_log.append("✓ Experiment Builder Step 4 (Input Data & CSV Upload) rendered")

wizard._show_step(5)
root.update()
results_log.append("✓ Experiment Builder Step 5 (Execution Configuration) rendered")

# 5. Inspect Results & Visualizer
exp_lab.switch_tab("results")
root.update()
results_view = exp_lab.views["results"]
results_view.execute_and_plot()
root.update()

# Save postscript of the active plot canvas
ps_plot_path = os.path.join(artifact_dir, "experiment_plot_canvas.ps")
results_view.plot_canvas.postscript(file=ps_plot_path, colormode="color")
results_log.append(f"✓ Results Tab executed and plotted. Canvas exported to {ps_plot_path}")

# 6. Inspect Run History & Multi-Run Overlay
exp_lab.switch_tab("history")
root.update()
history_view = exp_lab.views["history"]
history_view._select_all_runs()
root.update()

ps_comp_path = os.path.join(artifact_dir, "experiment_comparison_canvas.ps")
history_view.comp_canvas.postscript(file=ps_comp_path, colormode="color")
results_log.append(f"✓ Run History Tab rendered with overlay comparison. Canvas exported to {ps_comp_path}")

# 7. Inspect Research Documentation (13 fields)
exp_lab.switch_tab("discussion")
root.update()
disc_view = exp_lab.views["discussion"]
results_log.append(f"✓ Research Documentation Tab rendered with all {len(disc_view.FIELDS)} scientific fields and hypothesis status selector")

# 8. Inspect Built-in Experiments
exp_lab.switch_tab("builtins")
root.update()
builtins_view = exp_lab.views["builtins"]

builtins_view.switch_builtin("encryption")
root.update()
results_log.append("✓ Built-in Caesar Cipher Playground rendered")

builtins_view.switch_builtin("neural")
root.update()
results_log.append("✓ Built-in Single Artificial Neuron Simulator rendered")

builtins_view.switch_builtin("dataviz")
root.update()
results_log.append("✓ Built-in Data Visualization Lab rendered")

# Try to capture full window screenshot using macOS screencapture if possible
png_path = os.path.join(artifact_dir, "stage7_experiment_lab_full_window.png")
try:
    # Use screencapture
    subprocess.run(["screencapture", "-o", "-m", png_path], timeout=3, check=False)
    if os.path.exists(png_path):
        results_log.append(f"✓ Full application window screenshot captured to {png_path}")
except Exception as e:
    results_log.append(f"Screenshot note: {e}")

root.destroy()

print("\n".join(results_log))
print("\nALL VISUAL INSPECTIONS COMPLETED SUCCESSFULLY!")
