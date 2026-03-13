"""
UI package - handles all presentation layer components.
"""

from .colors import *
from .console import (
    colored, clear_screen, pause, header, subheader,
    table_header, table_divider, error, success, warning,
    info, menu_item, status_badge, prompt
)
from .input_handler import masked_input
from .views import (
    CandidateViews, VoterViews, StationViews, PositionViews,
    PollViews, ResultsViews, AdminViews
)
from .menus import MainMenu, AdminMenu, VoterMenu
