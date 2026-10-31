"""
CurioLab — Settings & Laboratory Configuration Module
=====================================================
Interactive settings interface for workspace aesthetics, system preferences,
and local in-memory data management.

Features:
- Theme selection (Deep Obsidian, Cyber Violet, Quantum Cyan, Solar Amber).
- Primary accent color customization with live swatch feedback.
- Application preferences (default landing page, sort order, journal defaults).
- Destructive reset operations with safety confirmation dialogs.
- Centralized AppState synchronization and observer notifications.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from theme import Theme


class SettingsView(tk.Frame):
    """
    Settings and laboratory configuration view.
    Manages appearance, application preferences, and local data controls.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # State tracking variables
        self.theme_var = tk.StringVar(value="Deep Obsidian")
        self.accent_var = tk.StringVar(value="#06B6D4")
        self.scale_var = tk.StringVar(value="Standard (100%)")
        self.landing_var = tk.StringVar(value="Discovery Hub")
        self.sort_var = tk.StringVar(value="Title (A-Z)")
        self.journal_type_var = tk.StringVar(value="Hypothesis")
        self.journal_status_var = tk.StringVar(value="Formulated")
        self.confirm_delete_var = tk.BooleanVar(value=True)
        self.galaxy_particles_var = tk.BooleanVar(value=True)

        # Load existing preferences from AppState if available
        self._load_preferences_from_state()

        # Build UI layout inside a scrollable canvas
        self._build_layout()

        # Subscribe to AppState observer
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

    def _load_preferences_from_state(self):
        """Initializes variables from AppState.preferences."""
        if hasattr(self.app, "state") and self.app.state and hasattr(self.app.state, "preferences"):
            p = self.app.state.preferences
            self.theme_var.set(p.get("theme_name", "Deep Obsidian"))
            self.accent_var.set(p.get("accent_color", "#06B6D4"))
            self.scale_var.set(p.get("ui_scale", "Standard (100%)"))
            self.landing_var.set(p.get("default_landing_page", "Discovery Hub"))
            self.sort_var.set(p.get("preferred_resource_sort", "Title (A-Z)"))
            self.journal_type_var.set(p.get("journal_default_type", "Hypothesis"))
            self.journal_status_var.set(p.get("journal_default_status", "Formulated"))
            self.confirm_delete_var.set(p.get("confirm_delete_journal", True))
            self.galaxy_particles_var.set(p.get("galaxy_show_particles", True))

    def _build_layout(self):
        """Constructs the scrollable settings page layout."""
        # Top Header & Hero
        self._build_header(self)

        # Scrollable container for settings sections
        container = tk.Frame(self, bg=Theme.BG_ROOT)
        container.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        self.canvas = tk.Canvas(container, bg=Theme.BG_ROOT, highlightthickness=0, yscrollincrement=1)
        self.canvas._is_curiolab_scroll_canvas = True
        self.vbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.content = tk.Frame(self.canvas, bg=Theme.BG_ROOT)
        self.canvas_win = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))

        # 1. Appearance Section
        self._build_appearance_section(self.content)

        # 2. Application Preferences Section
        self._build_preferences_section(self.content)

        # 3. Application Data Controls Section
        self._build_data_controls_section(self.content)

        # 4. Action Bar (Apply / Restore)
        self._build_action_bar(self.content)

    # -------------------------------------------------------------------------
    # HEADER & HERO BANNER
    # -------------------------------------------------------------------------
    def _build_header(self, parent):
        top_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 6))

        breadcrumb = tk.Label(
            top_bar,
            text="Settings > Laboratory Configuration & Local Storage",
            font=("Segoe UI", 9),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED
        )
        breadcrumb.pack(side="left")

        hero = tk.Frame(
            parent,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.AMBER,
            highlightthickness=1,
            padx=24,
            pady=12
        )
        hero.pack(fill="x", padx=32, pady=(0, 12))

        tag = tk.Label(
            hero,
            text="⚙️ SYSTEM CONFIGURATION • WORKSPACE PARAMETERS & LOCAL CONTROLS",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.AMBER,
            padx=8,
            pady=3
        )
        tag.pack(anchor="w")

        title_lbl = tk.Label(
            hero,
            text="Settings & Laboratory Configuration",
            font=("Segoe UI", 18, "bold"),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w", pady=(4, 2))

        desc_lbl = tk.Label(
            hero,
            text="Configure workspace aesthetics, default module landing behavior, research notebook parameters, "
                 "and local simulation state. CurioLab runs 100% locally in-memory with zero external tracking or cloud persistence.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_SECONDARY,
            wraplength=980,
            justify="left"
        )
        desc_lbl.pack(anchor="w")

    # -------------------------------------------------------------------------
    # SECTION 1: APPEARANCE SETTINGS
    # -------------------------------------------------------------------------
    def _build_appearance_section(self, parent):
        card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            padx=24,
            pady=18
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card,
            text="🎨 Appearance & Visual Aesthetics",
            font=("Segoe UI", 13, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card,
            text="Customize the dark futuristic laboratory theme and primary visual accent colors.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 14))

        # A. Theme Preset Selector
        theme_row = tk.Frame(card, bg=Theme.BG_CARD)
        theme_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            theme_row,
            text="Laboratory Theme:",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            width=20,
            anchor="w"
        ).pack(side="left")

        themes = list(Theme.THEMES.keys())
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Settings.TCombobox",
                        fieldbackground=Theme.BG_INPUT,
                        background=Theme.BG_CARD,
                        foreground=Theme.TEXT_PRIMARY,
                        arrowcolor=Theme.CYAN,
                        bordercolor=Theme.BORDER_MUTED)

        self.theme_combo = ttk.Combobox(
            theme_row,
            textvariable=self.theme_var,
            values=themes,
            state="readonly",
            width=24,
            style="Settings.TCombobox"
        )
        self.theme_combo.pack(side="left", padx=(0, 16))
        self.theme_combo.bind("<<ComboboxSelected>>", lambda _: self._update_live_preview())

        # B. Primary Accent Color
        accent_row = tk.Frame(card, bg=Theme.BG_CARD)
        accent_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            accent_row,
            text="Primary Accent Color:",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            width=20,
            anchor="w"
        ).pack(side="left")

        # Color chips for quick accent selection
        chips_frame = tk.Frame(accent_row, bg=Theme.BG_CARD)
        chips_frame.pack(side="left")

        for name, hex_code in Theme.ACCENT_PRESETS.items():
            chip = tk.Frame(
                chips_frame,
                bg=hex_code,
                width=24,
                height=24,
                cursor="hand2",
                highlightbackground="#FFFFFF",
                highlightthickness=1
            )
            chip.pack(side="left", padx=(0, 8))
            chip.pack_propagate(False)

            # Bind click to select accent
            chip.bind("<Button-1>", lambda _, c=hex_code: self._select_accent_chip(c))

            # Tooltip simulated by label
            chip_lbl = tk.Label(chip, text="", bg=hex_code, cursor="hand2")
            chip_lbl.pack(fill="both", expand=True)
            chip_lbl.bind("<Button-1>", lambda _, c=hex_code: self._select_accent_chip(c))

        self.accent_lbl = tk.Label(
            accent_row,
            text=f"Selected: {self.accent_var.get()}",
            font=("Segoe UI", 8, "italic"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        )
        self.accent_lbl.pack(side="left", padx=(10, 0))

        # C. UI Scale & Typography Preference
        scale_row = tk.Frame(card, bg=Theme.BG_CARD)
        scale_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            scale_row,
            text="Display Density & Scale:",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            width=20,
            anchor="w"
        ).pack(side="left")

        scale_combo = ttk.Combobox(
            scale_row,
            textvariable=self.scale_var,
            values=["Compact (90%)", "Standard (100%)", "Large (115%)"],
            state="readonly",
            width=24,
            style="Settings.TCombobox"
        )
        scale_combo.pack(side="left")

        # D. Live Palette Preview Swatch
        self.preview_box = tk.Frame(
            card,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        self.preview_box.pack(fill="x", pady=(6, 0))

        self.preview_title = tk.Label(
            self.preview_box,
            text="◈ Palette Preview: Active Theme Profile",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_INPUT,
            fg=self.accent_var.get()
        )
        self.preview_title.pack(anchor="w")

        self.preview_text = tk.Label(
            self.preview_box,
            text="Deep obsidian surfaces paired with vibrant luminescent accents ensure maximum contrast and visual focus for scientific inquiry.",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_SECONDARY,
            wraplength=640,
            justify="left"
        )
        self.preview_text.pack(anchor="w", pady=(2, 0))

    def _select_accent_chip(self, hex_code):
        self.accent_var.set(hex_code)
        self.accent_lbl.config(text=f"Selected: {hex_code}")
        self._update_live_preview()

    def _update_live_preview(self):
        accent = self.accent_var.get()
        self.preview_title.config(fg=accent)

    # -------------------------------------------------------------------------
    # SECTION 2: APPLICATION PREFERENCES
    # -------------------------------------------------------------------------
    def _build_preferences_section(self, parent):
        card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            padx=24,
            pady=18
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card,
            text="⚡ Laboratory Preferences",
            font=("Segoe UI", 13, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card,
            text="Configure startup navigation, default catalog ordering, and notebook behaviors.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 14))

        grid = tk.Frame(card, bg=Theme.BG_CARD)
        grid.pack(fill="x")

        # 1. Default Landing Page
        tk.Label(grid, text="Default Landing Page:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=6)
        pages = [
            "Discovery Hub", "Experiment Lab", "Research Detective",
            "Knowledge Library", "Research Galaxy", "Discovery Journal"
        ]
        p_combo = ttk.Combobox(grid, textvariable=self.landing_var, values=pages, state="readonly", width=22, style="Settings.TCombobox")
        p_combo.grid(row=0, column=1, sticky="w", padx=(10, 30), pady=6)

        # 2. Preferred Library Sorting
        tk.Label(grid, text="Preferred Monograph Sort:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).grid(row=0, column=2, sticky="w", pady=6)
        sorts = ["Title (A-Z)", "Title (Z-A)", "Curriculum Year (Newest)", "Curriculum Year (Oldest)"]
        s_combo = ttk.Combobox(grid, textvariable=self.sort_var, values=sorts, state="readonly", width=22, style="Settings.TCombobox")
        s_combo.grid(row=0, column=3, sticky="w", padx=(10, 0), pady=6)

        # 3. Journal Default Entry Type
        tk.Label(grid, text="Journal Default Type:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).grid(row=1, column=0, sticky="w", pady=6)
        types = ["Hypothesis", "Research Question", "Research Idea", "Experiment Log", "Observation", "Literature Note", "Finding"]
        t_combo = ttk.Combobox(grid, textvariable=self.journal_type_var, values=types, state="readonly", width=22, style="Settings.TCombobox")
        t_combo.grid(row=1, column=1, sticky="w", padx=(10, 30), pady=6)

        # 4. Journal Default Status
        tk.Label(grid, text="Journal Default Status:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).grid(row=1, column=2, sticky="w", pady=6)
        statuses = ["Formulated", "Testing", "Verified", "Refuted"]
        st_combo = ttk.Combobox(grid, textvariable=self.journal_status_var, values=statuses, state="readonly", width=22, style="Settings.TCombobox")
        st_combo.grid(row=1, column=3, sticky="w", padx=(10, 0), pady=6)

        # Checkboxes for confirmation dialogs & galaxy visuals
        chk_box = tk.Frame(card, bg=Theme.BG_CARD)
        chk_box.pack(fill="x", pady=(12, 0))

        c1 = tk.Checkbutton(
            chk_box,
            text="Confirm before deleting journal records",
            variable=self.confirm_delete_var,
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            selectcolor=Theme.BG_INPUT,
            activebackground=Theme.BG_CARD,
            activeforeground=Theme.CYAN
        )
        c1.pack(anchor="w", pady=2)

        c2 = tk.Checkbutton(
            chk_box,
            text="Show celestial background star particles in Research Galaxy",
            variable=self.galaxy_particles_var,
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            selectcolor=Theme.BG_INPUT,
            activebackground=Theme.BG_CARD,
            activeforeground=Theme.CYAN
        )
        c2.pack(anchor="w", pady=2)

    # -------------------------------------------------------------------------
    # SECTION 3: APPLICATION DATA CONTROLS (RESET OPERATIONS)
    # -------------------------------------------------------------------------
    def _build_data_controls_section(self, parent):
        card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            padx=24,
            pady=18
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card,
            text="🛡️ Local In-Memory Data Controls",
            font=("Segoe UI", 13, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 4))

        warn_box = tk.Frame(
            card,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=14,
            pady=8
        )
        warn_box.pack(fill="x", pady=(0, 14))

        tk.Label(
            warn_box,
            text="⚠️ In-Memory State Notice: CurioLab runs locally without an external database. "
                 "The actions below restore initial demonstration states. Every operation requires confirmation.",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT,
            fg=Theme.AMBER,
            wraplength=640,
            justify="left"
        ).pack(anchor="w")

        # Grid of reset operations
        btn_grid = tk.Frame(card, bg=Theme.BG_CARD)
        btn_grid.pack(fill="x")

        def make_reset_row(row_idx, title, desc, action_fn, btn_color=Theme.BG_INPUT, text_color=Theme.TEXT_PRIMARY):
            f = tk.Frame(btn_grid, bg=Theme.BG_CARD)
            f.pack(fill="x", pady=6)

            info = tk.Frame(f, bg=Theme.BG_CARD)
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=title, font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
            tk.Label(info, text=desc, font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")

            btn = tk.Label(
                f,
                text=" Reset ",
                font=("Segoe UI", 8, "bold"),
                bg=btn_color,
                fg=text_color,
                highlightbackground=Theme.BORDER_MUTED,
                highlightthickness=1,
                padx=12,
                pady=4,
                cursor="hand2"
            )
            btn.pack(side="right")
            btn.bind("<Button-1>", lambda _: action_fn())

        make_reset_row(
            0,
            "Reset Knowledge Library Bookmarks",
            "Clears user-added bookmarks and restores baseline demonstration favorites.",
            self._confirm_reset_bookmarks
        )
        make_reset_row(
            1,
            "Reset Discovery Journal Records",
            "Restores the 4 initial demonstration hypotheses and clears custom research entries.",
            self._confirm_reset_journal
        )
        make_reset_row(
            2,
            "Reset Experiment Telemetry",
            "Clears execution run counters for Caesar cipher, Single Neuron, and Data Visualizer.",
            self._confirm_reset_experiments
        )
        make_reset_row(
            3,
            "Reset Research Detective Progress",
            "Resets detective score to 0 and clears solved case dossiers.",
            self._confirm_reset_detective
        )
        make_reset_row(
            4,
            "Reset All Laboratory Data",
            "Restores complete application state to pristine educational baseline.",
            self._confirm_reset_all,
            btn_color=Theme.ROSE,
            text_color="#FFFFFF"
        )

    # -------------------------------------------------------------------------
    # RESET HANDLERS WITH CONFIRMATION DIALOGS
    # -------------------------------------------------------------------------
    def _confirm_reset_bookmarks(self):
        if messagebox.askyesno(
            "Confirm Reset Bookmarks",
            "Are you sure you want to restore Knowledge Library bookmarks to default demonstration settings?",
            parent=self
        ):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.reset_bookmarks()
                messagebox.showinfo("Reset Complete", "Knowledge Library bookmarks have been reset.", parent=self)

    def _confirm_reset_journal(self):
        if messagebox.askyesno(
            "Confirm Reset Journal",
            "Are you sure you want to reset Discovery Journal records to baseline demonstration entries?\n\nCustom notes will be cleared.",
            parent=self
        ):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.reset_journal_entries()
                messagebox.showinfo("Reset Complete", "Discovery Journal records have been restored to baseline.", parent=self)

    def _confirm_reset_experiments(self):
        if messagebox.askyesno(
            "Confirm Reset Telemetry",
            "Reset all experiment execution counters to zero?",
            parent=self
        ):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.reset_experiment_runs()
                messagebox.showinfo("Reset Complete", "Experiment counters reset to zero.", parent=self)

    def _confirm_reset_detective(self):
        if messagebox.askyesno(
            "Confirm Reset Detective",
            "Reset all investigative progress and reset researcher score to 0?",
            parent=self
        ):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.reset_detective_progress()
                messagebox.showinfo("Reset Complete", "Research Detective progress reset to zero.", parent=self)

    def _confirm_reset_all(self):
        if messagebox.askyesno(
            "⚠️ Confirm Complete Laboratory Reset",
            "This will reset all journal entries, bookmarks, scores, telemetry counters, and user preferences back to initial demonstration defaults.\n\nProceed with full laboratory reset?",
            parent=self
        ):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.reset_all_data()
                self._load_preferences_from_state()
                messagebox.showinfo("Reset Complete", "All CurioLab modules restored to initial state.", parent=self)

    # -------------------------------------------------------------------------
    # SECTION 4: ACTION BAR (APPLY / RESTORE)
    # -------------------------------------------------------------------------
    def _build_action_bar(self, parent):
        act_box = tk.Frame(parent, bg=Theme.BG_ROOT)
        act_box.pack(fill="x", pady=(4, 24))

        apply_btn = tk.Label(
            act_box,
            text=" 💾 Apply Preferences & Theme ",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.CYAN,
            fg=Theme.BG_ROOT,
            padx=16,
            pady=8,
            cursor="hand2"
        )
        apply_btn.pack(side="left", padx=(0, 10))
        apply_btn.bind("<Button-1>", lambda _: self.apply_preferences())

        restore_btn = tk.Label(
            act_box,
            text=" ↺ Restore Default Preferences ",
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        restore_btn.pack(side="left", padx=(0, 14))
        restore_btn.bind("<Button-1>", lambda _: self.restore_defaults())

        self.feedback_lbl = tk.Label(
            act_box,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_ROOT,
            fg=Theme.EMERALD
        )
        self.feedback_lbl.pack(side="left")

    def apply_preferences(self):
        """Saves current form inputs into AppState and updates active theme."""
        theme_name = self.theme_var.get()
        accent = self.accent_var.get()

        # Update Theme tokens
        Theme.apply_theme(theme_name, accent)

        # Commit to AppState
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.update_preferences(
                theme_name=theme_name,
                accent_color=accent,
                ui_scale=self.scale_var.get(),
                default_landing_page=self.landing_var.get(),
                preferred_resource_sort=self.sort_var.get(),
                journal_default_type=self.journal_type_var.get(),
                journal_default_status=self.journal_status_var.get(),
                confirm_delete_journal=self.confirm_delete_var.get(),
                galaxy_show_particles=self.galaxy_particles_var.get()
            )

        self.feedback_lbl.config(text="✓ Preferences and theme applied successfully!", fg=Theme.EMERALD)
        self.after(3000, lambda: self.feedback_lbl.config(text=""))

    def restore_defaults(self):
        """Restores preference controls to factory defaults."""
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.reset_preferences()
            self._load_preferences_from_state()
            Theme.apply_theme("Deep Obsidian", "#06B6D4")

        self.feedback_lbl.config(text="↺ Default preferences restored.", fg=Theme.CYAN)
        self.after(3000, lambda: self.feedback_lbl.config(text=""))

    def _on_app_state_changed(self):
        """Observer callback."""
        self._load_preferences_from_state()
