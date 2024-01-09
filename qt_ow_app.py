'''
A simple weather app providing radio stations for the selected city.
(In a virtual environment) install pyqt5, requests, pyradios and miniaudio with pip.
'''

from sys import argv
from time import sleep
from radio import Background_Radio_Thread
from requests import get

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QGraphicsDropShadowEffect


class MainWindow(QMainWindow):
    chose_radio_for_city = QtCore.pyqtSignal(str)
    stop_radio = QtCore.pyqtSignal()
    set_radio_station = QtCore.pyqtSignal(dict, list)
    kill = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.city_name = 'Berlin'
        self.city_searches = [self.city_name]
        self.search_index = 0
        self.Radio = Background_Radio_Thread()
        self.stations_to_chose = []
        self.selected_station_index = 0
        self.radio_thread = QtCore.QThread(self)
        self.Radio.available_stations.connect(self.populate_stations)
        self.Radio.selected_station.connect(self.report_selected_station)
        self.chose_radio_for_city.connect(self.Radio.get_radios_for_city)
        self.set_radio_station.connect(self.Radio.stream_radio_from_url)
        self.kill.connect(self.Radio.kill_me)
        self.stop_radio.connect(self.Radio.close_stream)
        self.Radio.moveToThread(self.radio_thread)
        self.radio_thread.start()

        connect = self.op_request(self.city_name)

        self.setWindowTitle("Open Weather Radio App")
        self.setStyleSheet("""
            background-color: #000000;
        """)

        layout = QVBoxLayout()

        label = QLabel("Weather for city:")
        label.setStyleSheet("""
            qproperty-alignment: AlignRight;
            background-color: rgba(25, 25, 25, 50%);
            color: orange;
            margin-left: 57px;
        """)

        self.location_edit = QLineEdit(self.city_name)
        self.location_edit.returnPressed.connect(self.return_pressed)
        self.location_edit.textChanged.connect(self.text_changed)
        self.location_edit.textEdited.connect(self.text_changed)
        self.location_edit.installEventFilter(self)
        self.location_edit.setStyleSheet("""
            color: #FFFFFF;
            border: 1px solid gray;
            background-color: rgba(35, 35, 35, 75%);
            qproperty-alignment: AlignRight;
        """)
        # creating a QGraphicsDropShadowEffect object 
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(-8)
        self.location_edit.setGraphicsEffect(shadow) 

        self.info_label = QLabel(connect)
        self.info_label.setStyleSheet("""
            qproperty-alignment: AlignCenter;
            background-color: rgba(25, 25, 25, 75%);
            color: green;
        """)

        self.radios_combobox = QComboBox()
        self.radios_combobox.activated.connect(self.user_selected_station)
        self.radios_combobox.setStyleSheet("""
            border: 1px solid gray;
            background-color: rgba(35, 35, 35, 75%);
        """)
        # creating a QGraphicsDropShadowEffect object 
        cshadow = QGraphicsDropShadowEffect() 
        cshadow.setBlurRadius(10) 
        self.radios_combobox.setGraphicsEffect(cshadow) 

        self.radio_info_label = QLabel()
        self.radio_info_label.setOpenExternalLinks(True)
        self.radio_info_label.setStyleSheet("""
            background-color: rgba(25, 25, 25, 50%);
            margin-right: 57px;
        """)

        layout.addWidget(label)
        layout.addWidget(self.location_edit)
        layout.addWidget(self.info_label)
        layout.addWidget(self.radios_combobox)
        layout.addWidget(self.radio_info_label)

        # Set the central widget of the Window.

        self.widget = QWidget(self)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("""
            color: #AAAAAA;
            font-size: 18px;
            padding: 20px;
            border: 1px solid dark-gray;
        """)
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        

    def eventFilter(self, obj, event):
        if obj is self.location_edit and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                self.browse_city_searches(self.search_index - 1)
            if event.key() == QtCore.Qt.Key_Down:
                self.browse_city_searches(self.search_index + 1)
        return super().eventFilter(obj, event)
    
    def browse_city_searches(self, index):
        if index >= 0 and index < len(self.city_searches):
            self.search_index = index
            self.city_name = self.city_searches[index]
            self.return_pressed()
            self.location_edit.setText(self.city_searches[index])

    def op_request(self, city):
        api_key = 'e8693736460fda1afa468683c6f17ea3'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
        response = get(url)
        info = ""
        def info_for_key(info_key):
            key_info = ""
            for info in weather_data[info_key]:
                key_info = key_info+f"\t{info}: {weather_data[info_key][info]}\n"
            return key_info
        if response.status_code == 200:
            # Request was successful
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            wind = info_for_key("wind")
            main = info_for_key("main")
            info = f"Temperature: {temperature} \nDescription: {description}\nwind: {wind}\nmain: {main}"
            self.stop_radio.emit()
            self.chose_radio_for_city.emit(self.city_name)
        else:
            # Request failed
            info = f"connection-error: {response.status_code}"
        return info
    
    def text_changed(self, s):
        self.city_name = s

    def return_pressed(self):
        new_request = self.op_request(self.city_name)
        self.info_label.setText(new_request)
        if not self.city_name in self.city_searches and not "connection-error: " in new_request:
            self.city_searches.append(self.city_name)
            self.search_index = len(self.city_searches) -1

    def populate_stations(self, stations):
        self.stations_to_chose = stations
        self.radios_combobox.clear()
        for station in self.stations_to_chose:
            self.radios_combobox.addItem(station["name"])

    def report_selected_station(self, station_index:str):
        if station_index.isnumeric():
            self.selected_station_index = int(station_index)
            self.radios_combobox.setCurrentIndex(self.selected_station_index)
            selected_station = self.stations_to_chose[self.selected_station_index]
            self.radio_info_label.setText(f"connecting to {selected_station['name']}")
        elif station_index == "connected":
            selected_station = self.stations_to_chose[self.selected_station_index]
            self.radio_info_label.setText(f"<a href=\"{selected_station['homepage']}\">radio station: {selected_station['name']}</a>")


    def user_selected_station(self, index):
        self.stop_radio.emit()
        self.selected_station_index = index
        selected_station = self.stations_to_chose[self.selected_station_index]
        self.set_radio_station.emit(selected_station, self.stations_to_chose)

    # app close
    def closeEvent(self, event:QtGui.QCloseEvent):
        event.ignore()
        self.stop_radio.emit()
        print("closing down...", end="")
        self.kill.emit()
        self.radio_thread.quit()
        print(" background thread quit", end="")
        print(" bye!")
        event.accept()

qss = """
#widget {
    border-image: url(bg_t.png) 0 0 0 0 stretch stretch; opacity: 127;
}
"""    

app = QApplication(argv)
app.setStyleSheet(qss)

window = MainWindow()
window.show()

app.exec()
