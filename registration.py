from email.mime.text import MIMEText
import smtplib
import sqlite3
import bcrypt
import random
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from session import SessionManager  # Import the session manager

Builder.load_file('kv/registration.kv')

class RegistrationScreen(Screen):

    def register_user(self):
        first_name = self.ids.first_name.text.strip()
        last_name = self.ids.last_name.text.strip()
        email = self.ids.email.text.strip()
        mobile = self.ids.mobile.text.strip()
        date_of_birth = self.ids.date_of_birth.text.strip()
        height = self.ids.height.text.strip()
        weight = self.ids.weight.text.strip()
        gender = self.ids.gender.text.strip()
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        # Validate inputs
        if not all([first_name, last_name, email, mobile, date_of_birth, height, weight, gender, password, confirm_password]):
            print("All fields are required!")
            return

        if password != confirm_password:
            print("Passwords do not match!")
            return

        # Validate height and weight as integers
        try:
            height = int(height)
            weight = int(weight)
        except ValueError:
            print("Height and Weight must be valid integers!")
            return

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate OTP
        otp = random.randint(100000, 999999)

        try:
            conn = sqlite3.connect("streamsmart.db")
            cursor = conn.cursor()

            # Insert the user data into the database
            cursor.execute('''
                INSERT INTO users (first_name, last_name, email, mobile, date_of_birth, height, weight, gender, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, mobile, date_of_birth, height, weight, gender, hashed_password))

            conn.commit()

            # Send OTP via email
            self.send_otp_email(email, otp)

            print("User registered successfully and OTP sent!")

            # Set user session
            SessionManager.set_user({
                'id': cursor.lastrowid,  # Assuming your database assigns this automatically
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'mobile': mobile,
                'date_of_birth': date_of_birth,
                'height': height,
                'weight': weight,
                'gender': gender
            })

            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            print("This email is already registered!")
        except Exception as e:
            print(f"An error occurred during registration: {e}")
        finally:
            conn.close()

    def send_otp_email(self, email, otp):
        """Send an OTP to the user's email."""
        sender_email = "youremail@gmail.com"
        sender_password = "yourpassword"

        subject = "Your OTP Code"
        body = f"Your OTP code for registration is {otp}."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())
            print("OTP sent to email!")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")

    def switch_to_login(self):
        """Switch to the login screen."""
        self.manager.current = 'login'
