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
#include <IotWebConf.h>
#include "webconfig.hpp"
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
IPAddress mqttServer = IPAddress();
int       mqttPort = 0;

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
////                 CONFIGURACION
///////////////////////////////////////////////////////////////////////

void configureWifi()
{	
	MqttServerParam=IotWebConfParameter("Mqtt Server Param", "StringMqttServerParam", StringMqttServerParam, STRING_LEN);
	MqttPortParam=IotWebConfParameter("Mqtt Port Param", "IntMqttPortParam", IntMqttPortParam, NUMBER_LEN);
	MqttTokenParam=IotWebConfParameter("Mqtt Token Param", "StringMqttTokenParam", StringMqttTokenParam, STRING_LEN);
	separator=IotWebConfSeparator("--------------------------------------"); 
	PinsParam=IotWebConfParameter("Pins Param", "StringPinsParam", StringPinsParam, STRING_LEN);
	ValuesParam=IotWebConfParameter("Values Param", "StringValuesParam", StringValuesParam, STRING_LEN);		
	
	webConfig.addParameter(&MqttServerParam);
	webConfig.addParameter(&MqttPortParam);
	webConfig.addParameter(&MqttTokenParam);
	webConfig.addParameter(&PinsParam);
	webConfig.addParameter(&ValuesParam);
	
	webConfig.setConfigSavedCallback(&configSaved);
 //webConfig.setWifiConnectionCallback(&wifiConnected);
	webConfig.getApTimeoutParameter()->visible = true;
	
	boolean validConfig = webConfig.init();	
	if (!validConfig)
	{
		StringMqttServerParam[0]='\0';
		IntMqttPortParam[0]='\0';
		StringMqttTokenParam[0]='\0';
		StringPinsParam[0]='\0';
		StringValuesParam[0]='\0';
	}	
	server.on("/", handleRoot);
	server.on("/config", []{ webConfig.handleConfig(); });
	server.onNotFound([](){ webConfig.handleNotFound(); });	
}


void configSaved()
{
  Serial.println("Configuration was updated.");
}


void handleRoot()
{
  // -- Let IotWebConf test and handle captive portal requests.
  if (webConfig.handleCaptivePortal())
  {
    // -- Captive portal request were already served.
    return;
  }
  String s = "<!DOCTYPE html><html lang=\"en\"><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1, user-scalable=no\"/>";
  s += "<title>IotWebConf 03 Custom Parameters</title></head><body>Hello world!";
  s += "<ul>";
  s += "<li>MQTT SERVER: ";
  s += StringMqttServerParam;
  s += "<li>MQTT PORT: ";
  s += atoi(IntMqttPortParam);
  s += "<li>MQTT TOKEN: ";
  s += StringMqttTokenParam;
  s += "<li>PIN LIST: ";
  s += StringPinsParam;
  s += "<li>VALUE LIST: ";
  s += StringValuesParam;
  s += "</ul>";
  s += "Go to <a href='config'>configure page</a> to change values.";
  s += "</body></html>\n";

  server.send(200, "text/html", s);
}

///////////////////////////////////////////////////////////////////////
////                 CONFIGURACION
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
  //WiFi.begin(WIFI_SSID, WIFI_PASSWD);
  WiFi.begin(webConfig.getWifiSsidParameter()->valueBuffer, webConfig.getWifiPasswordParameter()->valueBuffer);
}

void wifiConnected()
{
  Serial.printf("Conectados a wifi ... set params mqtt %s:%s",StringMqttServerParam,IntMqttPortParam);
  mqttServer.fromString(StringMqttServerParam);
  mqttPort = atoi(IntMqttPortParam);
  mqttClient.setServer(mqttServer,mqttPort);  
}

void onWifiConnect(const WiFiEventStationModeGotIP& event) {
  Serial.println("Connected to Wi-Fi.");
  delay(5000);
  wifiConnected();  
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
  
  uint16_t packetIdSub = mqttClient.subscribe(StringMqttTokenParam, 2);  
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
 String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void ConfigureLed() 
{
    Serial.printf("Initializing Leds\r\n"); 
    String PinString(StringPinsParam);
    String LevelString(StringValuesParam);     
    for(int i=0; i<NUM_PINS;i++)
    {
      String PinTemp;
      String LevelTemp;
      PinTemp = getValue(PinString, ',', i);
      LevelTemp = getValue(LevelString, ',', i);

      Serial.print("Read Config Led :"); 
      Serial.print(PinTemp);
      Serial.print(" Values = " );
      Serial.print(LevelTemp);
      
      LEVELS[i][0] = getValue(LevelTemp, '-', 0).toInt();
      LEVELS[i][1] = getValue(LevelTemp, '-', 1).toInt();
      Serial.printf(" Levels (%d-%d)\r\n", LEVELS[i][0],LEVELS[i][1]);

      PINES[i] = PinTemp.toInt();
      if(PINES[i] != 0)
        pinMode(PINES[i], OUTPUT);
    }       

    for( int j=0 ; j < NUM_PINS ; j++)
    {
      for( int i=0 ; i < NUM_PINS;i++)
      {
        if( PINES[i] != 0)
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
        
        if(PINES[i] != 0)
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
              Serial.printf("Write New level %d on %d\r\n",msgled.Level,LED_BRIGHT_LOW);  
            }          
            if(level >= min && level <= max )
            {
              analogWrite(PINES[i], LED_BRIGHT); 
              Serial.printf("Write New level %d on %d\r\n",msgled.Level,LED_BRIGHT);  
            }
          }
          else
          {
            if( level == max)
            {
                analogWrite(PINES[i], LED_BRIGHT);                                 
                Serial.printf("Write New level %d on %d\r\n",msgled.Level,LED_BRIGHT);  
            }
            else
            {
              analogWrite(PINES[i], LED_BRIGHT_OFF);  
            }
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
  configureWifi();

  wifiConnectHandler = WiFi.onStationModeGotIP(onWifiConnect);
  wifiDisconnectHandler = WiFi.onStationModeDisconnected(onWifiDisconnect);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onSubscribe(onMqttSubscribe);
  mqttClient.onUnsubscribe(onMqttUnsubscribe);
  mqttClient.onMessage(onMqttMessage);      
  
  

  //connectToWifi();  
}

void loop()
{
  webConfig.doLoop();
}
