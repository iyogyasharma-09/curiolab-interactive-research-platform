"""
CurioLab — Research Galaxy Module
=================================
Interactive visual knowledge exploration environment mapping relationships
between scientific concepts, disciplines, research topics, and educational monographs.

Features:
- Tkinter Canvas galaxy visualization with dark-space aesthetic and starry particles.
- Concept nodes with domain-specific color coding and glowing halos.
- Interactive pan (mouse drag), zoom (+ / - buttons and mousewheel), and view reset.
- Live concept search, domain filtering, and connected-only node filtering.
- Deep relationship exploration with clickable connected concept pills.
- Seamless integration with Knowledge Library ("Open in Library ➔").
- Direct concept transfer to Discovery Journal ("Add to Discovery Journal ➔").

CONTENT INTEGRITY NOTICE:
All concepts, relationship bridges, and monograph links are designed strictly for
educational modeling and simulated inquiry.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from theme import Theme


# =============================================================================
# DOMAIN COLOR PALETTE & VISUAL STYLING
# =============================================================================
DOMAIN_COLORS = {
    "Quantum Physics": {"accent": "#8B5CF6", "glow": "#A78BFA", "bg": "#1E1338"},
    "Artificial Intelligence": {"accent": "#06B6D4", "glow": "#22D3EE", "bg": "#0B2633"},
    "Neuroscience": {"accent": "#EC4899", "glow": "#F472B6", "bg": "#2E0E22"},
    "Information Theory": {"accent": "#10B981", "glow": "#34D399", "bg": "#0B2E1E"},
    "Computer Vision": {"accent": "#3B82F6", "glow": "#60A5FA", "bg": "#0E1E38"},
    "Cybersecurity": {"accent": "#F59E0B", "glow": "#FBBF24", "bg": "#33220B"},
    "Complexity Science": {"accent": "#F97316", "glow": "#FB923C", "bg": "#331808"},
    "Mathematics": {"accent": "#6366F1", "glow": "#818CF8", "bg": "#151838"},
    "General": {"accent": "#64748B", "glow": "#94A3B8", "bg": "#161D2B"}
}


class ResearchGalaxyView(tk.Frame):
    """
    Research Galaxy interactive knowledge constellation view.
    Renders an interactive Tkinter Canvas graph connected with AppState.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Galaxy transform state (Pan & Zoom)
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._press_x = 0
        self._press_y = 0
        self._is_dragging = False
        self._pressed_node_id = None
        self._redraw_job = None

        # UI Filter & Selection state
        self.search_var = tk.StringVar()
        self.domain_filter_var = tk.StringVar(value="All Domains")
        self.connected_only_var = tk.BooleanVar(value=False)
        self.selected_node_id = None

        # Canvas item tracking
        self.node_canvas_items = {}  # node_id -> list of canvas item IDs
        self.item_to_node_id = {}    # canvas item ID -> node_id
        self.edge_canvas_items = []  # list of edge info dicts

        # Build UI layout
        self._build_header(self)
        self._build_toolbar(self)
        self._build_main_workspace(self)

        # Subscribe to AppState observer
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

        # Initial view fit & selection
        self.after(50, self._initial_center_view)

    # -------------------------------------------------------------------------
    # HEADER & HERO BANNER
    # -------------------------------------------------------------------------
    def _build_header(self, parent):
        top_bar = tk.Frame(parent, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 6))

        breadcrumb = tk.Label(
            top_bar,
            text="Research Galaxy > Epistemic Knowledge Constellation",
            font=("Segoe UI", 9),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED
        )
        breadcrumb.pack(side="left")

        hero = tk.Frame(
            parent,
            bg=Theme.BG_CARD_ELEVATED,
            highlightbackground=Theme.PURPLE,
            highlightthickness=1,
            padx=24,
            pady=14
        )
        hero.pack(fill="x", padx=32, pady=(0, 10))

        tag = tk.Label(
            hero,
            text="🌌 MULTIDISCIPLINARY EPISTEMIC MAPPING • INTERACTIVE CONSTELLATION",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.PURPLE_LIGHT,
            padx=8,
            pady=3
        )
        tag.pack(anchor="w")

        title_lbl = tk.Label(
            hero,
            text="Research Galaxy: Connected Knowledge Constellation",
            font=("Segoe UI", 18, "bold"),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w", pady=(4, 2))

        desc_lbl = tk.Label(
            hero,
            text="Explore multidimensional relationships bridging physics, machine learning, neuroscience, "
                 "information theory, and mathematics. Click nodes to inspect core principles, explore connected "
                 "theories, open linked curriculum monographs, or stage research hypotheses directly into your Discovery Journal.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED,
            fg=Theme.TEXT_SECONDARY,
            wraplength=980,
            justify="left"
        )
        desc_lbl.pack(anchor="w")

    # -------------------------------------------------------------------------
    # EXPLORATION TOOLBAR & CONTROLS
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
        search_box.pack(side="left", padx=(0, 12))

        tk.Label(search_box, text="🔍", font=("Segoe UI", 10), bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(side="left", padx=(0, 6))

        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            relief="flat",
            width=22
        )
        self.search_entry.pack(side="left")
        self.search_var.trace_add("write", lambda *_: self._on_filter_changed())

        clear_lbl = tk.Label(search_box, text="✕", font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, cursor="hand2")
        clear_lbl.pack(side="left", padx=(4, 0))
        clear_lbl.bind("<Button-1>", lambda _: self.search_var.set(""))

        # 2. Domain Filter
        tk.Label(ctrl_bar, text="Domain:", font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        domains = ["All Domains"]
        if hasattr(self.app, "state") and self.app.state:
            domains += self.app.state.get_galaxy_domains()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Galaxy.TCombobox",
                        fieldbackground=Theme.BG_INPUT,
                        background=Theme.BG_CARD,
                        foreground=Theme.TEXT_PRIMARY,
                        arrowcolor=Theme.CYAN,
                        bordercolor=Theme.BORDER_MUTED,
                        darkcolor=Theme.BG_CARD,
                        lightcolor=Theme.BG_CARD)

        self.domain_combo = ttk.Combobox(
            ctrl_bar,
            textvariable=self.domain_filter_var,
            values=domains,
            state="readonly",
            width=18,
            style="Galaxy.TCombobox"
        )
        self.domain_combo.pack(side="left", padx=(0, 12))
        self.domain_combo.bind("<<ComboboxSelected>>", lambda _: self._on_filter_changed())

        # 3. Connected-Only Checkbox
        chk = tk.Checkbutton(
            ctrl_bar,
            text="Connected Only",
            variable=self.connected_only_var,
            command=self._on_filter_changed,
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            selectcolor=Theme.BG_INPUT,
            activebackground=Theme.BG_CARD,
            activeforeground=Theme.CYAN
        )
        chk.pack(side="left", padx=(0, 14))

        # 4. Canvas Navigation Buttons (Zoom & Reset)
        nav_box = tk.Frame(ctrl_bar, bg=Theme.BG_CARD)
        nav_box.pack(side="right")

        zoom_in_btn = tk.Label(
            nav_box,
            text=" ➕ Zoom In ",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        zoom_in_btn.pack(side="left", padx=(0, 6))
        zoom_in_btn.bind("<Button-1>", lambda _: self._zoom_view(1.2))

        zoom_out_btn = tk.Label(
            nav_box,
            text=" ➖ Zoom Out ",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        zoom_out_btn.pack(side="left", padx=(0, 6))
        zoom_out_btn.bind("<Button-1>", lambda _: self._zoom_view(0.8))

        reset_btn = tk.Label(
            nav_box,
            text=" ⟲ Reset View ",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.CYAN,
            highlightbackground=Theme.CYAN,
            highlightthickness=1,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        reset_btn.pack(side="left", padx=(0, 6))
        reset_btn.bind("<Button-1>", lambda _: self._reset_view())

        clear_sel_btn = tk.Label(
            nav_box,
            text=" ✕ Clear Selection ",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        clear_sel_btn.pack(side="left")
        clear_sel_btn.bind("<Button-1>", lambda _: self.select_node(None))

    # -------------------------------------------------------------------------
    # MAIN WORKSPACE (CANVAS + CONCEPT INSPECTOR PANEL)
    # -------------------------------------------------------------------------
    def _build_main_workspace(self, parent):
        workspace = tk.Frame(parent, bg=Theme.BG_ROOT)
        workspace.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        # Right Column: Concept Inspector Detail Panel (pack first on right to guarantee width)
        self.inspector_card = tk.Frame(
            workspace,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1,
            width=390
        )
        self.inspector_card.pack(side="right", fill="y")
        self.inspector_card.pack_propagate(False)

        # Left Column: Tkinter Canvas (Constellation Network, expands to fill remaining space)
        canvas_card = tk.Frame(
            workspace,
            bg=Theme.BG_CARD,
            highlightbackground=Theme.BORDER_SUBTLE,
            highlightthickness=1
        )
        canvas_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.canvas = tk.Canvas(
            canvas_card,
            bg="#070A12",
            highlightthickness=0,
            cursor="fleur"
        )
        self.canvas._is_galaxy_canvas = True
        self.canvas.galaxy_view = self
        self.canvas.pack(fill="both", expand=True)

        # Canvas Interaction Event Bindings
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<ButtonPress-2>", self._on_canvas_press)
        self.canvas.bind("<B2-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-2>", self._on_canvas_release)
        self.canvas.bind("<ButtonPress-3>", self._on_canvas_press)
        self.canvas.bind("<B3-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_canvas_release)
        self.canvas.bind("<MouseWheel>", self._on_canvas_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom_view(1.08, anchor_x=e.x, anchor_y=e.y))
        self.canvas.bind("<Button-5>", lambda e: self._zoom_view(0.92, anchor_x=e.x, anchor_y=e.y))
        self.canvas.bind("<Configure>", lambda _: self._request_redraw())

        # Inspector internal scrollable canvas with smooth scrolling
        self.inspector_scroll_canvas = tk.Canvas(
            self.inspector_card,
            bg=Theme.BG_CARD,
            highlightthickness=0,
            yscrollincrement=1
        )
        self.inspector_scroll_canvas._is_curiolab_scroll_canvas = True
        self.inspector_vbar = ttk.Scrollbar(
            self.inspector_card,
            orient="vertical",
            command=self.inspector_scroll_canvas.yview
        )
        self.inspector_scroll_canvas.configure(yscrollcommand=self.inspector_vbar.set)

        self.inspector_container = tk.Frame(self.inspector_scroll_canvas, bg=Theme.BG_CARD)
        self.inspector_canvas_win = self.inspector_scroll_canvas.create_window(
            (0, 0), window=self.inspector_container, anchor="nw"
        )

        self.inspector_scroll_canvas.pack(side="left", fill="both", expand=True)
        self.inspector_vbar.pack(side="right", fill="y")

        self.inspector_container.bind("<Configure>", self._on_inspector_frame_configure)
        self.inspector_scroll_canvas.bind("<Configure>", self._on_inspector_canvas_configure)

        # Initial inspector render (welcoming placeholder)
        self._render_inspector()

    def _on_inspector_frame_configure(self, event=None):
        self.inspector_scroll_canvas.configure(scrollregion=self.inspector_scroll_canvas.bbox("all"))

    def _on_inspector_canvas_configure(self, event):
        self.inspector_scroll_canvas.itemconfig(self.inspector_canvas_win, width=event.width)

    # -------------------------------------------------------------------------
    # CANVAS TRANSFORM & DRAWING ENGINE
    # -------------------------------------------------------------------------
    def _initial_center_view(self):
        """Calculates initial pan and zoom so all nodes are neatly centered."""
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 50 or ch < 50:
            self.after(50, self._initial_center_view)
            return

        # Canonical bounds are roughly [80..960] x [40..540]
        # Center of bounding box is (520, 290)
        self.pan_x = (cw / 2.0) - (520 * self.zoom)
        self.pan_y = (ch / 2.0) - (290 * self.zoom)
        self._redraw_galaxy()

    def _reset_view(self):
        """Resets zoom and pans view back to center."""
        self.zoom = 1.0
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        self.pan_x = (cw / 2.0) - (520 * self.zoom)
        self.pan_y = (ch / 2.0) - (290 * self.zoom)
        self._redraw_galaxy()

    def _zoom_view(self, factor, anchor_x=None, anchor_y=None):
        """
        Applies smooth incremental zoom.
        If anchor_x/y are provided, zooms anchored at that screen coordinate.
        Otherwise, zooms centered on the canvas midpoint.
        """
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10:
            cw = 800.0
        if ch < 10:
            ch = 600.0

        if anchor_x is None:
            anchor_x = cw / 2.0
        if anchor_y is None:
            anchor_y = ch / 2.0

        min_zoom = 0.35
        max_zoom = 3.20

        new_zoom = max(min_zoom, min(max_zoom, self.zoom * factor))
        if abs(new_zoom - self.zoom) < 0.0005:
            return

        # Anchor formula: Keep the world coordinate under (anchor_x, anchor_y) stationary
        scale = new_zoom / self.zoom
        self.pan_x = anchor_x - (anchor_x - self.pan_x) * scale
        self.pan_y = anchor_y - (anchor_y - self.pan_y) * scale
        self.zoom = new_zoom
        self._request_redraw()

    def _request_redraw(self):
        """Coalesces rapid redraw requests (e.g. during wheel/trackpad scrolling)."""
        if getattr(self, "_redraw_job", None) is not None:
            return
        self._redraw_job = self.after_idle(self._execute_redraw_job)

    def _execute_redraw_job(self):
        self._redraw_job = None
        self._redraw_galaxy()

    def _on_canvas_press(self, event):
        self._press_x = event.x
        self._press_y = event.y
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = False

        # Find if a node was clicked under cursor
        clicked_items = self.canvas.find_withtag("current")
        self._pressed_node_id = None
        for it in clicked_items:
            if it in self.item_to_node_id:
                self._pressed_node_id = self.item_to_node_id[it]
                break

        # Fallback proximity check for touch/trackpad taps
        if not self._pressed_node_id:
            wx, wy = self._screen_to_world(event.x, event.y)
            nodes = self.app.state.get_galaxy_nodes() if hasattr(self.app, "state") and self.app.state else []
            best_node = None
            best_dist = 999999
            for n in nodes:
                d = math.hypot(n.get("x", 0) - wx, n.get("y", 0) - wy)
                if d < best_dist:
                    best_dist = d
                    best_node = n
            if best_node and (best_dist * self.zoom) <= 26.0:
                self._pressed_node_id = best_node["id"]

    def _on_canvas_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        total_dist = math.hypot(event.x - self._press_x, event.y - self._press_y)

        # 4px deadzone distinguishes a deliberate pan from an in-place click
        if total_dist > 4:
            self._is_dragging = True
            self.canvas.config(cursor="fleur")

        if self._is_dragging and (dx != 0 or dy != 0):
            self.pan_x += dx
            self.pan_y += dy
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            # Direct canvas translation for instantaneous, smooth 60fps panning
            self.canvas.move("all", dx, dy)

    def _on_canvas_release(self, event):
        if not self._is_dragging:
            # Click without drag: select clicked node
            if self._pressed_node_id:
                self.select_node(self._pressed_node_id)
        else:
            # Drag completed
            self._is_dragging = False
            self.canvas.config(cursor="fleur")
            self._redraw_galaxy()

    def _on_canvas_mousewheel(self, event):
        """
        Smooth, proportional mouse-wheel and trackpad zoom handler.
        Handles macOS continuous variable delta values and Windows 120-unit increments.
        """
        if abs(event.delta) >= 120:
            # Windows or traditional notched mouse wheel
            ticks = event.delta / 120.0
            factor = math.pow(1.08, ticks)
        else:
            # macOS smooth trackpad or high-resolution mouse wheel
            delta = max(-25.0, min(25.0, float(event.delta)))
            factor = 1.0 + (delta * 0.008)
            factor = max(0.80, min(1.25, factor))

        self._zoom_view(factor, anchor_x=event.x, anchor_y=event.y)
        return "break"

    def _world_to_screen(self, wx, wy):
        sx = wx * self.zoom + self.pan_x
        sy = wy * self.zoom + self.pan_y
        return sx, sy

    def _screen_to_world(self, sx, sy):
        wx = (sx - self.pan_x) / self.zoom
        wy = (sy - self.pan_y) / self.zoom
        return wx, wy

    # -------------------------------------------------------------------------
    # GALAXY NETWORK RENDERING
    # -------------------------------------------------------------------------
    def _redraw_galaxy(self):
        """Renders the dark-space celestial background, epistemic edges, and interactive nodes."""
        if getattr(self, "_redraw_job", None) is not None:
            try:
                self.after_cancel(self._redraw_job)
            except Exception:
                pass
            self._redraw_job = None

        self.canvas.delete("all")
        self.node_canvas_items.clear()
        self.item_to_node_id.clear()

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        if not hasattr(self.app, "state") or not self.app.state:
            return

        nodes = self.app.state.get_galaxy_nodes()
        edges = self.app.state.get_galaxy_edges()

        # 1. Subtle Celestial Background: Faint starry particles & grid dots
        self._draw_celestial_background(cw, ch)

        # Build node lookup table
        node_map = {n["id"]: n for n in nodes}

        # Filter visibility criteria
        q_term = self.search_var.get().strip().lower()
        active_domain = self.domain_filter_var.get()
        connected_only = self.connected_only_var.get()

        selected_node = node_map.get(self.selected_node_id) if self.selected_node_id else None
        connected_ids = set(selected_node.get("related_nodes", [])) if selected_node else set()

        def is_node_visible(node):
            nid = node["id"]
            if q_term:
                c_name = node.get("name") or node.get("label", "")
                match_text = f"{c_name} {node.get('domain', '')} {node.get('summary', '')}".lower()
                if q_term not in match_text:
                    return False
            if active_domain != "All Domains" and node.get("domain") != active_domain:
                return False
            if connected_only and self.selected_node_id:
                if nid != self.selected_node_id and nid not in connected_ids:
                    return False
            return True

        visible_nodes = {n["id"] for n in nodes if is_node_visible(n)}

        # 2. Draw Epistemic Bridge Edges
        for edge in edges:
            src_id = edge.get("source")
            tgt_id = edge.get("target")

            if src_id not in node_map or tgt_id not in node_map:
                continue

            # Check if edge is visible
            src_vis = src_id in visible_nodes
            tgt_vis = tgt_id in visible_nodes

            # If connected_only is on, both must be visible
            if not src_vis and not tgt_vis:
                continue

            src_node = node_map[src_id]
            tgt_node = node_map[tgt_id]

            sx1, sy1 = self._world_to_screen(src_node.get("x", 0), src_node.get("y", 0))
            sx2, sy2 = self._world_to_screen(tgt_node.get("x", 0), tgt_node.get("y", 0))

            # Edge Styling based on active selection
            is_active_edge = False
            edge_color = "#151D2C"
            edge_width = 1.0

            if self.selected_node_id:
                if src_id == self.selected_node_id or tgt_id == self.selected_node_id:
                    is_active_edge = True
                    accent = DOMAIN_COLORS.get(src_node.get("domain"), DOMAIN_COLORS["General"])["accent"]
                    edge_color = accent
                    edge_width = max(2.5, 3.0 * self.zoom)
                else:
                    edge_color = "#101624"
                    edge_width = 1.0
            else:
                if src_vis and tgt_vis:
                    edge_color = "#1E293B"
                    edge_width = max(1.2, 1.5 * self.zoom)
                else:
                    edge_color = "#121824"
                    edge_width = 1.0

            # Draw line on canvas
            line_id = self.canvas.create_line(
                sx1, sy1, sx2, sy2,
                fill=edge_color,
                width=edge_width,
                capstyle="round"
            )

            # If active connected edge, draw glow line underneath
            if is_active_edge:
                glow_col = DOMAIN_COLORS.get(src_node.get("domain"), DOMAIN_COLORS["General"])["glow"]
                self.canvas.create_line(
                    sx1, sy1, sx2, sy2,
                    fill=glow_col,
                    width=edge_width + 3,
                    stipple="gray50" if hasattr(self.canvas, "stipple") else "",
                    capstyle="round"
                )

        # 3. Draw Nodes (in two passes: unselected first, selected last for clean layering)
        unselected_nodes = [n for n in nodes if n["id"] != self.selected_node_id]
        draw_order = unselected_nodes + ([selected_node] if selected_node else [])

        for node in draw_order:
            nid = node["id"]
            is_vis = nid in visible_nodes
            is_sel = (nid == self.selected_node_id)
            is_conn = (nid in connected_ids)

            wx = node.get("x", 0)
            wy = node.get("y", 0)
            sx, sy = self._world_to_screen(wx, wy)

            # Skip if wildly off screen
            if sx < -100 or sx > cw + 100 or sy < -100 or sy > ch + 100:
                continue

            dom_style = DOMAIN_COLORS.get(node.get("domain"), DOMAIN_COLORS["General"])

            # Base node radius scaled by zoom
            base_r = 18.0 * self.zoom
            base_r = max(12.0, min(36.0, base_r))

            # Dimming for non-matching nodes
            if not is_vis:
                opacity_border = "#1E2638"
                opacity_fill = "#0E131F"
                text_col = "#334155"
            else:
                opacity_border = dom_style["accent"]
                opacity_fill = dom_style["bg"]
                text_col = Theme.TEXT_PRIMARY

            item_group = []

            # A. Draw Outer Halo / Selection Ring
            if is_sel:
                # Pulsing selection outer glow
                halo1 = self.canvas.create_oval(
                    sx - (base_r + 14), sy - (base_r + 14),
                    sx + (base_r + 14), sy + (base_r + 14),
                    outline=dom_style["glow"],
                    width=2,
                    dash=(4, 3)
                )
                halo2 = self.canvas.create_oval(
                    sx - (base_r + 7), sy - (base_r + 7),
                    sx + (base_r + 7), sy + (base_r + 7),
                    outline=dom_style["accent"],
                    width=2
                )
                item_group.extend([halo1, halo2])
            elif is_conn:
                # Connected neighbor indicator ring
                conn_ring = self.canvas.create_oval(
                    sx - (base_r + 6), sy - (base_r + 6),
                    sx + (base_r + 6), sy + (base_r + 6),
                    outline=dom_style["accent"],
                    width=1.5,
                    dash=(2, 2)
                )
                item_group.append(conn_ring)

            # B. Main Node Body
            node_circle = self.canvas.create_oval(
                sx - base_r, sy - base_r,
                sx + base_r, sy + base_r,
                fill=opacity_fill,
                outline=opacity_border,
                width=3.0 if (is_sel or is_conn) else 1.8
            )
            item_group.append(node_circle)

            # C. Center Core Dot
            core_r = max(3.0, base_r * 0.35)
            core_color = dom_style["glow"] if (is_sel or is_conn) else dom_style["accent"]
            if not is_vis:
                core_color = "#24324A"

            core_dot = self.canvas.create_oval(
                sx - core_r, sy - core_r,
                sx + core_r, sy + core_r,
                fill=core_color,
                outline=""
            )
            item_group.append(core_dot)

            # D. Concept Name Label
            font_size = max(8, int(9 * self.zoom))
            font_weight = "bold" if is_sel else "normal"
            label_y = sy + base_r + 8

            # Text background pill for readability
            text_str = node.get("name") or node.get("label", "Concept")
            txt_id = self.canvas.create_text(
                sx, label_y,
                text=text_str,
                font=("Segoe UI", font_size, font_weight),
                fill=text_col,
                anchor="n"
            )
            item_group.append(txt_id)

            # Store canvas item references and bind hover events
            self.node_canvas_items[nid] = item_group

            for it in item_group:
                self.item_to_node_id[it] = nid
                self.canvas.tag_bind(it, "<Enter>", lambda _, n=nid: self._on_node_hover_enter(n))
                self.canvas.tag_bind(it, "<Leave>", lambda _, n=nid: self._on_node_hover_leave(n))

    def _draw_celestial_background(self, cw, ch):
        """Draws subtle background coordinates and starry particles for dark space depth."""
        # Fixed pseudo-star constellation coordinates (deterministic)
        star_coords = [
            (0.12, 0.18, 1), (0.24, 0.42, 1.5), (0.35, 0.12, 1),
            (0.52, 0.28, 2), (0.68, 0.14, 1), (0.82, 0.33, 1.5),
            (0.91, 0.22, 1), (0.15, 0.72, 1.5), (0.28, 0.85, 1),
            (0.44, 0.68, 2), (0.58, 0.88, 1), (0.74, 0.65, 1.5),
            (0.85, 0.82, 1), (0.95, 0.61, 1), (0.05, 0.48, 1)
        ]
        for rx, ry, sz in star_coords:
            px = rx * cw
            py = ry * ch
            self.canvas.create_oval(
                px - sz, py - sz, px + sz, py + sz,
                fill="#1E293B", outline=""
            )

    def _on_node_hover_enter(self, node_id):
        if not getattr(self, "_is_dragging", False):
            self.canvas.config(cursor="hand2")

    def _on_node_hover_leave(self, node_id):
        if not getattr(self, "_is_dragging", False):
            self.canvas.config(cursor="fleur")

    # -------------------------------------------------------------------------
    # SELECTION & RELATIONSHIP EXPLORATION
    # -------------------------------------------------------------------------
    def select_node(self, node_id):
        """
        Selects a concept node:
        1. Highlights active node & connected edges on canvas.
        2. Populates Concept Inspector with description, bridges, and monographs.
        """
        self.selected_node_id = node_id
        self._redraw_galaxy()
        self._render_inspector()

    def center_on_node(self, node_id):
        """Centers the canvas view smoothly onto the requested node."""
        if not hasattr(self.app, "state") or not self.app.state:
            return
        node = self.app.state.get_galaxy_node(node_id)
        if not node:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        wx = node.get("x", 500)
        wy = node.get("y", 300)

        self.pan_x = (cw / 2.0) - (wx * self.zoom)
        self.pan_y = (ch / 2.0) - (wy * self.zoom)
        self.select_node(node_id)

    def _on_filter_changed(self):
        self._redraw_galaxy()

    # -------------------------------------------------------------------------
    # CONCEPT INSPECTOR PANEL
    # -------------------------------------------------------------------------
    def _render_inspector(self):
        """Builds the rich right-hand inspection view for the selected node."""
        for child in self.inspector_container.winfo_children():
            child.destroy()

        if not hasattr(self.app, "state") or not self.app.state:
            return

        node = self.app.state.get_galaxy_node(self.selected_node_id) if self.selected_node_id else None

        if not node:
            # Welcoming Constellation Guide State
            self._render_inspector_empty()
            return

        domain = node.get("domain", "General")
        dom_style = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["General"])

        # 1. Domain & Difficulty Header Badges
        top_badge_row = tk.Frame(self.inspector_container, bg=Theme.BG_CARD)
        top_badge_row.pack(fill="x", padx=18, pady=(18, 8))

        dom_pill = tk.Label(
            top_badge_row,
            text=f"◈ {domain.upper()}",
            font=("Segoe UI", 7, "bold"),
            bg=dom_style["bg"],
            fg=dom_style["glow"],
            padx=8,
            pady=3
        )
        dom_pill.pack(side="left")

        diff = node.get("difficulty", "Standard")
        diff_pill = tk.Label(
            top_badge_row,
            text=f"LEVEL: {diff.upper()}",
            font=("Segoe UI", 7, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_MUTED,
            padx=6,
            pady=3
        )
        diff_pill.pack(side="right")

        # 2. Concept Name
        concept_title = node.get("name") or node.get("label", "Concept")
        title_lbl = tk.Label(
            self.inspector_container,
            text=concept_title,
            font=("Segoe UI", 16, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY,
            wraplength=350,
            justify="left"
        )
        title_lbl.pack(anchor="w", padx=18, pady=(0, 6))

        # 3. Action Buttons Row (Add to Journal & Center)
        act_row = tk.Frame(self.inspector_container, bg=Theme.BG_CARD)
        act_row.pack(fill="x", padx=18, pady=(0, 14))

        journal_btn = tk.Label(
            act_row,
            text="📓 Add to Discovery Journal ➔",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.PURPLE,
            fg=Theme.TEXT_ON_ACCENT,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        journal_btn.pack(side="left", padx=(0, 8))
        journal_btn.bind("<Button-1>", lambda _: self._add_to_discovery_journal(node["id"]))

        center_btn = tk.Label(
            act_row,
            text="🎯 Center",
            font=("Segoe UI", 8, "bold"),
            bg=Theme.BG_INPUT,
            fg=Theme.CYAN,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=10,
            pady=6,
            cursor="hand2"
        )
        center_btn.pack(side="left")
        center_btn.bind("<Button-1>", lambda _: self.center_on_node(node["id"]))

        # 4. Educational Explanation / Summary
        tk.Label(
            self.inspector_container,
            text="🔬 Educational Foundation",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(0, 6))

        summary_box = tk.Frame(
            self.inspector_container,
            bg=Theme.BG_INPUT,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1,
            padx=12,
            pady=10
        )
        summary_box.pack(fill="x", padx=18, pady=(0, 14))

        tk.Label(
            summary_box,
            text=node.get("summary", ""),
            font=("Segoe UI", 9),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_SECONDARY,
            wraplength=325,
            justify="left"
        ).pack(anchor="w")

        # 5. Connected Epistemic Concepts & Relationship Bridges
        tk.Label(
            self.inspector_container,
            text="🔗 Connected Concepts & Epistemic Bridges",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(0, 6))

        connected_nodes = self.app.state.get_connected_nodes(node["id"])
        edges = self.app.state.get_galaxy_edges()

        if connected_nodes:
            conn_list_box = tk.Frame(self.inspector_container, bg=Theme.BG_CARD)
            conn_list_box.pack(fill="x", padx=18, pady=(0, 14))

            for c_node in connected_nodes:
                cid = c_node["id"]
                c_dom = c_node.get("domain", "General")
                c_style = DOMAIN_COLORS.get(c_dom, DOMAIN_COLORS["General"])

                # Find relationship bridge metadata if available
                bridge_label = ""
                for e in edges:
                    if (e.get("source") == node["id"] and e.get("target") == cid) or \
                       (e.get("source") == cid and e.get("target") == node["id"]):
                        bridge_label = e.get("summary", "")
                        break

                c_card = tk.Frame(
                    conn_list_box,
                    bg=Theme.BG_INPUT,
                    highlightbackground=Theme.BORDER_MUTED,
                    highlightthickness=1,
                    padx=10,
                    pady=8,
                    cursor="hand2"
                )
                c_card.pack(fill="x", pady=(0, 6))

                # Header of connected card
                c_head = tk.Frame(c_card, bg=Theme.BG_INPUT)
                c_head.pack(fill="x")

                c_conn_name = c_node.get("name") or c_node.get("label", "Concept")
                c_name_lbl = tk.Label(
                    c_head,
                    text=f"➔ {c_conn_name}",
                    font=("Segoe UI", 9, "bold"),
                    bg=Theme.BG_INPUT,
                    fg=c_style["accent"]
                )
                c_name_lbl.pack(side="left")

                c_dom_lbl = tk.Label(
                    c_head,
                    text=c_dom,
                    font=("Segoe UI", 7),
                    bg=Theme.BG_INPUT,
                    fg=Theme.TEXT_MUTED
                )
                c_dom_lbl.pack(side="right")

                if bridge_label:
                    tk.Label(
                        c_card,
                        text=bridge_label,
                        font=("Segoe UI", 8),
                        bg=Theme.BG_INPUT,
                        fg=Theme.TEXT_SECONDARY,
                        wraplength=315,
                        justify="left"
                    ).pack(anchor="w", pady=(3, 0))

                # Bind click to explore connected concept
                for w in [c_card, c_head, c_name_lbl, c_dom_lbl]:
                    w.bind("<Button-1>", lambda _, nid=cid: self.center_on_node(nid))
        else:
            tk.Label(
                self.inspector_container,
                text="No direct bridges configured for this node.",
                font=("Segoe UI", 8),
                bg=Theme.BG_CARD,
                fg=Theme.TEXT_MUTED
            ).pack(anchor="w", padx=18, pady=(0, 14))

        # 6. Connected Knowledge Library Monographs
        tk.Label(
            self.inspector_container,
            text="📚 Linked Curriculum Monographs",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(0, 6))

        res_refs = node.get("resource_refs", [])
        lib_resources = self.app.state.library_resources if hasattr(self.app, "state") and self.app.state else []
        matched_resources = [r for r in lib_resources if r.get("id") in res_refs]

        if matched_resources:
            res_box = tk.Frame(self.inspector_container, bg=Theme.BG_CARD)
            res_box.pack(fill="x", padx=18, pady=(0, 20))

            for res in matched_resources:
                rid = res.get("id")
                r_card = tk.Frame(
                    res_box,
                    bg=Theme.BG_INPUT,
                    highlightbackground=Theme.BORDER_MUTED,
                    highlightthickness=1,
                    padx=10,
                    pady=8
                )
                r_card.pack(fill="x", pady=(0, 8))

                tk.Label(
                    r_card,
                    text=res.get("title", "Monograph"),
                    font=("Segoe UI", 9, "bold"),
                    bg=Theme.BG_INPUT,
                    fg=Theme.TEXT_PRIMARY,
                    wraplength=310,
                    justify="left"
                ).pack(anchor="w")

                tk.Label(
                    r_card,
                    text=f"Curator: {res.get('curator', 'CurioLab')} • Year: {res.get('year', 2026)}",
                    font=("Segoe UI", 7),
                    bg=Theme.BG_INPUT,
                    fg=Theme.TEXT_MUTED
                ).pack(anchor="w", pady=(2, 4))

                eq = res.get("key_equation")
                if eq:
                    eq_lbl = tk.Label(
                        r_card,
                        text=f"Eq: {eq}",
                        font=("Consolas", 8),
                        bg=Theme.BG_CARD,
                        fg=Theme.CYAN_BRIGHT,
                        padx=6,
                        pady=2
                    )
                    eq_lbl.pack(anchor="w", pady=(0, 6))

                open_btn = tk.Label(
                    r_card,
                    text="📖 Open in Library ➔",
                    font=("Segoe UI", 8, "bold"),
                    bg=Theme.TEAL,
                    fg=Theme.BG_ROOT,
                    padx=10,
                    pady=4,
                    cursor="hand2"
                )
                open_btn.pack(anchor="e")
                open_btn.bind("<Button-1>", lambda _, r=rid: self._open_monograph_in_library(r))
        else:
            no_res_box = tk.Frame(
                self.inspector_container,
                bg=Theme.BG_INPUT,
                highlightbackground=Theme.BORDER_MUTED,
                highlightthickness=1,
                padx=12,
                pady=10
            )
            no_res_box.pack(fill="x", padx=18, pady=(0, 20))

            tk.Label(
                no_res_box,
                text="No direct monograph linked to this concept. Browse all available educational resources in the Knowledge Library.",
                font=("Segoe UI", 8),
                bg=Theme.BG_INPUT,
                fg=Theme.TEXT_MUTED,
                wraplength=315,
                justify="left"
            ).pack(anchor="w", pady=(0, 6))

            browse_btn = tk.Label(
                no_res_box,
                text="Explore Knowledge Library ➔",
                font=("Segoe UI", 8, "bold"),
                bg=Theme.BG_CARD,
                fg=Theme.CYAN,
                padx=8,
                pady=4,
                cursor="hand2"
            )
            browse_btn.pack(anchor="w")
            browse_btn.bind("<Button-1>", lambda _: self.app.navigate_to("Knowledge Library"))

        self.inspector_scroll_canvas.yview_moveto(0)

    def _render_inspector_empty(self):
        """Displays guidance when no concept node is currently selected."""
        p_frame = tk.Frame(self.inspector_container, bg=Theme.BG_CARD, padx=20, pady=24)
        p_frame.pack(fill="both", expand=True)

        tk.Label(
            p_frame,
            text="🌌",
            font=("Segoe UI", 36),
            bg=Theme.BG_CARD
        ).pack(pady=(12, 8))

        tk.Label(
            p_frame,
            text="Constellation Explorer",
            font=("Segoe UI", 14, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(pady=(0, 6))

        tk.Label(
            p_frame,
            text="Select any concept node in the galaxy constellation to inspect educational principles, "
                 "explore cross-disciplinary epistemic bridges, and view linked curriculum monographs.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_SECONDARY,
            wraplength=310,
            justify="center"
        ).pack(pady=(0, 16))

        # Scientific Domains Breakdown Legend
        tk.Label(
            p_frame,
            text="Scientific Domains & Taxonomy",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(8, 8))

        domains_box = tk.Frame(p_frame, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=12, pady=10)
        domains_box.pack(fill="x")

        for dom, style in DOMAIN_COLORS.items():
            if dom == "General":
                continue
            d_row = tk.Frame(domains_box, bg=Theme.BG_INPUT)
            d_row.pack(fill="x", pady=2)

            dot = tk.Label(d_row, text="●", font=("Segoe UI", 9), bg=Theme.BG_INPUT, fg=style["accent"])
            dot.pack(side="left", padx=(0, 6))

            d_lbl = tk.Label(d_row, text=dom, font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)
            d_lbl.pack(side="left")

    # -------------------------------------------------------------------------
    # INTEGRATION ACTIONS (LIBRARY & JOURNAL)
    # -------------------------------------------------------------------------
    def _open_monograph_in_library(self, resource_id):
        """Switches navigation to Knowledge Library and selects the resource."""
        self.app.navigate_to("Knowledge Library")
        lib_page = self.app.pages.get("Knowledge Library")
        if lib_page and hasattr(lib_page, "select_resource"):
            if hasattr(lib_page, "reset_all_filters"):
                lib_page.reset_all_filters()
            lib_page.select_resource(resource_id)

    def _add_to_discovery_journal(self, node_id):
        """
        Transfers concept metadata into a new Discovery Journal draft:
        1. Calls AppState.generate_concept_journal_draft(node_id).
        2. Sets AppState.pending_journal_draft.
        3. Navigates to Discovery Journal for user review and saving.
        """
        if not hasattr(self.app, "state") or not self.app.state:
            return

        draft = self.app.state.generate_concept_journal_draft(node_id)
        if not draft:
            messagebox.showwarning("Transfer Warning", "Could not generate journal draft for this concept.")
            return

        self.app.state.pending_journal_draft = draft

        # Log notification
        self.app.state.notifications.insert(0, {
            "id": f"notif_concept_draft_{node_id}",
            "title": "🌌 Concept Transferred to Journal",
            "desc": f"Transferred research premise for '{draft['title']}' to Discovery Journal.",
            "timestamp": "Just now",
            "accent": Theme.PURPLE,
            "read": False
        })
        self.app.state.notify()

        # Switch to Discovery Journal
        self.app.navigate_to("Discovery Journal")

    def _on_app_state_changed(self):
        """Callback from AppState observer."""
        self._redraw_galaxy()
        if self.selected_node_id:
            self._render_inspector()
