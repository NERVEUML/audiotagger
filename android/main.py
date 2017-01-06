#!/usr/bin/env python
import kivy
kivy.require("1.9.1")

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
import socket

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


class MainMenuScreen(Screen):
    pass

class LesserMenuScreen(Screen):
    pass

class TaggingScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class APRSTagControlRoot(ScreenManager):
    def on_current(self, instance, value):
        self.last_screen = self.current_screen
        super(APRSTagControlRoot, self).on_current(instance, value)

    def last(self):
        return self.last_screen.name

class APRSTagControlApp(App):
    # on pause: self.m.loop_stop()
    def build_config(self, config):
        config.setdefaults('mqtt', 
                {
            'host': 'aprspi',
            'port': '1883',
            'tagtopic':"nerve/aprs", #should expect KISS frames?
            })

    def get_config_file(self):
        return super(APRSTagControlApp, self).get_application_config('~/.%(appname)s.ini')

    def sendtagreq(self):
        team = "MIT"
        task = "1A"
        attempt = "1.1"
        tagtopic = self.config.get('mqtt','tagtopic')
        if self.network:
            self.m.publish( tagtopic, "")
        else:
            pass #pop up a warning

    def build(self):
        config = self.config
        self.network = False
        self.m = mqtt.Client()
        self.m.on_connect = on_connect
        self.m.on_message = on_message
        self.m.on_disconnect = on_disconnect
        host = config.get('mqtt','host')
        port = config.get('mqtt','port')
        try:
            self.m.connect( str(host), int(port), 60)
            self.network = True
        except socket.error as e:
            self.network = False
        self.m.loop_start()
        return APRSTagControlRoot()

    def build_settings(self, settings):
        jsondata = """[
                    {
                    "type":"title",
                    "title":"application"
                    }
                    ]"""
        settings.add_json_panel('APRSTagControl', self.config, data=jsondata)

if __name__ == "__main__":
    APRSTagControlApp().run()
