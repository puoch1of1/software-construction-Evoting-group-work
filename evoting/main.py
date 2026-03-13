"""
National E-Voting System - Main Entry Point

A comprehensive console-based electronic voting system that supports:
- Candidate registration and management
- Voter registration and verification
- Multiple polling stations
- Multiple positions/offices
- Secure ballot casting
- Real-time results and statistics
- Complete audit trail

"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path for proper imports
evoting_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(evoting_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from evoting.repositories.data_store import DataStore
from evoting.services import (
    AuthService, CandidateService, StationService, PositionService,
    PollService, VoterService, AdminService, VotingService,
    StatisticsService, AuditService
)
from evoting.ui.views import (
    CandidateViews, VoterViews, StationViews, PositionViews,
    PollViews, ResultsViews, AdminViews
)
from evoting.ui.menus import MainMenu, AdminMenu, VoterMenu


def initialize_application():
    """
    Initialize all components with dependency injection.
    Returns the main menu ready to display.
    """
    # Initialize the data store (repository layer)
    data_store = DataStore()
    
    # Initialize services (business logic layer)
    auth_service = AuthService(data_store)
    candidate_service = CandidateService(data_store)
    station_service = StationService(data_store)
    position_service = PositionService(data_store)
    poll_service = PollService(data_store)
    voter_service = VoterService(data_store)
    admin_service = AdminService(data_store)
    voting_service = VotingService(data_store)
    statistics_service = StatisticsService(data_store)
    audit_service = AuditService(data_store)
    
    # Initialize views (presentation layer - display logic)
    candidate_views = CandidateViews(candidate_service, data_store)
    voter_views = VoterViews(voter_service, station_service, data_store)
    station_views = StationViews(station_service, data_store)
    position_views = PositionViews(position_service, data_store)
    poll_views = PollViews(
        poll_service, position_service, station_service,
        candidate_service, data_store
    )
    results_views = ResultsViews(statistics_service, data_store)
    admin_views = AdminViews(admin_service, data_store)
    
    # Initialize menus (navigation layer)
    admin_menu = AdminMenu(
        data_store, candidate_views, voter_views, station_views,
        position_views, poll_views, results_views, admin_views
    )
    
    voter_menu = VoterMenu(
        data_store, voter_service, voting_service,
        voter_views, poll_views
    )
    
    main_menu = MainMenu(auth_service, voter_views, admin_menu, voter_menu)
    
    return main_menu


def main():
    """Application entry point."""
    try:
        main_menu = initialize_application()
        main_menu.display()
    except KeyboardInterrupt:
        print("\n\n  Exiting... Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n  A critical error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
