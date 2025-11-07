import json
import datetime
import gettext
import os
from kivy.utils import platform # Import platform
from kivy.app import App # Import App for Android path resolution
from kivy.logger import Logger # Import Kivy's logger
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from tinydb import TinyDB, Query

# Set up gettext for internationalization
current_language = 'en' # Default language

# Use Kivy's app.directory for a more reliable path on Android
if platform == 'android':
    # On Android, app.directory points to the application's data directory
    # which is where Buildozer places the app files.
    app_instance = App.get_running_app() if App.get_running_app() else None
    if app_instance:
        localedir = os.path.join(app_instance.directory, 'locales')
    else:
        # Fallback if app is not yet running (e.g., during initial import)
        localedir = os.path.join(os.path.dirname(__file__), 'locales')
        Logger.warning("Translation: App instance not available, falling back to __file__ path.")
else:
    localedir = os.path.join(os.path.dirname(__file__), 'locales')

Logger.info(f"Translation: Resolved localedir: {localedir}")

try:
    # Attempt to load translations for all supported languages
    # This is done to ensure all translations are available for update_translations
    # and to prevent errors if a language is selected before its .mo is loaded.
    en_lang = gettext.translation('app', localedir, languages=['en'])
    am_lang = gettext.translation('app', localedir, languages=['am'])
    om_lang = gettext.translation('app', localedir, languages=['om'])
    
    # Initialize the global translation function _()
    # We'll re-bind this when the language changes
    _ = en_lang.gettext 
    Logger.info("Translation: Initial English translations loaded.")

except Exception as e:
    Logger.error(f"Translation: Error loading initial translations: {e}")
    # Fallback if translations fail to load
    _ = lambda s: s # No-op translation

def update_translations():
    global _
    try:
        # Re-bind the global _ function to the currently selected language
        lang_obj = gettext.translation('app', localedir, languages=[current_language])
        lang_obj.install() # This makes _() available globally
        _ = lang_obj.gettext
        Logger.info(f"Translation: Translations updated to: {current_language}")
    except Exception as e:
        Logger.error(f"Translation: Error updating translations for {current_language}: {e}")
        _ = lambda s: s # Fallback

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

    def load_all_translations(self):
        """Load all translations for the app"""
        global en_lang, am_lang, om_lang
        try:
            en_lang = gettext.translation('app', localedir, languages=['en'])
            am_lang = gettext.translation('app', localedir, languages=['am'])
            om_lang = gettext.translation('app', localedir, languages=['om'])
            Logger.info("Translation: All translation objects loaded successfully.")
        except Exception as e:
            Logger.error(f"Translation: Error in load_all_translations: {e}")

    def set_language(self, lang_code, button_text):
        global current_language
        current_language = lang_code
        self.root.ids.lang_button.text = button_text
        update_translations()
        self.update_ui_texts()
        Logger.info(f"Translation: Language set to {lang_code}")

    def update_ui_texts(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
            
        # Update text for all elements (no font changes to avoid errors)
        main_screen.ids.title_label.text = _("Expense Tracker")
        main_screen.ids.amount.hint_text = _("Amount")
        main_screen.ids.category.hint_text = _("Category")
        main_screen.ids.note.hint_text = _("Note (optional)")
        main_screen.ids.add_button.text = _("Add Expense")
        main_screen.ids.clear_button.text = _("Clear")
        main_screen.ids.expense_list_label.text = _("Expense List")
        
        # Update total label with current value
        current_text = main_screen.ids.total_label.text
        if ": ETB" in current_text:
            # Extract the numeric part and reformat with new translation
            try:
                etb_part = current_text.split(": ETB ")[1]
                main_screen.ids.total_label.text = f"{_("Total")}: ETB {etb_part}"
            except:
                main_screen.ids.total_label.text = f"{_("Total")}: ETB 0.00"
        else:
            main_screen.ids.total_label.text = f"{_("Total")}: ETB 0.00"

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
            item = OneLineListItem(text=_("No expenses yet."))
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
                
        main_screen.ids.total_label.text = f"{_("Total")}: ETB {total:.2f}"

if __name__ == "__main__":
    ExpenseTrackerApp().run()