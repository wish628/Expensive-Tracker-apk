import json
import datetime
import gettext
import os
from kivy.utils import platform  # Import platform
from kivy.app import App  # Import App for Android path resolution
from kivy.logger import Logger  # Import Kivy's logger
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from tinydb import TinyDB
from utils import validate_expense

# Set up gettext for internationalization
current_language = 'en'  # Default language

# Global translation function, will be set in build()


def _(s): return s  # Default no-op


# Fallback dictionary-based translations (populated by load_all_translations)
TRANSLATIONS = {}

# Optional Android/native notifications via plyer
try:
    from plyer import notification as plyer_notification
except Exception:
    plyer_notification = None


def update_translations():
    global _
    # localedir will be set on the app instance
    app_instance = App.get_running_app()
    if not app_instance or not hasattr(app_instance, 'localedir'):
        Logger.error(
            "Translation: App instance or localedir not available for update_translations.")

        def _(s): return s
        return

    try:
        lang_obj = gettext.translation(
            'app',
            app_instance.localedir,
            languages=[current_language])
        lang_obj.install()
        _ = lang_obj.gettext
        Logger.info(
            f"Translation: Translations updated to: {current_language}")
    except Exception as e:
        Logger.error(
            f"Translation: Error updating translations for {current_language}: {e}")

        def _(s): return s


