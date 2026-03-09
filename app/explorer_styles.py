"""
Color palette, CSS, and chart defaults for the SQL Explorer.
Copied from V1 styling (sql_explorer_utils/styling.py) for visual consistency.
"""

# ---------------------------------------------------------------------------
# Color palette (matches V1 exactly)
# ---------------------------------------------------------------------------
PRIMARY_TEXT = "#1E293B"
SECONDARY_TEXT = "#475569"
MUTED_TEXT = "#94A3B8"
ACCENT = "#0891B2"
ACCENT_DARK = "#0E7490"
SURFACE = "#F8FAFC"
BORDER = "#E2E8F0"
WHITE = "#FFFFFF"

BOROUGH_COLORS: dict[str, str] = {
    "Manhattan": "#2563EB",
    "Brooklyn": "#059669",
    "Queens": "#D97706",
    "Bronx": "#E11D48",
    "Staten Island": "#7C3AED",
    "EWR": "#6B7280",
}

COMPANY_COLORS: dict[str, str] = {
    "Uber": "#18181B",
    "Lyft": "#DB2777",
    "Via": "#16A34A",
}

LICENSE_TO_COMPANY: dict[str, str] = {
    "HV0003": "Uber",
    "HV0004": "Via",
    "HV0005": "Lyft",
}

# Reverse mapping for filters: friendly name -> license code
COMPANY_CODES: dict[str, str] = {v: k for k, v in LICENSE_TO_COMPANY.items()}

# ---------------------------------------------------------------------------
# Plotly chart defaults (matches V1 exactly)
# ---------------------------------------------------------------------------
CHART_MARGIN = dict(l=50, r=20, t=30, b=40)
CHART_FONT = dict(family="Inter, system-ui, sans-serif", size=12, color=SECONDARY_TEXT)

PLOTLY_LAYOUT_DEFAULTS = dict(
    font=CHART_FONT,
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    margin=CHART_MARGIN,
    hovermode="x unified",
)

# ---------------------------------------------------------------------------
# Custom CSS — V1 styling with V2 additions (scrollable radio, sidebar rules)
# ---------------------------------------------------------------------------
APP_CSS = """
<style>
/* Main container — keep horizontal padding compact, preserve default top for tab visibility */
.block-container {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 1rem;
}

/* Sidebar — reduce top padding so "SQL Explorer" aligns with the tab bar */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.75rem;
}

/* Headers — prevent any truncation / ellipsis */
h1, h2, h3, h4 {
    color: #1E293B;
    font-weight: 700;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    text-wrap: wrap !important;
    max-width: 100% !important;
}
h1 {
    margin-bottom: 0.25rem;
}

/* Hide the anchor link icon next to markdown headings */
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {
    display: none !important;
}

/* Also target Streamlit's own title/header elements */
[data-testid="stTitle"], [data-testid="stHeader"] {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}

/* Metric cards — light bordered boxes, compact */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.3rem 0.5rem;
    text-align: center;
}
[data-testid="stMetricValue"] {
    font-size: 1.05rem;
    font-weight: 400;
    color: #1E293B;
    justify-content: center;
}
[data-testid="stMetricLabel"] {
    font-size: 0.6rem;
    color: #94A3B8;
    justify-content: center;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Active tab underline — override subtle slate with visible coral */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #FF4B4B !important;
}

/* SQL code blocks */
.stCodeBlock {
    border: 1px solid #E2E8F0;
    border-radius: 6px;
}

/* Sidebar refinements */
section[data-testid="stSidebar"] {
    background: #F8FAFC;
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] h1 {
    font-size: 1.25rem;
    color: #0891B2;
    margin-bottom: 0;
}
section[data-testid="stSidebar"] .stCaption {
    margin-bottom: 0.05rem;
}

/* Pills — unselected: near-white with light border */
[data-testid="stPills"] button[kind="pills"] {
    font-size: 0.8rem !important;
    padding: 0.15rem 0.5rem !important;
    border-radius: 16px !important;
    background-color: #F8FAFC !important;
    color: #94A3B8 !important;
    border: 1px solid #E2E8F0 !important;
}
/* Pills — selected (active): dark gray with white text */
[data-testid="stPills"] button[kind="pillsActive"],
[data-testid="stPills"] button[kind="pills"][aria-checked="true"] {
    background-color: #64748B !important;
    color: #FFFFFF !important;
    border: 1px solid #64748B !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    font-size: 0.85rem;
    color: #0891B2;
    font-weight: 600;
}

/* Divider */
hr {
    margin: 0.75rem 0;
    border-color: #E2E8F0;
}

/* Info/warning banners */
.stAlert {
    border-radius: 8px;
}

/* Subtle sidebar multiselect pills (More Filters section) */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: #F1F5F9 !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] span[role="presentation"] {
    color: #94A3B8 !important;
}

/* Primary button styling — force teal over gray theme primary */
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {
    background-color: #0891B2 !important;
    border-color: #0891B2 !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
    background-color: #0E7490 !important;
    border-color: #0E7490 !important;
}

/* Date input / selectbox accent — keep teal for focus rings */
[data-testid="stDateInput"] input:focus,
[data-testid="stSelectbox"] [data-baseweb="select"] [aria-expanded="true"] {
    border-color: #0891B2 !important;
}

/* ----- V2 additions ----- */

/* Scrollable query selector container (Pre-Built Queries tab) */
.query-selector [data-testid="stRadio"] > div {
    max-height: 280px;
    overflow-y: auto;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.5rem;
}

/* Thin sidebar rules between blocks */
.sidebar-rule {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 0.5rem 0;
}
</style>
"""


