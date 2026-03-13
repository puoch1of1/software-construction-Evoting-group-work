"""
Candidate service - handles candidate business logic.
"""

import datetime
from ..config import MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS
from ..utils import apply_updates


class CandidateService:
    """Handles candidate management business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def create_candidate(
        self,
        full_name: str,
        national_id: str,
        date_of_birth: str,
        age: int,
        gender: str,
        education: str,
        party: str,
        manifesto: str,
        address: str,
        phone: str,
        email: str,
        has_criminal_record: bool,
        years_experience: int,
        created_by: str
    ) -> tuple:
        """
        Create a new candidate.
        Returns (success, candidate_id or error_message).
        """
        # Check for duplicate national ID
        for candidate_id, candidate in self.data_store.get_all_candidates().items():
            if candidate["national_id"] == national_id:
                return False, "A candidate with this National ID already exists."
        
        # Age validation
        if age < MIN_CANDIDATE_AGE:
            return False, f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"
        if age > MAX_CANDIDATE_AGE:
            return False, f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"
        
        # Criminal record check
        if has_criminal_record:
            self.data_store.log_action(
                "CANDIDATE_REJECTED",
                created_by,
                f"Candidate {full_name} rejected - criminal record"
            )
            return False, "Candidates with criminal records are not eligible."
        
        candidate_id = self.data_store.get_next_candidate_id()
        
        candidate_data = {
            "id": candidate_id,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": date_of_birth,
            "age": age,
            "gender": gender,
            "education": education,
            "party": party,
            "manifesto": manifesto,
            "address": address,
            "phone": phone,
            "email": email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by
        }
        
        self.data_store.add_candidate(candidate_data)
        self.data_store.log_action(
            "CREATE_CANDIDATE",
            created_by,
            f"Created candidate: {full_name} (ID: {candidate_id})"
        )
        
        return True, candidate_id
    
    def update_candidate(
        self,
        candidate_id: int,
        updates: dict,
        updated_by: str
    ) -> tuple:
        """
        Update a candidate.
        Returns (success, error_message or None).
        """
        candidate = self.data_store.get_candidate(candidate_id)
        if not candidate:
            return False, "Candidate not found."
        
        apply_updates(candidate, updates)
        
        self.data_store.update_candidate(candidate_id, candidate)
        self.data_store.log_action(
            "UPDATE_CANDIDATE",
            updated_by,
            f"Updated candidate: {candidate['full_name']} (ID: {candidate_id})"
        )
        
        return True, None
    
    def deactivate_candidate(self, candidate_id: int, deactivated_by: str) -> tuple:
        """
        Deactivate a candidate.
        Returns (success, error_message or None).
        """
        candidate = self.data_store.get_candidate(candidate_id)
        if not candidate:
            return False, "Candidate not found."
        
        # Check if candidate is in any open poll
        for pid, poll in self.data_store.get_all_polls().items():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if candidate_id in pos.get("candidate_ids", []):
                        return False, f"Cannot delete - candidate is in active poll: {poll['title']}"
        
        candidate["is_active"] = False
        self.data_store.update_candidate(candidate_id, candidate)
        self.data_store.log_action(
            "DELETE_CANDIDATE",
            deactivated_by,
            f"Deactivated candidate: {candidate['full_name']} (ID: {candidate_id})"
        )
        
        return True, None
    
    def get_candidate(self, candidate_id: int) -> dict:
        """Get a candidate by ID."""
        return self.data_store.get_candidate(candidate_id)
    
    def get_all_candidates(self) -> dict:
        """Get all candidates."""
        return self.data_store.get_all_candidates()
    
    def search_by_name(self, term: str) -> list:
        """Search candidates by name."""
        term = term.lower()
        return [candidate for candidate in self.data_store.get_all_candidates().values()
                if term in candidate["full_name"].lower()]
    
    def search_by_party(self, term: str) -> list:
        """Search candidates by party."""
        term = term.lower()
        return [candidate for candidate in self.data_store.get_all_candidates().values()
                if term in candidate["party"].lower()]
    
    def search_by_education(self, education: str) -> list:
        """Search candidates by education level."""
        return [candidate for candidate in self.data_store.get_all_candidates().values()
                if candidate["education"] == education]
    
    def search_by_age_range(self, min_age: int, max_age: int) -> list:
        """Search candidates by age range."""
        return [candidate for candidate in self.data_store.get_all_candidates().values()
                if min_age <= candidate["age"] <= max_age]
    
    def get_eligible_for_position(self, min_age: int) -> dict:
        """Get candidates eligible for a position based on age."""
        return {
            candidate_id: candidate for candidate_id, candidate in self.data_store.get_all_candidates().items()
            if candidate["is_active"] and candidate["is_approved"] and candidate["age"] >= min_age
        }
