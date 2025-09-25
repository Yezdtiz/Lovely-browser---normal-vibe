import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import QWebChannel

# Set environment variables to enable proprietary codecs for video and audio.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-proprietary-media-audios"


def get_app_icon():
    """
    Attempts to load the .ico file first. If it doesn't exist,
    it falls back to the .png file. This is a robust way to handle icons.
    """
    ICON_DIR = 'src/icons'
    ICON_BASE_NAME = 'icon'
    
    # Define the full paths for both options
    ico_path = os.path.join(ICON_DIR, f"{ICON_BASE_NAME}.ico")
    png_path = os.path.join(ICON_DIR, f"{ICON_BASE_NAME}.png")
    
    # Try the primary (.ico) path first
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    
    # Fall back to the secondary (.png) path
    elif os.path.exists(png_path):
        return QIcon(png_path)
    
    # If neither file exists, return a default/null icon
    else:
        print("Warning: Neither .ico nor .png icon file found. Using default.")
        return QIcon()


class CustomWebEnginePage(QWebEnginePage):
    """
    Custom page to handle link clicks directly in Python.
    """
    newTabRequested = pyqtSignal(QUrl)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mouseButton = Qt.NoButton  # Initialize mouseButton to avoid errors

    def acceptNavigationRequest(self, qurl, nav_type, is_main_frame):
        # Intercept middle-click on a link
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # Check if the button pressed was the middle mouse button
            if self.mouseButton == Qt.MiddleButton:
                self.newTabRequested.emit(qurl)
                return False  # Prevent the current tab from navigating
        return super().acceptNavigationRequest(qurl, nav_type, is_main_frame)

    def mousePressEvent(self, event):
        self.mouseButton = event.button()
        super().mousePressEvent(event)

class BrowserTab(QWidget):
    
    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        
        self.layout = QVBoxLayout(self)
        self.horizontal = QHBoxLayout()
        
        self.back_btn = QPushButton("<")
        self.forward_btn = QPushButton(">")
        self.url_bar = QLineEdit()
        self.go_btn = QPushButton("Go")
        self.reload_btn = QPushButton("Reload")

        self.back_btn.setFixedSize(32, 32)
        self.forward_btn.setFixedSize(32, 32)
        self.go_btn.setFixedSize(40, 32)
        self.reload_btn.setFixedSize(60, 32)
        
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)
        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)
        self.horizontal.addWidget(self.reload_btn)

        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self.browser)
        self.browser.setPage(self.page)

        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.browser)
        
        self.go_btn.clicked.connect(self.navigate)
        self.url_bar.returnPressed.connect(self.navigate)
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadFinished.connect(self.update_title)
        
        self.browser.setUrl(QUrl("https://google.com"))

    def navigate(self):
        url = self.url_bar.text().strip()
        
        # Check if the URL already has a protocol.
        if url.startswith("http://") or url.startswith("https://") or url.startswith("file:///"):
            final_url = url
        # Check if the URL has a dot with at least one character after it.
        elif '.' in url and len(url.split('.')[-1]) > 0:
            final_url = "https://" + url
        else:
            # Use the selected search engine for the query.
            search_engine = self.settings_manager.default_search_engine
            search_query = url.replace(" ", "+")
            if search_engine == "Google":
                final_url = f"https://www.google.com/search?q={search_query}"
            elif search_engine == "Bing":
                final_url = f"https://www.bing.com/search?q={search_query}"
            elif search_engine == "DuckDuckGo":
                final_url = f"https://duckduckgo.com/?q={search_query}"
            elif search_engine == "Yahoo":
                final_url = f"https://search.yahoo.com/search?p={search_query}"
            else: # Default to Google if something goes wrong
                final_url = f"https://www.google.com/search?q={search_query}"
            
        self.browser.setUrl(QUrl(final_url))

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)

    def update_title(self, success):
        if success:
            tab_widget = self.parentWidget()
            if isinstance(tab_widget, QTabWidget):
                index = tab_widget.indexOf(self)
                title = self.browser.page().title()
                tab_widget.setTabText(index, title or "New Tab")

