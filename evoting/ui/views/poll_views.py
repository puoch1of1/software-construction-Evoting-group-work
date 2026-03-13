"""
Poll views - display logic for poll/election screens.
"""

import datetime
from ..console import (
    clear_screen, header, subheader, table_header, table_divider,
    error, success, warning, info, menu_item, status_badge, prompt, pause
)
from ..colors import (
    RESET, BOLD, DIM, GREEN, YELLOW, RED,
    THEME_ADMIN, THEME_ADMIN_ACCENT, THEME_VOTER, THEME_VOTER_ACCENT,
    BRIGHT_GREEN, GRAY, ITALIC, BRIGHT_WHITE, BRIGHT_CYAN, BRIGHT_YELLOW
)
from ...config import MIN_CANDIDATE_AGE


class PollViews:
    """Handles poll-related UI rendering."""
    
    def __init__(self, poll_service, position_service, station_service, candidate_service, data_store):
        self.poll_service = poll_service
        self.position_service = position_service
        self.station_service = station_service
        self.candidate_service = candidate_service
        self.data_store = data_store
    
    def create_poll(self, current_user):
        """Display create poll form."""
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        
        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")
        
        try:
            sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd:
                error("End date must be after start date.")
                pause()
                return
        except ValueError:
            error("Invalid date format.")
            pause()
            return
        
        positions = self.position_service.get_all_positions()
        if not positions:
            error("No positions available. Create positions first.")
            pause()
            return
        
        subheader("Available Positions", THEME_ADMIN_ACCENT)
        active_positions = {poll_id: poll for poll_id, poll in positions.items() if poll["is_active"]}
        
        if not active_positions:
            error("No active positions.")
            pause()
            return
        
        for poll_id, poll in active_positions.items():
            print(f"    {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['level']}) - {poll['max_winners']} seat(station){RESET}")
        
        try:
            selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        poll_positions = []
        for spid in selected_position_ids:
            if spid not in active_positions:
                warning(f"Position ID {spid} not found or inactive. Skipping.")
                continue
            poll_positions.append({
                "position_id": spid,
                "position_title": positions[spid]["title"],
                "candidate_ids": [],
                "max_winners": positions[spid]["max_winners"]
            })
        
        if not poll_positions:
            error("No valid positions selected.")
            pause()
            return
        
        stations = self.station_service.get_all_stations()
        if not stations:
            error("No voting stations. Create stations first.")
            pause()
            return
        
        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        active_stations = {station_id: station for station_id, station in stations.items() if station["is_active"]}
        
        for station_id, station in active_stations.items():
            print(f"    {THEME_ADMIN}{station['id']}.{RESET} {station['name']} {DIM}({station['location']}){RESET}")
        
        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                error("Invalid input.")
                pause()
                return
        
        success_flag, result = self.poll_service.create_poll(
            title=title,
            description=description,
            election_type=election_type,
            start_date=start_date,
            end_date=end_date,
            poll_positions=poll_positions,
            station_ids=selected_station_ids,
            created_by=current_user["username"]
        )
        
        if success_flag:
            print()
            success(f"Poll '{title}' created! ID: {result}")
            warning("Status: DRAFT - Assign candidates and then open the poll.")
            self.data_store.save()
        else:
            error(result)
        pause()
    
    def view_all_polls(self):
        """Display all polls."""
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        for poll_id, poll in polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll['status'].upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll['start_date']} to {poll['end_date']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            
            for pos in poll["positions"]:
                cand_names = [candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in candidates]
                cand_display = ', '.join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {cand_display}")
        
        print(f"\n  {DIM}Total Polls: {len(polls)}{RESET}")
        pause()
    
    def update_poll(self, current_user):
        """Display update poll form."""
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        print()
        for poll_id, poll in polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {sc}({poll['status']}){RESET}")
        
        try:
            poll_id = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if poll_id not in polls:
            error("Poll not found.")
            pause()
            return
        
        poll = polls[poll_id]
        
        if poll["status"] == "open":
            error("Cannot update an open poll. Close it first.")
            pause()
            return
        
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            error("Cannot update a poll with votes.")
            pause()
            return
        
        print(f"\n  {BOLD}Updating: {poll['title']}{RESET}")
        info("Press Enter to keep current value\n")
        
        updates = {}
        
        new_title = prompt(f"Title [{poll['title']}]: ")
        if new_title:
            updates["title"] = new_title
        
        new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
        if new_desc:
            updates["description"] = new_desc
        
        new_type = prompt(f"Election Type [{poll['election_type']}]: ")
        if new_type:
            updates["election_type"] = new_type
        
        new_start = prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                datetime.datetime.strptime(new_start, "%Y-%m-%d")
                updates["start_date"] = new_start
            except ValueError:
                warning("Invalid date, keeping old value.")
        
        new_end = prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                datetime.datetime.strptime(new_end, "%Y-%m-%d")
                updates["end_date"] = new_end
            except ValueError:
                warning("Invalid date, keeping old value.")
        
        if updates:
            success_flag, err = self.poll_service.update_poll(
                poll_id, updates, current_user["username"]
            )
            if success_flag:
                print()
                success("Poll updated!")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def delete_poll(self, current_user):
        """Display delete poll confirmation."""
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        print()
        for poll_id, poll in polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        
        try:
            poll_id = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if poll_id not in polls:
            error("Poll not found.")
            pause()
            return
        
        poll = polls[poll_id]
        
        if poll["status"] == "open":
            error("Cannot delete an open poll. Close it first.")
            pause()
            return
        
        if poll["total_votes_cast"] > 0:
            warning(f"This poll has {poll['total_votes_cast']} votes recorded.")
        
        if prompt(f"Confirm deletion of '{poll['title']}'? (yes/no): ").lower() == "yes":
            success_flag, err = self.poll_service.delete_poll(poll_id, current_user["username"])
            if success_flag:
                print()
                success(f"Poll '{poll['title']}' deleted.")
                self.data_store.save()
            else:
                error(err)
        
        pause()
    
    def open_close_poll(self, current_user):
        """Display open/close poll interface."""
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        print()
        for poll_id, poll in polls.items():
            sc = GREEN if poll['status'] == 'open' else (YELLOW if poll['status'] == 'draft' else RED)
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']}  {sc}{BOLD}{poll['status'].upper()}{RESET}")
        
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
        
        if poll["status"] == "draft":
            if not any(pos["candidate_ids"] for pos in poll["positions"]):
                error("Cannot open - no candidates assigned.")
                pause()
                return
            
            if prompt(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                self.data_store.update_poll(poll_id, poll)
                self.data_store.log_action("OPEN_POLL", current_user["username"], f"Opened poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now OPEN for voting!")
                self.data_store.save()
        
        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): ").lower() == "yes":
                poll["status"] = "closed"
                self.data_store.update_poll(poll_id, poll)
                self.data_store.log_action("CLOSE_POLL", current_user["username"], f"Closed poll: {poll['title']}")
                print()
                success(f"Poll '{poll['title']}' is now CLOSED.")
                self.data_store.save()
        
        elif poll["status"] == "closed":
            info("This poll is already closed.")
            if prompt("Reopen it? (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                self.data_store.update_poll(poll_id, poll)
                self.data_store.log_action("REOPEN_POLL", current_user["username"], f"Reopened poll: {poll['title']}")
                print()
                success("Poll reopened!")
                self.data_store.save()
        
        pause()
    
    def assign_candidates_to_poll(self, current_user):
        """Display candidate assignment interface."""
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        positions = self.data_store.get_all_positions()
        
        if not polls:
            print()
            info("No polls found.")
            pause()
            return
        
        if not candidates:
            print()
            info("No candidates found.")
            pause()
            return
        
        print()
        for poll_id, poll in polls.items():
            print(f"  {THEME_ADMIN}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['status']}){RESET}")
        
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
        
        if poll["status"] == "open":
            error("Cannot modify candidates of an open poll.")
            pause()
            return
        
        for i, pos in enumerate(poll["positions"]):
            subheader(f"Position: {pos['position_title']}", THEME_ADMIN_ACCENT)
            
            current_cands = [f"{ccid}: {candidates[ccid]['full_name']}" for ccid in pos["candidate_ids"] if ccid in candidates]
            if current_cands:
                print(f"  {DIM}Current:{RESET} {', '.join(current_cands)}")
            else:
                info("No candidates assigned yet.")
            
            active_candidates = {candidate_id: candidate for candidate_id, candidate in candidates.items() if candidate["is_active"] and candidate["is_approved"]}
            pos_data = positions.get(pos["position_id"], {})
            min_age = pos_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
            eligible = {candidate_id: candidate for candidate_id, candidate in active_candidates.items() if candidate["age"] >= min_age}
            
            if not eligible:
                info("No eligible candidates found.")
                continue
            
            subheader("Available Candidates", THEME_ADMIN)
            for candidate_id, candidate in eligible.items():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if candidate_id in pos["candidate_ids"] else ""
                print(f"    {THEME_ADMIN}{candidate['id']}.{RESET} {candidate['full_name']} {DIM}({candidate['party']}) - Age: {candidate['age']}, Edu: {candidate['education']}{RESET}{marker}")
            
            if prompt(f"\nModify candidates for {pos['position_title']}? (yes/no): ").lower() == "yes":
                try:
                    new_cand_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    valid_ids = []
                    for ncid in new_cand_ids:
                        if ncid in eligible:
                            valid_ids.append(ncid)
                        else:
                            warning(f"Candidate {ncid} not eligible. Skipping.")
                    pos["candidate_ids"] = valid_ids
                    success(f"{len(valid_ids)} candidate(station) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        
        self.data_store.update_poll(poll_id, poll)
        self.data_store.log_action("ASSIGN_CANDIDATES", current_user["username"], f"Updated candidates for poll: {poll['title']}")
        self.data_store.save()
        pause()
    
    def view_open_polls_voter(self, current_user):
        """Display open polls for voters."""
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        
        open_polls = {poll_id: poll for poll_id, poll in polls.items() if poll["status"] == "open"}
        
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return
        
        for poll_id, poll in open_polls.items():
            already_voted = poll_id in current_user.get("has_voted_in", [])
            vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll['id']}: {poll['title']}{RESET}{vs}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Period:{RESET} {poll['start_date']} to {poll['end_date']}")
            
            for pos in poll["positions"]:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos['position_title']}{RESET}")
                for ccid in pos["candidate_ids"]:
                    if ccid in candidates:
                        candidate = candidates[ccid]
                        print(f"      {DIM}•{RESET} {candidate['full_name']} {DIM}({candidate['party']}) │ Age: {candidate['age']} │ Edu: {candidate['education']}{RESET}")
        
        pause()
    
    def cast_vote(self, current_user, voting_service):
        """Display voting interface."""
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        
        open_polls = {poll_id: poll for poll_id, poll in polls.items() if poll["status"] == "open"}
        
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return
        
        available_polls = {}
        for poll_id, poll in open_polls.items():
            if poll_id not in current_user.get("has_voted_in", []) and current_user["station_id"] in poll["station_ids"]:
                available_polls[poll_id] = poll
        
        if not available_polls:
            print()
            info("No available polls to vote in.")
            pause()
            return
        
        subheader("Available Polls", THEME_VOTER_ACCENT)
        for poll_id, poll in available_polls.items():
            print(f"  {THEME_VOTER}{poll['id']}.{RESET} {poll['title']} {DIM}({poll['election_type']}){RESET}")
        
        try:
            poll_id = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        
        if poll_id not in available_polls:
            error("Invalid poll selection.")
            pause()
            return
        
        poll = polls[poll_id]
        print()
        header(f"Voting: {poll['title']}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")
        
        my_votes = []
        
        for pos in poll["positions"]:
            subheader(pos['position_title'], THEME_VOTER_ACCENT)
            
            if not pos["candidate_ids"]:
                info("No candidates for this position.")
                continue
            
            for idx, ccid in enumerate(pos["candidate_ids"], 1):
                if ccid in candidates:
                    candidate = candidates[ccid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {candidate['full_name']} {DIM}({candidate['party']}){RESET}")
                    print(f"       {DIM}Age: {candidate['age']} │ Edu: {candidate['education']} │ Exp: {candidate['years_experience']} yrs{RESET}")
                    if candidate["manifesto"]:
                        print(f"       {ITALIC}{DIM}{candidate['manifesto'][:80]}...{RESET}")
            
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")
            
            try:
                vote_choice = int(prompt(f"\nYour choice for {pos['position_title']}: "))
            except ValueError:
                warning("Invalid input. Skipping.")
                vote_choice = 0
            
            if vote_choice == 0:
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": None,
                    "abstained": True
                })
            elif 1 <= vote_choice <= len(pos["candidate_ids"]):
                selected_cid = pos["candidate_ids"][vote_choice - 1]
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": selected_cid,
                    "candidate_name": candidates[selected_cid]["full_name"],
                    "abstained": False
                })
            else:
                warning("Invalid choice. Marking as abstain.")
                my_votes.append({
                    "position_id": pos["position_id"],
                    "position_title": pos["position_title"],
                    "candidate_id": None,
                    "abstained": True
                })
        
        subheader("VOTE SUMMARY", BRIGHT_WHITE)
        for mv in my_votes:
            if mv["abstained"]:
                print(f"  {mv['position_title']}: {GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {mv['position_title']}: {BRIGHT_GREEN}{BOLD}{mv['candidate_name']}{RESET}")
        
        print()
        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            info("Vote cancelled.")
            pause()
            return
        
        success_flag, result = voting_service.cast_vote(current_user, poll_id, my_votes)
        
        if success_flag:
            print()
            success("Your vote has been recorded successfully!")
            print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{result}{RESET}")
            print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
            self.data_store.save()
        else:
            error(result)
        
        pause()
    
    def view_voting_history(self, current_user, voting_service):
        """Display voter'station voting history."""
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        votes = self.data_store.get_all_votes()
        
        voted_polls = current_user.get("has_voted_in", [])
        
        if not voted_polls:
            print()
            info("You have not voted in any polls yet.")
            pause()
            return
        
        print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(station):{RESET}\n")
        
        for poll_id in voted_polls:
            if poll_id in polls:
                poll = polls[poll_id]
                sc = GREEN if poll['status'] == 'open' else RED
                print(f"  {BOLD}{THEME_VOTER}Poll #{poll_id}: {poll['title']}{RESET}")
                print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Status:{RESET} {sc}{poll['status'].upper()}{RESET}")
                
                for vr in [v for v in votes if v["poll_id"] == poll_id and v["voter_id"] == current_user["id"]]:
                    pos_title = next(
                        (pos["position_title"] for pos in poll.get("positions", []) if pos["position_id"] == vr["position_id"]),
                        "Unknown"
                    )
                    if vr["abstained"]:
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                    else:
                        print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{candidates.get(vr['candidate_id'], {}).get('full_name', 'Unknown')}{RESET}")
                print()
        
        pause()
    
    def view_closed_poll_results_voter(self):
        """Display results for closed polls (voter view)."""
        clear_screen()
        header("ELECTION RESULTS", THEME_VOTER)
        polls = self.data_store.get_all_polls()
        candidates = self.data_store.get_all_candidates()
        votes = self.data_store.get_all_votes()
        
        closed_polls = {poll_id: poll for poll_id, poll in polls.items() if poll["status"] == "closed"}
        
        if not closed_polls:
            print()
            info("No closed polls with results.")
            pause()
            return
        
        for poll_id, poll in closed_polls.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll['title']}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll['election_type']}  {DIM}│  Votes:{RESET} {poll['total_votes_cast']}")
            
            for pos in poll["positions"]:
                subheader(pos['position_title'], THEME_VOTER_ACCENT)
                vote_counts = {}
                abstain_count = 0
                
                for v in votes:
                    if v["poll_id"] == poll_id and v["position_id"] == pos["position_id"]:
                        if v["abstained"]:
                            abstain_count += 1
                        else:
                            vote_counts[v["candidate_id"]] = vote_counts.get(v["candidate_id"], 0) + 1
                
                total = sum(vote_counts.values()) + abstain_count
                
                from ..colors import BG_GREEN, BLACK
                
                for rank, (candidate_id, count) in enumerate(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1):
                    cand = candidates.get(candidate_id, {})
                    pct = (count / total * 100) if total > 0 else 0
                    bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos["max_winners"] else ""
                    print(f"    {BOLD}{rank}. {cand.get('full_name', '?')}{RESET} {DIM}({cand.get('party', '?')}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                
                if abstain_count > 0:
                    print(f"    {GRAY}Abstained: {abstain_count} ({(abstain_count / total * 100) if total > 0 else 0:.1f}%){RESET}")
        
        pause()
