"""
CurioLab — An Interactive Research & Discovery Platform
======================================================
Desktop GUI Application built with Python and Tkinter.

Features:
- Dark futuristic research-laboratory theme
- Fixed left sidebar navigation with 8 modules
- Dynamic top header with page info, search, notifications, and user profile
- Discovery Hub dashboard with statistics, quick navigation, recent discoveries,
  interactive "Today's Curiosity" quantum entropy generator, and activity charts
- Dedicated introductory views for all 7 other lab modules
- Zero external dependencies — runs on standard Python 3 with Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import datetime


# =============================================================================
# COLOR PALETTE & DESIGN SYSTEM
# =============================================================================
class Theme:
    """Futuristic research-laboratory dark color palette."""
    # Backgrounds
    BG_ROOT = "#090D16"         # Deepest obsidian navy (main window)
    BG_SIDEBAR = "#06080F"      # Midnight black-navy (fixed sidebar)
    BG_HEADER = "#0B101D"       # Top header bar
    BG_CARD = "#111726"         # Standard card background
    BG_CARD_HOVER = "#172033"   # Card hover state
    BG_CARD_ELEVATED = "#151D2E"# Elevated card surface
    BG_INPUT = "#0D1322"        # Form and search inputs

    # Borders & Dividers
    BORDER_SUBTLE = "#1C2638"   # Very subtle card outline
    BORDER_MUTED = "#24324A"    # Standard border
    BORDER_GLOW = "#38BDF8"     # Focused / accent border glow

    # Vibrant Futuristic Accents
    CYAN = "#06B6D4"            # Primary brand cyan
    CYAN_BRIGHT = "#22D3EE"     # Bright cyan glow
    TEAL = "#14B8A6"            # Lab teal
    PURPLE = "#8B5CF6"          # Cosmic purple
    PURPLE_LIGHT = "#A78BFA"    # Light lavender purple
    BLUE = "#3B82F6"            # Plasma blue
    EMERALD = "#10B981"         # Success / active emerald
    AMBER = "#F59E0B"           # Warning / attention amber
    ROSE = "#F43F5E"            # Red / critical alert

    # Typography Colors
    TEXT_PRIMARY = "#F8FAFC"    # Crisp pure off-white for headings
    TEXT_SECONDARY = "#94A3B8"  # Slate silver for body and subtitles
    TEXT_MUTED = "#64748B"      # Darker slate for captions and hints
    TEXT_ON_ACCENT = "#FFFFFF"  # Pure white on colored buttons


# =============================================================================
# REUSABLE CUSTOM WIDGETS
# =============================================================================

class ModernButton(tk.Frame):
    """
    A custom styled button with hover animations and smooth rounded pill feel.
    """
    def __init__(self, parent, text, command=None, bg_color=Theme.BLUE,
                 hover_color=None, text_color=Theme.TEXT_ON_ACCENT,
                 font=("Segoe UI", 10, "bold"), padx=16, pady=8,
                 icon="", width=None, cursor="hand2"):
        super().__init__(parent, bg=bg_color, cursor=cursor)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color or self._adjust_color(bg_color)
        self.text_color = text_color

        # Configure border highlight for flat modern aesthetic
        self.config(highlightbackground=self.bg_color, highlightthickness=1)

        display_text = f"{icon}  {text}".strip() if icon else text
        self.label = tk.Label(
            self,
            text=display_text,
            bg=bg_color,
            fg=text_color,
            font=font,
            padx=padx,
            pady=pady,
            cursor=cursor
        )
        if width:
            self.label.config(width=width)
        self.label.pack(fill="both", expand=True)

        # Bind hover and click events
        for widget in (self, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _adjust_color(self, hex_color):
        """Generates a slightly brighter or vibrant hover color."""
        if hex_color == Theme.BLUE:
            return "#60A5FA"
        if hex_color == Theme.CYAN:
            return Theme.CYAN_BRIGHT
        if hex_color == Theme.PURPLE:
            return Theme.PURPLE_LIGHT
        if hex_color == Theme.TEAL:
            return "#2DD4BF"
        if hex_color == Theme.BG_CARD:
            return Theme.BG_CARD_HOVER
        return hex_color

    def _on_enter(self, _):
        self.config(bg=self.hover_color, highlightbackground=self.hover_color)
        self.label.config(bg=self.hover_color)

    def _on_leave(self, _):
        self.config(bg=self.bg_color, highlightbackground=self.bg_color)
        self.label.config(bg=self.bg_color)

    def _on_click(self, _):
        if self.command:
            self.command()


class StatCard(tk.Frame):
    """
    Futuristic statistic card with colored accent bar, metric value,
    icon, descriptive label, and progress trend badge.
    """
    def __init__(self, parent, title, value, icon, subtitle,
                 accent_color=Theme.CYAN, trend="+12% this week"):
        super().__init__(parent, bg=Theme.BG_CARD,
                         highlightbackground=Theme.BORDER_SUBTLE,
                         highlightthickness=1, padx=20, pady=18)
        self.accent_color = accent_color

        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Top row: Icon and Trend Pill
        top_row = tk.Frame(self, bg=Theme.BG_CARD)
        top_row.pack(fill="x", anchor="w")

        icon_lbl = tk.Label(top_row, text=icon, font=("Segoe UI", 18),
                            bg=Theme.BG_CARD, fg=accent_color)
        icon_lbl.pack(side="left")

        trend_lbl = tk.Label(top_row, text=f" ● {trend} ",
                             font=("Segoe UI", 8, "bold"),
                             bg=Theme.BG_INPUT, fg=Theme.EMERALD,
                             padx=6, pady=2)
        trend_lbl.pack(side="right")

        # Large Metric Value
        val_lbl = tk.Label(self, text=value, font=("Segoe UI", 26, "bold"),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        val_lbl.pack(anchor="w", pady=(8, 2))

        # Title / Metric Name
        title_lbl = tk.Label(self, text=title, font=("Segoe UI", 11, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        title_lbl.pack(anchor="w")

        # Subtitle / Context
        sub_lbl = tk.Label(self, text=subtitle, font=("Segoe UI", 9),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        sub_lbl.pack(anchor="w", pady=(3, 0))

        # Bottom subtle accent line
        self.accent_line = tk.Frame(self, bg=accent_color, height=3)
        self.accent_line.pack(fill="x", pady=(14, 0))

        self.child_labels = [top_row, icon_lbl, trend_lbl, val_lbl, title_lbl, sub_lbl]
        for child in self.child_labels:
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=Theme.BG_CARD_HOVER, highlightbackground=self.accent_color)
        for child in self.child_labels:
            if child.cget("text") and "●" in child.cget("text"):
                continue  # keep trend pill bg
            child.config(bg=Theme.BG_CARD_HOVER)

    def _on_leave(self, _):
        self.config(bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE)
        for child in self.child_labels:
            if child.cget("text") and "●" in child.cget("text"):
                continue
            child.config(bg=Theme.BG_CARD)


class ScrollableFrame(tk.Frame):
    """
    A smooth scrollable container using Canvas and Scrollbar.
    Automatically resizes child width to prevent horizontal overflow.
    Supports Windows mousewheel scrolling.
    """
    def __init__(self, parent, bg=Theme.BG_ROOT, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0)
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

        # Dynamically resize inner frame width to match canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel binding
        self.bind_mousewheel(self)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        # Windows event.delta is typically 120 or -120
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self.bind_mousewheel(child)


# =============================================================================
# NOTIFICATION DROPDOWN / MODAL
# =============================================================================
class NotificationPopup(tk.Toplevel):
    """Futuristic laboratory notification center dropdown."""
    def __init__(self, parent, x, y, on_clear_callback=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=Theme.BG_CARD_ELEVATED)
        self.geometry(f"360x380+{x}+{y}")
        self.attributes("-topmost", True)
        self.on_clear = on_clear_callback

        # Border wrapper
        wrapper = tk.Frame(self, bg=Theme.BG_CARD_ELEVATED,
                           highlightbackground=Theme.BORDER_GLOW,
                           highlightthickness=1, padx=16, pady=14)
        wrapper.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        hdr.pack(fill="x", pady=(0, 10))

        title = tk.Label(hdr, text="🔔 Lab Notifications", font=("Segoe UI", 11, "bold"),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        title.pack(side="left")

        close_btn = tk.Label(hdr, text="✕", font=("Segoe UI", 10, "bold"),
                             bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.destroy())

        # Notification items
        items = [
            ("⚡ Quantum Simulation Finished", "Wave packet dispersion simulation #42 converged at 99.8% precision.", "10m ago", Theme.CYAN),
            ("🔍 Detective Case Solved", "Dr. Vance concluded investigation 'The Solar Wind Particle Anomaly'.", "1h ago", Theme.PURPLE),
            ("📚 New Knowledge Paper", "'Topological Insulators & Quantum Computing' added to library.", "3h ago", Theme.TEAL),
            ("💡 Discovery Recorded", "'Neural Synchrony in Collective Problem Solving' peer reviewed.", "Yesterday", Theme.EMERALD),
        ]

        for n_title, n_desc, n_time, color in items:
            card = tk.Frame(wrapper, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=10, pady=8)
            card.pack(fill="x", pady=4)

            t_lbl = tk.Label(card, text=n_title, font=("Segoe UI", 9, "bold"),
                             bg=Theme.BG_CARD, fg=color, anchor="w")
            t_lbl.pack(fill="x")

            d_lbl = tk.Label(card, text=n_desc, font=("Segoe UI", 8),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=310, justify="left")
            d_lbl.pack(anchor="w", pady=(2, 2))

            time_lbl = tk.Label(card, text=n_time, font=("Segoe UI", 7),
                                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            time_lbl.pack(anchor="e")

        # Footer action
        clear_btn = tk.Label(wrapper, text="Clear all notifications",
                             font=("Segoe UI", 9, "underline"),
                             bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN, cursor="hand2")
        clear_btn.pack(anchor="center", pady=(10, 0))
        clear_btn.bind("<Button-1>", self._clear_all)

        # Auto-dismiss on click outside
        self.bind("<FocusOut>", lambda _: self.destroy())
        self.focus_set()

    def _clear_all(self, _):
        if self.on_clear:
            self.on_clear()
        self.destroy()


# =============================================================================
# DISCOVERY HUB (DEFAULT MAIN DASHBOARD)
# =============================================================================
class DiscoveryHubView(tk.Frame):
    """
    Main dashboard page:
    - Welcome hero banner
    - 4 Statistic summary cards
    - 4 Quick Exploration module jump cards
    - Recent discoveries feed
    - Today's Curiosity interactive quantum entropy section
    - Laboratory activity graph & progress indicators
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Scrollable container for dashboard
        self.scroll_frame = ScrollableFrame(self, bg=Theme.BG_ROOT)
        self.scroll_frame.pack(fill="both", expand=True)
        content = self.scroll_frame.scrollable_content

        # Build sections with structured padding
        self._build_welcome_banner(content)
        self._build_statistics_grid(content)
        self._build_main_dashboard_layout(content)

        # Ensure mousewheel scrolls across all created widgets
        self.scroll_frame.bind_mousewheel(content)

    def _build_welcome_banner(self, parent):
        """Visually appealing dark futuristic welcome banner."""
        banner = tk.Frame(parent, bg=Theme.BG_CARD_ELEVATED,
                          highlightbackground=Theme.BORDER_MUTED,
                          highlightthickness=1, padx=30, pady=26)
        banner.pack(fill="x", padx=32, pady=(24, 18))

        # Top tag
        tag = tk.Label(banner, text="◈  DISCOVERY HUB  •  CENTRAL CORE",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        # Heading & Subtitle
        heading = tk.Label(banner, text="Welcome to CurioLab",
                           font=("Segoe UI", 26, "bold"),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        heading.pack(anchor="w", pady=(10, 4))

        subtitle = tk.Label(banner,
                            text="Explore ideas. Experiment with knowledge. Discover something new.",
                            font=("Segoe UI", 12),
                            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY)
        subtitle.pack(anchor="w")

        # Quick action button row inside banner
        btn_row = tk.Frame(banner, bg=Theme.BG_CARD_ELEVATED)
        btn_row.pack(anchor="w", pady=(18, 0))

        ModernButton(btn_row, text="Launch Experiment", icon="🧪",
                     bg_color=Theme.PURPLE,
                     command=lambda: self.app.navigate_to("Experiment Lab")).pack(side="left", padx=(0, 12))

        ModernButton(btn_row, text="Browse Library", icon="📚",
                     bg_color=Theme.BG_CARD, text_color=Theme.CYAN_BRIGHT,
                     hover_color=Theme.BORDER_MUTED,
                     command=lambda: self.app.navigate_to("Knowledge Library")).pack(side="left", padx=(0, 12))

        ModernButton(btn_row, text="Solve Case Dossier", icon="🔍",
                     bg_color=Theme.BG_CARD, text_color=Theme.TEAL,
                     hover_color=Theme.BORDER_MUTED,
                     command=lambda: self.app.navigate_to("Research Detective")).pack(side="left")

    def _build_statistics_grid(self, parent):
        """Displays 4 prominent laboratory statistics cards."""
        stats_frame = tk.Frame(parent, bg=Theme.BG_ROOT)
        stats_frame.pack(fill="x", padx=32, pady=(0, 20))

        stats_frame.columnconfigure(0, weight=1, uniform="stat")
        stats_frame.columnconfigure(1, weight=1, uniform="stat")
        stats_frame.columnconfigure(2, weight=1, uniform="stat")
        stats_frame.columnconfigure(3, weight=1, uniform="stat")

        cards_data = [
            ("8 Experiments", "Active & Simulated", "🧪", "Simulated labs", Theme.CYAN, "+2 this month"),
            ("5 Research Cases", "Detective Mysteries", "🔍", "3 resolved, 2 active", Theme.PURPLE, "60% solved"),
            ("24 Knowledge Resources", "Indexed Papers & Books", "📚", "Cross-domain library", Theme.TEAL, "+6 new"),
            ("12 Discoveries", "Documented Breakthroughs", "💡", "Peer-verified findings", Theme.EMERALD, "Top 5%"),
        ]

        for col, (title, sub, icon, ctx, color, trend) in enumerate(cards_data):
            card = StatCard(stats_frame, title=title, value=title.split()[0],
                            icon=icon, subtitle=ctx, accent_color=color, trend=trend)
            card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0 if col == 3 else 8), sticky="nsew")

    def _build_main_dashboard_layout(self, parent):
        """Two-column main layout for Quick Exploration, Discoveries, Curiosity, and Activity."""
        container = tk.Frame(parent, bg=Theme.BG_ROOT)
        container.pack(fill="both", expand=True, padx=32, pady=(0, 30))

        container.columnconfigure(0, weight=6, uniform="dash") # Left 60%
        container.columnconfigure(1, weight=4, uniform="dash") # Right 40%

        left_col = tk.Frame(container, bg=Theme.BG_ROOT)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        right_col = tk.Frame(container, bg=Theme.BG_ROOT)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(14, 0))

        # --- LEFT COLUMN: Quick Exploration & Recent Discoveries ---
        self._build_quick_exploration(left_col)
        self._build_recent_discoveries(left_col)

        # --- RIGHT COLUMN: Today's Curiosity & Activity Overview ---
        self._build_todays_curiosity(right_col)
        self._build_activity_overview(right_col)

    def _build_quick_exploration(self, parent):
        """Quick exploration cards leading directly to core modules."""
        section_hdr = tk.Frame(parent, bg=Theme.BG_ROOT)
        section_hdr.pack(fill="x", pady=(0, 12))

        tk.Label(section_hdr, text="⚡ Quick Exploration",
                 font=("Segoe UI", 14, "bold"),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(side="left")

        tk.Label(section_hdr, text="Direct access to interactive labs",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED).pack(side="left", padx=(10, 0), pady=(3, 0))

        grid = tk.Frame(parent, bg=Theme.BG_ROOT)
        grid.pack(fill="x", pady=(0, 24))
        grid.columnconfigure(0, weight=1, uniform="exp")
        grid.columnconfigure(1, weight=1, uniform="exp")

        modules = [
            ("Experiment Lab", "Test ideas through interactive experiments.", "🧪", Theme.CYAN, 0, 0),
            ("Research Detective", "Solve research-based challenges.", "🔍", Theme.PURPLE, 0, 1),
            ("Knowledge Library", "Explore interesting research resources.", "📚", Theme.TEAL, 1, 0),
            ("Research Galaxy", "Discover connections between ideas.", "🌌", Theme.BLUE, 1, 1),
        ]

        for title, desc, icon, color, r, c in modules:
            card = tk.Frame(grid, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=16, pady=16, cursor="hand2")
            card.grid(row=r, column=c, padx=(0 if c == 0 else 6, 6 if c == 0 else 0),
                      pady=(0 if r == 0 else 12, 12 if r == 0 else 0), sticky="nsew")

            top = tk.Frame(card, bg=Theme.BG_CARD)
            top.pack(fill="x")

            i_lbl = tk.Label(top, text=icon, font=("Segoe UI", 16), bg=Theme.BG_CARD, fg=color)
            i_lbl.pack(side="left")

            arrow = tk.Label(top, text="➔", font=("Segoe UI", 11), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            arrow.pack(side="right")

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 11, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            t_lbl.pack(fill="x", pady=(8, 4))

            d_lbl = tk.Label(card, text=desc, font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=210, justify="left", anchor="w")
            d_lbl.pack(fill="x")

            # Click & hover bindings
            target_page = title
            for widget in (card, top, i_lbl, arrow, t_lbl, d_lbl):
                widget.bind("<Button-1>", lambda _, p=target_page: self.app.navigate_to(p))
                widget.bind("<Enter>", lambda _, cd=card, cl=color: cd.config(
                    bg=Theme.BG_CARD_HOVER, highlightbackground=cl))
                widget.bind("<Leave>", lambda _, cd=card: cd.config(
                    bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE))

    def _build_recent_discoveries(self, parent):
        """Recent discoveries list showing 3 sample entries with inspect buttons."""
        section_hdr = tk.Frame(parent, bg=Theme.BG_ROOT)
        section_hdr.pack(fill="x", pady=(0, 12))

        tk.Label(section_hdr, text="💡 Recent Discoveries",
                 font=("Segoe UI", 14, "bold"),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(side="left")

        tk.Label(section_hdr, text="Verified laboratory findings",
                 font=("Segoe UI", 9),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED).pack(side="left", padx=(10, 0), pady=(3, 0))

        discoveries = [
            {
                "title": "Quantum Superposition in Mesoscopic Resonators",
                "desc": "Observed macroscopic quantum coherence across micro-cantilever resonators cooled to 15 mK, matching Schrödinger wavefunction predictions.",
                "category": "Quantum Physics",
                "date": "Oct 28, 2026",
                "badge_color": Theme.CYAN
            },
            {
                "title": "Neural Synchrony in Collective Problem Solving",
                "desc": "Discovered 40Hz gamma-wave synchronization across collaborative research team brains during breakthrough intellectual moments.",
                "category": "Cognitive Neuroscience",
                "date": "Oct 24, 2026",
                "badge_color": Theme.PURPLE
            },
            {
                "title": "CRISPR-Guided Metabolic Pathway Rewiring",
                "desc": "Synthesized bio-neutral carbon-sequestering enzyme complex using targeted genetic transcription in extremophile bacteria.",
                "category": "Bio-Engineering",
                "date": "Oct 19, 2026",
                "badge_color": Theme.EMERALD
            }
        ]

        for item in discoveries:
            card = tk.Frame(parent, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=18, pady=16)
            card.pack(fill="x", pady=(0, 12))

            # Header row: category badge + date
            hdr = tk.Frame(card, bg=Theme.BG_CARD)
            hdr.pack(fill="x", pady=(0, 6))

            badge = tk.Label(hdr, text=f" {item['category']} ",
                             font=("Segoe UI", 8, "bold"),
                             bg=Theme.BG_INPUT, fg=item["badge_color"],
                             padx=6, pady=2)
            badge.pack(side="left")

            date_lbl = tk.Label(hdr, text=f"📅 {item['date']}",
                                font=("Segoe UI", 8),
                                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            date_lbl.pack(side="right")

            # Title
            t_lbl = tk.Label(card, text=item["title"],
                             font=("Segoe UI", 11, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            t_lbl.pack(fill="x")

            # Description
            d_lbl = tk.Label(card, text=item["desc"],
                             font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=480, justify="left", anchor="w")
            d_lbl.pack(fill="x", pady=(4, 10))

            # Action bar
            act = tk.Frame(card, bg=Theme.BG_CARD)
            act.pack(fill="x")

            inspect_btn = ModernButton(
                act, text="Inspect Dossier", icon="🔬",
                bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                text_color=Theme.CYAN, font=("Segoe UI", 8, "bold"),
                padx=10, pady=4,
                command=lambda t=item["title"], d=item["desc"]: self._show_discovery_modal(t, d)
            )
            inspect_btn.pack(side="right")

    def _show_discovery_modal(self, title, desc):
        """Displays discovery detail modal."""
        messagebox.showinfo(
            "CurioLab Discovery Record",
            f"IDENTIFIER: {title}\n\n"
            f"ABSTRACT:\n{desc}\n\n"
            "STATUS: Peer Reviewed & Archived into Research Galaxy."
        )

    def _build_todays_curiosity(self, parent):
        """
        Today's Curiosity Section:
        Question: 'Can a computer generate truly random numbers?'
        Interactive simulator that lets the user generate simulated quantum entropy.
        """
        card = tk.Frame(parent, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.PURPLE,
                        highlightthickness=1, padx=20, pady=20)
        card.pack(fill="x", pady=(0, 20))

        # Tag
        tag = tk.Label(card, text="💡 TODAY'S CURIOSITY",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        # The exact question specified in requirements
        q_lbl = tk.Label(card,
                         text="Can a computer generate truly random numbers?",
                         font=("Segoe UI", 12, "bold"),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY,
                         wraplength=350, justify="left")
        q_lbl.pack(anchor="w", pady=(10, 6))

        # Scientific context
        expl = tk.Label(
            card,
            text="Standard computers rely on deterministic algorithms (PRNGs) like Mersenne Twister. "
                 "Without external physical entropy (thermal noise, radioactive decay, or quantum photon tunneling), "
                 "numbers are only pseudo-random and theoretically predictable.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=350, justify="left"
        )
        expl.pack(anchor="w", pady=(0, 14))

        # Interactive Entropy Simulation Box
        sim_box = tk.Frame(card, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_MUTED,
                           highlightthickness=1, padx=12, pady=10)
        sim_box.pack(fill="x", pady=(0, 12))

        sim_hdr = tk.Label(sim_box, text="Simulated Quantum Entropy Stream:",
                           font=("Segoe UI", 8, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED)
        sim_hdr.pack(anchor="w")

        self.entropy_display = tk.Label(
            sim_box,
            text="0x8F4A_19E2_B703_9D1C",
            font=("Consolas", 11, "bold"),
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT
        )
        self.entropy_display.pack(anchor="w", pady=(4, 6))

        # Entropy quality gauge
        self.entropy_status = tk.Label(
            sim_box,
            text="Entropy Quality: 99.98% (Atmospheric Fluctuation)",
            font=("Segoe UI", 8),
            bg=Theme.BG_INPUT, fg=Theme.EMERALD
        )
        self.entropy_status.pack(anchor="w")

        # Interactive Trigger Button
        ModernButton(
            card, text="Sample Quantum Fluctuation", icon="⚡",
            bg_color=Theme.PURPLE,
            command=self._generate_entropy
        ).pack(fill="x", pady=(4, 0))

    def _generate_entropy(self):
        """Generates random simulated quantum hex bitstream."""
        hex_parts = [f"{random.randint(0, 0xFFFF):04X}" for _ in range(4)]
        entropy_hex = f"0x{'_'.join(hex_parts)}"
        qualities = [
            ("99.99% (Quantum Photon Tunneling)", Theme.CYAN_BRIGHT),
            ("99.94% (Radioactive Alpha Drift)", Theme.EMERALD),
            ("99.87% (Atmospheric RF Fluctuation)", Theme.TEAL),
            ("100.0% (Zero-Point Field Fluctuation)", Theme.PURPLE_LIGHT),
        ]
        chosen_quality, color = random.choice(qualities)

        self.entropy_display.config(text=entropy_hex)
        self.entropy_status.config(text=f"Entropy Quality: {chosen_quality}", fg=color)

    def _build_activity_overview(self, parent):
        """
        Activity Overview section with a custom Canvas-rendered
        weekly research activity graph and progress meters.
        """
        card = tk.Frame(parent, bg=Theme.BG_CARD,
                        highlightbackground=Theme.BORDER_SUBTLE,
                        highlightthickness=1, padx=20, pady=18)
        card.pack(fill="x")

        # Header
        hdr = tk.Frame(card, bg=Theme.BG_CARD)
        hdr.pack(fill="x", pady=(0, 10))

        tk.Label(hdr, text="📊 Research Activity Overview",
                 font=("Segoe UI", 12, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        tk.Label(hdr, text="This Week",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN,
                 padx=6, pady=2).pack(side="right")

        # Custom Canvas Graph
        canvas_width = 330
        canvas_height = 130
        self.activity_canvas = tk.Canvas(
            card, width=canvas_width, height=canvas_height,
            bg=Theme.BG_INPUT, highlightthickness=0
        )
        self.activity_canvas.pack(fill="x", pady=(4, 14))

        self._draw_activity_chart(canvas_width, canvas_height)

        # Laboratory Velocity Progress Gauges
        gauges = [
            ("Hypothesis Verification Rate", 0.85, Theme.CYAN),
            ("Cross-Disciplinary Synthesis", 0.68, Theme.PURPLE),
            ("Knowledge Ingestion Index", 0.94, Theme.TEAL),
        ]

        for label, pct, color in gauges:
            row = tk.Frame(card, bg=Theme.BG_CARD)
            row.pack(fill="x", pady=4)

            t_lbl = tk.Label(row, text=label, font=("Segoe UI", 8),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY)
            t_lbl.pack(side="left")

            p_lbl = tk.Label(row, text=f"{int(pct * 100)}%", font=("Segoe UI", 8, "bold"),
                             bg=Theme.BG_CARD, fg=color)
            p_lbl.pack(side="right")

            # Mini Progress Bar
            bar_bg = tk.Frame(card, bg=Theme.BG_INPUT, height=5)
            bar_bg.pack(fill="x", pady=(2, 6))

            bar_fill = tk.Frame(bar_bg, bg=color, height=5)
            bar_fill.place(relx=0, rely=0, relwidth=pct, relheight=1.0)

    def _draw_activity_chart(self, w, h):
        """Draws a futuristic research velocity graph on Canvas."""
        c = self.activity_canvas
        c.delete("all")

        # Days of week and research activity scores
        data = [35, 60, 48, 85, 72, 95, 80]
        days = ["M", "T", "W", "T", "F", "S", "S"]
        n = len(data)

        pad_x = 24
        pad_y = 20
        chart_w = w - 2 * pad_x
        chart_h = h - 2 * pad_y - 12

        # Draw horizontal gridlines
        for i in range(3):
            y = pad_y + (chart_h / 2) * i
            c.create_line(pad_x, y, w - pad_x, y, fill=Theme.BORDER_MUTED, dash=(3, 3))

        # Compute point coordinates
        points = []
        for i, val in enumerate(data):
            x = pad_x + (i / (n - 1)) * chart_w
            y = (pad_y + chart_h) - (val / 100) * chart_h
            points.append((x, y))

        # Draw glowing gradient-like polygon under the line
        poly_points = [points[0][0], pad_y + chart_h]
        for x, y in points:
            poly_points.extend([x, y])
        poly_points.extend([points[-1][0], pad_y + chart_h])

        c.create_polygon(poly_points, fill="#0F243A", outline="")

        # Draw main glowing line
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            c.create_line(x1, y1, x2, y2, fill=Theme.CYAN, width=2.5, smooth=True)

        # Draw points and day labels
        for i, (x, y) in enumerate(points):
            c.create_oval(x - 3.5, y - 3.5, x + 3.5, y + 3.5,
                          fill=Theme.CYAN_BRIGHT, outline=Theme.BG_ROOT, width=1.5)
            c.create_text(x, h - 10, text=days[i], fill=Theme.TEXT_MUTED,
                          font=("Segoe UI", 7, "bold"))


# =============================================================================
# EXPERIMENT LAB (INTERACTIVE EXPERIMENTAL SIMULATION SUITE)
# =============================================================================

class ExperimentLabView(tk.Frame):
    """
    Experiment Lab page:
    - Interactive experiment suite with 4 dedicated workspaces:
      1. Overview: Intro banner and 3 feature cards with working Launch buttons
      2. Encryption Playground: Caesar Cipher with encrypt, decrypt, clear, copy, live shift mapping
      3. Neural Network Playground: Single artificial neuron with inputs, weights, bias, sigmoid, and Canvas diagram
      4. Data Visualization Lab: Dynamic Canvas bar chart with min, max, average statistics
    - Full bidirectional navigation:
      - Launch buttons open the corresponding experiment workspace.
      - "← Back to Experiments" buttons return to Overview.
      - Persistent top sub-navigation bar allows instant jumping between experiments.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Active sub-view tracker
        self.current_sub_view = "overview"
        self.sub_views = {}
        self.subnav_buttons = {}

        # 1. Build persistent top sub-navigation bar
        self._build_sub_navbar()

        # 2. Content container for sub-views
        self.content_box = tk.Frame(self, bg=Theme.BG_ROOT)
        self.content_box.pack(fill="both", expand=True)

        # 3. Instantiate all 4 sub-views
        self.sub_views["overview"] = self._create_overview_view()
        self.sub_views["encryption"] = self._create_encryption_view()
        self.sub_views["neural"] = self._create_neural_view()
        self.sub_views["dataviz"] = self._create_dataviz_view()

        # Display default sub-view
        self.switch_to_experiment("overview")

    # -------------------------------------------------------------------------
    # TOP SUB-NAVIGATION BAR & ROUTING
    # -------------------------------------------------------------------------
    def _build_sub_navbar(self):
        """Top tabbed sub-navigation bar for instant switching between experiments."""
        bar = tk.Frame(self, bg=Theme.BG_HEADER,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=24, pady=8)
        bar.pack(fill="x", side="top")

        lbl = tk.Label(bar, text="LAB MODULES:", font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        lbl.pack(side="left", padx=(0, 12))

        tabs = [
            ("overview", "◈ All Experiments", Theme.BLUE),
            ("encryption", "🔐 Encryption Playground", Theme.PURPLE),
            ("neural", "🧠 Neural Network Playground", Theme.CYAN),
            ("dataviz", "📊 Data Visualization Lab", Theme.TEAL),
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
                w.bind("<Button-1>", lambda _, k=key: self.switch_to_experiment(k))
                w.bind("<Enter>", lambda _, bf=btn_frame, bl=btn_lbl, k=key: self._on_tab_hover(bf, bl, k, True))
                w.bind("<Leave>", lambda _, bf=btn_frame, bl=btn_lbl, k=key: self._on_tab_hover(bf, bl, k, False))

            self.subnav_buttons[key] = {
                "frame": btn_frame,
                "label": btn_lbl,
                "accent": accent
            }

    def _on_tab_hover(self, frame, label, key, entering):
        if key != self.current_sub_view:
            if entering:
                frame.config(bg=Theme.BG_CARD)
                label.config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
            else:
                frame.config(bg=Theme.BG_INPUT)
                label.config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

    def switch_to_experiment(self, exp_key):
        """Switches active experiment workspace and updates tab highlights."""
        if exp_key not in self.sub_views:
            return

        # Hide current sub-view
        for v in self.sub_views.values():
            v.pack_forget()

        self.current_sub_view = exp_key

        # Update tab styling
        for k, item in self.subnav_buttons.items():
            if k == exp_key:
                item["frame"].config(bg=Theme.BG_CARD_HOVER,
                                     highlightbackground=item["accent"])
                item["label"].config(bg=Theme.BG_CARD_HOVER,
                                     fg=item["accent"])
            else:
                item["frame"].config(bg=Theme.BG_INPUT,
                                     highlightbackground=Theme.BORDER_MUTED)
                item["label"].config(bg=Theme.BG_INPUT,
                                     fg=Theme.TEXT_SECONDARY)

        # Show target sub-view
        self.sub_views[exp_key].pack(fill="both", expand=True)

        # Ensure responsive rendering on active canvas views
        if exp_key == "neural":
            self.after(50, self._calculate_neuron)
        elif exp_key == "dataviz":
            self.after(50, self._generate_chart)

    # =========================================================================
    # SUB-VIEW 1: OVERVIEW (INTRODUCTION BANNER & EXPERIMENT CARDS)
    # =========================================================================
    def _create_overview_view(self):
        """Builds the main Experiment Lab hub with introduction and 3 launch cards."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # 1. Introduction Banner
        banner = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                          highlightbackground=Theme.BORDER_MUTED,
                          highlightthickness=1, padx=30, pady=24)
        banner.pack(fill="x", padx=32, pady=(20, 20))

        tag = tk.Label(banner, text="◈  EXPERIMENT LAB  •  ALGORITHMIC SANDBOX",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        heading = tk.Label(banner, text="Experiment Lab",
                           font=("Segoe UI", 26, "bold"),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        heading.pack(anchor="w", pady=(10, 4))

        subtitle = tk.Label(banner,
                            text="Test ideas, explore algorithms, and learn by experimenting.",
                            font=("Segoe UI", 12),
                            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY)
        subtitle.pack(anchor="w")

        desc = tk.Label(
            banner,
            text="Welcome to CurioLab's interactive computing laboratory. Choose an experiment below "
                 "to manipulate variables, observe algorithmic state transitions, and analyze mathematical "
                 "outcomes in real time. All calculations run locally in pure Python.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED,
            wraplength=850, justify="left"
        )
        desc.pack(anchor="w", pady=(10, 0))

        # 2. Three Interactive Experiment Cards (Grid)
        cards_section = tk.Frame(content, bg=Theme.BG_ROOT)
        cards_section.pack(fill="x", padx=32, pady=(0, 24))

        cards_section.columnconfigure(0, weight=1, uniform="expcard")
        cards_section.columnconfigure(1, weight=1, uniform="expcard")
        cards_section.columnconfigure(2, weight=1, uniform="expcard")

        exp_data = [
            {
                "key": "encryption",
                "icon": "🔐",
                "accent": Theme.PURPLE,
                "tag": "CRYPTOGRAPHY",
                "title": "Encryption Playground",
                "desc": "Explore classical substitution cryptography. Shift plaintext alphabets through modular arithmetic to encrypt and decrypt secret laboratory communications.",
                "specs": ["Caesar Cipher", "Modular Shift", "Clipboard Sync"],
                "btn_text": "Launch Playground"
            },
            {
                "key": "neural",
                "icon": "🧠",
                "accent": Theme.CYAN,
                "tag": "MACHINE LEARNING",
                "title": "Neural Network Playground",
                "desc": "Simulate a fundamental artificial neuron (perceptron). Adjust synaptic inputs, connection weights, and bias to observe linear summation and non-linear sigmoid activation.",
                "specs": ["Perceptron Unit", "Sigmoid σ(z)", "Canvas Diagram"],
                "btn_text": "Launch Simulator"
            },
            {
                "key": "dataviz",
                "icon": "📊",
                "accent": Theme.TEAL,
                "tag": "DATA SCIENCE",
                "title": "Data Visualization Lab",
                "desc": "Transform raw numerical streams into structured visual bar charts on Tkinter Canvas. Automatically extracts statistical bounds including minimum, maximum, and mean values.",
                "specs": ["Canvas Engine", "Statistical Metrics", "Zero Dependencies"],
                "btn_text": "Launch Visualizer"
            }
        ]

        for col, data in enumerate(exp_data):
            card = tk.Frame(cards_section, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=20, pady=20)
            card.grid(row=0, column=col, padx=(0 if col == 0 else 10, 0 if col == 2 else 10), sticky="nsew")

            # Header row: Tag + Icon
            top = tk.Frame(card, bg=Theme.BG_CARD)
            top.pack(fill="x")

            t_badge = tk.Label(top, text=f" {data['tag']} ", font=("Segoe UI", 8, "bold"),
                               bg=Theme.BG_INPUT, fg=data["accent"], padx=6, pady=2)
            t_badge.pack(side="left")

            i_lbl = tk.Label(top, text=data["icon"], font=("Segoe UI", 18),
                             bg=Theme.BG_CARD, fg=data["accent"])
            i_lbl.pack(side="right")

            # Title
            t_lbl = tk.Label(card, text=data["title"], font=("Segoe UI", 13, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            t_lbl.pack(fill="x", pady=(12, 6))

            # Description
            d_lbl = tk.Label(card, text=data["desc"], font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=260, justify="left", anchor="w")
            d_lbl.pack(fill="x", pady=(0, 14))

            # Specs Pills
            specs_row = tk.Frame(card, bg=Theme.BG_CARD)
            specs_row.pack(fill="x", pady=(0, 18))
            for spec in data["specs"]:
                p = tk.Label(specs_row, text=f"• {spec}", font=("Segoe UI", 7),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
                p.pack(side="left", padx=(0, 8))

            # Working Launch Button
            target_key = data["key"]
            launch_btn = ModernButton(
                card, text=data["btn_text"], icon="⚡",
                bg_color=data["accent"],
                text_color=Theme.BG_ROOT if data["accent"] == Theme.CYAN else Theme.TEXT_ON_ACCENT,
                font=("Segoe UI", 9, "bold"),
                command=lambda k=target_key: self.switch_to_experiment(k)
            )
            launch_btn.pack(fill="x")

        # 3. Scientific Methodology Tip Card
        method_card = tk.Frame(content, bg=Theme.BG_CARD,
                               highlightbackground=Theme.BORDER_SUBTLE,
                               highlightthickness=1, padx=24, pady=18)
        method_card.pack(fill="x", padx=32, pady=(0, 30))

        tk.Label(method_card, text="🔬 CurioLab Experimental Protocol",
                 font=("Segoe UI", 11, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

        steps = [
            ("1. Hypothesize", "Formulate an expected outcome based on physical laws or algorithmic logic.", Theme.CYAN),
            ("2. Parameterize", "Adjust shift constants, synaptic weights, or sample data streams.", Theme.PURPLE),
            ("3. Execute", "Run client-side mathematical routines with instantaneous telemetry feedback.", Theme.TEAL),
            ("4. Deduce", "Compare simulated empirical output with theoretical predictions.", Theme.EMERALD),
        ]

        steps_row = tk.Frame(method_card, bg=Theme.BG_CARD)
        steps_row.pack(fill="x")
        steps_row.columnconfigure(0, weight=1)
        steps_row.columnconfigure(1, weight=1)
        steps_row.columnconfigure(2, weight=1)
        steps_row.columnconfigure(3, weight=1)

        for i, (st, sd, sc) in enumerate(steps):
            box = tk.Frame(steps_row, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=12, pady=10)
            box.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0 if i == 3 else 6), sticky="nsew")

            tk.Label(box, text=st, font=("Segoe UI", 9, "bold"),
                     bg=Theme.BG_INPUT, fg=sc).pack(anchor="w")
            tk.Label(box, text=sd, font=("Segoe UI", 8),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED,
                     wraplength=190, justify="left").pack(anchor="w", pady=(3, 0))

        scroll.bind_mousewheel(content)
        return scroll

    # =========================================================================
    # SUB-VIEW 2: ENCRYPTION PLAYGROUND (CAESAR CIPHER)
    # =========================================================================
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
                     command=self._calculate_neuron).pack(side="left", padx=(0, 10))

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

    def _load_neural_preset(self, x1, w1, x2, w2, bias):
        self.x1_var.set(x1)
        self.w1_var.set(w1)
        self.x2_var.set(x2)
        self.w2_var.set(w2)
        self.bias_var.set(bias)
        self._calculate_neuron()
        self.neural_status.config(text="Loaded preset parameters.", fg=Theme.CYAN)

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
# RESEARCH DETECTIVE (INVESTIGATION SUITE & CASE FILES)
# =============================================================================

class ResearchDetectiveView(tk.Frame):
    """
    Research Detective module:
    - Interactive scientific investigation suite featuring:
      1. Detective HQ Dashboard: Metrics, ranks, progress, and 4 challenge cards
      2. Challenge One: The Cipher Room (3 encrypted mystery levels with clues and answer validation)
      3. Challenge Two: The Data Detective (3 empirical sensor datasets with live statistical outlier detection)
      4. Challenge Three: The Statistical Trap (3 deceptive statistics & visual truncation scenarios)
      5. Challenge Four: The Pattern Mystery (5 mathematical sequence and logic deduction puzzles)
    - Local in-memory session scoring, hint-usage bonus tracking, and ranks
    - Full bidirectional navigation and responsive scrollable workspaces
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # In-memory investigation progress and scoring state
        self.score = 0
        self.completed_challenges = set()
        self.hints_used = set()
        self.current_sub_view = "overview"
        self.sub_views = {}
        self.subnav_buttons = {}

        # 1. Top Sub-Navigation Bar
        self._build_sub_navbar()

        # 2. Sub-views Container
        self.content_box = tk.Frame(self, bg=Theme.BG_ROOT)
        self.content_box.pack(fill="both", expand=True)

        # 3. Instantiate Sub-Views
        self.sub_views["overview"] = self._create_overview_view()
        self.sub_views["cipher"] = self._create_cipher_view()
        self.sub_views["data"] = self._create_data_view()
        self.sub_views["stat"] = self._create_statistical_view()
        self.sub_views["pattern"] = self._create_pattern_view()

        # Display default sub-view
        self.switch_to_challenge("overview")

    # -------------------------------------------------------------------------
    # TOP SUB-NAVIGATION BAR & ROUTING
    # -------------------------------------------------------------------------
    def _build_sub_navbar(self):
        """Top tabbed sub-navigation bar for instant switching between investigation rooms."""
        bar = tk.Frame(self, bg=Theme.BG_HEADER,
                       highlightbackground=Theme.BORDER_SUBTLE,
                       highlightthickness=1, padx=24, pady=8)
        bar.pack(fill="x", side="top")

        lbl = tk.Label(bar, text="DETECTIVE SUITE:", font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        lbl.pack(side="left", padx=(0, 12))

        tabs = [
            ("overview", "◈ Detective HQ", Theme.BLUE),
            ("cipher", "🔐 The Cipher Room", Theme.PURPLE),
            ("data", "🔍 The Data Detective", Theme.CYAN),
            ("stat", "⚠️ The Statistical Trap", Theme.AMBER),
            ("pattern", "🧩 The Pattern Mystery", Theme.TEAL),
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
                w.bind("<Button-1>", lambda _, k=key: self.switch_to_challenge(k))
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

    def switch_to_challenge(self, key):
        """Switches active investigation workspace and updates tab styling and stats."""
        if key not in self.sub_views:
            return

        # Hide current view
        for v in self.sub_views.values():
            v.pack_forget()

        self.current_sub_view = key

        # Update tab styling
        for k, item in self.subnav_buttons.items():
            if k == key:
                item["frame"].config(bg=Theme.BG_CARD_HOVER, highlightbackground=item["accent"])
                item["label"].config(bg=Theme.BG_CARD_HOVER, fg=item["accent"])
            else:
                item["frame"].config(bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED)
                item["label"].config(bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY)

        # Show target sub-view
        self.sub_views[key].pack(fill="both", expand=True)

        # Update metrics when returning to overview
        if key == "overview":
            self._update_overview_metrics()

    def _get_detective_rank(self):
        """Calculates detective rank based on points score."""
        if self.score >= 850:
            return "Master Polymath Detective (Rank IV)", Theme.CYAN_BRIGHT
        elif self.score >= 500:
            return "Senior Investigator (Rank III)", Theme.PURPLE_LIGHT
        elif self.score >= 200:
            return "Research Sleuth (Rank II)", Theme.TEAL
        return "Novice Sleuth (Rank I)", Theme.EMERALD

    def _register_solve(self, challenge_id, feedback_lbl):
        """Awards points and updates session achievement state."""
        base_points = 100
        used_hint = challenge_id in self.hints_used
        bonus_points = 0 if used_hint else 50
        total_award = base_points + bonus_points

        is_new = challenge_id not in self.completed_challenges
        if is_new:
            self.completed_challenges.add(challenge_id)
            self.score += total_award
            self._update_overview_metrics()

            bonus_txt = " (+50 No-Hint Diligence Bonus!)" if bonus_points > 0 else ""
            feedback_lbl.config(
                text=f"✓ CASE SOLVED! Brilliant deduction. Awarded +{total_award} pts{bonus_txt}. Total Score: {self.score} pts.",
                fg=Theme.EMERALD
            )
        else:
            feedback_lbl.config(
                text=f"✓ CASE SOLVED! (Challenge previously cleared. Current Score: {self.score} pts.)",
                fg=Theme.EMERALD
            )

    # =========================================================================
    # SUB-VIEW 1: DETECTIVE HQ DASHBOARD (OVERVIEW)
    # =========================================================================
    def _create_overview_view(self):
        """Builds the main Detective HQ dashboard with metrics and challenge cards."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # 1. Investigation Welcome Banner
        banner = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                          highlightbackground=Theme.PURPLE,
                          highlightthickness=1, padx=30, pady=24)
        banner.pack(fill="x", padx=32, pady=(20, 20))

        tag = tk.Label(banner, text="◈  RESEARCH DETECTIVE  •  CASE SOLVING DIVISION",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        heading = tk.Label(banner, text="Research Detective",
                           font=("Segoe UI", 26, "bold"),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        heading.pack(anchor="w", pady=(10, 4))

        subtitle = tk.Label(banner,
                            text="Question the evidence. Follow the clues. Discover the truth.",
                            font=("Segoe UI", 12),
                            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY)
        subtitle.pack(anchor="w")

        desc = tk.Label(
            banner,
            text="Welcome to CurioLab's investigative headquarters. Put your scientific deduction to the test "
                 "across intercepted cryptography, anomalous laboratory measurements, deceptive statistical traps, "
                 "and recursive logical patterns. Accumulate points, earn bonus ratings, and rise through the detective ranks.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED,
            wraplength=850, justify="left"
        )
        desc.pack(anchor="w", pady=(10, 0))

        # 2. Achievement & Progress Metrics Row (4 Cards)
        metrics_frame = tk.Frame(content, bg=Theme.BG_ROOT)
        metrics_frame.pack(fill="x", padx=32, pady=(0, 24))

        metrics_frame.columnconfigure(0, weight=1, uniform="det_metric")
        metrics_frame.columnconfigure(1, weight=1, uniform="det_metric")
        metrics_frame.columnconfigure(2, weight=1, uniform="det_metric")
        metrics_frame.columnconfigure(3, weight=1, uniform="det_metric")

        # Metric 1: Total Investigation Score
        c1 = tk.Frame(metrics_frame, bg=Theme.BG_CARD,
                      highlightbackground=Theme.BORDER_SUBTLE,
                      highlightthickness=1, padx=16, pady=16)
        c1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        tk.Label(c1, text="🏆 Total Score", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.AMBER).pack(anchor="w")
        self.hq_score_lbl = tk.Label(c1, text="0 pts", font=("Segoe UI", 20, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.hq_score_lbl.pack(anchor="w", pady=(4, 2))
        tk.Label(c1, text="+100 base / +50 no-hint bonus", font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")

        # Metric 2: Completed Cases
        c2 = tk.Frame(metrics_frame, bg=Theme.BG_CARD,
                      highlightbackground=Theme.BORDER_SUBTLE,
                      highlightthickness=1, padx=16, pady=16)
        c2.grid(row=0, column=1, padx=(8, 8), sticky="nsew")
        tk.Label(c2, text="📁 Cases Solved", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN).pack(anchor="w")
        self.hq_solved_lbl = tk.Label(c2, text="0 / 14 Closed", font=("Segoe UI", 20, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.hq_solved_lbl.pack(anchor="w", pady=(4, 2))
        self.hq_progress_bar_lbl = tk.Label(c2, text="0.0% Completion", font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
        self.hq_progress_bar_lbl.pack(anchor="w")

        # Metric 3: Detective Rank
        c3 = tk.Frame(metrics_frame, bg=Theme.BG_CARD,
                      highlightbackground=Theme.BORDER_SUBTLE,
                      highlightthickness=1, padx=16, pady=16)
        c3.grid(row=0, column=2, padx=(8, 8), sticky="nsew")
        tk.Label(c3, text="🎖️ Detective Rank", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.PURPLE_LIGHT).pack(anchor="w")
        self.hq_rank_lbl = tk.Label(c3, text="Novice Sleuth", font=("Segoe UI", 13, "bold"), bg=Theme.BG_CARD, fg=Theme.EMERALD)
        self.hq_rank_lbl.pack(anchor="w", pady=(8, 2))
        tk.Label(c3, text="Rank I • Level 1 Clearance", font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")

        # Metric 4: Diligence / Hint Efficiency
        c4 = tk.Frame(metrics_frame, bg=Theme.BG_CARD,
                      highlightbackground=Theme.BORDER_SUBTLE,
                      highlightthickness=1, padx=16, pady=16)
        c4.grid(row=0, column=3, padx=(8, 0), sticky="nsew")
        tk.Label(c4, text="🎯 Diligence Rating", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEAL).pack(anchor="w")
        self.hq_diligence_lbl = tk.Label(c4, text="100%", font=("Segoe UI", 20, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN_BRIGHT)
        self.hq_diligence_lbl.pack(anchor="w", pady=(4, 2))
        tk.Label(c4, text="Independent deduction rate", font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")

        # 3. Four Challenge Cards (2x2 Grid)
        section_hdr = tk.Frame(content, bg=Theme.BG_ROOT)
        section_hdr.pack(fill="x", padx=32, pady=(0, 12))
        tk.Label(section_hdr, text="🔬 Active Investigation Rooms", font=("Segoe UI", 14, "bold"),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(side="left")
        tk.Label(section_hdr, text="Select a dossier to enter the investigation workspace",
                 font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED).pack(side="left", padx=(10, 0), pady=(3, 0))

        grid = tk.Frame(content, bg=Theme.BG_ROOT)
        grid.pack(fill="x", padx=32, pady=(0, 30))
        grid.columnconfigure(0, weight=1, uniform="chall")
        grid.columnconfigure(1, weight=1, uniform="chall")

        challenges_info = [
            {
                "key": "cipher",
                "icon": "🔐",
                "accent": Theme.PURPLE,
                "diff": "Medium",
                "diff_bg": "#2E1A47",
                "tag": "CRYPTOGRAPHY",
                "title": "Challenge One: The Cipher Room",
                "desc": "Intercepted research transmissions are protected by classical ciphers. Decode confidential scientific messages using letter frequencies and modular shift logic.",
                "total": 3,
                "row": 0, "col": 0
            },
            {
                "key": "data",
                "icon": "🔍",
                "accent": Theme.CYAN,
                "diff": "Medium",
                "diff_bg": "#0B2D3A",
                "tag": "EMPIRICAL AUDITING",
                "title": "Challenge Two: The Data Detective",
                "desc": "Sensors across research laboratories have logged anomalous readings. Cross-examine experimental tables, calculate statistical bounds, and flag corrupt observations.",
                "total": 3,
                "row": 0, "col": 1
            },
            {
                "key": "stat",
                "icon": "⚠️",
                "accent": Theme.AMBER,
                "diff": "Hard",
                "diff_bg": "#3A2807",
                "tag": "DATA FALLACIES",
                "title": "Challenge Three: The Statistical Trap",
                "desc": "Identify deceptive charts with truncated axes, mean vs median distortions, and spurious correlation fallacies designed to mislead scientific researchers.",
                "total": 3,
                "row": 1, "col": 0
            },
            {
                "key": "pattern",
                "icon": "🧩",
                "accent": Theme.TEAL,
                "diff": "Easy to Hard",
                "diff_bg": "#0D2C28",
                "tag": "MATHEMATICAL LOGIC",
                "title": "Challenge Four: The Pattern Mystery",
                "desc": "Solve recursive number sequences, missing matrix terms, and logical deduction puzzles that test your mathematical pattern recognition.",
                "total": 5,
                "row": 1, "col": 1
            }
        ]

        self.overview_card_refs = {}

        for ch in challenges_info:
            card = tk.Frame(grid, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=20, pady=18)
            card.grid(row=ch["row"], column=ch["col"],
                      padx=(0 if ch["col"] == 0 else 8, 8 if ch["col"] == 0 else 0),
                      pady=(0 if ch["row"] == 0 else 14, 14 if ch["row"] == 0 else 0),
                      sticky="nsew")

            top_row = tk.Frame(card, bg=Theme.BG_CARD)
            top_row.pack(fill="x")

            # Difficulty Badge
            d_badge = tk.Label(top_row, text=f" {ch['diff']} ", font=("Segoe UI", 8, "bold"),
                               bg=ch["diff_bg"], fg=ch["accent"], padx=6, pady=2)
            d_badge.pack(side="left")

            i_lbl = tk.Label(top_row, text=ch["icon"], font=("Segoe UI", 16),
                             bg=Theme.BG_CARD, fg=ch["accent"])
            i_lbl.pack(side="right")

            # Title
            t_lbl = tk.Label(card, text=ch["title"], font=("Segoe UI", 12, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            t_lbl.pack(fill="x", pady=(10, 4))

            # Description
            d_lbl = tk.Label(card, text=ch["desc"], font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=380, justify="left", anchor="w")
            d_lbl.pack(fill="x", pady=(0, 14))

            # Progress row
            prog_row = tk.Frame(card, bg=Theme.BG_CARD)
            prog_row.pack(fill="x", pady=(0, 14))

            prog_lbl = tk.Label(prog_row, text="Progress: 0 / 3 Solved", font=("Segoe UI", 8, "bold"),
                                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            prog_lbl.pack(side="left")
            self.overview_card_refs[ch["key"]] = prog_lbl

            # Working Start Investigation Button
            target_k = ch["key"]
            start_btn = ModernButton(
                card, text="Start Investigation", icon="🔍",
                bg_color=ch["accent"],
                text_color=Theme.BG_ROOT if ch["accent"] in (Theme.CYAN, Theme.AMBER) else Theme.TEXT_ON_ACCENT,
                font=("Segoe UI", 9, "bold"),
                command=lambda k=target_k: self.switch_to_challenge(k)
            )
            start_btn.pack(fill="x")

        self._update_overview_metrics()

        scroll.bind_mousewheel(content)
        return scroll

    def _update_overview_metrics(self):
        """Updates the Detective HQ dashboard achievement counters and progress."""
        if not hasattr(self, "hq_score_lbl"):
            return

        total_solved = len(self.completed_challenges)
        pct = (total_solved / 14.0) * 100.0

        self.hq_score_lbl.config(text=f"{self.score} pts")
        self.hq_solved_lbl.config(text=f"{total_solved} / 14 Closed")
        self.hq_progress_bar_lbl.config(text=f"{pct:.1f}% Curriculum Complete")

        rank_title, rank_color = self._get_detective_rank()
        self.hq_rank_lbl.config(text=rank_title, fg=rank_color)

        # Diligence
        if total_solved > 0:
            no_hint_count = sum(1 for cid in self.completed_challenges if cid not in self.hints_used)
            diligence = (no_hint_count / total_solved) * 100.0
            self.hq_diligence_lbl.config(text=f"{diligence:.0f}%")
        else:
            self.hq_diligence_lbl.config(text="100%")

        # Update challenge card progress labels
        cipher_solved = sum(1 for cid in self.completed_challenges if cid.startswith("cipher_"))
        data_solved = sum(1 for cid in self.completed_challenges if cid.startswith("data_"))
        stat_solved = sum(1 for cid in self.completed_challenges if cid.startswith("stat_"))
        pattern_solved = sum(1 for cid in self.completed_challenges if cid.startswith("pattern_"))

        if "cipher" in self.overview_card_refs:
            self.overview_card_refs["cipher"].config(
                text=f"Progress: {cipher_solved} / 3 Solved",
                fg=Theme.EMERALD if cipher_solved == 3 else Theme.TEXT_MUTED
            )
        if "data" in self.overview_card_refs:
            self.overview_card_refs["data"].config(
                text=f"Progress: {data_solved} / 3 Solved",
                fg=Theme.EMERALD if data_solved == 3 else Theme.TEXT_MUTED
            )
        if "stat" in self.overview_card_refs:
            self.overview_card_refs["stat"].config(
                text=f"Progress: {stat_solved} / 3 Solved",
                fg=Theme.EMERALD if stat_solved == 3 else Theme.TEXT_MUTED
            )
        if "pattern" in self.overview_card_refs:
            self.overview_card_refs["pattern"].config(
                text=f"Progress: {pattern_solved} / 5 Solved",
                fg=Theme.EMERALD if pattern_solved == 5 else Theme.TEXT_MUTED
            )

    # =========================================================================
    # SUB-VIEW 2: CHALLENGE ONE - THE CIPHER ROOM
    # =========================================================================
    def _create_cipher_view(self):
        """Builds Challenge One: The Cipher Room with 3 levels and real verification."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Bar: Back to Detective HQ
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Detective HQ", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_challenge("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Research Detective > Challenge One > The Cipher Room",
                              font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.PURPLE,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="🔐 CLASSIFIED DOSSIER #01",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="The Cipher Room: Secret Message Investigation",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="Several sensitive transmissions from CurioLab research wings have been intercepted. "
                 "The messages are obscured by classical substitution ciphers. Analyze frequency cues, "
                 "deduce the secret shift keys, and enter the recovered plaintext message.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        # Level Switcher Bar
        lvl_bar = tk.Frame(content, bg=Theme.BG_CARD,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=16, pady=10)
        lvl_bar.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(lvl_bar, text="SELECT LEVEL:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 12))

        self.cipher_level_buttons = {}
        levels = [
            (1, "Level 1: The Alpha Protocol (Shift 3)", "Easy"),
            (2, "Level 2: Deep Space Telemetry (Shift 7)", "Medium"),
            (3, "Level 3: Quantum Core Log (ROT13)", "Hard"),
        ]

        for lvl_num, lvl_name, lvl_diff in levels:
            btn = tk.Label(lvl_bar, text=f"◈ {lvl_name}", font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                           padx=12, pady=5, cursor="hand2",
                           highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda _, n=lvl_num: self._load_cipher_level(n))
            self.cipher_level_buttons[lvl_num] = btn

        # Main Investigation Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        # Scenario Description Box
        self.cipher_title_lbl = tk.Label(workspace, text="Level 1: The Alpha Protocol",
                                         font=("Segoe UI", 13, "bold"),
                                         bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.cipher_title_lbl.pack(anchor="w")

        self.cipher_scenario_lbl = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
            wraplength=820, justify="left"
        )
        self.cipher_scenario_lbl.pack(anchor="w", pady=(4, 14))

        # Mysterious Encrypted Ciphertext Box
        c_box = tk.Frame(workspace, bg=Theme.BG_INPUT,
                         highlightbackground=Theme.BORDER_MUTED,
                         highlightthickness=1, padx=16, pady=14)
        c_box.pack(fill="x", pady=(0, 16))

        tk.Label(c_box, text="INTERCEPTED CIPHERTEXT TRANSMISSION:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.PURPLE_LIGHT).pack(anchor="w")

        self.cipher_text_display = tk.Label(
            c_box, text="",
            font=("Consolas", 11, "bold"),
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
            wraplength=780, justify="left"
        )
        self.cipher_text_display.pack(anchor="w", pady=(6, 0))

        # Text Field for entering decoded answer
        tk.Label(workspace, text="Enter Decoded Plaintext Message:",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        self.cipher_answer_var = tk.StringVar()
        self.cipher_entry = tk.Entry(
            workspace, textvariable=self.cipher_answer_var,
            bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Consolas", 10),
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1, bd=0, relief="flat"
        )
        self.cipher_entry.pack(fill="x", ipady=8, pady=(0, 14))
        self.cipher_entry.bind("<Return>", lambda _: self._check_cipher_answer())

        # Action Buttons Row
        btn_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        btn_row.pack(fill="x", pady=(0, 12))

        ModernButton(btn_row, text="Check Answer", icon="✓",
                     bg_color=Theme.PURPLE,
                     command=self._check_cipher_answer).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Hint", icon="💡",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.AMBER,
                     command=self._show_cipher_hint).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Reveal Solution", icon="👁️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_MUTED,
                     command=self._reveal_cipher_solution).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Retry", icon="↺",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._retry_cipher_level).pack(side="left")

        # Feedback Banner
        self.cipher_feedback_lbl = tk.Label(
            workspace, text="Inspect the intercepted message above and enter your deduction.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED
        )
        self.cipher_feedback_lbl.pack(anchor="w", pady=(0, 10))

        # Hint Display Box (initially empty)
        self.cipher_hint_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9, "italic"),
            bg=Theme.BG_CARD, fg=Theme.AMBER,
            wraplength=800, justify="left"
        )
        self.cipher_hint_box.pack(anchor="w")

        # Solution Disclosure Frame
        self.cipher_solution_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.CYAN,
            wraplength=800, justify="left"
        )
        self.cipher_solution_box.pack(anchor="w")

        # Cipher Level Data Store
        self.cipher_levels_data = {
            1: {
                "title": "Level 1: The Alpha Protocol",
                "diff": "Easy",
                "scenario": "An encrypted transmission was intercepted from the thermodynamics lab. It appears to be an urgent reminder of the First Law of Thermodynamics encoded with a historical Caesar shift.",
                "cipher": "FXULRODE SURWRFRO: HQHUSB FDQQRW EH FUHDWHG RU GHVWURBHG",
                "target": "CURIOLAB PROTOCOL: ENERGY CANNOT BE CREATED OR DESTROYED",
                "hints": [
                    "Hint 1: The first word 'FXULRODE' corresponds to our laboratory name 'CURIOLAB'.",
                    "Hint 2: Compare 'F' with 'C'. The letter 'F' is 3 positions forward from 'C'. This is a Caesar Shift of 3 (A ➔ D).",
                    "Hint 3: Shift every character backward by 3: F➔C, X➔U, U➔R, L➔I, R➔O, O➔L, D➔A, E➔B."
                ],
                "explanation": "Shift: k = 3 backward (or +23 modulo 26).\nDecoded Plaintext: CURIOLAB PROTOCOL: ENERGY CANNOT BE CREATED OR DESTROYED"
            },
            2: {
                "title": "Level 2: Deep Space Telemetry",
                "diff": "Medium",
                "scenario": "A transmission from the astrophysics sub-station contains fundamental cosmological constants encoded with an advanced offset key.",
                "cipher": "AOL ZWLLK VM SPNOA PZ AOL JVZTPJ ZWLLK SPTPA",
                "target": "THE SPEED OF LIGHT IS THE COSMIC SPEED LIMIT",
                "hints": [
                    "Hint 1: The short word 'AOL' appears twice. What is the most common 3-letter English word?",
                    "Hint 2: 'AOL' decodes to 'THE'. The distance from 'T' forward to 'A' across the alphabet boundary is 7 positions.",
                    "Hint 3: Apply a backward shift of 7 (or forward shift of 19) to decode the full message."
                ],
                "explanation": "Shift: k = 7 backward (or +19 modulo 26).\nDecoded Plaintext: THE SPEED OF LIGHT IS THE COSMIC SPEED LIMIT"
            },
            3: {
                "title": "Level 3: Quantum Core Logbook",
                "diff": "Hard",
                "scenario": "A scrambled entry in the quantum core logbook was encrypted with a symmetric rotation algorithm that is its own mathematical inverse.",
                "cipher": "DHRAGHZ RAGNATYRZrag vf abg ybapny",
                "target": "QUANTUM ENTANGLEMENT IS NOT LOCAL",
                "hints": [
                    "Hint 1: This cipher uses ROT13: rotating by 13 positions (half of the 26-letter English alphabet).",
                    "Hint 2: Because 13 is half of 26, encrypting and decrypting use the exact same transformation!",
                    "Hint 3: 'D' + 13 = 'Q', 'H' + 13 = 'U', 'R' + 13 = 'E', 'A' + 13 = 'N'."
                ],
                "explanation": "Shift: ROT13 (k = 13).\nDecoded Plaintext: QUANTUM ENTANGLEMENT IS NOT LOCAL"
            }
        }

        self.current_cipher_level = 1
        self.cipher_hint_step = 0
        self._load_cipher_level(1)

        scroll.bind_mousewheel(content)
        return scroll

    def _load_cipher_level(self, level_num):
        """Loads selected Cipher Room investigation level."""
        self.current_cipher_level = level_num
        self.cipher_hint_step = 0
        data = self.cipher_levels_data[level_num]

        # Update level tab buttons styling
        for num, btn in self.cipher_level_buttons.items():
            cid = f"cipher_{num}"
            solved = cid in self.completed_challenges
            prefix = "✓ " if solved else "◈ "
            name_base = self.cipher_levels_data[num]["title"]
            if num == level_num:
                btn.config(text=f"{prefix}{name_base}", bg=Theme.BG_CARD_HOVER,
                           fg=Theme.PURPLE_LIGHT, highlightbackground=Theme.PURPLE)
            else:
                btn.config(text=f"{prefix}{name_base}", bg=Theme.BG_INPUT,
                           fg=Theme.EMERALD if solved else Theme.TEXT_SECONDARY,
                           highlightbackground=Theme.BORDER_MUTED)

        self.cipher_title_lbl.config(text=f"{data['title']} ({data['diff']})")
        self.cipher_scenario_lbl.config(text=data["scenario"])
        self.cipher_text_display.config(text=data["cipher"])

        self.cipher_answer_var.set("")
        self.cipher_hint_box.config(text="")
        self.cipher_solution_box.config(text="")

        cid = f"cipher_{level_num}"
        if cid in self.completed_challenges:
            self.cipher_feedback_lbl.config(text="✓ Solved: Case file closed. You can review or re-enter deductions.", fg=Theme.EMERALD)
        else:
            self.cipher_feedback_lbl.config(text="Inspect the ciphertext above, decode the message, and click Check Answer.", fg=Theme.TEXT_MUTED)

    def _check_cipher_answer(self):
        """Validates decoded message answer."""
        data = self.cipher_levels_data[self.current_cipher_level]
        raw_ans = self.cipher_answer_var.get().strip().upper()
        target = data["target"].upper()

        if not raw_ans:
            self.cipher_feedback_lbl.config(text="⚠️ Please enter your decoded plaintext before checking.", fg=Theme.AMBER)
            return

        # Compare whitespace-normalized text
        norm_ans = " ".join(raw_ans.split())
        norm_target = " ".join(target.split())

        if norm_ans == norm_target:
            cid = f"cipher_{self.current_cipher_level}"
            self._register_solve(cid, self.cipher_feedback_lbl)
            self._load_cipher_level(self.current_cipher_level)
        else:
            self.cipher_feedback_lbl.config(
                text="✗ Incorrect decoding. Check letter alignments, capitalization, or request a Hint.",
                fg=Theme.ROSE
            )

    def _show_cipher_hint(self):
        """Progressively displays clues."""
        data = self.cipher_levels_data[self.current_cipher_level]
        hints = data["hints"]
        cid = f"cipher_{self.current_cipher_level}"
        self.hints_used.add(cid)

        if self.cipher_hint_step < len(hints):
            current_hint = hints[self.cipher_hint_step]
            self.cipher_hint_step += 1
            existing = self.cipher_hint_box.cget("text")
            new_text = f"{existing}\n{current_hint}".strip()
            self.cipher_hint_box.config(text=new_text)
            self.cipher_feedback_lbl.config(text="💡 Clue revealed. (Bonus points forfeited for this case file).", fg=Theme.AMBER)
        else:
            self.cipher_feedback_lbl.config(text="All clues have been revealed for this case.", fg=Theme.AMBER)

    def _reveal_cipher_solution(self):
        """Displays complete solution explanation."""
        data = self.cipher_levels_data[self.current_cipher_level]
        cid = f"cipher_{self.current_cipher_level}"
        self.hints_used.add(cid)
        self.cipher_solution_box.config(
            text=f"🔍 DISCLOSED SOLUTION:\n{data['explanation']}"
        )

    def _retry_cipher_level(self):
        """Resets inputs for current cipher level."""
        self.cipher_answer_var.set("")
        self.cipher_hint_box.config(text="")
        self.cipher_solution_box.config(text="")
        self.cipher_hint_step = 0
        self.cipher_feedback_lbl.config(text="Investigation reset. Enter your deduction.", fg=Theme.TEXT_MUTED)

    # =========================================================================
    # SUB-VIEW 3: CHALLENGE TWO - THE DATA DETECTIVE
    # =========================================================================
    def _create_data_view(self):
        """Builds Challenge Two: The Data Detective with 3 empirical dataset cases."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Bar: Back to Detective HQ
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Detective HQ", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_challenge("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Research Detective > Challenge Two > The Data Detective",
                              font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.CYAN,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="🔍 EMPIRICAL AUDIT DOSSIER #02",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="The Data Detective: Anomaly & Outlier Investigation",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="The research team has discovered unusual measurements in a dataset. "
                 "Investigate the recorded values, analyze physical constraints, calculate statistical "
                 "metrics, and identify the suspicious observation.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        # Case Selector Bar
        case_bar = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=16, pady=10)
        case_bar.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(case_bar, text="SELECT CASE:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 12))

        self.data_case_buttons = {}
        cases = [
            (1, "Case 1: Cryogenic Resonator Temperature", "Physical Violation"),
            (2, "Case 2: Particle Velocity Telemetry", "Superluminal Glitch"),
            (3, "Case 3: Microbial Culture Density", "Decimal Entry Error"),
        ]

        for c_num, c_name, c_type in cases:
            btn = tk.Label(case_bar, text=f"◈ {c_name}", font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                           padx=12, pady=5, cursor="hand2",
                           highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda _, n=c_num: self._load_data_case(n))
            self.data_case_buttons[c_num] = btn

        # Main Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        # Scenario header
        self.data_case_title_lbl = tk.Label(workspace, text="Case 1: Cryogenic Resonator Temperature",
                                            font=("Segoe UI", 13, "bold"),
                                            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.data_case_title_lbl.pack(anchor="w")

        self.data_case_desc_lbl = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
            wraplength=820, justify="left"
        )
        self.data_case_desc_lbl.pack(anchor="w", pady=(4, 12))

        # Table & Statistical Audit Container (Two columns)
        table_container = tk.Frame(workspace, bg=Theme.BG_CARD)
        table_container.pack(fill="x", pady=(0, 16))
        table_container.columnconfigure(0, weight=6)
        table_container.columnconfigure(1, weight=4)

        # Left Column: Table of Measurements
        table_box = tk.Frame(table_container, bg=Theme.BG_INPUT,
                             highlightbackground=Theme.BORDER_MUTED,
                             highlightthickness=1, padx=14, pady=12)
        table_box.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        tk.Label(table_box, text="EXPERIMENTAL TELEMETRY TABLE (Select Suspicious Row):",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(anchor="w", pady=(0, 8))

        self.data_table_rows_frame = tk.Frame(table_box, bg=Theme.BG_INPUT)
        self.data_table_rows_frame.pack(fill="x")

        # Right Column: Live Python Statistical Analysis
        stats_box = tk.Frame(table_container, bg=Theme.BG_INPUT,
                            highlightbackground=Theme.BORDER_MUTED,
                            highlightthickness=1, padx=14, pady=12)
        stats_box.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        tk.Label(stats_box, text="LIVE STATISTICAL AUDIT:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEAL).pack(anchor="w", pady=(0, 8))

        self.data_stats_display = tk.Label(
            stats_box, text="",
            font=("Consolas", 9),
            bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
            justify="left"
        )
        self.data_stats_display.pack(anchor="w")

        # Action Buttons Row
        btn_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        btn_row.pack(fill="x", pady=(10, 12))

        ModernButton(btn_row, text="Check Answer", icon="✓",
                     bg_color=Theme.CYAN, text_color=Theme.BG_ROOT,
                     command=self._check_data_answer).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Hint", icon="💡",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.AMBER,
                     command=self._show_data_hint).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Reveal Explanation", icon="👁️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_MUTED,
                     command=self._reveal_data_explanation).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Retry", icon="↺",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._retry_data_case).pack(side="left")

        # Feedback & Explanation Banner
        self.data_feedback_lbl = tk.Label(
            workspace, text="Select the anomalous observation from the table above and click Check Answer.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED
        )
        self.data_feedback_lbl.pack(anchor="w", pady=(0, 8))

        self.data_hint_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9, "italic"),
            bg=Theme.BG_CARD, fg=Theme.AMBER,
            wraplength=800, justify="left"
        )
        self.data_hint_box.pack(anchor="w")

        self.data_explanation_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.CYAN,
            wraplength=800, justify="left"
        )
        self.data_explanation_box.pack(anchor="w")

        # Case Data Store
        self.data_cases_data = {
            1: {
                "title": "Case 1: Cryogenic Resonator Temperature",
                "desc": "A dilution refrigerator cooling micro-cantilever resonators should operate strictly between 0.010 K and 0.050 K. One sensor is reporting impossible thermal noise.",
                "rows": [
                    ("S-1", "0.014 K", "Normal"),
                    ("S-2", "0.018 K", "Normal"),
                    ("S-3", "0.015 K", "Normal"),
                    ("S-4", "0.019 K", "Normal"),
                    ("S-5", "293.15 K", "SUSPICIOUS"),
                    ("S-6", "0.021 K", "Normal"),
                    ("S-7", "0.016 K", "Normal"),
                    ("S-8", "0.017 K", "Normal"),
                ],
                "values": [0.014, 0.018, 0.015, 0.019, 293.15, 0.021, 0.016, 0.017],
                "units": "Kelvin (K)",
                "target_id": "S-5",
                "hint": "Hint: 293.15 Kelvin is exactly 20°C (standard laboratory room temperature). A cryogenic dilution refrigerator cannot simultaneously be at room temperature and functional!",
                "explanation": "Outlier Identified: Sensor S-5 (293.15 K).\nCause: Sensor S-5 failed to make thermal contact with the cold plate and was measuring the ambient laboratory room temperature (20°C = 293.15 K) rather than the dilution refrigerator's 15 mK baseline."
            },
            2: {
                "title": "Case 2: Particle Velocity Telemetry",
                "desc": "Linear accelerator sensors measure beam packets in meters per second. According to Einstein's Special Relativity, no particle with mass can reach or exceed the speed of light c (≈ 3.00 × 10⁸ m/s).",
                "rows": [
                    ("P-1", "2.84 × 10⁸ m/s", "0.95 c"),
                    ("P-2", "2.91 × 10⁸ m/s", "0.97 c"),
                    ("P-3", "2.79 × 10⁸ m/s", "0.93 c"),
                    ("P-4", "3.85 × 10⁸ m/s", "1.28 c"),
                    ("P-5", "2.88 × 10⁸ m/s", "0.96 c"),
                    ("P-6", "2.94 × 10⁸ m/s", "0.98 c"),
                    ("P-7", "2.82 × 10⁸ m/s", "0.94 c"),
                ],
                "values": [2.84, 2.91, 2.79, 3.85, 2.88, 2.94, 2.82],
                "units": "× 10⁸ m/s",
                "target_id": "P-4",
                "hint": "Hint: The speed of light c is approximately 3.00 × 10⁸ m/s. Check which packet's velocity exceeds this universal physical boundary.",
                "explanation": "Outlier Identified: Packet P-4 (3.85 × 10⁸ m/s = 1.28c).\nCause: A photodetector timing jitter desynchronized the time-of-flight clock, yielding a superluminal measurement that violates Special Relativity."
            },
            3: {
                "title": "Case 3: Microbial Culture Density",
                "desc": "Extremophile bacterial culture growth density after 24 hours of incubation. The expected bio-density is approximately 400 to 800 CFU/mL.",
                "rows": [
                    ("Culture A", "480 CFU/mL", "Normal"),
                    ("Culture B", "520 CFU/mL", "Normal"),
                    ("Culture C", "610 CFU/mL", "Normal"),
                    ("Culture D", "59000 CFU/mL", "SUSPICIOUS"),
                    ("Culture E", "540 CFU/mL", "Normal"),
                    ("Culture F", "670 CFU/mL", "Normal"),
                    ("Culture G", "580 CFU/mL", "Normal"),
                    ("Culture H", "620 CFU/mL", "Normal"),
                ],
                "values": [480, 520, 610, 59000, 540, 670, 580, 620],
                "units": "CFU/mL",
                "target_id": "Culture D",
                "hint": "Hint: Look for a classical clerical data entry error where extra zeroes or a decimal shift resulted in a value two orders of magnitude higher than the entire cluster.",
                "explanation": "Outlier Identified: Culture D (59000 CFU/mL).\nCause: Clerical typo. The researcher typed 59000 instead of 590.0 CFU/mL. Removing the typographic error restores standard normal distribution."
            }
        }

        self.current_data_case = 1
        self.selected_data_row_var = tk.StringVar()
        self._load_data_case(1)

        scroll.bind_mousewheel(content)
        return scroll

    def _load_data_case(self, case_num):
        """Loads selected dataset challenge case."""
        self.current_data_case = case_num
        data = self.data_cases_data[case_num]

        # Update case buttons styling
        for num, btn in self.data_case_buttons.items():
            cid = f"data_{num}"
            solved = cid in self.completed_challenges
            prefix = "✓ " if solved else "◈ "
            if num == case_num:
                btn.config(text=f"{prefix}Case {num}", bg=Theme.BG_CARD_HOVER,
                           fg=Theme.CYAN_BRIGHT, highlightbackground=Theme.CYAN)
            else:
                btn.config(text=f"{prefix}Case {num}", bg=Theme.BG_INPUT,
                           fg=Theme.EMERALD if solved else Theme.TEXT_SECONDARY,
                           highlightbackground=Theme.BORDER_MUTED)

        self.data_case_title_lbl.config(text=data["title"])
        self.data_case_desc_lbl.config(text=data["desc"])
        self.selected_data_row_var.set("")
        self.data_hint_box.config(text="")
        self.data_explanation_box.config(text="")

        # Build interactive table rows
        for w in self.data_table_rows_frame.winfo_children():
            w.destroy()

        # Header Row
        hdr_frame = tk.Frame(self.data_table_rows_frame, bg=Theme.BG_CARD)
        hdr_frame.pack(fill="x", pady=(0, 4))
        tk.Label(hdr_frame, text="Select", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, width=6).pack(side="left")
        tk.Label(hdr_frame, text="Observation ID", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, width=16, anchor="w").pack(side="left", padx=6)
        tk.Label(hdr_frame, text="Recorded Measurement", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN, width=22, anchor="w").pack(side="left", padx=6)
        tk.Label(hdr_frame, text="Status Flag", font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, width=12, anchor="w").pack(side="left")

        for row_id, val_str, note in data["rows"]:
            r_frame = tk.Frame(self.data_table_rows_frame, bg=Theme.BG_INPUT, cursor="hand2")
            r_frame.pack(fill="x", pady=2)

            rb = tk.Radiobutton(
                r_frame, variable=self.selected_data_row_var, value=row_id,
                bg=Theme.BG_INPUT, activebackground=Theme.BG_INPUT,
                selectcolor=Theme.BG_ROOT, highlightthickness=0, bd=0
            )
            rb.pack(side="left", padx=(4, 0))

            lbl_id = tk.Label(r_frame, text=row_id, font=("Consolas", 9, "bold"),
                              bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, width=15, anchor="w")
            lbl_id.pack(side="left", padx=6)

            lbl_val = tk.Label(r_frame, text=val_str, font=("Consolas", 9),
                               bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT, width=20, anchor="w")
            lbl_val.pack(side="left", padx=6)

            lbl_note = tk.Label(r_frame, text="Flagged" if "SUSPICIOUS" in note else "Recorded",
                                font=("Segoe UI", 8),
                                bg=Theme.BG_INPUT, fg=Theme.AMBER if "SUSPICIOUS" in note else Theme.TEXT_MUTED, width=12, anchor="w")
            lbl_note.pack(side="left")

            for item_w in (r_frame, lbl_id, lbl_val, lbl_note):
                item_w.bind("<Button-1>", lambda _, rid=row_id: self.selected_data_row_var.set(rid))

        # Real Python Statistical Calculations
        vals = data["values"]
        n = len(vals)
        mean_all = sum(vals) / n
        sorted_vals = sorted(vals)
        median_all = (sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2)
        std_all = math.sqrt(sum((x - mean_all) ** 2 for x in vals) / n)

        stats_txt = (
            f"• Sample Size (N) : {n} observations\n"
            f"• Mean Value (μ)  : {mean_all:.2f} {data['units']}\n"
            f"• Median Value    : {median_all:.2f} {data['units']}\n"
            f"• Std Deviation(σ): {std_all:.2f}\n"
            f"• Target Task     : Identify observation with extreme\n"
            f"                    divergence from physical constraints."
        )
        self.data_stats_display.config(text=stats_txt)

        cid = f"data_{case_num}"
        if cid in self.completed_challenges:
            self.data_feedback_lbl.config(text="✓ Solved: Suspicious measurement logged and confirmed.", fg=Theme.EMERALD)
        else:
            self.data_feedback_lbl.config(text="Select the anomalous observation above and click Check Answer.", fg=Theme.TEXT_MUTED)

    def _check_data_answer(self):
        """Checks if selected row matches the real anomaly."""
        data = self.data_cases_data[self.current_data_case]
        chosen = self.selected_data_row_var.get()

        if not chosen:
            self.data_feedback_lbl.config(text="⚠️ Please select an observation row from the table first.", fg=Theme.AMBER)
            return

        if chosen == data["target_id"]:
            cid = f"data_{self.current_data_case}"
            self._register_solve(cid, self.data_feedback_lbl)
            self._load_data_case(self.current_data_case)
        else:
            self.data_feedback_lbl.config(
                text=f"✗ {chosen} is within expected standard experimental error bounds. Inspect other sensors!",
                fg=Theme.ROSE
            )

    def _show_data_hint(self):
        data = self.data_cases_data[self.current_data_case]
        cid = f"data_{self.current_data_case}"
        self.hints_used.add(cid)
        self.data_hint_box.config(text=data["hint"])
        self.data_feedback_lbl.config(text="💡 Scientific Clue revealed. (Bonus points forfeited for this case).", fg=Theme.AMBER)

    def _reveal_data_explanation(self):
        data = self.data_cases_data[self.current_data_case]
        cid = f"data_{self.current_data_case}"
        self.hints_used.add(cid)
        self.data_explanation_box.config(text=f"🔍 DISCLOSED AUDIT REPORT:\n{data['explanation']}")

    def _retry_data_case(self):
        self.selected_data_row_var.set("")
        self.data_hint_box.config(text="")
        self.data_explanation_box.config(text="")
        self.data_feedback_lbl.config(text="Audit reset. Select an observation.", fg=Theme.TEXT_MUTED)

    # =========================================================================
    # SUB-VIEW 4: CHALLENGE THREE - THE STATISTICAL TRAP
    # =========================================================================
    def _create_statistical_view(self):
        """Builds Challenge Three: The Statistical Trap with misleading charts & fallacies."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Bar: Back to Detective HQ
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Detective HQ", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_challenge("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Research Detective > Challenge Three > The Statistical Trap",
                              font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.AMBER,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="⚠️ DATA INTEGRITY DOSSIER #03",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.AMBER,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="The Statistical Trap: Deceptive Charts & Fallacies",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="Numbers don't lie, but how they are framed can deceive. Investigate cases involving "
                 "misleading truncated bar charts, distorted salary averages, and correlation vs causation fallacies.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        # Scenario Selector Bar
        scen_bar = tk.Frame(content, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=16, pady=10)
        scen_bar.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(scen_bar, text="SELECT SCENARIO:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 12))

        self.stat_scen_buttons = {}
        scenarios = [
            (1, "Scenario 1: Truncated Y-Axis Bar Chart", "Chart Distortion"),
            (2, "Scenario 2: Skewed Postdoc Salary (Mean vs Median)", "Average Fallacy"),
            (3, "Scenario 3: Ice Cream & Hardware Overheating", "Correlation vs Causation"),
        ]

        for s_num, s_name, s_type in scenarios:
            btn = tk.Label(scen_bar, text=f"◈ {s_name}", font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                           padx=12, pady=5, cursor="hand2",
                           highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda _, n=s_num: self._load_stat_scenario(n))
            self.stat_scen_buttons[s_num] = btn

        # Main Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        self.stat_title_lbl = tk.Label(workspace, text="Scenario 1: Truncated Y-Axis Bar Chart",
                                       font=("Segoe UI", 13, "bold"),
                                       bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.stat_title_lbl.pack(anchor="w")

        self.stat_scenario_desc = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
            wraplength=820, justify="left"
        )
        self.stat_scenario_desc.pack(anchor="w", pady=(4, 12))

        # Canvas Area for Scenario 1 visual chart
        self.stat_canvas = tk.Canvas(
            workspace, height=160, bg=Theme.BG_INPUT, highlightthickness=0
        )
        self.stat_canvas.pack(fill="x", pady=(0, 14))

        # Multiple-choice Question
        self.stat_question_lbl = tk.Label(
            workspace, text="Question: Why is this statistical presentation misleading?",
            font=("Segoe UI", 10, "bold"),
            bg=Theme.BG_CARD, fg=Theme.CYAN_BRIGHT
        )
        self.stat_question_lbl.pack(anchor="w", pady=(0, 8))

        # Options Container
        self.stat_options_frame = tk.Frame(workspace, bg=Theme.BG_CARD)
        self.stat_options_frame.pack(fill="x", pady=(0, 14))

        self.stat_selected_option = tk.StringVar()

        # Action Buttons
        btn_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        btn_row.pack(fill="x", pady=(0, 12))

        ModernButton(btn_row, text="Check Answer", icon="✓",
                     bg_color=Theme.AMBER, text_color=Theme.BG_ROOT,
                     command=self._check_stat_answer).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Hint", icon="💡",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.AMBER,
                     command=self._show_stat_hint).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Reveal Explanation", icon="👁️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_MUTED,
                     command=self._reveal_stat_explanation).pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="Retry", icon="↺",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._retry_stat_scenario).pack(side="left")

        # Feedback & Detailed Breakdown Labels
        self.stat_feedback_lbl = tk.Label(
            workspace, text="Choose your deduction and click Check Answer.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED
        )
        self.stat_feedback_lbl.pack(anchor="w", pady=(0, 6))

        self.stat_hint_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9, "italic"),
            bg=Theme.BG_CARD, fg=Theme.AMBER,
            wraplength=800, justify="left"
        )
        self.stat_hint_box.pack(anchor="w")

        self.stat_explanation_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.CYAN,
            wraplength=800, justify="left"
        )
        self.stat_explanation_box.pack(anchor="w")

        # Scenarios Data Store
        self.stat_scenarios_data = {
            1: {
                "title": "Scenario 1: Truncated Y-Axis Bar Chart",
                "desc": "A pharmaceutical trial presents a bar chart comparing Drug Alpha (cure rate 81.2%) vs Drug Beta (cure rate 82.5%). By starting the Y-axis at 80% rather than 0%, Drug Beta appears visually three times taller than Drug Alpha!",
                "has_chart": True,
                "options": [
                    ("A", "Drug Alpha is significantly less effective because its bar is only one-third the height of Drug Beta."),
                    ("B", "The Y-axis is truncated at 80% rather than 0%, artificially exaggerating a tiny 1.3% difference into a massive visual gap.", True),
                    ("C", "Clinical drug trials should never be compared using bar charts under any circumstances."),
                    ("D", "Drug Beta's sample population is mathematically infinite, which invalidates the baseline.")
                ],
                "hint": "Hint: Notice where the vertical Y-axis begins on the chart. What happens when a baseline starts near the top of the data range instead of zero?",
                "explanation": "CORRECT: Option B.\nWhy B is correct: Starting the Y-axis at 80.0% instead of 0.0% is a classic chart distortion technique called 'axis truncation'. A 1.3% absolute difference (82.5% vs 81.2%) represents a visual bar height ratio of 2.5 : 1.2 (over double!), misleading viewers who judge value by bar area.\n\nWhy other choices are misleading:\n• A falls directly for the visual illusion without checking the actual values.\n• C is incorrect because bar charts are valid when properly scaled from zero.\n• D makes an absurd claim unrelated to chart scaling."
            },
            2: {
                "title": "Scenario 2: Skewed Postdoc Salary (Mean vs. Median)",
                "desc": "A prestigious research department recruits candidates with the brochure headline: 'Average Starting Salary in our Laboratory: $180,000!' You investigate the actual 10 salaries:\nNine postdocs make $50,000 each. The founding institute director earns $1,350,000.",
                "has_chart": False,
                "options": [
                    ("A", "The Mean ($180,000) is the most accurate figure because it incorporates every single dollar earned in the lab."),
                    ("B", "The Median ($50,000) represents the typical researcher experience because extreme outliers heavily distort the arithmetic mean.", True),
                    ("C", "The Mode divided by the sample size is the only reliable metric for payroll audits."),
                    ("D", "Multiplying the lowest salary by standard deviation yields the true salary." )
                ],
                "hint": "Hint: If 9 out of 10 people make $50,000, does $180,000 accurately describe what a newly hired researcher will experience?",
                "explanation": "CORRECT: Option B.\nWhy B is correct: In heavily skewed distributions, a single extreme outlier ($1,350,000) drags the arithmetic mean upward to $180,000, even though 90% of the team makes only $50,000! The Median ($50,000) is resistant to outliers and truthfully represents the central tendency.\n\nWhy other choices are misleading:\n• A uses mathematical inclusion as an excuse for real-world distortion.\n• C and D invent mathematically nonsensical formulas."
            },
            3: {
                "title": "Scenario 3: Ice Cream & Hardware Overheating",
                "desc": "A data audit uncovers a near-perfect positive correlation (r = 0.94) between daily campus ice cream sales and high-performance server overheating errors. A junior administrator drafts a policy banning ice cream to protect server hardware.",
                "has_chart": False,
                "options": [
                    ("A", "Ice cream sugar particles are venting into the server cooling intake fans."),
                    ("B", "Correlation is not causation: a lurking confounding variable (ambient summer heatwave) independently increases both ice cream cravings and computer thermal load.", True),
                    ("C", "A correlation coefficient of r = 0.94 proves beyond doubt that ice cream causes overheating."),
                    ("D", "Computer overheating emits magnetic radiation that induces ice cream appetite in researchers.")
                ],
                "hint": "Hint: What third atmospheric factor happens during hot summer months that affects both people and computers?",
                "explanation": "CORRECT: Option B.\nWhy B is correct: Correlation does not imply causation. A confounding 'lurking variable'—namely severe summer heatwaves—simultaneously drives human appetite for cold treats and strains server cooling chillers. Banning ice cream will have zero effect on server temperatures!\n\nWhy other choices are misleading:\n• A and D propose physically unfounded mechanisms.\n• C commits the quintessential statistical fallacy: equating mathematical association with physical causation."
            }
        }

        self.current_stat_scen = 1
        self._load_stat_scenario(1)

        scroll.bind_mousewheel(content)
        return scroll

    def _load_stat_scenario(self, scen_num):
        """Loads selected Statistical Trap scenario."""
        self.current_stat_scen = scen_num
        data = self.stat_scenarios_data[scen_num]

        # Update button styles
        for num, btn in self.stat_scen_buttons.items():
            cid = f"stat_{num}"
            solved = cid in self.completed_challenges
            prefix = "✓ " if solved else "◈ "
            if num == scen_num:
                btn.config(text=f"{prefix}Scenario {num}", bg=Theme.BG_CARD_HOVER,
                           fg=Theme.AMBER, highlightbackground=Theme.AMBER)
            else:
                btn.config(text=f"{prefix}Scenario {num}", bg=Theme.BG_INPUT,
                           fg=Theme.EMERALD if solved else Theme.TEXT_SECONDARY,
                           highlightbackground=Theme.BORDER_MUTED)

        self.stat_title_lbl.config(text=data["title"])
        self.stat_scenario_desc.config(text=data["desc"])
        self.stat_selected_option.set("")
        self.stat_hint_box.config(text="")
        self.stat_explanation_box.config(text="")

        # Draw chart on Canvas if Scenario 1
        c = self.stat_canvas
        c.delete("all")
        if data.get("has_chart"):
            self.stat_canvas.pack(fill="x", pady=(0, 14))
            self._draw_truncated_chart()
        else:
            self.stat_canvas.pack_forget()

        # Build radio options
        for w in self.stat_options_frame.winfo_children():
            w.destroy()

        for opt_key, opt_text, *rest in data["options"]:
            opt_card = tk.Frame(self.stat_options_frame, bg=Theme.BG_INPUT,
                                highlightbackground=Theme.BORDER_MUTED,
                                highlightthickness=1, padx=12, pady=8, cursor="hand2")
            opt_card.pack(fill="x", pady=4)

            rb = tk.Radiobutton(
                opt_card, text=f"{opt_key})  {opt_text}",
                variable=self.stat_selected_option, value=opt_key,
                font=("Segoe UI", 9),
                bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                selectcolor=Theme.BG_ROOT, activebackground=Theme.BG_INPUT,
                activeforeground=Theme.CYAN,
                wraplength=760, justify="left", bd=0
            )
            rb.pack(anchor="w")

            for item_w in (opt_card, rb):
                item_w.bind("<Button-1>", lambda _, k=opt_key: self.stat_selected_option.set(k))

        cid = f"stat_{scen_num}"
        if cid in self.completed_challenges:
            self.stat_feedback_lbl.config(text="✓ Solved: Statistical fallacy identified and documented.", fg=Theme.EMERALD)
        else:
            self.stat_feedback_lbl.config(text="Review the scenario and choose the correct deduction.", fg=Theme.TEXT_MUTED)

    def _draw_truncated_chart(self):
        """Draws the misleading truncated Y-axis bar chart on Canvas for Scenario 1."""
        c = self.stat_canvas
        c.delete("all")
        w = max(400, c.winfo_width())
        h = 160

        # Draw title
        c.create_text(30, 15, text="MISLEADING GRAPH: Truncated Y-Axis (Baseline starts at 80.0%, NOT 0.0%)",
                      fill=Theme.AMBER, font=("Segoe UI", 8, "bold"), anchor="w")

        # Chart bounds
        y_top = 40
        y_base = 125
        x_start = 120

        # Y Axis lines & labels
        c.create_line(x_start - 10, y_top, x_start - 10, y_base, fill=Theme.TEXT_MUTED, width=1.5)
        c.create_line(x_start - 10, y_base, x_start + 360, y_base, fill=Theme.TEXT_MUTED, width=1.5)

        c.create_text(x_start - 15, y_base, text="80.0%", fill=Theme.ROSE, font=("Consolas", 8, "bold"), anchor="e")
        c.create_text(x_start - 15, y_top, text="83.0%", fill=Theme.TEXT_MUTED, font=("Consolas", 8), anchor="e")
        c.create_text(x_start - 15, (y_top + y_base) / 2, text="81.5%", fill=Theme.TEXT_MUTED, font=("Consolas", 8), anchor="e")

        # Bars: Drug Alpha (81.2%) -> Height = (81.2 - 80) / 3.0 = 1.2/3.0 = 40% height
        # Bars: Drug Beta (82.5%) -> Height = (82.5 - 80) / 3.0 = 2.5/3.0 = 83% height!
        bar1_h = ((81.2 - 80.0) / 3.0) * (y_base - y_top)
        bar2_h = ((82.5 - 80.0) / 3.0) * (y_base - y_top)

        # Draw Drug Alpha bar
        bx1 = x_start + 40
        c.create_rectangle(bx1, y_base - bar1_h, bx1 + 65, y_base, fill=Theme.TEAL, outline=Theme.BORDER_GLOW)
        c.create_text(bx1 + 32, y_base - bar1_h - 10, text="81.2%", fill=Theme.CYAN_BRIGHT, font=("Segoe UI", 8, "bold"))
        c.create_text(bx1 + 32, y_base + 14, text="Drug Alpha", fill=Theme.TEXT_SECONDARY, font=("Segoe UI", 8))

        # Draw Drug Beta bar
        bx2 = x_start + 180
        c.create_rectangle(bx2, y_base - bar2_h, bx2 + 65, y_base, fill=Theme.PURPLE, outline=Theme.PURPLE_LIGHT)
        c.create_text(bx2 + 32, y_base - bar2_h - 10, text="82.5%", fill=Theme.PURPLE_LIGHT, font=("Segoe UI", 8, "bold"))
        c.create_text(bx2 + 32, y_base + 14, text="Drug Beta", fill=Theme.TEXT_SECONDARY, font=("Segoe UI", 8))

        # Visual discrepancy callout arrow
        c.create_line(bx1 + 65, y_base - bar1_h, bx2, y_base - bar2_h, fill=Theme.AMBER, width=1.5, dash=(2, 2))
        c.create_text(bx2 + 90, (y_base - bar2_h + y_base - bar1_h) / 2,
                      text="Looks 2.5× taller,\nactual diff is 1.3%!", fill=Theme.AMBER,
                      font=("Segoe UI", 7, "bold"), anchor="w")

    def _check_stat_answer(self):
        """Checks selected multiple choice answer."""
        data = self.stat_scenarios_data[self.current_stat_scen]
        chosen = self.stat_selected_option.get()

        if not chosen:
            self.stat_feedback_lbl.config(text="⚠️ Please select an option before checking.", fg=Theme.AMBER)
            return

        # Find which option is correct
        correct_key = next((opt[0] for opt in data["options"] if len(opt) > 2 and opt[2] is True), None)

        if chosen == correct_key:
            cid = f"stat_{self.current_stat_scen}"
            self._register_solve(cid, self.stat_feedback_lbl)
            self._load_stat_scenario(self.current_stat_scen)
        else:
            self.stat_feedback_lbl.config(
                text=f"✗ Option {chosen} is a common misconception! Inspect the clues or try again.",
                fg=Theme.ROSE
            )

    def _show_stat_hint(self):
        data = self.stat_scenarios_data[self.current_stat_scen]
        cid = f"stat_{self.current_stat_scen}"
        self.hints_used.add(cid)
        self.stat_hint_box.config(text=data["hint"])
        self.stat_feedback_lbl.config(text="💡 Clue revealed. (Bonus points forfeited for this scenario).", fg=Theme.AMBER)

    def _reveal_stat_explanation(self):
        data = self.stat_scenarios_data[self.current_stat_scen]
        cid = f"stat_{self.current_stat_scen}"
        self.hints_used.add(cid)
        self.stat_explanation_box.config(text=f"🔍 DISCLOSED ANALYSIS:\n{data['explanation']}")

    def _retry_stat_scenario(self):
        self.stat_selected_option.set("")
        self.stat_hint_box.config(text="")
        self.stat_explanation_box.config(text="")
        self.stat_feedback_lbl.config(text="Scenario reset. Select your answer.", fg=Theme.TEXT_MUTED)

    # =========================================================================
    # SUB-VIEW 5: CHALLENGE FOUR - THE PATTERN MYSTERY
    # =========================================================================
    def _create_pattern_view(self):
        """Builds Challenge Four: The Pattern Mystery with 5 sequence & logic puzzles."""
        scroll = ScrollableFrame(self.content_box, bg=Theme.BG_ROOT)
        content = scroll.scrollable_content

        # Top Bar: Back to Detective HQ
        top_bar = tk.Frame(content, bg=Theme.BG_ROOT)
        top_bar.pack(fill="x", padx=32, pady=(16, 12))

        back_btn = ModernButton(
            top_bar, text="Back to Detective HQ", icon="←",
            bg_color=Theme.BG_CARD, hover_color=Theme.BORDER_MUTED,
            text_color=Theme.CYAN, font=("Segoe UI", 9, "bold"),
            padx=12, pady=6,
            command=lambda: self.switch_to_challenge("overview")
        )
        back_btn.pack(side="left")

        breadcrumb = tk.Label(top_bar, text="Research Detective > Challenge Four > The Pattern Mystery",
                              font=("Segoe UI", 9), bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        breadcrumb.pack(side="right", pady=6)

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.TEAL,
                        highlightthickness=1, padx=28, pady=20)
        hero.pack(fill="x", padx=32, pady=(0, 20))

        tag = tk.Label(hero, text="🧩 LOGIC & PATTERN DOSSIER #04",
                       font=("Segoe UI", 8, "bold"),
                       bg=Theme.BG_INPUT, fg=Theme.TEAL,
                       padx=8, pady=3)
        tag.pack(anchor="w")

        tk.Label(hero, text="The Pattern Mystery: Mathematical Sequence Deduction",
                 font=("Segoe UI", 20, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))

        tk.Label(
            hero,
            text="Scientific breakthroughs frequently originate from recognizing hidden patterns in empirical sequences. "
                 "Analyze the progression of numbers, deduce the underlying transformation rule, and determine the missing value.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY,
            wraplength=850, justify="left"
        ).pack(anchor="w")

        # Puzzle Selector Bar (5 Puzzles)
        puz_bar = tk.Frame(content, bg=Theme.BG_CARD,
                           highlightbackground=Theme.BORDER_SUBTLE,
                           highlightthickness=1, padx=16, pady=10)
        puz_bar.pack(fill="x", padx=32, pady=(0, 16))

        tk.Label(puz_bar, text="SELECT PUZZLE:", font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(side="left", padx=(0, 10))

        self.pattern_puz_buttons = {}
        puzzles = [
            (1, "Puzzle 1", "Easy"),
            (2, "Puzzle 2", "Easy"),
            (3, "Puzzle 3", "Medium"),
            (4, "Puzzle 4", "Medium"),
            (5, "Puzzle 5", "Hard"),
        ]

        for p_num, p_name, p_diff in puzzles:
            btn = tk.Label(puz_bar, text=f"◈ {p_name} ({p_diff})", font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY,
                           padx=10, pady=5, cursor="hand2",
                           highlightbackground=Theme.BORDER_MUTED, highlightthickness=1)
            btn.pack(side="left", padx=(0, 6))
            btn.bind("<Button-1>", lambda _, n=p_num: self._load_pattern_puzzle(n))
            self.pattern_puz_buttons[p_num] = btn

        # Main Workspace Card
        workspace = tk.Frame(content, bg=Theme.BG_CARD,
                             highlightbackground=Theme.BORDER_SUBTLE,
                             highlightthickness=1, padx=24, pady=22)
        workspace.pack(fill="x", padx=32, pady=(0, 24))

        self.pattern_title_lbl = tk.Label(workspace, text="Puzzle 1: Geometric Multiplier Sequence",
                                          font=("Segoe UI", 13, "bold"),
                                          bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
        self.pattern_title_lbl.pack(anchor="w")

        self.pattern_desc_lbl = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
            wraplength=820, justify="left"
        )
        self.pattern_desc_lbl.pack(anchor="w", pady=(4, 16))

        # Visual Pattern Display Sequence Box
        seq_box = tk.Frame(workspace, bg=Theme.BG_INPUT,
                           highlightbackground=Theme.BORDER_MUTED,
                           highlightthickness=1, padx=20, pady=18)
        seq_box.pack(fill="x", pady=(0, 16))

        tk.Label(seq_box, text="DEDUCE THE RECURSIVE PATTERN:",
                 font=("Segoe UI", 8, "bold"),
                 bg=Theme.BG_INPUT, fg=Theme.TEAL).pack(anchor="w", pady=(0, 8))

        self.pattern_sequence_lbl = tk.Label(
            seq_box, text="3,  9,  27,  81,  [ ? ]",
            font=("Consolas", 18, "bold"),
            bg=Theme.BG_INPUT, fg=Theme.CYAN_BRIGHT
        )
        self.pattern_sequence_lbl.pack(anchor="center", pady=(4, 8))

        # Input Row
        in_row = tk.Frame(workspace, bg=Theme.BG_CARD)
        in_row.pack(fill="x", pady=(0, 14))

        tk.Label(in_row, text="Enter the Missing Value [ ? ]:",
                 font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 12))

        self.pattern_answer_var = tk.StringVar()
        self.pattern_entry = tk.Entry(
            in_row, textvariable=self.pattern_answer_var,
            bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Consolas", 11, "bold"), justify="center",
            width=14,
            highlightbackground=Theme.BORDER_MUTED,
            highlightthickness=1, bd=0, relief="flat"
        )
        self.pattern_entry.pack(side="left", ipady=6, padx=(0, 12))
        self.pattern_entry.bind("<Return>", lambda _: self._check_pattern_answer())

        ModernButton(in_row, text="Check Answer", icon="✓",
                     bg_color=Theme.TEAL,
                     command=self._check_pattern_answer).pack(side="left", padx=(0, 8))

        ModernButton(in_row, text="Hint", icon="💡",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.AMBER,
                     command=self._show_pattern_hint).pack(side="left", padx=(0, 8))

        ModernButton(in_row, text="Reveal Solution", icon="👁️",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_MUTED,
                     command=self._reveal_pattern_solution).pack(side="left", padx=(0, 8))

        ModernButton(in_row, text="Retry", icon="↺",
                     bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                     text_color=Theme.TEXT_SECONDARY,
                     command=self._retry_pattern_puzzle).pack(side="left")

        # Feedback & Explanation
        self.pattern_feedback_lbl = tk.Label(
            workspace, text="Examine the sequence above and deduce the missing number.",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED
        )
        self.pattern_feedback_lbl.pack(anchor="w", pady=(0, 6))

        self.pattern_hint_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9, "italic"),
            bg=Theme.BG_CARD, fg=Theme.AMBER,
            wraplength=800, justify="left"
        )
        self.pattern_hint_box.pack(anchor="w")

        self.pattern_solution_box = tk.Label(
            workspace, text="",
            font=("Segoe UI", 9),
            bg=Theme.BG_CARD, fg=Theme.CYAN,
            wraplength=800, justify="left"
        )
        self.pattern_solution_box.pack(anchor="w")

        # Puzzles Data Store (5 puzzles with varying difficulty)
        self.pattern_puzzles_data = {
            1: {
                "title": "Puzzle 1: Geometric Expansion Sequence",
                "diff": "Easy",
                "desc": "Identify the exponential growth constant governing this sequence.",
                "seq_text": "3,   9,   27,   81,   [ ? ]",
                "target": "243",
                "hint": "Hint: Each number is generated by multiplying the preceding value by 3 (powers of 3).",
                "explanation": "Pattern: Exponential geometric progression where aₙ = 3ⁿ (or each term × 3).\n81 × 3 = 243."
            },
            2: {
                "title": "Puzzle 2: Fibonacci Recurrence Sequence",
                "diff": "Easy",
                "desc": "Recognize the additive relationship connecting consecutive pairs of terms.",
                "seq_text": "2,   3,   5,   8,   13,   21,   [ ? ]",
                "target": "34",
                "hint": "Hint: Notice that 2 + 3 = 5, 3 + 5 = 8, 5 + 8 = 13... Add the last two numbers together!",
                "explanation": "Pattern: Fibonacci recurrence relation aₙ = aₙ₋₁ + aₙ₋₂.\n13 + 21 = 34."
            },
            3: {
                "title": "Puzzle 3: Alternating Dual-Operator Sequence",
                "diff": "Medium",
                "desc": "This algorithmic progression alternates between two distinct arithmetic operations.",
                "seq_text": "2,   6,   7,   21,   22,   66,   67,   [ ? ]",
                "target": "201",
                "hint": "Hint: The rule alternates: (× 3), (+ 1), (× 3), (+ 1)... The previous operation was + 1 (66 + 1 = 67). What comes next?",
                "explanation": "Pattern: Alternating operations: (× 3), (+ 1), (× 3), (+ 1)...\n67 × 3 = 201."
            },
            4: {
                "title": "Puzzle 4: Square Offset Progression",
                "diff": "Medium",
                "desc": "Compare each value in the sequence to perfect mathematical squares.",
                "seq_text": "0,   3,   8,   15,   24,   35,   [ ? ]",
                "target": "48",
                "hint": "Hint: Compare with squares: 1, 4, 9, 16, 25, 36, 49... (Or examine the first differences: +3, +5, +7, +9, +11, +13).",
                "explanation": "Pattern: n² - 1 for n = 1, 2, 3, 4, 5, 6, 7.\nFor n = 7: 7² - 1 = 49 - 1 = 48 (or 35 + 13 = 48)."
            },
            5: {
                "title": "Puzzle 5: Exponential Difference Hierarchy",
                "diff": "Hard",
                "desc": "Analyze the rate of change between successive terms in this higher-order sequence.",
                "seq_text": "2,   3,   5,   9,   17,   33,   [ ? ]",
                "target": "65",
                "hint": "Hint: Look at the step difference between terms: +1, +2, +4, +8, +16... The differences double each step!",
                "explanation": "Pattern: First differences are powers of 2 (2ⁿ): +1, +2, +4, +8, +16, +32 (or formula: 2ⁿ + 1).\n33 + 32 = 65."
            }
        }

        self.current_pattern_puzzle = 1
        self._load_pattern_puzzle(1)

        scroll.bind_mousewheel(content)
        return scroll

    def _load_pattern_puzzle(self, puz_num):
        """Loads selected pattern mystery puzzle."""
        self.current_pattern_puzzle = puz_num
        data = self.pattern_puzzles_data[puz_num]

        # Update button styles
        for num, btn in self.pattern_puz_buttons.items():
            cid = f"pattern_{num}"
            solved = cid in self.completed_challenges
            prefix = "✓ " if solved else "◈ "
            diff = self.pattern_puzzles_data[num]["diff"]
            if num == puz_num:
                btn.config(text=f"{prefix}Puzzle {num} ({diff})", bg=Theme.BG_CARD_HOVER,
                           fg=Theme.TEAL, highlightbackground=Theme.TEAL)
            else:
                btn.config(text=f"{prefix}Puzzle {num} ({diff})", bg=Theme.BG_INPUT,
                           fg=Theme.EMERALD if solved else Theme.TEXT_SECONDARY,
                           highlightbackground=Theme.BORDER_MUTED)

        self.pattern_title_lbl.config(text=f"{data['title']} ({data['diff']})")
        self.pattern_desc_lbl.config(text=data["desc"])
        self.pattern_sequence_lbl.config(text=data["seq_text"])

        self.pattern_answer_var.set("")
        self.pattern_hint_box.config(text="")
        self.pattern_solution_box.config(text="")

        cid = f"pattern_{puz_num}"
        if cid in self.completed_challenges:
            self.pattern_feedback_lbl.config(text="✓ Solved: Sequence law deduced and verified.", fg=Theme.EMERALD)
        else:
            self.pattern_feedback_lbl.config(text="Examine the sequence above and deduce the missing value.", fg=Theme.TEXT_MUTED)

    def _check_pattern_answer(self):
        """Validates numerical answer for pattern puzzle."""
        data = self.pattern_puzzles_data[self.current_pattern_puzzle]
        raw_ans = self.pattern_answer_var.get().strip()

        if not raw_ans:
            self.pattern_feedback_lbl.config(text="⚠️ Please enter your deduced value into the box.", fg=Theme.AMBER)
            return

        # Tolerate float/integer format equality (e.g. 243 vs 243.0)
        try:
            val_user = float(raw_ans)
            val_target = float(data["target"])
            is_match = abs(val_user - val_target) < 1e-6
        except ValueError:
            is_match = raw_ans.lower() == data["target"].lower()

        if is_match:
            cid = f"pattern_{self.current_pattern_puzzle}"
            self._register_solve(cid, self.pattern_feedback_lbl)
            self._load_pattern_puzzle(self.current_pattern_puzzle)
        else:
            self.pattern_feedback_lbl.config(
                text=f"✗ {raw_ans} does not fit the sequence progression. Check the differences or ask for a Hint!",
                fg=Theme.ROSE
            )

    def _show_pattern_hint(self):
        data = self.pattern_puzzles_data[self.current_pattern_puzzle]
        cid = f"pattern_{self.current_pattern_puzzle}"
        self.hints_used.add(cid)
        self.pattern_hint_box.config(text=data["hint"])
        self.pattern_feedback_lbl.config(text="💡 Sequence clue revealed. (Bonus points forfeited for this puzzle).", fg=Theme.AMBER)

    def _reveal_pattern_solution(self):
        data = self.pattern_puzzles_data[self.current_pattern_puzzle]
        cid = f"pattern_{self.current_pattern_puzzle}"
        self.hints_used.add(cid)
        self.pattern_solution_box.config(text=f"🔍 DISCLOSED PATTERN LOGIC:\n{data['explanation']}")

    def _retry_pattern_puzzle(self):
        self.pattern_answer_var.set("")
        self.pattern_hint_box.config(text="")
        self.pattern_solution_box.config(text="")
        self.pattern_feedback_lbl.config(text="Puzzle reset. Enter your deduction.", fg=Theme.TEXT_MUTED)


# =============================================================================
# INTRODUCTORY PLACEHOLDER PAGES
# =============================================================================

class PlaceholderPageView(tk.Frame):
    """
    Standardized, highly polished introductory page for modules
    under active research development.
    """
    def __init__(self, parent, title, subtitle, icon, accent_color,
                 description, features, sample_cards=None, app=None):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        scroll = ScrollableFrame(self, bg=Theme.BG_ROOT)
        scroll.pack(fill="both", expand=True)
        content = scroll.scrollable_content

        # Header Hero Panel
        hero = tk.Frame(content, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=accent_color,
                        highlightthickness=1, padx=30, pady=26)
        hero.pack(fill="x", padx=32, pady=(24, 20))

        badge = tk.Label(hero, text=f"◈  {title.upper()} MODULE",
                         font=("Segoe UI", 8, "bold"),
                         bg=Theme.BG_INPUT, fg=accent_color,
                         padx=8, pady=3)
        badge.pack(anchor="w")

        top_row = tk.Frame(hero, bg=Theme.BG_CARD_ELEVATED)
        top_row.pack(fill="x", pady=(10, 4))

        i_lbl = tk.Label(top_row, text=icon, font=("Segoe UI", 26),
                         bg=Theme.BG_CARD_ELEVATED, fg=accent_color)
        i_lbl.pack(side="left", padx=(0, 12))

        t_lbl = tk.Label(top_row, text=title, font=("Segoe UI", 22, "bold"),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        t_lbl.pack(side="left")

        sub_lbl = tk.Label(hero, text=subtitle, font=("Segoe UI", 12),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY)
        sub_lbl.pack(anchor="w")

        desc_lbl = tk.Label(hero, text=description, font=("Segoe UI", 10),
                            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED,
                            wraplength=850, justify="left")
        desc_lbl.pack(anchor="w", pady=(12, 0))

        # Planned Capabilities Section
        caps_frame = tk.Frame(content, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_SUBTLE,
                              highlightthickness=1, padx=24, pady=20)
        caps_frame.pack(fill="x", padx=32, pady=(0, 20))

        tk.Label(caps_frame, text="🔬 Core Capabilities & Specifications",
                 font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 12))

        for feat_title, feat_detail in features:
            f_row = tk.Frame(caps_frame, bg=Theme.BG_CARD)
            f_row.pack(fill="x", pady=6)

            dot = tk.Label(f_row, text="◈", font=("Segoe UI", 10),
                           bg=Theme.BG_CARD, fg=accent_color)
            dot.pack(side="left", anchor="n", padx=(0, 8))

            info_col = tk.Frame(f_row, bg=Theme.BG_CARD)
            info_col.pack(side="left", fill="x", expand=True)

            f_t = tk.Label(info_col, text=feat_title, font=("Segoe UI", 10, "bold"),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            f_t.pack(fill="x")

            f_d = tk.Label(info_col, text=feat_detail, font=("Segoe UI", 9),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, anchor="w")
            f_d.pack(fill="x")

        # Sample preview cards if provided
        if sample_cards:
            tk.Label(content, text="🧪 Active Simulation Previews & Records",
                     font=("Segoe UI", 13, "bold"),
                     bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(anchor="w", padx=32, pady=(10, 12))

            cards_grid = tk.Frame(content, bg=Theme.BG_ROOT)
            cards_grid.pack(fill="x", padx=32, pady=(0, 30))
            cards_grid.columnconfigure(0, weight=1, uniform="preview")
            cards_grid.columnconfigure(1, weight=1, uniform="preview")
            cards_grid.columnconfigure(2, weight=1, uniform="preview")

            for idx, c_data in enumerate(sample_cards):
                card = tk.Frame(cards_grid, bg=Theme.BG_CARD,
                                highlightbackground=Theme.BORDER_SUBTLE,
                                highlightthickness=1, padx=16, pady=16)
                card.grid(row=0, column=idx, padx=(0 if idx == 0 else 8, 0 if idx == 2 else 8), sticky="nsew")

                tk.Label(card, text=c_data.get("tag", "PREVIEW"),
                         font=("Segoe UI", 8, "bold"),
                         bg=Theme.BG_INPUT, fg=accent_color,
                         padx=6, pady=2).pack(anchor="w")

                tk.Label(card, text=c_data["title"], font=("Segoe UI", 11, "bold"),
                         bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                         wraplength=260, justify="left").pack(anchor="w", pady=(8, 4))

                tk.Label(card, text=c_data["desc"], font=("Segoe UI", 9),
                         bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                         wraplength=260, justify="left").pack(anchor="w", pady=(0, 12))

                ModernButton(card, text=c_data.get("action", "Launch Preview"),
                             bg_color=Theme.BG_INPUT, hover_color=Theme.BORDER_MUTED,
                             text_color=accent_color, font=("Segoe UI", 8, "bold"),
                             padx=10, pady=4,
                             command=lambda t=c_data["title"]: messagebox.showinfo(
                                 "CurioLab Module Preview",
                                 f"Preparing environment for: {t}\n\n"
                                 "Simulation parameters validated. Full interactive workspace available in upcoming update."
                             )).pack(anchor="w")

        scroll.bind_mousewheel(content)


# =============================================================================
# MAIN WINDOW CONTROLLER & SHELL
# =============================================================================

class CurioLabApp:
    """
    Core Application Window:
    - Fixed sidebar with 8 navigation buttons
    - Top header with dynamic title, search bar, notifications, and user avatar
    - Swappable content container
    """
    def __init__(self, root):
        self.root = root
        self.root.title("CurioLab — An Interactive Research & Discovery Platform")

        # Initial and minimum window sizes as requested
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg=Theme.BG_ROOT)

        # Center window on screen
        self._center_window(1400, 850)

        # Navigation state
        self.current_page_name = "Discovery Hub"
        self.nav_buttons = {}
        self.active_nav_indicator = None

        # Build application shell
        self._build_sidebar()
        self._build_main_area()

        # Initialize pages dictionary
        self.pages = {}
        self._initialize_pages()

        # Display default page (Discovery Hub)
        self.navigate_to("Discovery Hub")

        # Global keyboard shortcuts
        self.root.bind("<Control-f>", lambda _: self.search_entry.focus_set())

    def _center_window(self, width, height):
        """Centers window on primary display."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, int((screen_w - width) / 2))
        y = max(0, int((screen_h - height) / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # -------------------------------------------------------------------------
    # SIDEBAR COMPONENT
    # -------------------------------------------------------------------------
    def _build_sidebar(self):
        """Fixed left sidebar with brand logo, nav buttons, and status."""
        self.sidebar = tk.Frame(self.root, bg=Theme.BG_SIDEBAR, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 1. Brand Logo & Title Area
        brand_frame = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR, padx=20, pady=22)
        brand_frame.pack(fill="x")

        logo_row = tk.Frame(brand_frame, bg=Theme.BG_SIDEBAR)
        logo_row.pack(fill="x")

        # Glowing flask / atom logo icon
        logo_icon = tk.Label(logo_row, text="⚗️", font=("Segoe UI", 20),
                             bg=Theme.BG_SIDEBAR, fg=Theme.CYAN_BRIGHT)
        logo_icon.pack(side="left", padx=(0, 10))

        brand_text_col = tk.Frame(logo_row, bg=Theme.BG_SIDEBAR)
        brand_text_col.pack(side="left")

        app_name = tk.Label(brand_text_col, text="CurioLab",
                            font=("Segoe UI", 16, "bold"),
                            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_PRIMARY)
        app_name.pack(anchor="w")

        app_sub = tk.Label(brand_text_col, text="RESEARCH & DISCOVERY",
                           font=("Segoe UI", 7, "bold"),
                           bg=Theme.BG_SIDEBAR, fg=Theme.CYAN)
        app_sub.pack(anchor="w")

        # Subtle divider
        divider = tk.Frame(self.sidebar, bg=Theme.BORDER_SUBTLE, height=1)
        divider.pack(fill="x", padx=16, pady=(6, 16))

        # 2. Navigation Items List (Exact items from prompt)
        nav_items = [
            ("Discovery Hub", "◈"),
            ("Experiment Lab", "🧪"),
            ("Research Detective", "🔍"),
            ("Knowledge Library", "📚"),
            ("Research Galaxy", "🌌"),
            ("Discovery Journal", "📓"),
            ("Settings", "⚙️"),
            ("Help & About", "❓"),
        ]

        self.nav_container = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR)
        self.nav_container.pack(fill="both", expand=True, padx=12)

        for name, icon in nav_items:
            self._create_nav_button(self.nav_container, name, icon)

        # 3. Sidebar Bottom Status Card
        footer = tk.Frame(self.sidebar, bg=Theme.BG_INPUT,
                          highlightbackground=Theme.BORDER_SUBTLE,
                          highlightthickness=1, padx=14, pady=12)
        footer.pack(fill="x", side="bottom", padx=14, pady=16)

        st_row = tk.Frame(footer, bg=Theme.BG_INPUT)
        st_row.pack(fill="x")

        st_dot = tk.Label(st_row, text="●", font=("Segoe UI", 8),
                          bg=Theme.BG_INPUT, fg=Theme.EMERALD)
        st_dot.pack(side="left", padx=(0, 6))

        st_txt = tk.Label(st_row, text="Core Engine Online",
                          font=("Segoe UI", 8, "bold"),
                          bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        st_txt.pack(side="left")

        env_txt = tk.Label(footer, text="Simulation Node: Alpha-7 • Latency 1ms",
                           font=("Segoe UI", 7),
                           bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED)
        env_txt.pack(anchor="w", pady=(2, 0))

    def _create_nav_button(self, parent, name, icon):
        """Creates a modern clickable navigation button with active state."""
        btn_frame = tk.Frame(parent, bg=Theme.BG_SIDEBAR, cursor="hand2")
        btn_frame.pack(fill="x", pady=2)

        # Left active glowing indicator bar (initially invisible)
        indicator = tk.Frame(btn_frame, bg=Theme.BG_SIDEBAR, width=3)
        indicator.pack(side="left", fill="y")

        # Icon
        icon_lbl = tk.Label(btn_frame, text=icon, font=("Segoe UI", 12),
                            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED,
                            width=3, cursor="hand2")
        icon_lbl.pack(side="left", padx=(6, 2), pady=9)

        # Label
        text_lbl = tk.Label(btn_frame, text=name, font=("Segoe UI", 10),
                            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY,
                            anchor="w", cursor="hand2")
        text_lbl.pack(side="left", fill="x", expand=True, pady=9)

        widgets = (btn_frame, indicator, icon_lbl, text_lbl)

        # Event bindings
        for w in widgets:
            w.bind("<Button-1>", lambda _, n=name: self.navigate_to(n))
            w.bind("<Enter>", lambda _, bf=btn_frame, n=name: self._on_nav_enter(bf, n))
            w.bind("<Leave>", lambda _, bf=btn_frame, n=name: self._on_nav_leave(bf, n))

        self.nav_buttons[name] = {
            "frame": btn_frame,
            "indicator": indicator,
            "icon": icon_lbl,
            "label": text_lbl
        }

    def _on_nav_enter(self, frame, name):
        if name != self.current_page_name:
            frame.config(bg=Theme.BG_CARD)
            self.nav_buttons[name]["icon"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
            self.nav_buttons[name]["label"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)

    def _on_nav_leave(self, frame, name):
        if name != self.current_page_name:
            frame.config(bg=Theme.BG_SIDEBAR)
            self.nav_buttons[name]["icon"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED)
            self.nav_buttons[name]["label"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY)

    # -------------------------------------------------------------------------
    # MAIN AREA & HEADER COMPONENT
    # -------------------------------------------------------------------------
    def _build_main_area(self):
        """Builds top header and content container."""
        self.main_container = tk.Frame(self.root, bg=Theme.BG_ROOT)
        self.main_container.pack(side="right", fill="both", expand=True)

        # Top Header
        self.header = tk.Frame(self.main_container, bg=Theme.BG_HEADER, height=72,
                               highlightbackground=Theme.BORDER_SUBTLE,
                               highlightthickness=1)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        # Header Left: Page Title & Subtitle
        title_box = tk.Frame(self.header, bg=Theme.BG_HEADER, padx=28)
        title_box.pack(side="left", fill="y", pady=12)

        self.header_title = tk.Label(title_box, text="Discovery Hub",
                                     font=("Segoe UI", 15, "bold"),
                                     bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY)
        self.header_title.pack(anchor="w")

        self.header_subtitle = tk.Label(title_box,
                                        text="Laboratory Overview & Real-Time Research Intel",
                                        font=("Segoe UI", 8),
                                        bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        self.header_subtitle.pack(anchor="w")

        # Header Right Controls: Profile, Notification, Search
        controls_box = tk.Frame(self.header, bg=Theme.BG_HEADER, padx=28)
        controls_box.pack(side="right", fill="y")

        # 1. User Profile Area
        self._build_user_profile(controls_box)

        # 2. Notification Button
        self._build_notification_btn(controls_box)

        # 3. Search Field
        self._build_search_field(controls_box)

        # Page Content Display Area
        self.content_area = tk.Frame(self.main_container, bg=Theme.BG_ROOT)
        self.content_area.pack(fill="both", expand=True)

    def _build_search_field(self, parent):
        """Futuristic search input with placeholder and search action."""
        search_wrap = tk.Frame(parent, bg=Theme.BG_INPUT,
                               highlightbackground=Theme.BORDER_MUTED,
                               highlightthickness=1, padx=8, pady=4)
        search_wrap.pack(side="right", padx=(0, 16), pady=18)

        search_icon = tk.Label(search_wrap, text="🔍", font=("Segoe UI", 9),
                               bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED)
        search_icon.pack(side="left", padx=(2, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_wrap,
            textvariable=self.search_var,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Segoe UI", 9),
            width=28,
            bd=0,
            relief="flat"
        )
        self.search_entry.pack(side="left")

        # Placeholder logic
        self.placeholder = "Search experiments, papers, cases..."
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(fg=Theme.TEXT_MUTED)

        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<Return>", self._execute_search)

        clear_btn = tk.Label(search_wrap, text="✕", font=("Segoe UI", 8),
                             bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, cursor="hand2")
        clear_btn.pack(side="right", padx=(4, 2))
        clear_btn.bind("<Button-1>", lambda _: self._clear_search())

    def _on_search_focus_in(self, _):
        if self.search_entry.get() == self.placeholder:
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=Theme.TEXT_PRIMARY)

    def _on_search_focus_out(self, _):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.config(fg=Theme.TEXT_MUTED)

    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(fg=Theme.TEXT_MUTED)
        self.root.focus_set()

    def _execute_search(self, _):
        query = self.search_var.get().strip()
        if not query or query == self.placeholder:
            return

        messagebox.showinfo(
            "CurioLab Search Results",
            f"Query: '{query}'\n\n"
            f"Found 4 relevant laboratory records:\n"
            f"1. [Experiment] Quantum Wavepacket Dispersal ({query})\n"
            f"2. [Knowledge] Theoretical Framework on {query.capitalize()}\n"
            f"3. [Case #104] Investigation into {query}\n"
            f"4. [Journal] Preliminary lab observations regarding {query}"
        )

    def _build_notification_btn(self, parent):
        """Clickable bell notification icon with unread badge."""
        self.notif_frame = tk.Frame(parent, bg=Theme.BG_HEADER, cursor="hand2", padx=6, pady=18)
        self.notif_frame.pack(side="right", padx=(0, 16))

        box = tk.Frame(self.notif_frame, bg=Theme.BG_INPUT,
                       highlightbackground=Theme.BORDER_MUTED,
                       highlightthickness=1, padx=8, pady=4)
        box.pack(side="left")

        bell = tk.Label(box, text="🔔", font=("Segoe UI", 11),
                        bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY, cursor="hand2")
        bell.pack(side="left")

        self.unread_badge = tk.Label(box, text=" 4 ", font=("Segoe UI", 7, "bold"),
                                     bg=Theme.ROSE, fg="#FFFFFF")
        self.unread_badge.pack(side="left", padx=(4, 0))

        for w in (self.notif_frame, box, bell, self.unread_badge):
            w.bind("<Button-1>", self._toggle_notifications)

    def _toggle_notifications(self, event):
        """Displays or closes floating notification center."""
        x = event.x_root - 180
        y = event.y_root + 20
        NotificationPopup(self.root, x, y, on_clear_callback=self._clear_notifications)

    def _clear_notifications(self):
        self.unread_badge.config(text=" 0 ", bg=Theme.TEXT_MUTED)

    def _build_user_profile(self, parent):
        """User avatar and credentials pill."""
        prof_frame = tk.Frame(parent, bg=Theme.BG_INPUT,
                              highlightbackground=Theme.BORDER_MUTED,
                              highlightthickness=1, padx=10, pady=5, cursor="hand2")
        prof_frame.pack(side="right", pady=16)

        # Avatar circle simulation
        avatar = tk.Label(prof_frame, text="EV", font=("Segoe UI", 9, "bold"),
                          bg=Theme.PURPLE, fg="#FFFFFF", padx=6, pady=2)
        avatar.pack(side="left", padx=(0, 8))

        info_col = tk.Frame(prof_frame, bg=Theme.BG_INPUT)
        info_col.pack(side="left")

        name = tk.Label(info_col, text="Dr. Elena Vance", font=("Segoe UI", 8, "bold"),
                        bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY)
        name.pack(anchor="w")

        role = tk.Label(info_col, text="Lead Investigator", font=("Segoe UI", 7),
                        bg=Theme.BG_INPUT, fg=Theme.CYAN)
        role.pack(anchor="w")

        for w in (prof_frame, avatar, info_col, name, role):
            w.bind("<Button-1>", lambda _: messagebox.showinfo(
                "Researcher Profile",
                "Name: Dr. Elena Vance\n"
                "Designation: Lead Research Investigator\n"
                "Security Clearance: Level 5 (Quantum & Neural Lab)\n"
                "Active Projects: 4\n"
                "Laboratory: CurioLab Alpha Facility"
            ))

    # -------------------------------------------------------------------------
    # PAGE REGISTRATION & NAVIGATION ROUTING
    # -------------------------------------------------------------------------
    def _initialize_pages(self):
        """Instantiates all application pages."""
        # 1. Discovery Hub (Default)
        self.pages["Discovery Hub"] = DiscoveryHubView(self.content_area, self)

        # 2. Experiment Lab (Interactive Experimental Simulation Suite)
        self.pages["Experiment Lab"] = ExperimentLabView(self.content_area, self)

        # 3. Research Detective (Fully Developed Investigation Suite)
        self.pages["Research Detective"] = ResearchDetectiveView(self.content_area, self)

        # 4. Knowledge Library
        self.pages["Knowledge Library"] = PlaceholderPageView(
            self.content_area,
            title="Knowledge Library",
            subtitle="Curated repository of foundational papers, interactive models, and cross-domain texts.",
            icon="📚",
            accent_color=Theme.TEAL,
            description="Browse categorized scientific monographs, interactive mathematical proofs, "
                        "and interdisciplinary knowledge trees spanning theoretical physics, neuroscience, "
                        "computer science, and bio-computation.",
            features=[
                ("Deep Taxonomy Filter", "Sort by domain, mathematical rigor, publication epoch, or research group."),
                ("Interactive Equation Inspectors", "Hover over complex equations to break down tensor terms and units."),
                ("Citation Graph Explorer", "Trace how seminal discoveries inspired contemporary technological breakthroughs."),
                ("Personal Annotation Highlighting", "Attach personal lab thoughts directly onto digital paper margins.")
            ],
            sample_cards=[
                {"title": "Topological Phases of Matter", "desc": "Comprehensive overview of Chern insulators and Majorana fermion edge modes.", "tag": "CONDENSED MATTER"},
                {"title": "Information Theory & Entropy", "desc": "Claude Shannon's foundational proofs on channel capacity and entropy limits.", "tag": "INFORMATION THEORY"},
                {"title": "The Synaptic Plasticity Compendium", "desc": "Long-term potentiation, spike-timing-dependent plasticity, and memory formation.", "tag": "NEUROSCIENCE"},
            ],
            app=self
        )

        # 5. Research Galaxy
        self.pages["Research Galaxy"] = PlaceholderPageView(
            self.content_area,
            title="Research Galaxy",
            subtitle="Discover connections, synergies, and bridges between disparate disciplines.",
            icon="🌌",
            accent_color=Theme.BLUE,
            description="Navigate a multidimensional constellation of human knowledge. "
                        "Watch how thermodynamics connects with information theory, or how evolutionary biology "
                        "influences genetic algorithm optimization in artificial intelligence.",
            features=[
                ("Interactive Force-Directed Node Graph", "Pan and zoom across interconnected epistemological domains."),
                ("Epistemic Bridge Highlighting", "Pinpoint unexpected conceptual bridges between completely different sciences."),
                ("Serendipity Discovery Engine", "Generates novel cross-disciplinary research prompts at the press of a button."),
                ("Domain Affinity Heatmaps", "View density of contemporary research papers clustering around knowledge nodes.")
            ],
            sample_cards=[
                {"title": "Thermodynamics ⟷ Information Theory", "desc": "Landauer's Principle: the minimum physical energy dissipation of erasing a single bit.", "tag": "BRIDGE NODE"},
                {"title": "Neurobiology ⟷ Deep Learning", "desc": "Transforming biological dendritic computation into attention mechanisms and transformers.", "tag": "BRIDGE NODE"},
                {"title": "Quantum Mechanics ⟷ Cryptography", "desc": "From Shor's factoring algorithm to post-quantum lattice-based encryption standards.", "tag": "BRIDGE NODE"},
            ],
            app=self
        )

        # 6. Discovery Journal
        self.pages["Discovery Journal"] = PlaceholderPageView(
            self.content_area,
            title="Discovery Journal",
            subtitle="Your personal scientific logbook, hypothesis tracker, and laboratory record.",
            icon="📓",
            accent_color=Theme.EMERALD,
            description="Document your intellectual journey. Record spontaneous hypotheses, "
                        "attach simulation parameters, bookmark library papers, and timestamp breakthrough moments.",
            features=[
                ("Rich Laboratory Notebook Editor", "Record observations with Markdown, LaTeX symbols, and parameter tags."),
                ("Chronological Discovery Timeline", "Trace the evolution of your understanding across calendar months."),
                ("Hypothesis Status Tracking", "Mark entries as 'Formulated', 'Testing', 'Verified', or 'Refuted'."),
                ("Encrypted Local Export", "Export lab notes to standardized PDF, Markdown, and JSON archives.")
            ],
            sample_cards=[
                {"title": "Log #204: Quantum Phase Drift", "desc": "Recorded anomalous 0.04 rad phase shift during 15 mK resonator test run.", "tag": "LOG ENTRY"},
                {"title": "Log #203: Randomness Invariance", "desc": "Verified entropy output of atmospheric noise generator against Dieharder suite.", "tag": "LOG ENTRY"},
                {"title": "Log #202: Synaptic Simulation Setup", "desc": "Calibrated 10,000 Hodgkin-Huxley neuron array with Poisson spike inputs.", "tag": "LOG ENTRY"},
            ],
            app=self
        )

        # 7. Settings
        self.pages["Settings"] = PlaceholderPageView(
            self.content_area,
            title="Settings & Laboratory Configuration",
            subtitle="Configure workspace visual aesthetics, simulation fidelity, and data preferences.",
            icon="⚙️",
            accent_color=Theme.AMBER,
            description="Customize your CurioLab operating parameters. Adjust graphic rendering rates, "
                        "manage local simulation caches, configure notification filters, and toggle dark lab themes.",
            features=[
                ("Graphic & Canvas Rendering Quality", "Toggle 60FPS high-fidelity vs battery-saver rendering pipelines."),
                ("Telemetry & Privacy Safeguards", "CurioLab operates 100% offline — zero telemetry or tracking sent."),
                ("Color Palette Customizer", "Switch between Deep Obsidian, Cyber Violet, and High-Contrast Teal."),
                ("Cache & Storage Manager", "Clear temporary simulation buffers and compact journal indices.")
            ],
            sample_cards=[
                {"title": "Workspace Theme", "desc": "Currently Active: Deep Obsidian Lab (Cyberpunk Teal/Cyan/Purple Accent).", "tag": "APPEARANCE"},
                {"title": "Simulation Engine Mode", "desc": "Hardware acceleration configured for maximum local precision.", "tag": "COMPUTATION"},
                {"title": "Data Security & Local Storage", "desc": "All logs stored strictly on local device in zero-cloud offline mode.", "tag": "PRIVACY"},
            ],
            app=self
        )

        # 8. Help & About
        self.pages["Help & About"] = PlaceholderPageView(
            self.content_area,
            title="Help & About CurioLab",
            subtitle="CurioLab — An Interactive Research & Discovery Platform v1.0.0",
            icon="❓",
            accent_color=Theme.CYAN_BRIGHT,
            description="CurioLab is designed to rekindle the joy of scientific inquiry. "
                        "Through interactive experiments, investigative challenges, and connected concept graphs, "
                        "CurioLab bridges the gap between passive reading and active laboratory discovery.",
            features=[
                ("Keyboard Navigation", "Use Ctrl+F for Search, Ctrl+1..8 for instantaneous page switching."),
                ("Zero External Dependencies", "Built purely with Python and Tkinter for maximum desktop portability."),
                ("Open Scientific Spirit", "Inspired by Feynman, Shannon, Lovelace, Turing, and Curie."),
                ("Interactive Architecture", "Designed for students, researchers, polymaths, and curious minds.")
            ],
            sample_cards=[
                {"title": "Version Specification", "desc": "CurioLab Desktop Core v1.0.0 (Research Edition) • Python Desktop GUI.", "tag": "BUILD INFO"},
                {"title": "Design Philosophy", "desc": "Dark futuristic laboratory aesthetic with zero web bloat.", "tag": "PHILOSOPHY"},
                {"title": "Support & Documentation", "desc": "Comprehensive offline user manual and lab protocol guides included.", "tag": "DOCUMENTATION"},
            ],
            app=self
        )

    def navigate_to(self, page_name):
        """Switches the visible page inside content_area without creating new windows."""
        if page_name not in self.pages:
            return

        # Hide currently active page
        for p in self.pages.values():
            p.pack_forget()

        # Update current page tracking
        self.current_page_name = page_name

        # Update sidebar button states
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn["frame"].config(bg=Theme.BG_CARD)
                btn["indicator"].config(bg=Theme.CYAN)
                btn["icon"].config(bg=Theme.BG_CARD, fg=Theme.CYAN)
                btn["label"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 10, "bold"))
            else:
                btn["frame"].config(bg=Theme.BG_SIDEBAR)
                btn["indicator"].config(bg=Theme.BG_SIDEBAR)
                btn["icon"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED)
                btn["label"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY, font=("Segoe UI", 10))

        # Update top header title & subtitle
        self.header_title.config(text=page_name)
        subtitles = {
            "Discovery Hub": "Laboratory Overview & Real-Time Research Intel",
            "Experiment Lab": "Interactive Experiments in Computing, Mathematics & Data",
            "Research Detective": "Question the evidence. Follow the clues. Discover the truth.",
            "Knowledge Library": "Curated Multidisciplinary Papers & Monographs",
            "Research Galaxy": "Constellation of Connected Scientific Concepts",
            "Discovery Journal": "Personal Scientific Notes, Logs & Breakthroughs",
            "Settings": "Laboratory Parameters, Aesthetics & Local Storage",
            "Help & About": "Platform Specifications, Shortcuts & Mission",
        }
        self.header_subtitle.config(text=subtitles.get(page_name, "Interactive Research Platform"))

        # Pack and display target page
        self.pages[page_name].pack(fill="both", expand=True)


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
def main():
    """Launches the CurioLab Desktop Application."""
    root = tk.Tk()

    # Set Windows taskbar application icon / process model if applicable
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # High DPI crisp font scaling on Windows
    except Exception:
        pass

    app = CurioLabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
