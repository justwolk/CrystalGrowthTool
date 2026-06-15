import os
import json
from PySide2.QtCore import QStandardPaths, QObject, Signal
from PySide2.QtWidgets import QShortcut, QMessageBox
from PySide2.QtGui import QKeySequence

class HotkeyManager(QObject):
    
    hotkeyChanged = Signal(str, str)
    
    def __init__(self):
        super().__init__()
        self.settings_file = self._get_settings_file_path()
        self.default_hotkeys = {
            'openProject': 'Ctrl+O',
            'saveProject': 'Ctrl+S', 
            'closeProject': 'Ctrl+W',
            'cropImages': 'Ctrl+Shift+C',
            'saveExcel': 'Ctrl+E',
            'switchInterfaceMode': 'F1',
            'previousImage': 'Left',
            'nextImage': 'Right', 
            'selectCenter': 'V',
            'generateOnLayer': 'Ctrl+L',
            'generateOnImage': 'Ctrl+I',
            'generateAll': 'Ctrl+A',
            'addLayerPoint': '3',
            'moveLayerPoint': '4',
            'deleteLayerPoint': '5',
            'deleteLayer': 'Ctrl+D',
            'deleteLayerPoints': 'Ctrl+Shift+D',
            'deleteAllPoints': 'Ctrl+Del',
            'nextLayer': 'W',
            'previousLayer': 'Q',
            'zoomIn': 'Up',
            'zoomOut': 'Down'
        }
        self.hotkeys = self._load_hotkeys()
        self.save_hotkeys()
    
    def _get_settings_file_path(self):
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        app_settings_dir = os.path.join(documents_path, 'CrystalGrowthTool')
        if not os.path.exists(app_settings_dir):
            os.makedirs(app_settings_dir)
        return os.path.join(app_settings_dir, 'app_hotkeys.json')
    
    def _load_hotkeys(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_hotkeys = json.load(f)
                merged = self.default_hotkeys.copy()
                merged.update(saved_hotkeys)
                return merged
        except Exception as e:
            print(f"Ошибка загрузки хоткеев: {e}")
        return self.default_hotkeys.copy()
    
    def save_hotkeys(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotkeys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения хоткеев: {e}")
    
    def get_hotkey(self, action):
        return self.hotkeys.get(action, '')
    
    def find_conflicting_action(self, hotkey, exclude_action=None):
        if not hotkey:
            return None
        
        for key, value in self.hotkeys.items():
            if value == hotkey and key != exclude_action:
                return key
        return None
    
    def set_hotkey(self, action, hotkey, parent_widget=None):
        if not hotkey:
            self.hotkeys[action] = ''
            self.save_hotkeys()
            self.hotkeyChanged.emit(action, '')
            return True
        
        conflicting_action = self.find_conflicting_action(hotkey, action)
        
        if conflicting_action:
            msg_box = QMessageBox(parent_widget)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Конфликт горячих клавиш")
            msg_box.setText(
                f"Комбинация '{hotkey}' уже занята.\n\n"
                f"Освободить её для текущего действия?"
            )
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Да")
            msg_box.button(QMessageBox.No).setText("Нет")
            msg_box.setDefaultButton(QMessageBox.No)
            
            if msg_box.exec_() != QMessageBox.Yes:
                return False
            
            self.hotkeys[conflicting_action] = ''
            self.hotkeyChanged.emit(conflicting_action, '')
        
        self.hotkeys[action] = hotkey
        self.save_hotkeys()
        self.hotkeyChanged.emit(action, hotkey)
        return True

class HotkeyController(QObject):
    
    def __init__(self, main_window, hotkey_manager):
        super().__init__()
        self.main_window = main_window
        self.hotkey_manager = hotkey_manager
        self.shortcuts = {}
        self.hotkey_mappings = {}
        
        self.hotkey_manager.hotkeyChanged.connect(self.refresh_shortcuts)
    
    def setup_hotkeys(self, hotkey_mappings):
        self.hotkey_mappings = hotkey_mappings
        self.refresh_shortcuts()
    
    def refresh_shortcuts(self):
        for shortcut in self.shortcuts.values():
            shortcut.setParent(None)
        self.shortcuts.clear()
        
        for action, (key_edit, callback) in self.hotkey_mappings.items():
            self._setup_single_hotkey(action, key_edit, callback)
    
    def _setup_single_hotkey(self, action, key_edit, callback):
        try:
            hotkey_str = self.hotkey_manager.get_hotkey(action)
            
            if hotkey_str:
                key_edit.setKeySequence(QKeySequence(hotkey_str))
            else:
                key_edit.clear()
            
            if hotkey_str:
                shortcut = QShortcut(QKeySequence(hotkey_str), self.main_window)
                shortcut.activated.connect(callback)
                self.shortcuts[action] = shortcut
            
            try:
                key_edit.editingFinished.disconnect()
            except RuntimeError:
                pass
            
            key_edit.editingFinished.connect(lambda act=action, edit=key_edit: self._on_editing_finished(act, edit))
            
        except Exception as e:
            print(f"Ошибка установки хоткея {action}: {e}")
    
    def _on_editing_finished(self, action, key_edit):
        try:
            new_hotkey = key_edit.keySequence().toString()
            old_hotkey = self.hotkey_manager.get_hotkey(action)
            
            if new_hotkey == old_hotkey:
                return
            
            success = self.hotkey_manager.set_hotkey(action, new_hotkey, self.main_window)
            
            if not success:
                if old_hotkey:
                    key_edit.setKeySequence(QKeySequence(old_hotkey))
                else:
                    key_edit.clear()
            
        except Exception as e:
            print(f"Ошибка изменения хоткея {action}: {e}")
