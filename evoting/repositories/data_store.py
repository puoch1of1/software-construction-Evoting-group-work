"""
DataStore - centralized data persistence handler.
Manages loading and saving all application data to JSON.
"""

import json
import os
import hashlib
import datetime

from ..config import (
    DATA_FILE_PATH,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_EMAIL,
)
from ..ui.console import info, error


class DataStore:
    """
    Centralized data storage manager.
    Handles JSON persistence and maintains all entity collections.
    """
    
    def __init__(self, data_file_path: str = DATA_FILE_PATH):
        self.data_file_path = data_file_path
        
        # Entity collections (stored as dicts with int keys)
        self.candidates = {}
        self.candidate_id_counter = 1
        
        self.voting_stations = {}
        self.station_id_counter = 1
        
        self.polls = {}
        self.poll_id_counter = 1
        
        self.positions = {}
        self.position_id_counter = 1
        
        self.voters = {}
        self.voter_id_counter = 1
        
        self.admins = {}
        self.admin_id_counter = 1
        
        self.votes = []
        self.audit_log = []
        
        # Initialize default admin
        self._init_default_admin()
    
    def _init_default_admin(self):
        """Create the default system administrator."""
        self.admins[1] = {
            "id": 1,
            "username": DEFAULT_ADMIN_USERNAME,
            "password": hashlib.sha256(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest(),
            "full_name": "System Administrator",
            "email": DEFAULT_ADMIN_EMAIL,
            "role": "super_admin",
            "created_at": str(datetime.datetime.now()),
            "is_active": True
        }
        self.admin_id_counter = 2
    
    def save(self):
        """Save all data to JSON file."""
        data = {
            "candidates": self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": self.voting_stations,
            "station_id_counter": self.station_id_counter,
            "polls": self.polls,
            "poll_id_counter": self.poll_id_counter,
            "positions": self.positions,
            "position_id_counter": self.position_id_counter,
            "voters": self.voters,
            "voter_id_counter": self.voter_id_counter,
            "admins": self.admins,
            "admin_id_counter": self.admin_id_counter,
            "votes": self.votes,
            "audit_log": self.audit_log
        }
        try:
            with open(self.data_file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            error(f"Error saving data: {e}")
    

    
    def load(self):
        """Load all data from JSON file."""
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, "r") as f:
                    data = json.load(f)
                
                self.candidates = {int(k): candidate_data for k, candidate_data in data.get("candidates", {}).items()}
                self.candidate_id_counter = data.get("candidate_id_counter", 1)
                
                self.voting_stations = {int(k): station_data for k, station_data in data.get("voting_stations", {}).items()}
                self.station_id_counter = data.get("station_id_counter", 1)
                
                self.polls = {int(k): poll_data for k, poll_data in data.get("polls", {}).items()}
                self.poll_id_counter = data.get("poll_id_counter", 1)
                
                self.positions = {int(k): position_data for k, position_data in data.get("positions", {}).items()}
                self.position_id_counter = data.get("position_id_counter", 1)
                
                self.voters = {int(k): voter_data for k, voter_data in data.get("voters", {}).items()}
                self.voter_id_counter = data.get("voter_id_counter", 1)
                
                self.admins = {int(k): admin_data for k, admin_data in data.get("admins", {}).items()}
                self.admin_id_counter = data.get("admin_id_counter", 1)
                
                self.votes = data.get("votes", [])
                self.audit_log = data.get("audit_log", [])
                
                info("Data loaded successfully")
        except Exception as e:
            error(f"Error loading data: {e}")
    
    def log_action(self, action: str, user: str, details: str):
        """Add an entry to the audit log."""
        self.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details
        })
    
    # Candidate operations
    def get_next_candidate_id(self) -> int:
        """Get and increment candidate ID counter."""
        current_id = self.candidate_id_counter
        self.candidate_id_counter += 1
        return current_id
    
    def add_candidate(self, candidate_data: dict):
        """Add a new candidate."""
        self.candidates[candidate_data["id"]] = candidate_data
    
    def get_candidate(self, candidate_id: int) -> dict:
        """Get a candidate by ID."""
        return self.candidates.get(candidate_id)
    
    def get_all_candidates(self) -> dict:
        """Get all candidates."""
        return self.candidates
    
    def update_candidate(self, candidate_id: int, candidate_data: dict):
        """Update a candidate."""
        self.candidates[candidate_id] = candidate_data
    
    # Voting Station operations
    def get_next_station_id(self) -> int:
        """Get and increment station ID counter."""
        current_id = self.station_id_counter
        self.station_id_counter += 1
        return current_id
    
    def add_station(self, station_data: dict):
        """Add a new voting station."""
        self.voting_stations[station_data["id"]] = station_data
    
    def get_station(self, station_id: int) -> dict:
        """Get a station by ID."""
        return self.voting_stations.get(station_id)
    
    def get_all_stations(self) -> dict:
        """Get all voting stations."""
        return self.voting_stations
    
    def update_station(self, station_id: int, station_data: dict):
        """Update a voting station."""
        self.voting_stations[station_id] = station_data
    
    # Position operations
    def get_next_position_id(self) -> int:
        """Get and increment position ID counter."""
        current_id = self.position_id_counter
        self.position_id_counter += 1
        return current_id
    
    def add_position(self, position_data: dict):
        """Add a new position."""
        self.positions[position_data["id"]] = position_data
    
    def get_position(self, position_id: int) -> dict:
        """Get a position by ID."""
        return self.positions.get(position_id)
    
    def get_all_positions(self) -> dict:
        """Get all positions."""
        return self.positions
    
    def update_position(self, position_id: int, position_data: dict):
        """Update a position."""
        self.positions[position_id] = position_data
    
    # Poll operations
    def get_next_poll_id(self) -> int:
        """Get and increment poll ID counter."""
        current_id = self.poll_id_counter
        self.poll_id_counter += 1
        return current_id
    
    def add_poll(self, poll_data: dict):
        """Add a new poll."""
        self.polls[poll_data["id"]] = poll_data
    
    def get_poll(self, poll_id: int) -> dict:
        """Get a poll by ID."""
        return self.polls.get(poll_id)
    
    def get_all_polls(self) -> dict:
        """Get all polls."""
        return self.polls
    
    def update_poll(self, poll_id: int, poll_data: dict):
        """Update a poll."""
        self.polls[poll_id] = poll_data
    
    def delete_poll(self, poll_id: int):
        """Delete a poll."""
        if poll_id in self.polls:
            del self.polls[poll_id]
    
    # Voter operations
    def get_next_voter_id(self) -> int:
        """Get and increment voter ID counter."""
        current_id = self.voter_id_counter
        self.voter_id_counter += 1
        return current_id
    
    def add_voter(self, voter_data: dict):
        """Add a new voter."""
        self.voters[voter_data["id"]] = voter_data
    
    def get_voter(self, voter_id: int) -> dict:
        """Get a voter by ID."""
        return self.voters.get(voter_id)
    
    def get_all_voters(self) -> dict:
        """Get all voters."""
        return self.voters
    
    def update_voter(self, voter_id: int, voter_data: dict):
        """Update a voter."""
        self.voters[voter_id] = voter_data
    
    def get_voter_by_card(self, card_number: str) -> dict:
        """Get a voter by card number."""
        for voter in self.voters.values():
            if voter["voter_card_number"] == card_number:
                return voter
        return None
    
    def get_voter_by_national_id(self, national_id: str) -> dict:
        """Get a voter by national ID."""
        for voter in self.voters.values():
            if voter["national_id"] == national_id:
                return voter
        return None
    
    # Admin operations
    def get_next_admin_id(self) -> int:
        """Get and increment admin ID counter."""
        current_id = self.admin_id_counter
        self.admin_id_counter += 1
        return current_id
    
    def add_admin(self, admin_data: dict):
        """Add a new admin."""
        self.admins[admin_data["id"]] = admin_data
    
    def get_admin(self, admin_id: int) -> dict:
        """Get an admin by ID."""
        return self.admins.get(admin_id)
    
    def get_all_admins(self) -> dict:
        """Get all admins."""
        return self.admins
    
    def update_admin(self, admin_id: int, admin_data: dict):
        """Update an admin."""
        self.admins[admin_id] = admin_data
    
    def get_admin_by_username(self, username: str) -> dict:
        """Get an admin by username."""
        for admin in self.admins.values():
            if admin["username"] == username:
                return admin
        return None
    
    # Vote operations
    def add_vote(self, vote_data: dict):
        """Add a new vote."""
        self.votes.append(vote_data)
    
    def get_all_votes(self) -> list:
        """Get all votes."""
        return self.votes
    
    def get_votes_for_poll(self, poll_id: int) -> list:
        """Get all votes for a specific poll."""
        return [v for v in self.votes if v["poll_id"] == poll_id]
    
    def delete_votes_for_poll(self, poll_id: int):
        """Delete all votes for a specific poll."""
        self.votes = [v for v in self.votes if v["poll_id"] != poll_id]
    
    # Audit log operations
    def get_audit_log(self) -> list:
        """Get the full audit log."""
        return self.audit_log
