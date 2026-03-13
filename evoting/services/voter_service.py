"""
Voter service - handles voter registration and management.
"""

import datetime
from ..validators import hash_password, generate_voter_card_number


class VoterService:
    """Handles voter management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def register_voter(
        self,
        full_name: str,
        national_id: str,
        date_of_birth: str,
        age: int,
        gender: str,
        address: str,
        phone: str,
        email: str,
        password: str,
        station_id: int
    ) -> tuple:
        """
        Register a new voter.
        Returns (success, voter_card_number or error_message).
        """
        # Check for duplicate national ID
        for voter_id, voter in self.data_store.get_all_voters().items():
            if voter["national_id"] == national_id:
                return False, "A voter with this National ID already exists."
        
        voter_card = generate_voter_card_number()
        voter_id = self.data_store.get_next_voter_id()
        
        voter_data = {
            "id": voter_id,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": date_of_birth,
            "age": age,
            "gender": gender,
            "address": address,
            "phone": phone,
            "email": email,
            "password": hash_password(password),
            "voter_card_number": voter_card,
            "station_id": station_id,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter"
        }
        
        self.data_store.add_voter(voter_data)
        self.data_store.log_action(
            "REGISTER",
            full_name,
            f"New voter registered with card: {voter_card}"
        )
        
        return True, voter_card
    
    def verify_voter(self, voter_id: int, verified_by: str) -> tuple:
        """
        Verify a voter.
        Returns (success, error_message or None).
        """
        voter = self.data_store.get_voter(voter_id)
        if not voter:
            return False, "Voter not found."
        
        if voter["is_verified"]:
            return False, "Already verified."
        
        voter["is_verified"] = True
        self.data_store.update_voter(voter_id, voter)
        self.data_store.log_action(
            "VERIFY_VOTER",
            verified_by,
            f"Verified voter: {voter['full_name']}"
        )
        
        return True, None
    
    def verify_all_pending(self, verified_by: str) -> int:
        """
        Verify all pending voters.
        Returns count of verified voters.
        """
        count = 0
        for voter_id, voter in self.data_store.get_all_voters().items():
            if not voter["is_verified"]:
                voter["is_verified"] = True
                self.data_store.update_voter(voter_id, voter)
                count += 1
        
        if count > 0:
            self.data_store.log_action(
                "VERIFY_ALL_VOTERS",
                verified_by,
                f"Verified {count} voters"
            )
        
        return count
    
    def deactivate_voter(self, voter_id: int, deactivated_by: str) -> tuple:
        """
        Deactivate a voter.
        Returns (success, error_message or None).
        """
        voter = self.data_store.get_voter(voter_id)
        if not voter:
            return False, "Voter not found."
        
        if not voter["is_active"]:
            return False, "Already deactivated."
        
        voter["is_active"] = False
        self.data_store.update_voter(voter_id, voter)
        self.data_store.log_action(
            "DEACTIVATE_VOTER",
            deactivated_by,
            f"Deactivated voter: {voter['full_name']}"
        )
        
        return True, None
    
    def change_password(self, voter_id: int, old_password: str, new_password: str) -> tuple:
        """
        Change voter password.
        Returns (success, error_message or None).
        """
        voter = self.data_store.get_voter(voter_id)
        if not voter:
            return False, "Voter not found."
        
        if hash_password(old_password) != voter["password"]:
            return False, "Incorrect current password."
        
        voter["password"] = hash_password(new_password)
        self.data_store.update_voter(voter_id, voter)
        self.data_store.log_action(
            "CHANGE_PASSWORD",
            voter["voter_card_number"],
            "Password changed"
        )
        
        return True, None
    
    def get_voter(self, voter_id: int) -> dict:
        """Get a voter by ID."""
        return self.data_store.get_voter(voter_id)
    
    def get_all_voters(self) -> dict:
        """Get all voters."""
        return self.data_store.get_all_voters()
    
    def get_unverified_voters(self) -> dict:
        """Get all unverified voters."""
        return {
            voter_id: voter for voter_id, voter in self.data_store.get_all_voters().items()
            if not voter["is_verified"]
        }
    
    def search_by_name(self, term: str) -> list:
        """Search voters by name."""
        term = term.lower()
        return [voter for voter in self.data_store.get_all_voters().values()
                if term in voter["full_name"].lower()]
    
    def search_by_card(self, card_number: str) -> list:
        """Search voters by card number."""
        return [voter for voter in self.data_store.get_all_voters().values()
                if card_number == voter["voter_card_number"]]
    
    def search_by_national_id(self, national_id: str) -> list:
        """Search voters by national ID."""
        return [voter for voter in self.data_store.get_all_voters().values()
                if national_id == voter["national_id"]]
    
    def search_by_station(self, station_id: int) -> list:
        """Search voters by station."""
        return [voter for voter in self.data_store.get_all_voters().values()
                if voter["station_id"] == station_id]
