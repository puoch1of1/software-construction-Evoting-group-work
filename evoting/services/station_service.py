"""
Station service - handles voting station business logic.
"""

import datetime
from ..config import MIN_STATION_CAPACITY
from ..utils import apply_updates


class StationService:
    """Handles voting station management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def create_station(
        self,
        name: str,
        location: str,
        region: str,
        capacity: int,
        supervisor: str,
        contact: str,
        opening_time: str,
        closing_time: str,
        created_by: str
    ) -> tuple:
        """
        Create a new voting station.
        Returns (success, station_id or error_message).
        """
        if capacity < MIN_STATION_CAPACITY:
            return False, "Capacity must be positive."
        
        station_id = self.data_store.get_next_station_id()
        
        station_data = {
            "id": station_id,
            "name": name,
            "location": location,
            "region": region,
            "capacity": capacity,
            "registered_voters": 0,
            "supervisor": supervisor,
            "contact": contact,
            "opening_time": opening_time,
            "closing_time": closing_time,
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by
        }
        
        self.data_store.add_station(station_data)
        self.data_store.log_action(
            "CREATE_STATION",
            created_by,
            f"Created station: {name} (ID: {station_id})"
        )
        
        return True, station_id
    
    def update_station(
        self,
        station_id: int,
        updates: dict,
        updated_by: str
    ) -> tuple:
        """
        Update a voting station.
        Returns (success, error_message or None).
        """
        station = self.data_store.get_station(station_id)
        if not station:
            return False, "Station not found."
        
        apply_updates(station, updates)
        
        self.data_store.update_station(station_id, station)
        self.data_store.log_action(
            "UPDATE_STATION",
            updated_by,
            f"Updated station: {station['name']} (ID: {station_id})"
        )
        
        return True, None
    
    def deactivate_station(self, station_id: int, deactivated_by: str) -> tuple:
        """
        Deactivate a voting station.
        Returns (success, error_message or None).
        """
        station = self.data_store.get_station(station_id)
        if not station:
            return False, "Station not found."
        
        station["is_active"] = False
        self.data_store.update_station(station_id, station)
        self.data_store.log_action(
            "DELETE_STATION",
            deactivated_by,
            f"Deactivated station: {station['name']}"
        )
        
        return True, None
    
    def get_station(self, station_id: int) -> dict:
        """Get a station by ID."""
        return self.data_store.get_station(station_id)
    
    def get_all_stations(self) -> dict:
        """Get all voting stations."""
        return self.data_store.get_all_stations()
    
    def get_active_stations(self) -> dict:
        """Get all active voting stations."""
        return {
            station_id: station for station_id, station in self.data_store.get_all_stations().items()
            if station["is_active"]
        }
    
    def get_voter_count_for_station(self, station_id: int) -> int:
        """Get count of voters registered at a station."""
        return sum(
            1 for v in self.data_store.get_all_voters().values()
            if v["station_id"] == station_id
        )
