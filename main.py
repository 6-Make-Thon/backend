import math
import threading
import time

import yaml
from paho.mqtt import client as mqtt

from trilateration import trilateration

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

client = mqtt.Client(client_id='beaconator')
if 'user' in config['mqtt'] and config['mqtt']['user'] != '' 'pass' in config['mqtt'] and config['mqtt']['pass']:
    client.username_pw_set(config['mqtt']['user'], config['mqtt']['pass'])

client.connect(config['mqtt']['host'], port=config['mqtt']['port'])
client.subscribe('beaconator/#')
lock = threading.Lock()
devlist = {}


class Subscribing:
    def __init__(self, lock):
        self.lock = lock
        client.on_message = self.on_message
        client.loop_forever()

    def on_message(self, client, userdata, message):
        self.save_measure(message)

    def save_measure(self, message):
        self.lock.acquire()
        path = message.topic.split('/')
        if path[2] in config['receiver']:
            x0,y0 = float(config['receiver'][path[2]]['x']), float(config['receiver'][path[2]]['y'])
        else:
            raise
        rssi = float(message.payload.decode('utf-8'))
        distance = pow(10.0, ((-69.0 - rssi)/(10.0 * 2.0)))
        entry = {'rssi': rssi, 'x': x0, 'y': y0, 'dist': distance, 'time': time.time()}
        if path[4] not in devlist:
            devlist[path[4]] = {path[2]: entry}
        else:
            devlist[path[4]][path[2]] = entry
        lock.release()


def main(lock):
    global devlist
    while True:
        time.sleep(1)

        lock.acquire()
        newlist = {}
        for k1, receiver in devlist.items():
            newlist[k1] = {k2: item for (k2,item) in receiver.items() if item['time'] > time.time()-10}
        devlist = {k1: item for (k1, item) in newlist.items() if len(item)}
        lock.release()

        devicelist = []
        for k1, receiver in devlist.items():
            if len(receiver) >= 3:
                coordinates = (trilateration([item for item in receiver.values()]).calc())
                x,y = coordinates[0],coordinates[1]
                devicelist.append({
                    'mac': k1,
                    'x': x,
                    'y': y
                })
                print(f"receiver:{k1}; x:{x:.2f},y:{y:.2f}")
        searchNeightbors(devicelist)


def searchNeightbors(devicelist):
    strangerlist = devicelist.copy()
    for item in devicelist:
        for stranger in strangerlist:
            if item != stranger:
                delta_x = abs(item['x'] - stranger['x'])
                delta_y = abs(item['y'] - stranger['y'])

                if item['x'] < stranger['x']:  # 1. and 4. quadrant
                    if item['y'] < stranger['y']:  # 1. quadrant
                        offset = -90
                    else:  # 4. quadrant
                        offset = 360
                else:
                    if item['y'] < stranger['y']:  # 2. quadrant
                        offset = 180
                    else:  # 3. quadrant
                        offset = 180

                distance = math.sqrt(pow(delta_x, 2) + pow(delta_y,2))

                grad = abs(math.degrees(math.atan(delta_y/delta_x)) + offset)
                print(f"Distance between {item['mac']} and {stranger['mac']}: {distance:.2f} and {grad:.2f}°")


sub = threading.Thread(target=Subscribing, args=(lock,), name='Sub')
pub = threading.Thread(target=main, args=(lock,), name='Main')

sub.start()
pub.start()
