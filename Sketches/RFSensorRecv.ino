// -*- c -*-

// Required libraries:
// RadioHead - http://www.airspayce.com/mikem/arduino/RadioHead/

// Sketch to receive sensor data via a cheap 433MHz receiver
// and then print them on the serial link. RadioHead expects
// the data pin for the receiver to be on D11


#include <RH_ASK.h>
#include <SPI.h>

RH_ASK driver;

typedef struct {
    float humidity;
    float temperature;
    uint8_t station_id;
} StationReport;


void setup()
{
    Serial.begin(9600);
    if (!driver.init()) {
        Serial.println("init failed");
    }
}

void printStationReport(StationReport *r)
{
    Serial.print("S:");
    Serial.print(r->station_id);
    Serial.print(" H:");
    Serial.print(r->humidity);
    Serial.print(" T:");
    Serial.println(r->temperature);
}

void loop()
{
    uint8_t recv_buffer[RH_ASK_MAX_MESSAGE_LEN];
    uint8_t bytes_recvd = sizeof(recv_buffer);
    StationReport *rep;
    
    if (driver.recv(recv_buffer, &bytes_recvd)) {
        if (bytes_recvd == sizeof(StationReport)) {
            printStationReport((StationReport*)recv_buffer);
        }
    }
}
