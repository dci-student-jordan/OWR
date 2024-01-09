# OWR
## Open Weather Radio

A Weather App providing radio streams from the selected city, made with PyQt5.

### Installation:
[Create and activate a virtual environment,](https://docs.python.org/3/library/venv.html) clone, cd, then run

    pip install requirements.txt

### Get OpenWeatherMap API key
- [Get a free API key here](https://home.openweathermap.org/api_keys)
- Create a file named .env in the root directory of this repo (Hidden files must be shown).
- Paste this content replacing <your_api_key> with the one you got from openweathermap:

        OPENWEATHERAPIKEY = '<your_api_key>'

### Running:
With the virtual environment activated run

    python qt_ow_app.py

### Enjoy!
This app was created as a practice during the Python Backend Development Course at the [DCI.](https://digitalcareerinstitute.org/)

### Known bugs
Sometimes the radio hangs when failing to establish a connection. The App needs to be force-quit then (^C).