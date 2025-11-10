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
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineIconListItem
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IconLeftWidget
from tinydb import TinyDB, Query

# Set up gettext for internationalization
current_language = 'en' # Default language

# Global translation function, will be set in build()
_ = lambda s: s # Default no-op

def update_translations():
    global _
    # localedir will be set on the app instance
    app_instance = App.get_running_app()
    if not app_instance or not hasattr(app_instance, 'localedir'):
        Logger.error("Translation: App instance or localedir not available for update_translations.")
        _ = lambda s: s
        return

    try:
        # Use fallback=True so missing .mo files won't raise an exception on Android
        lang_obj = gettext.translation('app', app_instance.localedir, languages=[current_language], fallback=True)
        lang_obj.install()
        _ = lang_obj.gettext
        Logger.info(f"Translation: Translations updated to: {current_language}")
    except Exception as e:
        Logger.error(f"Translation: Error updating translations for {current_language}: {e}")
        _ = lambda s: s

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
                size_hint_x: 0.2
                on_release: app.show_language_menu()
                
            MDIconButton:
                id: debug_button
                icon: "bug"
                size_hint_x: 0.1
                on_release: app.show_debug_info()
        
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
    confirm_dialog = None
    
    def build(self):
        self.sm = ScreenManager()
        # Load the KV string and create the screen
        Builder.load_string(KV)
        main_screen = MainScreen()
        self.sm.add_widget(main_screen)
        
        # Initialize localedir based on platform
        if platform == 'android':
            from android.storage import app_storage_path
            # Get the app's private storage directory on Android
            app_dir = app_storage_path()
            self.localedir = os.path.join(app_dir, 'locales')
            # Ensure the locales directory exists in app private storage
            os.makedirs(self.localedir, exist_ok=True)
        else:
            self.localedir = os.path.join(self.directory, 'locales')
        
        Logger.info(f"Translation: Resolved localedir: {self.localedir}")

        global en_lang, am_lang, om_lang, _
        try:
            # First try loading translations
            en_lang = gettext.translation('app', self.localedir, languages=['en'], fallback=True)
            am_lang = gettext.translation('app', self.localedir, languages=['am'], fallback=True)
            om_lang = gettext.translation('app', self.localedir, languages=['om'], fallback=True)
            _ = en_lang.gettext # Set initial translation function
            Logger.info("Translation: Initial English translations loaded in build().")
        except Exception as e:
            Logger.error(f"Translation: Error loading initial translations in build(): {e}")
            _ = lambda s: s # Fallback

        self.update_list()
        self.update_ui_texts()
        return self.sm

    def get_main_screen(self):
                try:
                    expense_list = main_screen.ids.expense_list
                    expense_list.clear_widgets()
                    total = 0
            
                    for expense in db.all():
                        amount = expense.get('amount', 0)
                        category = expense.get('category', '')
                        note = expense.get('note', '')
                        date = expense.get('date', '')
                        doc_id = expense.doc_id
                
                        # Create the list item with left icon and delete button
                        item = ThreeLineIconListItem(
                            text=f"{category}",
                            secondary_text=f"ETB {amount}",
                            tertiary_text=f"{date}{' - ' + note if note else ''}",
                        )
                
                        # Add category icon
                        icon = IconLeftWidget(
                            icon="cash"
                        )
                        item.add_widget(icon)
                
                        # Add delete button
                        delete_button = MDIconButton(
                            icon="delete",
                            pos_hint={'center_y': 0.5},
                            on_release=lambda x, doc_id=doc_id: self.show_delete_confirm(doc_id)
                        )
                        item.add_widget(delete_button)
                
                        expense_list.add_widget(item)
                        total += float(amount)
                
                    # Update total
                    main_screen.ids.total_label.text = f"Total: ETB {total:.2f}"
                except Exception as e:
                    Logger.error(f"Error updating expense list: {str(e)}")
                    self.show_error_dialog(_("Error updating expense list"))
                "on_release": lambda: self.set_language('en', 'EN')
            def show_delete_confirm(self, doc_id):
                """Show confirmation dialog before deleting an expense"""
                try:
                    expense = db.get(doc_id=doc_id)
                    if not expense:
                        self.show_error_dialog(_("Expense not found"))
                        return

                    # Create confirmation dialog
                    if self.confirm_dialog:
                        self.confirm_dialog.dismiss()

                    self.confirm_dialog = MDDialog(
                        title=_("Delete Expense"),
                        text=_(f"Are you sure you want to delete this expense?\n\nCategory: {expense['category']}\nAmount: ETB {expense['amount']}\nDate: {expense['date']}"),
                        buttons=[
                            MDFlatButton(
                                text=_("Cancel"),
                                on_release=lambda x: self.confirm_dialog.dismiss()
                            ),
                            MDRaisedButton(
                                text=_("Delete"),
                                on_release=lambda x: self.delete_expense(doc_id)
                            ),
                        ],
                    )
                    self.confirm_dialog.open()
                except Exception as e:
                    Logger.error(f"Error showing delete confirmation: {str(e)}")
                    self.show_error_dialog(_("Error showing delete confirmation"))
            },
            def delete_expense(self, doc_id):
                """Delete an expense from the database"""
                try:
                    db.remove(doc_ids=[doc_id])
                    if self.confirm_dialog:
                        self.confirm_dialog.dismiss()
                    self.update_list()
                    Logger.info(f"Successfully deleted expense with ID: {doc_id}")
                except Exception as e:
                    Logger.error(f"Error deleting expense: {str(e)}")
                    self.show_error_dialog(_("Error deleting expense"))
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
            # Use fallback=True so missing files won't crash the app
            en_lang = gettext.translation('app', self.localedir, languages=['en'], fallback=True)
            am_lang = gettext.translation('app', self.localedir, languages=['am'], fallback=True)
            om_lang = gettext.translation('app', self.localedir, languages=['om'], fallback=True)
            Logger.info("Translation: All translation objects loaded successfully.")
        except Exception as e:
            Logger.error(f"Translation: Error in load_all_translations: {e}")

    def set_language(self, lang_code, button_text):
        try:
            global current_language
            current_language = lang_code
            
            # Get the main screen safely
            main_screen = self.get_main_screen()
            if main_screen and hasattr(main_screen, 'ids') and hasattr(main_screen.ids, 'lang_button'):
                main_screen.ids.lang_button.text = button_text
            
            # Update translations safely
            self.update_translations_with_localedir(self.localedir)
            self.update_ui_texts()
            
            # Close the language menu if it's open
            if self.language_menu:
                self.language_menu.dismiss()
                
            Logger.info(f"Translation: Language set to {lang_code}")
        except Exception as e:
            Logger.error(f"Translation: Error in set_language: {str(e)}")
            # Don't propagate the exception - keep the app running

    def update_translations_with_localedir(self, localedir_path):
        global _
        try:
            # Use fallback=True to prevent exceptions if translation file is missing
            lang_obj = gettext.translation('app', localedir_path, languages=[current_language], fallback=True)
            lang_obj.install()
            _ = lang_obj.gettext
            Logger.info(f"Translation: Translations updated to: {current_language}")
        except Exception as e:
            Logger.error(f"Translation: Error updating translations for {current_language}: {e}")
            # Keep the current translation function if there's an error
            if not callable(_):
                _ = lambda s: s

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
                main_screen.ids.total_label.text = f'{_("Total")}: ETB {etb_part}'
            except:
                main_screen.ids.total_label.text = f'{_("Total")}: ETB 0.00'
        else:
            main_screen.ids.total_label.text = f'{_("Total")}: ETB 0.00'

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

    def show_debug_info(self):
        """Show debug information about translations"""
        try:
            # Get translation paths and files
            debug_info = ["Translation Debug Info:"]
            debug_info.append(f"Platform: {platform}")
            debug_info.append(f"Current language: {current_language}")
            debug_info.append(f"Localedir: {self.localedir}")
            
            # List translation files
            if os.path.exists(self.localedir):
                debug_info.append("\nAvailable translation files:")
                for root, dirs, files in os.walk(self.localedir):
                    for file in files:
                        if file.endswith('.mo') or file.endswith('.po'):
                            rel_path = os.path.relpath(os.path.join(root, file), self.localedir)
                            debug_info.append(f"- {rel_path}")
            else:
                debug_info.append(f"\nLocales directory not found: {self.localedir}")
            
            # Show the debug info in a dialog
            content = MDLabel(
                text="\n".join(debug_info),
                size_hint_y=None,
                height=400,
                halign="left"
            )
            self.debug_dialog = MDDialog(
                title="Debug Information",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_release=lambda x: self.debug_dialog.dismiss()
                    )
                ]
            )
            self.debug_dialog.open()
            
        except Exception as e:
            Logger.error(f"Debug: Error showing debug info: {str(e)}")
            # Show error in a simple dialog
            content = MDLabel(
                text=f"Error getting debug info:\n{str(e)}",
                size_hint_y=None,
                height=100
            )
            self.debug_dialog = MDDialog(
                title="Debug Error",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_release=lambda x: self.debug_dialog.dismiss()
                    )
                ]
            )
            self.debug_dialog.open()

    def close_dialog(self, instance):
        if self.dialog is not None:
            self.dialog.dismiss()
            
    def confirm_delete(self, expense):
        """Show confirmation dialog before deleting an expense"""
        if not self.confirm_dialog:
            amount = f"ETB {expense['amount']:.2f}"
            category = expense['category']
            self.expense_to_delete = expense
            
            self.confirm_dialog = MDDialog(
                text=_("Are you sure you want to delete this expense?") + f"\n{amount} - {category}",
                buttons=[
                    MDFlatButton(
                        text=_("Cancel"),
                        on_release=lambda x: self.confirm_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text=_("Delete"),
                        on_release=lambda x: self.delete_expense(expense)
                    ),
                ],
            )
        self.confirm_dialog.open()

    def delete_expense(self, expense):
        """Delete an expense from the database"""
        try:
            Expense = Query()
            # Delete expense matching all fields
            db.remove(
                (Expense.amount == expense["amount"]) & 
                (Expense.category == expense["category"]) & 
                (Expense.date == expense["date"])
            )
            # Close the confirmation dialog
            if self.confirm_dialog:
                self.confirm_dialog.dismiss()
            # Update the list view
            self.update_list()
        except Exception as e:
            Logger.error(f"Error deleting expense: {str(e)}")
            if self.confirm_dialog:
                self.confirm_dialog.dismiss()
            # Show error dialog
            error_dialog = MDDialog(
                text=_("Error deleting expense"),
                buttons=[
                    MDFlatButton(
                        text=_("ok"),
                        on_release=lambda x: error_dialog.dismiss()
                    ),
                ],
            )
            error_dialog.open()

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
                    secondary_text=secondary_text,
                )
                # Add delete icon
                delete_icon = MDIconButton(
                    icon="delete",
                    pos_hint={"center_y": .5},
                    on_release=lambda x, expense=e: self.confirm_delete(expense)
                )
                item.add_widget(delete_icon)
                main_screen.ids.expense_list.add_widget(item)
                
        main_screen.ids.total_label.text = f'{_("Total")}: ETB {total:.2f}'

if __name__ == "__main__":
    ExpenseTrackerApp().run()