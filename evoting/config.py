"""
Configuration constants for the E-Voting System.
Contains all magic numbers and constant values extracted from the monolith.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(_PACKAGE_DIR)

# Data file path - stored in workspace root
DATA_FILE_PATH = os.path.join(WORKSPACE_DIR, "evoting_data.json")

# ---------------------------------------------------------------------------
# Age constraints
# ---------------------------------------------------------------------------
MIN_VOTER_AGE = 18
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75

# ---------------------------------------------------------------------------
# Voter card
# ---------------------------------------------------------------------------
VOTER_CARD_LENGTH = 12

# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------
MIN_PASSWORD_LENGTH = 6

# ---------------------------------------------------------------------------
# Default system administrator credentials
# ---------------------------------------------------------------------------
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_EMAIL = "admin@evote.com"

# ---------------------------------------------------------------------------
# Admin roles
# ---------------------------------------------------------------------------
ADMIN_ROLES = [
    "super_admin",
    "election_officer",
    "station_manager",
    "auditor"
]

# ---------------------------------------------------------------------------
# Gender options
# ---------------------------------------------------------------------------
VALID_GENDERS = ["M", "F", "OTHER"]

# ---------------------------------------------------------------------------
# Education levels required for candidates
# ---------------------------------------------------------------------------
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate"
]

# ---------------------------------------------------------------------------
# Valid position and election types
# ---------------------------------------------------------------------------
POSITION_LEVELS = ["national", "regional", "local"]
ELECTION_TYPES = ["General", "Primary", "By-election", "Referendum"]

# ---------------------------------------------------------------------------
# Station / position capacity guards
# ---------------------------------------------------------------------------
MIN_STATION_CAPACITY = 1
MIN_POSITION_SEATS = 1

# ---------------------------------------------------------------------------
# Position defaults
# ---------------------------------------------------------------------------
DEFAULT_POSITION_SEATS = 1
DEFAULT_TERM_LENGTH_YEARS = 5

# ---------------------------------------------------------------------------
# Voting
# ---------------------------------------------------------------------------
VOTE_HASH_LENGTH = 16   # characters of SHA-256 hash shown on receipt

# ---------------------------------------------------------------------------
# UI display
# ---------------------------------------------------------------------------
HEADER_WIDTH = 58       # character width of header/footer borders

# ---------------------------------------------------------------------------
# Voter age-group boundaries used in statistics reports.
# Each tuple is (lower_inclusive, upper_inclusive, label).
# The catch-all "65+" bucket is handled separately in statistics_service.
# ---------------------------------------------------------------------------
AGE_GROUPS = [
    (18, 25, "18-25"),
    (26, 35, "26-35"),
    (36, 45, "36-45"),
    (46, 55, "46-55"),
    (56, 65, "56-65"),
]
AGE_GROUP_OVERFLOW_LABEL = "65+"
