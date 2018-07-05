#include <Wire.h>
byte recieved_data;
void setup() {
  Serial.begin(9600);
  Serial.println("nunchuck test starting");
  Wire.begin();                                                             //Start the I2C bus as master
  TWBR = 12;                                                                //Set the I2C clock speed to 400kHz
}

void loop() {
  if (Serial.available()) 
  {
    recieved_data = Serial.read();
    Serial.print(recieved_data);
    Serial.print("\n");
  }
  else 
  {
  //  Serial.print("not working \n");
  }
  }
