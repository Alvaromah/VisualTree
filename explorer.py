import os
import sys
import logging
import markdown
import configparser

from typing import List, Tuple, Optional, Set, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QTextEdit, QToolBar, QWidget,
    QAction, QAbstractItemView, QSplitter, QMessageBox, QDialog, QFileDialog,
    QTabWidget, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QDir, QSize, QModelIndex, QObject, QSettings

# ----------------------------
# Helper Functions
# ----------------------------

def get_language_from_extension(ext: str) -> Optional[str]:
    """
    Map file extensions to programming languages for syntax highlighting.

    :param ext: File extension (e.g., '.py', '.js').
    :return: Corresponding language string or empty string if not found.
    """
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.json': 'json',
        '.html': 'html',
        '.qss': 'qss',
        '.vue': 'vue'
    }
    return mapping.get(ext.lower(), '')

# ----------------------------
# Models
# ----------------------------

class CheckableFileSystemModel(QFileSystemModel):
    def __init__(self, extensions: Optional[List[str]] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.checked_files: Set[str] = set()
        self.extensions = extensions or ['*.py', '*.js']
        self.setNameFilters(self.extensions)
        self.setNameFilterDisables(False)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemIsUserCheckable
        return flags

    def data(self, index: QModelIndex, role: int) -> Any:
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            return Qt.Checked if file_path in self.checked_files else Qt.Unchecked
        return super().data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        if role == Qt.CheckStateRole:
            file_path = self.filePath(index)
            if value == Qt.Checked:
                self.checked_files.add(file_path)
            else:
                self.checked_files.discard(file_path)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)

    def get_checked_files(self) -> List[str]:
        return list(self.checked_files)

    def update_extensions(self, new_extensions: List[str]) -> None:
        """
        Update the file extensions used for filtering.

        :param new_extensions: List of new file extension patterns (e.g., ['*.py', '*.js']).
        """
        self.extensions = new_extensions
        self.setNameFilters(self.extensions)
        self.setNameFilterDisables(False)
        # Clear checked files that no longer match the new extensions
        self.checked_files = {f for f in self.checked_files if any(fnmatch.fnmatch(f, pattern) for pattern in self.extensions)}
        self.layoutChanged.emit()

import fnmatch

class DirectoryFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, hidden_dirs: Optional[List[str]] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.hidden_dirs = hidden_dirs or ['__pycache__', '.git']

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        if model.isDir(index):
            dir_name = model.fileName(index)
            if dir_name in self.hidden_dirs:
                return False
        return super().filterAcceptsRow(source_row, source_parent)

# ----------------------------
# Views
# ----------------------------

