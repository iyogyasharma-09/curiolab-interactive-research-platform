"""
CurioLab — Discovery Journal Module
===================================
Interactive research notebook with complete CRUD functionality,
dynamic AppState dashboard metrics, hypothesis tracking workflow,
multi-criteria search and filtering, and integration with Knowledge Library
citations and Research Galaxy concepts.

CONTENT INTEGRITY NOTICE:
All hypotheses, experiment logs, and journal entries are personal educational
study records. Verification statuses indicate the user's recorded conclusion
within local simulations, not external scientific peer review.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from theme import Theme


STATUS_COLORS = {
    "Formulated": {"accent": "#94A3B8", "bg": "#1E2638", "icon": "⚪"},
    "Testing": {"accent": "#38BDF8", "bg": "#0C2738", "icon": "🔵"},
    "Verified": {"accent": "#10B981", "bg": "#0B2E1E", "icon": "🟢"},
    "Refuted": {"accent": "#F43F5E", "bg": "#33121A", "icon": "🔴"},
}

TYPE_COLORS = {
    "Research Idea": "#A78BFA",
    "Research Question": "#38BDF8",
    "Hypothesis": "#06B6D4",
    "Experiment Log": "#F59E0B",
    "Observation": "#10B981",
    "Literature Note": "#EC4899",
    "Finding": "#6366F1"
}


class DiscoveryJournalView(tk.Frame):
    """
    Complete interactive scientific research notebook for CurioLab.
    Provides dashboard statistics, full entry CRUD, hypothesis workflows,
    and draft transfer receiver.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Filtering & Search State
        self.search_var = tk.StringVar()
        self.domain_filter_var = tk.StringVar(value="All Domains")
        self.type_filter_var = tk.StringVar(value="All Types")
        self.status_filter_var = tk.StringVar(value="All Statuses")
        self.sort_var = tk.StringVar(value="Newest First")

        # Active Entry Selection & Editor State
        self.selected_entry_id = None
        self.editor_mode = False          # True when showing Editor, False when showing Explorer
        self.editing_entry_id = None      # ID if updating existing, None if creating new
        self.draft_source_info = None     # Metadata if editing pending draft

        # Form Editor Variables
        self.form_title_var = tk.StringVar()
        self.form_domain_var = tk.StringVar(value="General")
        self.form_type_var = tk.StringVar(value="Hypothesis")
        self.form_status_var = tk.StringVar(value="Formulated")
        self.form_tags_var = tk.StringVar()

        # Backward compatibility aliases for Stage 2 citation transfer flow
        self.title_var = self.form_title_var
        self.domain_var = self.form_domain_var
        self.status_var = self.form_status_var
        self.tags_var = self.form_tags_var
        self.text_widgets = {}

        # Build UI Structure
        self._build_header(self)
        self._build_stats_dashboard(self)
        self._build_toolbar(self)

        # Main Workspace Container (swaps between Explorer and Editor)
        self.workspace_frame = tk.Frame(self, bg=Theme.BG_ROOT)
        self.workspace_frame.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        # Explorer Mode Containers
        self.explorer_frame = tk.Frame(self.workspace_frame, bg=Theme.BG_ROOT)
        self.editor_frame = tk.Frame(self.workspace_frame, bg=Theme.BG_ROOT)

        self._build_explorer_layout(self.explorer_frame)
        self._build_editor_layout(self.editor_frame)

        # Show Explorer by default
        self.explorer_frame.pack(fill="both", expand=True)

        # Subscribe to AppState observer
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

        # Initial data refresh
        self._refresh_dashboard()
        self._refresh_entries_list()
        self._select_first_available_entry()

    # -------------------------------------------------------------------------
    # HEADER & HERO BANNER
    # -------------------------------------------------------------------------
    def _build_header(self, parent):
        top_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 6))

        breadcrumb = tk.Label(
            top_bar,
            text="Discovery Journal > Research Notebook & Hypothesis Dossier",
            font=("Segoe UI", 9),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED
        )
        breadcrumb.pack(side="left")

        hero = tk.Frame(
            parent,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.EMERALD,
            highlightthickness=1,
            padx=24,
            pady=12
        )
        hero.pack(fill="x", padx=32, pady=(0, 10))

        tag = tk.Label(
            hero,
            text="📓 RESEARCH NOTEBOOK • HYPOTHESIS FORMULATION & VERIFICATION WORKSPACE",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.EMERALD,
            padx=8,
            pady=3
        )
        tag.pack(anchor="w")

        title_lbl = tk.Label(
            hero,
            text="Discovery Journal: Personal Scientific Notebook",
            font=("Segoe UI", 18, "bold"),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w", pady=(4, 2))

        desc_lbl = tk.Label(
            hero,
            text="Record questions, formulate testable hypotheses, document experimental protocols, "
                 "and synthesize empirical findings. Track the lifecycle of your scientific inquiries from "
                 "initial conjecture to verification.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_SECONDARY,
            wraplength=980,
            justify="left"
        )
        desc_lbl.pack(anchor="w")

    # -------------------------------------------------------------------------
    # DYNAMIC DASHBOARD METRICS (5 CARDS)
    # -------------------------------------------------------------------------
    def _build_stats_dashboard(self, parent):
        self.stats_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        self.stats_bar.pack(fill="x", padx=32, pady=(0, 10))

        # We will hold reference to value labels to update dynamically
        self.stat_val_labels = {}

        metrics_def = [
            ("total_entries", "Total Entries", "All records", Theme.CYAN, "📚"),
            ("formulated", "Formulated", "Hypotheses staged", "#94A3B8", "⚪"),
            ("testing", "Testing", "Active experiments", "#38BDF8", "🔵"),
            ("verified", "Verified", "Conclusions supported", "#10B981", "🟢"),
            ("refuted", "Refuted", "Premises disproven", "#F43F5E", "🔴")
        ]

        for key, title, sub, color, icon in metrics_def:
            card = tk.Frame(
                self.stats_bar,
                bg=Theme.BG_CARD,
                highlightbackground=Theme.BORDER_SUBTLE,
                highlightthickness=1,
                padx=14,
                pady=10
            )
            card.pack(side="left", fill="x", expand=True, padx=(0, 8 if key != "refuted" else 0))

            top_row = tk.Frame(card, bg=Theme.BG_CARD)
            top_row.pack(fill="x")

            tk.Label(top_row, text=icon, font=("Segoe UI", 11), bg=Theme.BG_CARD).pack(side="left", padx=(0, 6))
            tk.Label(top_row, text=title, font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")

            val_lbl = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 18, "bold"),
                bg=Theme.BG_CARD,
                fg=color
            )
            val_lbl.pack(anchor="w", pady=(2, 0))
            self.stat_val_labels[key] = val_lbl

            tk.Label(
                card,
                text=sub,
                font=("Segoe UI", 7),
                bg=Theme.BG_CARD,
                fg=Theme.TEXT_MUTED
            ).pack(anchor="w")

    def _refresh_dashboard(self):
        """Derives all 5 metrics dynamically from AppState. Never uses hardcoded values."""
        if not hasattr(self.app, "state") or not self.app.state:
            return

        stats = self.app.state.get_journal_stats()
        for key, lbl in self.stat_val_labels.items():
            lbl.config(text=str(stats.get(key, 0)))

    # -------------------------------------------------------------------------
    # FILTER & ACTION TOOLBAR
    # -------------------------------------------------------------------------
    def _build_toolbar(self, parent):
        ctrl_bar = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            padx=16,
            pady=8
        )
        ctrl_bar.pack(fill="x", padx=32, pady=(0, 10))

        # 1. Search Box
        search_box = tk.Frame(
            ctrl_bar,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=10,
            pady=4
        )
        search_box.pack(side="left", padx=(0, 10))

        tk.Label(search_box, text="🔍", font=("Segoe UI", 10), bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            relief="flat",
            width=20
        )
        self.search_entry.pack(side="left")
        self.search_var.trace_add("write", lambda *_: self._on_filter_changed())

        clear_s = tk.Label(search_box, text="✕", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, cursor="hand2")
        clear_s.pack(side="left", padx=(4, 0))
        clear_s.bind("<Button-1>", lambda _: self.search_var.set(""))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Journal.TCombobox",
                        fieldbackground=Theme.BG_INPUT,
                        background=Theme.BG_CARD,
                        foreground=Theme.TEXT_PRIMARY,
                        arrowcolor=Theme.CYAN,
                        bordercolor=Theme.BORDER_MUTED)

        # 2. Domain Filter
        tk.Label(ctrl_bar, text="Domain:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        domains = ["All Domains", "Quantum Physics", "Artificial Intelligence", "Neuroscience",
                   "Information Theory", "Computer Vision", "Cybersecurity", "Complexity Science", "Mathematics", "General"]
        self.domain_combo = ttk.Combobox(ctrl_bar, textvariable=self.domain_filter_var, values=domains,
                                         state="readonly", width=14, style="Journal.TCombobox")
        self.domain_combo.pack(side="left", padx=(0, 8))
        self.domain_combo.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 3. Type Filter
        tk.Label(ctrl_bar, text="Type:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        types = ["All Types", "Research Idea", "Research Question", "Hypothesis", "Experiment Log", "Observation", "Literature Note", "Finding"]
        self.type_combo = ttk.Combobox(ctrl_bar, textvariable=self.type_filter_var, values=types,
                                       state="readonly", width=13, style="Journal.TCombobox")
        self.type_combo.pack(side="left", padx=(0, 8))
        self.type_combo.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 4. Status Filter
        tk.Label(ctrl_bar, text="Status:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        statuses = ["All Statuses", "Formulated", "Testing", "Verified", "Refuted"]
        self.status_combo = ttk.Combobox(ctrl_bar, textvariable=self.status_filter_var, values=statuses,
                                         state="readonly", width=11, style="Journal.TCombobox")
        self.status_combo.pack(side="left", padx=(0, 8))
        self.status_combo.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 5. Sort Dropdown
        tk.Label(ctrl_bar, text="Sort:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        sorts = ["Newest First", "Oldest First", "Title (A-Z)", "Status"]
        self.sort_combo = ttk.Combobox(ctrl_bar, textvariable=self.sort_var, values=sorts,
                                       state="readonly", width=11, style="Journal.TCombobox")
        self.sort_combo.pack(side="left", padx=(0, 10))
        self.sort_combo.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 6. Reset Filters Button
        reset_b = tk.Label(
            ctrl_bar,
            text=" ↺ Reset ",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        reset_b.pack(side="left")
        reset_b.bind("<Button-1>", lambda _: self.reset_filters())

        # 7. Action Button: + New Entry
        new_btn = tk.Label(
            ctrl_bar,
            text=" ➕ New Research Entry ",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.EMERALD,
            fg=Theme.BG_ROOT,
            padx=12,
            pady=5,
            cursor="hand2"
        )
        new_btn.pack(side="right")
        new_btn.bind("<Button-1>", lambda _: self.open_new_entry_editor())

    def reset_filters(self):
        self.search_var.set("")
        self.domain_filter_var.set("All Domains")
        self.type_filter_var.set("All Types")
        self.status_filter_var.set("All Statuses")
        self.sort_var.set("Newest First")
        self._refresh_entries_list()

    def _on_filter_changed(self):
        self._refresh_entries_list()

    # -------------------------------------------------------------------------
    # EXPLORER LAYOUT (LEFT LIST + RIGHT DETAIL INSPECTOR)
    # -------------------------------------------------------------------------
    def _build_explorer_layout(self, parent):
        # Left Column: Scrollable Entry Card List
        self.list_card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            width=430
        )
        self.list_card.pack(side="left", fill="both", padx=(0, 12))
        self.list_card.pack_propagate(False)

        list_header = tk.Frame(self.list_card, bg=Theme.BG_CARD, padx=14, pady=10)
        list_header.pack(fill="x")

        self.list_count_lbl = tk.Label(
            list_header,
            text="Saved Entries (0)",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        )
        self.list_count_lbl.pack(side="left")

        # Scrollable area for cards
        self.list_canvas = tk.Canvas(self.list_card, bg=Theme.BG_CARD, highlightthickness=0, yscrollincrement=1)
        self.list_canvas._is_curiolab_scroll_canvas = True
        self.list_vbar = ttk.Scrollbar(self.list_card, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.list_vbar.set)

        self.list_container = tk.Frame(self.list_canvas, bg=Theme.BG_CARD)
        self.list_win_id = self.list_canvas.create_window((0, 0), window=self.list_container, anchor="nw")

        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_vbar.pack(side="right", fill="y")

        self.list_container.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(self.list_win_id, width=e.width))

        # Right Column: Entry Detail Inspector
        self.detail_card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1
        )
        self.detail_card.pack(side="right", fill="both", expand=True)

        self.detail_canvas = tk.Canvas(self.detail_card, bg=Theme.BG_CARD, highlightthickness=0, yscrollincrement=1)
        self.detail_canvas._is_curiolab_scroll_canvas = True
        self.detail_vbar = ttk.Scrollbar(self.detail_card, orient="vertical", command=self.detail_canvas.yview)
        self.detail_canvas.configure(yscrollcommand=self.detail_vbar.set)

        self.detail_container = tk.Frame(self.detail_canvas, bg=Theme.BG_CARD)
        self.detail_win_id = self.detail_canvas.create_window((0, 0), window=self.detail_container, anchor="nw")

        self.detail_canvas.pack(side="left", fill="both", expand=True)
        self.detail_vbar.pack(side="right", fill="y")

        self.detail_container.bind("<Configure>", lambda e: self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all")))
        self.detail_canvas.bind("<Configure>", self._on_detail_canvas_configure)

    def _on_detail_canvas_configure(self, event):
        self.detail_canvas.itemconfig(self.detail_win_id, width=event.width)
        avail = max(280, event.width - 56)
        for lbl in getattr(self, "detail_wrap_labels", []):
            try:
                lbl.config(wraplength=avail)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # FILTERED ENTRY QUERY & SORTING
    # -------------------------------------------------------------------------
    def _get_filtered_entries(self):
        if not hasattr(self.app, "state") or not self.app.state:
            return []

        entries = list(self.app.state.journal_entries)
        q = self.search_var.get().strip().lower()
        d_filter = self.domain_filter_var.get()
        t_filter = self.type_filter_var.get()
        s_filter = self.status_filter_var.get()

        res = []
        for e in entries:
            # Domain filter
            if d_filter != "All Domains" and e.get("domain") != d_filter:
                continue
            # Type filter
            if t_filter != "All Types" and e.get("entry_type") != t_filter:
                continue
            # Status filter
            if s_filter != "All Statuses" and e.get("status") != s_filter:
                continue
            # Search query (matches title, questions, hypotheses, observations, results, conclusion, tags)
            if q:
                search_corpus = (
                    f"{e.get('title', '')} {e.get('domain', '')} {e.get('entry_type', '')} "
                    f"{e.get('research_question', '')} {e.get('hypothesis', '')} "
                    f"{e.get('observations', '')} {e.get('results', '')} "
                    f"{e.get('conclusion', '')} {e.get('tags', '')} {e.get('body', '')}"
                ).lower()
                if q not in search_corpus:
                    continue
            res.append(e)

        # Sorting
        sort_mode = self.sort_var.get()
        if sort_mode == "Newest First":
            res.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        elif sort_mode == "Oldest First":
            res.sort(key=lambda x: x.get("timestamp", ""))
        elif sort_mode == "Title (A-Z)":
            res.sort(key=lambda x: x.get("title", "").lower())
        elif sort_mode == "Status":
            order = {"Formulated": 1, "Testing": 2, "Verified": 3, "Refuted": 4}
            res.sort(key=lambda x: order.get(x.get("status", "Formulated"), 5))

        return res

    # -------------------------------------------------------------------------
    # REFRESH ENTRIES LIST (CARDS)
    # -------------------------------------------------------------------------
    def _refresh_entries_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        entries = self._get_filtered_entries()
        self.list_count_lbl.config(text=f"Saved Entries ({len(entries)})")

        if not entries:
            empty_card = tk.Frame(self.list_container, bg=Theme.BG_INPUT, padx=16, pady=24)
            empty_card.pack(fill="x", padx=12, pady=12)

            tk.Label(empty_card, text="📓 No Entries Found", font=("Segoe UI", 11, "bold"),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack(anchor="w")
            tk.Label(empty_card, text="No journal records match the active search and filter parameters.",
                     font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, wraplength=360, justify="left").pack(anchor="w", pady=(4, 8))

            r_btn = tk.Label(empty_card, text="Clear All Filters", font=("Segoe UI", 8, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.CYAN, padx=8, pady=3, cursor="hand2")
            r_btn.pack(anchor="w")
            r_btn.bind("<Button-1>", lambda _: self.reset_filters())
            self._render_detail_empty()
            return

        for entry in entries:
            eid = entry["id"]
            is_active = (eid == self.selected_entry_id)
            bg_col = Theme.BG_CARD_HOVER if is_active else Theme.BG_INPUT
            border_col = Theme.CYAN if is_active else Theme.BORDER_MUTED

            card = tk.Frame(
                self.list_container,
                bg=bg_col,
                highlightbackground=border_col,
                highlightthickness=1,
                padx=12,
                pady=10,
                cursor="hand2"
            )
            card.pack(fill="x", padx=10, pady=(0, 6))

            # Row 1: Badges & Timestamp
            row1 = tk.Frame(card, bg=bg_col)
            row1.pack(fill="x")

            status = entry.get("status", "Formulated")
            st_style = STATUS_COLORS.get(status, STATUS_COLORS["Formulated"])

            st_pill = tk.Label(
                row1,
                text=f"{st_style['icon']} {status.upper()}",
                font=("Segoe UI", 7, "bold"),
                bg=st_style["bg"],
                fg=st_style["accent"],
                padx=5,
                pady=2
            )
            st_pill.pack(side="left", padx=(0, 6))

            etype = entry.get("entry_type", "Observation")
            etype_col = TYPE_COLORS.get(etype, Theme.CYAN)
            type_pill = tk.Label(
                row1,
                text=etype,
                font=("Segoe UI", 7, "bold"),
                bg=Theme.BG_CARD,
                fg=etype_col,
                padx=5,
                pady=2
            )
            type_pill.pack(side="left")

            time_lbl = tk.Label(
                row1,
                text=entry.get("timestamp", ""),
                font=("Segoe UI", 7),
                bg=bg_col,
                fg=Theme.TEXT_MUTED
            )
            time_lbl.pack(side="right")

            # Row 2: Title
            title_lbl = tk.Label(
                card,
                text=entry.get("title", "Untitled Entry"),
                font=("Segoe UI", 10, "bold"),
                bg=bg_col,
                fg=Theme.TEXT_PRIMARY,
                wraplength=380,
                justify="left"
            )
            title_lbl.pack(anchor="w", pady=(4, 2))

            # Row 3: Domain
            dom_lbl = tk.Label(
                card,
                text=f"Domain: {entry.get('domain', 'General')}",
                font=("Segoe UI", 8),
                bg=bg_col,
                fg=Theme.TEXT_MUTED
            )
            dom_lbl.pack(anchor="w")

            # Row 4: Snippet
            snippet = entry.get("hypothesis") or entry.get("observations") or entry.get("body", "")
            if len(snippet) > 110:
                snippet = snippet[:107] + "..."

            if snippet:
                snip_lbl = tk.Label(
                    card,
                    text=snippet,
                    font=("Segoe UI", 8),
                    bg=bg_col,
                    fg=Theme.TEXT_SECONDARY,
                    wraplength=380,
                    justify="left"
                )
                snip_lbl.pack(anchor="w", pady=(3, 0))

            # Click binding to inspect
            for w in [card, row1, st_pill, type_pill, time_lbl, title_lbl, dom_lbl]:
                w.bind("<Button-1>", lambda _, i=eid: self.select_entry(i))

    def _select_first_available_entry(self):
        entries = self._get_filtered_entries()
        if entries:
            self.select_entry(entries[0]["id"])
        else:
            self.selected_entry_id = None
            self._render_detail_empty()

    def select_entry(self, entry_id):
        self.selected_entry_id = entry_id
        self._refresh_entries_list()
        self._render_detail()

    # -------------------------------------------------------------------------
    # ENTRY DETAIL INSPECTOR VIEW
    # -------------------------------------------------------------------------
    def _render_detail(self):
        for child in self.detail_container.winfo_children():
            child.destroy()

        if not hasattr(self.app, "state") or not self.app.state:
            return

        entry = next((e for e in self.app.state.journal_entries if e.get("id") == self.selected_entry_id), None)
        if not entry:
            self._render_detail_empty()
            return

        self.detail_wrap_labels = []

        # 1. Header Row: Domain & Type Badges + Timestamps
        top_row = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
        top_row.pack(fill="x", padx=24, pady=(20, 8))

        etype = entry.get("entry_type", "Observation")
        etype_col = TYPE_COLORS.get(etype, Theme.CYAN)
        tk.Label(
            top_row,
            text=f"◈ {etype.upper()}",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=etype_col,
            padx=8,
            pady=3
        ).pack(side="left", padx=(0, 8))

        dom = entry.get("domain", "General")
        tk.Label(
            top_row,
            text=f"DOMAIN: {dom.upper()}",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_SECONDARY,
            padx=8,
            pady=3
        ).pack(side="left")

        ts_str = f"Created: {entry.get('timestamp', '')}"
        if entry.get("updated_at"):
            ts_str += f" • Updated: {entry.get('updated_at')}"

        tk.Label(
            top_row,
            text=ts_str,
            font=("Segoe UI", 8),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        ).pack(side="right")

        # 2. Main Title
        cur_w = max(300, self.detail_canvas.winfo_width() - 64)
        title_lbl = tk.Label(
            self.detail_container,
            text=entry.get("title", "Untitled Entry"),
            font=("Segoe UI", 18, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            wraplength=cur_w,
            justify="left"
        )
        title_lbl.pack(anchor="w", padx=24, pady=(0, 10))
        self.detail_wrap_labels.append(title_lbl)

        # 3. Action Toolbar (Edit, Duplicate, Delete) + Quick Hypothesis Status Transitions
        action_bar = tk.Frame(self.detail_container, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=14, pady=8)
        action_bar.pack(fill="x", padx=24, pady=(0, 14))

        # Status Transition Workflow Buttons
        tk.Label(action_bar, text="Status Workflow:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        cur_status = entry.get("status", "Formulated")
        for st_name, st_info in STATUS_COLORS.items():
            is_cur = (st_name == cur_status)
            btn_bg = st_info["accent"] if is_cur else Theme.BG_CARD
            btn_fg = Theme.BG_ROOT if is_cur else st_info["accent"]

            st_btn = tk.Label(
                action_bar,
                text=f"{st_info['icon']} {st_name}",
                font=("Segoe UI", 7, "bold"),
                bg=btn_bg,
                fg=btn_fg,
                padx=8,
                pady=4,
                cursor="hand2"
            )
            st_btn.pack(side="left", padx=(0, 4))
            st_btn.bind("<Button-1>", lambda _, s=st_name: self._change_entry_status(entry["id"], s))

        # Right Action Buttons: Edit, Duplicate, Delete
        del_btn = tk.Label(
            action_bar,
            text="🗑 Delete",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.ROSE,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>", lambda _: self._delete_entry_with_confirm(entry["id"]))

        dup_btn = tk.Label(
            action_bar,
            text="📑 Duplicate",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.PURPLE_LIGHT,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        dup_btn.pack(side="right", padx=(0, 6))
        dup_btn.bind("<Button-1>", lambda _: self._duplicate_entry(entry["id"]))

        edit_btn = tk.Label(
            action_bar,
            text="✏️ Edit Entry",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.CYAN,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        edit_btn.pack(side="right", padx=(0, 6))
        edit_btn.bind("<Button-1>", lambda _: self.open_edit_entry_editor(entry["id"]))

        # 4. Status Disclaimer Alert
        disclaimer_box = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
        disclaimer_box.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(
            disclaimer_box,
            text=f"ⓘ Hypothesis Progression: Currently marked as [{cur_status}]. "
                 "Verification status represents the student's recorded conclusion in this educational laboratory.",
            font=("Segoe UI", 8, "italic"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED,
            justify="left"
        ).pack(anchor="w")

        # Helper method for structured sections
        def add_section(sec_title, sec_content, icon, accent_col=Theme.TEXT_PRIMARY):
            if not sec_content:
                return
            s_box = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
            s_box.pack(fill="x", padx=24, pady=(0, 12))

            tk.Label(s_box, text=f"{icon} {sec_title}", font=("Segoe UI", 10, "bold"),
                     bg=Theme.BG_CARD, fg=accent_col).pack(anchor="w", pady=(0, 4))

            c_frame = tk.Frame(s_box, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=14, pady=10)
            c_frame.pack(fill="x")

            c_lbl = tk.Label(
                c_frame,
                text=sec_content,
                font=("Segoe UI", 9),
                bg=Theme.BG_INPUT,
                fg=Theme.TEXT_SECONDARY,
                wraplength=max(300, self.detail_canvas.winfo_width() - 80),
                justify="left"
            )
            c_lbl.pack(anchor="w")
            self.detail_wrap_labels.append(c_lbl)

        # 5. Scientific Dossier Sections
        add_section("Research Question", entry.get("research_question"), "❓", Theme.CYAN)
        add_section("Hypothesis", entry.get("hypothesis"), "💡", Theme.PURPLE_LIGHT)
        add_section("Observations & Background Context", entry.get("observations") or entry.get("body"), "📝")
        add_section("Methodology & Experimental Notes", entry.get("methodology"), "🔬")
        add_section("Results & Quantitative Findings", entry.get("results"), "📊")
        add_section("Conclusion & Scientific Synthesis", entry.get("conclusion"), "🏁", Theme.EMERALD)

        # 6. Tags Row
        tags_str = entry.get("tags")
        if tags_str:
            t_box = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
            t_box.pack(fill="x", padx=24, pady=(0, 20))

            tk.Label(t_box, text="🏷 Tags:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 6))

            for tg in tags_str.split(","):
                clean_tg = tg.strip()
                if clean_tg:
                    tk.Label(
                        t_box,
                        text=f"#{clean_tg}",
                        font=("Segoe UI", 8),
                        bg=Theme.BG_INPUT,
                        fg=Theme.TEXT_SECONDARY,
                        padx=6,
                        pady=2
                    ).pack(side="left", padx=(0, 6))

        self.detail_canvas.yview_moveto(0)

    def _render_detail_empty(self):
        for child in self.detail_container.winfo_children():
            child.destroy()

        p = tk.Frame(self.detail_container, bg=Theme.BG_CARD, padx=20, pady=40)
        p.pack(fill="both", expand=True)

        tk.Label(p, text="📓", font=("Segoe UI", 36), bg=Theme.BG_CARD).pack(pady=(20, 8))
        tk.Label(p, text="Discovery Journal Dossier", font=("Segoe UI", 15, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(pady=(0, 6))
        tk.Label(p, text="Select an entry from the list to view full research documentation, "
                        "update hypothesis statuses, duplicate, or edit records.",
                 font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=420, justify="center").pack(pady=(0, 16))

        n_btn = tk.Label(p, text=" ➕ Create New Entry ", font=("Segoe UI", 9, "bold"),
                         bg=Theme.EMERALD, fg=Theme.BG_ROOT, padx=14, pady=6, cursor="hand2")
        n_btn.pack()
        n_btn.bind("<Button-1>", lambda _: self.open_new_entry_editor())

    # -------------------------------------------------------------------------
    # HYPOTHESIS STATUS WORKFLOW & MUTATIONS
    # -------------------------------------------------------------------------
    def _change_entry_status(self, entry_id, new_status):
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.update_journal_entry_status(entry_id, new_status)

    def _duplicate_entry(self, entry_id):
        if hasattr(self.app, "state") and self.app.state:
            cloned = self.app.state.duplicate_journal_entry(entry_id)
            if cloned:
                self.selected_entry_id = cloned["id"]

    def _delete_entry_with_confirm(self, entry_id):
        entry = next((e for e in self.app.state.journal_entries if e.get("id") == entry_id), None)
        title = entry.get("title", "this entry") if entry else "this entry"

        confirm = messagebox.askyesno(
            "Confirm Record Deletion",
            f"Are you sure you want to permanently remove '{title}' from your Discovery Journal?\n\nThis action cannot be undone.",
            parent=self
        )
        if confirm:
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.delete_journal_entry(entry_id)
                self.selected_entry_id = None
                self._select_first_available_entry()

    # -------------------------------------------------------------------------
    # ENTRY EDITOR LAYOUT & WORKFLOW (CREATE / EDIT / DRAFT RECEIVER)
    # -------------------------------------------------------------------------
    def _build_editor_layout(self, parent):
        # Card container with full scrollable form
        editor_card = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1
        )
        editor_card.pack(fill="both", expand=True)

        self.editor_canvas = tk.Canvas(editor_card, bg=Theme.BG_CARD, highlightthickness=0, yscrollincrement=1)
        self.editor_canvas._is_curiolab_scroll_canvas = True
        self.editor_vbar = ttk.Scrollbar(editor_card, orient="vertical", command=self.editor_canvas.yview)
        self.editor_canvas.configure(yscrollcommand=self.editor_vbar.set)

        self.editor_container = tk.Frame(self.editor_canvas, bg=Theme.BG_CARD)
        self.editor_win_id = self.editor_canvas.create_window((0, 0), window=self.editor_container, anchor="nw")

        self.editor_canvas.pack(side="left", fill="both", expand=True)
        self.editor_vbar.pack(side="right", fill="y")

        self.editor_container.bind("<Configure>", lambda e: self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all")))
        self.editor_canvas.bind("<Configure>", lambda e: self.editor_canvas.itemconfig(self.editor_win_id, width=e.width))

        # We will build form fields dynamically in open_editor()

    def open_new_entry_editor(self):
        """Opens editor for creating a new research entry."""
        self.editing_entry_id = None
        self.draft_source_info = None

        self.form_title_var.set("")
        self.form_domain_var.set("General")
        self.form_type_var.set("Hypothesis")
        self.form_status_var.set("Formulated")
        self.form_tags_var.set("Laboratory, Research")

        self._show_editor_mode(
            banner_title="Create New Scientific Research Entry",
            banner_desc="Formulate an inquiry, hypothesize expected behaviors, and record experimental methods.",
            initial_fields={}
        )

    def open_edit_entry_editor(self, entry_id):
        """Opens editor populated with existing entry fields."""
        if not hasattr(self.app, "state") or not self.app.state:
            return
        entry = next((e for e in self.app.state.journal_entries if e.get("id") == entry_id), None)
        if not entry:
            return

        self.editing_entry_id = entry_id
        self.draft_source_info = None

        self.form_title_var.set(entry.get("title", ""))
        self.form_domain_var.set(entry.get("domain", "General"))
        self.form_type_var.set(entry.get("entry_type", "Observation"))
        self.form_status_var.set(entry.get("status", "Formulated"))
        self.form_tags_var.set(entry.get("tags", ""))

        self._show_editor_mode(
            banner_title=f"Edit Entry: {entry.get('title', 'Entry')}",
            banner_desc="Update research questions, empirical observations, results, or conclusions.",
            initial_fields={
                "research_question": entry.get("research_question", ""),
                "hypothesis": entry.get("hypothesis", ""),
                "observations": entry.get("observations") or entry.get("body", ""),
                "methodology": entry.get("methodology", ""),
                "results": entry.get("results", ""),
                "conclusion": entry.get("conclusion", "")
            }
        )

    def load_pending_draft(self, draft):
        """Loads pending citation or galaxy concept draft into editor."""
        self.editing_entry_id = None
        self.draft_source_info = draft

        source_type = draft.get("source_type", "external")
        if source_type == "library_citation":
            b_title = "📋 Knowledge Library Demonstration Citation Staged"
            b_desc = "Review and adapt this educational reference into your personal discovery notes. Retains educational demonstration status."
        elif source_type == "galaxy_concept":
            b_title = "🌌 Research Galaxy Concept Staged for Investigation"
            b_desc = "Transferred theoretical concept and connected disciplines. Refine your research questions before committing."
        elif source_type == "research_detective":
            b_title = "🔍 Research Detective Investigation Dossier Staged"
            b_desc = "Transferred empirical investigation findings, anomalies, and conclusions. Review and refine your journal entry."
        else:
            b_title = "Staged Journal Draft"
            b_desc = "Review and edit research notes before saving."

        self.form_title_var.set(draft.get("title", ""))
        self.form_domain_var.set(draft.get("domain", "General"))
        self.form_type_var.set(draft.get("entry_type", "Finding" if source_type == "research_detective" else ("Literature Note" if source_type == "library_citation" else "Hypothesis")))
        self.form_status_var.set(draft.get("status", "Formulated"))
        self.form_tags_var.set(draft.get("tags", "Draft"))

        meth = draft.get("methodology", "")
        if "dataset_description" in draft and draft["dataset_description"]:
            if draft["dataset_description"] not in meth:
                meth = f"Dataset Description:\n{draft['dataset_description']}\n\nMethodology:\n{meth}"

        conc = draft.get("conclusion", "")
        if "limitations" in draft and draft["limitations"]:
            if draft["limitations"] not in conc:
                conc = f"{conc}\n\nLimitations & Confounders:\n{draft['limitations']}"

        self._show_editor_mode(
            banner_title=b_title,
            banner_desc=b_desc,
            initial_fields={
                "research_question": draft.get("research_question", ""),
                "hypothesis": draft.get("hypothesis", ""),
                "observations": draft.get("observations") or draft.get("body", ""),
                "methodology": meth,
                "results": draft.get("results", ""),
                "conclusion": conc
            }
        )

    def _show_editor_mode(self, banner_title, banner_desc, initial_fields):
        self.explorer_frame.pack_forget()
        self.editor_frame.pack(fill="both", expand=True)
        self.editor_mode = True

        for child in self.editor_container.winfo_children():
            child.destroy()

        # 1. Editor Banner
        banner = tk.Frame(
            self.editor_container,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.CYAN,
            highlightthickness=1,
            padx=20,
            pady=12
        )
        banner.pack(fill="x", padx=24, pady=(20, 14))

        tk.Label(banner, text=banner_title, font=("Segoe UI", 13, "bold"), bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN).pack(anchor="w")
        tk.Label(banner, text=banner_desc, font=("Segoe UI", 9), bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        # 2. Top Save / Cancel Action Bar
        act_bar = tk.Frame(self.editor_container, bg=Theme.BG_CARD)
        act_bar.pack(fill="x", padx=24, pady=(0, 14))

        save_btn = tk.Label(
            act_bar,
            text=" 💾 Save Journal Entry ",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.EMERALD,
            fg=Theme.BG_ROOT,
            padx=16,
            pady=6,
            cursor="hand2"
        )
        save_btn.pack(side="left", padx=(0, 10))
        save_btn.bind("<Button-1>", lambda _: self._save_form_data())

        cancel_btn = tk.Label(
            act_bar,
            text=" ✕ Cancel & Return ",
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=14,
            pady=6,
            cursor="hand2"
        )
        cancel_btn.pack(side="left")
        cancel_btn.bind("<Button-1>", lambda _: self._cancel_editor())

        # 3. Form Grid: Title, Domain, Type, Status, Tags
        grid_box = tk.Frame(self.editor_container, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=16, pady=14)
        grid_box.pack(fill="x", padx=24, pady=(0, 14))

        # Title Field
        tk.Label(grid_box, text="Entry Title *:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=4)
        t_entry = tk.Entry(grid_box, textvariable=self.form_title_var, font=("Segoe UI", 10), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN, relief="flat")
        t_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=4, padx=(8, 0))

        # Domain Field
        tk.Label(grid_box, text="Scientific Domain:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).grid(row=1, column=0, sticky="w", pady=4)
        domains = ["Quantum Physics", "Artificial Intelligence", "Neuroscience",
                   "Information Theory", "Computer Vision", "Cybersecurity", "Complexity Science", "Mathematics", "General"]
        d_combo = ttk.Combobox(grid_box, textvariable=self.form_domain_var, values=domains, state="readonly", style="Journal.TCombobox")
        d_combo.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 16))

        # Type Field
        tk.Label(grid_box, text="Entry Type:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).grid(row=1, column=2, sticky="w", pady=4)
        types = ["Research Idea", "Research Question", "Hypothesis", "Experiment Log", "Observation", "Literature Note", "Finding"]
        tp_combo = ttk.Combobox(grid_box, textvariable=self.form_type_var, values=types, state="readonly", style="Journal.TCombobox")
        tp_combo.grid(row=1, column=3, sticky="ew", pady=4, padx=(8, 0))

        # Status Field
        tk.Label(grid_box, text="Hypothesis Status:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).grid(row=2, column=0, sticky="w", pady=4)
        statuses = ["Formulated", "Testing", "Verified", "Refuted"]
        st_combo = ttk.Combobox(grid_box, textvariable=self.form_status_var, values=statuses, state="readonly", style="Journal.TCombobox")
        st_combo.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 16))

        # Tags Field
        tk.Label(grid_box, text="Tags (comma-separated):", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY).grid(row=2, column=2, sticky="w", pady=4)
        tags_entry = tk.Entry(grid_box, textvariable=self.form_tags_var, font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, insertbackground=Theme.CYAN, relief="flat")
        tags_entry.grid(row=2, column=3, sticky="ew", pady=4, padx=(8, 0))

        grid_box.columnconfigure(1, weight=1)
        grid_box.columnconfigure(3, weight=1)

        # 4. Multiline Text Areas for Scientific Dossier
        self.text_widgets = {}

        def add_text_field(field_key, label_str, num_lines, default_val=""):
            f_frame = tk.Frame(self.editor_container, bg=Theme.BG_CARD)
            f_frame.pack(fill="x", padx=24, pady=(0, 10))

            tk.Label(f_frame, text=label_str, font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

            txt_box = tk.Frame(f_frame, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            txt_box.pack(fill="x")

            txt = tk.Text(
                txt_box,
                height=num_lines,
                font=("Segoe UI", 9),
                bg=Theme.BG_INPUT,
                fg=Theme.TEXT_PRIMARY,
                insertbackground=Theme.CYAN,
                relief="flat",
                wrap="word",
                padx=8,
                pady=6
            )
            txt.pack(fill="x", expand=True)
            txt.insert("1.0", default_val)
            self.text_widgets[field_key] = txt

        add_text_field("research_question", "❓ Research Question:", 3, initial_fields.get("research_question", ""))
        add_text_field("hypothesis", "💡 Theoretical Hypothesis:", 3, initial_fields.get("hypothesis", ""))
        add_text_field("observations", "📝 Empirical Observations & Theoretical Context:", 5, initial_fields.get("observations", ""))
        add_text_field("methodology", "🔬 Methodology & Experimental Protocol:", 4, initial_fields.get("methodology", ""))
        add_text_field("results", "📊 Empirical Results & Quantitative Analysis:", 4, initial_fields.get("results", ""))
        add_text_field("conclusion", "🏁 Scientific Synthesis & Conclusion:", 4, initial_fields.get("conclusion", ""))

        # Bottom Save / Cancel Bar
        bottom_act = tk.Frame(self.editor_container, bg=Theme.BG_CARD)
        bottom_act.pack(fill="x", padx=24, pady=(4, 24))

        b_save = tk.Label(bottom_act, text=" 💾 Save Journal Entry ", font=("Segoe UI", 9, "bold"),
                          bg=Theme.EMERALD, fg=Theme.BG_ROOT, padx=16, pady=6, cursor="hand2")
        b_save.pack(side="left", padx=(0, 10))
        b_save.bind("<Button-1>", lambda _: self._save_form_data())

        b_cancel = tk.Label(bottom_act, text=" ✕ Cancel & Return ", font=("Segoe UI", 9),
                            bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, padx=14, pady=6, cursor="hand2")
        b_cancel.pack(side="left")
        b_cancel.bind("<Button-1>", lambda _: self._cancel_editor())

        self.editor_canvas.yview_moveto(0)

    def _save_form_data(self):
        title = self.form_title_var.get().strip()
        if not title:
            messagebox.showwarning("Incomplete Entry", "Please provide a title for your journal entry before saving.", parent=self)
            return

        domain = self.form_domain_var.get().strip() or "General"
        etype = self.form_type_var.get().strip() or "Observation"
        status = self.form_status_var.get().strip() or "Formulated"
        tags = self.form_tags_var.get().strip()

        rq = self.text_widgets["research_question"].get("1.0", "end-1c").strip()
        hyp = self.text_widgets["hypothesis"].get("1.0", "end-1c").strip()
        obs = self.text_widgets["observations"].get("1.0", "end-1c").strip()
        meth = self.text_widgets["methodology"].get("1.0", "end-1c").strip()
        res = self.text_widgets["results"].get("1.0", "end-1c").strip()
        conc = self.text_widgets["conclusion"].get("1.0", "end-1c").strip()

        if hasattr(self.app, "state") and self.app.state:
            if self.editing_entry_id:
                # Update existing
                updated = self.app.state.update_journal_entry(
                    self.editing_entry_id,
                    title=title,
                    domain=domain,
                    entry_type=etype,
                    status=status,
                    tags=tags,
                    research_question=rq,
                    hypothesis=hyp,
                    observations=obs,
                    methodology=meth,
                    results=res,
                    conclusion=conc
                )
                self.selected_entry_id = self.editing_entry_id
            else:
                # Create new entry
                new_e = self.app.state.add_journal_entry(
                    title=title,
                    domain=domain,
                    status=status,
                    tags=tags,
                    body=obs,
                    entry_type=etype,
                    research_question=rq,
                    hypothesis=hyp,
                    observations=obs,
                    methodology=meth,
                    results=res,
                    conclusion=conc,
                    source_ref=self.draft_source_info.get("resource_id") if self.draft_source_info else None
                )
                self.selected_entry_id = new_e["id"]

            # Clear pending draft if active
            self.app.state.pending_journal_draft = None

        # Return to Explorer
        self._cancel_editor()

    def _cancel_editor(self):
        # Clear pending draft on cancellation as well if user chooses to discard
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.pending_journal_draft = None

        self.editor_frame.pack_forget()
        self.explorer_frame.pack(fill="both", expand=True)
        self.editor_mode = False
        self._refresh_dashboard()
        self._refresh_entries_list()
        if self.selected_entry_id:
            self.select_entry(self.selected_entry_id)

    # -------------------------------------------------------------------------
    # NAVIGATION RECEIVER & APPSTATE OBSERVER
    # -------------------------------------------------------------------------
    def on_navigate_to(self):
        """
        Invoked by CurioLabApp.navigate_to("Discovery Journal").
        Checks for pending citation or galaxy concept drafts and opens editor if present.
        """
        if hasattr(self.app, "state") and self.app.state and self.app.state.pending_journal_draft:
            draft = self.app.state.pending_journal_draft
            self.load_pending_draft(draft)
        else:
            if not self.editor_mode:
                self._refresh_dashboard()
                self._refresh_entries_list()
                if not self.selected_entry_id:
                    self._select_first_available_entry()
                else:
                    self._render_detail()

    def _on_app_state_changed(self):
        """Observer callback when any AppState mutation occurs."""
        self._refresh_dashboard()
        if not self.editor_mode:
            self._refresh_entries_list()
            if self.selected_entry_id:
                self._render_detail()

    @property
    def body_text(self):
        """Backward compatibility alias for Stage 2 citation transfer tests."""
        return self.text_widgets.get("observations")

    def _save_entry(self):
        """Backward compatibility alias for Stage 2 citation transfer tests."""
        self._save_form_data()
