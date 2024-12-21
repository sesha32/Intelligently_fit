class SessionManager:
    _user_data = None  # Class-level variable to store user session data

    @classmethod
    def set_user(cls, user_data):
        """Set user data in the session."""
        if user_data:
            cls._user_data = user_data  # Store the session data
        else:
            raise ValueError("User data cannot be None.")

    @classmethod
    def get_user(cls):
        """Retrieve full user data from the session."""
        if cls._user_data:
            return cls._user_data  # Return the stored session data
        else:
            print("No user data found in the session.")
            return None  # Return None if no session is found

    @classmethod
    def clear_session(cls):
        """Clear the session data."""
        cls._user_data = None  # Reset the session data

# Usage example:
# Set user data after login
user_data = {
    'id': 9,
    'first_name': 'dhanam',
    'last_name': 'boddepalli',
    'email': 'dhanam@gmail.com',
    'mobile': '9876543210',
    'date_of_birth': '1990-01-01',
    'gender': 'female',
    'weight': '60',
    'height': '165'
}
SessionManager.set_user(user_data)

# Get user data
user_session = SessionManager.get_user()
print(user_session)

# Clear session data
SessionManager.clear_session()
