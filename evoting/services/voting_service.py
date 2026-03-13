"""
Voting service - handles ballot casting and vote management.
"""

import datetime
import hashlib
from ..config import VOTE_HASH_LENGTH


class VotingService:
    """Handles voting/ballot casting business logic."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def get_available_polls_for_voter(self, voter: dict) -> dict:
        """Get polls available for a voter to vote in."""
        open_polls = {
            poll_id: poll for poll_id, poll in self.data_store.get_all_polls().items()
            if poll["status"] == "open"
        }
        
        available = {}
        for poll_id, poll in open_polls.items():
            # Check if voter hasn't voted and station is included
            if (poll_id not in voter.get("has_voted_in", []) and
                voter["station_id"] in poll["station_ids"]):
                available[poll_id] = poll
        
        return available
    
    def cast_vote(
        self,
        voter: dict,
        poll_id: int,
        votes: list
    ) -> tuple:
        """
        Cast votes for a poll.
        votes is a list of dicts with position_id, candidate_id, abstained.
        Returns (success, vote_hash or error_message).
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return False, "Poll not found."
        
        if poll["status"] != "open":
            return False, "Poll is not open."
        
        if poll_id in voter.get("has_voted_in", []):
            return False, "You have already voted in this poll."
        
        if voter["station_id"] not in poll["station_ids"]:
            return False, "Your station is not included in this poll."
        
        vote_timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{voter['id']}{poll_id}{vote_timestamp}".encode()
        ).hexdigest()[:VOTE_HASH_LENGTH]
        
        # Record each vote
        for vote in votes:
            vote_data = {
                "vote_id": vote_hash + str(vote["position_id"]),
                "poll_id": poll_id,
                "position_id": vote["position_id"],
                "candidate_id": vote.get("candidate_id"),
                "voter_id": voter["id"],
                "station_id": voter["station_id"],
                "timestamp": vote_timestamp,
                "abstained": vote.get("abstained", False)
            }
            self.data_store.add_vote(vote_data)
        
        # Update voter's voted list
        for voter_id, iter_voter in self.data_store.get_all_voters().items():
            if iter_voter["id"] == voter["id"]:
                iter_voter["has_voted_in"].append(poll_id)
                self.data_store.update_voter(voter_id, iter_voter)
                break
        
        # Update poll vote count
        poll["total_votes_cast"] += 1
        self.data_store.update_poll(poll_id, poll)
        
        self.data_store.log_action(
            "CAST_VOTE",
            voter["voter_card_number"],
            f"Voted in poll: {poll['title']} (Hash: {vote_hash})"
        )
        
        return True, vote_hash
    
    def get_voter_votes_in_poll(self, voter_id: int, poll_id: int) -> list:
        """Get a voter's votes in a specific poll."""
        return [
            vote for vote in self.data_store.get_all_votes()
            if vote["poll_id"] == poll_id and vote["voter_id"] == voter_id
        ]
    
    def has_voter_voted_in_poll(self, voter: dict, poll_id: int) -> bool:
        """Check if voter has voted in a poll."""
        return poll_id in voter.get("has_voted_in", [])
