/*
driver.ino
Communicates over Serial with python
to alllow python control of CNC

Written By: Caleb Sanford (2019)
 */

struct Motor
{
    int dirPin;
    int stepPin;
    int stepDelay;
    float stepsPerInch;
    int current;
};

Motor X = {3, 4, 600, 1310, 0};
Motor Y = {5, 6, 600, 1310, 0};
Motor Z = {7, 8, 600, 5025, 0};

String readString;

void setup()
{
    Serial.begin(9600);
    pinMode(X.dirPin, OUTPUT);
    pinMode(X.stepPin, OUTPUT);
    pinMode(Y.dirPin, OUTPUT);
    pinMode(Y.stepPin, OUTPUT);
    pinMode(Z.dirPin, OUTPUT);
    pinMode(Z.stepPin, OUTPUT);
}

void loop()
{
    while (!Serial.available()) {} // wait for data to arrive

    while (Serial.available())
    {
        if (Serial.available())
        {
            char c = Serial.read();
            readString += c;
            delay(2);
        }
    }

    char *readin = (char *)readString.c_str();
    char *x = strtok(readin, ",");
    char *y = strtok(NULL, ",");

    if (strcmp(x, "z") == 0)
    {
        goto_z(Z, atof(y));
        Serial.println(1);
    }

    else if (strcmp(x, "p") == 0)
    {
        if (strcmp(y, "x") == 0)
        {
            Serial.println(get_motor_location(X))
        }

        else if (strcmp(y, "y") == 0)
        {
            Serial.println(get_motor_location(Y))
        }

        else if (strcmp(y, "z") == 0)
        {
            Serial.println(get_motor_location(Z))
        }
        else
        {
            Serial.println(2);
        }
    }

    else
    {
        goto_xy(X, Y, atof(x), atof(y));
        Serial.println(1);
    }
    Serial.flush();
    readString = "";
}

void goto_xy(Motor MotorX, Motor MotorY, float x, float y)
{
    // Set the directions to move in

    float xdir = x * MotorX.stepsPerInch;
    float ydir = y * MotorY.stepsPerInch;
    set_direction(MotorX, xdir);
    set_direction(MotorY, ydir);
    MotorX.current = MotorX.current + xdir;
    MotorY.current = MotorY.current + ydir;
    xdir = abs(xdir);
    ydir = abs(ydir);
    // Move
    for (int i = 0; i < max(xdir, ydir); i++)
    {
        if (i < xdir)
        {
            digitalWrite(MotorX.stepPin, HIGH);
        }
        if (i < ydir)
        {
            digitalWrite(MotorY.stepPin, HIGH);
        }
        delayMicroseconds(MotorX.stepDelay);
        digitalWrite(MotorX.stepPin, LOW);
        digitalWrite(MotorY.stepPin, LOW);
        delayMicroseconds(MotorX.stepDelay);
    }
}

void goto_z(Motor MotorZ, float z)
{
    float zdir = z * MotorZ.stepsPerInch;
    set_direction(MotorZ, zdir);
    MotorZ.current = MotorZ.current + zdir;
    zdir = abs(zdir);
    for (int i = 0; i < zdir; i++)
    {
        digitalWrite(MotorZ.stepPin, HIGH);
        delayMicroseconds(MotorZ.stepDelay);
        digitalWrite(MotorZ.stepPin, LOW);
        delayMicroseconds(MotorZ.stepDelay);
    }
}

void set_direction(Motor motor, float direction)
{
    if (direction > 0)
    {
        digitalWrite(motor.dirPin, HIGH);
    }
    else
    {
        digitalWrite(motor.dirPin, LOW);
    }
}

int get_motor_location(Motor motor)
{
    return motor.current / motor.stepsPerInch;
}