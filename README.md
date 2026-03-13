# National E-Voting System

## Professional Documentation

**Version:** 2.1.0  
**Date:** March 2026  
**Platform:** Console-based Python Application  
**Course:** Software Construction - Uganda Christian University

---

## Table of Contents

1. [Development Team](#development-team)
2. [Executive Summary](#1-executive-summary)
3. [System Overview](#2-system-overview)
4. [Architecture](#3-architecture)
5. [Module Documentation](#4-module-documentation)
6. [Features & Functionality](#5-features--functionality)
7. [Security Considerations](#6-security-considerations)
8. [Data Management](#7-data-management)
9. [Refactoring Improvements](#8-refactoring-improvements)
10. [Installation & Usage](#9-installation--usage)
11. [API Reference](#10-api-reference)

---

## Development Team

The E-Voting System was developed by a team of five professional software engineers:

| Name | Reg No. |
|------|---------|
| Lufene Mark Travis | [S23B23/032] |
| Ezamamti Ronald Austine  | [S23B23/018] |
| Allan Kagimu Sebatta | [S23B23/057] |
| Puoch Mabor Makuei  | [S23B23/O55] |
| Ariko Ethan | [S23b23/007] |

**Institution:** Uganda Christian University  
**Course:** Software Construction

---

## 1. Executive Summary

The **National E-Voting System** is a comprehensive console-based electronic voting application designed to facilitate secure, transparent, and democratic elections. The system supports the complete electoral lifecycle from candidate registration through vote casting to results tabulation.

### Key Capabilities

- Multi-role authentication (Administrators & Voters)
- End-to-end election management
- Real-time vote tallying with visual representation
- Complete audit trail for transparency
- Secure password handling with SHA-256 hashing

### Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| Data Storage | JSON (file-based) |
| UI | ANSI Terminal Colors |
| Security | SHA-256 Hashing |

---

## 2. System Overview

### 2.1 Purpose

The system addresses the need for a transparent, accessible, and secure voting mechanism that can be deployed in environments without requiring complex infrastructure.

### 2.2 Scope

The application covers:

- **Candidate Management:** Registration, verification, and tracking of electoral candidates
- **Voter Management:** Registration, verification, and authentication of eligible voters
- **Polling Station Management:** Setup and administration of voting locations
- **Position Management:** Definition of electoral offices/positions
- **Poll/Election Management:** Creation and lifecycle management of elections
- **Vote Casting:** Secure ballot submission with duplicate prevention
- **Results Reporting:** Real-time statistics and visual result representation
- **Audit Logging:** Comprehensive activity tracking

### 2.3 User Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| **Super Admin** | Full system access, can manage other admins | Highest |
| **Election Officer** | Manages elections, candidates, results | High |
| **Station Manager** | Manages specific voting station operations | Medium |
| **Auditor** | Read-only access to logs and reports | Limited |
| **Voter** | Can register, vote, view results | Standard |

---

## 3. Architecture

### 3.1 Architectural Pattern

The system follows a **Layered Architecture** combined with the **Repository Pattern** and **Service Layer Pattern**.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Menus     │  │   Views     │  │   Console/Colors    │  │
│  │ (Navigation)│  │ (Rendering) │  │   (UI Primitives)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ AuthService  │  │ VotingService│  │ StatisticsService│   │
│  │ VoterService │  │ PollService  │  │ AuditService     │   │
│  │ AdminService │  │ CandidateServ│  │ StationService   │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   REPOSITORY LAYER                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    DataStore                         │    │
│  │   (Centralized data access, CRUD operations)        │    │
│  └────────────────────────┬────────────────────────────┘    │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               evoting_data.json                      │    │
│  │   (Persistent storage: candidates, voters, polls,   │    │
│  │    stations, positions, votes, admins, audit log)   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Directory Structure

```
evoting/
├── __init__.py              # Package initialization
├── config.py                # Configuration constants (no magic numbers)
├── main.py                  # Application entry point with DI
├── utils.py                 # Shared utility helpers (e.g., apply_updates)
│
├── models/                  # Data Transfer Objects
│   ├── __init__.py
│   ├── admin.py             # Admin model
│   ├── candidate.py         # Candidate model
│   ├── poll.py              # Poll/Election model
│   ├── position.py          # Electoral position model
│   ├── vote.py              # Vote record model
│   ├── voter.py             # Voter model
│   └── voting_station.py    # Voting station model
│
├── repositories/            # Data Access Layer
│   ├── __init__.py
│   └── data_store.py        # Centralized JSON persistence
│
├── services/                # Business Logic Layer
│   ├── __init__.py
│   ├── admin_service.py     # Admin management
│   ├── audit_service.py     # Audit log operations
│   ├── auth_service.py      # Authentication
│   ├── candidate_service.py # Candidate CRUD
│   ├── poll_service.py      # Poll lifecycle
│   ├── position_service.py  # Position management
│   ├── station_service.py   # Station management
│   ├── statistics_service.py# Results & analytics
│   ├── voter_service.py     # Voter management
│   └── voting_service.py    # Vote casting
│
├── ui/                      # Presentation Layer
│   ├── __init__.py
│   ├── colors.py            # ANSI color definitions
│   ├── console.py           # Display helper functions
│   ├── input_handler.py     # Secure input handling
│   │
│   ├── menus/               # Navigation Controllers
│   │   ├── __init__.py
│   │   ├── main_menu.py     # Entry point menu
│   │   ├── admin_menu.py    # Admin dashboard
│   │   └── voter_menu.py    # Voter dashboard
│   │
│   └── views/               # View Renderers
│       ├── __init__.py
│       ├── admin_views.py   # Admin management screens
│       ├── candidate_views.py# Candidate screens
│       ├── poll_views.py    # Poll/election screens
│       ├── position_views.py# Position screens
│       ├── results_views.py # Results & statistics
│       ├── station_views.py # Station screens
│       └── voter_views.py   # Voter screens
│
└── validators/              # Validation Utilities
    ├── __init__.py
    └── validators.py        # Date, age, password validation
```

### 3.3 Design Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility (SRP)** | Each class/module has one reason to change |
| **Open/Closed Principle (OCP)** | Services can be extended without modification |
| **Dependency Inversion (DIP)** | High-level modules depend on abstractions |
| **Separation of Concerns** | UI, business logic, and data access are isolated |
| **DRY (Don't Repeat Yourself)** | Common functionality extracted to utilities |
| **KISS (Keep It Simple)** | Straightforward implementations without over-engineering |

---

## 4. Module Documentation

### 4.1 Configuration Module (`config.py`)

Centralizes all system constants and configuration values to avoid magic numbers across the codebase.

```python
# Key configurations
MIN_VOTER_AGE = 18          # Minimum voting age
MIN_CANDIDATE_AGE = 25      # Minimum age for candidates
MAX_CANDIDATE_AGE = 75      # Maximum age for candidates
VOTER_CARD_LENGTH = 12      # Voter card number format
MIN_PASSWORD_LENGTH = 6     # Password security requirement
VOTE_HASH_LENGTH = 16       # Characters of SHA-256 hash shown on receipt
HEADER_WIDTH = 58           # Character width of header/footer borders

# Age groups for demographics
AGE_GROUPS = [
    (18, 25, "18-25"),
    (26, 35, "26-35"),
    # ...
]

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
# ...

# Education requirements for candidates
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate"
]

# Administrative roles
ADMIN_ROLES = [
    "super_admin",
    "election_officer",
    "station_manager",
    "auditor"
]
```

### 4.2 Models Layer

Each model provides:
- Data structure definition
- `to_dict()` method for serialization
- `from_dict()` class method for deserialization

**Example: Candidate Model**

```python
class Candidate:
    def __init__(self, id, full_name, national_id, date_of_birth, age,
                 gender, education, party, manifesto, address, phone,
                 email, has_criminal_record, years_experience,
                 created_at, created_by, is_active=True, is_approved=True):
        self.id = id
        self.full_name = full_name
        # ... additional fields
    
    def to_dict(self):
        return { ... }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
```

### 4.3 Repository Layer (`DataStore`)

The `DataStore` class provides:

- **Data Loading:** `load()` - Read from JSON file
- **Data Persistence:** `save()` - Write to JSON file
- **CRUD Operations:** Get, add, update, delete for all entities
- **Audit Logging:** `log_action()` - Record all activities
- **Initialization:** Auto-create default admin on first run

**Key Methods:**

| Method | Description |
|--------|-------------|
| `get_all_candidates()` | Retrieve all candidates |
| `add_candidate(candidate)` | Add new candidate |
| `update_candidate(id, data)` | Modify existing candidate |
| `get_voter(id)` | Get specific voter |
| `log_action(action, user, details)` | Record audit entry |

### 4.4 Service Layer

Each service encapsulates business logic for a specific domain:

| Service | Responsibilities |
|---------|-----------------|
| `AuthService` | Login validation, session management |
| `CandidateService` | Candidate CRUD, eligibility checks |
| `VoterService` | Registration, verification, password changes |
| `StationService` | Station management |
| `PositionService` | Electoral position management |
| `PollService` | Election lifecycle (draft → open → closed) |
| `VotingService` | Ballot casting, duplicate prevention |
| `StatisticsService` | Results calculation, analytics |
| `AuditService` | Log filtering and retrieval |
| `AdminService` | Administrator management |

### 4.5 Presentation Layer

**Colors Module (`colors.py`):**
Defines ANSI escape codes for consistent theming:
- Text styles: Bold, Dim, Italic, Underline
- Foreground colors: Standard and bright variants
- Background colors
- Theme presets: Admin (green), Voter (blue)

**Console Module (`console.py`):**
UI helper functions:
- `header()`, `subheader()` - Section headers
- `table_header()`, `table_divider()` - Table formatting
- `error()`, `success()`, `warning()`, `info()` - Status messages
- `menu_item()` - Consistent menu rendering
- `status_badge()` - Active/Inactive indicators
- `prompt()` - User input with styling
- `clear_screen()`, `pause()` - Screen management

**Input Handler (`input_handler.py`):**
- `masked_input()` - Password input with asterisk masking

### 4.6 Utility Module (`utils.py`)

Contains shared helper functions to enforce DRY principles across services.
- `apply_updates(entity, updates)` - Safely applies dictionary updates (ignoring `None` and empty strings), eliminating duplicate loops across 5 service modules.

---

## 5. Features & Functionality

### 5.1 Candidate Management

| Feature | Description |
|---------|-------------|
| Create Candidate | Register with full details, eligibility checks |
| View All | Table display with status badges |
| Update | Modify candidate information |
| Delete/Deactivate | Soft delete with active poll protection |
| Search | By name, party, education, age range |

**Eligibility Rules:**
- Age: 25-75 years
- Education: Bachelor's degree or higher
- Criminal Record: Must have none
- National ID: Must be unique

### 5.2 Voter Management

| Feature | Description |
|---------|-------------|
| Self-Registration | Voters register themselves |
| Admin Verification | Admin must verify before voting |
| Profile View | Personal details and voting history |
| Password Change | Self-service password update |
| Search | By name, card number, national ID, station |

**Registration Flow:**
1. Voter submits details
2. System generates unique Voter Card Number
3. Admin verifies voter identity
4. Voter can now participate in elections

### 5.3 Voting Station Management

| Feature | Description |
|---------|-------------|
| Create Station | Name, location, capacity, supervisor |
| View All | List with registered voter counts |
| Update | Modify station details |
| Deactivate | Soft delete with voter warning |

### 5.4 Position Management

| Feature | Description |
|---------|-------------|
| Create Position | Title, level, seats, term length |
| View All | Tabular display |
| Update | Modify position details |
| Deactivate | With active poll protection |

### 5.5 Poll/Election Management

**Poll Lifecycle:**

```
┌───────────┐         ┌───────────┐         ┌───────────┐
│   DRAFT   │────────▶│    OPEN   │────────▶│  CLOSED   │
│           │         │           │         │           │
│ Configure │         │  Voting   │         │  Results  │
│ candidates│         │  allowed  │         │  final    │
└───────────┘         └───────────┘         └───────────┘
                           │                      │
                           └──────────────────────┘
                                 (can reopen)
```

| Feature | Description |
|---------|-------------|
| Create Poll | Title, dates, positions, stations |
| Assign Candidates | Link candidates to positions |
| Open Poll | Enable voting |
| Close Poll | Stop voting, finalize results |
| View Results | Bar charts, percentages, winners |

### 5.6 Vote Casting

**Voting Process:**
1. Voter logs in with card number and password
2. Views available polls (verified voters only)
3. Selects candidates for each position (or abstains)
4. Reviews vote summary
5. Confirms submission
6. Receives vote reference number

**Security Features:**
- One vote per poll per voter
- Station assignment validation
- Verification requirement
- Audit trail recording

### 5.7 Results & Statistics

| Report | Content |
|--------|---------|
| Poll Results | Bar chart visualization, vote counts, percentages, winner badges |
| Results by Station | Breakdown per voting location |
| System Statistics | Totals, turnout, demographics |
| Voter Turnout | Participation rates per poll |

### 5.8 Audit Logging

Every significant action is recorded:
- Timestamp
- Action type (LOGIN, CREATE_CANDIDATE, CAST_VOTE, etc.)
- User who performed the action
- Details/context

---

## 6. Security Considerations

### 6.1 Password Security

- **Hashing:** SHA-256 one-way hash
- **Minimum Length:** 6 characters
- **Masked Input:** Asterisks displayed during entry

### 6.2 Access Control

- Role-based permissions
- Session management via login/logout
- Voter verification requirement

### 6.3 Data Integrity

- Duplicate prevention (National ID, Voter Card)
- Age validation at registration time
- Criminal record disqualification

### 6.4 Audit Trail

- All actions logged with timestamps
- User attribution for accountability
- Cannot be modified by users

---

## 7. Data Management

### 7.1 Data File Structure

```json
{
  "candidates": {
    "1": { "id": 1, "full_name": "...", ... }
  },
  "voters": {
    "1": { "id": 1, "full_name": "...", "password_hash": "...", ... }
  },
  "admins": {
    "1": { "id": 1, "username": "admin", "password_hash": "...", ... }
  },
  "voting_stations": { ... },
  "positions": { ... },
  "polls": { ... },
  "votes": [ ... ],
  "audit_log": [ ... ],
  "next_ids": {
    "candidate": 2,
    "voter": 2,
    "station": 2,
    ...
  }
}
```

### 7.2 Backup & Recovery

To reset the system:
1. Delete `evoting_data.json`
2. Restart application
3. Default admin account is auto-created

### 7.3 Data Export

Admin can export:
- Full system data
- Voters only (without passwords)
- Poll results
- Audit log

---

## 8. Refactoring Improvements

### 8.1 Before vs After Comparison

| Aspect | Before (v1.0) | After (v2.0) |
|--------|---------------|--------------|
| File Count | 1 monolithic file (1600+ lines) | 30+ focused modules |
| Code Organization | All in one file | Layered architecture |
| Functions | Global functions | Class methods |
| Data Storage | Global dictionaries | Repository pattern |
| Configuration | Magic numbers inline | Centralized config.py |
| UI Code | Mixed with logic | Separated into views |
| Reusability | Copy-paste patterns | DRY principles |
| Variable Naming | Single-letter (`v`, `c`) | Descriptive (`voter`, `candidate`) |
| Testing | Difficult to test | Unit-testable services |
| Maintainability | Low | High |

### 8.2 Specific Improvements

#### Code Structure
- **Modular Design:** Split into 7 packages (models, repositories, services, ui, validators, etc.)
- **Class-Based:** 20+ classes instead of procedural functions
- **Package Organization:** Proper `__init__.py` files with controlled exports

#### Separation of Concerns
- **Models:** Pure data structures with serialization
- **Repositories:** Data access abstracted behind `DataStore`
- **Services:** Business logic isolated from UI
- **Views:** Display logic separated from navigation
- **Menus:** Navigation logic independent of rendering

#### Configuration Management
- All constants moved to `config.py`
- No more magic numbers or strings deep in logic code (e.g. age boundaries, vote hash lengths)
- Easy to modify system parameters

#### Code Quality Improvements (v2.1.0 Audit)
- **DRY Verification**: Extracted identical dict-updating `for` loops from 5 services into a single modular `apply_updates` helper in `utils.py`.
- **Removed Redundancies**: Removed legacy alias methods (`authenticate_admin`, `save_data`) in favour of canonical direct method names (`login_admin`, `save`).
- **Audit Correctness**: Fixed a state-handling bug in `poll_service.py` to correctly differentiate `OPEN_POLL` vs `REOPEN_POLL` audit actions.
- **Descriptive Variables**: Refactored hundreds of poorly named single-letter loop/comprehension variables (`v`, `c`, `p`, `s`) across 16 files into their professional, self-documenting equivalents (`voter`, `candidate`, `poll`, `station`).

#### UI Improvements
- Consistent color theming via `colors.py`
- Reusable UI primitives in `console.py`
- Secure password input with masking

#### Error Handling
- Service methods return `(success, result/error)` tuples
- Graceful error display to users
- Input validation at entry points

#### Dependency Injection
- Components initialized in `main.py`
- Dependencies passed via constructors
- Easy to substitute implementations

### 8.3 Design Patterns Applied

| Pattern | Application |
|---------|-------------|
| **Repository** | `DataStore` abstracts data access |
| **Service Layer** | Business logic in service classes |
| **Factory Method** | `from_dict()` class methods in models |
| **Dependency Injection** | Constructor injection in `main.py` |
| **Facade** | Menu classes simplify complex operations |

### 8.4 Maintainability Improvements

1. **Single Point of Change:** Modify behavior in one place
2. **Readable Code:** Meaningful names, docstrings
3. **Reduced Coupling:** Components communicate via defined interfaces
4. **High Cohesion:** Related functionality grouped together

### 8.5 What Remained Unchanged

Per requirements, the following were preserved exactly:
- All menu options and navigation flow
- User prompts and messages
- Output formatting (tables, headers, status badges)
- Business rules (age limits, verification, etc.)
- Data file format and compatibility
- Default admin credentials

---

## 9. Installation & Usage

### 9.1 Requirements

- Python 3.6 or higher
- Terminal with ANSI color support
- No external dependencies

### 9.2 Installation

```bash
# Clone or extract to desired location
cd c:\Users\DELL\Desktop\E-voting-App

# No additional installation needed
```

### 9.3 Running the Application

```bash
python evoting/main.py
```

### 9.4 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

---

## 10. API Reference

### 10.1 Service Method Signatures

#### AuthService

```python
authenticate_admin(username: str, password: str) -> Tuple[bool, Union[dict, str]]
authenticate_voter(voter_card: str, password: str) -> Tuple[bool, Union[dict, str]]
```

#### CandidateService

```python
create_candidate(**kwargs) -> Tuple[bool, Union[int, str]]
update_candidate(id: int, updates: dict, updated_by: str) -> Tuple[bool, str]
deactivate_candidate(id: int, deactivated_by: str) -> Tuple[bool, str]
search_by_name(term: str) -> List[dict]
search_by_party(term: str) -> List[dict]
search_by_education(education: str) -> List[dict]
search_by_age_range(min_age: int, max_age: int) -> List[dict]
```

#### VotingService

```python
cast_vote(voter: dict, poll_id: int, votes: List[dict]) -> Tuple[bool, str]
has_voter_voted_in_poll(voter_id: int, poll_id: int) -> bool
```

#### PollService

```python
create_poll(**kwargs) -> Tuple[bool, Union[int, str]]
update_poll(id: int, updates: dict, updated_by: str) -> Tuple[bool, str]
delete_poll(id: int, deleted_by: str) -> Tuple[bool, str]
```

### 10.2 Data Store Methods

```python
# CRUD Operations
get_all_candidates() -> Dict[int, dict]
add_candidate(candidate: dict) -> int
update_candidate(id: int, data: dict) -> None
get_candidate(id: int) -> Optional[dict]

# Similar patterns for voters, admins, stations, positions, polls

# Votes
add_vote(vote: dict) -> None
get_all_votes() -> List[dict]

# Audit
log_action(action: str, user: str, details: str) -> None
get_audit_log() -> List[dict]

# Persistence
save() -> None
load() -> None
```

---

## Appendix A: File Inventory

| File | Lines | Purpose |
|------|-------|---------|
| config.py | ~60 | Configuration constants |
| main.py | 75 | Entry point, DI setup |
| utils.py | ~25 | Shared helpers (apply_updates) |
| models/*.py | ~250 | 7 data models |
| repositories/data_store.py | ~350 | Data persistence |
| services/*.py | ~650 | 10 service classes |
| ui/colors.py | 50 | ANSI color definitions |
| ui/console.py | 100 | UI helper functions |
| ui/input_handler.py | 30 | Masked input |
| ui/views/*.py | ~1200 | 7 view classes |
| ui/menus/*.py | ~300 | 3 menu classes |
| validators/validators.py | 60 | Validation utilities |
| **Total** | **~3150** | Full application |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Poll** | An election or referendum event |
| **Position** | An office or role being contested |
| **Station** | A physical voting location |
| **Voter Card Number** | Unique identifier for voter authentication |
| **Verification** | Admin approval of voter registration |
| **Abstain** | Choice to not select any candidate |

---

**Document Version:** 1.0  
**Last Updated:** March 12, 2026  
**Author:** E-Voting Development Team
