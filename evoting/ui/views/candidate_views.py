"""
Candidate views - display logic for candidate-related screens.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, THEME_ADMIN, THEME_ADMIN_ACCENT, BRIGHT_BLUE
)
from ..input_handler import masked_input
from ...config import REQUIRED_EDUCATION_LEVELS, MIN_CANDIDATE_AGE
from ...validators import validate_date, calculate_age


class CandidateViews:
    """Handles candidate-related UI rendering."""
    
    def __init__(self, candidate_service, data_store):
        self.candidate_service = candidate_service
        self.data_store = data_store
    
    def create_candidate(self, current_user):
        """Display create candidate form and process input."""
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return
        
        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return
        
        # Check duplicate
        for candidate_id, candidate in self.data_store.get_all_candidates().items():
            if candidate["national_id"] == national_id:
                error("A candidate with this National ID already exists.")
                pause()
                return
        
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        valid, result = validate_date(dob_str)
        if not valid:
            error("Invalid date format.")
            pause()
            return
        age = calculate_age(result)
        
        if age < MIN_CANDIDATE_AGE:
            error(f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}")
            pause()
            return
        
        from ...config import MAX_CANDIDATE_AGE
        if age > MAX_CANDIDATE_AGE:
            error(f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}")
            pause()
            return
        
        gender = prompt("Gender (M/F/Other): ").upper()
        
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        
        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice.")
                pause()
                return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        
        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            error("Candidates with criminal records are not eligible.")
            self.data_store.log_action(
                "CANDIDATE_REJECTED",
                current_user["username"],
                f"Candidate {full_name} rejected - criminal record"
            )
            pause()
            return
        
        years_experience = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_experience)
        except ValueError:
            years_experience = 0
        
        success_flag, result = self.candidate_service.create_candidate(
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            education=education,
            party=party,
            manifesto=manifesto,
            address=address,
            phone=phone,
            email=email,
            has_criminal_record=False,
            years_experience=years_experience,
            created_by=current_user["username"]
        )
        
        if success_flag:
            print()
            success(f"Candidate '{full_name}' created successfully! ID: {result}")
            self.data_store.save()
        else:
            error(result)
        pause()
    
    def view_all_candidates(self):
        """Display all candidates in a table."""
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        candidates = self.data_store.get_all_candidates()
        
        if not candidates:
            print()
            info("No candidates found.")
            pause()
            return
        
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}",
            THEME_ADMIN
        )
        table_divider(85, THEME_ADMIN)
        
        for candidate_id, candidate in candidates.items():
            status = status_badge("Active", True) if candidate["is_active"] else status_badge("Inactive", False)
            print(f"  {candidate['id']:<5} {candidate['full_name']:<25} {candidate['party']:<20} {candidate['age']:<5} {candidate['education']:<20} {status}")
        
        print(f"\n  {DIM}Total Candidates: {len(candidates)}{RESET}")
        pause()
    
    def update_candidate(self, current_user):
        """Display update candidate form."""
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        candidates = self.data_store.get_all_candidates()
        
        if not candidates:
            print()
            info("No candidates found.")
            pause()
            return
        
        print()
        for candidate_id, candidate in candidates.items():
            print(f"  {THEME_ADMIN}{candidate['id']}.{RESET} {candidate['full_name']} {DIM}({candidate['party']}){RESET}")
        
        try:
            candidate_id = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if candidate_id not in candidates:
            error("Candidate not found.")
            pause()
            return
        
        candidate = candidates[candidate_id]
        print(f"\n  {BOLD}Updating: {candidate['full_name']}{RESET}")
        info("Press Enter to keep current value\n")
        
        updates = {}
        
        new_name = prompt(f"Full Name [{candidate['full_name']}]: ")
        if new_name:
            updates["full_name"] = new_name
        
        new_party = prompt(f"Party [{candidate['party']}]: ")
        if new_party:
            updates["party"] = new_party
        
        new_manifesto = prompt(f"Manifesto [{candidate['manifesto'][:50]}...]: ")
        if new_manifesto:
            updates["manifesto"] = new_manifesto
        
        new_phone = prompt(f"Phone [{candidate['phone']}]: ")
        if new_phone:
            updates["phone"] = new_phone
        
        new_email = prompt(f"Email [{candidate['email']}]: ")
        if new_email:
            updates["email"] = new_email
        
        new_address = prompt(f"Address [{candidate['address']}]: ")
        if new_address:
            updates["address"] = new_address
        
        new_exp = prompt(f"Years Experience [{candidate['years_experience']}]: ")
        if new_exp:
            try:
                updates["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        if updates:
            success_flag, err = self.candidate_service.update_candidate(
                candidate_id, updates, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Candidate '{candidate['full_name']}' updated successfully!")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def delete_candidate(self, current_user):
        """Display delete candidate confirmation."""
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        candidates = self.data_store.get_all_candidates()
        
        if not candidates:
            print()
            info("No candidates found.")
            pause()
            return
        
        print()
        for candidate_id, candidate in candidates.items():
            status = status_badge("Active", True) if candidate["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{candidate['id']}.{RESET} {candidate['full_name']} {DIM}({candidate['party']}){RESET} {status}")
        
        try:
            candidate_id = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if candidate_id not in candidates:
            error("Candidate not found.")
            pause()
            return
        
        # Check if in active poll
        for pid, poll in self.data_store.get_all_polls().items():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if candidate_id in pos.get("candidate_ids", []):
                        error(f"Cannot delete - candidate is in active poll: {poll['title']}")
                        pause()
                        return
        
        confirm = prompt(f"Are you sure you want to delete '{candidates[candidate_id]['full_name']}'? (yes/no): ").lower()
        if confirm == "yes":
            success_flag, err = self.candidate_service.deactivate_candidate(
                candidate_id, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Candidate '{candidates[candidate_id]['full_name']}' has been deactivated.")
                self.data_store.save()
            else:
                error(err)
        else:
            info("Deletion cancelled.")
        pause()
    
    def search_candidates(self):
        """Display candidate search interface."""
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)
        
        choice = prompt("\nChoice: ")
        results = []
        
        if choice == "1":
            term = prompt("Enter name to search: ")
            results = self.candidate_service.search_by_name(term)
        elif choice == "2":
            term = prompt("Enter party name: ")
            results = self.candidate_service.search_by_party(term)
        elif choice == "3":
            subheader("Education Levels", THEME_ADMIN_ACCENT)
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self.candidate_service.search_by_education(edu)
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
                return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self.candidate_service.search_by_age_range(min_age, max_age)
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
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(
                f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}",
                THEME_ADMIN
            )
            table_divider(75, THEME_ADMIN)
            for candidate in results:
                print(f"  {candidate['id']:<5} {candidate['full_name']:<25} {candidate['party']:<20} {candidate['age']:<5} {candidate['education']:<20}")
        
        pause()
