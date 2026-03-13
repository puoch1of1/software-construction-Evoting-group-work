"""
Statistics service - handles results and statistics calculations.
"""

from ..config import AGE_GROUPS, AGE_GROUP_OVERFLOW_LABEL


class StatisticsService:
    """Handles election statistics and results calculations."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def get_poll_results(self, poll_id: int) -> dict:
        """
        Get comprehensive results for a poll.
        Returns dict with position results, turnout, etc.
        """
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return None
        
        # Calculate eligible voters
        eligible_voters = sum(
            1 for voter in self.data_store.get_all_voters().values()
            if voter["is_verified"] and voter["is_active"] and voter["station_id"] in poll["station_ids"]
        )
        
        turnout = (poll['total_votes_cast'] / eligible_voters * 100) if eligible_voters > 0 else 0
        
        # Get results per position
        position_results = []
        votes = self.data_store.get_all_votes()
        
        for pos in poll["positions"]:
            vote_counts = {}
            abstain_count = 0
            total_pos = 0
            
            for vote in votes:
                if vote["poll_id"] == poll_id and vote["position_id"] == pos["position_id"]:
                    total_pos += 1
                    if vote["abstained"]:
                        abstain_count += 1
                    else:
                        candidate_id = vote["candidate_id"]
                        vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1
            
            # Sort by votes descending
            sorted_results = sorted(
                vote_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            position_results.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "max_winners": pos["max_winners"],
                "vote_counts": sorted_results,
                "abstain_count": abstain_count,
                "total_votes": total_pos
            })
        
        return {
            "poll": poll,
            "eligible_voters": eligible_voters,
            "turnout": turnout,
            "position_results": position_results
        }
    
    def get_station_results(self, poll_id: int, station_id: int) -> dict:
        """Get results for a specific station in a poll."""
        poll = self.data_store.get_poll(poll_id)
        if not poll:
            return None
        
        station = self.data_store.get_station(station_id)
        if not station:
            return None
        
        votes = self.data_store.get_all_votes()
        station_votes = [vote for vote in votes if vote["poll_id"] == poll_id and vote["station_id"] == station_id]
        
        # Count unique voters
        unique_voters = len(set(vote["voter_id"] for vote in station_votes))
        
        # Registered voters at station
        registered = sum(
            1 for voter in self.data_store.get_all_voters().values()
            if voter["station_id"] == station_id and voter["is_verified"] and voter["is_active"]
        )
        
        turnout = (unique_voters / registered * 100) if registered > 0 else 0
        
        # Results per position
        position_results = []
        for pos in poll["positions"]:
            pos_votes = [vote for vote in station_votes if vote["position_id"] == pos["position_id"]]
            vote_counts = {}
            abstain_count = 0
            
            for vote in pos_votes:
                if vote["abstained"]:
                    abstain_count += 1
                else:
                    candidate_id = vote["candidate_id"]
                    vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1
            
            position_results.append({
                "position_id": pos["position_id"],
                "position_title": pos["position_title"],
                "vote_counts": sorted(vote_counts.items(), key=lambda x: x[1], reverse=True),
                "abstain_count": abstain_count,
                "total_votes": len(pos_votes)
            })
        
        return {
            "station": station,
            "registered_voters": registered,
            "votes_cast": unique_voters,
            "turnout": turnout,
            "position_results": position_results
        }
    
    def get_system_statistics(self) -> dict:
        """Get comprehensive system statistics."""
        candidates = self.data_store.get_all_candidates()
        voters = self.data_store.get_all_voters()
        stations = self.data_store.get_all_stations()
        polls = self.data_store.get_all_polls()
        votes = self.data_store.get_all_votes()
        
        # Candidate statistics
        total_candidates = len(candidates)
        active_candidates = sum(1 for candidate in candidates.values().values() if candidate["is_active"])
        
        # Voter statistics
        total_voters = len(voters)
        verified_voters = sum(1 for voter in voters.values().values() if voter["is_verified"])
        active_voters = sum(1 for voter in voters.values().values() if voter["is_active"])
        
        # Station statistics
        total_stations = len(stations)
        active_stations = sum(1 for station in stations.values().values() if station["is_active"])
        
        # Poll statistics
        total_polls = len(polls)
        open_polls = sum(1 for poll in polls.values().values() if poll["status"] == "open")
        closed_polls = sum(1 for poll in polls.values().values() if poll["status"] == "closed")
        draft_polls = sum(1 for poll in polls.values().values() if poll["status"] == "draft")
        
        # Voter demographics
        gender_counts = {}
        age_groups = {label: 0 for _, _, label in AGE_GROUPS}
        age_groups[AGE_GROUP_OVERFLOW_LABEL] = 0
        
        for voter in voters.values().values():
            gender = voter.get("gender", "?")
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            age = voter.get("age", 0)
            placed = False
            for low, high, label in AGE_GROUPS:
                if low <= age <= high:
                    age_groups[label] += 1
                    placed = True
                    break
            if not placed:
                age_groups[AGE_GROUP_OVERFLOW_LABEL] += 1
        
        # Station load
        station_loads = []
        for station_id, station in stations.items():
            voter_count = sum(1 for voter in voters.values().values() if voter["station_id"] == station_id)
            load_pct = (voter_count / station["capacity"] * 100) if station["capacity"] > 0 else 0
            station_loads.append({
                "station": station,
                "voter_count": voter_count,
                "load_percent": load_pct
            })
        
        # Party distribution
        party_counts = {}
        for candidate in candidates.values().values():
            if candidate["is_active"]:
                party = candidate["party"]
                party_counts[party] = party_counts.get(party, 0) + 1
        
        # Education distribution
        edu_counts = {}
        for candidate in candidates.values().values():
            if candidate["is_active"]:
                edu = candidate["education"]
                edu_counts[edu] = edu_counts.get(edu, 0) + 1
        
        return {
            "candidates": {
                "total": total_candidates,
                "active": active_candidates
            },
            "voters": {
                "total": total_voters,
                "verified": verified_voters,
                "active": active_voters
            },
            "stations": {
                "total": total_stations,
                "active": active_stations
            },
            "polls": {
                "total": total_polls,
                "open": open_polls,
                "closed": closed_polls,
                "draft": draft_polls
            },
            "total_votes": len(votes),
            "gender_distribution": gender_counts,
            "age_distribution": age_groups,
            "station_loads": station_loads,
            "party_distribution": party_counts,
            "education_distribution": edu_counts
        }
