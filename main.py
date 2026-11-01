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
import sys

from app_state import AppState
from theme import Theme
from knowledge_library import KnowledgeLibraryView
from research_galaxy import ResearchGalaxyView
from discovery_journal import DiscoveryJournalView
from settings import SettingsView
from help_about import HelpAboutView
from research_detective import ResearchDetectiveView
from experiment_lab import ExperimentLabView


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

        self.val_lbl = val_lbl
        self.title_lbl = title_lbl
        self.sub_lbl = sub_lbl
        self.trend_lbl = trend_lbl

        self.child_labels = [top_row, icon_lbl, trend_lbl, val_lbl, title_lbl, sub_lbl]
        for child in self.child_labels:
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def update_values(self, value=None, title=None, subtitle=None, trend=None):
        """Dynamically updates metric value, title, subtitle, and trend pill."""
        if value is not None:
            self.val_lbl.config(text=str(value))
        if title is not None:
            self.title_lbl.config(text=str(title))
        if subtitle is not None:
            self.sub_lbl.config(text=str(subtitle))
        if trend is not None:
            self.trend_lbl.config(text=f" ● {trend} ")

    def _on_enter(self, _):
        self.config(bg=Theme.BG_CARD_HOVER, highlightbackground=self.accent_color)
        for child in self.child_labels:
            if isinstance(child, tk.Label):
                try:
                    if child.cget("text") and "●" in child.cget("text"):
                        continue  # keep trend pill bg
                except Exception:
                    pass
            child.config(bg=Theme.BG_CARD_HOVER)

    def _on_leave(self, _):
        self.config(bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_SUBTLE)
        for child in self.child_labels:
            if isinstance(child, tk.Label):
                try:
                    if child.cget("text") and "●" in child.cget("text"):
                        continue
                except Exception:
                    pass
            child.config(bg=Theme.BG_CARD)


