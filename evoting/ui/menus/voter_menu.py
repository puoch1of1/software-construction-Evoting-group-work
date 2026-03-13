"""
Voter menu - handle voter dashboard and navigation.
"""

from ..console import (
    clear_screen, header, error, warning,
    menu_item, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, THEME_VOTER
)


class VoterMenu:
    """Handles voter navigation and menu system."""
    
    def __init__(self, data_store, voter_service, voting_service,
                 voter_views, poll_views):
        self.data_store = data_store
        self.voter_service = voter_service
        self.voting_service = voting_service
        self.voter_views = voter_views
        self.poll_views = poll_views
    
    def display(self, current_user):
        """Display the voter dashboard menu."""
        while True:
            # Refresh user data
            voter = self.data_store.get_voter(current_user["id"])
            if voter:
                current_user = voter
            
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            station_name = self.data_store.get_station(current_user.get("station_id", 0))
            station_name = station_name.get("name", "Unknown") if station_name else "Unknown"
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}")
            print(f"  {DIM}    Card: {current_user['voter_card_number']}  │  Station: {station_name}{RESET}")
            print()
            menu_item(1, "View Open Polls", THEME_VOTER)
            menu_item(2, "Cast Vote", THEME_VOTER)
            menu_item(3, "View My Voting History", THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
            menu_item(5, "View My Profile", THEME_VOTER)
            menu_item(6, "Change Password", THEME_VOTER)
            menu_item(7, "Logout", THEME_VOTER)
            print()
            choice = prompt("Enter choice: ")
            
            if choice == "1":
                self.poll_views.view_open_polls_voter(current_user)
            
            elif choice == "2":
                if not current_user.get("is_verified"):
                    warning("Your account must be verified before voting.")
                    pause()
                    continue
                self.poll_views.cast_vote(current_user, self.voting_service)
            
            elif choice == "3":
                self.poll_views.view_voting_history(current_user, self.voting_service)
            
            elif choice == "4":
                self.poll_views.view_closed_poll_results_voter()
            
            elif choice == "5":
                stations = self.data_store.get_all_stations()
                self.voter_views.view_profile(current_user, stations)
            
            elif choice == "6":
                self.voter_views.change_password(current_user, self.voter_service)
            
            elif choice == "7":
                self.data_store.log_action(
                    "LOGOUT", 
                    current_user.get("voter_card_number", str(current_user["id"])),
                    "Voter logged out"
                )
                self.data_store.save()
                break
            
            else:
                error("Invalid choice.")
                pause()
