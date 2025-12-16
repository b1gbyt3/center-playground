import sys
from datetime import datetime, timedelta
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QGraphicsView,
    QGraphicsScene, QMessageBox # Added QMessageBox for completeness, though not strictly used in this mock
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPolygonF, QFont, QPainter, QPainterPath, QResizeEvent
)

# --- Design Constants ---
COLOR_BG = QColor("#2F2F2F")       
COLOR_LINE = QColor("#3272AE")     
COLOR_NODE_Border = QColor("#e0e0e0") 
COLOR_TEXT_HEADER = QColor("#ffffff")
COLOR_TEXT_USER = QColor("#7b7766")   
COLOR_TEXT_TASK = QColor("#ffffff")

COLOR_RED = QColor("#C53F3F")      
COLOR_GREEN = QColor("#529850")    
COLOR_ORANGE = QColor("#d25b35")   
COLOR_BLACK = QColor("#000000")    

# --- User-Specified Button Colors (Used in LoginScreen and MonitoringScreen) ---
COLOR_START_MONITORING_ENABLED = QColor("#4c8e35") # Requested Start Color
COLOR_STOP_MONITORING = QColor("#a63c3a")         # Requested Stop Color
COLOR_BUTTON_DISABLED = QColor("#d0d0d0")         # Standard disabled grey

FONT_HEADER = QFont("Arial", 10, QFont.Weight.Bold)
FONT_USER = QFont("Arial", 22, QFont.Weight.Bold)
FONT_TASK = QFont("Arial", 11, QFont.Weight.Bold)

REPORT_SHIFT = "swing" # Shift to display on the visualization

# --- Logical Coordinates ---
STATION_CONFIG = {
    # Top Row (Y=200)
    "Shaving":     {"pos": (250, 200), "shape": "circle", "layout": "top", "tasks": ["Workstation Setup", "Verify Open Documents", "Perform Process"]},
    "Lamination":  {"pos": (550, 200), "shape": "circle", "layout": "top", "tasks": ["Workstation Setup", "Equipment Setup", "Perform Process"]},
    "Prep":        {"pos": (850, 200), "shape": "circle", "layout": "top", "tasks": ["Workstation Setup", "Equipment Setup", "Issue Floor Stock", "Material Verification", "Perform Process"]},
    "DDT":         {"pos": (1150, 200),"shape": "circle", "layout": "top", "tasks": ["Workstation Setup", "Equipment Setup", "Issue Floor Stock", "Material Verification", "Perform Process"]},
    
    # Left Middle (Y=500)
    "Wireloading": {"pos": (250, 500), "shape": "circle", "layout": "left","tasks": ["Workstation Setup", "Equipment Setup", "Material Verification", "Perform Process"]},
    
    # Bottom Row (Y=800)
    "Crimp":       {"pos": (250, 800), "shape": "circle", "layout": "bottom", "tasks": ["Workstation Setup", "Equipment Setup", "Material Verification", "Perform Process"]},
    "Bump":        {"pos": (550, 800), "shape": "circle", "layout": "bottom", "tasks": ["Workstation Setup", "Equipment Setup", "Material Verification", "Perform Process"]},
    "QC":          {"pos": (850, 800), "shape": "triangle","layout": "bottom", "tasks": ["Workstation Setup", "Verify LHC and Docs", "Perform Process"]},
    "Shipping":    {"pos": (1150, 800),"shape": "square",  "layout": "bottom", "tasks": ["Workstation Setup", "Verify Open Documents", "Perform Process"]}
}

# --- Mapping for Data Integration ---
STATION_MAPPING = {
    "DA-1181_MQI-24751": "Wireloading", 
    "MQI-24747_03": "Prep",
    "MQI-24748_03": "DDT",
    "MQI-24749_04": "Lamination",
    "MQI-24750_03": "Shaving",
    "MQI-24752_04": "Crimp",
    "MQI-24753_03": "Bump",
    "MQI-24803_03": "Shipping",
    "MQI-2565_QC_Insp_05": "QC"
}

