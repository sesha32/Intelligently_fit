import subprocess  # Import subprocess to call external scripts
import numpy as np
import csv
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from kivy.lang import Builder



class UserDashBoardScreen(Screen):
    def __init__(self, **kwargs):
        super(UserDashBoardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Hardcoded user data
        self.user_data = {
            'first_name': 'Dhana',
            'last_name': 'Boddepalli',
            'height': 158,  # in cm
            'weight': 50,   # in kg
            'gender': 'female',
            'date_of_birth': '1999-01-01'
        }

        # Add Close Button at the top of the screen
        self.close_button = Button(text="Go to Chatbot", size_hint_y=None, height=50)
        self.close_button.bind(on_press=self.redirect_to_chatbot)  # Bind to the redirect function
        self.layout.add_widget(self.close_button)

        # Greeting and BMI display
        self.bmi_label = Label(text="Hello!")
        self.layout.add_widget(self.bmi_label)

        self.bmi_value_label = Label(text="Your BMI: --")
        self.layout.add_widget(self.bmi_value_label)

        # Fitness suggestion button
        self.predict_button = Button(text="Get Fitness Suggestion")
        self.predict_button.bind(on_press=self.on_predict)
        self.layout.add_widget(self.predict_button)

        # Scrollable area for suggestions
        self.result_scroll = ScrollView(size_hint=(1, None), height=200)
        self.result_grid = GridLayout(cols=2, size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        self.result_scroll.add_widget(self.result_grid)
        self.layout.add_widget(self.result_scroll)

        # Score display
        self.score = 0
        self.score_label = Label(text="Your Score: 0")
        self.layout.add_widget(self.score_label)

        self.add_widget(self.layout)

        # Prepare the ML model
        self.model, self.label_encoder = self.prepare_model()

    def on_enter(self):
        """Called when the screen is displayed."""
        # Schedule the method to be called after the screen is fully initialized
        Clock.schedule_once(self.load_user_data, 0.1)

    def load_user_data(self, *args):
        """Load user data directly."""
        print(f"User data: {self.user_data}")

        # Update greeting and BMI
        self.bmi_label.text = f"Hello, {self.user_data['first_name']} {self.user_data['last_name']}"

        try:
            bmi = self.calculate_bmi()
            self.bmi_value_label.text = f"Your BMI: {bmi:.2f}"
        except (ZeroDivisionError, ValueError):
            self.bmi_value_label.text = "BMI cannot be calculated. Please check your height and weight."

    def calculate_bmi(self):
        """Calculate BMI using height (in cm) and weight (in kg)."""
        height = float(self.user_data['height']) / 100  # Convert height to meters
        weight = float(self.user_data['weight'])
        return weight / (height ** 2)

    def on_predict(self, instance):
        """Predict fitness suggestion based on user data."""
        bmi = self.calculate_bmi()
        gender = self.user_data['gender']
        age = self.calculate_age()

        # Encode gender input (Male = 1, Female = 0)
        gender_encoded = 1 if gender.lower() == 'male' else 0

        # Prepare input data for prediction
        input_data = np.array([[bmi, gender_encoded, age]])

        # Predict exercise suggestion
        exercise_suggestion = self.model.predict(input_data)

        # Decode the exercise suggestion (convert numeric value back to string)
        exercise_suggestion = self.label_encoder.inverse_transform(exercise_suggestion)

        # Display the result as a list of tasks
        exercises = exercise_suggestion[0].split(',')  # Assuming the suggestions are comma-separated

        # Clear previous results
        self.result_grid.clear_widgets()

        # Add each exercise as a separate checkbox in the scrollable list
        for exercise in exercises:
            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            checkbox = CheckBox(size_hint_x=None, width=50)
            checkbox.bind(active=self.update_score)

            task_label = Label(text=f"{exercise.strip()}", size_hint_x=0.8)

            task_layout.add_widget(checkbox)
            task_layout.add_widget(task_label)

            self.result_grid.add_widget(task_layout)

    def update_score(self, checkbox, value):
        """Update the score when a checkbox is toggled."""
        self.score += 10 if value else -10
        self.score_label.text = f"Your Score: {self.score}"

    def calculate_age(self):
        """Calculate age from date of birth."""
        birth_date = datetime.strptime(self.user_data['date_of_birth'], '%Y-%m-%d')
        current_date = datetime.now()
        return current_date.year - birth_date.year - (
            (current_date.month, current_date.day) < (birth_date.month, birth_date.day)
        )

    def prepare_model(self):
        """Prepare the machine learning model for fitness suggestions."""
        # Helper function to read fitness data from a CSV file
        def read_fitness_data(file_path):
            fitness_data = []
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    fitness_data.append(row)
            return fitness_data

        # Helper function to prepare feature and target data
        def prepare_data(fitness_data):
            X = []  # Features: BMI, Gender, Age
            y = []  # Target: Exercise type
            for row in fitness_data:
                X.append([float(row['BMI']), row['Gender'], int(row['Age'])])
                y.append(row['Recommended Exercises'])
            return X, y

        fitness_data = read_fitness_data('fitness.csv')
        X, y = prepare_data(fitness_data)

        # Encode categorical data (Gender and Exercise)
        label_encoder = LabelEncoder()

        # Encode gender (Male = 1, Female = 0)
        X = np.array(X)
        X[:, 1] = label_encoder.fit_transform(X[:, 1])  # Encode Gender
        X = X.astype(float)

        # Encode exercise types
        y = label_encoder.fit_transform(y)  # Encode target labels (Exercise)

        # Split the data into training and testing sets (80% training, 20% testing)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model using Decision Tree Classifier
        model = DecisionTreeClassifier()
        model.fit(X_train, y_train)

        return model, label_encoder

    def redirect_to_chatbot(self, instance):
        """Redirect to chatbot.py when the button is pressed."""
        try:
            subprocess.run(['python', 'chatbot.py'])  # Ensure chatbot.py is in the same directory
        except Exception as e:
            print(f"Error launching chatbot: {e}")
