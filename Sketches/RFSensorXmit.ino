// -*- c -*-

// Required libraries:
// RadioHead - http://www.airspayce.com/mikem/arduino/RadioHead/
// DHT - https://github.com/adafruit/DHT-sensor-library
// JeeLib - https://github.com/jcw/jeelib

// Sketch to read from a DHT22 and transmit it via a cheap 433MHz RF
// transmitter. Attempts to conserve power by going into deep sleep
// between transmissions and unpowering both the sensor and the radio
// when not in use.

// Connect the DHT's data pin to D2 and its VCC to pin D4
// Connect the RF transmitter's data pin to D12 and the VCC to D6

// This was written to run on an arduino nano. If you use a widely
// different board, you may have to check the powerOff function to
// make sure it disables the correct timer interrupt RadioHead uses.

// Be sure to change STATION_ID for each new sensor (0-255)

#include <RH_ASK.h>
#include <SPI.h>
#include <DHT.h>
#include <Ports.h>
#include <avr/power.h>

// Each station includes its ID when transmitting sensor readings
#define STATION_ID 5

// Uncomment to see debug information on a serial link
// Output is a bit mangled at times but readable
//#define PRINT_SERIAL

// Sensor config
#define DHT_PIN 2
#define DHT_POWER_PIN 4
#define DHT_TYPE DHT22

#define CELSIUS false
#define FAHRENHEIT true

// Radio config
#define RF_POWER_PIN 6
// This define is just for readability. It does NOT change which pin
// the RF uses
#define RF_XMIT_PIN 12

// Sleep for WAIT_FIXED plus a random amount between 0 and WAIT_RANDOM
// between transmissions (in milliseconds)
#define WAIT_FIXED 15000
#define WAIT_RANDOM 2000

typedef struct {
    float humidity;
    float temperature;
    uint8_t station_id;
} StationReport;

RH_ASK driver;
uint8_t station_id = STATION_ID;

DHT dht = DHT(DHT_PIN, DHT_TYPE);


// Watchdog ISR for Sleepy
ISR(WDT_vect) { Sleepy::watchdogEvent(); }

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
    pinMode(DHT_POWER_PIN, OUTPUT);
    digitalWrite(DHT_POWER_PIN, LOW);
    pinMode(RF_POWER_PIN, OUTPUT);
    digitalWrite(RF_POWER_PIN, LOW);

    minimisePower();
}

inline void pinUnused(int pin)
{
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
}

void minimisePower(void)
{
    for (int i = 2; i < 14; i++) {
        if (i != DHT_PIN && i != DHT_POWER_PIN && i != RF_POWER_PIN && i != RF_XMIT_PIN) {
            pinUnused(3);
        }
    }

    pinUnused(A0);
    pinUnused(A1);
    pinUnused(A2);
    pinUnused(A3);
    pinUnused(A4);
    pinUnused(A5);
    pinUnused(A6);
    pinUnused(A7);

    // Not using analog I/O
    power_adc_disable();
    // Not using SPI
    power_spi_disable();
    // Not using two-wire
    power_twi_disable();

    // Enabled only when Radio needs to work
    power_timer1_disable();
    // Never used
    power_timer2_disable();
}

void powerOff(int time)
{
    int result;
#ifdef PRINT_SERIAL
    Serial.print(time);
    Serial.println("ms sleep requested");
#endif
    // Round down to the nearest multiple of 64
    time &= 0xff80;
#ifdef PRINT_SERIAL
    Serial.print("Rounded to ");
    Serial.println(time);
    delay(100);
#endif
    // disable RadioHead's interrupts
    TIMSK1 &= ~(_BV(OCIE1A));
    // Power off
    result = Sleepy::loseSomeTime(time);
    // Re-enable RadioHead's interrupts
    TIMSK1 |= _BV(OCIE1A);
#ifdef PRINT_SERIAL
    if (result != 0) {
        Serial.println("Woke up early");
    }
#endif
}

void readSensor(StationReport *report)
{
    // power on sensor
    digitalWrite(DHT_POWER_PIN, HIGH);
    // Give it time to settle
    Sleepy::loseSomeTime(520);

    report->station_id = station_id;
    report->humidity = dht.readHumidity();
    report->temperature = dht.readTemperature(CELSIUS);

    // And power sensor off again
    digitalWrite(DHT_POWER_PIN, LOW);
    return;
}

void sendReport(StationReport *report)
{
    power_timer1_enable();
    // power on rf xmitter
    digitalWrite(RF_POWER_PIN, HIGH);
    // Give it time to settle
    Sleepy::loseSomeTime(192);

    // Send 3 times (can't hurt)
    driver.send((uint8_t*)report, sizeof(StationReport));
    driver.waitPacketSent();
    driver.send((uint8_t*)report, sizeof(StationReport));
    driver.waitPacketSent();
    driver.send((uint8_t*)report, sizeof(StationReport));
    driver.waitPacketSent();
    // power off RF
    digitalWrite(RF_POWER_PIN, LOW);
    power_timer1_disable();
}

void loop()
{
    StationReport report;

    readSensor(&report);

#ifdef PRINT_SERIAL
    Serial.print("H ");
    Serial.println(report.humidity);
    Serial.print("T ");
    Serial.println(report.temperature);
    driver.printBuffer("Xmit: ", (uint8_t*)&report, sizeof(StationReport));
#endif

    sendReport(&report);
    powerOff(WAIT_FIXED + random(WAIT_RANDOM));
}
