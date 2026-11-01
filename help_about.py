"""
CurioLab — Help & About Module
==============================
Comprehensive offline user guide, module operations manual,
keyboard shortcuts reference, and platform mission dossier.

Features:
- Category navigation (Platform Overview, Module Guides, Shortcuts, About).
- Comprehensive operational walkthroughs for all 6 core laboratory modules.
- Accurately verified keyboard shortcuts table.
- CurioLab architecture specifications and educational integrity disclaimer.
"""

import tkinter as tk
from tkinter import ttk
from theme import Theme


class HelpAboutView(tk.Frame):
    """
    Help & About information center.
    Provides in-depth educational documentation for every module.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Active documentation topic tracking
        self.active_topic = "overview"
        self.nav_buttons = {}

        # Build UI layout
        self._build_header(self)
        self._build_workspace(self)

    # -------------------------------------------------------------------------
    # HEADER & HERO BANNER
    # -------------------------------------------------------------------------
    def _build_header(self, parent):
        top_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 6))

        breadcrumb = tk.Label(
            top_bar,
            text="Help & About > Documentation & Specifications",
            font=("Segoe UI", 9),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED
        )
        breadcrumb.pack(side="left")

        hero = tk.Frame(
            parent,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.CYAN_BRIGHT,
            highlightthickness=1,
            padx=24,
            pady=12
        )
        hero.pack(fill="x", padx=32, pady=(0, 12))

        tag = tk.Label(
            hero,
            text="📖 DOCUMENTATION & ABOUT • OPERATIONAL MANUAL & PLATFORM SPECIFICATIONS",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.CYAN_BRIGHT,
            padx=8,
            pady=3
        )
        tag.pack(anchor="w")

        title_lbl = tk.Label(
            hero,
            text="CurioLab Help Center & Platform Dossier",
            font=("Segoe UI", 18, "bold"),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w", pady=(4, 2))

        desc_lbl = tk.Label(
            hero,
            text="Learn how to navigate CurioLab's interactive research modules, conduct simulations, "
                 "investigate forensic evidence, explore connected concept graphs, and document your discoveries. "
                 "Built 100% with standard Python 3 and Tkinter.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_SECONDARY,
            wraplength=980,
            justify="left"
        )
        desc_lbl.pack(anchor="w")

    # -------------------------------------------------------------------------
    # WORKSPACE LAYOUT (SIDEBAR TABS + RICH CONTENT READER)
    # -------------------------------------------------------------------------
    def _build_workspace(self, parent):
        workspace = tk.Frame(parent, bg=Theme.BG_ROOT)
        workspace.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        # Left Column: Category Navigation List
        nav_card = tk.Frame(
            workspace,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            width=260
        )
        nav_card.pack(side="left", fill="y", padx=(0, 14))
        nav_card.pack_propagate(False)

        tk.Label(
            nav_card,
            text="Documentation Index",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            padx=16,
            pady=12
        ).pack(anchor="w")

        topics = [
            ("overview", "🌟 Platform Overview", "Introduction & Architecture"),
            ("hub", "🧭 Discovery Hub", "Dashboard & Metrics"),
            ("experiments", "⚗️ Experiment Lab", "Simulations & Protocols"),
            ("detective", "🔍 Research Detective", "Scientific Investigation Workspace"),
            ("library", "📚 Knowledge Library", "Monographs & Citations"),
            ("galaxy", "🌌 Research Galaxy", "Constellations & Bridges"),
            ("journal", "📓 Discovery Journal", "Hypotheses & Notes"),
            ("shortcuts", "⌨️ Keyboard Shortcuts", "Hotkeys & Navigation"),
            ("about", "ℹ️ About & Credits", "Mission & Specifications")
        ]

        for topic_id, title, sub in topics:
            btn_frame = tk.Frame(nav_card, bg=Theme.BG_CARD, cursor="hand2", padx=12, pady=8)
            btn_frame.pack(fill="x")

            lbl_title = tk.Label(
                btn_frame,
                text=title,
                font=("Segoe UI", 9, "bold"),
                bg=Theme.BG_CARD,
                fg=Theme.TEXT_SECONDARY,
                anchor="w"
            )
            lbl_title.pack(fill="x")

            lbl_sub = tk.Label(
                btn_frame,
                text=sub,
                font=("Segoe UI", 7),
                bg=Theme.BG_CARD,
                fg=Theme.TEXT_MUTED,
                anchor="w"
            )
            lbl_sub.pack(fill="x")

            self.nav_buttons[topic_id] = {
                "frame": btn_frame,
                "title": lbl_title,
                "sub": lbl_sub
            }

            for w in (btn_frame, lbl_title, lbl_sub):
                w.bind("<Button-1>", lambda _, t=topic_id: self.show_topic(t))

        # Right Column: Scrollable Content Reader
        content_card = tk.Frame(
            workspace,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1
        )
        content_card.pack(side="right", fill="both", expand=True)

        self.reader_canvas = tk.Canvas(content_card, bg=Theme.BG_CARD, highlightthickness=0, yscrollincrement=1)
        self.reader_canvas._is_curiolab_scroll_canvas = True
        self.reader_vbar = ttk.Scrollbar(content_card, orient="vertical", command=self.reader_canvas.yview)
        self.reader_canvas.configure(yscrollcommand=self.reader_vbar.set)

        self.reader_content = tk.Frame(self.reader_canvas, bg=Theme.BG_CARD)
        self.reader_win = self.reader_canvas.create_window((0, 0), window=self.reader_content, anchor="nw")

        self.reader_canvas.pack(side="left", fill="both", expand=True)
        self.reader_vbar.pack(side="right", fill="y")

        self.reader_content.bind("<Configure>", lambda e: self.reader_canvas.configure(scrollregion=self.reader_canvas.bbox("all")))
        self.reader_canvas.bind("<Configure>", lambda e: self.reader_canvas.itemconfig(self.reader_win, width=e.width))

        # Display default topic
        self.show_topic("overview")

    # -------------------------------------------------------------------------
    # TOPIC SWITCHER & RENDERING
    # -------------------------------------------------------------------------
    def show_topic(self, topic_id):
        """Switches active topic in the documentation reader."""
        self.active_topic = topic_id

        # Update sidebar highlighting
        for tid, btn in self.nav_buttons.items():
            if tid == topic_id:
                btn["frame"].config(bg=Theme.BG_INPUT)
                btn["title"].config(bg=Theme.BG_INPUT, fg=Theme.CYAN)
                btn["sub"].config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)
            else:
                btn["frame"].config(bg=Theme.BG_CARD)
                btn["title"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY)
                btn["sub"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)

        # Clear reader area
        for child in self.reader_content.winfo_children():
            child.destroy()

        # Render selected topic
        render_method = getattr(self, f"_render_{topic_id}", self._render_overview)
        render_method()

        self.reader_canvas.yview_moveto(0)

    # -------------------------------------------------------------------------
    # TOPIC CONTENT BUILDERS
    # -------------------------------------------------------------------------
    def _add_section_header(self, title, subtitle, icon="◈", accent=Theme.CYAN):
        top = tk.Frame(self.reader_content, bg=Theme.BG_CARD, padx=28, pady=16)
        top.pack(fill="x")

        tk.Label(
            top,
            text=f"{icon} {title}",
            font=("Segoe UI", 16, "bold"),
            bg=Theme.BG_CARD,
            fg=accent
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                top,
                text=subtitle,
                font=("Segoe UI", 9),
                bg=Theme.BG_CARD,
                fg=Theme.TEXT_SECONDARY
            ).pack(anchor="w", pady=(2, 0))

        tk.Frame(self.reader_content, bg=Theme.BORDER_SUBTLE, height=1).pack(fill="x", padx=28, pady=(0, 14))

    def _add_guide_card(self, title, desc, details=None, icon="●", accent=Theme.CYAN):
        card = tk.Frame(
            self.reader_content,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=16,
            pady=12
        )
        card.pack(fill="x", padx=28, pady=(0, 12))

        header = tk.Frame(card, bg=Theme.BG_INPUT)
        header.pack(fill="x")

        tk.Label(header, text=icon, font=("Segoe UI", 10), bg=Theme.BG_INPUT, fg=accent).pack(side="left", padx=(0, 8))
        tk.Label(header, text=title, font=("Segoe UI", 11, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).pack(side="left")

        tk.Label(
            card,
            text=desc,
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_SECONDARY,
            wraplength=640,
            justify="left"
        ).pack(anchor="w", pady=(6, 4))

        if details:
            for item_title, item_desc in details:
                row = tk.Frame(card, bg=Theme.BG_INPUT)
                row.pack(fill="x", pady=2)
                tk.Label(row, text="•", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=accent).pack(side="left", anchor="n", padx=(6, 6))
                t_lbl = tk.Label(row, text=f"{item_title}: ", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
                t_lbl.pack(side="left", anchor="n")
                d_lbl = tk.Label(row, text=item_desc, font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, wraplength=520, justify="left")
                d_lbl.pack(side="left", anchor="n")

    # 1. Platform Overview
    def _render_overview(self):
        self._add_section_header("Platform Overview & Architecture", "Interactive Research & Discovery Platform v1.0.0", "🌟")
        self._add_guide_card(
            "What is CurioLab?",
            "CurioLab is an interactive scientific research and discovery platform built purely in standard Python 3 and Tkinter. "
            "It unites computational experiments, investigative reasoning, curated theoretical monographs, interactive concept mapping, "
            "and personal research notebooks into a single cohesive desktop application.",
            [
                ("Zero External Dependencies", "Runs directly on standard Python with standard Tkinter — no web servers, node runtimes, or databases required."),
                ("In-Memory State Engine", "Centralized AppState coordinates all shared data structures with a real-time Observer subscription bus."),
                ("Local Privacy & Offline Operation", "All data remains on your local machine; zero telemetry or tracking is transmitted.")
            ]
        )
        self._add_guide_card(
            "The 8 Laboratory Modules",
            "CurioLab is organized into eight integrated scientific modules accessible via the persistent left navigation sidebar:",
            [
                ("1. Discovery Hub", "Real-time dashboard overview with dynamic curriculum metrics, recent activity, and entropy generator."),
                ("2. Experiment Lab", "Interactive laboratory simulations in cryptography, neural computing, and statistical visualization."),
                ("3. Research Detective", "Interactive scientific investigation environment: dataset exploration, anomaly auditing, statistical trap analysis, and pattern discovery across connected stages."),
                ("4. Knowledge Library", "Curated multidisciplinary demonstration monographs with live search, filtering, and citation transfer."),
                ("5. Research Galaxy", "Interactive knowledge constellation mapping concept relationships across 8 scientific domains."),
                ("6. Discovery Journal", "Digital research notebook with 5-card dashboard, full CRUD lifecycle, and hypothesis tracking."),
                ("7. Settings", "Workspace parameter configuration, custom dark theme presets, and local data controls."),
                ("8. Help & About", "Complete offline operating manual, verified keyboard shortcuts, and platform specifications.")
            ]
        )

    # 2. Discovery Hub
    def _render_hub(self):
        self._add_section_header("Discovery Hub Guide", "Laboratory Overview & Real-Time Research Intel", "🧭")
        self._add_guide_card(
            "Dashboard Metrics & Statistics",
            "The Discovery Hub features four dynamically computed metrics derived directly from AppState in real time:",
            [
                ("Total Experiments Run", "Sum of executions recorded across Caesar Cipher, Single Neuron Playground, and Data Visualizer."),
                ("Investigation Stages", "Number of completed scientific investigation stages out of the 7 connected stages."),
                ("Curated Library Monograph Count", "Total active educational demonstration monographs available in Knowledge Library."),
                ("Verified Journal Hypotheses", "Count of personal research entries transitioned to the 'Verified' hypothesis stage.")
            ]
        )
        self._add_guide_card(
            "Today's Curiosity: Quantum Entropy Generator",
            "An interactive entropy simulation that models quantum state fluctuations. Click 'Generate New Curiosity' to trigger a simulated vacuum wave fluctuation and uncover a serendipitous multidisciplinary research prompt."
        )

    # 3. Experiment Lab
    def _render_experiments(self):
        self._add_section_header("Experiment Lab Guide", "Interactive Computing, Mathematics & Data Simulations", "⚗️")
        self._add_guide_card(
            "Caesar Substitution Cipher & Attack Tool",
            "Explore modular arithmetic in classical cryptography. Enter plaintext and select a shift key from 0 to 25 to encrypt in real time. "
            "Use the automated frequency analysis attack tool to inspect English letter distribution and break intercepted ciphertexts.",
            [
                ("Input Parameters", "Plaintext input box, shift slider (0-25), mode selection (Encrypt/Decrypt)."),
                ("Attack Analysis", "Computes chi-squared deviation against standard English letter frequencies to recover unknown keys.")
            ]
        )
        self._add_guide_card(
            "Single-Neuron Activation Playground",
            "Simulate artificial dendritic computation using McCulloch-Pitts neuron models and continuous sigmoid squashing functions.",
            [
                ("Weights & Bias", "Tune input weights w1, w2 and bias threshold b to observe linear decision boundary shifts."),
                ("Minsky-Papert XOR Limit", "Demonstrates the mathematical impossibility of separating non-linear XOR coordinates using a single linear hyperplane.")
            ]
        )
        self._add_guide_card(
            "Interactive Data Visualizer",
            "Simulates multi-frequency wave packet superposition with Gaussian noise injection. Plot and inspect amplitude distributions across time-series samples."
        )

    # 4. Research Detective
    def _render_detective(self):
        self._add_section_header("Research Detective Guide", "Scientific Investigation Workspace & Empirical Auditing", "🔍")
        self._add_guide_card(
            "Scientific Investigation Workspaces",
            "Four integrated investigation environments designed for authentic empirical analysis and quantitative deduction:",
            [
                ("Detective Map", "Interactive 7-stage connected investigation pipeline: Research Question, Evidence Collection, Dataset Exploration, Analysis, Observations, Hypothesis, and Conclusion."),
                ("Data Detective", "Import CSV datasets, validate records, compute descriptive statistics, configure IQR outlier and Z-score anomaly bounds, and highlight normal vs flagged points."),
                ("Statistical Trap", "Audit misleading statistics, the accuracy paradox under class imbalance, confusion matrix metrics (Precision, Recall, F1), mean vs median skew, and correlation vs causation."),
                ("Pattern Mystery", "Explore bivariate patterns, fit linear regression trendlines (y = mx + b), calculate Pearson's r and R², and uncover unusual high-residual observations.")
            ]
        )
        self._add_guide_card(
            "Discussion-Based Scientific Workflow & Journal Transfer",
            "Replace quiz answering with genuine scientific documentation. Formulate testable hypotheses, record observations in response to guided inquiry prompts, and stage completed investigation dossiers directly into the Discovery Journal."
        )

    # 5. Knowledge Library
    def _render_library(self):
        self._add_section_header("Knowledge Library Guide", "Educational Monograph Repository & Citation Flow", "📚")
        self._add_guide_card(
            "Search, Filter & Monograph Inspection",
            "Browse 10 educational demonstration monographs across 8 scientific disciplines with live keyword filtering, domain dropdowns, and curriculum level tags.",
            [
                ("Search Bar", "Live query matching title, curator, abstract, and study notes."),
                ("Bookmarking", "Click the star icon to curate an active study list. Toggle 'Bookmarked Only' to view your favorites."),
                ("Monograph Viewer", "Inspect demonstration abstracts, theoretical equations, key concepts, and curriculum synthesis notes.")
            ]
        )
        self._add_guide_card(
            "Citation Transfer Flow ('Cite in Journal ➔')",
            "Clicking 'Cite in Journal' generates a standardized educational reference containing the record identifier, curator, year, domain, and theoretical equation. "
            "It automatically navigates to the Discovery Journal and stages the citation into the notebook editor for student review and saving."
        )

    # 6. Research Galaxy
    def _render_galaxy(self):
        self._add_section_header("Research Galaxy Guide", "Connected Knowledge Constellation & Epistemic Bridges", "🌌")
        self._add_guide_card(
            "Constellation Map & Visual Aesthetics",
            "An interactive Tkinter Canvas knowledge graph featuring 18 scientific concepts across 8 domains and 18 epistemic relationship bridges.",
            [
                ("Interactive Nodes", "Click any node to highlight active connections and display deep educational explanations in the Concept Inspector."),
                ("Pan & Zoom Navigation", "Click and drag background to pan smoothly. Use '+', '-', 'Reset View', or mouse wheel to zoom in and out."),
                ("Targeted Centering", "Click '🎯 Center' in the inspector to smoothly reposition the canvas view onto the selected concept.")
            ]
        )
        self._add_guide_card(
            "Cross-Module Integrations",
            "Research Galaxy connects directly with the rest of CurioLab:",
            [
                ("Open in Library ➔", "Directly opens the corresponding curriculum monograph in Knowledge Library."),
                ("Add to Discovery Journal ➔", "Transfers concept definitions, research questions, and connected disciplines into a new journal draft.")
            ]
        )

    # 7. Discovery Journal
    def _render_journal(self):
        self._add_section_header("Discovery Journal Guide", "Personal Scientific Notebook & Hypothesis Dossier", "📓")
        self._add_guide_card(
            "5-Card Dynamic Dashboard",
            "Tracks the complete lifecycle of your scientific inquiries: Total Entries, Formulated, Under Testing, Verified, and Refuted. "
            "All statistics derive directly from in-memory AppState."
        )
        self._add_guide_card(
            "Hypothesis Progression Workflow",
            "Every research entry supports transition between 4 progression stages: Formulated ➔ Testing ➔ Verified / Refuted.",
            [
                ("Educational Notice", "Verification status represents the student's recorded conclusion in this educational laboratory, not external scientific peer review.")
            ]
        )
        self._add_guide_card(
            "CRUD Operations & Inbound Drafts",
            "Create new entries, view dossiers, edit previously saved records, duplicate entries with a single click, or safely delete records with confirmation. "
            "Seamlessly receives citation drafts from Knowledge Library and concept drafts from Research Galaxy."
        )

    # 8. Keyboard Shortcuts
    def _render_shortcuts(self):
        self._add_section_header("Verified Keyboard Shortcuts", "Verified & Working Hotkeys in CurioLab", "⌨️")
        card = tk.Frame(
            self.reader_content,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=16,
            pady=12
        )
        card.pack(fill="x", padx=28, pady=(0, 12))

        shortcuts = [
            ("Ctrl+1  /  Cmd+1", "Discovery Hub", "Switches to main overview dashboard"),
            ("Ctrl+2  /  Cmd+2", "Experiment Lab", "Navigates to interactive simulations"),
            ("Ctrl+3  /  Cmd+3", "Research Detective", "Opens investigative challenges"),
            ("Ctrl+4  /  Cmd+4", "Knowledge Library", "Opens monograph catalog"),
            ("Ctrl+5  /  Cmd+5", "Research Galaxy", "Opens concept constellation"),
            ("Ctrl+6  /  Cmd+6", "Discovery Journal", "Opens research notebook"),
            ("Ctrl+7  /  Cmd+7", "Settings", "Opens laboratory configuration"),
            ("Ctrl+8  /  Cmd+8", "Help & About", "Opens documentation and user guide"),
            ("Ctrl+F  /  Cmd+F", "Global Search", "Focuses top header search field"),
            ("Enter", "Execute Search", "Runs global federated query across all modules"),
            ("Esc", "Dismiss / Focus Out", "Dismisses active dropdowns and search")
        ]

        # Table Header
        h_row = tk.Frame(card, bg=Theme.BG_INPUT)
        h_row.pack(fill="x", pady=(0, 6))
        tk.Label(h_row, text="Shortcut Key", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN, width=18, anchor="w").pack(side="left")
        tk.Label(h_row, text="Target Action", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, width=22, anchor="w").pack(side="left")
        tk.Label(h_row, text="Description", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, anchor="w").pack(side="left")

        tk.Frame(card, bg=Theme.BORDER_MUTED, height=1).pack(fill="x", pady=(2, 6))

        for key, act, desc in shortcuts:
            row = tk.Frame(card, bg=Theme.BG_INPUT)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=key, font=("Consolas", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN, width=18, anchor="w", padx=4).pack(side="left")
            tk.Label(row, text=act, font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, width=22, anchor="w").pack(side="left")
            tk.Label(row, text=desc, font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, anchor="w").pack(side="left")

    # 9. About & Credits
    def _render_about(self):
        self._add_section_header("About CurioLab & Platform Dossier", "Desktop Core v1.0.0 (Research & Education Edition)", "ℹ️")
        self._add_guide_card(
            "Core Specifications",
            "CurioLab is engineered as a clean, portable desktop platform designed to eliminate web bloat, cloud dependencies, and telemetry.",
            [
                ("Platform Core", "CurioLab Desktop Core v1.0.0 (Research & Education Edition)"),
                ("Implementation Language", "Standard Python 3.10+ with Tkinter GUI Engine"),
                ("Storage & State Architecture", "Zero external database / 100% offline in-memory AppState Observer model"),
                ("Hardware Acceleration", "High-DPI crisp rendering on macOS and Windows with native Tk canvas graphics")
            ]
        )
        self._add_guide_card(
            "Educational Integrity Disclaimer",
            "CurioLab is an interactive learning platform designed for local educational simulation and discovery. "
            "All scientific monographs, author labels, citation records, and relationship graphs contained herein are strictly "
            "educational demonstration models. They do NOT represent or fabricate real-world peer-reviewed publications, "
            "living authors, DOI identifiers, or academic metrics."
        )
        self._add_guide_card(
            "Inspirations & Acknowledgements",
            "CurioLab is inspired by the open scientific spirit and legacy of pioneering polymaths: "
            "Richard Feynman (intuitive visualization), Claude Shannon (information entropy), "
            "Ada Lovelace (algorithmic universality), Alan Turing (computational patterns), "
            "and Marie Curie (rigorous empirical inquiry). Developed for curious minds, students, and polymaths."
        )
