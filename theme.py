"""
CurioLab — Design System & Theme Tokens
========================================
Futuristic research-laboratory dark color palette with multi-theme support
and dynamic accent configuration.
"""

class Theme:
    """Futuristic research-laboratory dark color palette."""
    CURRENT_THEME_NAME = "Deep Obsidian"

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

    # Preset Palette Configurations
    THEMES = {
        "Deep Obsidian": {
            "BG_ROOT": "#090D16",
            "BG_SIDEBAR": "#06080F",
            "BG_HEADER": "#0B101D",
            "BG_CARD": "#111726",
            "BG_CARD_HOVER": "#172033",
            "BG_CARD_ELEVATED": "#151D2E",
            "BG_INPUT": "#0D1322",
            "BORDER_SUBTLE": "#1C2638",
            "BORDER_MUTED": "#24324A",
            "BORDER_GLOW": "#38BDF8",
            "TEXT_PRIMARY": "#F8FAFC",
            "TEXT_SECONDARY": "#94A3B8",
            "TEXT_MUTED": "#64748B"
        },
        "Cyber Violet": {
            "BG_ROOT": "#0C0A17",
            "BG_SIDEBAR": "#080612",
            "BG_HEADER": "#110E21",
            "BG_CARD": "#17142E",
            "BG_CARD_HOVER": "#211D3F",
            "BG_CARD_ELEVATED": "#1D1838",
            "BG_INPUT": "#100D22",
            "BORDER_SUBTLE": "#271F47",
            "BORDER_MUTED": "#362C61",
            "BORDER_GLOW": "#8B5CF6",
            "TEXT_PRIMARY": "#FAF5FF",
            "TEXT_SECONDARY": "#C4B5FD",
            "TEXT_MUTED": "#7C6DAF"
        },
        "Quantum Cyan": {
            "BG_ROOT": "#040D17",
            "BG_SIDEBAR": "#020810",
            "BG_HEADER": "#071424",
            "BG_CARD": "#0B1E33",
            "BG_CARD_HOVER": "#102B47",
            "BG_CARD_ELEVATED": "#0F2640",
            "BG_INPUT": "#061526",
            "BORDER_SUBTLE": "#133557",
            "BORDER_MUTED": "#1E4B7A",
            "BORDER_GLOW": "#22D3EE",
            "TEXT_PRIMARY": "#F0FDFF",
            "TEXT_SECONDARY": "#A5F3FC",
            "TEXT_MUTED": "#4F829E"
        },
        "Solar Amber": {
            "BG_ROOT": "#120E08",
            "BG_SIDEBAR": "#0A0703",
            "BG_HEADER": "#1A130B",
            "BG_CARD": "#24190D",
            "BG_CARD_HOVER": "#332414",
            "BG_CARD_ELEVATED": "#2B1E11",
            "BG_INPUT": "#171008",
            "BORDER_SUBTLE": "#3D2B17",
            "BORDER_MUTED": "#543C21",
            "BORDER_GLOW": "#F59E0B",
            "TEXT_PRIMARY": "#FFFBEB",
            "TEXT_SECONDARY": "#FDE68A",
            "TEXT_MUTED": "#8C7147"
        }
    }

    ACCENT_PRESETS = {
        "Cyan": "#06B6D4",
        "Teal": "#14B8A6",
        "Cosmic Purple": "#8B5CF6",
        "Emerald": "#10B981",
        "Amber": "#F59E0B",
        "Plasma Blue": "#3B82F6",
        "Rose": "#F43F5E"
    }

    @classmethod
    def apply_theme(cls, theme_name, accent_color=None):
        """Updates class tokens to the selected theme preset and accent."""
        if theme_name in cls.THEMES:
            cls.CURRENT_THEME_NAME = theme_name
            cfg = cls.THEMES[theme_name]
            for key, val in cfg.items():
                setattr(cls, key, val)

        if accent_color:
            cls.CYAN = accent_color
            cls.BORDER_GLOW = accent_color
