# Arduino sketches

## HumTemPol.pde

Very simple sketch to return humidity/temperature readings on
demand. Running on an A-Star 32U4 Micro with a DHT22.

## AutoPlug.pde
Sketch to control a relay board over serial. Running on Arduino Nano
clone.

## RFSensorXmit and RFSensorRecv
Hopefully these can replace HumTemPol eventually. Using cheap RF
transmitter/receiver pairs multiple sensors can report to a single
receiver instance which then talks serial to the pi. Currently, these
run on Arduino Nano clones powered by a small USB power pack.