# --- Mock Data Structure (list of dicts) ---
MOCK_RAW_DATA = [
  {
    "DA-1181_MQI-24751": {
      "day": {
        "employee": "CGuzmanSuarez",
        "task_completed": [
          "Equipment Setup", "Material Verification", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 4
      },
      "swing": {
        "employee": "SmithJ", 
        "task_completed": ["Equipment Setup"],
        "total_passed": 1
      }
    }
  },
  {
    "MQI-24747_03": {
      "day": {
        "employee": "vphosakham",
        "task_completed": [
          "Equipment Setup", "Issue Floor Stock", "Material Verification", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 5
      },
      "swing": {
        "employee": "",
        "task_completed": [],
        "total_passed": 0
      }
    }
  },
  {
    "MQI-24748_03": {
      "day": {
        "employee": "ibabenko",
        "task_completed": [
          "Equipment Setup", "Issue Floor Stock", "Material Verification", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 5
      },
      "swing": {
        "employee": "BakerA",
        "task_completed": ["Workstation Setup", "Equipment Setup", "Issue Floor Stock", "Material Verification", "Perform Process"],
        "total_passed": 5
      }
    }
  },
  {
    "MQI-24749_04": {
      "day": {
        "employee": "souk",
        "task_completed": [
          "Equipment Setup", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 3
      },
      "swing": {
        "employee": "ChenL",
        "task_completed": ["Equipment Setup", "Perform Process"],
        "total_passed": 2
      }
    }
  },
  {
    "MQI-24750_03": {
      "day": {
        "employee": "SLutfi",
        "task_completed": [
          "Perform Process", "Verify Open Documents", "Workstation Setup"
        ],
        "total_passed": 3
      },
      "swing": {
        "employee": "DavidsM",
        "task_completed": [],
        "total_passed": 0
      }
    }
  },
  {
    "MQI-24752_04": {
      "day": {
        "employee": "JCafe",
        "task_completed": [
          "Equipment Setup", "Material Verification", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 4
      },
      "swing": {
        "employee": "RiveraK",
        "task_completed": ["Workstation Setup", "Equipment Setup", "Material Verification"],
        "total_passed": 3
      }
    }
  },
  {
    "MQI-24753_03": {
      "day": {
        "employee": "aezeli",
        "task_completed": [
          "Equipment Setup", "Material Verification", "Perform Process", "Workstation Setup"
        ],
        "total_passed": 4
      },
      "swing": {
        "employee": "",
        "task_completed": [],
        "total_passed": 0
      }
    }
  },
  {
    "MQI-24803_03": {
      "day": {
        "employee": "souk",
        "task_completed": [
          "Perform Process", "Verify Open Documents", "Workstation Setup"
        ],
        "total_passed": 3
      },
      "swing": {
        "employee": "LeeH",
        "task_completed": ["Workstation Setup"],
        "total_passed": 1
      }
    }
  },
  {
    "MQI-2565_QC_Insp_05": {
      "day": {
        "employee": "tafu",
        "task_completed": [
          "Perform Process", "Verify LHC and Docs", "Workstation Setup"
        ],
        "total_passed": 3
      },
      "swing": {
        "employee": "AliZ",
        "task_completed": ["Workstation Setup", "Verify LHC and Docs"],
        "total_passed": 2
      }
    }
  }
]

def update_timestamp(last_check_time: datetime) -> str:
    """Formats the current time string as: MM/DD/YYYY HH:SS AM/PM."""
    now = datetime.now()
    return now.strftime("%m/%d/%Y %I:%M:%S %p")

class StationNode:
    """Represents a single station's visual element and data."""
    def __init__(self, name, config, scene):
        self.name = name
        self.config = config
        self.scene = scene
        self.x, self.y = config["pos"]
        self.shape = config["shape"]
        self.layout_type = config["layout"]
        
        self.node_size = 70
        self.status = "no_employee" 
        self.employee = "Waiting..."
        self.tasks = {task: False for task in config["tasks"]}
        
        self.items = []
        self.create_graphics()
    
    def clear_graphics(self):
        for item in self.items:
            if item.scene():
                self.scene.removeItem(item)
        self.items = []

    def create_graphics(self):
        self.clear_graphics()

        # 1. Shape and Color Logic
        border_pen = QPen(COLOR_NODE_Border, 5)
        fill_color = COLOR_BLACK # Default to Black (Logged In, but no tasks)
        if self.status == "no_employee": fill_color = COLOR_RED
        elif self.status == "in_progress": fill_color = COLOR_ORANGE
        elif self.status == "completed": fill_color = COLOR_GREEN

        shape_brush = QBrush(fill_color)
        
        # --- Node Drawing ---
        if self.shape == "circle":
            shape_item = self.scene.addEllipse(self.x - self.node_size/2, self.y - self.node_size/2, self.node_size, self.node_size, border_pen, shape_brush)
        elif self.shape == "square":
            shape_item = self.scene.addRect(self.x - self.node_size/2, self.y - self.node_size/2, self.node_size, self.node_size, border_pen, shape_brush)
        elif self.shape == "triangle":
            h = self.node_size
            points = QPolygonF([QPointF(self.x, self.y - h/1.5), QPointF(self.x - h/1.5, self.y + h/2), QPointF(self.x + h/1.5, self.y + h/2)])
            shape_item = self.scene.addPolygon(points, border_pen, shape_brush)
        
        shape_item.setZValue(2)
        self.items.append(shape_item)

        # 2. Text Content (Created at (0, 0) and positioned later)
        text_group_items = []
        
        header_txt = self.scene.addText(f"{self.name}:")
        header_txt.setDefaultTextColor(COLOR_TEXT_HEADER)
        header_txt.setFont(FONT_HEADER)
        text_group_items.append(header_txt)
        
        user_txt = self.scene.addText(self.employee)
        user_txt.setDefaultTextColor(COLOR_TEXT_USER)
        user_txt.setFont(FONT_USER)
        user_txt.setPos(0, header_txt.boundingRect().height() - 5)
        text_group_items.append(user_txt)
        
        current_y = user_txt.pos().y() + user_txt.boundingRect().height() + 5
        
        for task_name, is_done in self.tasks.items():
            dot_color = COLOR_GREEN if is_done else COLOR_RED
            dot = self.scene.addEllipse(0, 0, 16, 16, QPen(Qt.PenStyle.NoPen), QBrush(dot_color))
            dot.setPos(0, current_y + 4)
            text_group_items.append(dot)
            
            t_txt = self.scene.addText(task_name)
            t_txt.setDefaultTextColor(COLOR_TEXT_TASK)
            t_txt.setFont(FONT_TASK)
            t_txt.setPos(25, current_y)
            text_group_items.append(t_txt)
            current_y += 25

        self.items.extend(text_group_items)

        # 3. Layout Positioning
        max_width = max(item.boundingRect().width() + item.x() for item in text_group_items)
        text_block_height = current_y
        vertical_offset_to_center = self.y - (text_block_height / 2)

        if self.layout_type == "top":
            start_x = self.x - max_width / 2
            SPACING = 20
            start_y = self.y - self.node_size/2 - SPACING - text_block_height 
            
            for item in text_group_items:
                if item is header_txt or item is user_txt:
                    offset_x = (max_width - item.boundingRect().width()) / 2
                    item.setPos(start_x + offset_x, start_y + item.y())
                else:
                    item.setPos(start_x + item.x(), start_y + item.y())

        elif self.layout_type == "bottom":
            start_x = self.x - max_width / 2 
            SPACING = 20
            start_y = self.y + self.node_size/2 + SPACING

            for item in text_group_items:
                if item is header_txt or item is user_txt:
                    offset_x = (max_width - item.boundingRect().width()) / 2
                    item.setPos(start_x + offset_x, start_y + item.y())
                else:
                    item.setPos(start_x + item.x(), start_y + item.y())
        
        elif self.layout_type == "left":
            SPACING = 30 
            start_x = self.x - self.node_size/2 - SPACING - max_width 
            start_y = vertical_offset_to_center 
            
            for item in text_group_items:
                item.setPos(item.x() + start_x, item.y() + start_y)

    def update_status(self, employee, tasks_completed):
        """Updates the node's data and triggers a redraw."""
        self.employee = employee if employee else "Waiting..."
        for task in self.tasks: self.tasks[task] = task in tasks_completed
        
        if not employee: self.status = "no_employee"
        elif all(self.tasks.values()): self.status = "completed"
        elif any(self.tasks.values()): self.status = "in_progress"
        else: self.status = "logged_in"
        self.create_graphics()

class ResizableGraphicsView(QGraphicsView):
    """Custom view that handles resize events to refit the scene"""
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.scene():
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class MonitoringScreen(QWidget):
    """
    Simulates the monitoring screen, refreshing data from the mock structure 
    using a QTimer instead of a Selenium thread.
    """
    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self.stations = {}
        self.last_check_time = datetime.now() 
        self.timer = QTimer()
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # -- Header --
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {COLOR_BG.name()}; padding: 10px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        self.container_label = QLabel(f"Container: {self.container}")
        self.container_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.last_checked_label = QLabel("Last Checked: --")
        self.last_checked_label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        
        header_layout.addWidget(self.container_label)
        header_layout.addStretch()
        header_layout.addWidget(self.last_checked_label)
        
        layout.addWidget(header_widget)
        
        # -- Graphics View --
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(COLOR_BG))
        self.scene.setSceneRect(0, 0, 1400, 1000)
        
        self.view = ResizableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("border: none; background-color: #2F2F2F;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.draw_workflow_lines()
        
        for name, config in STATION_CONFIG.items():
            self.stations[name] = StationNode(name, config, self.scene)

        bounds = self.scene.itemsBoundingRect()
        buffer = 20
        self.scene.setSceneRect(bounds.adjusted(-buffer, -buffer, buffer, buffer))

        layout.addWidget(self.view)
        
        # -- Footer Button -- 
        footer_widget = QWidget()
        footer_widget.setStyleSheet(f"background-color: {COLOR_BG.name()};")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 10, 20, 20)
        footer_layout.addStretch()
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_STOP_MONITORING.name()};
                color: white; 
                font-weight: bold;
                font-size: 16px;
                padding: 12px 40px;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {COLOR_STOP_MONITORING.darker(120).name()}; }}
        """)
        footer_layout.addWidget(self.stop_button)
        footer_layout.addStretch()
        layout.addWidget(footer_widget)
        
        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, lambda: self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio))

    def draw_workflow_lines(self):
        path = QPainterPath()
        s = STATION_CONFIG
        
        # Draw the workflow path between stations
        path.moveTo(s["Shaving"]["pos"][0], s["Shaving"]["pos"][1])
        path.lineTo(s["Lamination"]["pos"][0], s["Lamination"]["pos"][1])
        path.lineTo(s["Prep"]["pos"][0], s["Prep"]["pos"][1])
        path.lineTo(s["DDT"]["pos"][0], s["DDT"]["pos"][1])
        
        path.moveTo(s["Shaving"]["pos"][0], s["Shaving"]["pos"][1])
        path.lineTo(s["Wireloading"]["pos"][0], s["Wireloading"]["pos"][1])
        path.lineTo(s["Crimp"]["pos"][0], s["Crimp"]["pos"][1])
        
        path.moveTo(s["Crimp"]["pos"][0], s["Crimp"]["pos"][1])
        path.lineTo(s["Bump"]["pos"][0], s["Bump"]["pos"][1])
        path.lineTo(s["QC"]["pos"][0], s["QC"]["pos"][1])
        path.lineTo(s["Shipping"]["pos"][0], s["Shipping"]["pos"][1])
        
        pen = QPen(COLOR_LINE, 20)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        path_item = self.scene.addPath(path, pen)
        path_item.setZValue(0) # Put lines behind nodes

    def setup_timer(self):
        self.timer.timeout.connect(self.refresh_data)
        self.timer.setSingleShot(True)
        self.timer.start(1) # Start immediately on load

    def refresh_data(self):
        """Simulates fetching and processing data."""
        # 1. Update the time
        self.last_check_time = datetime.now()
        self.last_checked_label.setText(f"Last Checked: {update_timestamp(self.last_check_time)}")
        
        # Reset stations to "Waiting..." before applying new data
        for station in self.stations.values():
             station.update_status("", [])
             
        # 2. Process the new data format for the specified shift
        for container_dict in MOCK_RAW_DATA:
            container_id, container_data = next(iter(container_dict.items()))
            
            shift_data = container_data.get(REPORT_SHIFT, {})
            employee = shift_data.get("employee", "")
            tasks_completed = shift_data.get("task_completed", [])
            
            station_name = STATION_MAPPING.get(container_id)
            
            if station_name and station_name in self.stations:
                self.stations[station_name].update_status(employee, tasks_completed)
        
        # 3. Recalculate bounds and fit view
        bounds = self.scene.itemsBoundingRect()
        buffer = 20
        self.scene.setSceneRect(bounds.adjusted(-buffer, -buffer, buffer, buffer))
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # 4. Set the random interval for the NEXT check
        random_delay_seconds = random.randint(3, 15)
        self.timer.start(random_delay_seconds * 1000) # Convert to milliseconds


class LoginScreen(QWidget):
    """Initial screen for credentials and container ID with enforced validation."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        l1 = QLabel("Container:")
        l1.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        self.entry_container = QLineEdit()
        self.entry_container.setPlaceholderText("Enter Container ID")
        self.apply_entry_style(self.entry_container)
        
        l2 = QLabel("Username:")
        l2.setStyleSheet("color: white; font-weight: bold; font-size: 16px; margin-top: 10px;")
        self.entry_user = QLineEdit()
        self.entry_user.setPlaceholderText("Enter Username")
        self.apply_entry_style(self.entry_user)
        
        l3 = QLabel("Password:")
        l3.setStyleSheet("color: white; font-weight: bold; font-size: 16px; margin-top: 10px;")
        self.entry_pass = QLineEdit()
        self.entry_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_pass.setPlaceholderText("Enter Password")
        self.apply_entry_style(self.entry_pass)
        
        self.btn_start = QPushButton("Start Monitoring")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Connect signals to update button state
        self.entry_container.textChanged.connect(self.update_button_state)
        self.entry_user.textChanged.connect(self.update_button_state)
        self.entry_pass.textChanged.connect(self.update_button_state)
        
        self.update_button_state() # Initial call to set the disabled state
        
        layout.addWidget(l1)
        layout.addWidget(self.entry_container)
        layout.addWidget(l2)
        layout.addWidget(self.entry_user)
        layout.addWidget(l3)
        layout.addWidget(self.entry_pass)
        layout.addWidget(self.btn_start)
        self.setLayout(layout)

    def apply_entry_style(self, widget):
        widget.setFixedWidth(400)
        # Use 'color: black;' for the input text as requested
        widget.setStyleSheet("QLineEdit { color: black; padding: 10px; font-size: 14px; background-color: #e0e0e0; border-radius: 4px; border: none; }")

    def update_button_state(self):
        """
        Enables the button only if all required fields are non-empty and applies 
        the specified colors for enabled/disabled states.
        """
        container_filled = bool(self.entry_container.text().strip())
        user_filled = bool(self.entry_user.text().strip())
        password_filled = bool(self.entry_pass.text().strip())
        
        is_valid = container_filled and user_filled and password_filled
        self.btn_start.setEnabled(is_valid)
        
        if is_valid:
            style = f"""
                QPushButton {{
                    background-color: {COLOR_START_MONITORING_ENABLED.name()};
                    color: white;
                    padding: 15px 50px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin-top: 30px;
                }}
                QPushButton:hover {{ background-color: {COLOR_START_MONITORING_ENABLED.darker(120).name()}; }}
            """
        else:
            style = f"""
                QPushButton {{
                    background-color: {COLOR_BUTTON_DISABLED.name()};
                    color: black;
                    padding: 15px 50px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin-top: 30px;
                }}
            """
        self.btn_start.setStyleSheet(style)


class MainWindow(QMainWindow):
    """Main application window controlling screen switching."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineClearance Monitor")
        self.setStyleSheet(f"background-color: {COLOR_BG.name()};")
        self.resize(1200, 800)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.login = LoginScreen()
        self.login.btn_start.clicked.connect(self.go_to_monitor)
        self.stack.addWidget(self.login)
        
        self.monitor = None # Initialize monitor reference

    def go_to_monitor(self):
        # Rely on the LoginScreen button's enabled state for validation
        if not self.login.btn_start.isEnabled():
            return
            
        container_id = self.login.entry_container.text()
        
        # Cleanup any old monitor screen before creating a new one
        if self.monitor:
             self.monitor.timer.stop()
             self.stack.removeWidget(self.monitor)
             self.monitor.deleteLater()
             
        self.monitor = MonitoringScreen(container_id)
        self.monitor.stop_button.clicked.connect(self.go_to_login)
        self.stack.addWidget(self.monitor)
        self.stack.setCurrentWidget(self.monitor)
        
    def go_to_login(self):
        if self.monitor:
            self.monitor.timer.stop()
            self.stack.removeWidget(self.monitor)
            self.monitor.deleteLater()
            self.monitor = None
        
        self.stack.setCurrentWidget(self.login)
        
        # Clear sensitive fields upon returning to login
        self.login.entry_pass.clear()
        self.login.entry_user.clear() 
        self.login.entry_container.clear()
        self.login.update_button_state()

    def closeEvent(self, event):
        """Ensure the timer is stopped when the main window closes."""
        if self.monitor and self.monitor.timer.isActive():
            self.monitor.timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())