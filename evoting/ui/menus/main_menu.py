"""
Main menu - entry point for the application.
"""

from ..console import (
    clear_screen, header, subheader, error, success, warning, info,
    menu_item, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, BRIGHT_CYAN, BRIGHT_WHITE, THEME_PRIMARY,
    THEME_ACCENT, THEME_ADMIN, THEME_VOTER, THEME_LOGIN
)
from ..input_handler import masked_input


class MainMenu:
    """Handles the main application menu and authentication."""
    
    def __init__(self, auth_service, voter_views, admin_menu, voter_menu):
        self.auth_service = auth_service
        self.voter_views = voter_views
        self.admin_menu = admin_menu
        self.voter_menu = voter_menu
    
    def display(self):
        """Display the main menu and handle navigation."""
        while True:
            clear_screen()
            header("E-VOTING SYSTEM", THEME_LOGIN)
            print()
            menu_item(1, "Login as Admin", THEME_LOGIN)
            menu_item(2, "Login as Voter", THEME_LOGIN)
            menu_item(3, "Register as Voter", THEME_LOGIN)
            menu_item(4, "Exit", THEME_LOGIN)
            print()
            choice = prompt("Enter choice: ")
            
            if choice == "1":
                self.admin_login()
            elif choice == "2":
                self.voter_login()
            elif choice == "3":
                self.voter_views.register_voter()
            elif choice == "4":
                print()
                info("Goodbye!")
                self.auth_service.data_store.save()
                exit()
            else:
                error("Invalid choice.")
                pause()
    
    def admin_login(self):
        """Handle administrator login."""
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()
        
        success_result, user_or_error = self.auth_service.login_admin(username, password)
        
        if success_result:
            print()
            success(f"Welcome, {user_or_error['full_name']}!")
            pause()
            self.admin_menu.display(user_or_error)
        else:
            print()
            error(user_or_error)
            pause()
    
    def voter_login(self):
        """Handle voter login."""
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()
        
        success_result, user_or_error = self.auth_service.login_voter(voter_card, password)
        
        if success_result:
            print()
            success(f"Welcome, {user_or_error['full_name']}!")
            pause()
            self.voter_menu.display(user_or_error)
        else:
            print()
            if user_or_error == "not_verified":
                warning("Your voter registration has not been verified yet.")
                info("Please contact an admin to verify your registration.")
            else:
                error(user_or_error)
            pause()
