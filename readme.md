# BubbleBoy - Backend

##Beschreibung
BubbleBoy ist ein Trackingtool für BLE Beacons welches im Rahmen des 6. Make@thon entwickelt wurde.


##TestData
```
mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver1/raw/8caab583a40a' -m '-87.318' && 
mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver2/raw/8caab583a40a' -m '-91.67' &&
mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver3/raw/8caab583a40a' -m '-91.29' &&
mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver4/raw/8caab583a40a' -m '-86.24' 
```
Should result in (4;10)

##MQTT
MQTT is reachable on Port 1883

##API
    http://IP:5000/getBeacons
Returns a List of Beacons with position

    http://IP:5000/getArea
Returns list of Areas with among of beacons in area

    http://IP:5000/getArea?area=AREANAME
Returns among of beacons in area defined by argument

    http://IP:5000/?area=AREANAME
Returns self refreshing SIGN for signage

##Install
Just clone this repository.

After that copy config.sample.yaml to config.yaml and edit it.

To install it use
    docker-compose up -d
