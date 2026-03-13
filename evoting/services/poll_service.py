"""
Poll service - handles poll/election business logic.
"""

import datetime
from ..utils import apply_updates


class PollService:
    """Handles poll/election management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def create_poll(
        self,
        title: str,
        description: str,
        election_type: str,
        start_date: str,
        end_date: str,
        poll_positions: list,
        station_ids: list,
        created_by: str
    ) -> tuple:
        """
        Create a new poll.
        Returns (success, poll_id or error_message).
        """
        poll_id = self.data_store.get_next_poll_id()
        
        poll_data = {
            "id": poll_id,
            "title": title,
            "description": description,
            "election_type": election_type,
            "start_date": start_date,
            "end_date": end_date,
            "positions": poll_positions,
            "station_ids": station_ids,
            "status": "draft",
            "total_votes_cast": 0,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by
        }
        
        self.data_store.add_poll(poll_data)
        self.data_store.log_action(
            "CREATE_POLL",
            created_by,
            f"Created poll: {title} (ID: {poll_id})"
        )
        
        return True, poll_id
    
    def update_poll(
        self,
        poll_id: int,
        updates: dict,
        updated_by: str
    ) -> tuple:
        """
        Update a poll.
        Returns (success, error_message or None).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] == "open":
            return False, "Cannot update an open poll. Close it first."
        
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            return False, "Cannot update a poll with votes."
        
        apply_updates(poll, updates)
        
        self.data_store.update_poll(poll_id, poll)
        self.data_store.log_action(
            "UPDATE_POLL",
            updated_by,
            f"Updated poll: {poll['title']}"
        )
        
        return True, None
    
    def delete_poll(self, poll_id: int, deleted_by: str) -> tuple:
        """
        Delete a poll.
        Returns (success, error_message or None).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] == "open":
            return False, "Cannot delete an open poll. Close it first."
        
        deleted_title = poll["title"]
        self.data_store.delete_poll(poll_id)
        self.data_store.delete_votes_for_poll(poll_id)
        
        self.data_store.log_action(
            "DELETE_POLL",
            deleted_by,
            f"Deleted poll: {deleted_title}"
        )
        
        return True, None
    
    def open_poll(self, poll_id: int, opened_by: str) -> tuple:
        """
        Open a poll for voting.
        Returns (success, error_message or None).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] != "draft" and poll["status"] != "closed":
            return False, "Poll cannot be opened from current status."
        
        # Capture original status before overwriting (used for audit log below)
        original_status = poll["status"]
        
        # Check if candidates are assigned (only required for fresh draft polls)
        if original_status == "draft":
            if not any(pos["candidate_ids"] for pos in poll["positions"]):
                return False, "Cannot open - no candidates assigned."
        
        poll["status"] = "open"
        self.data_store.update_poll(poll_id, poll)
        
        action = "OPEN_POLL" if original_status == "draft" else "REOPEN_POLL"
        self.data_store.log_action(
            action,
            opened_by,
            f"Opened poll: {poll['title']}"
        )
        
        return True, None
    
    def close_poll(self, poll_id: int, closed_by: str) -> tuple:
        """
        Close a poll.
        Returns (success, error_message or None).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] != "open":
            return False, "Poll is not open."
        
        poll["status"] = "closed"
        self.data_store.update_poll(poll_id, poll)
        
        self.data_store.log_action(
            "CLOSE_POLL",
            closed_by,
            f"Closed poll: {poll['title']}"
        )
        
        return True, None
    
    def assign_candidates(
        self,
        poll_id: int,
        position_index: int,
        candidate_ids: list,
        assigned_by: str
    ) -> tuple:
        """
        Assign candidates to a position in a poll.
        Returns (success, error_message or None).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] == "open":
            return False, "Cannot modify candidates of an open poll."
        
        if position_index >= len(poll["positions"]):
            return False, "Invalid position index."
        
        poll["positions"][position_index]["candidate_ids"] = candidate_ids
        self.data_store.update_poll(poll_id, poll)
        
        self.data_store.log_action(
            "ASSIGN_CANDIDATES",
            assigned_by,
            f"Updated candidates for poll: {poll['title']}"
        )
        
        return True, None
    
    def get_poll(self, poll_id: int) -> dict:
        """Get a poll by ID."""
        return self.data_store.get_poll(poll_id)
    
    def get_all_polls(self) -> dict:
        """Get all polls."""
        return self.data_store.get_all_polls()
    
    def get_open_polls(self) -> dict:
        """Get all open polls."""
        return {
            poll_id: poll for poll_id, poll in self.data_store.get_all_polls().items()
            if poll["status"] == "open"
        }
    
    def get_closed_polls(self) -> dict:
        """Get all closed polls."""
        return {
            poll_id: poll for poll_id, poll in self.data_store.get_all_polls().items()
            if poll["status"] == "closed"
        }
