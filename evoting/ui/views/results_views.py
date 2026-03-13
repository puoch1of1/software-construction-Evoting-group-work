"""
Results views - display logic for election results and statistics.
"""

from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, GREEN, YELLOW, RED, GRAY,
    THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER, THEME_VOTER_ACCENT,
    BRIGHT_GREEN, BRIGHT_CYAN, BRIGHT_YELLOW, BRIGHT_MAGENTA,
    BG_GREEN, BLACK
)


class ResultsViews:
    """Handles results and statistics UI rendering."""
    
    def __init__(self, statistics_service, data_store):
        self.statistics_service = statistics_service
        self.data_store = data_store
    
    def view_poll_results(self):
        """Display detailed poll results with bar charts."""
        clear_screen()
        header("ELECTION RESULTS", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        votes = self.data_store.get_all_votes()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        subheader("Select Poll", THEME_ADMIN_ACCENT)
        for poll_id, poll in polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET} - {poll['total_votes_cast']} votes")
        
        try:
            poll_id = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if poll_id not in polls:
            error("Poll not found.")
            pause()
            return
        
        poll = polls[poll_id]
        
        clear_screen()
        header(f"RESULTS: {poll['title']}", THEME_ADMIN)
        print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {poll['status'].upper()}  {DIM}│  Total Votes:{RESET} {poll['total_votes_cast']}")
        print()
        
        for pos in poll["positions"]:
            subheader(pos['position_title'], THEME_ADMIN_ACCENT)
            vote_counts = {}
            abstain_count = 0
            
            for vote in votes:
                if vote["poll_id"] == poll_id and vote["position_id"] == pos["position_id"]:
                    if vote["abstained"]:
                        abstain_count += 1
                    else:
                        vote_counts[vote["candidate_id"]] = vote_counts.get(vote["candidate_id"], 0) + 1
            
            total = sum(vote_counts.values()) + abstain_count
            
            if total == 0:
                info("No votes recorded for this position.")
                continue
            
            sorted_results = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (candidate_id, count) in enumerate(sorted_results, 1):
                cand = candidates.get(candidate_id, {})
                pct = (count / total * 100) if total > 0 else 0
                bar_length = int(pct / 2)
                bar = f"{BRIGHT_GREEN}{'█' * bar_length}{GRAY}{'░' * (50 - bar_length)}{RESET}"
                
                winner_badge = ""
                if rank <= pos["max_winners"] and poll["status"] == "closed":
                    winner_badge = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}"
                
                print(f"  {BOLD}{rank}. {cand.get('full_name', 'Unknown')}{RESET} {DIM}({cand.get('party', 'N/A')}){RESET}")
                print(f"     {bar} {BOLD}{count}{RESET} votes ({pct:.1f}%){winner_badge}")
            
            if abstain_count > 0:
                pct = (abstain_count / total * 100)
                print(f"  {GRAY}Abstained: {abstain_count} ({pct:.1f}%){RESET}")
            
            print()
        
        pause()
    
    def view_results_by_station(self):
        """Display results broken down by voting station."""
        clear_screen()
        header("RESULTS BY VOTING STATION", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        stations = self.data_store.get_all_stations()
        candidates = self.data_store.get_all_candidates()
        votes = self.data_store.get_all_votes()
        
        closed_polls = {poll_id: poll for poll_id, poll in polls.items() if poll["status"] in ["open", "closed"]}
        
        if not closed_polls:
            print()
            info("No polls with results.")
            pause()
            return
        
        for poll_id, poll in closed_polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}")
        
        try:
            poll_id = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if poll_id not in closed_polls:
            error("Poll not found.")
            pause()
            return
        
        poll = closed_polls[poll_id]
        
        clear_screen()
        header(f"STATION BREAKDOWN: {poll['title']}", THEME_ADMIN)
        
        for station_id in poll.get("station_ids", []):
            if station_id not in stations:
                continue
            station = stations[station_id]
            
            station_votes = [vote for vote in votes if vote["poll_id"] == poll_id and vote.get("station_id") == station_id]
            
            subheader(f"{station['name']} ({station['location']})", THEME_ADMIN_ACCENT)
            print(f"  {DIM}Total votes from this station: {len(station_votes)}{RESET}")
            
            if not station_votes:
                info("No votes from this station.")
                continue
            
            for pos in poll["positions"]:
                print(f"\n  {BRIGHT_CYAN}{pos['position_title']}{RESET}")
                vote_counts = {}
                
                for vote in station_votes:
                    if vote["position_id"] == pos["position_id"] and not vote["abstained"]:
                        vote_counts[vote["candidate_id"]] = vote_counts.get(vote["candidate_id"], 0) + 1
                
                for candidate_id, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
                    cand = candidates.get(candidate_id, {})
                    print(f"    {cand.get('full_name', 'Unknown')}: {BOLD}{count}{RESET} votes")
            
            print()
        
        pause()
    
    def view_system_statistics(self):
        """Display comprehensive system statistics."""
        clear_screen()
        header("SYSTEM STATISTICS", THEME_ADMIN)
        
        candidates = self.data_store.get_all_candidates()
        voters = self.data_store.get_all_voters()
        polls = self.data_store.get_all_polls()
        stations = self.data_store.get_all_stations()
        votes = self.data_store.get_all_votes()
        admins = self.data_store.get_all_admins()
        
        subheader("Overview", THEME_ADMIN_ACCENT)
        print(f"  {BRIGHT_CYAN}Total Candidates:{RESET}   {len(candidates)}")
        print(f"  {BRIGHT_CYAN}Total Voters:{RESET}       {len(voters)}")
        print(f"  {BRIGHT_CYAN}Total Polls:{RESET}        {len(polls)}")
        print(f"  {BRIGHT_CYAN}Voting Stations:{RESET}    {len(stations)}")
        print(f"  {BRIGHT_CYAN}Administrators:{RESET}     {len(admins)}")
        print(f"  {BRIGHT_CYAN}Total Votes Cast:{RESET}   {len(votes)}")
        
        subheader("Voter Statistics", THEME_ADMIN_ACCENT)
        verified = sum(1 for voter in voters.values().values() if voter["is_verified"])
        unverified = len(voters) - verified
        active_voters = sum(1 for voter in voters.values().values() if voter["is_active"])
        
        print(f"  {GREEN}Verified:{RESET}      {verified}")
        print(f"  {YELLOW}Unverified:{RESET}    {unverified}")
        print(f"  {BRIGHT_GREEN}Active:{RESET}        {active_voters}")
        
        subheader("Poll Statistics", THEME_ADMIN_ACCENT)
        draft_polls = sum(1 for poll in polls.values().values() if poll["status"] == "draft")
        open_polls = sum(1 for poll in polls.values().values() if poll["status"] == "open")
        closed_polls = sum(1 for poll in polls.values().values() if poll["status"] == "closed")
        
        print(f"  {YELLOW}Draft:{RESET}    {draft_polls}")
        print(f"  {GREEN}Open:{RESET}     {open_polls}")
        print(f"  {RED}Closed:{RESET}   {closed_polls}")
        
        subheader("Voter Turnout", THEME_ADMIN_ACCENT)
        voters_who_voted = sum(1 for voter in voters.values().values() if len(voter.get("has_voted_in", [])) > 0)
        turnout = (voters_who_voted / len(voters) * 100) if voters else 0
        print(f"  {DIM}Voters who participated:{RESET}  {voters_who_voted} / {len(voters)} ({turnout:.1f}%)")
        
        subheader("Voters by Station", THEME_ADMIN_ACCENT)
        for station_id, station in stations.items():
            count = sum(1 for voter in voters.values().values() if voter["station_id"] == station_id)
            bar_len = min(count, 40)
            bar = f"{THEME_ADMIN}{'█' * bar_len}{RESET}"
            print(f"  {station['name']:<30} {bar} {count}")
        
        subheader("Candidates by Party", THEME_ADMIN_ACCENT)
        party_counts = {}
        for candidate in candidates.values().values():
            party_counts[candidate["party"]] = party_counts.get(candidate["party"], 0) + 1
        
        for party, count in sorted(party_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {party:<30} {BRIGHT_MAGENTA}{'█' * count}{RESET} {count}")
        
        subheader("Demographics", THEME_ADMIN_ACCENT)
        male = sum(1 for voter in voters.values().values() if voter["gender"] == "M")
        female = sum(1 for voter in voters.values().values() if voter["gender"] == "F")
        other = len(voters) - male - female
        
        print(f"  {DIM}Male:{RESET}    {male}")
        print(f"  {DIM}Female:{RESET}  {female}")
        print(f"  {DIM}Other:{RESET}   {other}")
        
        pause()
    
    def view_voter_turnout(self):
        """Display voter turnout analysis."""
        clear_screen()
        header("VOTER TURNOUT ANALYSIS", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        voters = self.data_store.get_all_voters()
        stations = self.data_store.get_all_stations()
        votes = self.data_store.get_all_votes()
        
        for poll_id, poll in polls.items():
            if poll["status"] in ["open", "closed"]:
                station_voters = sum(1 for voter in voters.values().values() if voter["station_id"] in poll.get("station_ids", []) and voter["is_verified"])
                actual_votes = poll["total_votes_cast"]
                turnout = (actual_votes / station_voters * 100) if station_voters > 0 else 0
                
                subheader(poll['title'], THEME_ADMIN_ACCENT)
                print(f"  {DIM}Eligible Voters:{RESET}  {station_voters}")
                print(f"  {DIM}Votes Cast:{RESET}       {actual_votes}")
                print(f"  {DIM}Turnout:{RESET}          {BOLD}{turnout:.1f}%{RESET}")
                
                bar_len = int(turnout / 2)
                bar = f"{GREEN}{'█' * bar_len}{GRAY}{'░' * (50 - bar_len)}{RESET}"
                print(f"  {bar}")
                print()
        
        pause()
