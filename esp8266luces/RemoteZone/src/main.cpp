#include <Arduino.h>

#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager
#include <PubSubClient.h>
#include <pb_decode.h>


#include "main.h"
#include "protocol.proto.pb.h"

const char* mqtt_server = "192.168.1.196";
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup() {
    Serial.begin(115200);    
    WiFiManager wifiManager;
    wifiManager.autoConnect("AutoConnectAP");    
    Serial.println("connected...yeey :)");
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
}

void reconnect() 
{
  // Loop until we're reconnected
  while (!client.connected()) 
  {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) 
    {
      Serial.println("connected");                 
      client.subscribe("inTopic");
    } 
    else 
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) 
{
  bool status;

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  SimpleMessage message = SimpleMessage_init_zero;  
  pb_istream_t stream = pb_istream_from_buffer(payload, length);

  status = pb_decode(&stream, SimpleMessage_fields, &message);
        
  /* Check for errors... */
  if (!status)
  {
      Serial.printf("Decoding failed: %s\n", PB_GET_ERROR(&stream));      
  }
  
  Serial.printf("data = [%d,%d,%b]\n", message.Pin, message.RGBint, message.End);      

    /* Print the data contained in the message. */
  
}

void loop() 
{
  if (!client.connected()) 
  {
    reconnect();
  }
  client.loop();
    // put your main code here, to run repeatedly:
    
}