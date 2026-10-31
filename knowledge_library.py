"""
CurioLab — Knowledge Library Module
====================================
Interactive educational resource catalog with live filtering,
domain taxonomy, bookmarking, detailed monograph viewer, and citation transfer.

CONTENT INTEGRITY NOTICE:
All records displayed herein are strictly educational demonstration records
designed for local simulation and learning. They do NOT represent or fabricate
real-world peer-reviewed publications, living authors, DOI identifiers, or
academic citation metrics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from theme import Theme


class KnowledgeLibraryView(tk.Frame):
    """
    Polished academic resource browsing experience.
    Fully data-driven through AppState.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # State tracking for UI filtering
        self.search_var = tk.StringVar()
        self.selected_domain_var = tk.StringVar(value="All Domains")
        self.sort_var = tk.StringVar(value="Title (A-Z)")
        self.bookmarked_only_var = tk.BooleanVar(value=False)

        self.selected_resource_id = None
        self.card_widget_refs = {}

        # Build UI layout
        self._build_header(self)
        self._build_controls_bar(self)
        self._build_main_workspace(self)

        # Subscribe to AppState observer updates
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

        # Initial selection and render
        self._refresh_resource_cards()
        resources = self._get_filtered_resources()
        if resources:
            self.select_resource(resources[0]["id"])

    # -------------------------------------------------------------------------
    # HEADER & HERO BANNER
    # -------------------------------------------------------------------------
    def _build_header(self, parent):
        top_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 8))

        breadcrumb = tk.Label(
            top_bar,
            text="Knowledge Library > Educational Monograph Repository",
            font=("Segoe UI", 9),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED
        )
        breadcrumb.pack(side="left")

        hero = tk.Frame(
            parent,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.TEAL,
            highlightthickness=1,
            padx=28,
            pady=16
        )
        hero.pack(fill="x", padx=32, pady=(0, 14))

        tag = tk.Label(
            hero,
            text="◈ EDUCATIONAL DEMONSTRATION MONOGRAPHS • PEER-REVIEW SIMULATION",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEAL,
            padx=8,
            pady=3
        )
        tag.pack(anchor="w")

        title_lbl = tk.Label(
            hero,
            text="Knowledge Library & Theory Repository",
            font=("Segoe UI", 20, "bold"),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w", pady=(6, 2))

        desc_lbl = tk.Label(
            hero,
            text="Browse categorized demonstration resources across quantum systems, information theory, "
                 "computational neuroscience, and complexity science. Use bookmarks to curate active study lists "
                 "and transfer demonstration citations directly into your Discovery Journal.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_SECONDARY,
            wraplength=950,
            justify="left"
        )
        desc_lbl.pack(anchor="w")

    # -------------------------------------------------------------------------
    # FILTER, SEARCH & SORT CONTROLS BAR
    # -------------------------------------------------------------------------
    def _build_controls_bar(self, parent):
        ctrl_bar = tk.Frame(
            parent,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            padx=16,
            pady=10
        )
        ctrl_bar.pack(fill="x", padx=32, pady=(0, 14))

        # 1. Search Box
        search_box = tk.Frame(
            ctrl_bar,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=8,
            pady=4
        )
        search_box.pack(side="left", padx=(0, 12))

        s_icon = tk.Label(search_box, text="🔍", font=("Segoe UI", 9), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED)
        s_icon.pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Segoe UI", 9),
            width=26,
            bd=0,
            relief="flat"
        )
        self.search_entry.pack(side="left")
        self.search_var.trace_add("write", lambda *_: self._on_filter_changed())

        # Clear search button
        clear_lbl = tk.Label(search_box, text="✕", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, cursor="hand2")
        clear_lbl.pack(side="right", padx=(4, 2))
        clear_lbl.bind("<Button-1>", lambda _: self.search_var.set(""))

        # 2. Domain Filter Dropdown
        tk.Label(ctrl_bar, text="Domain:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(4, 4))

        domains = [
            "All Domains",
            "Quantum Physics",
            "Information Theory",
            "Neuroscience",
            "Artificial Intelligence",
            "Complexity Science",
            "Cybersecurity",
            "Computer Vision",
            "Empirical Data Analysis"
        ]
        self.domain_dropdown = ttk.Combobox(
            ctrl_bar,
            textvariable=self.selected_domain_var,
            values=domains,
            state="readonly",
            width=18,
            font=("Segoe UI", 9)
        )
        self.domain_dropdown.pack(side="left", padx=(0, 12))
        self.domain_dropdown.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 3. Sort Dropdown
        tk.Label(ctrl_bar, text="Sort by:", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(4, 4))
        sort_options = [
            "Title (A-Z)",
            "Title (Z-A)",
            "Curriculum Year (Newest)",
            "Level (Intro ➔ Adv)",
            "Domain"
        ]
        self.sort_dropdown = ttk.Combobox(
            ctrl_bar,
            textvariable=self.sort_var,
            values=sort_options,
            state="readonly",
            width=16,
            font=("Segoe UI", 9)
        )
        self.sort_dropdown.pack(side="left", padx=(0, 12))
        self.sort_dropdown.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 4. Bookmarked-Only Toggle Button
        self.bm_toggle_frame = tk.Frame(
            ctrl_bar,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            cursor="hand2"
        )
        self.bm_toggle_frame.pack(side="left", padx=(0, 12))

        self.bm_toggle_lbl = tk.Label(
            self.bm_toggle_frame,
            text="☆ Bookmarked Only",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_SECONDARY,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.bm_toggle_lbl.pack()

        for w in (self.bm_toggle_frame, self.bm_toggle_lbl):
            w.bind("<Button-1>", lambda _: self._toggle_bookmarked_filter())

        # 5. Reset All Filters Button
        reset_btn = tk.Label(
            ctrl_bar,
            text="↺ Reset Filters",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED,
            cursor="hand2",
            padx=8,
            pady=4
        )
        reset_btn.pack(side="left")
        reset_btn.bind("<Button-1>", lambda _: self.reset_all_filters())
        reset_btn.bind("<Enter>", lambda _: reset_btn.config(fg=Theme.CYAN))
        reset_btn.bind("<Leave>", lambda _: reset_btn.config(fg=Theme.TEXT_MUTED))

        # 6. Resource Counter
        self.count_badge = tk.Label(
            ctrl_bar,
            text="Showing 0 of 0 records",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.CYAN
        )
        self.count_badge.pack(side="right")

    # -------------------------------------------------------------------------
    # MAIN WORKSPACE: TWO-COLUMN SPLIT LAYOUT
    # -------------------------------------------------------------------------
    def _build_main_workspace(self, parent):
        container = tk.Frame(parent, bg=Theme.BG_ROOT)
        container.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        container.columnconfigure(0, weight=5)  # Left: 45% Cards List
        container.columnconfigure(1, weight=6)  # Right: 55% Monograph Reader Panel

        # Left Column: Resource Cards List (Scrollable)
        self.left_scroll = tk.Canvas(container, bg=Theme.BG_ROOT, highlightthickness=0)
        self.left_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.left_scroll.yview)
        self.cards_container = tk.Frame(self.left_scroll, bg=Theme.BG_ROOT)

        self.cards_container.bind(
            "<Configure>",
            lambda e: self.left_scroll.configure(scrollregion=self.left_scroll.bbox("all"))
        )
        self.left_window_id = self.left_scroll.create_window((0, 0), window=self.cards_container, anchor="nw")
        self.left_scroll.configure(yscrollcommand=self.left_scrollbar.set)

        self.left_scroll.bind("<Configure>", lambda e: self.left_scroll.itemconfig(self.left_window_id, width=e.width))

        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.left_scrollbar.grid(row=0, column=0, sticky="nse", padx=(0, 8))

        # Mousewheel binding
        self._bind_mousewheel_tree(self.left_scroll)

        # Right Column: Resource Detail Inspector Panel (Scrollable)
        self.right_scroll = tk.Canvas(container, bg=Theme.BG_CARD, highlightthickness=1, highlightbackground=Theme.BORDER_SUBTLE)
        self.right_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.right_scroll.yview)
        self.detail_container = tk.Frame(self.right_scroll, bg=Theme.BG_CARD, padx=24, pady=20)

        self.detail_container.bind(
            "<Configure>",
            lambda e: self.right_scroll.configure(scrollregion=self.right_scroll.bbox("all"))
        )
        self.right_window_id = self.right_scroll.create_window((0, 0), window=self.detail_container, anchor="nw")
        self.right_scroll.configure(yscrollcommand=self.right_scrollbar.set)

        self.right_scroll.bind("<Configure>", self._on_right_canvas_configure)

        self.right_scroll.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.right_scrollbar.grid(row=0, column=1, sticky="nse")

        self._bind_mousewheel_tree(self.right_scroll, self.right_scroll)

    def _on_right_canvas_configure(self, event):
        self.right_scroll.itemconfig(self.right_window_id, width=event.width)
        avail = max(260, event.width - 56)
        for lbl in getattr(self, "detail_wrap_labels", []):
            try:
                lbl.config(wraplength=avail)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # FILTER & SORT LOGIC
    # -------------------------------------------------------------------------
    def _get_filtered_resources(self):
        """Filters and sorts library resources based on current controls."""
        if not hasattr(self.app, "state") or not self.app.state:
            return []

        resources = list(self.app.state.library_resources)

        # 1. Domain Filter
        domain = self.selected_domain_var.get()
        if domain and domain != "All Domains":
            resources = [r for r in resources if r.get("module_domain") == domain]

        # 2. Bookmarked-Only Filter
        if self.bookmarked_only_var.get():
            resources = [r for r in resources if r.get("bookmarked", False)]

        # 3. Search Query Filter
        query = self.search_var.get().strip().lower()
        if query:
            def matches(r):
                title = r.get("title", "").lower()
                curator = r.get("curator", "").lower()
                summary = r.get("summary", "").lower()
                tags = " ".join(r.get("tags", [])).lower()
                concepts = " ".join(r.get("key_concepts", [])).lower()
                return (query in title or query in curator or query in summary or
                        query in tags or query in concepts)
            resources = [r for r in resources if matches(r)]

        # 4. Sorting
        sort_mode = self.sort_var.get()
        if sort_mode == "Title (A-Z)":
            resources.sort(key=lambda r: r.get("title", "").lower())
        elif sort_mode == "Title (Z-A)":
            resources.sort(key=lambda r: r.get("title", "").lower(), reverse=True)
        elif sort_mode == "Curriculum Year (Newest)":
            resources.sort(key=lambda r: r.get("year", 2026), reverse=True)
        elif sort_mode == "Level (Intro ➔ Adv)":
            level_rank = {"Introductory": 1, "Intermediate": 2, "Advanced": 3}
            resources.sort(key=lambda r: level_rank.get(r.get("curriculum_level", "Introductory"), 1))
        elif sort_mode == "Domain":
            resources.sort(key=lambda r: (r.get("module_domain", "").lower(), r.get("title", "").lower()))

        return resources

    def _on_filter_changed(self):
        """Called whenever search query, domain, or sort dropdown changes."""
        self._refresh_resource_cards()

    def _toggle_bookmarked_filter(self):
        """Toggles the bookmarked-only filter switch."""
        new_val = not self.bookmarked_only_var.get()
        self.bookmarked_only_var.set(new_val)
        if new_val:
            self.bm_toggle_frame.config(bg=Theme.AMBER, highlightbackground=Theme.AMBER)
            self.bm_toggle_lbl.config(text="★ Bookmarked Only", bg=Theme.AMBER, fg=Theme.BG_ROOT)
        else:
            self.bm_toggle_frame.config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
            self.bm_toggle_lbl.config(text="☆ Bookmarked Only", bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)
        self._refresh_resource_cards()

    def reset_all_filters(self):
        """Restores search, category, sort, and bookmark switches to defaults."""
        self.search_var.set("")
        self.selected_domain_var.set("All Domains")
        self.sort_var.set("Title (A-Z)")
        self.bookmarked_only_var.set(False)
        self.bm_toggle_frame.config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
        self.bm_toggle_lbl.config(text="☆ Bookmarked Only", bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)
        self._refresh_resource_cards()

    # -------------------------------------------------------------------------
    # CARD RENDERING & LIST VIEW
    # -------------------------------------------------------------------------
    def _refresh_resource_cards(self):
        """Rebuilds the left scrollable cards list based on filtered results."""
        for w in self.cards_container.winfo_children():
            w.destroy()
        self.card_widget_refs = {}

        resources = self._get_filtered_resources()
        total_count = len(self.app.state.library_resources) if (hasattr(self.app, "state") and self.app.state) else 0

        self.count_badge.config(text=f"Showing {len(resources)} of {total_count} records")

        if not resources:
            self._render_empty_state()
            self._render_empty_detail_panel()
            return

        for res in resources:
            card = self._create_resource_card(self.cards_container, res)
            card.pack(fill="x", pady=(0, 10))
            self.card_widget_refs[res["id"]] = card

        # Ensure current selection remains valid
        if self.selected_resource_id not in [r["id"] for r in resources]:
            self.select_resource(resources[0]["id"])
        else:
            self._highlight_selected_card()

        self._bind_mousewheel_tree(self.cards_container, self.left_scroll)

    def _create_resource_card(self, parent, res):
        rid = res["id"]
        is_selected = (rid == self.selected_resource_id)
        is_bookmarked = res.get("bookmarked", False)

        border_color = Theme.CYAN if is_selected else Theme.BORDER_SUBTLE
        bg_color = Theme.BG_CARD_HOVER if is_selected else Theme.BG_CARD

        card = tk.Frame(
            parent,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=14,
            pady=12,
            cursor="hand2"
        )

        # 1. Header Row: Domain Badge + Level + Year
        hdr = tk.Frame(card, bg=bg_color)
        hdr.pack(fill="x")

        domain_colors = {
            "Quantum Physics": Theme.CYAN,
            "Information Theory": Theme.PURPLE,
            "Neuroscience": Theme.PURPLE_LIGHT,
            "Artificial Intelligence": Theme.BLUE,
            "Complexity Science": Theme.EMERALD,
            "Cybersecurity": Theme.AMBER,
            "Computer Vision": Theme.TEAL,
            "Empirical Data Analysis": Theme.CYAN_BRIGHT
        }
        accent = domain_colors.get(res.get("module_domain"), Theme.CYAN)

        badge = tk.Label(
            hdr,
            text=f" {res.get('module_domain', 'Science')} ",
            font=("Segoe UI", 7, "bold"),
            bg=Theme.BG_INPUT,
            fg=accent,
            padx=4,
            pady=2
        )
        badge._keep_bg = True
        badge.pack(side="left")

        lvl_badge = tk.Label(
            hdr,
            text=f" {res.get('curriculum_level', 'Demonstration')} ",
            font=("Segoe UI", 7),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=4,
            pady=2
        )
        lvl_badge._keep_bg = True
        lvl_badge.pack(side="left", padx=(4, 0))

        year_lbl = tk.Label(
            hdr,
            text=f"📅 {res.get('year', 2026)}",
            font=("Segoe UI", 7),
            bg=bg_color,
            fg=Theme.TEXT_MUTED
        )
        year_lbl.pack(side="right")

        # 2. Title
        title_lbl = tk.Label(
            card,
            text=res.get("title", "Resource Title"),
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg=Theme.TEXT_PRIMARY,
            wraplength=340,
            justify="left",
            anchor="w"
        )
        title_lbl.pack(fill="x", pady=(6, 2))

        # 3. Curator
        curator_lbl = tk.Label(
            card,
            text=f"Curated by: {res.get('curator', 'CurioLab Staff')}",
            font=("Segoe UI", 8),
            bg=bg_color,
            fg=Theme.TEXT_MUTED,
            anchor="w"
        )
        curator_lbl.pack(fill="x", pady=(0, 4))

        # 4. Summary Preview
        summary_text = res.get("summary", "")
        if len(summary_text) > 130:
            summary_text = summary_text[:127] + "..."
        summary_lbl = tk.Label(
            card,
            text=summary_text,
            font=("Segoe UI", 8),
            bg=bg_color,
            fg=Theme.TEXT_SECONDARY,
            wraplength=340,
            justify="left",
            anchor="w"
        )
        summary_lbl.pack(fill="x", pady=(0, 8))

        # 5. Tag pills
        tag_box = tk.Frame(card, bg=bg_color)
        tag_box.pack(fill="x", pady=(0, 8))
        for t in res.get("tags", [])[:3]:
            t_lbl = tk.Label(
                tag_box,
                text=f"#{t}",
                font=("Segoe UI", 7),
                bg=Theme.BG_INPUT,
                fg=Theme.TEXT_MUTED,
                padx=4,
                pady=1
            )
            t_lbl._keep_bg = True
            t_lbl.pack(side="left", padx=(0, 4))

        # 6. Action Row: Bookmark Button + Inspect Monograph
        act_row = tk.Frame(card, bg=bg_color)
        act_row.pack(fill="x")

        bm_text = "★ Bookmarked" if is_bookmarked else "☆ Bookmark"
        bm_color = Theme.AMBER if is_bookmarked else Theme.TEXT_MUTED

        bm_btn = tk.Label(
            act_row,
            text=bm_text,
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=bm_color,
            padx=8,
            pady=3,
            cursor="hand2"
        )
        bm_btn._keep_bg = True
        bm_btn.pack(side="left")
        bm_btn.bind("<Button-1>", lambda e, r=rid: self._on_card_bookmark_clicked(e, r))

        inspect_lbl = tk.Label(
            act_row,
            text="Read Monograph ➔",
            font=("Segoe UI", 8, "bold"),
            bg=bg_color,
            fg=Theme.CYAN,
            cursor="hand2"
        )
        inspect_lbl.pack(side="right")

        # Bind whole card surface to selection
        child_widgets = [card, hdr, badge, lvl_badge, year_lbl, title_lbl, curator_lbl, summary_lbl, tag_box, act_row, inspect_lbl]
        for w in child_widgets:
            w.bind("<Button-1>", lambda _, r=rid: self.select_resource(r))

        return card

    def _render_empty_state(self):
        """Displays empty state when no records match filter query."""
        box = tk.Frame(self.cards_container, bg=Theme.BG_CARD, padx=20, pady=32, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
        box.pack(fill="x", pady=20)

        tk.Label(box, text="🔍", font=("Segoe UI", 26), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack()
        tk.Label(box, text="No Matching Demonstration Records", font=("Segoe UI", 12, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(pady=(6, 4))

        q = self.search_var.get().strip()
        msg = f"No monographs matched your search '{q}'." if q else "No resources match the selected domain and bookmark filters."
        tk.Label(box, text=msg, font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=280).pack(pady=(0, 14))

        reset_b = tk.Label(box, text="↺ Reset All Filters", font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN, padx=12, pady=5, cursor="hand2")
        reset_b.pack()
        reset_b.bind("<Button-1>", lambda _: self.reset_all_filters())

    def _render_empty_detail_panel(self):
        for w in self.detail_container.winfo_children():
            w.destroy()

        box = tk.Frame(self.detail_container, bg=Theme.BG_CARD, pady=40)
        box.pack(fill="both", expand=True)

        tk.Label(box, text="📖", font=("Segoe UI", 32), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack()
        tk.Label(box, text="No Resource Selected", font=("Segoe UI", 13, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(pady=(8, 4))
        tk.Label(box, text="Select an educational monograph from the left panel to inspect full theoretical notes, equations, and citation options.",
                 font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, wraplength=400, justify="center").pack()

    # -------------------------------------------------------------------------
    # DETAIL INSPECTOR PANEL RENDERING
    # -------------------------------------------------------------------------
    def select_resource(self, resource_id):
        """Selects and loads a resource into the right reading panel."""
        self.selected_resource_id = resource_id
        self._highlight_selected_card()

        # Find resource record
        resource = None
        if hasattr(self.app, "state") and self.app.state:
            for r in self.app.state.library_resources:
                if r.get("id") == resource_id:
                    resource = r
                    break

        if not resource:
            self._render_empty_detail_panel()
            return

        for w in self.detail_container.winfo_children():
            w.destroy()

        # 1. Header Metadata Section
        meta_row = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
        meta_row.pack(fill="x")

        domain_colors = {
            "Quantum Physics": Theme.CYAN,
            "Information Theory": Theme.PURPLE,
            "Neuroscience": Theme.PURPLE_LIGHT,
            "Artificial Intelligence": Theme.BLUE,
            "Complexity Science": Theme.EMERALD,
            "Cybersecurity": Theme.AMBER,
            "Computer Vision": Theme.TEAL,
            "Empirical Data Analysis": Theme.CYAN_BRIGHT
        }
        accent = domain_colors.get(resource.get("module_domain"), Theme.CYAN)

        tk.Label(meta_row, text=f" {resource.get('module_domain')} ", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=accent, padx=6, pady=2).pack(side="left")

        tk.Label(meta_row, text=f" {resource.get('curriculum_level')} Level ", font=("Segoe UI", 8),
                 bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY, padx=6, pady=2).pack(side="left", padx=(6, 0))

        tk.Label(meta_row, text=f"📅 Curriculum Release: {resource.get('year', 2026)}", font=("Segoe UI", 8),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="right")

        self.detail_wrap_labels = []

        # 2. Main Title
        title_lbl = tk.Label(
            self.detail_container,
            text=resource.get("title", ""),
            font=("Segoe UI", 16, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            wraplength=480,
            justify="left"
        )
        title_lbl.pack(anchor="w", pady=(8, 4))
        self.detail_wrap_labels.append(title_lbl)

        # 3. Curator
        tk.Label(
            self.detail_container,
            text=f"Curating Body: {resource.get('curator', 'CurioLab Staff')}  •  Record ID: {resource.get('id')}",
            font=("Segoe UI", 8),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        # 4. Content Integrity Notice Badge
        notice_box = tk.Frame(self.detail_container, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=10, pady=6)
        notice_box.pack(fill="x", pady=(0, 14))

        notice_lbl = tk.Label(
            notice_box,
            text="ℹ️ Educational Demonstration Record: This module contains instructional curriculum data "
                 "for conceptual learning. It does not fabricate external publications or citations.",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            wraplength=460,
            justify="left"
        )
        notice_lbl.pack(anchor="w")
        self.detail_wrap_labels.append(notice_lbl)

        # 5. Action Toolbar (Bookmark + Cite in Journal)
        act_box = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
        act_box.pack(fill="x", pady=(0, 16))

        is_bm = resource.get("bookmarked", False)
        bm_btn_text = "★ Bookmarked in Library" if is_bm else "☆ Add to Bookmarks"
        bm_btn_color = Theme.AMBER if is_bm else Theme.TEXT_SECONDARY

        detail_bm_btn = tk.Label(
            act_box,
            text=bm_btn_text,
            font=("Segoe UI", 9, "bold"),
            bg=Theme.BG_INPUT,
            fg=bm_btn_color,
            padx=12,
            pady=6,
            cursor="hand2",
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1
        )
        detail_bm_btn.pack(side="left", padx=(0, 10))
        detail_bm_btn.bind("<Button-1>", lambda _: self._toggle_resource_bookmark(resource["id"]))

        cite_btn = tk.Label(
            act_box,
            text="📋 Cite in Journal ➔",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.TEAL,
            fg=Theme.BG_ROOT,
            padx=14,
            pady=6,
            cursor="hand2"
        )
        cite_btn.pack(side="left")
        cite_btn.bind("<Button-1>", lambda _: self._cite_in_journal(resource["id"]))

        # 6. Abstract Section
        tk.Label(self.detail_container, text="🔬 Demonstration Abstract", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        summary_lbl = tk.Label(
            self.detail_container,
            text=resource.get("summary", ""),
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            wraplength=480,
            justify="left"
        )
        summary_lbl.pack(anchor="w", pady=(0, 14))
        self.detail_wrap_labels.append(summary_lbl)

        # 7. Key Concepts
        if resource.get("key_concepts"):
            tk.Label(self.detail_container, text="💡 Key Curriculum Concepts", font=("Segoe UI", 11, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

            concepts_frame = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
            concepts_frame.pack(fill="x", pady=(0, 14))

            for conc in resource.get("key_concepts", []):
                c_pill = tk.Label(
                    concepts_frame,
                    text=f"◈ {conc}",
                    font=("Segoe UI", 8),
                    bg=Theme.BG_INPUT,
                    fg=accent,
                    padx=6,
                    pady=2
                )
                c_pill.pack(side="left", padx=(0, 6))

        # 8. Theoretical Formulation / Key Equation Box
        eq = resource.get("key_equation")
        if eq:
            tk.Label(self.detail_container, text="📐 Theoretical Mathematical Formulation", font=("Segoe UI", 11, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

            eq_box = tk.Frame(self.detail_container, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=14, pady=10)
            eq_box.pack(fill="x", pady=(0, 14))

            tk.Label(
                eq_box,
                text=eq,
                font=("Consolas", 10, "bold"),
                bg=Theme.BG_INPUT,
                fg=Theme.CYAN_BRIGHT
            ).pack(anchor="w")

        # 9. Full Educational Walkthrough Content
        tk.Label(self.detail_container, text="📖 Detailed Educational Walkthrough", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        walk_lbl = tk.Label(
            self.detail_container,
            text=resource.get("demonstration_content", ""),
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            wraplength=480,
            justify="left"
        )
        walk_lbl.pack(anchor="w", pady=(0, 14))
        self.detail_wrap_labels.append(walk_lbl)

        # 10. Laboratory Synthesis & Study Notes Box
        tk.Label(self.detail_container, text="🧪 Laboratory Synthesis & Investigation Notes", font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        notes_box = tk.Frame(self.detail_container, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=12, pady=10)
        notes_box.pack(fill="x", pady=(0, 14))

        notes_lbl = tk.Label(
            notes_box,
            text=resource.get("study_notes", "No notes recorded."),
            font=("Segoe UI", 9, "italic"),
            bg=Theme.BG_INPUT,
            fg=Theme.AMBER,
            wraplength=460,
            justify="left"
        )
        notes_lbl.pack(anchor="w")
        self.detail_wrap_labels.append(notes_lbl)

        # 11. Related Disciplines
        if resource.get("related_topics"):
            tk.Label(self.detail_container, text="🌌 Cross-Domain Disciplinary Connections", font=("Segoe UI", 11, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

            rel_box = tk.Frame(self.detail_container, bg=Theme.BG_CARD)
            rel_box.pack(fill="x", pady=(0, 20))

            for topic in resource.get("related_topics", []):
                t_lbl = tk.Label(
                    rel_box,
                    text=f"⟷ {topic}",
                    font=("Segoe UI", 8),
                    bg=Theme.BG_INPUT,
                    fg=Theme.TEXT_MUTED,
                    padx=6,
                    pady=2
                )
                t_lbl.pack(side="left", padx=(0, 6))

        # Reset scroll position to top and bind mousewheel
        self.right_scroll.yview_moveto(0)
        self._bind_mousewheel_tree(self.detail_container, self.right_scroll)

    def _highlight_selected_card(self):
        """Highlights the active card in the left list."""
        for rid, card in self.card_widget_refs.items():
            is_active = (rid == self.selected_resource_id)
            border = Theme.CYAN if is_active else Theme.BORDER_SUBTLE
            bg = Theme.BG_CARD_HOVER if is_active else Theme.BG_CARD
            card.config(bg=bg, highlightbackground=border)
            for child in card.winfo_children():
                if getattr(child, "_keep_bg", False):
                    continue
                try:
                    child.config(bg=bg)
                except Exception:
                    pass
                for sub in child.winfo_children():
                    if getattr(sub, "_keep_bg", False):
                        continue
                    try:
                        sub.config(bg=bg)
                    except Exception:
                        pass

    # -------------------------------------------------------------------------
    # INTERACTIONS: BOOKMARKING & CITATION TRANSFER
    # -------------------------------------------------------------------------
    def _on_card_bookmark_clicked(self, event, resource_id):
        self._toggle_resource_bookmark(resource_id)
        return "break"

    def _toggle_resource_bookmark(self, resource_id):
        """Toggles bookmark state in AppState."""
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.toggle_bookmark(resource_id)

    def _cite_in_journal(self, resource_id):
        """
        Executes citation transfer:
        1. Generates educational citation draft from available metadata.
        2. Populates AppState.pending_journal_draft.
        3. Navigates to Discovery Journal for user review and saving.
        """
        if not hasattr(self.app, "state") or not self.app.state:
            return

        draft = self.app.state.generate_citation_draft(resource_id)
        if not draft:
            messagebox.showwarning("Citation Error", "Could not generate citation draft for this record.")
            return

        self.app.state.pending_journal_draft = draft

        # Add notification
        self.app.state.notifications.insert(0, {
            "id": f"notif_cite_{resource_id}",
            "title": "📋 Citation Transferred to Journal",
            "desc": f"Transferred educational reference for '{draft['title']}' to Discovery Journal.",
            "timestamp": "Just now",
            "accent": Theme.TEAL,
            "read": False
        })
        self.app.state.notify()

        # Navigate to Discovery Journal
        self.app.navigate_to("Discovery Journal")

    def _on_app_state_changed(self):
        """Callback invoked whenever AppState mutates."""
        self._refresh_resource_cards()
        if self.selected_resource_id:
            self.select_resource(self.selected_resource_id)

    def _bind_mousewheel_tree(self, widget, target_canvas=None):
        if target_canvas is None:
            c = widget
            while not isinstance(c, tk.Canvas) and hasattr(c, "master") and c.master:
                c = c.master
            if isinstance(c, tk.Canvas):
                target_canvas = c

        if target_canvas:
            widget.bind("<MouseWheel>", lambda e, c=target_canvas: self._scroll_canvas(e, c))
            widget.bind("<Button-4>", lambda e, c=target_canvas: c.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e, c=target_canvas: c.yview_scroll(1, "units"))

        for child in widget.winfo_children():
            self._bind_mousewheel_tree(child, target_canvas)

    def _scroll_canvas(self, event, canvas):
        import sys
        if sys.platform == "darwin":
            if event.delta != 0:
                canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
