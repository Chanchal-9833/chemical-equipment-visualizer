import sys
import requests
import webbrowser
from PyQt5.QtWidgets import QPushButton, QFileDialog, QMessageBox


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox,
    QFrame, QTableWidget, QTableWidgetItem, QMessageBox
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE = "http://127.0.0.1:8000/api"


# ================= CHART WIDGET =================
class ChartWidget(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(5, 3))
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)


# ================= MAIN APP =================
class EquipmentApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chemical Equipment Dashboard")
        self.setGeometry(100, 100, 950, 650)

        self.main_layout = QVBoxLayout()

        # ===== HEADER =====
        title = QLabel("Chemical Equipment Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:26px; font-weight:bold; padding:10px;")
        self.main_layout.addWidget(title)

        # ===== TOP FILTERS =====
        top_layout = QHBoxLayout()

        
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4e73df;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e59d9;
            }
        """)

        self.upload_btn.clicked.connect(self.upload_csv)
        self.upload_combo = QComboBox()
        self.upload_combo.currentIndexChanged.connect(self.on_filter_changed)

        self.chart_combo = QComboBox()
        self.chart_combo.addItems([
            "Type Distribution",
            "Flowrate vs Pressure",
            "Temperature Distribution",
            "Upload Trend"
        ])
        self.chart_combo.currentIndexChanged.connect(self.on_filter_changed)

        top_layout.addWidget(self.upload_btn)


        top_layout.addWidget(QLabel("Select Upload:"))
        top_layout.addWidget(self.upload_combo)
        top_layout.addWidget(QLabel("Select Chart:"))
        top_layout.addWidget(self.chart_combo)

        self.main_layout.addLayout(top_layout)

        # ===== SUMMARY CARDS =====
        card_layout = QHBoxLayout()

        self.total_card = self.create_card("Total Equipment")
        self.flow_card = self.create_card("Avg Flowrate")
        self.temp_card = self.create_card("Avg Temperature")

        card_layout.addWidget(self.total_card)
        card_layout.addWidget(self.flow_card)
        card_layout.addWidget(self.temp_card)

        self.main_layout.addLayout(card_layout)

        # ===== DOWNLOAD BUTTON =====
        self.report_btn = QPushButton("Download Report")
        
        self.report_btn.clicked.connect(self.download_report)
        self.report_btn.setEnabled(False)

        self.main_layout.addWidget(self.report_btn)

        # ===== CHART =====
        self.chart_widget = ChartWidget()
        self.chart_widget.setMinimumHeight(250)
        self.main_layout.addWidget(self.chart_widget)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Type", "Flowrate", "Pressure", "Temperature"]
        )

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.main_layout.addWidget(self.table)

        self.setLayout(self.main_layout)

        self.load_uploads()

    # ================= CARD UI =================
    def create_card(self, title):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border:1px solid gray;
                border-radius:8px;
                padding:10px;
                background:#f5f5f5;
            }
        """)

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight:bold")

        value_label = QLabel("--")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size:20px")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame.setLayout(layout)
        frame.value_label = value_label

        return frame
    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return  # user cancelled

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    "http://127.0.0.1:8000/api/upload-csv/",
                    files=files
                )

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "CSV uploaded successfully")

                # 🔁 refresh UI just like React
                self.load_uploads()
                self.refresh_dashboard()

            else:
                QMessageBox.critical(self, "Error", "CSV upload failed")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def refresh_dashboard(self):
        upload_id = self.upload_combo.currentData()
        if not upload_id:
            return

        self.load_summary(upload_id)
        self.load_equipment(upload_id)
        


    def load_uploads(self):
        try:
            res = requests.get(f"{API_BASE}/uploads/")
            uploads = res.json()

            self.upload_combo.clear()

            for u in uploads:
                self.upload_combo.addItem(
                    f"Upload {u['id']} - {u['uploaded_at']}",
                    u["id"]
                )

            # Auto select first upload
            if uploads:
                self.upload_combo.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    def on_filter_changed(self):
        upload_id = self.upload_combo.currentData()

        if not upload_id:
            return

        self.report_btn.setEnabled(True)

        self.load_summary(upload_id)
        self.load_equipment(upload_id)
        self.update_chart(upload_id)


    def load_summary(self, upload_id):
        res = requests.get(f"{API_BASE}/summary/?upload_id={upload_id}")
        data = res.json()["summary"]

        self.total_card.value_label.setText(str(data["total_equipment"]))
        self.flow_card.value_label.setText(f"{data['avg_flowrate']:.2f}")
        self.temp_card.value_label.setText(f"{data['avg_temperature']:.2f}")

    #
    def load_equipment(self, upload_id):
        res = requests.get(f"{API_BASE}/filter-equipment/?upload_id={upload_id}")
        equipment = res.json()

        self.table.setRowCount(len(equipment))

        for row, e in enumerate(equipment):
            self.table.setItem(row, 0, QTableWidgetItem(e["equipment_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(e["equipment_type"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(e["flowrate"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(e["pressure"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e["temperature"])))

        self.table.resizeColumnsToContents()

    
    def update_chart(self, upload_id):
        chart_type = self.chart_combo.currentText()

        self.chart_widget.ax.clear()

        if chart_type == "Type Distribution":
            res = requests.get(f"{API_BASE}/summary/?upload_id={upload_id}")
            dist = res.json()["type_distribution"]

            labels = [d["equipment_type"] for d in dist]
            counts = [d["count"] for d in dist]

            self.chart_widget.ax.bar(labels, counts)
            self.chart_widget.ax.set_title("Equipment Type Distribution")

        elif chart_type == "Flowrate vs Pressure":
            equipment = self.get_equipment_data(upload_id)

            flow = [e["flowrate"] for e in equipment]
            pressure = [e["pressure"] for e in equipment]

            self.chart_widget.ax.scatter(flow, pressure)
            self.chart_widget.ax.set_xlabel("Flowrate")
            self.chart_widget.ax.set_ylabel("Pressure")

        elif chart_type == "Temperature Distribution":
            equipment = self.get_equipment_data(upload_id)
            temps = [e["temperature"] for e in equipment]

            self.chart_widget.ax.hist(temps, bins=10)
            self.chart_widget.ax.set_title("Temperature Distribution")

        elif chart_type == "Upload Trend":
            res = requests.get(f"{API_BASE}/uploads/")
            uploads = res.json()

            ids = [u["id"] for u in uploads]
            counts = [u["total_equipment"] for u in uploads]

            self.chart_widget.ax.plot(ids, counts, marker="o")
            self.chart_widget.ax.set_title("Upload Trend")

        self.chart_widget.draw()

    
    def download_report(self):
        upload_id = self.upload_combo.currentData()
        webbrowser.open(f"{API_BASE}/report/?upload_id={upload_id}")

  
    def get_equipment_data(self, upload_id):
        res = requests.get(f"{API_BASE}/filter-equipment/?upload_id={upload_id}")
        return res.json()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EquipmentApp()
    window.show()
    sys.exit(app.exec_())
