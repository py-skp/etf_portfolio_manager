"""
Financial number formatting utilities.
Ensures consistent, professional formatting throughout the app.
"""

def fmt_currency(value, decimals=2, prefix="$"):
    """Format as currency: $1,234.56"""
    try:
        v = float(value)
        return f"{prefix}{v:,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"

def fmt_currency_short(value, prefix="$"):
    """Format large numbers with suffixes: $1.23B, $456.7M, $12.3K"""
    try:
        v = float(value)
        if abs(v) >= 1e12:
            return f"{prefix}{v/1e12:.2f}T"
        elif abs(v) >= 1e9:
            return f"{prefix}{v/1e9:.2f}B"
        elif abs(v) >= 1e6:
            return f"{prefix}{v/1e6:.2f}M"
        elif abs(v) >= 1e3:
            return f"{prefix}{v/1e3:.2f}K"
        else:
            return f"{prefix}{v:.2f}"
    except (TypeError, ValueError):
        return "N/A"

def fmt_pct(value, decimals=2, multiply=False):
    """Format as percentage: 12.34%"""
    try:
        v = float(value)
        if multiply:
            v = v * 100
        return f"{v:+.{decimals}f}%" if v != 0 else f"{v:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"

def fmt_pct_plain(value, decimals=2, multiply=False):
    """Format as percentage without leading + sign: 12.34%"""
    try:
        v = float(value)
        if multiply:
            v = v * 100
        return f"{v:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"

def fmt_number(value, decimals=2):
    """Format as a plain number with commas: 1,234,567.89"""
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"

def fmt_ratio(value, decimals=2):
    """Format as a ratio/multiple: 1.85x"""
    try:
        return f"{float(value):.{decimals}f}x"
    except (TypeError, ValueError):
        return "N/A"
