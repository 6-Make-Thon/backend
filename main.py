import math
import threading
import time

import yaml
from flask import Flask, jsonify, request, abort, render_template
from paho.mqtt import client as mqtt
from shapely.geometry import Point, Polygon

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


devicelist = []
area = {}


def main(lock):
    global devlist, area
    while True:
        time.sleep(1)

        lock.acquire()
        newlist = {}
        for k1, receiver in devlist.items():
            newlist[k1] = {k2: item for (k2,item) in receiver.items() if item['time'] > time.time()-10}
        devlist = {k1: item for (k1, item) in newlist.items() if len(item)}
        lock.release()

        devicelist.clear()
        for k1, receiver in devlist.items():
            if len(receiver) >= 3:
                coordinates = (trilateration([item for item in receiver.values()]).calc())
                x, y = coordinates[0], coordinates[1]
                devicelist.append({
                    'mac': k1,
                    'x': x,
                    'y': y,
                    'bestsender': findbestsender(receiver)
                })
                print(f"receiver:{k1}; x:{x:.2f},y:{y:.2f}")
        searchNeightbors(devicelist)
        area = beaconinarea(devicelist)


def beaconinarea(devicelist):
    returndict = {}
    for area in config['areas']:
        poly = Polygon([tuple(x) for x in area['points']])
        beaconnumber = 0
        for device in devicelist:
            point = Point(device['x'], device['y'])
            beaconnumber += 1
        returndict[area['name']] = beaconnumber
    return returndict


def findbestsender(devlist):
    bestsender = ''
    min = -255
    for name, value in devlist.items():
        if value['rssi'] > min:
            min = value['rssi']
            bestsender = name
    return bestsender


def searchNeightbors(devicelist):
    strangerlist = devicelist.copy()
    for item in devicelist:
        strangerInGrad = {}
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

                if config['strangerdetection']['mindistance'] < distance < config['strangerdetection']['maxdistance']:
                    strangerInGrad[int(grad/45)] = strangerInGrad[int(grad/45)] + 1 if int(grad/45) in strangerInGrad else 1
        client.publish(f"beaconator/ble/{item['bestsender']}/downlink/{item['mac']}", payload=calcColorWord(strangerInGrad))


def calcColorWord(dictofled):
    returnbyte = 0x00

    for led, count in dictofled.items():
        if count >= config['ledColor']['red']:
            returnbyte = returnbyte | 3 << led * 2
        elif count >= config['ledColor']['orange']:
            returnbyte = returnbyte | 2 << led * 2
        elif count >= config['ledColor']['yellow']:
            returnbyte = returnbyte | 1 << led * 2


    return returnbyte


app = Flask(__name__)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa832323'


@app.route("/getBeacons", methods=['GET'])
def getBeacons():
    return jsonify(devicelist)


@app.route('/getArea', methods=['GET'])
def getArea():
    areareg = request.args.get('area')
    if areareg is None:
        return jsonify(area)
    else:
        return {'value': area[areareg] } if areareg in area else {'error': True}


@app.route('/getAreaForSign', methods=['GET'])
def getAreaForSign():
    areareg = request.args.get('area')
    if areareg is None:
        return jsonify(area)
    else:
        if areareg not in area:
            return {'error': True}

        value = area[areareg]

        if value >= config['ledColor']['red']:
            return {'text': 'überfüllt', 'color': 'red'}
        elif value >= config['ledColor']['red']:
            return {'text': 'ist stark besucht', 'color': 'orange'}
        elif value >= config['ledColor']['red']:
            return {'text': 'ist mittel besucht', 'color': 'yellow'}
        else:
            return {'text': 'ist aktuell wenig besucht. <br>Wir wünschen viel Spaß beim Einkaufen', 'color': 'green'}


@app.context_processor
def inject_title():
    return dict(title="Bereichsschild")


@app.route('/')
def sign():
    areareg = request.args.get('area')
    if areareg is None:
        abort(404, description="Ressource not found")
    else:
        return render_template("sign.html", name=areareg)


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


def webWorker():
    app.run(host="0.0.0.0")


sub = threading.Thread(target=Subscribing, args=(lock,), name='Sub')
pub = threading.Thread(target=main, args=(lock,), name='Main')
web = threading.Thread(target=webWorker)

sub.start()
pub.start()
web.start()
