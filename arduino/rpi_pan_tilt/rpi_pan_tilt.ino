#include <Servo.h> // Import the library

Servo servoPan, servoTilt; // Create servo object
String data = ""; // Store incoming commands (buffer)

void setup() {
    // Setup servos on PWM capable pins
    servoPan.attach(9); 
    servoTilt.attach(10);

    Serial.begin(9600); // Start serial at 9600 bps (speed)

    servoPan.write(60);
     // servoPan needs to be betwen 100P left and 20P right
     // 70P is about as left as we should go
    servoTilt.write(70);
    // servoTilt needs to be betwen 50T down and 100T up
    // 8OT is aobut as up as we should go

}

void loop() {
    while (Serial.available() > 0)
    {
        // If there is data
        char singleChar = Serial.read(); // Read each character
        delay(2); // slow looping to allow buffer to fill with next character

        if (singleChar == 'P') {
            // Move pan servo
            servoPan.write(data.toInt());
            data = ""; // Clear buffer
        }
        else if (singleChar == 'T') {
            // Move tilt servo
            servoTilt.write(data.toInt());
            data = ""; // Clear buffer
        }
        else {
            data += singleChar; // Append new data
        }
    }
}
