from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from login import LoginScreen
from registration import RegistrationScreen  # Assuming the class is defined in register.py
from admindashboard import AdminDashboardScreen
from userdashboard import UserDashBoardScreen

class StreamSmartApp(App):
    def build(self):
        # Create the ScreenManager and add screens
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))  # Login screen
        sm.add_widget(RegistrationScreen(name="registration"))
        sm.add_widget(AdminDashboardScreen(name='admindashboard'))  # Admin dashboard
        sm.add_widget(UserDashBoardScreen(name='userdashboard'))  # User dashboard
       
        return sm
    
    def forgot_password(self):
        # Switch to the forgot_password screen
        self.root.current = 'forgot_password'

    
if __name__ == '__main__':
    StreamSmartApp().run()
