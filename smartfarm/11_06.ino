#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <Adafruit_NeoPixel.h>

#define NeoPixel_PIN 16 // LED Pin Number
#define NUMPIXELS 16 // LED 갯수
#define DHTPIN 4
#define DHTTYPE DHT11    
#define CDS_PIN 11
#define WATER_LEVEL_PIN 5
#define SOIL_MOISTURE_PIN 19
#define motorPin 10 //relay Pin Number

#define RED 17
#define GREEN 18
#define BLUE 8

#define NeoPixel_relay_Pin 1
#define LED_12V_relay_Pin 2

const char* ssid = "yuki";
const char* password = "asdf5561";
const char* mqtt_server = "158.180.89.1";

WiFiClient espClient;
PubSubClient client(espClient);

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, NeoPixel_PIN, NEO_GRB + NEO_KHZ800);

long lastMsg = 0;
const long interval = 2000;

char msg[150];

float Humi, Temp;
int cdsValue;
int waterLevel;
int moistureValue, moisturePercent;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(CDS_PIN, INPUT);
  pinMode(WATER_LEVEL_PIN, INPUT_PULLUP);
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(motorPin, OUTPUT);
  pinMode(LED_12V_relay_Pin, OUTPUT);
  pinMode(NeoPixel_relay_Pin, OUTPUT);
  digitalWrite(motorPin,HIGH);
  digitalWrite(LED_12V_relay_Pin, HIGH);
  digitalWrite(NeoPixel_relay_Pin,HIGH);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  pinMode(RED , OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  strip.begin(); //NeoPixel 스트립 시작
  strip.show(); //NeoPixel OFF

}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  if (String(topic) == "Sensor/Environment/CDS/Send") {
    if (message == "LED ON") {
      Serial.println("h");
      digitalWrite(LED_12V_relay_Pin, LOW); // 12V LED 릴레이 켜기
      digitalWrite(NeoPixel_relay_Pin, LOW); // NeoPixel 릴레이 켜기 (필요한 경우)
      setStripColor(255, 255, 255, 0); // 밝은 흰색 설정, delayTime을 0으로 설정
      strip.show(); // NeoPixel 색상 적용
    } 
    else if (message == "LED OFF") {
      Serial.println("j");
      digitalWrite(LED_12V_relay_Pin, HIGH); // 12V LED 릴레이 끄기
      digitalWrite(NeoPixel_relay_Pin, HIGH); // NeoPixel 릴레이 끄기 (필요한 경우)
      // NeoPixel을 끄기 위해 색상 설정
      setStripColor(0, 0, 0, 0); // 모든 LED 끄기, delayTime을 0으로 설정
      strip.show(); // NeoPixel 색상 적용
    }
  }
  if (String(topic) == "Sensor/Environment/Temperature/Send"){
    if (message == "Temperature High"){
      analogWrite(RED, 0);
      analogWrite(GREEN, 0); 
      analogWrite(BLUE, 255);
    }
    else if (message = "Temperature Normal"){
      analogWrite(RED, 0);
      analogWrite(GREEN, 255); //파랑
      analogWrite(BLUE, 0); 
    }
    else if (message = "Temperature Low"){
      analogWrite(RED, 0);
      analogWrite(GREEN, 0);
      analogWrite(BLUE, 255);
    }
  }
  if (String(topic) == "Sensor/Environment/SoliMoisture/Send"){
    if (message == "Pum ON"){
      digitalWrite(motorPin,LOW);
      delay(2000);
      digitalWrite(motorPin,HIGH);
      delay(2000);
      client.publish("Sensor/Environment/waterPum","waterPum On");
    }
    else if(message == "Pum OFF"){
      digitalWrite(motorPin, HIGH);
      client.publish("Sensor/Environment/waterPum", "waterPum OFF");      
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("Sensor/Environment/CDS/Send");
      client.subscribe("Sensor/Environment/Temperature/Send");
      client.subscribe("Sensor/Environment/SoliMoisture/Send");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// DHT11
float getHumi() {
  float h = dht.readHumidity();
 
  if (isnan(h)) {
    Serial.println("Failed to read from DHT sensor!");
    return -1;
  }

  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %\t");
  return h;
}

float getTemp() {
  float t = dht.readTemperature();

  if (isnan(t)) {
    Serial.println("Failed to read temperature from DHT sensor!");
    return -1;
  }

  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println(" *C ");
  return t;
}

// CDS 가리면 올라가고 빛이 있으면 내려감
int getCDSValue() {
  cdsValue = analogRead(CDS_PIN);  
  Serial.print("CDS Sensor Value: ");
  Serial.println(cdsValue);
  return cdsValue;
}

//NeoPixel led 색상 설정
void setStripColor(uint8_t red, uint8_t green, uint8_t blue, int delayTime) {
  for (int i = 0; i < NUMPIXELS; i++) {
    strip.setPixelColor(i, strip.Color(red, green, blue)); // 각 LED의 색상 설정
    strip.show();                                          // 색상 적용
    delay(delayTime);                                      // 지연 시간
  }
}
void neoPixelOFF(){
  strip.show();
}
// 수위 센서 Max 3600 Min 2600
int getWaterLevelValue() {
  int waterLevelAnalog = analogRead(WATER_LEVEL_PIN);
  Serial.print("Water Level Sensor Analog Value: ");
  Serial.println(waterLevelAnalog);

  // 임계값을 설정하여 수위 상태 판단 (예: 3000)
  if (waterLevelAnalog < 3000) {
    Serial.println("Water Level: LOW");
    return waterLevelAnalog;
  } else {
    Serial.println("Water Level: HIGH (Enough)");
    return waterLevelAnalog;
  }
}

// 토양 습도 센서
int getSoilMoisture() {
  moistureValue = analogRead(SOIL_MOISTURE_PIN);
  moisturePercent = map(moistureValue, 4096,0, 0, 100);

  Serial.print("Soil Moisture: ");
  Serial.print(moisturePercent);
  Serial.println("%");
  return moisturePercent;
}


void mqtt_publish(float Humi, float Temp, int cdsValue, int waterLevel, int moisturePercent) {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;
    
    // 각 데이터를 MQTT 메시지로 발행
    String humidityPacket = String(Humi) + "%";
    client.publish("Sensor/Environment/Humidity", humidityPacket.c_str());
    
    String temperaturePacket = String(Temp) + "*C";
    client.publish("Sensor/Environment/Temperature", temperaturePacket.c_str());
    
    String cdsPacket = String(cdsValue);
    client.publish("Sensor/Environment/CDS", cdsPacket.c_str());
    
    String waterLevelPacket = String(waterLevel);
    client.publish("Sensor/Environment/WaterLevel", waterLevelPacket.c_str());
    
    String moisturePacket = String(moisturePercent) + "%";
    client.publish("Sensor/Environment/SoilMoisture", moisturePacket.c_str());
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();
  
  
  Humi = getHumi();
  Temp = getTemp();
  cdsValue = getCDSValue();
  waterLevel = getWaterLevelValue();
  moisturePercent = getSoilMoisture();
  if (Humi != -1 && Temp != -1) {
    mqtt_publish(Humi, Temp, cdsValue, waterLevel, moisturePercent);
  }
  
  
}