class ScrollableFrame(tk.Frame):
    """
    A smooth scrollable container using Canvas and Scrollbar.
    Automatically resizes child width to prevent horizontal overflow.
    Supports Windows mousewheel scrolling.
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

        # Dynamically resize inner frame width to match canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel binding
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
        # Linux bindings
        widget.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-32, "units"))
        widget.bind("<Button-5>", lambda e: self.canvas.yview_scroll(32, "units"))


# =============================================================================
# NOTIFICATION DROPDOWN / MODAL
# =============================================================================
class NotificationPopup(tk.Toplevel):
    """Futuristic laboratory notification center dropdown with interactive navigation."""
    def __init__(self, parent, x, y, on_clear_callback=None, app_state=None, app_instance=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=Theme.BG_CARD_ELEVATED)
        self.geometry(f"390x440+{x}+{y}")
        self.attributes("-topmost", True)
        self.on_clear = on_clear_callback
        self.app_state = app_state
        self.app_instance = app_instance

        # Border wrapper
        wrapper = tk.Frame(self, bg=Theme.BG_CARD_ELEVATED,
                           highlightbackground=Theme.BORDER_GLOW,
                           highlightthickness=1, padx=14, pady=12)
        wrapper.pack(fill="both", expand=True)

        # Header
        hdr = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        hdr.pack(fill="x", pady=(0, 8))

        title = tk.Label(hdr, text="🔔 Lab Notifications", font=("Segoe UI", 11, "bold"),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        title.pack(side="left")

        close_btn = tk.Label(hdr, text="✕", font=("Segoe UI", 10, "bold"),
                             bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.destroy())

        # Scrollable container for cards
        canvas_container = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        canvas_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_container, bg=Theme.BG_CARD_ELEVATED, highlightthickness=0)
        vbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)

        notif_list_frame = tk.Frame(canvas, bg=Theme.BG_CARD_ELEVATED)
        win_id = canvas.create_window((0, 0), window=notif_list_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")

        notif_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        # Notification items
        notifications = self.app_state.notifications if (self.app_state and hasattr(self.app_state, "notifications")) else []

        if not notifications:
            empty_box = tk.Frame(notif_list_frame, bg=Theme.BG_INPUT, padx=14, pady=24)
            empty_box.pack(fill="x", pady=12)
            tk.Label(empty_box, text="No Notifications", font=("Segoe UI", 10, "bold"),
                     bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack()
            tk.Label(empty_box, text="Laboratory events and milestones will appear here.",
                     font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED).pack(pady=(4, 0))
        else:
            for notif in notifications:
                nid = notif.get("id")
                is_read = notif.get("read", False)
                accent = notif.get("accent", Theme.CYAN)
                target_page = notif.get("target_page")
                target_id = notif.get("target_id")

                card = tk.Frame(
                    notif_list_frame,
                    bg=Theme.BG_CARD,
                    highlightbackground=accent if not is_read else Theme.BORDER_SUBTLE,
                    highlightthickness=1,
                    padx=10,
                    pady=8,
                    cursor="hand2"
                )
                card.pack(fill="x", pady=3)

                top_row = tk.Frame(card, bg=Theme.BG_CARD)
                top_row.pack(fill="x")

                t_lbl = tk.Label(top_row, text=notif.get("title", "Notification"),
                                 font=("Segoe UI", 9, "bold"), bg=Theme.BG_CARD, fg=accent, anchor="w")
                t_lbl.pack(side="left", fill="x", expand=True)

                if not is_read:
                    unread_dot = tk.Label(top_row, text=" NEW ", font=("Segoe UI", 6, "bold"),
                                          bg=Theme.ROSE, fg="#FFFFFF", padx=3, pady=1)
                    unread_dot.pack(side="right", padx=(4, 0))

                time_lbl = tk.Label(top_row, text=notif.get("timestamp", "Recent"),
                                    font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
                time_lbl.pack(side="right")

                d_lbl = tk.Label(card, text=notif.get("desc", ""), font=("Segoe UI", 8),
                                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                                 wraplength=330, justify="left")
                d_lbl.pack(anchor="w", pady=(2, 2))

                if target_page:
                    nav_hint = tk.Label(card, text=f"➔ Open in {target_page}",
                                        font=("Segoe UI", 7, "bold"), bg=Theme.BG_CARD, fg=Theme.CYAN)
                    nav_hint.pack(anchor="e")

                def _make_handler(n_item=notif):
                    def _h():
                        if self.app_state:
                            self.app_state.mark_notification_read(n_item["id"])
                        if self.on_clear:
                            self.on_clear()
                        t_page = n_item.get("target_page")
                        t_id = n_item.get("target_id")
                        if t_page and self.app_instance:
                            self.app_instance.navigate_to(t_page)
                            if t_page == "Knowledge Library" and t_id and hasattr(self.app_instance.pages.get(t_page), "select_resource"):
                                self.app_instance.pages[t_page].select_resource(t_id)
                            elif t_page == "Research Galaxy" and t_id and hasattr(self.app_instance.pages.get(t_page), "center_on_node"):
                                self.app_instance.pages[t_page].center_on_node(t_id)
                            elif t_page == "Discovery Journal" and t_id and hasattr(self.app_instance.pages.get(t_page), "select_entry"):
                                self.app_instance.pages[t_page].select_entry(t_id)
                        self.destroy()
                    return _h

                h_func = _make_handler(notif)
                for w in (card, top_row, t_lbl, d_lbl, time_lbl):
                    w.bind("<Button-1>", lambda _, h=h_func: h())

        # Footer actions
        footer = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        footer.pack(fill="x", pady=(8, 0))

        clear_btn = tk.Label(footer, text="✓ Mark all as read",
                             font=("Segoe UI", 8, "underline"),
                             bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN, cursor="hand2")
        clear_btn.pack(side="left")
        clear_btn.bind("<Button-1>", self._clear_all)

        settings_link = tk.Label(footer, text="⚙️ Configure notifications",
                                 font=("Segoe UI", 8),
                                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED, cursor="hand2")
        settings_link.pack(side="right")
        settings_link.bind("<Button-1>", lambda _: (self.destroy(), self.app_instance.navigate_to("Settings") if self.app_instance else None))

        # Auto-dismiss on click outside
        self.bind("<FocusOut>", lambda _: self.destroy())
        self.focus_set()

    def _clear_all(self, _):
        if self.app_state and hasattr(self.app_state, "clear_notifications"):
            self.app_state.clear_notifications()
        if self.on_clear:
            self.on_clear()
        self.destroy()


# =============================================================================
# GLOBAL FEDERATED SEARCH MODAL
# =============================================================================
class GlobalSearchModal(tk.Toplevel):
    """
    Federated multi-module global search modal.
    Searches across Knowledge Library, Research Galaxy, Discovery Journal,
    Experiment Lab, and Research Detective.
    """
    def __init__(self, parent, initial_query, app_instance, app_state):
        super().__init__(parent)
        self.title("CurioLab — Global Federated Search")
        self.configure(bg=Theme.BG_ROOT)
        self.geometry("680x560")
        self.minsize(540, 420)
        self.attributes("-topmost", True)
        self.app_instance = app_instance
        self.app_state = app_state

        self.query_var = tk.StringVar(value=initial_query)

        self._build_header()
        self._build_results_area()

        self.bind("<Escape>", lambda _: self.destroy())
        self.search_entry.bind("<Return>", lambda _: self.execute_search())

        if initial_query:
            self.execute_search()

    def _build_header(self):
        hdr = tk.Frame(self, bg=Theme.BG_HEADER, padx=20, pady=14)
        hdr.pack(fill="x")

        top_line = tk.Frame(hdr, bg=Theme.BG_HEADER)
        top_line.pack(fill="x")

        tk.Label(
            top_line,
            text="🔍 Global Laboratory Federated Search",
            font=("Segoe UI", 12, "bold"),
            bg=Theme.BG_HEADER,
            fg=Theme.TEXT_PRIMARY
        ).pack(side="left")

        close_btn = tk.Label(top_line, text="✕ Esc", font=("Segoe UI", 9, "bold"),
                             bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, padx=8, pady=3, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda _: self.destroy())

        s_row = tk.Frame(hdr, bg=Theme.BG_HEADER)
        s_row.pack(fill="x", pady=(10, 0))

        s_box = tk.Frame(s_row, bg=Theme.BG_INPUT, highlightbackground=Theme.BORDER_MUTED, highlightthickness=1, padx=10, pady=6)
        s_box.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_entry = tk.Entry(
            s_box,
            textvariable=self.query_var,
            font=("Segoe UI", 10),
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            relief="flat"
        )
        self.search_entry.pack(fill="x")
        self.search_entry.focus_set()

        run_btn = tk.Label(
            s_row,
            text=" Search ",
            font=("Segoe UI", 9, "bold"),
            bg=Theme.CYAN,
            fg=Theme.BG_ROOT,
            padx=14,
            pady=6,
            cursor="hand2"
        )
        run_btn.pack(side="right")
        run_btn.bind("<Button-1>", lambda _: self.execute_search())

        self.status_lbl = tk.Label(
            self,
            text="Type a scientific concept, topic, author, or keyword and press Enter.",
            font=("Segoe UI", 8),
            bg=Theme.BG_ROOT,
            fg=Theme.TEXT_MUTED,
            padx=20,
            pady=6
        )
        self.status_lbl.pack(anchor="w")

    def _build_results_area(self):
        container = tk.Frame(self, bg=Theme.BG_ROOT, padx=20, pady=10)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=Theme.BG_ROOT, highlightthickness=0)
        self.vbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.results_frame = tk.Frame(self.canvas, bg=Theme.BG_ROOT)
        self.canvas_win = self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

        self.results_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))

    def execute_search(self):
        query = self.query_var.get().strip()
        for child in self.results_frame.winfo_children():
            child.destroy()

        if not query:
            self.status_lbl.config(text="Please specify a search term.")
            return

        results = self.app_state.search_all(query) if (self.app_state and hasattr(self.app_state, "search_all")) else []
        self.status_lbl.config(text=f"Found {len(results)} matching records across CurioLab modules for '{query}':")

        if not results:
            empty_card = tk.Frame(self.results_frame, bg=Theme.BG_CARD, padx=20, pady=24, highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
            empty_card.pack(fill="x", pady=10)

            tk.Label(empty_card, text="🔍 No Matching Laboratory Records", font=("Segoe UI", 12, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
            tk.Label(empty_card, text=f"No monograph, concept, journal entry, or simulation matched '{query}'.",
                     font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 10))

            tk.Label(empty_card, text="Try suggested search topics:", font=("Segoe UI", 8, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(anchor="w")

            suggestions_row = tk.Frame(empty_card, bg=Theme.BG_CARD)
            suggestions_row.pack(fill="x", pady=(6, 0))

            for kw in ["Quantum", "Entropy", "Neural", "Automata", "Cipher", "Telemetry", "Perceptron"]:
                pill = tk.Label(suggestions_row, text=f"◈ {kw}", font=("Segoe UI", 8),
                                bg=Theme.BG_INPUT, fg=Theme.CYAN, padx=8, pady=3, cursor="hand2")
                pill.pack(side="left", padx=(0, 6))
                pill.bind("<Button-1>", lambda _, k=kw: (self.query_var.set(k), self.execute_search()))
            return

        for r in results:
            cat = r.get("category", "")
            badge = r.get("badge", "")
            accent = r.get("accent", Theme.CYAN)
            target_page = r.get("target_page")
            target_id = r.get("target_id")

            card = tk.Frame(
                self.results_frame,
                bg=Theme.BG_CARD,
                highlightbackground=Theme.BORDER_SUBTLE,
                highlightthickness=1,
                padx=14,
                pady=10,
                cursor="hand2"
            )
            card.pack(fill="x", pady=(0, 8))

            top_row = tk.Frame(card, bg=Theme.BG_CARD)
            top_row.pack(fill="x")

            badge_lbl = tk.Label(top_row, text=f" {badge} ", font=("Segoe UI", 7, "bold"),
                                 bg=Theme.BG_INPUT, fg=accent, padx=4, pady=2)
            badge_lbl.pack(side="left", padx=(0, 8))

            mod_lbl = tk.Label(top_row, text=f"{r.get('icon', '')} {cat}",
                               font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            mod_lbl.pack(side="left")

            nav_btn = tk.Label(top_row, text="Open ➔", font=("Segoe UI", 8, "bold"),
                               bg=Theme.BG_CARD, fg=Theme.CYAN)
            nav_btn.pack(side="right")

            title_lbl = tk.Label(card, text=r.get("title", ""), font=("Segoe UI", 11, "bold"),
                                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w")
            title_lbl.pack(fill="x", pady=(4, 2))

            sub_lbl = tk.Label(card, text=r.get("subtitle", ""), font=("Segoe UI", 8),
                               bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, anchor="w")
            sub_lbl.pack(fill="x")

            if r.get("snippet"):
                snip_lbl = tk.Label(card, text=r.get("snippet", ""), font=("Segoe UI", 8),
                                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, wraplength=600, justify="left", anchor="w")
                snip_lbl.pack(fill="x", pady=(3, 0))

            def _make_open_action(page=target_page, tid=target_id):
                def _act():
                    if page and self.app_instance:
                        self.app_instance.navigate_to(page)
                        if page == "Knowledge Library" and tid and hasattr(self.app_instance.pages.get(page), "select_resource"):
                            self.app_instance.pages[page].select_resource(tid)
                        elif page == "Research Galaxy" and tid and hasattr(self.app_instance.pages.get(page), "center_on_node"):
                            self.app_instance.pages[page].center_on_node(tid)
                        elif page == "Discovery Journal" and tid and hasattr(self.app_instance.pages.get(page), "select_entry"):
                            self.app_instance.pages[page].select_entry(tid)
                    self.destroy()
                return _act

            open_act = _make_open_action(target_page, target_id)
            for w in (card, top_row, badge_lbl, mod_lbl, nav_btn, title_lbl, sub_lbl):
                w.bind("<Button-1>", lambda _, a=open_act: a())


# =============================================================================
# RESEARCHER PROFILE MODAL
# =============================================================================
class UserProfileModal(tk.Toplevel):
    """Researcher Profile & Credentials dossier popup."""
    def __init__(self, parent, x, y, app_state):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=Theme.BG_CARD_ELEVATED)
        self.geometry(f"320x360+{x}+{y}")
        self.attributes("-topmost", True)
        self.app_state = app_state

        wrapper = tk.Frame(self, bg=Theme.BG_CARD_ELEVATED,
                           highlightbackground=Theme.PURPLE,
                           highlightthickness=1, padx=16, pady=14)
        wrapper.pack(fill="both", expand=True)

        top = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        top.pack(fill="x", pady=(0, 10))

        av = tk.Label(top, text="EV", font=("Segoe UI", 12, "bold"),
                      bg=Theme.PURPLE, fg="#FFFFFF", padx=8, pady=4)
        av.pack(side="left", padx=(0, 10))

        info = tk.Frame(top, bg=Theme.BG_CARD_ELEVATED)
        info.pack(side="left")

        tk.Label(info, text="Dr. Elena Vance", font=("Segoe UI", 10, "bold"),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY).pack(anchor="w")
        tk.Label(info, text="Lead Research Investigator", font=("Segoe UI", 8),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.CYAN).pack(anchor="w")

        close_b = tk.Label(top, text="✕", font=("Segoe UI", 9, "bold"),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED, cursor="hand2")
        close_b.pack(side="right", anchor="n")
        close_b.bind("<Button-1>", lambda _: self.destroy())

        tk.Frame(wrapper, bg=Theme.BORDER_SUBTLE, height=1).pack(fill="x", pady=(0, 10))

        tk.Label(wrapper, text="Clearance: Level 5 (Quantum & Neural Systems)",
                 font=("Segoe UI", 8, "bold"), bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED, padx=6, pady=3).pack(fill="x", pady=(0, 10))

        m = self.app_state.get_metrics() if (self.app_state and hasattr(self.app_state, "get_metrics")) else {}

        stats_box = tk.Frame(wrapper, bg=Theme.BG_CARD_ELEVATED)
        stats_box.pack(fill="x")

        stats_data = [
            ("Investigator Score", f"{m.get('detective_score', 0)} pts", Theme.CYAN),
            ("Cleared Challenges", f"{m.get('solved_challenges_count', 0)} / {m.get('total_challenges_count', 14)}", Theme.PURPLE_LIGHT),
            ("Experiments Run", f"{m.get('total_experiment_executions', 0)}", Theme.TEAL),
            ("Verified Hypotheses", f"{m.get('verified_hypotheses', 0)}", Theme.EMERALD),
            ("Curated Bookmarks", f"{m.get('bookmarked_count', 0)} monographs", Theme.AMBER),
            ("Diligence Rating", f"{m.get('diligence_pct', 100.0):.1f}%", Theme.CYAN_BRIGHT)
        ]

        for s_title, s_val, s_col in stats_data:
            row = tk.Frame(stats_box, bg=Theme.BG_CARD_ELEVATED)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=s_title, font=("Segoe UI", 8), bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY).pack(side="left")
            tk.Label(row, text=s_val, font=("Segoe UI", 8, "bold"), bg=Theme.BG_CARD_ELEVATED, fg=s_col).pack(side="right")

        tk.Label(wrapper, text="CurioLab Local Offline Session", font=("Segoe UI", 7),
                 bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED).pack(anchor="center", pady=(14, 0))

        self.bind("<FocusOut>", lambda _: self.destroy())
        self.focus_set()



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

        # Subscribe to AppState observer notifications
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self.update_statistics_display)

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
        """Displays 4 prominent data-driven laboratory statistics cards."""
        stats_frame = tk.Frame(parent, bg=Theme.BG_ROOT)
        stats_frame.pack(fill="x", padx=32, pady=(0, 20))

        stats_frame.columnconfigure(0, weight=1, uniform="stat")
        stats_frame.columnconfigure(1, weight=1, uniform="stat")
        stats_frame.columnconfigure(2, weight=1, uniform="stat")
        stats_frame.columnconfigure(3, weight=1, uniform="stat")

        self.stat_cards = {}

        # 1. Interactive Labs Card
        c1 = StatCard(stats_frame, title="Interactive Labs", value="3",
                      icon="🧪", subtitle="0 executions recorded", accent_color=Theme.CYAN, trend="Ready")
        c1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self.stat_cards["experiments"] = c1

        # 2. Detective Dossiers Card
        c2 = StatCard(stats_frame, title="Dossiers Solved", value="0/14",
                      icon="🔍", subtitle="0 score pts earned", accent_color=Theme.PURPLE, trend="0% closed")
        c2.grid(row=0, column=1, padx=(8, 8), sticky="nsew")
        self.stat_cards["cases"] = c2

        # 3. Demonstration Resources Card
        c3 = StatCard(stats_frame, title="Demo Resources", value="6",
                      icon="📚", subtitle="1 bookmarked for study", accent_color=Theme.TEAL, trend="Curated")
        c3.grid(row=0, column=2, padx=(8, 8), sticky="nsew")
        self.stat_cards["library"] = c3

        # 4. Lab Journal Entries Card
        c4 = StatCard(stats_frame, title="Journal Entries", value="4",
                      icon="💡", subtitle="1 verified hypothesis", accent_color=Theme.EMERALD, trend="Active")
        c4.grid(row=0, column=3, padx=(8, 0), sticky="nsew")
        self.stat_cards["discoveries"] = c4

        # Initial live refresh from AppState
        self.update_statistics_display()

    def update_statistics_display(self):
        """Refreshes the 4 statistics cards with live data calculated from AppState."""
        if not hasattr(self, "stat_cards") or not self.stat_cards:
            return
        if not hasattr(self.app, "state") or self.app.state is None:
            return

        m = self.app.state.get_metrics()

        # 1. Experiments
        exp_runs = m["total_experiment_executions"]
        self.stat_cards["experiments"].update_values(
            value=f"{m['experiments_count']}",
            title="Interactive Labs",
            subtitle=f"{exp_runs} execution{'s' if exp_runs != 1 else ''} recorded",
            trend=f"{exp_runs} runs" if exp_runs > 0 else "Ready"
        )

        # 2. Research Detective Investigation Stages
        solved = m["solved_challenges_count"]
        total = m["total_challenges_count"]
        score = m["detective_score"]
        self.stat_cards["cases"].update_values(
            value=f"{solved}/{total}",
            title="Stages Complete",
            subtitle=f"{score} score pts earned" if score > 0 else "Investigation active",
            trend=f"{m['curriculum_pct']:.0f}% completed"
        )

        # 3. Knowledge Resources
        lib_count = m["library_count"]
        bm_count = m["bookmarked_count"]
        self.stat_cards["library"].update_values(
            value=f"{lib_count}",
            title="Demo Resources",
            subtitle=f"{bm_count} bookmarked for study",
            trend=f"{bm_count} saved"
        )

        # 4. Discoveries (Journal)
        j_count = m["journal_count"]
        v_count = m["verified_hypotheses"]
        self.stat_cards["discoveries"].update_values(
            value=f"{j_count}",
            title="Journal Entries",
            subtitle=f"{v_count} verified hypothesis",
            trend=f"{v_count} verified"
        )

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

            card.bind("<Configure>", lambda e, lbl=d_lbl: lbl.config(wraplength=max(160, e.width - 32)))

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
            card.bind("<Configure>", lambda e, lbl=d_lbl: lbl.config(wraplength=max(200, e.width - 32)))

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

        card.bind("<Configure>", lambda e, ql=q_lbl, el=expl: (
            ql.config(wraplength=max(200, e.width - 40)),
            el.config(wraplength=max(200, e.width - 40))
        ))

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
# EXPERIMENT LAB (CUSTOM EXPERIMENT BUILDER, AST ENGINE & SIMULATION SUITE)
# =============================================================================

# ExperimentLabView is modularized in experiment_lab.py and imported at the top.

# =============================================================================
# RESEARCH DETECTIVE (INVESTIGATION SUITE & CASE FILES)
# =============================================================================

# ResearchDetectiveView is modularized in research_detective.py and imported at the top.


# =============================================================================
# DISCOVERY JOURNAL DRAFT & CITATION REVIEW VIEW
# =============================================================================

class DiscoveryJournalDraftView(tk.Frame):
    """
    Discovery Journal view with active citation draft review,
    laboratory note recording, and in-memory AppState log repository.
    """
    def __init__(self, parent, app):
        super().__init__(parent, bg=Theme.BG_ROOT)
        self.app = app

        # Scrollable container
        self.scroll_frame = ScrollableFrame(self, bg=Theme.BG_ROOT)
        self.scroll_frame.pack(fill="both", expand=True)
        self.content = self.scroll_frame.scrollable_content

        # UI State variables
        self.title_var = tk.StringVar()
        self.domain_var = tk.StringVar(value="General Lab Observation")
        self.status_var = tk.StringVar(value="Formulated")
        self.tags_var = tk.StringVar(value="Citation, Demonstration")

        # Build sections
        self._build_hero(self.content)
        self._build_draft_editor(self.content)
        self._build_entries_repository(self.content)
        self._build_planned_capabilities(self.content)

        # Mousewheel
        self.scroll_frame.bind_mousewheel(self.content)

        # AppState subscription
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.subscribe(self._on_app_state_changed)

        # Initial render of entries
        self._render_entries()

    def _build_hero(self, parent):
        hero = tk.Frame(parent, bg=Theme.BG_CARD_ELEVATED,
                        highlightbackground=Theme.EMERALD,
                        highlightthickness=1, padx=30, pady=24)
        hero.pack(fill="x", padx=32, pady=(24, 18))

        badge = tk.Label(hero, text="◈  DISCOVERY JOURNAL  •  RESEARCH LOGBOOK & CITATION REPOSITORY",
                         font=("Segoe UI", 8, "bold"),
                         bg=Theme.BG_INPUT, fg=Theme.EMERALD,
                         padx=8, pady=3)
        badge.pack(anchor="w")

        top_row = tk.Frame(hero, bg=Theme.BG_CARD_ELEVATED)
        top_row.pack(fill="x", pady=(10, 4))

        i_lbl = tk.Label(top_row, text="📓", font=("Segoe UI", 26),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.EMERALD)
        i_lbl.pack(side="left", padx=(0, 12))

        t_lbl = tk.Label(top_row, text="Discovery Journal", font=("Segoe UI", 22, "bold"),
                         bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_PRIMARY)
        t_lbl.pack(side="left")

        sub_lbl = tk.Label(hero, text="Personal Scientific Notes, Hypotheses & Educational Citations",
                           font=("Segoe UI", 12),
                           bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_SECONDARY)
        sub_lbl.pack(anchor="w")

        desc_lbl = tk.Label(hero,
                            text="Document your intellectual journey. Record spontaneous hypotheses, "
                                 "attach simulation parameters, cite educational monographs from the Knowledge Library, "
                                 "and timestamp breakthrough moments.",
                            font=("Segoe UI", 10),
                            bg=Theme.BG_CARD_ELEVATED, fg=Theme.TEXT_MUTED,
                            wraplength=850, justify="left")
        desc_lbl.pack(anchor="w", pady=(10, 0))

    def _build_draft_editor(self, parent):
        editor_frame = tk.Frame(parent, bg=Theme.BG_CARD,
                                highlightbackground=Theme.BORDER_MUTED,
                                highlightthickness=1, padx=24, pady=20)
        editor_frame.pack(fill="x", padx=32, pady=(0, 20))

        # Title & Alert header
        hdr_row = tk.Frame(editor_frame, bg=Theme.BG_CARD)
        hdr_row.pack(fill="x", pady=(0, 12))

        tk.Label(hdr_row, text="📝 Laboratory Note & Citation Draft Editor",
                 font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left")

        self.feedback_lbl = tk.Label(hdr_row, text="", font=("Segoe UI", 9, "bold"),
                                     bg=Theme.BG_CARD, fg=Theme.EMERALD)
        self.feedback_lbl.pack(side="right")

        # Dynamic Citation Transfer Notification Banner
        self.draft_banner = tk.Frame(editor_frame, bg=Theme.BG_INPUT,
                                     highlightbackground=Theme.CYAN,
                                     highlightthickness=1, padx=12, pady=8)
        tk.Label(self.draft_banner, text="📋 Citation Draft Loaded from Knowledge Library",
                 font=("Segoe UI", 9, "bold"), bg=Theme.BG_INPUT, fg=Theme.CYAN).pack(anchor="w")
        tk.Label(self.draft_banner,
                 text="A demonstration citation has been transferred. Review, edit details below, and save to register this entry into your Discovery Journal.",
                 font=("Segoe UI", 8), bg=Theme.BG_INPUT, fg=Theme.TEXT_SECONDARY).pack(anchor="w")

        # Form Grid
        grid_frame = tk.Frame(editor_frame, bg=Theme.BG_CARD)
        grid_frame.pack(fill="x", pady=(4, 10))
        grid_frame.columnconfigure(1, weight=3)
        grid_frame.columnconfigure(3, weight=1)

        # Row 0: Title & Status
        tk.Label(grid_frame, text="Log Title:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 8))
        self.title_entry = tk.Entry(grid_frame, textvariable=self.title_var,
                                    bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                    insertbackground=Theme.CYAN, font=("Segoe UI", 9),
                                    highlightthickness=1, highlightbackground=Theme.BORDER_MUTED)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=6, padx=(0, 16))

        tk.Label(grid_frame, text="Status:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).grid(row=0, column=2, sticky="w", pady=6, padx=(0, 8))
        self.status_cb = ttk.Combobox(grid_frame, textvariable=self.status_var,
                                      values=["Formulated", "Testing", "Verified", "Refuted"],
                                      state="readonly", width=14, font=("Segoe UI", 9))
        self.status_cb.grid(row=0, column=3, sticky="ew", pady=6)

        # Row 1: Domain & Tags
        tk.Label(grid_frame, text="Domain:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 8))
        self.domain_entry = tk.Entry(grid_frame, textvariable=self.domain_var,
                                     bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                     insertbackground=Theme.CYAN, font=("Segoe UI", 9),
                                     highlightthickness=1, highlightbackground=Theme.BORDER_MUTED)
        self.domain_entry.grid(row=1, column=1, sticky="ew", pady=6, padx=(0, 16))

        tk.Label(grid_frame, text="Tags:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).grid(row=1, column=2, sticky="w", pady=6, padx=(0, 8))
        self.tags_entry = tk.Entry(grid_frame, textvariable=self.tags_var,
                                   bg=Theme.BG_INPUT, fg=Theme.TEXT_PRIMARY,
                                   insertbackground=Theme.CYAN, font=("Segoe UI", 9),
                                   highlightthickness=1, highlightbackground=Theme.BORDER_MUTED)
        self.tags_entry.grid(row=1, column=3, sticky="ew", pady=6)

        # Content Integrity Disclaimer
        disclaimer = tk.Label(
            editor_frame,
            text="ℹ️ Educational Demonstration Reference: Journal citations record demonstration metadata for local learning. They do not represent peer-reviewed publication indexes.",
            font=("Segoe UI", 8),
            bg=Theme.BG_CARD,
            fg=Theme.TEXT_MUTED
        )
        disclaimer.pack(anchor="w", pady=(0, 8))

        # Body Text Area
        tk.Label(editor_frame, text="Log Body & Synthesis Observations:", font=("Segoe UI", 9, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

        self.body_text = tk.Text(
            editor_frame,
            height=8,
            bg=Theme.BG_INPUT,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.CYAN,
            font=("Consolas", 9),
            wrap="word",
            highlightthickness=1,
            highlightbackground=Theme.BORDER_MUTED,
            relief="flat",
            padx=10,
            pady=8
        )
        self.body_text.pack(fill="x", pady=(0, 14))

        # Action Buttons
        btn_row = tk.Frame(editor_frame, bg=Theme.BG_CARD)
        btn_row.pack(fill="x")

        ModernButton(btn_row, text="Save Log Entry", icon="💾",
                     bg_color=Theme.EMERALD,
                     command=self._save_entry).pack(side="left", padx=(0, 10))

        ModernButton(btn_row, text="Clear / Discard", icon="✕",
                     bg_color=Theme.BG_INPUT, text_color=Theme.TEXT_SECONDARY,
                     hover_color=Theme.BORDER_MUTED,
                     command=self._clear_editor).pack(side="left", padx=(0, 10))

        ModernButton(btn_row, text="New Blank Note", icon="✏️",
                     bg_color=Theme.BG_INPUT, text_color=Theme.CYAN,
                     hover_color=Theme.BORDER_MUTED,
                     command=self._new_blank_note).pack(side="left")

    def _build_entries_repository(self, parent):
        self.repo_frame = tk.Frame(parent, bg=Theme.BG_ROOT)
        self.repo_frame.pack(fill="x", padx=32, pady=(0, 20))

        hdr_row = tk.Frame(self.repo_frame, bg=Theme.BG_ROOT)
        hdr_row.pack(fill="x", pady=(0, 10))

        tk.Label(hdr_row, text="📚 Cataloged Journal Entries (AppState In-Memory)",
                 font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_ROOT, fg=Theme.TEXT_PRIMARY).pack(side="left")

        self.repo_count_lbl = tk.Label(hdr_row, text="", font=("Segoe UI", 8, "bold"),
                                       bg=Theme.BG_ROOT, fg=Theme.TEXT_MUTED)
        self.repo_count_lbl.pack(side="right")

        self.entries_cards_box = tk.Frame(self.repo_frame, bg=Theme.BG_ROOT)
        self.entries_cards_box.pack(fill="x")

    def _build_planned_capabilities(self, parent):
        caps_frame = tk.Frame(parent, bg=Theme.BG_CARD,
                              highlightbackground=Theme.BORDER_SUBTLE,
                              highlightthickness=1, padx=24, pady=20)
        caps_frame.pack(fill="x", padx=32, pady=(0, 20))

        tk.Label(caps_frame, text="🔬 Future Discovery Journal Roadmap & Capabilities",
                 font=("Segoe UI", 13, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 12))

        features = [
            ("Rich Laboratory Notebook Editor", "Record observations with Markdown, LaTeX symbols, and parameter tags."),
            ("Chronological Discovery Timeline", "Trace the evolution of your understanding across calendar months."),
            ("Hypothesis Status Tracking", "Mark entries as 'Formulated', 'Testing', 'Verified', or 'Refuted'."),
            ("Encrypted Local Export", "Export lab notes to standardized PDF, Markdown, and JSON archives.")
        ]
        for feat_title, feat_detail in features:
            f_row = tk.Frame(caps_frame, bg=Theme.BG_CARD)
            f_row.pack(fill="x", pady=5)

            dot = tk.Label(f_row, text="◈", font=("Segoe UI", 10),
                           bg=Theme.BG_CARD, fg=Theme.EMERALD)
            dot.pack(side="left", anchor="n", padx=(0, 8))

            info_col = tk.Frame(f_row, bg=Theme.BG_CARD)
            info_col.pack(side="left", fill="x", expand=True)

            tk.Label(info_col, text=feat_title, font=("Segoe UI", 10, "bold"),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x")
            tk.Label(info_col, text=feat_detail, font=("Segoe UI", 9),
                     bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, anchor="w").pack(fill="x")

    def on_navigate_to(self):
        """Called by CurioLabApp.navigate_to when switching to this page."""
        if hasattr(self.app, "state") and self.app.state and self.app.state.pending_journal_draft:
            draft = self.app.state.pending_journal_draft
            self.title_var.set(draft.get("title", ""))
            self.domain_var.set(draft.get("domain", "General Lab Observation"))
            self.status_var.set(draft.get("status", "Formulated"))
            self.tags_var.set(draft.get("tags", "Citation"))
            self.body_text.delete("1.0", "end")
            self.body_text.insert("1.0", draft.get("body", ""))
            try:
                self.draft_banner.pack(fill="x", pady=(0, 12), before=self.title_entry.master)
            except Exception:
                self.draft_banner.pack(fill="x", pady=(0, 12))
            self.feedback_lbl.config(text="Citation draft ready for review!", fg=Theme.CYAN)
        self._render_entries()

    def _save_entry(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Incomplete Log", "Please specify a title before saving this journal entry.")
            return

        domain = self.domain_var.get().strip()
        status = self.status_var.get().strip()
        tags = self.tags_var.get().strip()
        body = self.body_text.get("1.0", "end").strip()

        if hasattr(self.app, "state") and self.app.state:
            new_entry = self.app.state.add_journal_entry(title, domain, status, tags, body)
            self.app.state.pending_journal_draft = None
            try:
                self.draft_banner.pack_forget()
            except Exception:
                pass
            self.feedback_lbl.config(text=f"✓ Entry saved successfully as {new_entry['id']}!", fg=Theme.EMERALD)
            self._render_entries()

    def _clear_editor(self):
        self.title_var.set("")
        self.domain_var.set("General Lab Observation")
        self.status_var.set("Formulated")
        self.tags_var.set("")
        self.body_text.delete("1.0", "end")
        try:
            self.draft_banner.pack_forget()
        except Exception:
            pass
        self.feedback_lbl.config(text="Editor cleared.", fg=Theme.TEXT_MUTED)
        if hasattr(self.app, "state") and self.app.state:
            self.app.state.pending_journal_draft = None

    def _new_blank_note(self):
        self._clear_editor()
        self.title_var.set("Spontaneous Observation #")
        self.title_entry.focus()

    def _delete_entry(self, entry_id):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove journal entry '{entry_id}'?"):
            if hasattr(self.app, "state") and self.app.state:
                self.app.state.delete_journal_entry(entry_id)
                self._render_entries()

    def _render_entries(self):
        for w in self.entries_cards_box.winfo_children():
            w.destroy()

        if not hasattr(self.app, "state") or not self.app.state:
            return

        entries = self.app.state.journal_entries
        self.repo_count_lbl.config(text=f"Showing {len(entries)} recorded log{'s' if len(entries) != 1 else ''}")

        if not entries:
            empty_box = tk.Frame(self.entries_cards_box, bg=Theme.BG_CARD, padx=20, pady=24,
                                 highlightbackground=Theme.BORDER_SUBTLE, highlightthickness=1)
            empty_box.pack(fill="x", pady=8)
            tk.Label(empty_box, text="No journal entries recorded in this session.",
                     font=("Segoe UI", 9), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack()
            return

        status_colors = {
            "Formulated": Theme.CYAN,
            "Testing": Theme.AMBER,
            "Verified": Theme.EMERALD,
            "Refuted": Theme.ROSE
        }

        for entry in entries:
            card = tk.Frame(self.entries_cards_box, bg=Theme.BG_CARD,
                            highlightbackground=Theme.BORDER_SUBTLE,
                            highlightthickness=1, padx=16, pady=14)
            card.pack(fill="x", pady=(0, 10))

            # Header row
            top_line = tk.Frame(card, bg=Theme.BG_CARD)
            top_line.pack(fill="x")

            status = entry.get("status", "Formulated")
            st_color = status_colors.get(status, Theme.CYAN)

            st_pill = tk.Label(top_line, text=f" {status.upper()} ",
                               font=("Segoe UI", 7, "bold"),
                               bg=Theme.BG_INPUT, fg=st_color, padx=4, pady=2)
            st_pill.pack(side="left")

            dom_lbl = tk.Label(top_line, text=f"•  {entry.get('domain', 'General')}",
                               font=("Segoe UI", 8), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            dom_lbl.pack(side="left", padx=(8, 0))

            time_lbl = tk.Label(top_line, text=f"📅 {entry.get('timestamp', '')}",
                                font=("Segoe UI", 7), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED)
            time_lbl.pack(side="right")

            # Title & Delete action row
            title_line = tk.Frame(card, bg=Theme.BG_CARD)
            title_line.pack(fill="x", pady=(6, 4))

            t_lbl = tk.Label(title_line, text=entry.get("title", "Untitled Log"),
                             font=("Segoe UI", 11, "bold"),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                             anchor="w")
            t_lbl.pack(side="left", fill="x", expand=True)

            del_btn = tk.Label(title_line, text="🗑 Delete", font=("Segoe UI", 8),
                               bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, cursor="hand2")
            del_btn.pack(side="right")
            del_btn.bind("<Button-1>", lambda _, eid=entry["id"]: self._delete_entry(eid))
            del_btn.bind("<Enter>", lambda _, b=del_btn: b.config(fg=Theme.ROSE))
            del_btn.bind("<Leave>", lambda _, b=del_btn: b.config(fg=Theme.TEXT_MUTED))

            # Tags
            if entry.get("tags"):
                tags_row = tk.Frame(card, bg=Theme.BG_CARD)
                tags_row.pack(fill="x", pady=(0, 6))
                for tg in entry.get("tags").split(","):
                    tg_clean = tg.strip()
                    if tg_clean:
                        tk.Label(tags_row, text=f"#{tg_clean}", font=("Segoe UI", 7),
                                 bg=Theme.BG_INPUT, fg=Theme.TEXT_MUTED,
                                 padx=4, pady=1).pack(side="left", padx=(0, 4))

            # Body snippet / content
            body_snippet = entry.get("body", "")
            if len(body_snippet) > 280:
                body_snippet = body_snippet[:277] + "..."
            b_lbl = tk.Label(card, text=body_snippet, font=("Segoe UI", 9),
                             bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                             wraplength=800, justify="left", anchor="w")
            b_lbl.pack(fill="x")

        self.scroll_frame.bind_mousewheel(self.entries_cards_box)

    def _on_app_state_changed(self):
        self._render_entries()


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

        # Instantiate centralized in-memory AppState
        self.state = AppState()

        # Build application shell
        self._build_sidebar()
        self._build_main_area()

        # Subscribe header notification badge to AppState
        self.state.subscribe(self._update_header_notif_badge)

        # Initialize pages dictionary
        self.pages = {}
        self._initialize_pages()

        # Display default page from preferences (defaulting to Discovery Hub)
        default_landing = self.state.preferences.get("default_landing_page", "Discovery Hub")
        self.navigate_to(default_landing)

        # Global keyboard shortcuts: Ctrl+F (or Cmd+F on Mac) for search
        self.root.bind("<Control-f>", lambda _: self.search_entry.focus_set())
        self.root.bind("<Command-f>", lambda _: self.search_entry.focus_set())

        # Page navigation shortcuts (Ctrl+1..8 and Cmd+1..8)
        page_names = [
            "Discovery Hub", "Experiment Lab", "Research Detective",
            "Knowledge Library", "Research Galaxy", "Discovery Journal",
            "Settings", "Help & About"
        ]
        for idx, p_name in enumerate(page_names, 1):
            self.root.bind(f"<Control-Key-{idx}>", lambda _, name=p_name: self.navigate_to(name))
            self.root.bind(f"<Command-Key-{idx}>", lambda _, name=p_name: self.navigate_to(name))

        # Application-wide unified smooth mouse-wheel & trackpad event dispatcher
        self.root.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_global_button4, add="+")
        self.root.bind_all("<Button-5>", self._on_global_button5, add="+")

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

        # Thin glowing transition accent strip at the bottom of header
        self.nav_transition_bar = tk.Frame(self.header, bg=Theme.CYAN, height=2)
        self.nav_transition_bar.pack(side="bottom", fill="x")

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
        GlobalSearchModal(self.root, query, self, self.state)

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
        NotificationPopup(self.root, x, y, on_clear_callback=self._clear_notifications, app_state=self.state, app_instance=self)

    def _clear_notifications(self):
        if hasattr(self, "state") and self.state:
            self.state.clear_notifications()
        self.unread_badge.config(text=" 0 ", bg=Theme.TEXT_MUTED)

    def _update_header_notif_badge(self):
        """Updates the notification bell badge based on live unread count."""
        if hasattr(self, "unread_badge") and hasattr(self, "state") and self.state:
            m = self.state.get_metrics()
            unread = m["unread_notifs"]
            if unread > 0:
                self.unread_badge.config(text=f" {unread} ", bg=Theme.ROSE)
            else:
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
            w.bind("<Button-1>", lambda event: UserProfileModal(self.root, event.x_root - 140, event.y_root + 20, self.state))

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
        self.pages["Knowledge Library"] = KnowledgeLibraryView(self.content_area, self)

        # 5. Research Galaxy
        self.pages["Research Galaxy"] = ResearchGalaxyView(self.content_area, self)

        # 6. Discovery Journal
        self.pages["Discovery Journal"] = DiscoveryJournalView(self.content_area, self)

        # 7. Settings
        self.pages["Settings"] = SettingsView(self.content_area, self)

        # 8. Help & About
        self.pages["Help & About"] = HelpAboutView(self.content_area, self)

    def refresh_theme(self):
        """Refreshes shell visual tokens and active page styling when Theme changes."""
        self.root.configure(bg=Theme.BG_ROOT)
        if hasattr(self, "sidebar"):
            self.sidebar.configure(bg=Theme.BG_SIDEBAR)
        if hasattr(self, "main_container"):
            self.main_container.configure(bg=Theme.BG_ROOT)
        if hasattr(self, "header"):
            self.header.configure(bg=Theme.BG_HEADER, highlightbackground=Theme.BORDER_SUBTLE)
        if hasattr(self, "header_title"):
            self.header_title.configure(bg=Theme.BG_HEADER, fg=Theme.TEXT_PRIMARY)
        if hasattr(self, "header_subtitle"):
            self.header_subtitle.configure(bg=Theme.BG_HEADER, fg=Theme.TEXT_MUTED)
        if hasattr(self, "content_area"):
            self.content_area.configure(bg=Theme.BG_ROOT)
        if hasattr(self, "nav_transition_bar"):
            self.nav_transition_bar.configure(bg=Theme.CYAN)
        if hasattr(self, "nav_buttons"):
            for name, btn in self.nav_buttons.items():
                if name == self.current_page_name:
                    btn["frame"].config(bg=Theme.BG_CARD)
                    btn["indicator"].config(bg=Theme.CYAN)
                    btn["icon"].config(bg=Theme.BG_CARD, fg=Theme.CYAN)
                    btn["label"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY)
                else:
                    btn["frame"].config(bg=Theme.BG_SIDEBAR)
                    btn["indicator"].config(bg=Theme.BG_SIDEBAR)
                    btn["icon"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED)
                    btn["label"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY)

    def navigate_to(self, page_name):
        """
        Seamlessly switches the visible page inside content_area without visible flicker,
        preserving all component states and applying distinct module accent highlights.
        """
        if page_name not in self.pages:
            return

        prev_page = getattr(self, "current_page_name", None)

        # Distinct futuristic laboratory module accent palette
        module_accents = {
            "Discovery Hub": Theme.CYAN_BRIGHT,
            "Experiment Lab": Theme.PURPLE,
            "Research Detective": Theme.CYAN,
            "Knowledge Library": Theme.TEAL,
            "Research Galaxy": Theme.PURPLE_LIGHT,
            "Discovery Journal": Theme.EMERALD,
            "Settings": Theme.AMBER,
            "Help & About": Theme.BLUE,
        }
        mod_accent = module_accents.get(page_name, Theme.CYAN)

        # 1. Seamless zero-flicker transition: pack target page first so window is never blank
        target_page = self.pages[page_name]
        target_page.pack(fill="both", expand=True)

        # 2. Hide previous page without unmapping or destroying any internal widgets
        if prev_page and prev_page != page_name and prev_page in self.pages:
            self.pages[prev_page].pack_forget()

        # Update current page tracking
        self.current_page_name = page_name

        # 3. Update sidebar active button styling with matching module accent
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn["frame"].config(bg=Theme.BG_CARD)
                btn["indicator"].config(bg=mod_accent)
                btn["icon"].config(bg=Theme.BG_CARD, fg=mod_accent)
                btn["label"].config(bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, font=("Segoe UI", 10, "bold"))
            else:
                btn["frame"].config(bg=Theme.BG_SIDEBAR)
                btn["indicator"].config(bg=Theme.BG_SIDEBAR)
                btn["icon"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED)
                btn["label"].config(bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY, font=("Segoe UI", 10))

        # 4. Update top header title, subtitle & transition accent bar
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

        if hasattr(self, "nav_transition_bar"):
            self.nav_transition_bar.config(bg=mod_accent)

        # 5. Refresh page state observers if defined
        if page_name == "Discovery Hub" and hasattr(self.pages[page_name], "update_statistics_display"):
            self.pages[page_name].update_statistics_display()
        elif hasattr(self.pages[page_name], "on_navigate_to"):
            self.pages[page_name].on_navigate_to()

    # -------------------------------------------------------------------------
    # APPLICATION-WIDE SMOOTH MOUSEWHEEL & TRACKPAD SCROLLING
    # -------------------------------------------------------------------------
    def _on_global_mousewheel(self, event):
        """
        Application-wide smooth mouse-wheel and trackpad event dispatcher.
        Dynamically finds the interactive component or scrollable canvas under the cursor.
        """
        try:
            w = self.root.winfo_containing(event.x_root, event.y_root)
        except Exception:
            return

        cur = w
        while cur and cur != self.root:
            # 1. Research Galaxy Canvas (Zooming)
            if getattr(cur, "_is_galaxy_canvas", False):
                g_view = getattr(cur, "galaxy_view", None)
                if g_view and hasattr(g_view, "_on_canvas_mousewheel"):
                    g_view._on_canvas_mousewheel(event)
                return "break"

            # 2. Text widget with overflow content (Text editing/reading)
            if isinstance(cur, tk.Text):
                try:
                    yview = cur.yview()
                    if yview != (0.0, 1.0):
                        delta = event.delta
                        step = -1 if delta > 0 else 1
                        cur.yview_scroll(step, "units")
                        return "break"
                except Exception:
                    pass

            # 3. Dedicated CurioLab scrollable canvas (Smooth pixel scrolling)
            if getattr(cur, "_is_curiolab_scroll_canvas", False):
                try:
                    if sys.platform == "darwin":
                        if abs(event.delta) < 120:
                            step = int(-1 * event.delta * 16)
                            if step == 0 and event.delta != 0:
                                step = -2 if event.delta > 0 else 2
                        else:
                            step = int(-1 * (event.delta / 120.0) * 36)
                    else:
                        step = int(-1 * (event.delta / 120.0) * 36)
                    cur.yview_scroll(step, "units")
                    return "break"
                except Exception:
                    pass

            cur = getattr(cur, "master", None)

    def _on_global_button4(self, event):
        self._dispatch_scroll_step(event, -32)

    def _on_global_button5(self, event):
        self._dispatch_scroll_step(event, 32)

    def _dispatch_scroll_step(self, event, step):
        try:
            w = self.root.winfo_containing(event.x_root, event.y_root)
        except Exception:
            return

        cur = w
        while cur and cur != self.root:
            if getattr(cur, "_is_galaxy_canvas", False):
                g_view = getattr(cur, "galaxy_view", None)
                if g_view and hasattr(g_view, "_zoom_view"):
                    g_view._zoom_view(1.08 if step < 0 else 0.92, anchor_x=event.x, anchor_y=event.y)
                return "break"
            if getattr(cur, "_is_curiolab_scroll_canvas", False):
                try:
                    cur.yview_scroll(step, "units")
                    return "break"
                except Exception:
                    pass
            cur = getattr(cur, "master", None)


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
