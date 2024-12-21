# Example SessionManager setup
class SessionManager:
    _user_session = None

    @staticmethod
    def set_user(user_data):
        """Set user data after login."""
        SessionManager._user_session = user_data

    @staticmethod
    def get_user():
        """Get current user session."""
        return SessionManager._user_session


    @staticmethod
    def clear_user():
        """Clears the current user session."""
        SessionManager._current_user = None
