"""
Authentication service - handles login and session management.
"""

from ..validators import hash_password


class AuthService:
    """Handles authentication and session management."""
    
    def __init__(self, data_store):
        self.data_store = data_store
        self.current_user = None
        self.current_role = None
    
    def login_admin(self, username: str, password: str) -> tuple:
        """
        Attempt admin login.
        Returns (success, user_dict or error_message).
        """
        hashed = hash_password(password)
        
        for aid, admin in self.data_store.get_all_admins().items():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    self.data_store.log_action("LOGIN_FAILED", username, "Account deactivated")
                    return False, "This account has been deactivated."
                
                self.current_user = admin
                self.current_role = "admin"
                self.data_store.log_action("LOGIN", username, "Admin login successful")
                return True, admin
        
        self.data_store.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
        return False, "Invalid credentials."
    
    def login_voter(self, voter_card: str, password: str) -> tuple:
        """
        Attempt voter login.
        Returns (success, user_dict or error_message).
        """
        hashed = hash_password(password)
        
        for vid, voter in self.data_store.get_all_voters().items():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    self.data_store.log_action("LOGIN_FAILED", voter_card, "Voter account deactivated")
                    return False, "This voter account has been deactivated."
                
                if not voter["is_verified"]:
                    self.data_store.log_action("LOGIN_FAILED", voter_card, "Voter not verified")
                    return False, "not_verified"
                
                self.current_user = voter
                self.current_role = "voter"
                self.data_store.log_action("LOGIN", voter_card, "Voter login successful")
                return True, voter
        
        self.data_store.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        return False, "Invalid voter card number or password."
    
    def logout(self):
        """Logout current user."""
        if self.current_user:
            if self.current_role == "admin":
                self.data_store.log_action("LOGOUT", self.current_user["username"], "Admin logged out")
            else:
                self.data_store.log_action("LOGOUT", self.current_user["voter_card_number"], "Voter logged out")
        
        self.current_user = None
        self.current_role = None
    
    def get_current_user(self) -> dict:
        """Get the current logged in user."""
        return self.current_user
    
    def get_current_role(self) -> str:
        """Get the current user's role."""
        return self.current_role
    
    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self.current_user is not None
    
    def refresh_current_user(self):
        """Refresh current user data from store."""
        if self.current_user and self.current_role == "voter":
            for vid, voter in self.data_store.get_all_voters().items():
                if voter["id"] == self.current_user["id"]:
                    self.current_user = voter
                    break
    

