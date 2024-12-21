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
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        email = self.ids.email.text
        mobile = self.ids.mobile.text
        date_of_birth = self.ids.date_of_birth.text
        height = self.ids.height.text  # Height as text
        weight = self.ids.weight.text  # Weight as text
        gender = self.ids.gender.text  # Gender as text
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text

        if password != confirm_password:
            print("Passwords do not match!")
            return

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Check if height and weight are valid integers
        try:
            height = int(height)
            weight = int(weight)
        except ValueError:
            print("Height and Weight must be valid integers!")
            return

        try:
            conn = sqlite3.connect("streamsmart.db")
            cursor = conn.cursor()

            # Inserting the user data into the database
            cursor.execute('''INSERT INTO users (first_name, last_name, email, mobile, date_of_birth, height, weight, gender, password)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (first_name, last_name, email, mobile, date_of_birth, height, weight, gender, hashed_password))

            conn.commit()
            conn.close()

            # Send OTP via email
            self.send_otp_email(email, otp)

            print("User registered successfully and OTP sent!")

            # Set user session
            # After successful registration, set user data into the session
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

    def send_otp_email(self, email, otp):
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
        except Exception as e:
            print(f"Error sending email: {e}")
