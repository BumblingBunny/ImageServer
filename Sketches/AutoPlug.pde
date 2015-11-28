// -*- c -*-

// Serial controlled relay sketch, using the ubiquitous boards from
// eBay (my particular one is 8-way and has "Songle" SRD-05VDC-SL-C
// mechanical relays. I only use the first 6

// How many relays to use, see also pin_map
#define RELAY_COUNT 6

////
// Serial command handling
////
#define CMD_BUF_SIZE 2
#define CMD_CHAR(x) x[0]
#define CMD_ARG(x)  x[1]
#define CMD_CLEAR(x) memset(x, 0, CMD_BUF_SIZE)

// All functions acting on relays expect an index into this array to
// determine which data pin to affect.
int pin_map[RELAY_COUNT] = {2, 3, 4, 5, 6, 7};

void setup()
{
    Serial.begin(9600);
    for (int i = 0; i < RELAY_COUNT; i++) {
        pinMode(pin_map[i], OUTPUT);
    }
}

bool relay_toggle(int which)
{
    bool state;

    Serial.print("->");
    Serial.print(which);

    which = pin_map[which];

    state = digitalRead(which);
    print_bool(!state);
 
    digitalWrite(which, !state);
    return !state;
}

bool relay_set(int which, bool value)
{
    bool state;
    which = pin_map[which];
    
    state = digitalRead(which);
    if (value != state) {
        digitalWrite(which, value);
    }
}

void print_bool(bool b)
{
    if (b) { Serial.println(" HIGH"); }
    else { Serial.println(" LOW"); }
}

void relay_status()
{
    for (int i = 0; i < RELAY_COUNT; i++) {
        Serial.print("#");
        Serial.print(i);
        print_bool(digitalRead(pin_map[i]));
    }
}

void read_buf(char *buf, int buf_size)
{
    int read = 0;
    int count = 0;

    while (1) {
        if (Serial.available()) {
            read = Serial.read();
            if  (0 > read || 0 != isspace((char)read)) { 
                continue;
            }
            if (read == '*') {
                // reset comms
                count = 0;
                continue;
            }

            buf[count++] = (byte)read;
            if (count >= buf_size) {
                break;
            }
        }
    }
    return;
}

void loop()
{
    byte buf[CMD_BUF_SIZE];

    read_buf(buf, CMD_BUF_SIZE);

    if (CMD_CHAR(buf) == '?') {
        relay_status();
        CMD_CLEAR(buf);
        Serial.println("--END--");
        return;
    }

    if (CMD_ARG(buf) < '0' && CMD_ARG(buf) > '9') {
        // garbage
        CMD_CLEAR(buf);
        return;
    }

    switch((int)CMD_CHAR(buf)) {
    case 't': // toggle
        relay_toggle((int)(CMD_ARG(buf) - '0'));
        break;
    case 'e': // enable
        relay_set((int)(CMD_ARG(buf) - '0'), LOW);
        break;
    case 'd': // disable
        relay_set((int)(CMD_ARG(buf) - '0'), HIGH);
        break;
    case 'c': // count
        Serial.println(RELAY_COUNT);
        break;
    default:
        break;
    }
    relay_status();
    CMD_CLEAR(buf);
    Serial.println("--END--");
}
