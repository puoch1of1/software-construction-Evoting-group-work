"""
Admin service - handles admin management.
"""

import datetime
from ..validators import hash_password


class AdminService:
    """Handles admin management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def create_admin(
        self,
        username: str,
        password: str,
        full_name: str,
        email: str,
        role: str,
        created_by: str
    ) -> tuple:
        """
        Create admin new admin.
        Returns (success, admin_id or error_message).
        """
        # Check for duplicate username
        for admin_id, admin in self.data_store.get_all_admins().items():
            if admin["username"] == username:
                return False, "Username already exists."
        
        admin_id = self.data_store.get_next_admin_id()
        
        admin_data = {
            "id": admin_id,
            "username": username,
            "password": hash_password(password),
            "full_name": full_name,
            "email": email,
            "role": role,
            "created_at": str(datetime.datetime.now()),
            "is_active": True
        }
        
        self.data_store.add_admin(admin_data)
        self.data_store.log_action(
            "CREATE_ADMIN",
            created_by,
            f"Created admin: {username} (Role: {role})"
        )
        
        return True, admin_id
    
    def deactivate_admin(
        self,
        admin_id: int,
        current_admin_id: int,
        deactivated_by: str
    ) -> tuple:
        """
        Deactivate an admin.
        Returns (success, error_message or None).
        """
        admin = self.data_store.get_admin(admin_id)
        if not admin:
            return False, "Admin not found."
        
        if admin_id == current_admin_id:
            return False, "Cannot deactivate your own account."
        
        admin["is_active"] = False
        self.data_store.update_admin(admin_id, admin)
        self.data_store.log_action(
            "DEACTIVATE_ADMIN",
            deactivated_by,
            f"Deactivated admin: {admin['username']}"
        )
        
        return True, None
    
    def get_admin(self, admin_id: int) -> dict:
        """Get an admin by ID."""
        return self.data_store.get_admin(admin_id)
    
    def get_all_admins(self) -> dict:
        """Get all admins."""
        return self.data_store.get_all_admins()
