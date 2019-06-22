#include <ArduinoJson.h>
#include <DHT.h> //teperature&humidity
#define DHTPIN A0 // A0 for temperature & humidity
#define DHTTYPE DHT22 // DHT 22 (AM2302)
DHT dht(DHTPIN, DHTTYPE);

const int ledPin = 13;


void setup() 
{
 
  Serial.begin(9600);
  Serial.println();
  dht.begin();
  pinMode(ledPin,OUTPUT);
 
}

void loop()
{
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  StaticJsonDocument<256> doc;
  JsonObject root = doc.as<JsonObject>(); 
  doc["Temperature"] = t;
  doc["Humidity"] = h;
  serializeJson(doc, Serial);
  Serial.println();
  delay(5000);

  digitalWrite(ledPin,HIGH);
  delay(3000);

  
 }
