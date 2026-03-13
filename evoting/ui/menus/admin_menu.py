"""
Admin menu - handle admin dashboard and navigation.
"""

from ..console import (
    clear_screen, header, subheader, error, success, warning, info,
    menu_item, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, THEME_ADMIN, THEME_ADMIN_ACCENT, BRIGHT_CYAN
)


class AdminMenu:
    """Handles administrator navigation and menu system."""
    
    def __init__(self, data_store, candidate_views, voter_views, station_views,
                 position_views, poll_views, results_views, admin_views):
        self.data_store = data_store
        self.candidate_views = candidate_views
        self.voter_views = voter_views
        self.station_views = station_views
        self.position_views = position_views
        self.poll_views = poll_views
        self.results_views = results_views
        self.admin_views = admin_views
    
    def display(self, current_user):
        """Display the admin dashboard menu."""
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{current_user['full_name']}{RESET}  {DIM}│  Role: {current_user['role']}{RESET}")
            
            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1, "Create Candidate", THEME_ADMIN)
            menu_item(2, "View All Candidates", THEME_ADMIN)
            menu_item(3, "Update Candidate", THEME_ADMIN)
            menu_item(4, "Delete Candidate", THEME_ADMIN)
            menu_item(5, "Search Candidates", THEME_ADMIN)
            
            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6, "Create Voting Station", THEME_ADMIN)
            menu_item(7, "View All Stations", THEME_ADMIN)
            menu_item(8, "Update Station", THEME_ADMIN)
            menu_item(9, "Delete Station", THEME_ADMIN)
            
            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position", THEME_ADMIN)
            menu_item(11, "View Positions", THEME_ADMIN)
            menu_item(12, "Update Position", THEME_ADMIN)
            menu_item(13, "Delete Position", THEME_ADMIN)
            menu_item(14, "Create Poll", THEME_ADMIN)
            menu_item(15, "View All Polls", THEME_ADMIN)
            menu_item(16, "Update Poll", THEME_ADMIN)
            menu_item(17, "Delete Poll", THEME_ADMIN)
            menu_item(18, "Open/Close Poll", THEME_ADMIN)
            menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)
            
            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters", THEME_ADMIN)
            menu_item(21, "Verify Voter", THEME_ADMIN)
            menu_item(22, "Deactivate Voter", THEME_ADMIN)
            menu_item(23, "Search Voters", THEME_ADMIN)
            
            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account", THEME_ADMIN)
            menu_item(25, "View Admins", THEME_ADMIN)
            menu_item(26, "Deactivate Admin", THEME_ADMIN)
            
            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results", THEME_ADMIN)
            menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            menu_item(29, "View Audit Log", THEME_ADMIN)
            menu_item(30, "Station-wise Results", THEME_ADMIN)
            
            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data", THEME_ADMIN)
            menu_item(32, "Logout", THEME_ADMIN)
            print()
            choice = prompt("Enter choice: ")
            
            # Candidate Management
            if choice == "1":
                self.candidate_views.create_candidate(current_user)
            elif choice == "2":
                self.candidate_views.view_all_candidates()
            elif choice == "3":
                self.candidate_views.update_candidate(current_user)
            elif choice == "4":
                self.candidate_views.delete_candidate(current_user)
            elif choice == "5":
                self.candidate_views.search_candidates()
            
            # Station Management
            elif choice == "6":
                self.station_views.create_station(current_user)
            elif choice == "7":
                self.station_views.view_all_stations()
            elif choice == "8":
                self.station_views.update_station(current_user)
            elif choice == "9":
                self.station_views.delete_station(current_user)
            
            # Position Management
            elif choice == "10":
                self.position_views.create_position(current_user)
            elif choice == "11":
                self.position_views.view_all_positions()
            elif choice == "12":
                self.position_views.update_position(current_user)
            elif choice == "13":
                self.position_views.delete_position(current_user)
            
            # Poll Management
            elif choice == "14":
                self.poll_views.create_poll(current_user)
            elif choice == "15":
                self.poll_views.view_all_polls()
            elif choice == "16":
                self.poll_views.update_poll(current_user)
            elif choice == "17":
                self.poll_views.delete_poll(current_user)
            elif choice == "18":
                self.poll_views.open_close_poll(current_user)
            elif choice == "19":
                self.poll_views.assign_candidates_to_poll(current_user)
            
            # Voter Management
            elif choice == "20":
                self.voter_views.view_all_voters()
            elif choice == "21":
                self.voter_views.verify_voter(current_user)
            elif choice == "22":
                self.voter_views.deactivate_voter(current_user)
            elif choice == "23":
                self.voter_views.search_voters()
            
            # Admin Management
            elif choice == "24":
                self.admin_views.create_admin(current_user)
            elif choice == "25":
                self.admin_views.view_all_admins()
            elif choice == "26":
                self.admin_views.deactivate_admin(current_user)
            
            # Results & Reports
            elif choice == "27":
                self.results_views.view_poll_results()
            elif choice == "28":
                self.results_views.view_system_statistics()
            elif choice == "29":
                self.admin_views.view_audit_log()
            elif choice == "30":
                self.results_views.view_results_by_station()
            
            # System
            elif choice == "31":
                self.data_store.save()
                pause()
            elif choice == "32":
                self.data_store.log_action("LOGOUT", current_user["username"], "Admin logged out")
                self.data_store.save()
                break
            else:
                error("Invalid choice.")
                pause()
