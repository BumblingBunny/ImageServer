// -*- c -*-

// Required libraries:
// RadioHead - http://www.airspayce.com/mikem/arduino/RadioHead/
// DHT - https://github.com/adafruit/DHT-sensor-library

// Sketch to read from a DHT22 and transmit it via a cheap 433MHz RF transmitter
// RadioHead expects the data pin for the transmitter to be on D12


#include <RH_ASK.h>
#include <SPI.h>
#include <DHT.h>

//// Uncomment to see debug information on a serial link
//#define PRINT_SERIAL

#define DHT_PIN 2
#define DHT_TYPE DHT22
#define CELSIUS false
#define FAHRENHEIT true

#define WAIT_FIXED 2000
#define WAIT_RANDOM 2000

typedef struct {
    float humidity;
    float temperature;
    uint8_t station_id;
} StationReport;

RH_ASK driver;
uint8_t station_id = 5;

DHT dht = DHT(DHT_PIN, DHT_TYPE);

void setup()
{
#ifdef PRINT_SERIAL
    Serial.begin(9600);
    if (!driver.init()) {
        Serial.println("init failed");
    }
#else
    driver.init();
#endif
}

void loop()
{
    StationReport report;

    report.station_id = station_id;
    report.humidity = dht.readHumidity();
    report.temperature = dht.readTemperature(CELSIUS);

#ifdef PRINT_SERIAL
    Serial.print("H ");
    Serial.println(report.humidity);
    Serial.print("T ");
    Serial.println(report.temperature);
    driver.printBuffer("Xmit: ", &report, sizeof(StationReport));
#endif

    driver.send((uint8_t*)&report, sizeof(StationReport));
    driver.waitPacketSent();
    delay(WAIT_FIXED + random(WAIT_RANDOM));
}