KV = """
<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(8)
        padding: dp(8)

        MDToolbar:
            id: toolbar
            title: "Expense Tracker"
            elevation: 10
            md_bg_color: app.theme_cls.primary_color
            left_action_items: []
            right_action_items: [["language", lambda x: app.show_language_menu()]]

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(8)
            size_hint_y: None
            height: dp(56)

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
            size_hint_y: None
            height: dp(100)

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(8)
            size_hint_y: None
            height: dp(48)

            MDRaisedButton:
                id: add_button
                text: "Add Expense"
                on_release: app.add_expense()
                size_hint_x: 0.6

            MDIconButton:
                id: export_button
                icon: "export"
                on_release: app.export_database()
                pos_hint: {"center_y": .5}

            MDIconButton:
                id: delete_selected_button
                icon: "delete"
                on_release: app.delete_selected()
                disabled: True
                opacity: .0

            MDIconButton:
                id: delete_all_button
                icon: "delete-forever"
                on_release: app.confirm_clear_database()
                pos_hint: {"center_y": .5}

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(36)
            MDLabel:
                id: total_label
                text: "Total: ETB 0.00"
                halign: "left"
                font_style: "H6"
                theme_text_color: "Primary"
            MDCheckbox:
                id: select_all_checkbox
                size_hint_x: None
                width: dp(48)
                on_active: app.toggle_select_all(self, args[1])
            MDLabel:
                text: "Select All"
                size_hint_x: None
                width: dp(90)

        MDLabel:
            id: expense_list_label
            text: "Expense List"
            halign: "left"
            font_style: "Subtitle1"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(28)

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
    selected_ids = None
    _directory = None  # Private storage for directory property

    @property
    def directory(self):
        """Get the app's directory path"""
        if self._directory is None:
            self._directory = os.path.dirname(os.path.abspath(__file__))
        return self._directory

    @directory.setter
    def directory(self, value):
        """Set the app's directory path (used in testing)"""
        self._directory = value

    @property
    def _get_text(self):
        """Helper for tests to get current translation function"""
        return _

    def build(self):
        self.sm = ScreenManager()
        # Load the KV string and create the screen
        Builder.load_string(KV)
        main_screen = MainScreen()
        self.sm.add_widget(main_screen)

        # Initialize localedir and translations here, after app is running
        self.localedir = os.path.join(self.directory, 'locales')
        Logger.info(
            f"Translation: App.directory resolved localedir: {self.localedir}")

        global en_lang, am_lang, om_lang, _
        try:
            en_lang = gettext.translation(
                'app', self.localedir, languages=['en'])
            am_lang = gettext.translation(
                'app', self.localedir, languages=['am'])
            om_lang = gettext.translation(
                'app', self.localedir, languages=['om'])
            _ = en_lang.gettext  # Set initial translation function
            Logger.info(
                "Translation: Initial English translations loaded in build().")
        except Exception as e:
            Logger.error(
                f"Translation: Error loading initial translations in build(): {e}")

            def _(s): return s  # Fallback

        self.update_list()
        self.update_ui_texts()
        # Initialize selected set for multi-select without adding new widgets
        self.selected_ids = set()
        return self.sm

    def get_main_screen(self):
        """Safely get the main screen"""
        if self.sm is None:
            return None
        try:
            return self.sm.get_screen("main")
        except BaseException:
            return None

    def show_language_menu(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
        # Create language menu with safe callbacks that dismiss the menu
        def _make_item(label, code, button_text):
            return {
                "text": label,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=None, c=code, b=button_text: (self.language_menu.dismiss(), self.set_language(c, b))
            }

        menu_items = [
            _make_item("English", 'en', 'EN'),
            _make_item("አማርኛ", 'am', 'AM'),
            _make_item("Oromoo", 'om', 'OM')
        ]

        self.language_menu = MDDropdownMenu(
            caller=main_screen.ids.toolbar.ids.right_actions if hasattr(main_screen.ids.toolbar, 'ids') else main_screen.ids.toolbar,
            items=menu_items,
            width_mult=4,
        )
        # Fallback: attach to toolbar if lang button not present
        try:
            self.language_menu.caller = main_screen.ids.toolbar
        except Exception:
            pass
        self.language_menu.open()

    def load_all_translations(self):
        """Load all translations for the app"""
        global en_lang, am_lang, om_lang, _
        global TRANSLATIONS
        try:
            en_lang = gettext.translation(
                'app', self.localedir, languages=['en'])
            am_lang = gettext.translation(
                'app', self.localedir, languages=['am'])
            om_lang = gettext.translation(
                'app', self.localedir, languages=['om'])

            # Try to build simple dictionaries from PO files as a reliable
            # fallback
            def _parse_po(lang_code):
                po_path = os.path.join(
                    self.localedir, lang_code, 'LC_MESSAGES', 'app.po')
                mapping = {}
                try:
                    with open(po_path, 'r', encoding='utf-8') as fh:
                        lines = fh.readlines()
                    msgid = None
                    msgstr = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('msgid '):
                            # remove leading msgid and surrounding quotes
                            msgid = line[6:].strip().strip('"')
                        elif line.startswith('msgstr '):
                            msgstr = line[7:].strip().strip('"')
                            if msgid is not None:
                                mapping[msgid] = msgstr
                                msgid = None
                                msgstr = None
                except Exception:
                    # If PO isn't available, leave mapping empty
                    mapping = {}
                return mapping

            TRANSLATIONS['en'] = _parse_po('en')
            TRANSLATIONS['am'] = _parse_po('am')
            TRANSLATIONS['om'] = _parse_po('om')

            # Prefer gettext objects when they have entries; otherwise use PO
            # mapping
            def _gettext_factory(lang_code, gettext_obj):
                def _t(s):
                    # Try gettext object first
                    try:
                        res = gettext_obj.gettext(s)
                        if res and res != s:
                            return res
                    except Exception:
                        pass
                    # Fallback to PO mapping
                    return TRANSLATIONS.get(lang_code, {}).get(s, s)
                return _t

            _ = _gettext_factory('en', en_lang)
            Logger.info(
                "Translation: All translation objects loaded successfully.")
        except Exception as e:
            Logger.error(f"Translation: Error in load_all_translations: {e}")

    def set_language(self, lang_code, button_text):
        """Change the app's language."""
        global current_language, _, en_lang, am_lang, om_lang

        try:
            current_language = lang_code

            # Update toolbar title (UI may use toolbar now)
            try:
                main_screen = self.get_main_screen()
                if main_screen and hasattr(main_screen.ids, 'toolbar'):
                    main_screen.ids.toolbar.title = _("expense_tracker")
            except Exception as e:
                Logger.error(f"Translation: Failed to update toolbar title: {e}")

            # Update global translation function using factory
            def _gettext_factory(lang_code, gettext_obj):
                def _t(s):
                    # Try gettext object first
                    try:
                        res = gettext_obj.gettext(s)
                        if res and res != s:
                            return res
                    except Exception:
                        pass
                    # Fallback to PO mapping
                    return TRANSLATIONS.get(lang_code, {}).get(s, s)
                return _t

            # Get the appropriate gettext object
            lang_obj_map = {'en': en_lang, 'am': am_lang, 'om': om_lang}
            lang_obj = lang_obj_map.get(lang_code)
            if lang_obj:
                _ = _gettext_factory(lang_code, lang_obj)
            else:
                def _(s): return s

            # Update UI texts if UI is available
            try:
                if self.root:
                    self.update_ui_texts()
            except Exception as e:
                Logger.error(f"Translation: Failed to update UI texts: {e}")

            Logger.info(f"Translation: Language set to {lang_code}")
            self.notify(f"Language changed to {button_text}")
        except Exception as e:
            Logger.error(f"Translation: Error in set_language: {e}")
            self.notify("Language change failed")

    def update_translations_with_localedir(self, localedir_path):
        """Legacy method for compatibility; use set_language instead."""
        # This is kept for backward compatibility with existing code
        # set_language now handles translation updates
        pass

    def update_ui_texts(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return

        try:
            # Update text for all elements using translation keys from PO files
            # toolbar title
            try:
                if hasattr(main_screen.ids, 'toolbar'):
                    main_screen.ids.toolbar.title = _("expense_tracker")
            except Exception:
                pass
            main_screen.ids.amount.hint_text = _("amount")
            main_screen.ids.category.hint_text = _("category")
            main_screen.ids.note.hint_text = _("note")
            main_screen.ids.add_button.text = _("add_expense")
            # export and delete buttons are icon-based; no text to update
            main_screen.ids.expense_list_label.text = _("expense_list")

            # Update total label with current value (use translation key 'total')
            current_text = main_screen.ids.total_label.text
            if ": ETB" in current_text:
                try:
                    etb_part = current_text.split(": ETB ")[1]
                    main_screen.ids.total_label.text = f'{_("total")}: ETB {etb_part}'
                except BaseException:
                    main_screen.ids.total_label.text = f'{_("total")}: ETB 0.00'
            else:
                main_screen.ids.total_label.text = f'{_("total")}: ETB 0.00'
        except Exception as e:
            Logger.error(f"Translation: Error updating UI texts overall: {e}")
        # ensure action buttons reflect selection state
        try:
            self.update_action_buttons_visibility()
        except Exception:
            pass
        except Exception as e:
            Logger.error(f"Translation: Error updating UI texts: {e}")

    def notify(self, message):
        """Show an in-app notification (Snackbar) and try native notification on Android."""
        try:
            Snackbar(text=message, duration=2).open()
        except Exception as e:
            Logger.info(f"Notification: {message} (Snackbar error: {e})")

        # Try native notification if available
        if plyer_notification and platform == 'android':
            try:
                plyer_notification.notify(
                    title="ExpenseTracker", message=message, timeout=2)
            except Exception as e:
                Logger.error(f"Notification: plyer failed: {e}")

    def add_expense(self):
        main_screen = self.get_main_screen()
        if main_screen is None:
            return

        amount = main_screen.ids.amount.text
        category = main_screen.ids.category.text
        note = main_screen.ids.note.text

        # Use utils.validate_expense so we can unit test validation logic
        ok, err_key = validate_expense(amount, category)
        if not ok:
            msg_key = err_key or 'fill_all_fields'
            error_msg = _(msg_key)
            if not self.dialog:
                self.dialog = MDDialog(
                    text=error_msg,
                    buttons=[
                        MDFlatButton(
                            text=_('ok'),
                            on_release=self.close_dialog
                        ),
                    ],
                )
            if self.dialog is not None:
                self.dialog.open()
            return

        # Add to database with current date
        try:
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
            # Notify user with success message
            success_msg = f"✓ Added ETB {amount} to {category}"
            self.notify(success_msg)
            Logger.info(f"DB: Expense added - {category}: ETB {amount}")
        except Exception as e:
            Logger.error(f"DB: Failed to insert expense: {e}")
            error_dialog = MDDialog(
                text=f"Error adding expense: {str(e)}",
                buttons=[
                    MDFlatButton(
                        text=_('ok'),
                        on_release=lambda x: error_dialog.dismiss())])
            error_dialog.open()

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
            item = OneLineListItem(text=_("no_expenses"))
            main_screen.ids.expense_list.add_widget(item)
        else:
            # Sort expenses by date (newest first), handling cases where date
            # might be missing
            try:
                expenses.sort(key=lambda x: x.get('date', ''), reverse=True)
            except BaseException:
                pass  # If sorting fails, continue with unsorted list

            for e in expenses:
                # e may be a Document which contains a doc_id attribute
                doc_id = getattr(e, 'doc_id', None)
                total += e["amount"]
                # Format the display text
                amount_text = f"ETB {e['amount']:.2f}"
                category_text = e['category']

                # Handle date field (for existing expenses that might not have
                # date)
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
                # Show selection prefix if selected
                try:
                    prefix = "[x] " if doc_id in (
                        self.selected_ids or set()) else ""
                    item.text = f"{prefix}{amount_text} - {category_text}"
                except Exception:
                    pass
                # Bind tap to toggle selection for multi-select
                try:
                    def _toggle(instance, did=doc_id):
                        self.toggle_select(did, instance)
                    item.bind(on_release=_toggle)
                except Exception:
                    pass
                main_screen.ids.expense_list.add_widget(item)

        # Update total label
        main_screen.ids.total_label.text = f'{_("total")}: ETB {total:.2f}'

        # Update select-all checkbox state
        try:
            all_doc_ids = set(getattr(d, 'doc_id', None) for d in expenses if getattr(d, 'doc_id', None) is not None)
            if hasattr(main_screen.ids, 'select_all_checkbox'):
                main_screen.ids.select_all_checkbox.active = (all_doc_ids and all_doc_ids == (self.selected_ids or set()))
        except Exception:
            pass

        # Ensure buttons visibility updated after list refresh
        try:
            self.update_action_buttons_visibility()
        except Exception:
            pass

    def toggle_select(self, doc_id, instance=None):
        """Toggle selection for a given document id and update the visual prefix."""
        if self.selected_ids is None:
            self.selected_ids = set()
        if doc_id in self.selected_ids:
            self.selected_ids.remove(doc_id)
            # update instance text to remove prefix
            try:
                if instance and instance.text.startswith('[x] '):
                    instance.text = instance.text[4:]
            except Exception:
                pass
        else:
            self.selected_ids.add(doc_id)
            try:
                if instance and not instance.text.startswith('[x] '):
                    instance.text = '[x] ' + instance.text
            except Exception:
                pass
        # Update action button visibility when selection changes
        try:
            self.update_action_buttons_visibility()
        except Exception:
            pass

    def update_action_buttons_visibility(self):
        """Show or hide action buttons (like delete) based on selection state."""
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
        try:
            has_selection = bool(self.selected_ids)
            # Delete selected button visible only when there are selections
            main_screen.ids.delete_selected_button.disabled = not has_selection
            main_screen.ids.delete_selected_button.opacity = 1.0 if has_selection else 0.0
        except Exception as e:
            Logger.error(f"UI: update_action_buttons_visibility failed: {e}")

    def toggle_select_all(self, checkbox_instance, value):
        """Select or deselect all expenses when the 'Select All' checkbox is toggled."""
        main_screen = self.get_main_screen()
        if main_screen is None:
            return
        try:
            if value:
                # select all doc_ids
                all_docs = db.all()
                self.selected_ids = set(getattr(d, 'doc_id', None) for d in all_docs if getattr(d, 'doc_id', None) is not None)
            else:
                self.selected_ids = set()
            # refresh list display so prefixes update
            self.update_list()
            self.update_action_buttons_visibility()
        except Exception as e:
            Logger.error(f"UI: toggle_select_all failed: {e}")

    def delete_selected(self):
        """Delete all selected expenses with confirmation dialog."""
        if not self.selected_ids:
            self.notify("ℹ️ No expenses selected. Tap on expenses to select them.")
            return
        
        count = len(self.selected_ids)
        
        def _confirm_delete(instance):
            try:
                # remove by doc_ids
                db.remove(doc_ids=list(self.selected_ids))
                self.selected_ids.clear()
                self.update_list()
                self.notify(f"✓ Deleted {count} expense(s)")
                Logger.info(f"DB: Deleted {count} selected expense(s)")
            except Exception as e:
                Logger.error(f"DB: delete_selected failed: {e}")
                self.notify(f"✗ Error deleting expenses: {e}")
            finally:
                confirm_dialog.dismiss()

        confirm_dialog = MDDialog(
            text=f"Delete {count} selected expense(s)? This cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="Yes, Delete",
                    on_release=_confirm_delete
                ),
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: confirm_dialog.dismiss()
                )
            ]
        )
        confirm_dialog.open()

    def confirm_delete(self, doc_id):
        """Show confirmation dialog before deleting a single expense."""
        if doc_id is None:
            self.notify("✗ Unable to identify this expense for deletion.")
            return

        def _do_delete(instance):
            try:
                db.remove(doc_ids=[doc_id])
                self.update_list()
                self.notify("✓ Expense deleted")
                Logger.info(f"DB: Single expense deleted (id: {doc_id})")
            except Exception as e:
                Logger.error(f"DB: delete failed: {e}")
                self.notify(f"✗ Failed to delete: {e}")
            d.dismiss()

        d = MDDialog(
            text="Are you sure you want to delete this expense?",
            buttons=[
                MDFlatButton(
                    text="Yes, Delete",
                    on_release=_do_delete
                ),
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: d.dismiss()
                )
            ]
        )
        d.open()

    def confirm_clear_database(self):
        """Ask user to confirm clearing the whole database."""
        def _do_clear(instance):
            try:
                self.clear_database()
                d.dismiss()
            except Exception as e:
                Logger.error(f"DB: Failed to clear database: {e}")
                self.notify(f"✗ Error: {e}")
                d.dismiss()

        d = MDDialog(
            text="⚠️  Delete ALL expenses? This action cannot be undone and will permanently remove all data.",
            buttons=[
                MDFlatButton(
                    text="Yes, Delete All",
                    on_release=_do_clear
                ),
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: d.dismiss()
                )
            ]
        )
        d.open()

    def clear_database(self):
        try:
            docs = db.all()
            doc_ids = [
                getattr(
                    d,
                    'doc_id',
                    None) for d in docs if getattr(
                    d,
                    'doc_id',
                    None) is not None]
            if doc_ids:
                try:
                    db.remove(doc_ids=doc_ids)
                except Exception:
                    # Fallback: remove by iterating
                    for did in doc_ids:
                        try:
                            db.remove(doc_ids=[did])
                        except Exception:
                            pass
            self.update_list()
            self.notify(f"✓ Database cleared ({len(doc_ids)} expenses deleted)")
            Logger.info(f"DB: Database cleared - removed {len(doc_ids)} expenses")
        except Exception as e:
            Logger.error(f"DB: clear failed: {e}")
            self.notify(f"✗ Failed to clear database: {e}")

    def export_database(self):
        try:
            data = db.all()
            if not data:
                self.notify("ℹ️ No data to export")
                return
            fname = f"expenses_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.notify(f"✓ Exported {len(data)} expense(s) to {fname}")
            Logger.info(f"DB: Exported {len(data)} expenses to {fname}")
        except Exception as e:
            Logger.error(f"Export failed: {e}")
            self.notify(f"✗ Export failed: {e}")


if __name__ == "__main__":
    ExpenseTrackerApp().run()
