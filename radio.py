from pyradios import RadioBrowser
from miniaudio import IceCastClient, PlaybackDevice, stream_any
from random import randint
from PyQt5 import QtCore
import requests
import concurrent.futures

class Background_Radio_Thread(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.radio_browser = RadioBrowser()
        self.audio_device = PlaybackDevice()
        self.radio_stream = None
        self.radio_running = False

    available_stations = QtCore.pyqtSignal(list)
    selected_station = QtCore.pyqtSignal(str)
    
    @QtCore.pyqtSlot(str)
    def get_radios_for_city(self, city_name):
        radios_dict_list = [{"name":radio["name"], "url":radio["url"], "homepage":radio["homepage"]} for radio in self.radio_browser.search(name=city_name, name_exact=False)]
        if radios_dict_list:
            self.select_random_station(radios_dict_list)

    def select_random_station(self, radios_dict_list):
        self.available_stations.emit(radios_dict_list)
        random_radio = randint(0, len(radios_dict_list)-1)
        self.selected_station.emit(str(random_radio))
        try:
            self.stream_radio_from_url(radios_dict_list[random_radio], radios_dict_list)
        except requests.HTTPError:
            # remove Forbidden requests and retry
            radios_dict_list.remove(radios_dict_list[random_radio])
            self.select_random_station(radios_dict_list)

    @QtCore.pyqtSlot(dict, list)
    def stream_radio_from_url(self, radio_dict, radios_list):
        # print("pre Icecast")
        self.radio_stream = IceCastClient(radio_dict["url"])
        # print("post Icecast, pre stream")
        stream = None
        def connect_stream():
            nonlocal stream
            stream = stream_any(self.radio_stream, self.radio_stream.audio_format)
            print("stream STARTED")
            return stream
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(connect_stream)
            try:
                future.result(timeout=3)
                print("stream CONNECTED")
            except concurrent.futures.TimeoutError:
                print("stream conection TIMEDOUT")
                radios_list.remove(radio_dict)
                self.select_random_station(radios_list)
        # print("post stream, pre audio_device start")
        self.audio_device.start(stream)
        self.selected_station.emit("connected")
        # print("done")
        self.radio_running = True

    def close_stream(self):
        if self.radio_running:
            self.audio_device.stop()
            # print("device stopped")
            self.radio_stream.close()
            # print("stream closed")
            self.radio_running = False

    def kill_me(self):
        self.audio_device.close()