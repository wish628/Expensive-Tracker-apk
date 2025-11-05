import os
import gettext
import json
import datetime
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase

# Register the Amharic font
LabelBase.register(name='AmharicFont', fn_regular='fonts/NotoSansEthiopic-Regular.ttf')
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from tinydb import TinyDB, Query

# Global variables for language selection
current_language = 'en'

# Configure gettext for internationalization
locales_dir = os.path.join(os.path.dirname(__file__), 'locales')

# Dictionary to hold translation functions for each language
translators = {}

# Initialize translations for each language
def init_translations():
    global translators
    if os.path.exists(locales_dir):
        # English translator
        try:
            en_translator = gettext.translation('app', locales_dir, languages=['en'])
            translators['en'] = en_translator.gettext
        except:
            # Fallback to dummy translator
            # Try JSON fallback (locales/en/LC_MESSAGES/app.json)
            json_path = os.path.join(locales_dir, 'en', 'LC_MESSAGES', 'app.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    translators['en'] = lambda s, d=data: d.get(s, s)
                except Exception:
                    translators['en'] = lambda x: x
            else:
                translators['en'] = lambda x: x
            
        # Amharic translator
        try:
            am_translator = gettext.translation('app', locales_dir, languages=['am'])
            translators['am'] = am_translator.gettext
        except:
            # Try JSON fallback (locales/am/LC_MESSAGES/app.json)
            json_path = os.path.join(locales_dir, 'am', 'LC_MESSAGES', 'app.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    translators['am'] = lambda s, d=data: d.get(s, s)
                except Exception:
                    translators['am'] = lambda x: x
            else:
                translators['am'] = lambda x: x
            
        # Oromo translator
        try:
            om_translator = gettext.translation('app', locales_dir, languages=['om'])
            translators['om'] = om_translator.gettext
        except:
            # Try JSON fallback (locales/om/LC_MESSAGES/app.json)
            json_path = os.path.join(locales_dir, 'om', 'LC_MESSAGES', 'app.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    translators['om'] = lambda s, d=data: d.get(s, s)
                except Exception:
                    translators['om'] = lambda x: x
            else:
                translators['om'] = lambda x: x

# Initialize translations
init_translations()

# Create a global translation function
def _(message):
    global current_language, translators
    try:
        if current_language in translators:
            result = translators[current_language](message)
            return result
        else:
            return message
    except Exception as e:
        # Return the original message if translation fails
        return message

# Pre-translate strings
def update_translations():
    global EXPENSE_TRACKER, AMOUNT, CATEGORY, NOTE, ADD_EXPENSE, TOTAL, DATE, EDIT, DELETE
    global LANGUAGE, ENGLISH, AMHARIC, OROMO, EXPENSE_LIST, NO_EXPENSES, SELECT_LANGUAGE
    EXPENSE_TRACKER = _("expense_tracker")
    AMOUNT = _("amount")
    CATEGORY = _("category")
    NOTE = _("note")
    ADD_EXPENSE = _("add_expense")
    TOTAL = _("total")
    DATE = _("date")
    EDIT = _("edit")
    DELETE = _("delete")
    LANGUAGE = _("language")
    ENGLISH = _("english")
    AMHARIC = _("amharic")
    OROMO = _("oromo")
    EXPENSE_LIST = _("expense_list")
    NO_EXPENSES = _("no_expenses")
    SELECT_LANGUAGE = _("select_language")
    
    # Debug print to see what translations are loaded
    print(f"=== Language Switch Debug ===")
    print(f"Current language: {current_language}")
    print(f"EXPENSE_TRACKER: '{EXPENSE_TRACKER}'")
    print(f"AMOUNT: '{AMOUNT}'")
    print(f"CATEGORY: '{CATEGORY}'")
    print(f"ADD_EXPENSE: '{ADD_EXPENSE}'")
    print(f"TOTAL: '{TOTAL}'")

# Initial translation
update_translations()

KV = """
<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(10)
        
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(50)
            
            MDLabel:
                id: title_label
                text: "Expense Tracker"
                halign: "left"
                font_style: "H4"
                size_hint_x: 0.7
            
            MDRaisedButton:
                id: lang_button
                text: "EN"
                size_hint_x: 0.3
                on_release: app.show_language_menu()
        
        MDTextField:
            id: amount
            hint_text: "Amount"
            input_filter: "float"
            helper_text: "Enter amount in ETB"
            helper_text_mode: "on_focus"

        MDTextField:
            id: category
            hint_text: "Category"
            helper_text: "e.g., Food, Transport, etc."
            helper_text_mode: "on_focus"

        MDTextField:
            id: note
            hint_text: "Note (optional)"
            multiline: True
            mode: "rectangle"

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(10)
            size_hint_y: None
            height: dp(50)
            
            MDRaisedButton:
                id: add_button
                text: "Add Expense"
                on_release: app.add_expense()
                size_hint_x: 0.7
            
            MDFlatButton:
                id: clear_button
                text: "Clear"
                on_release: app.clear_fields()
                size_hint_x: 0.3

        MDLabel:
            id: total_label
            text: "Total: ETB 0.00"
            halign: "center"
            font_style: "H6"
            theme_text_color: "Primary"
        
        MDLabel:
            id: expense_list_label
            text: "Expense List"
            halign: "left"
            font_style: "Subtitle1"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(30)
        
        ScrollView:
            MDList:
                id: expense_list
"""

db = TinyDB("expenses.json")

class MainScreen(Screen):
    pass

class ExpenseTrackerApp(MDApp):
    dialog = None
    language_menu = None
    
    def build(self):
        self.sm = ScreenManager()
        # Load the KV string and create the screen
        Builder.load_string(KV)
        main_screen = MainScreen()
        self.sm.add_widget(main_screen)
        self.update_list()
        self.update_ui_texts()
        return self.sm

    def get_main_screen(self):
        """Safely get the main screen"""
        if self.sm is None:
            return None
        try:
            return self.sm.get_screen("main")
        except:
            return None

    def show_language_menu(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        # Create language menu
        menu_items = [
            {
                "text": "English",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_language('en', 'EN')
            },
            {
                "text": "አማርኛ",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_language('am', 'AM')
            },
            {
                "text": "Oromoo",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_language('om', 'OM')
            }
        ]
        
        self.language_menu = MDDropdownMenu(
            caller=main_screen.ids.lang_button,
            items=menu_items,
            width_mult=4,
        )
        self.language_menu.open()

    def set_language(self, lang_code, button_text):
        global current_language
        current_language = lang_code
        
        # Close the menu
        if self.language_menu is not None:
            self.language_menu.dismiss()
        
        # Update translations
        update_translations()
        
        # Update UI texts
        self.update_ui_texts()
        
        # Update the language button text
        main_screen = self.get_main_screen()
        if main_screen is not None:
            main_screen.ids.lang_button.text = button_text

    def update_ui_texts(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        # Update text for all elements (no font changes to avoid errors)
        main_screen.ids.title_label.text = EXPENSE_TRACKER
        main_screen.ids.amount.hint_text = AMOUNT
        main_screen.ids.category.hint_text = CATEGORY
        main_screen.ids.note.hint_text = NOTE
        main_screen.ids.add_button.text = ADD_EXPENSE
        main_screen.ids.clear_button.text = _("clear")
        main_screen.ids.expense_list_label.text = EXPENSE_LIST
        
        # Apply Amharic font if current language is Amharic
        if current_language == 'am':
            main_screen.ids.title_label.font_name = 'AmharicFont'
            main_screen.ids.amount.font_name = 'AmharicFont'
            main_screen.ids.category.font_name = 'AmharicFont'
            main_screen.ids.note.font_name = 'AmharicFont'
            main_screen.ids.add_button.font_name = 'AmharicFont'
            main_screen.ids.clear_button.font_name = 'AmharicFont'
            main_screen.ids.expense_list_label.font_name = 'AmharicFont'
        else:
            # Reset to default font for other languages
            main_screen.ids.title_label.font_name = 'Roboto'
            main_screen.ids.amount.font_name = 'Roboto'
            main_screen.ids.category.font_name = 'Roboto'
            main_screen.ids.note.font_name = 'Roboto'
            main_screen.ids.add_button.font_name = 'Roboto'
            main_screen.ids.clear_button.font_name = 'Roboto'
            main_screen.ids.expense_list_label.font_name = 'Roboto'
        
        # Update total label with current value
        current_text = main_screen.ids.total_label.text
        if ": ETB" in current_text:
            # Extract the numeric part and reformat with new translation
            try:
                etb_part = current_text.split(": ETB ")[1]
                main_screen.ids.total_label.text = f"{TOTAL}: ETB {etb_part}"
            except:
                main_screen.ids.total_label.text = f"{TOTAL}: ETB 0.00"
        else:
            main_screen.ids.total_label.text = f"{TOTAL}: ETB 0.00"

    def add_expense(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        amount = main_screen.ids.amount.text
        category = main_screen.ids.category.text
        note = main_screen.ids.note.text
        
        if amount.strip() == "" or category.strip() == "":
            # Show error dialog
            if not self.dialog:
                self.dialog = MDDialog(
                    text=_("fill_all_fields"),
                    buttons=[
                        MDFlatButton(
                            text=_("ok"),
                            on_release=self.close_dialog
                        ),
                    ],
                )
            if self.dialog is not None:
                self.dialog.open()
            return
            
        # Add to database with current date
        db.insert({
            "amount": float(amount), 
            "category": category, 
            "note": note,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        # Clear fields
        self.clear_fields()
        
        # Update list
        self.update_list()

    def close_dialog(self, instance):
        if self.dialog is not None:
            self.dialog.dismiss()

    def clear_fields(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        main_screen.ids.amount.text = ""
        main_screen.ids.category.text = ""
        main_screen.ids.note.text = ""

    def update_list(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        main_screen.ids.expense_list.clear_widgets()
        total = 0
        
        expenses = db.all()
        if not expenses:
            # Show no expenses message
            item = OneLineListItem(text=NO_EXPENSES)
            main_screen.ids.expense_list.add_widget(item)
        else:
            # Sort expenses by date (newest first), handling cases where date might be missing
            try:
                expenses.sort(key=lambda x: x.get('date', ''), reverse=True)
            except:
                pass  # If sorting fails, continue with unsorted list
            
            for e in expenses:
                total += e["amount"]
                # Format the display text
                amount_text = f"ETB {e['amount']:.2f}"
                category_text = e['category']
                
                # Handle date field (for existing expenses that might not have date)
                date_text = e.get('date', 'Unknown date')
                if e["note"]:
                    secondary_text = f"{e['note']} - {date_text}"
                else:
                    secondary_text = date_text
                    
                # Create list item
                item = TwoLineListItem(
                    text=f"{amount_text} - {category_text}",
                    secondary_text=secondary_text
                )
                main_screen.ids.expense_list.add_widget(item)
                
        main_screen.ids.total_label.text = f"{TOTAL}: ETB {total:.2f}"

if __name__ == "__main__":
    ExpenseTrackerApp().run()