class MarkdownView(QWidget):
    """
    A view to display markdown content rendered as HTML.
    """

    def __init__(self, font_size=12, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        font = QFont('Consolas', font_size)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_html_content(self, html_content: str) -> None:
        """
        Set the HTML content to be displayed in the text edit.

        :param html_content: The HTML string to display.
        """
        self.text_edit.setHtml(html_content)

    def set_font_size(self, font_size: int) -> None:
        """
        Update the font size of the text edit.

        :param font_size: The new font size to apply.
        """
        font = self.text_edit.font()
        font.setPointSize(font_size)
        self.text_edit.setFont(font)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_font_size=12, current_theme='Light', current_extensions=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 250)

        layout = QVBoxLayout()

        # Font Size
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Size:")
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 48)
        self.font_spin.setValue(current_font_size)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spin)
        layout.addLayout(font_layout)

        # Theme
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # File Extensions
        extensions_layout = QVBoxLayout()
        extensions_label = QLabel("File Extensions (comma-separated, e.g., *.py, *.js):")
        self.extensions_edit = QLineEdit(", ".join(current_extensions) if current_extensions else "")
        extensions_layout.addWidget(extensions_label)
        extensions_layout.addWidget(self.extensions_edit)
        layout.addLayout(extensions_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connections
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_settings(self):
        return {
            'font_size': self.font_spin.value(),
            'theme': self.theme_combo.currentText(),
            'file_extensions': [ext.strip() for ext in self.extensions_edit.text().split(",") if ext.strip()]
        }

# ----------------------------
# Views (continued)
# ----------------------------

class MainWindow(QMainWindow):
    """
    The main window of the File Concatenator application.

    Manages the user interface components, settings, and interactions.
    """

    # Embedded Dark Theme Stylesheet
    DARK_THEME_STYLESHEET = """
    /* Dark Theme Stylesheet */
    QMainWindow, QWidget, QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QTextEdit, QTreeView, QTabWidget::pane, QTabBar::tab:selected {
        background-color: #3c3f41;
        color: #ffffff;
        selection-background-color: #6c6c6c;
    }
    QTabBar::tab {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QToolBar {
        background-color: #2b2b2b;
        color: #ffffff;
        border-bottom: 1px solid #444;
    }
    QToolButton {
        background-color: #2b2b2b;
        color: #ffffff;
        border: none;
        padding: 5px;
    }
    QToolButton:hover {
        background-color: #3c3f41;
    }
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenuBar::item {
        background: transparent;
    }
    QMenuBar::item:selected {
        background: #3c3f41;
    }
    QMenu {
        background-color: #3c3f41;
        color: #ffffff;
    }
    QMenu::item:selected {
        background-color: #505357;
    }
    QPushButton {
        background-color: #4e4e4e;
        color: #ffffff;
    }
    QSpinBox, QComboBox, QLineEdit {
        background-color: #4e4e4e;
        color: #ffffff;
    }
    QScrollBar:vertical {
        background-color: #2b2b2b;
        width: 15px;
        margin: 22px 0 22px 0;
    }
    QScrollBar::handle:vertical {
        background-color: #5c5c5c;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: none;
    }
    """

    def __init__(self, settings, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("File Concatenator")
        self.resize(1200, 700)

        # Initialize settings
        self.settings = settings
        self.font_size = self.settings.value('font_size', 12, type=int)
        self.theme = self.settings.value('theme', 'Light', type=str)
        self.extensions = self.settings.value('file_extensions', ['*.py', '*.js'], type=list)
        self.hidden_dirs = self.settings.value('hidden_directories', ['__pycache__', '.git'], type=list)

        # Create actions
        self.create_actions()

        # Main layout with splitter
        splitter = QSplitter(Qt.Horizontal)

        # File system model
        self.model = CheckableFileSystemModel(self.extensions)
        self.model.setRootPath(QDir.currentPath())

        # Proxy model for filtering directories
        self.proxy_model = DirectoryFilterProxyModel(hidden_dirs=self.hidden_dirs)
        self.proxy_model.setSourceModel(self.model)

        # Directory tree view
        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        root_index = self.model.index(QDir.currentPath())
        proxy_root_index = self.proxy_model.mapFromSource(root_index)
        self.tree.setRootIndex(proxy_root_index)
        self.tree.setSelectionMode(QAbstractItemView.NoSelection)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.setHeaderHidden(True)
        splitter.addWidget(self.tree)

        # Expand the tree view on application start
        self.tree.expandAll()

        # Tab widget for multiple views
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)

        # Markdown view as first tab
        self.markdown_view = MarkdownView(font_size=self.font_size)
        self.tab_widget.addTab(self.markdown_view, "Markdown View")

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        self.setCentralWidget(splitter)

        # Toolbar
        self.create_toolbar()

        # Menu Bar
        self.create_menu()

        # Apply theme
        self.apply_theme()

        # Signal connections
        self.model.dataChanged.connect(self.update_text)

        self.showMaximized()

    def create_actions(self) -> None:
        """
        Create all QAction instances used in the application.
        """
        # Change Root Directory Action
        self.change_root_action = QAction(QIcon.fromTheme("folder-open"), "Change Root Directory", self)
        self.change_root_action.setStatusTip("Change the root directory")
        self.change_root_action.triggered.connect(self.change_root_directory)

        # Save Action
        self.save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        self.save_action.setStatusTip("Save concatenated content to file")
        self.save_action.triggered.connect(self.save_content)

        # Clear Action
        self.clear_action = QAction(QIcon.fromTheme("edit-clear"), "Clear Selection", self)
        self.clear_action.setStatusTip("Deselect all files")
        self.clear_action.triggered.connect(self.clear_selection)

        # Select All Action
        self.select_all_action = QAction(QIcon.fromTheme("edit-select-all"), "Select All", self)
        self.select_all_action.setStatusTip("Select all files")
        self.select_all_action.triggered.connect(self.select_all)

        # Copy Markdown Action
        self.copy_md_action = QAction(QIcon.fromTheme("edit-copy"), "Copy Markdown", self)
        self.copy_md_action.setStatusTip("Copy markdown content to clipboard")
        self.copy_md_action.triggered.connect(self.copy_markdown)

        # Copy Plain Text Action
        self.copy_text_action = QAction(QIcon.fromTheme("edit-copy"), "Copy Plain Text", self)
        self.copy_text_action.setStatusTip("Copy plain text content to clipboard")
        self.copy_text_action.triggered.connect(self.copy_plain_text)

        # Exit Action
        self.exit_action = QAction("Exit", self)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)

        # Settings Action
        self.settings_action = QAction("Settings", self)
        self.settings_action.setStatusTip("Configure application settings")
        self.settings_action.triggered.connect(self.open_settings_dialog)

        # About Action
        self.about_action = QAction("About", self)
        self.about_action.setStatusTip("About this application")
        self.about_action.triggered.connect(self.show_about_dialog)

    def create_toolbar(self) -> None:
        """
        Create the main toolbar and add pre-created actions.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Add actions to the toolbar
        toolbar.addAction(self.clear_action)
        toolbar.addAction(self.select_all_action)
        toolbar.addAction(self.copy_md_action)

    def create_menu(self) -> None:
        """
        Create the menu bar with actions.
        """
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        file_menu.addAction(self.change_root_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.select_all_action)
        edit_menu.addAction(self.clear_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.copy_md_action)
        edit_menu.addAction(self.copy_text_action)

        # View Menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.settings_action)

        # Help Menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(self.about_action)

    def show_about_dialog(self) -> None:
        """
        Show the About dialog.
        """
        QMessageBox.about(self, "About File Concatenator",
                          "File Concatenator Application\nVersion 1.0\n\nDeveloped by Alvaro Mateos.")

    def clear_selection(self) -> None:
        """
        Deselects all files by unchecking them.
        Before performing the operation, expand all tree nodes to ensure all files are accessible.
        """
        self.tree.expandAll()
        for file_path in list(self.model.checked_files):
            index = self.model.index(file_path)
            if index.isValid():
                self.model.setData(index, Qt.Unchecked, Qt.CheckStateRole)

    def select_all(self) -> None:
        """
        Selects (checks) all eligible files in the model, including those in collapsed folders.
        Before performing the operation, expand all tree nodes to ensure all files are accessible.
        """
        self.tree.expandAll()
        # Retrieve the root index from the source model to ensure all directories are traversed
        root_path = self.model.rootPath()
        root_index = self.model.index(root_path)
        self._traverse_and_set(root_index, Qt.Checked)

    def _traverse_and_set(self, parent_index: QModelIndex, check_state: Qt.CheckState) -> None:
        """
        Recursively traverses the model and sets the check state for each file.
        This method ensures that all files are selected, regardless of their visibility in the view.

        :param parent_index: The parent index to start traversal.
        :param check_state: The check state to set (Qt.Checked or Qt.Unchecked).
        """
        for row in range(self.model.rowCount(parent_index)):
            index = self.model.index(row, 0, parent_index)
            if not index.isValid():
                continue

            if self.model.isDir(index):
                # If it's a directory, traverse its children
                self._traverse_and_set(index, check_state)
            else:
                # If it's a file, set its check state
                self.model.setData(index, check_state, Qt.CheckStateRole)

    def copy_markdown(self) -> None:
        """
        Copy markdown content to the clipboard.
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.markdown_content)
        # QMessageBox.information(self, "Copied", "Markdown content copied to clipboard.")

    def copy_plain_text(self) -> None:
        """
        Copy plain text content to the clipboard.
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.plain_text_content)
        # QMessageBox.information(self, "Copied", "Plain text content copied to clipboard.")

    def save_content(self) -> None:
        """
        Save the concatenated content to a file.
        """
        options = QFileDialog.Options()
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Concatenated Content",
            "",
            "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)",
            options=options
        )
        if file_name:
            try:
                if file_name.endswith('.md') or selected_filter == "Markdown Files (*.md)":
                    content_to_save = self.markdown_content
                else:
                    content_to_save = self.plain_text_content
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)
                QMessageBox.information(self, "Saved", f"Content saved to {file_name}.")
            except Exception as e:
                logging.error(f"Error saving file {file_name}: {e}")
                QMessageBox.critical(self, "Save Error", f"Could not save file: {e}")

    def change_root_directory(self) -> None:
        """
        Change the root directory of the file system model.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Root Directory", QDir.currentPath())
        if directory:
            self.model.setRootPath(directory)
            proxy_root_index = self.proxy_model.mapFromSource(self.model.index(directory))
            self.tree.setRootIndex(proxy_root_index)
            self.update_text()

    def open_settings_dialog(self) -> None:
        """
        Open the settings dialog to configure application settings.
        """
        dialog = SettingsDialog(
            self,
            current_font_size=self.font_size,
            current_theme=self.theme,
            current_extensions=self.extensions
        )
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.font_size = new_settings['font_size']
            self.theme = new_settings['theme']
            new_extensions = new_settings.get('file_extensions', self.extensions)

            # Update extensions in settings
            self.settings.setValue('file_extensions', new_extensions)

            # Update the model with new extensions
            self.model.update_extensions(new_extensions)

            self.theme = new_settings['theme']
            self.apply_settings()

            # Save other settings
            self.settings.setValue('font_size', self.font_size)
            self.settings.setValue('theme', self.theme)

            # Update the text view after changing extensions
            self.update_text()

    def apply_settings(self) -> None:
        """
        Apply the current settings to the UI components.
        """
        # Apply font size
        self.markdown_view.set_font_size(self.font_size)

        # Apply theme
        self.apply_theme()

    def apply_theme(self) -> None:
        """
        Apply the selected theme to the application.
        """
        if self.theme == 'Dark':
            self.setStyleSheet(self.DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet("")  # Reset to default

    def update_text(self) -> None:
        """
        Update the concatenated text in the markdown view based on checked files.
        """
        self.markdown_content, self.plain_text_content = concatenate_files(self.model.get_checked_files())
        html_content = markdown.markdown(self.markdown_content, extensions=['fenced_code'])
        self.markdown_view.set_html_content(html_content)

# ----------------------------
# Utilities
# ----------------------------

def concatenate_files(file_paths: List[str]) -> Tuple[str, str]:
    """
    Concatenate the contents of the given files into markdown and plain text formats.

    :param file_paths: List of file paths to concatenate.
    :return: A tuple containing markdown content and plain text content.
    """
    markdown_content = ''
    plain_text_content = ''
    for file_path in file_paths:
        if file_path.endswith('explorer.py'):
            continue
        rel_path = os.path.relpath(file_path)
        file_ext = os.path.splitext(file_path)[1]
        language = get_language_from_extension(file_ext)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                file_content = file_content or "TODO"
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            continue  # Skip this file
        # Append markdown
        markdown_content += f"## `{rel_path}`\n```{language}\n{file_content}\n```\n\n"
        # Append plain text
        plain_text_content += f"{rel_path}\n{file_content}\n\n"
    return markdown_content, plain_text_content

# ----------------------------
# Controller
# ----------------------------

class AppController:
    def __init__(self):
        self.settings = QSettings('MyCompany', 'FileConcatenatorApp')
        self.main_window = MainWindow(self.settings)

    def show_main_window(self):
        self.main_window.show()

# ----------------------------
# Main Entry Point
# ----------------------------

def main():
    # Configure logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    controller = AppController()
    controller.show_main_window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