class SettingsDialog(QDialog):
    """
    A dialog for the browser settings.
    """
    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)
        self.settings_manager = settings_manager
        
        self.main_layout = QVBoxLayout(self)
        
        # Theme Mode section
        self.theme_group = QGroupBox("Theme Mode")
        self.theme_layout = QHBoxLayout()
        self.light_mode_btn = QRadioButton("Light")
        self.dark_mode_btn = QRadioButton("Dark")
        self.theme_layout.addWidget(self.light_mode_btn)
        self.theme_layout.addWidget(self.dark_mode_btn)
        self.theme_group.setLayout(self.theme_layout)
        
        # Search Engine section
        self.search_group = QGroupBox("Default Search Engine")
        self.search_layout = QHBoxLayout()
        self.search_dropdown = QComboBox()
        self.search_dropdown.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo"])
        self.search_layout.addWidget(self.search_dropdown)
        self.search_group.setLayout(self.search_layout)

        # Apply button
        self.apply_btn = QPushButton("Apply")

        self.main_layout.addWidget(self.theme_group)
        self.main_layout.addWidget(self.search_group)
        self.main_layout.addWidget(self.apply_btn)

        self.apply_btn.clicked.connect(self.apply_settings)
        
        # Set initial values based on the settings manager
        if self.settings_manager.current_theme == "dark":
            self.dark_mode_btn.setChecked(True)
        else:
            self.light_mode_btn.setChecked(True)
            
        self.search_dropdown.setCurrentText(self.settings_manager.default_search_engine)

    def apply_settings(self):
        # Update settings in the main window
        if self.dark_mode_btn.isChecked():
            self.settings_manager.current_theme = "dark"
        else:
            self.settings_manager.current_theme = "light"
            
        self.settings_manager.default_search_engine = self.search_dropdown.currentText()
        
        # Apply the new theme to the main window
        self.settings_manager.toggle_theme(self.settings_manager.current_theme)
        
        self.accept()

