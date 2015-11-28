/* Relies on the DHT11 libraries from Adafruit */
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22
#define LEDPIN 13
#define CELSIUS false
#define FAHRENHEIT true


DHT dht = DHT(DHTPIN, DHTTYPE);

void setup()
{
    Serial.begin(9600);
    delay(100);
    //pinMode(LEDPIN, OUTPUT);
}

void nan_print(float value)
{
    if (isnan(value)) { Serial.print("NaN"); }
    else { Serial.print(value); }
    return;
}

void nan_println(float value)
{
    nan_print(value);
    Serial.print("\r\n");
    return;
}

void get_humidity(void)
{
    float h = 0.0f;

    //digitalWrite(LEDPIN, LOW);
    h = dht.readHumidity();
    //digitalWrite(LEDPIN, HIGH);
    Serial.print("Humidity: ");
    nan_println(h);
    return;
}

void get_temperature(void)
{
    //digitalWrite(LEDPIN, LOW);
    float t = dht.readTemperature(CELSIUS);
    //digitalWrite(LEDPIN, HIGH);
    Serial.print("Temperature: ");
    nan_println(t);
    return;
}

void loop()
{
    char cmd;
    
    cmd = Serial.read();
    switch (cmd) {
    case 't':
        get_temperature();
        break;
    case 'h':
        get_humidity();
        break;
    case 'e':
        get_temperature();
        get_humidity();
        break;
    }
}
