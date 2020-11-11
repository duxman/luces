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

#define FASTLED_ESP8266_RAW_PIN_ORDER
#define FASTLED_ESP8266_NODEMCU_PIN_ORDER
#define FASTLED_ESP8266_D1_PIN_ORDER
#include <Arduino.h>


#include "config.h"
#include <ESP8266WiFi.h>
//#include <PubSubClient.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>
#include <pb_decode.h>
#define __FASTLED__ 1
#ifdef __FASTLED__
  //#define FASTLED_ESP8266_RAW_PIN_ORDER
  //#define FASTLED_ALLOW_INTERRUPTS 0
  //#define FASTLED_INTERRUPT_RETRY_COUNT 3
  #include <FastLED.h>
  CRGB leds[NUM_LEDS];
#else
  #define NEO_KHZ400 0x0100 ///< 400 KHz data transmission
  #include <Adafruit_NeoPixel.h>
  Adafruit_NeoPixel leds(NUM_LEDS, PIN, NEO_RGB + NEO_KHZ800); 
#endif
#include "protocol.proto.pb.h"
#include "main.h"

///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////
display msgdisplay = display_init_zero;        
led msgled = led_init_zero;
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
void decodedisplay( byte* payload,unsigned int length )
{       
    Serial.printf("try decoding display \n %d",length);          
    msgdisplay.frame.funcs.decode=&decodeled;
    pb_istream_t stream = pb_istream_from_buffer(payload,length);    
    bool status = pb_decode(&stream, display_fields, &msgdisplay);

    if (!status)
    {
        Serial.printf("Decoding failed decodedisplay: %s\n", PB_GET_ERROR(&stream));            
        return;
    }
    Serial.printf("display: fin = %d  inicio = %d \n", msgdisplay.Fin, msgdisplay.Ini);            

    if( msgdisplay.Fin == true)
      #ifdef __FASTLED__
        FastLED.show();
        FastLED.clear();
      #else
        leds.show();
        leds.fill(0);        
      #endif
}

bool decodeled( pb_istream_t *stream, const pb_field_t *field, void **arg)
{    
    bool status = pb_decode(stream, led_fields, &msgled);
    if (!status)
    {
        Serial.printf("Decoding failed decodeled: %s\n", PB_GET_ERROR(stream));            
        return false;
    }
   // Serial.printf("Decoding PIN decodeLed %d,Color %d ", msgled.Pin, msgled.Color);                
    
     #ifdef __FASTLED__
       leds[msgled.Pin] = CRGB(msgled.Color);
      #else
        leds.setPixelColor( msgled.Pin,msgled.Color);        
      #endif
    return true;

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
  WiFi.begin( WIFI_SSID, WIFI_PASSWD);
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
  Serial.println("Connecting to MQTT..." );  
  mqttClient.connect();
}

void onMqttConnect(bool sessionPresent)
 {
  Serial.println("Connected to MQTT.");
  Serial.print("Session present: ");
  ConfigureFastLed();
  Serial.println(sessionPresent);
  
  uint16_t packetIdSub = mqttClient.subscribe(MQTT_TOKEN, 2);  
  Serial.print("Subscribing at QoS 2, packetId: ");
  Serial.println(packetIdSub);  
  
  
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
    decodedisplay((byte *)payloadBuffer,total);     
    free(payloadBuffer);
  }
  
}
///////////////////////////////////////////////////////////////////////
////                 MQTT
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 FASTLED
///////////////////////////////////////////////////////////////////////

void ConfigureFastLed() 
{
  delay(3000); // sanity delay
  Serial.println("Configuring led strip");
  #ifdef __FASTLED__
    
    FastLED.addLeds<CHIPSET, PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    //FastLED.addLeds<WS2812Controller800Khz, PIN>(leds, NUM_LEDS); 
    FastLED.clear();
    FastLED.show();
    Serial.println("FastLed Configured");

  #else    
    leds.begin();
    leds.setBrightness(50);
    leds.fill(0); 
    leds.show();        
    Serial.println("Adafruit Configure Configured");
  #endif
  printConfigStep( 1);
  
}
// Config step  1 = FastLed
//              2 = wifi conecting 
//              3 = wifi Conected
//              4 = Mqtt conecting
//              5 = Mqtt Conected
void printConfigStep( int ConfigStep)
{
  int iniLed=(ConfigStep-1)*10;
  int finLed=ConfigStep;
  int color= CRGB(255,0,0);  
  for( int i=iniLed ; i< finLed ; i++)
  {
    Serial.printf("Print led %d\r\n",i);
    #ifdef __FASTLED__
      
      FastLED.clear();
      leds[i] = CRGB(0,0,150);
      FastLED.show();      
    #else
      leds.fill(0); 
      leds.setPixelColor( i,msgled.Color);        
      leds.show(); 
    #endif
    delay(25);
  }
}
///////////////////////////////////////////////////////////////////////
////                 FASTLED
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

void loop() {
}

///////////////////////////////////////////////////////////////////////
////                 ARDUINO
///////////////////////////////////////////////////////////////////////