class MyWebBrowser(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_theme = "light"
        self.default_search_engine = "Google"

        # --- FIX: Use the new function to set the window icon with fallback ---
        self.setWindowIcon(get_app_icon())
        # ---------------------------------------------------------------------

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        self.setCentralWidget(self.tabs)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.add_tab_btn = QPushButton('+')
        self.add_tab_btn.clicked.connect(self.add_new_tab)
        
        # Modern settings button icon
        self.settings_btn = QPushButton('⋮') 
        self.settings_btn.clicked.connect(self.open_settings)
        
        self.toggle_theme(self.current_theme)
        
        self.add_tab_btn.setObjectName("add_tab_btn")
        self.settings_btn.setObjectName("settings_btn")

        self.top_right_widget = QWidget()
        self.top_right_layout = QHBoxLayout(self.top_right_widget)
        self.top_right_layout.setContentsMargins(0, 0, 0, 0)
        
        # New tab button before settings button
        self.top_right_layout.addWidget(self.add_tab_btn)
        self.top_right_layout.addWidget(self.settings_btn)
        
        self.tabs.setCornerWidget(self.top_right_widget, Qt.Corner.TopRightCorner)

        self.add_new_tab(QUrl('https://google.com/'), 'Homepage')
        self.add_new_tab(QUrl("https://github.com/Yezdtiz/"), "My projects :P")
        
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.setMovable(True)
        
        self.setWindowTitle("Python Browser")
        self.setMinimumSize(1024, 768)
        self.show()

    def toggle_theme(self, mode):
        if mode == "dark":
            dark_stylesheet = """
                QWidget {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                QTabWidget::pane {
                    border: 1px solid #333;
                    background-color: #1a1a1a;
                }
                QTabBar::tab {
                    background-color: #333;
                    color: #e0e0e0;
                    border: 1px solid #444;
                    border-bottom-color: #333;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #1a1a1a;
                    border-bottom-color: #1a1a1a;
                }
                QTabBar::tab:hover {
                    background-color: #2a2a2a;
                }
                QPushButton {
                    background-color: #333;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 6px;
                    font-family: Arial;
                    font-size: 14px;
                    color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #444;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QLineEdit {
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-family: Arial;
                    font-size: 14px;
                    color: #e0e0e0;
                }
                QLineEdit:focus {
                    border: 1px solid #66A3FF;
                }
                #add_tab_btn {
                    background-color: #66A3FF;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 18px;
                    padding: 4px 6px;
                }
                #add_tab_btn:hover {
                    background-color: #558ED4;
                }
                #add_tab_btn:pressed {
                    background-color: #4477A9;
                }
                #settings_btn {
                    background-color: transparent; 
                    border: none;
                    font-size: 24px; 
                    color: #e0e0e0; 
                    padding: 4px 6px;
                    border-radius: 12px; 
                }
                #settings_btn:hover {
                    background-color: #444;
                }
                #settings_btn:pressed {
                    background-color: #2a2a2a;
                }
                QGroupBox {
                    font-weight: bold;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                }
                QComboBox {
                    background-color: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSIjRTAwRTAwIiBkPSJNOCA5LjVMMy41IDUuNWwxLTFoNS0xLjIgMS41IDQuNVoiLz48L2N2Zz4=);
                }
                QComboBox QAbstractItemView {
                    background-color: #2a2a2a;
                    color: #e0e0e0;
                    border: 1px solid #444;
                    selection-background-color: #66A3FF;
                }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            light_stylesheet = """
                QWidget {
                    background-color: #F0F2F5;
                    color: #333;
                }
                QTabWidget::pane {
                    border: 1px solid #D4DCE3;
                    background-color: #F0F2F5;
                }
                QTabBar::tab {
                    background-color: #E8F0F5;
                    color: #333;
                    border: 1px solid #D4DCE3;
                    border-bottom-color: #E8F0F5;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #F0F2F5;
                    border-bottom-color: #F0F2F5;
                }
                QTabBar::tab:hover {
                    background-color: #DAE3EB;
                }
                QPushButton {
                    background-color: #E8F0F5;
                    border: 1px solid #D4DCE3;
                    border-radius: 6px;
                    padding: 6px;
                    font-family: Arial;
                    font-size: 14px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #DAE3EB;
                }
                QPushButton:pressed {
                    background-color: #C6D0DB;
                }
                QLineEdit {
                    background-color: #F0F2F5;
                    border: 1px solid #D4DCE3;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-family: Arial;
                    font-size: 14px;
                    color: #333;
                }
                QLineEdit:focus {
                    border: 1px solid #66A3FF;
                }
                #add_tab_btn {
                    background-color: #66A3FF;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 18px;
                    padding: 4px 6px;
                }
                #add_tab_btn:hover {
                    background-color: #558ED4;
                }
                #add_tab_btn:pressed {
                    background-color: #4477A9;
                }
                #settings_btn {
                    background-color: transparent; 
                    border: none;
                    font-size: 24px; 
                    color: #333; 
                    padding: 4px 6px;
                    border-radius: 12px; 
                }
                #settings_btn:hover {
                    background-color: #DAE3EB;
                }
                #settings_btn:pressed {
                    background-color: #C6D0DB;
                }
                QGroupBox {
                    font-weight: bold;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                }
                QComboBox {
                    background-color: #E8F0F5;
                    border: 1px solid #D4DCE3;
                    border-radius: 4px;
                    padding: 4px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSIjMzMzMzMzIiBkPSJNOCA5LjVMMy41IDUuNWwxLTFoNS0xLjIgMS41IDQuNVoiLz48L2N2Zz4=);
                }
                QComboBox QAbstractItemView {
                    background-color: #E8F0F5;
                    color: #333;
                    border: 1px solid #D4DCE3;
                    selection-background-color: #66A3FF;
                }
            """
            self.setStyleSheet(light_stylesheet)

    def open_settings(self):
        # Open the settings dialog
        dialog = SettingsDialog(parent=self, settings_manager=self)
        dialog.exec_()
        
    # FIX: Safely check for unexpected signal arguments (like tab index or boolean) 
    # and default to a new tab behavior.
    def add_new_tab(self, qurl_or_bool_or_int=None, title="New Tab"):
        
        qurl = None
        if isinstance(qurl_or_bool_or_int, QUrl):
            qurl = qurl_or_bool_or_int
        
        # If no URL is provided (from '+' button or tab double-click on empty space),
        # use a default URL.
        if qurl is None:
            qurl = QUrl('https://google.com/') 
            title = "New Tab"

        # Create a new BrowserTab widget
        browser_tab = BrowserTab(settings_manager=self)
        
        # Use the determined URL
        browser_tab.browser.setUrl(qurl)
        
        # Connect the custom signal for opening new tabs
        browser_tab.page.newTabRequested.connect(self.add_new_tab)
        
        # Add the tab to the QTabWidget
        i = self.tabs.addTab(browser_tab, title)
        self.tabs.setCurrentIndex(i)

    def tab_open_doubleclick(self, index):
        if index == -1: # Double-clicked on the empty space
            # Call add_new_tab without arguments, not passing the index
            self.add_new_tab() 

    def current_tab_changed(self, index):
        if self.tabs.currentWidget():
            qurl = self.tabs.currentWidget().browser.url()
            title = self.tabs.currentWidget().browser.page().title()
            self.setWindowTitle("Python Browser - " + title)
            self.tabs.currentWidget().update_url_bar(qurl)
        
    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

app = QApplication(sys.argv)
window = MyWebBrowser()
app.exec_()
