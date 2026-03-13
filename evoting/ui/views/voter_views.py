"""
Voter views - display logic for voter-related screens.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER,
    BRIGHT_BLUE, BRIGHT_YELLOW
)
from ..input_handler import masked_input
from ...config import MIN_VOTER_AGE, MIN_PASSWORD_LENGTH
from ...validators import validate_date, calculate_age, validate_password


class VoterViews:
    """Handles voter-related UI rendering."""
    
    def __init__(self, voter_service, station_service, data_store):
        self.voter_service = voter_service
        self.station_service = station_service
        self.data_store = data_store
    
    def register_voter(self):
        """Display voter registration form."""
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()
        
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return
        
        national_id = prompt("National ID Number: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return
        
        # Check duplicate
        for voter_id, voter in self.data_store.get_all_voters().items():
            if voter["national_id"] == national_id:
                error("A voter with this National ID already exists.")
                pause()
                return
        
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        valid, result = validate_date(dob_str)
        if not valid:
            error("Invalid date format.")
            pause()
            return
        age = calculate_age(result)
        
        if age < MIN_VOTER_AGE:
            error(f"You must be at least {MIN_VOTER_AGE} years old to register.")
            pause()
            return
        
        gender = prompt("Gender (M/F/Other): ").upper()
        if gender not in ["M", "F", "OTHER"]:
            error("Invalid gender selection.")
            pause()
            return
        
        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")
        
        password = masked_input("Create Password: ").strip()
        if len(password) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            pause()
            return
        
        confirm_password = masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            error("Passwords do not match.")
            pause()
            return
        
        stations = self.station_service.get_all_stations()
        if not stations:
            error("No voting stations available. Contact admin.")
            pause()
            return
        
        subheader("Available Voting Stations", THEME_VOTER)
        for sid, station in stations.items():
            if station["is_active"]:
                print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
        
        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
            if station_choice not in stations or not stations[station_choice]["is_active"]:
                error("Invalid station selection.")
                pause()
                return
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        success_flag, result = self.voter_service.register_voter(
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            address=address,
            phone=phone,
            email=email,
            password=password,
            station_id=station_choice
        )
        
        if success_flag:
            print()
            success("Registration successful!")
            print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{result}{RESET}")
            warning("IMPORTANT: Save this number! You need it to login.")
            info("Your registration is pending admin verification.")
            self.data_store.save()
        else:
            error(result)
        
        pause()
    
    def view_all_voters(self):
        """Display all voters in a table."""
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        voters = self.data_store.get_all_voters()
        
        if not voters:
            print()
            info("No voters registered.")
            pause()
            return
        
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN
        )
        table_divider(70, THEME_ADMIN)
        
        for voter_id, voter in voters.items():
            verified = status_badge("Yes", True) if voter["is_verified"] else status_badge("No", False)
            active = status_badge("Yes", True) if voter["is_active"] else status_badge("No", False)
            print(f"  {voter['id']:<5} {voter['full_name']:<25} {voter['voter_card_number']:<15} {voter['station_id']:<6} {verified:<19} {active}")
        
        verified_count = sum(1 for voter in voters.values() if voter["is_verified"])
        unverified_count = sum(1 for voter in voters.values() if not voter["is_verified"])
        print(f"\n  {DIM}Total: {len(voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        pause()
    
    def verify_voter(self, current_user):
        """Display voter verification interface."""
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        
        unverified = self.voter_service.get_unverified_voters()
        if not unverified:
            print()
            info("No unverified voters.")
            pause()
            return
        
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for voter_id, voter in unverified.items():
            print(f"  {THEME_ADMIN}{voter['id']}.{RESET} {voter['full_name']} {DIM}│ NID: {voter['national_id']} │ Card: {voter['voter_card_number']}{RESET}")
        
        print()
        menu_item(1, "Verify a single voter", THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        
        choice = prompt("\nChoice: ")
        
        if choice == "1":
            try:
                voter_id = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input.")
                pause()
                return
            
            success_flag, err = self.voter_service.verify_voter(
                voter_id, current_user["username"]
            )
            if success_flag:
                voter = self.data_store.get_voter(voter_id)
                print()
                success(f"Voter '{voter['full_name']}' verified!")
                self.data_store.save()
            else:
                error(err if err else "Voter not found or already verified.")
        
        elif choice == "2":
            count = self.voter_service.verify_all_pending(current_user["username"])
            print()
            success(f"{count} voters verified!")
            self.data_store.save()
        
        pause()
    
    def deactivate_voter(self, current_user):
        """Display voter deactivation interface."""
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        voters = self.data_store.get_all_voters()
        
        if not voters:
            print()
            info("No voters found.")
            pause()
            return
        
        print()
        try:
            voter_id = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if voter_id not in voters:
            error("Voter not found.")
            pause()
            return
        
        if not voters[voter_id]["is_active"]:
            info("Already deactivated.")
            pause()
            return
        
        if prompt(f"Deactivate '{voters[voter_id]['full_name']}'? (yes/no): ").lower() == "yes":
            success_flag, err = self.voter_service.deactivate_voter(
                voter_id, current_user["username"]
            )
            if success_flag:
                print()
                success("Voter deactivated.")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def search_voters(self):
        """Display voter search interface."""
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID", THEME_ADMIN)
        menu_item(4, "Station", THEME_ADMIN)
        
        choice = prompt("\nChoice: ")
        results = []
        
        if choice == "1":
            term = prompt("Name: ")
            results = self.voter_service.search_by_name(term)
        elif choice == "2":
            term = prompt("Card Number: ")
            results = self.voter_service.search_by_card(term)
        elif choice == "3":
            term = prompt("National ID: ")
            results = self.voter_service.search_by_national_id(term)
        elif choice == "4":
            try:
                sid = int(prompt("Station ID: "))
                results = self.voter_service.search_by_station(sid)
            except ValueError:
                error("Invalid input.")
                pause()
                return
        else:
            error("Invalid choice.")
            pause()
            return
        
        if not results:
            print()
            info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for voter in results:
                verified = status_badge("Verified", True) if voter['is_verified'] else status_badge("Unverified", False)
                print(f"  {THEME_ADMIN}ID:{RESET} {voter['id']}  {DIM}│{RESET}  {voter['full_name']}  {DIM}│  Card:{RESET} {voter['voter_card_number']}  {DIM}│{RESET}  {verified}")
        
        pause()
    
    def view_profile(self, current_user, stations):
        """Display voter profile."""
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        
        voter = current_user
        station_name = stations.get(voter["station_id"], {}).get("name", "Unknown")
        
        print()
        for label, value in [
            ("Name", voter['full_name']),
            ("National ID", voter['national_id']),
            ("Voter Card", f"{BRIGHT_YELLOW}{voter['voter_card_number']}{RESET}"),
            ("Date of Birth", voter['date_of_birth']),
            ("Age", voter['age']),
            ("Gender", voter['gender']),
            ("Address", voter['address']),
            ("Phone", voter['phone']),
            ("Email", voter['email']),
            ("Station", station_name),
            ("Verified", status_badge('Yes', True) if voter['is_verified'] else status_badge('No', False)),
            ("Registered", voter['registered_at']),
            ("Polls Voted", len(voter.get('has_voted_in', [])))
        ]:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        
        pause()
    
    def change_password(self, current_user, voter_service):
        """Display change password form."""
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        print()
        
        old_pass = masked_input("Current Password: ").strip()
        new_pass = masked_input("New Password: ").strip()
        
        if len(new_pass) < MIN_PASSWORD_LENGTH:
            error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            pause()
            return
        
        confirm_pass = masked_input("Confirm New Password: ").strip()
        if new_pass != confirm_pass:
            error("Passwords do not match.")
            pause()
            return
        
        success_flag, err = voter_service.change_password(
            current_user["id"], old_pass, new_pass
        )
        
        if success_flag:
            print()
            success("Password changed successfully!")
            self.data_store.save()
        else:
            error(err)
        
        pause()
