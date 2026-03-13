"""
Position service - handles position business logic.
"""

import datetime
from ..config import MIN_CANDIDATE_AGE, MIN_POSITION_SEATS
from ..utils import apply_updates


class PositionService:
    """Handles position management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def create_position(
        self,
        title: str,
        description: str,
        level: str,
        max_winners: int,
        min_candidate_age: int,
        created_by: str
    ) -> tuple:
        """
        Create a new position.
        Returns (success, position_id or error_message).
        """
        if max_winners < MIN_POSITION_SEATS:
            return False, "Must be at least 1."
        
        position_id = self.data_store.get_next_position_id()
        
        position_data = {
            "id": position_id,
            "title": title,
            "description": description,
            "level": level,
            "max_winners": max_winners,
            "min_candidate_age": min_candidate_age,
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by
        }
        
        self.data_store.add_position(position_data)
        self.data_store.log_action(
            "CREATE_POSITION",
            created_by,
            f"Created position: {title} (ID: {position_id})"
        )
        
        return True, position_id
    
    def update_position(
        self,
        position_id: int,
        updates: dict,
        updated_by: str
    ) -> tuple:
        """
        Update a position.
        Returns (success, error_message or None).
        """
        position = self.data_store.get_position(position_id)
        if not position:
            return False, "Position not found."
        
        apply_updates(position, updates)
        
        self.data_store.update_position(position_id, position)
        self.data_store.log_action(
            "UPDATE_POSITION",
            updated_by,
            f"Updated position: {position['title']}"
        )
        
        return True, None
    
    def deactivate_position(self, position_id: int, deactivated_by: str) -> tuple:
        """
        Deactivate a position.
        Returns (success, error_message or None).
        """
        position = self.data_store.get_position(position_id)
        if not position:
            return False, "Position not found."
        
        # Check if position is in any open poll
        for position_id, poll in self.data_store.get_all_polls().items():
            for pp in poll.get("positions", []):
                if pp["position_id"] == position_id and poll["status"] == "open":
                    return False, f"Cannot delete - in active poll: {poll['title']}"
        
        position["is_active"] = False
        self.data_store.update_position(position_id, position)
        self.data_store.log_action(
            "DELETE_POSITION",
            deactivated_by,
            f"Deactivated position: {position['title']}"
        )
        
        return True, None
    
    def get_position(self, position_id: int) -> dict:
        """Get a position by ID."""
        return self.data_store.get_position(position_id)
    
    def get_all_positions(self) -> dict:
        """Get all positions."""
        return self.data_store.get_all_positions()
    
    def get_active_positions(self) -> dict:
        """Get all active positions."""
        return {
            position_id: position for position_id, position in self.data_store.get_all_positions().items()
            if position["is_active"]
        }
