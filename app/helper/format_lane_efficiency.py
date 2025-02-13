import re

def format_lane_efficiency(eff) -> str:
    try:
        cleaned = re.sub(r'[^\d\.]', '', str(eff))
        eff_float = float(cleaned)
        return f"{eff_float:.2f}%"
    except (TypeError, ValueError):
        return "-"
