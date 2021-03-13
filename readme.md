# Test packages
mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver1/raw/8caab583a40a' -m '-87.318' && 

mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver2/raw/8caab583a40a' -m '-91.67' &&

mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver3/raw/8caab583a40a' -m '-91.29' &&

mosquitto_pub -h 10.1.6.31 -d -u USERNAME -P PASSWORT -t 'beaconator/ble/receiver4/raw/8caab583a40a' -m '-86.24' 


Should result in (4;10)