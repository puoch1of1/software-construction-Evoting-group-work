"""
Audit service - handles audit log operations.
"""


class AuditService:
    """Handles audit log operations."""
    
    def __init__(self, data_store):
        self.data_store = data_store
    
    def get_all_entries(self) -> list:
        """Get all audit log entries."""
        return self.data_store.get_audit_log()
    
    def get_last_n_entries(self, n: int) -> list:
        """Get the last N audit log entries."""
        return self.data_store.get_audit_log()[-n:]
    
    def filter_by_action(self, action_type: str) -> list:
        """Filter audit log by action type."""
        return [
            e for e in self.data_store.get_audit_log()
            if e["action"] == action_type
        ]
    
    def filter_by_user(self, user_filter: str) -> list:
        """Filter audit log by user."""
        user_filter = user_filter.lower()
        return [
            e for e in self.data_store.get_audit_log()
            if user_filter in e["user"].lower()
        ]
    
    def get_unique_action_types(self) -> list:
        """Get list of unique action types."""
        return list(set(e["action"] for e in self.data_store.get_audit_log()))
