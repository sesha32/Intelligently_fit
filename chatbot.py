from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle


class ChatBotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Adjust window size
        Window.size = (600, 700)

        self.username = "User"
        self.current_category = None
        self.feedback_collected = False

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        # Chat History
        self.chat_history = ScrollView(size_hint=(1, 0.8))
        self.chat_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.chat_history.add_widget(self.chat_box)
        main_layout.add_widget(self.chat_history)

        # Input Field and Send Button
        input_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.user_input = TextInput(
            hint_text="Type your feedback here...",
            multiline=True,
            size_hint=(0.8, None),
            height=40,
            font_size=16
        )
        send_button = Button(
            text="Send",
            size_hint=(0.2, None),
            height=40,
            font_size=16,
            background_color=(0.2, 0.6, 0.8, 1)  # Light blue
        )
        send_button.bind(on_release=self.process_feedback)
        input_layout.add_widget(self.user_input)
        input_layout.add_widget(send_button)
        main_layout.add_widget(input_layout)

        # Add layout to the screen
        self.add_widget(main_layout)

        # Initial greeting
        self.bot_message(f"Hi {self.username}! Welcome to our chatbot. How can I assist you today?")
        self.present_main_menu()

    def bot_message(self, message):
        """Display bot messages."""
        self._add_message(f"[b]Bot:[/b] {message}", "left", (0.9, 0.9, 0.9, 1))

    def user_message(self, message):
        """Display user messages."""
        self._add_message(f"[b]You:[/b] {message}", "right", (0, 0.6, 0, 1))

    def _add_message(self, message, alignment, bg_color):
        """Helper to add messages to the chat box."""
        label = Label(
            text=message,
            markup=True,
            size_hint_y=None,
            halign=alignment,
            valign="middle",
            font_size=16,
            text_size=(self.chat_box.width * 0.9, None),
        )
        label.bind(size=self._update_height)
        with label.canvas.before:
            Color(*bg_color)
            label.rect = RoundedRectangle(size=label.size, pos=label.pos)
        label.bind(size=lambda instance, value: setattr(label.rect, "size", value))
        label.bind(pos=lambda instance, value: setattr(label.rect, "pos", value))
        self.chat_box.add_widget(label)
        self.chat_history.scroll_to(label)

    def _update_height(self, instance, *args):
        """Update label height based on content."""
        instance.text_size = (instance.width, None)
        instance.height = instance.texture_size[1] + 15

    def display_option(self, text, callback):
        """Display options as buttons."""
        font_size = max(12, 16 - len(text) // 10)
        button = Button(
            text=text,
            size_hint=(None, None),
            size=(min(len(text) * font_size, Window.width * 0.8), 50),
            font_size=font_size,
            halign="center",
            valign="middle",
            background_color=(0.8, 0.9, 1, 1),
            text_size=(None, None),
        )
        button.bind(on_release=callback)
        self.chat_box.add_widget(button)
        self.chat_history.scroll_to(button)

    def process_feedback(self, instance):
        """Handle user feedback."""
        feedback = self.user_input.text.strip()
        if feedback:
            self.user_message(feedback)
            self.bot_message("Thank you for your valuable feedback! Would you like to restart?")
            self.display_option("Restart", lambda x: self.restart_chatbot())
            self.user_input.text = ""
            self.user_input.disabled = True
            self.feedback_collected = True

    def restart_chatbot(self):
        """Restart chatbot interaction."""
        self.chat_box.clear_widgets()
        self.user_input.disabled = False
        self.feedback_collected = False
        self.bot_message(f"Hi {self.username}! Welcome back. How can I assist you today?")
        self.present_main_menu()

    def present_main_menu(self):
        """Show main menu options."""
        self.bot_message("What would you like to know about our application?")
        self.display_option("Subscription Plans", lambda x: self.present_sub_questions("subscription plan"))
        self.display_option("OTT Platforms", lambda x: self.present_sub_questions("ott platforms"))
        self.display_option("Security", lambda x: self.present_sub_questions("security"))
        self.display_option("Legality Issues", lambda x: self.present_sub_questions("legality issues"))

    def present_sub_questions(self, category):
        """Show sub-questions for a category."""
        self.current_category = category
        self.user_message(f"Selected: {category.capitalize()}")
        questions = {
            "subscription plan": [
                ("What plans do you offer?", "We offer Basic, Standard, and Premium plans."),
                ("How much does it cost?", "Our plans range from $5 to $20 per month."),
            ],
            "ott platforms": [
                ("What platforms are supported?", "We support Netflix, Amazon Prime, Disney+, and more."),
                ("How to link my account?", "Go to Settings > Link Account > Follow the instructions."),
            ],
            "security": [
                ("How secure is my data?", "We use 256-bit encryption to secure all data."),
                ("What measures are in place to protect me?", "We implement multi-factor authentication and secure payments."),
            ],
            "legality issues": [
                ("Is subscription sharing legal?", "Subscription sharing depends on the platform's terms of service."),
                ("Are there any risks involved?", "Sharing accounts may lead to account suspension."),
            ],
        }
        for question, answer in questions.get(category, []):
            self.display_option(question, lambda x, q=question, a=answer: self.show_answer(q, a))

    def show_answer(self, question, answer):
        """Show an answer to a question."""
        self.user_message(question)
        self.bot_message(answer)
        self.ask_satisfaction()

    def ask_satisfaction(self):
        """Ask if the user is satisfied."""
        self.bot_message("Are you satisfied with my answer?")
        self.display_option("Yes", lambda x: self.collect_feedback())
        self.display_option("No", lambda x: self.represent_questions())

    def represent_questions(self):
        """Re-present questions for the current category."""
        self.bot_message("Let me present the questions again for you.")
        self.present_sub_questions(self.current_category)

    def collect_feedback(self):
        """Prompt the user for feedback."""
        self.bot_message("I'm glad I could help! Please provide your feedback below.")
        self.user_input.disabled = False
