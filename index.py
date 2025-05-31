from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import StringProperty
import threading
import time

Window.size = (500, 700)
Window.clearcolor = (0.1, 0.1, 0.1, 1)
CHAT_HISTORY_FILE = "chat_history.txt"


class ChatBubble(Label):
    def __init__(self, **kwargs):
        super(ChatBubble, self).__init__(**kwargs)
        self.size_hint_y = None
        self.text_size = (Window.width - 60, None)
        self.halign = "left"
        self.valign = "top"
        self.padding = (12, 12)
        self.markup = True
        self.color = (1, 1, 1, 1)
        self.font_size = 20
        self.bind(texture_size=self.update_height)
    
    def update_height(self, instance, value):
        self.height = value[1] + 20  # Add padding if needed


class ChatUI(BoxLayout):
    def __init__(self, on_submit_callback=None, **kwargs):
        super(ChatUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        self.on_submit_callback = on_submit_callback

        # Output area
        self.scrollview = ScrollView(size_hint=(1, 0.75), bar_width=10)
        self.output_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        self.output_layout.bind(minimum_height=self.output_layout.setter('height'))
        self.scrollview.add_widget(self.output_layout)
        self.add_widget(self.scrollview)

        # Input field
        self.chat_input = TextInput(
            hint_text="Type your message...",
            multiline=True,
            size_hint=(1, 0.15),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=20
        )
        self.chat_input.bind(on_text_validate=self.on_enter)
        self.chat_input.bind(on_key_down=self.on_key_down)
        self.add_widget(self.chat_input)

        # Enter key function
        Window.bind(on_key_down=self.on_key_down)

        # # Submit button
        # self.submit_button = Button(
        #     text="Send",
        #     size_hint=(0.2, 0.1),
        #     background_color=(0.3, 0.5, 1, 1),
        #     color=(1, 1, 1, 1),
        #     font_size=44
        # )
        # self.submit_button.bind(on_press=self.on_submit)
        # self.add_widget(self.submit_button)

        # Centered container for the button
        button_container = AnchorLayout(
            anchor_x='center',
            anchor_y='top',
            size_hint=(1, None),
            height=60
        )

        # Submit button
        self.submit_button = Button(
            text="Send",
            size_hint=(None, None),
            size=(150, 50),  # fixed size to help centering
            background_color=(0.3, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=20
        )
        self.submit_button.bind(on_press=self.on_submit)

        # Add button to container, and container to main layout
        button_container.add_widget(self.submit_button)
        self.add_widget(button_container)

    # Enter key dynamic function
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 13:  # Enter key
            if 'shift' in modifiers:
                # Insert newline if Shift+Enter
                self.input_box.insert_text('\n')
            else:
                # Submit if only Enter
                self.on_submit(None)
        return True

    def on_enter(self, instance):
        self.on_submit(None)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if 'shift' in modifiers and keycode == 40:  # Shift + Enter
            instance.insert_text("\n")
        elif keycode == 40:  # Enter
            self.on_submit(None)
            return True

    def on_submit(self, instance):
        user_text = self.chat_input.text.strip()
        if user_text:
            self.chat_input.text = ""
            self.append_output(f"[b][color=00ffff]You:[/color][/b] {user_text}", from_user=True)
            self.save_to_history(f"You: {user_text}")
            if self.on_submit_callback:
                threading.Thread(target=self.on_submit_callback, args=(user_text,), daemon=True).start()

    def append_output(self, text, from_user=False):
        bubble = ChatBubble(text=text)
        # bubble.halign = "left" if from_user else "right"
        bubble.halign = "right" if from_user else "left"
        self.output_layout.add_widget(bubble)
        self.scrollview.scroll_y = 0

    def save_to_history(self, text):
        with open(CHAT_HISTORY_FILE, "a") as f:
            f.write(text + "\n")


class KivyChatApp(App):
    def __init__(self, on_submit_callback, **kwargs):
        super().__init__(**kwargs)
        self.chat_ui = None
        self.on_submit_callback = on_submit_callback

    def build(self):
        self.chat_ui = ChatUI(on_submit_callback=self.on_submit_callback)
        return self.chat_ui

    def display_output(self, text):
        self.chat_ui.append_output(text, from_user=False)
        self.chat_ui.save_to_history(text)

