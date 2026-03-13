"""
Admin views - display logic for admin management and audit.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, GREEN, YELLOW, RED,
    THEME_ADMIN, THEME_ADMIN_ACCENT, BRIGHT_YELLOW
)
from ..input_handler import masked_input
from ...config import ADMIN_ROLES, MIN_PASSWORD_LENGTH


class AdminViews:
    """Handles admin management UI rendering."""
    
    def __init__(self, admin_service, data_store):
        self.admin_service = admin_service
        self.data_store = data_store
    
    def create_admin(self, current_user):
        """Display create admin form."""
        clear_screen()
        header("CREATE NEW ADMINISTRATOR", THEME_ADMIN)
        print()
        
        username = prompt("Username: ")
        if not username:
            error("Username cannot be empty.")
            pause()
            return
        
        # Check duplicate
        for admin in self.data_store.get_all_admins().values():
            if admin["username"].lower() == username.lower():
                error("Username already exists.")
                pause()
                return
        
        full_name = prompt("Full Name: ")
        email = prompt("Email: ")
        phone = prompt("Phone: ")
        
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        for i, role in enumerate(ADMIN_ROLES, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {role}")
        
        try:
            role_choice = int(prompt("\nSelect role: "))
            if role_choice < 1 or role_choice > len(ADMIN_ROLES):
                error("Invalid role selection.")
                pause()
                return
            role = ADMIN_ROLES[role_choice - 1]
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        password = masked_input("Password: ").strip()
        if len(password) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            pause()
            return
        
        confirm = masked_input("Confirm Password: ").strip()
        if password != confirm:
            error("Passwords do not match.")
            pause()
            return
        
        success_flag, result = self.admin_service.create_admin(
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            role=role,
            password=password,
            created_by=current_user["username"]
        )
        
        if success_flag:
            print()
            success(f"Administrator '{username}' created with role '{role}'!")
            self.data_store.save()
        else:
            error(result)
        pause()
    
    def view_all_admins(self):
        """Display all administrators."""
        clear_screen()
        header("ALL ADMINISTRATORS", THEME_ADMIN)
        admins = self.data_store.get_all_admins()
        
        if not admins:
            print()
            info("No administrators found.")
            pause()
            return
        
        print()
        table_header(
            f"{'ID':<5} {'Username':<15} {'Full Name':<25} {'Role':<20} {'Status':<10}",
            THEME_ADMIN
        )
        table_divider(75, THEME_ADMIN)
        
        for admin_id, admin in admins.items():
            status = status_badge("Active", True) if admin["is_active"] else status_badge("Inactive", False)
            print(f"  {admin['id']:<5} {admin['username']:<15} {admin['full_name']:<25} {admin['role']:<20} {status}")
        
        print(f"\n  {DIM}Total Administrators: {len(admins)}{RESET}")
        pause()
    
    def deactivate_admin(self, current_user):
        """Display admin deactivation interface."""
        clear_screen()
        header("DEACTIVATE ADMINISTRATOR", THEME_ADMIN)
        admins = self.data_store.get_all_admins()
        
        if not admins:
            print()
            info("No administrators found.")
            pause()
            return
        
        print()
        for admin_id, admin in admins.items():
            status = status_badge("Active", True) if admin["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{admin['id']}.{RESET} {admin['username']} {DIM}({admin['role']}){RESET} {status}")
        
        try:
            admin_id = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if admin_id not in admins:
            error("Admin not found.")
            pause()
            return
        
        if admins[admin_id]["username"] == current_user["username"]:
            error("Cannot deactivate yourself.")
            pause()
            return
        
        if admins[admin_id]["username"] == "admin":
            error("Cannot deactivate the super admin.")
            pause()
            return
        
        if prompt(f"Deactivate '{admins[admin_id]['username']}'? (yes/no): ").lower() == "yes":
            success_flag, err = self.admin_service.deactivate_admin(
                admin_id, current_user["username"]
            )
            if success_flag:
                print()
                success("Administrator deactivated.")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def view_audit_log(self):
        """Display audit log."""
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        
        audit_log = self.data_store.get_audit_log()
        
        if not audit_log:
            print()
            info("No audit entries.")
            pause()
            return
        
        subheader("Filter Options", THEME_ADMIN_ACCENT)
        menu_item(1, "View all (last 50)", THEME_ADMIN)
        menu_item(2, "Filter by action type", THEME_ADMIN)
        menu_item(3, "Filter by user", THEME_ADMIN)
        
        choice = prompt("\nChoice: ")
        
        if choice == "1":
            entries = audit_log[-50:]
        elif choice == "2":
            action_type = prompt("Enter action type (e.g. LOGIN, CREATE_CANDIDATE): ").upper()
            entries = [e for e in audit_log if action_type in e.get("action", "")][-50:]
        elif choice == "3":
            username = prompt("Enter username: ")
            entries = [e for e in audit_log if username.lower() in e.get("user", "").lower()][-50:]
        else:
            entries = audit_log[-50:]
        
        if not entries:
            print()
            info("No matching entries.")
            pause()
            return
        
        print()
        table_header(
            f"{'Timestamp':<20} {'Action':<25} {'User':<15} {'Details':<30}",
            THEME_ADMIN
        )
        table_divider(90, THEME_ADMIN)
        
        for entry in reversed(entries):
            ts = entry.get("timestamp", "")[:19]
            action = entry.get("action", "")[:24]
            user = entry.get("user", "")[:14]
            details = entry.get("details", "")[:29]
            print(f"  {ts:<20} {action:<25} {user:<15} {details:<30}")
        
        print(f"\n  {DIM}Showing {len(entries)} entries{RESET}")
        pause()
    
    def export_data(self):
        """Display data export options."""
        clear_screen()
        header("EXPORT DATA", THEME_ADMIN)
        
        subheader("Export Options", THEME_ADMIN_ACCENT)
        menu_item(1, "Export all data (JSON)", THEME_ADMIN)
        menu_item(2, "Export voters only", THEME_ADMIN)
        menu_item(3, "Export poll results", THEME_ADMIN)
        menu_item(4, "Export audit log", THEME_ADMIN)
        
        choice = prompt("\nChoice: ")
        
        import json
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if choice == "1":
            filename = f"evoting_export_full_{timestamp}.json"
            data = {
                "candidates": self.data_store.get_all_candidates(),
                "voters": self.data_store.get_all_voters(),
                "polls": self.data_store.get_all_polls(),
                "stations": self.data_store.get_all_stations(),
                "votes": self.data_store.get_all_votes(),
                "audit_log": self.data_store.get_audit_log()
            }
        elif choice == "2":
            filename = f"evoting_export_voters_{timestamp}.json"
            voters = self.data_store.get_all_voters()
            # Remove sensitive info
            data = {}
            for voter_id, voter in voters.items():
                data[voter_id] = {k: voter[k] for k in voter if k != "password_hash"}
        elif choice == "3":
            filename = f"evoting_export_results_{timestamp}.json"
            data = {
                "polls": self.data_store.get_all_polls(),
                "votes": self.data_store.get_all_votes(),
                "candidates": self.data_store.get_all_candidates()
            }
        elif choice == "4":
            filename = f"evoting_export_audit_{timestamp}.json"
            data = {"audit_log": self.data_store.get_audit_log()}
        else:
            error("Invalid choice.")
            pause()
            return
        
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print()
            success(f"Data exported to: {BRIGHT_YELLOW}{filename}{RESET}")
        except Exception as e:
            error(f"Export failed: {e}")
        
        pause()