def get_app_css() -> str:
    """Return the full CSS block for the SQL Explorer app."""
    return APP_CSS


def inject_global_css():
    """Inject all custom CSS styles into the Streamlit page."""
    import streamlit as st

    st.markdown(
        """
    <style>

    /* ── Hide Streamlit default chrome ── */
    #MainMenu        { visibility: hidden; }
    footer           { visibility: hidden; }
    header           { visibility: hidden; }
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }

    /* ── Page background ── */
    body, .stApp {
        background-color: #F9FAFB;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* ── Block container padding ── */
    .block-container {
        background-color: #FFFFFF;
        padding-top:    0rem;
        padding-bottom: 1rem;
        padding-left:   2rem;
        padding-right:  2rem;
        max-width:      100%;
    }

    /* ── Tab bar ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #E5E7EB;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size:   13px;
        font-weight: 500;
        padding:     10px 18px;
        color:       #6B7280;
        background:  transparent;
        border:      none;
    }
    .stTabs [aria-selected="true"] {
        color:         __ACCENT__ !important;
        border-bottom: 2px solid __ACCENT__ !important;
        background:    transparent;
    }

    /* ── Expander label ── */
    .streamlit-expanderHeader {
        font-size:      12px;
        color:          #6B7280;
        font-weight:    500;
        letter-spacing: 0.02em;
    }

    /* ── Selectbox input text ── */
    .stSelectbox > div {
        font-size: 13px;
    }

    /* ── Primary button (Run Query, Export CSV) ── */
    .stButton > button {
        background:    __ACCENT__;
        color:         white;
        border:        none;
        border-radius: 6px;
        font-size:     13px;
        font-weight:   500;
        padding:       6px 16px;
    }
    .stButton > button:hover {
        background: #0F766E;
    }
    .stButton > button[kind="secondary"] {
        background:    transparent !important;
        color:         #9CA3AF !important;
        border:        none !important;
        font-size:     11px !important;
        font-weight:   400 !important;
        padding:       4px 8px !important;
    }
    .stButton > button[kind="secondary"]:hover {
        color:         #374151 !important;
        background:    transparent !important;
    }

    /* ── Radio label text ── */

    [data-testid="stRadio"] p {
        font-size: 13px !important;
        color: #374151 !important;
    }

    /* ── Hide sidebar entirely ── */
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    /* ── Section 1: Header bar (dark) ── */
    .v3-header-bar {
        background: __SURFACE__;
        margin: -0.5rem -2rem 0 -2rem;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .v3-title {
        color: #0891B2 !important;
        font-size: 26px !important;        /* was 22px */
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }
    .v3-subtitle {
        color: #1E293B !important;
        font-size: 17px !important;
        font-weight: 400 !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }
    .v3-info {
        color: #1E293B !important;
        font-size: 11px !important;
        font-weight: 400 !important;
        text-align: left; !important;
        margin: 0; !important;
        line-height: 1.7 !important;
        font-style: italic !important;
    }

    /* ── Section 2: Filter bar (white strip) ── */
    .v3-filter-bar {
        background: #FFFFFF;
        margin: 0 -2rem;
        padding: 16px 2rem 0 2rem;
        border-bottom: none;
    }
    .v3-filter-label {
        font-size: 10px;
        font-weight: 600;
        color: #9CA3AF;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0;
    }

    /* Style the st.container that holds filter widgets */
    .v3-filter-bar + div > [data-testid="stVerticalBlock"] {
        background: #FFFFFF;
        margin: 0 -2rem;
        padding: 0 2rem 16px 2rem;
        border-bottom: 1px solid #E5E7EB;
    }

    /* ── Section 3: Data area (gray bg, breathing room) ── */
    .v3-data-area {
        padding-top: 1.5rem;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: __SURFACE__;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.3rem 0.5rem;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.05rem;
        font-weight: 400;
        color: #1E293B;
        justify-content: center;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem;
        color: #94A3B8;
        justify-content: center;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── SQL code blocks ── */
    .stCodeBlock {
        border: 1px solid #E5E7EB;
        border-radius: 6px;
    }

    /* ── Compact selectbox height ── */
    .stSelectbox > div[data-baseweb="select"] {
        min-height: 36px;
    }

    /* ── Selectbox font size ── */
    .stSelectbox [data-baseweb="select"] span {
        font-size: 13px;
        color: #374151;
    }

    /* ── Dividers ── */
    hr {
        margin-top:    0.5rem;
        margin-bottom: 0.5rem;
        border-color:  #E5E7EB;
    }


    /* ── Compact label text above each filter ── */
    .stSelectbox label,
    .stDateInput label {
        font-size:      11px;
        font-weight:    600;
        color:          #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Filter dropdowns — light gray fill ── */
    [data-testid="stSelectbox"] > div > div {
        background-color: __SURFACE__ !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── Date input — light gray fill ── */
    [data-testid="stDateInput"] input {
        background-color: __SURFACE__ !important;
        border: 1px solid #E2E8F0 !important;
    }


    </style>
    """.replace("__ACCENT__", ACCENT).replace("__SURFACE__", SURFACE),
        unsafe_allow_html=True,
    )
