from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import csv
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from session import SessionManager  # Assuming the session.py is in the same directory
from datetime import datetime

class UserDashBoardScreen(Screen):
    def __init__(self, **kwargs):
        super(UserDashBoardScreen, self).__init__(**kwargs)

        # Get the current logged-in user from the session
        self.user_data = SessionManager.get_user()

        if not self.user_data:
            print("No user is logged in!")
            # You may want to redirect to the login screen or show an error message
            return

        # Debugging to ensure user data is loaded
        print(f"User data: {self.user_data}")
        if 'date_of_birth' not in self.user_data:
                print("Date of birth is missing!")
        if 'gender' not in self.user_data:
            print("Gender is missing!")
        if 'weight' not in self.user_data:
            print("Weight is missing!")
        if 'height' not in self.user_data:
            print("Height is missing!")

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Display user data (height, weight, gender) for BMI calculation
        self.bmi_label = Label(text=f"Hello, {self.user_data['first_name']} {self.user_data['last_name']}")
        self.layout.add_widget(self.bmi_label)

        # Calculate and display BMI
        bmi = self.calculate_bmi()
        self.bmi_value_label = Label(text=f"Your BMI: {bmi:.2f}")
        self.layout.add_widget(self.bmi_value_label)

        # Button to get fitness suggestions
        self.predict_button = Button(text="Get Fitness Suggestion")
        self.predict_button.bind(on_press=self.on_predict)
        self.layout.add_widget(self.predict_button)

        # Create a ScrollView for displaying exercise suggestions as tasks
        self.result_scroll = ScrollView(size_hint=(1, None), height=200)
        self.result_grid = GridLayout(cols=1, size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        self.result_scroll.add_widget(self.result_grid)
        self.layout.add_widget(self.result_scroll)

        self.add_widget(self.layout)

        # Prepare the model for prediction
        self.model, self.label_encoder = self.prepare_model()

    def calculate_bmi(self):
        """Calculate BMI using height (in cm) and weight (in kg)."""
        height = float(self.user_data['height']) / 100  # Convert height to meters
        weight = float(self.user_data['weight'])
        bmi = weight / (height ** 2)
        return bmi

    def prepare_model(self):
        """Prepare the machine learning model for fitness suggestions."""
        def read_fitness_data(file_path):
            fitness_data = []
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    fitness_data.append(row)
            return fitness_data

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

        # Add each exercise as a separate label in the scrollable list
        for exercise in exercises:
            self.result_grid.add_widget(Label(text=f"✓ {exercise.strip()}", size_hint_y=None, height=40))

    def calculate_age(self):
        """Calculate age from date_of_birth."""
        birth_date = datetime.strptime(self.user_data['date_of_birth'], '%Y-%m-%d')
        current_date = datetime.now()
        age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        return age
