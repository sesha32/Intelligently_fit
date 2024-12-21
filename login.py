import sqlite3
import bcrypt
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from session import SessionManager  # Correct import for SessionManager

Builder.load_file('kv/login.kv')

class LoginScreen(Screen):
    def validate_user(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if not username or not password:
            print("Please enter both email and password!")
            return

        try:
            conn = sqlite3.connect("streamsmart.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id, first_name, last_name, email, mobile, password, date_of_birth, height, weight, gender FROM users WHERE email=?", (username,))
            user_data = cursor.fetchone()

            if user_data:
                user_id, first_name, last_name, email, mobile, stored_password, date_of_birth, height, weight, gender = user_data

                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    print("Login successful!")

                    # Store user data in session
                    session_data = {
                        "id": user_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "mobile": mobile,
                        "date_of_birth": date_of_birth,
                        "height": height,
                        "weight": weight,
                        "gender": gender
                    }
                    SessionManager.set_user(session_data)  # Store session using SessionManager
                    print(f"Session Data: {SessionManager.get_user()}")

                    # Redirect based on user ID
                    if user_id in (1, 2):  # Admin IDs (1 and 2)
                        self.manager.current = "admindashboard"
                    else:  # Regular user
                        self.manager.current = "userdashboard"

                    # Clear input fields after successful login
                    self.ids.username.text = ""
                    self.ids.password.text = ""

                else:
                    print("Invalid password!")
            else:
                print("User not found!")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
