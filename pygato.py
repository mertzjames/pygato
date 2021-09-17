import requests
import json

MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100

MIN_TEMP = 143
MAX_TEMP = 344

class Light():
    base_uri = 'http://{ip_addr}:{port}/elgato/lights'

    def __init__(self, ip_addr, port=9123, on=None, brightness=None, temperature=None):
        self.uri = self.base_uri.format(ip_addr=ip_addr, port=port)
        self._status = None
        self._brightness = None
        self._temperature = None

        self.__update_light()

        if on is not None:
            self.status = on
        if brightness is not None:
            self.brightness = brightness
        if temperature is not None:
            self.temperature = temperature

    @property
    def status(self):
        return 'on' if self._status else 'off'

    @status.setter
    def status(self, val):
        if not isinstance(val, bool):
            raise TypeError(f'Must set status to a boolean')

        self.__update_light(status=val)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        if not isinstance(val, int):
            raise TypeError('Must set brightness to a int')
        if MIN_BRIGHTNESS < val > MAX_BRIGHTNESS:
            raise ValueError(f'Brightness must be between {MIN_BRIGHTNESS}:{MAX_BRIGHTNESS}')
        self.__update_light(bright=val)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, val):
        if not isinstance(val, int):
            raise TypeError('Must set temperature to an int')
        if not (MIN_TEMP <= val <= MAX_TEMP):
            raise ValueError(f'Temperature must be between {MIN_TEMP}:{MAX_TEMP}')
        self.__update_light(temp=val)

    def __craft_payload(self, on=None, bright=None, temp=None):
        on = self._status if on is None else on
        bright = self._brightness if bright is None else bright
        temp = self._temperature if temp is None else temp
        payload = {
            'numberOfLights': 1,
            'lights':[
                {
                    'on': int(on),
                    'brightness': bright,
                    'temperature': temp
                }
            ]
        }
        return payload

    def __update_light(self, status=None, bright=None, temp=None):
        if status is None and bright is None and temp is None:
            r = requests.get(self.uri)
            data = r.json()['lights'][0]

        else:
            payload = self.__craft_payload(status, bright, temp)
            r = requests.put(self.uri, data=json.dumps(payload))

            # No response from the light, try again
            if r.content == b'':
                r = requests.put(self.uri, data=json.dumps(payload))
            
            # If no response a second time or there are errors, raise 
            if r.content == '':
                raise TimeoutError("Device is no longer responding")
            
            if 'errors' in r.json():
                raise ValueError("")
            data = r.json()['lights'][0]

        self._status = data['on']
        self._brightness = data['brightness']
        self._temperature = data['temperature']
