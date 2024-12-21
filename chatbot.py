from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  # Loading all the environment variables

# Configure the Generative AI client with API key
genai.configure(api_key="AIzaSyBDhsdjYQ_GC1CGrwZubfB_mUvebrtlmrI")

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

class GeminiApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.chat_history = []
        
        # Create a ScrollView to hold the chat history
        self.scroll_view = ScrollView(size_hint=(1, None), height=400)
        
        # Create a BoxLayout to arrange the labels vertically inside the ScrollView
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        # Add the BoxLayout inside the ScrollView
        self.scroll_view.add_widget(self.history_layout)
        self.add_widget(self.scroll_view)

        # Input field for user message
        self.user_input = TextInput(hint_text="Type your question here", multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.user_input)

        # Send button
        self.send_button = Button(text="Send", size_hint_y=None, height=50)
        self.send_button.bind(on_press=self.send_message)
        self.add_widget(self.send_button)

    def send_message(self, instance):
        user_input = self.user_input.text.strip()
        if not user_input:
            return

        # Add user input to chat history
        self.chat_history.append(f"You: {user_input}")
        self.update_history()
        
        if user_input.lower() in ["exit", "quit"]:
            self.chat_history.append("Exiting the application. Goodbye!")
            self.update_history()
            App.get_running_app().stop()
            return

        # Get response from Gemini AI
        response = get_gemini_response(user_input)

        bot_response = ""
        for chunk in response:
            bot_response += chunk.text

        # Add bot response to chat history
        self.chat_history.append(f"Bot: {bot_response}")
        self.update_history()

        # Clear input field
        self.user_input.text = ""

    def update_history(self):
        # Clear the previous content from the layout
        self.history_layout.clear_widgets()

        # Add each chat history item as a Label to the layout
        for message in self.chat_history:
            label = Label(text=message, size_hint_y=None, height=40, halign="left", valign="top", size_hint_x=1)
            label.bind(size=self.on_label_resize)
            self.history_layout.add_widget(label)

        # Make sure the ScrollView scrolls to the bottom
        self.scroll_view.scroll_y = 0

    def on_label_resize(self, label, size):
        label.text_size = (label.width - 20, None)  # Adjust text size to fit within the label width minus padding

class GeminiAppWrapper(App):
    def build(self):
        return GeminiApp()

if __name__ == "__main__":
    GeminiAppWrapper().run()