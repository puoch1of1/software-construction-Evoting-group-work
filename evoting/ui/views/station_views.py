"""
Station views - display logic for voting station screens.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import RESET, BOLD, DIM, THEME_ADMIN, THEME_ADMIN_ACCENT


class StationViews:
    """Handles voting station-related UI rendering."""
    
    def __init__(self, station_service, data_store):
        self.station_service = station_service
        self.data_store = data_store
    
    def create_station(self, current_user):
        """Display create station form."""
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        
        name = prompt("Station Name: ")
        if not name:
            error("Name cannot be empty.")
            pause()
            return
        
        location = prompt("Location/Address: ")
        if not location:
            error("Location cannot be empty.")
            pause()
            return
        
        region = prompt("Region/District: ")
        
        try:
            capacity = int(prompt("Voter Capacity: "))
            if capacity <= 0:
                error("Capacity must be positive.")
                pause()
                return
        except ValueError:
            error("Invalid capacity.")
            pause()
            return
        
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")
        
        success_flag, result = self.station_service.create_station(
            name=name,
            location=location,
            region=region,
            capacity=capacity,
            supervisor=supervisor,
            contact=contact,
            opening_time=opening_time,
            closing_time=closing_time,
            created_by=current_user["username"]
        )
        
        if success_flag:
            print()
            success(f"Voting Station '{name}' created! ID: {result}")
            self.data_store.save()
        else:
            error(result)
        pause()
    
    def view_all_stations(self):
        """Display all voting stations."""
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        stations = self.data_store.get_all_stations()
        voters = self.data_store.get_all_voters()
        
        if not stations:
            print()
            info("No voting stations found.")
            pause()
            return
        
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
            THEME_ADMIN
        )
        table_divider(96, THEME_ADMIN)
        
        for station_id, station in stations.items():
            reg_count = sum(1 for v in voters.values() if v["station_id"] == station_id)
            status = status_badge("Active", True) if station["is_active"] else status_badge("Inactive", False)
            print(f"  {station['id']:<5} {station['name']:<25} {station['location']:<25} {station['region']:<15} {station['capacity']:<8} {reg_count:<8} {status}")
        
        print(f"\n  {DIM}Total Stations: {len(stations)}{RESET}")
        pause()
    
    def update_station(self, current_user):
        """Display update station form."""
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        stations = self.data_store.get_all_stations()
        
        if not stations:
            print()
            info("No stations found.")
            pause()
            return
        
        print()
        for station_id, station in stations.items():
            print(f"  {THEME_ADMIN}{station['id']}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")
        
        try:
            station_id = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if station_id not in stations:
            error("Station not found.")
            pause()
            return
        
        station = stations[station_id]
        print(f"\n  {BOLD}Updating: {station['name']}{RESET}")
        info("Press Enter to keep current value\n")
        
        updates = {}
        
        new_name = prompt(f"Name [{station['name']}]: ")
        if new_name:
            updates["name"] = new_name
        
        new_location = prompt(f"Location [{station['location']}]: ")
        if new_location:
            updates["location"] = new_location
        
        new_region = prompt(f"Region [{station['region']}]: ")
        if new_region:
            updates["region"] = new_region
        
        new_capacity = prompt(f"Capacity [{station['capacity']}]: ")
        if new_capacity:
            try:
                updates["capacity"] = int(new_capacity)
            except ValueError:
                warning("Invalid number, keeping old value.")
        
        new_supervisor = prompt(f"Supervisor [{station['supervisor']}]: ")
        if new_supervisor:
            updates["supervisor"] = new_supervisor
        
        new_contact = prompt(f"Contact [{station['contact']}]: ")
        if new_contact:
            updates["contact"] = new_contact
        
        if updates:
            success_flag, err = self.station_service.update_station(
                station_id, updates, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Station '{station['name']}' updated successfully!")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def delete_station(self, current_user):
        """Display delete station confirmation."""
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        stations = self.data_store.get_all_stations()
        voters = self.data_store.get_all_voters()
        
        if not stations:
            print()
            info("No stations found.")
            pause()
            return
        
        print()
        for station_id, station in stations.items():
            status = status_badge("Active", True) if station["is_active"] else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{station['id']}.{RESET} {station['name']} {DIM}({station['location']}){RESET} {status}")
        
        try:
            station_id = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if station_id not in stations:
            error("Station not found.")
            pause()
            return
        
        voter_count = sum(1 for v in voters.values() if v["station_id"] == station_id)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                info("Cancelled.")
                pause()
                return
        
        if prompt(f"Confirm deactivation of '{stations[station_id]['name']}'? (yes/no): ").lower() == "yes":
            success_flag, err = self.station_service.deactivate_station(
                station_id, current_user["username"]
            )
            if success_flag:
                print()
                success(f"Station '{stations[station_id]['name']}' deactivated.")
                self.data_store.save()
            else:
                error(err)
        else:
            info("Cancelled.")
        
        pause()
