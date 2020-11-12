/*
 * Copyright (c) 2020-2037 duxman.
 *
 * This file is part of Duxman Luces 
 * (see https://github.com/duxman/luces).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */


#include <Arduino.h>
#include "config.h"
#include <ESP8266WiFi.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>
#include <pb_decode.h>
#include "protocol.proto.pb.h"
#include "main.h"


///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////
ledLevel msgled = ledLevel_init_zero;

AsyncMqttClient mqttClient;
Ticker mqttReconnectTimer;
WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;
Ticker wifiReconnectTimer;
byte *payloadBuffer;
int posicion=0;
///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 DECODIFICACION
///////////////////////////////////////////////////////////////////////
void decodeLedLevel( byte* payload,unsigned int length )
{       
    //Serial.printf("try decoding ledLevel \n %d",length);              
    pb_istream_t stream = pb_istream_from_buffer(payload,length);    
    bool status = pb_decode(&stream, ledLevel_fields, &msgled);
    if (!status)
    {
        Serial.printf("Decoding failed ledlevel: %s\n", PB_GET_ERROR(&stream));            
        return;
    }  
    Serial.printf("New level %d\r\n",msgled.Level);        
    writeLeds( msgled.Level );
    

}

///////////////////////////////////////////////////////////////////////
////                 DECODIFICACION
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 WIFI
///////////////////////////////////////////////////////////////////////

void connectToWifi() 
{
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWD);
}

void onWifiConnect(const WiFiEventStationModeGotIP& event) {
  Serial.println("Connected to Wi-Fi.");
  connectToMqtt();
}

void onWifiDisconnect(const WiFiEventStationModeDisconnected& event) {
  Serial.println("Disconnected from Wi-Fi.");
  mqttReconnectTimer.detach(); // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
  wifiReconnectTimer.once(2, connectToWifi);
}
///////////////////////////////////////////////////////////////////////
////                 WIFI
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 MQTT
///////////////////////////////////////////////////////////////////////
void connectToMqtt() 
{
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();  
}

void onMqttConnect(bool sessionPresent)
 {
  Serial.println("Connected to MQTT.");
  Serial.print("Session present: ");
  
  Serial.println(sessionPresent);
  
  uint16_t packetIdSub = mqttClient.subscribe(MQTT_TOKEN, 2);  
  Serial.print("Subscribing at QoS 2, packetId: ");
  Serial.println(packetIdSub);  
  ConfigureLed();
  
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason)
 {
  Serial.println("Disconnected from MQTT.");

  if (WiFi.isConnected()) 
  {
    mqttReconnectTimer.once(2, connectToMqtt);
  }
}

void onMqttSubscribe(uint16_t packetId, uint8_t qos) 
{
  Serial.println("Subscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
  Serial.print("  qos: ");
  Serial.println(qos);
}

void onMqttUnsubscribe(uint16_t packetId) 
{
  Serial.println("Unsubscribe acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}

void onMqttMessage(char* topic, char* payload, AsyncMqttClientMessageProperties properties, size_t len, size_t index, size_t total) 
{
  Serial.printf("Publish received. len %d  index %d total %d len payload %d \r\n", (int)len, (int)index, (int)total,sizeof(payload));  

  if (index==0)
    payloadBuffer = (byte*) malloc(total);

  memcpy( payloadBuffer+index,payload,len); 
  if( index+len == total)
  {
    Serial.printf("Mensaje completo len\r\n");  
    decodeLedLevel((byte *)payloadBuffer,total);     
    free(payloadBuffer);
  }
  
}
///////////////////////////////////////////////////////////////////////
////                 MQTT
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 LED STRIP
///////////////////////////////////////////////////////////////////////

void ConfigureLed() 
{
    Serial.printf("Initializing Leds\r\n"); 
    for( int i=0 ; i < NUM_PINS;i++)
    {
      pinMode(PINES[i], OUTPUT);
    }   

    for( int j=0 ; j < NUM_PINS ; j++)
    {
      for( int i=0 ; i < NUM_PINS;i++)
      {
        //digitalWrite(PINES[i], HIGH);  
        Serial.printf("enciendo %d \r\n",PINES[i]); 
        analogWrite(PINES[i], LED_BRIGHT);  
        delay(200);
        //digitalWrite(PINES[i], LOW);  
        Serial.printf("Apago %d \r\n",PINES[i]); 
        analogWrite(PINES[i], 0);  
      }
    }            
}

void offLeds()
{
 for( int i=0; i< NUM_PINS ;i++) 
  {
    //digitalWrite(PINES[i], LOW);  
    analogWrite(PINES[i], LED_BRIGHT_OFF);  
    Serial.printf("off leds %d\r\n",i);        
               
  }
}
void writeLeds( int level)
{
    for( int i=NUM_PINS-1; i>=0 ;i--) 
    {
        int min = LEVELS[i][0];
        int max = LEVELS[i][1];
        if( min != max)
        {
          if(level < min )
          {
            analogWrite(PINES[i], LED_BRIGHT_OFF); 
          }
          if(level > max )
          {
            analogWrite(PINES[i], LED_BRIGHT_LOW); 
          }          
          if(level >= min && level <= max )
          {
            analogWrite(PINES[i], LED_BRIGHT); 
          }
        }
        else
        {
          if( level == max)
          {
              analogWrite(PINES[i], LED_BRIGHT);                
            Serial.printf("Write New level %d\r\n",msgled.Level);        
          }
          else
          {
            analogWrite(PINES[i], LED_BRIGHT_OFF);  
          }
        }
    }
}
///////////////////////////////////////////////////////////////////////
////                 LED STRIP
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 ARDUINO
///////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(BAUDSSERIAL);
  Serial.println("/////////////////////////////////////////////////////////////////////");
  Serial.println("/////////////                      INICIO                     ///////");
  Serial.println("/////////////////////////////////////////////////////////////////////");
  

  wifiConnectHandler = WiFi.onStationModeGotIP(onWifiConnect);
  wifiDisconnectHandler = WiFi.onStationModeDisconnected(onWifiDisconnect);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onSubscribe(onMqttSubscribe);
  mqttClient.onUnsubscribe(onMqttUnsubscribe);
  mqttClient.onMessage(onMqttMessage);  
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  
  
  connectToWifi();  
}

void loop()
{
}
