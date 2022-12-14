import threading
import requests
import threading
import time
import logging

log = logging.getLogger(__name__)

class ThangsEvents(object):
    def __init__(self):
        self.deviceId = ""
        self.ampURL = 'https://events.thangs.com'
        pass

    def send_thangs_event(self, event_type, event_properties=None):
        threading.Thread(
            target=self._send_thangs_event,
            args=(event_type, event_properties)
        ).start()
        return

    def _send_thangs_event(self, event_type, event_properties):
        if event_type == "Results":
            requests.post("https://thangs.com/api/search/v1/result",
                          json=event_properties,
                          headers={},
                          )

        elif event_type == "Capture":
            requests.post("https://thangs.com/api/search/v1/capture-text-search",
                          json=event_properties,
                          headers={
                              "x-device-id": self.deviceId},
                          )

    def send_amplitude_event(self, event_name, event_properties=None):
        threading.Thread(
            target=self._send_amplitude_event,
            args=(event_name, event_properties)
        ).start()
        return

    def _construct_event(self, event_name, event_properties):
        event = {
            'event_type': event_name,
            'device_id': str(self.deviceId),
            'event_properties': {}
        }
        if event_properties:
            event['event_properties'] = event_properties

        return event

    def _send_amplitude_event(self, event_name, event_properties):
        event = self._construct_event(event_name, event_properties)
        response = requests.post(self.ampURL, json={'events': [event]})
        log.info('Sent amplitude event: ' + event_name + 'Response: ' + str(response.status_code))

