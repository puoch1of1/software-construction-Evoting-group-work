"""
Position views - display logic for position management screens.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import RESET, BOLD, DIM, THEME_ADMIN, THEME_ADMIN_ACCENT
from ...config import MIN_CANDIDATE_AGE, DEFAULT_POSITION_SEATS, DEFAULT_TERM_LENGTH_YEARS


class PositionViews:
    """Handles position-related UI rendering."""
    
    def __init__(self, position_service, data_store):
        self.position_service = position_service
        self.data_store = data_store
    
    def create_position(self, current_user):
        """Display create position form."""
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        
        title = prompt("Position Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        
        description = prompt("Description: ")
        
        level = prompt("Level (National/Regional/Local): ")
        if level not in ["National", "Regional", "Local"]:
            warning("Using 'Local' as default level.")
            level = "Local"
        
        try:
            max_winners = int(prompt(f"Number of seats/winners (default {DEFAULT_POSITION_SEATS}): ") or str(DEFAULT_POSITION_SEATS))
            if max_winners < 1:
                max_winners = DEFAULT_POSITION_SEATS
        except ValueError:
            max_winners = DEFAULT_POSITION_SEATS
        
        try:
            term_length = int(prompt(f"Term length in years (default {DEFAULT_TERM_LENGTH_YEARS}): ") or str(DEFAULT_TERM_LENGTH_YEARS))
        except ValueError:
            term_length = DEFAULT_TERM_LENGTH_YEARS
        
        try:
            min_age = int(prompt(f"Minimum candidate age (default {MIN_CANDIDATE_AGE}): ") or str(MIN_CANDIDATE_AGE))
        except ValueError:
            min_age = MIN_CANDIDATE_AGE
        
        responsibilities = prompt("Key Responsibilities: ")
        
        success_flag, result = self.position_service.create_position(
            title=title,
            description=description,
            level=level,
            max_winners=max_winners,
            term_length=term_length,
            min_candidate_age=min_age,
            responsibilities=responsibilities,
            created_by=current_user["username"]
        )
        
        if success_flag:
            print()
            success(f"Position '{title}' created! ID: {result}")
            self.data_store.save()
        else:
            error(result)
        pause()
    
    def view_all_positions(self):
        """Display all positions."""
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        positions = self.data_store.get_all_positions()
        
        if not positions:
            print()
            info("No positions found.")
            pause()
            return
        
        print()
        table_header(
            f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<6} {'Min Age':<8} {'Term':<6} {'Status':<10}",
            THEME_ADMIN
        )
        table_divider(72, THEME_ADMIN)
        
        for position_id, position in positions.items():
            status = status_badge("Active", True) if position["is_active"] else status_badge("Inactive", False)
            print(f"  {position['id']:<5} {position['title']:<25} {position['level']:<12} {position['max_winners']:<6} {position['min_candidate_age']:<8} {position['term_length']} yrs {status}")
        
        print(f"\n  {DIM}Total Positions: {len(positions)}{RESET}")
        pause()
    
    def update_position(self, current_user):
        """Display update position form."""
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        positions = self.data_store.get_all_positions()
        
        if not positions:
            print()
            info("No positions found.")
            pause()
            return
        
        print()
        for position_id, position in positions.items():
            print(f"  {THEME_ADMIN}{position['id']}.{RESET} {position['title']} {DIM}({position['level']}){RESET}")
        
        try:
            position_id = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if position_id not in positions:
            error("Position not found.")
            pause()
            return
        
        position = positions[position_id]
        print(f"\n  {BOLD}Updating: {position['title']}{RESET}")
        info("Press Enter to keep current value\n")
        
        updates = {}
        
        new_title = prompt(f"Title [{position['title']}]: ")
        if new_title:
            updates["title"] = new_title
        
        new_desc = prompt(f"Description [{position['description'][:50]}]: ")
        if new_desc:
            updates["description"] = new_desc
        
        new_level = prompt(f"Level [{position['level']}]: ")
        if new_level and new_level in ["National", "Regional", "Local"]:
            updates["level"] = new_level
        
        new_winners = prompt(f"Max Winners [{position['max_winners']}]: ")
        if new_winners:
            try:
                updates["max_winners"] = int(new_winners)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        new_term = prompt(f"Term Length [{position['term_length']}]: ")
        if new_term:
            try:
                updates["term_length"] = int(new_term)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        new_age = prompt(f"Min Candidate Age [{position['min_candidate_age']}]: ")
        if new_age:
            try:
                updates["min_candidate_age"] = int(new_age)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        if updates:
            success_flag, err = self.position_service.update_position(
                position_id, updates, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Position '{position['title']}' updated successfully!")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def delete_position(self, current_user):
        """Display delete position confirmation."""
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        positions = self.data_store.get_all_positions()
        polls = self.data_store.get_all_polls()
        
        if not positions:
            print()
            info("No positions found.")
            pause()
            return
        
        print()
        for position_id, position in positions.items():
            status = status_badge("Active", True) if position["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{position['id']}.{RESET} {position['title']} {DIM}({position['level']}){RESET} {status}")
        
        try:
            position_id = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if position_id not in positions:
            error("Position not found.")
            pause()
            return
        
        # Check if position is used in any poll
        for poll_id, poll in polls.items():
            for pos in poll.get("positions", []):
                if pos["position_id"] == position_id and poll["status"] == "open":
                    error(f"Cannot delete - position is used in active poll: {poll['title']}")
                    pause()
                    return
        
        if prompt(f"Deactivate position '{positions[position_id]['title']}'? (yes/no): ").lower() == "yes":
            success_flag, err = self.position_service.deactivate_position(
                position_id, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Position '{positions[position_id]['title']}' deactivated.")
                self.data_store.save()
            else:
                error(err)
        
        pause()
