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

#ifdef SP01
  #define FASTLED_ESP8266_NODEMCU_PIN_ORDER
  #define FASTLED_ESP8266_RAW_PIN_ORDER  
  #define FASTLED_ESP8266_D1_PIN_ORDER
#endif
#include <Arduino.h>
#include <IotWebConf.h>
#include "webconfig.hpp"
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
  CRGB* leds;
#else
  #define NEO_KHZ400 0x0100 ///< 400 KHz data transmission
  #include <Adafruit_NeoPixel.h>
  Adafruit_NeoPixel leds;
#endif
#include "protocol.proto.pb.h"
#include "main.h"
///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////
display msgdisplay = display_init_zero;        
led msgled = led_init_zero;
IPAddress mqttServer = IPAddress();
int       mqttPort = 0;
AsyncMqttClient mqttClient;
Ticker mqttReconnectTimer;
WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;
Ticker wifiReconnectTimer;
byte *payloadBuffer;
int posicion=0;
char wifiName[100];
///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 CONFIGURACION
///////////////////////////////////////////////////////////////////////

IotWebConf webConfig = IotWebConf(getWifiName(), &dnsServer, &server, INITIAL_PASS, CONFIG_VERSION);
void configureWifi()
{	
  Serial.print("Wifi : ");Serial.println(getWifiName());
	MqttServerParam=IotWebConfParameter("Mqtt Server Param", "StringMqttServerParam", StringMqttServerParam, STRING_LEN);
	MqttPortParam=IotWebConfParameter("Mqtt Port Param", "IntMqttPortParam", IntMqttPortParam, NUMBER_LEN);
	MqttTokenParam=IotWebConfParameter("Mqtt Token Param", "StringMqttTokenParam", StringMqttTokenParam, STRING_LEN);
	separator=IotWebConfSeparator("--------------------------------------"); 
	PinsParam=IotWebConfParameter("Pin Param", "StringPinsParam", StringPinsParam, NUMBER_LEN);
	ValuesParam=IotWebConfParameter("Leds Number Param", "StringValuesParam", StringValuesParam, NUMBER_LEN);		
	
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
  s += "<li>PIN: ";
  s += StringPinsParam;
  s += "<li>LEDS NUMBER: ";
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
void decodedisplay( byte* payload,unsigned int length )
{       
    Serial.printf("try decoding display %d\n",length);          
    msgdisplay.frame.funcs.decode=&decodeled;
    pb_istream_t stream = pb_istream_from_buffer(payload,length);    
    bool status = pb_decode(&stream, display_fields, &msgdisplay);

    if (!status)
    {
        Serial.printf("Decoding failed decodedisplay: %s\n", PB_GET_ERROR(&stream));            
        return;
    }
    Serial.printf("display: fin = %d  inicio = %d \n", msgdisplay.Fin, msgdisplay.Ini);            

    Serial.printf("try to show \n");          
    if( msgdisplay.Fin == true)
      #ifdef __FASTLED__
        
        FastLED.show();
        FastLED.clear();
      #else
        leds.show();
        leds.fill(0);        
      #endif
    Serial.printf("End Show \n");          
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
char*  getWifiName( )
{    
    char seconds[6];
    int h,m,s;
    long t;
    if(sscanf(__TIME__,"%d:%d:%d",&h,&m,&s)==3)
    {
       t = (((h*60)+m)*60)+s;
       ltoa(t,seconds,16);
       sprintf(wifiName,"%s_%s" , INITIAL_SSID,seconds);
       
       return wifiName;
    }
    return INITIAL_SSID;
}
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
  ConfigureFastLed();
  Serial.println(sessionPresent);
  
  uint16_t packetIdSub = mqttClient.subscribe(StringMqttTokenParam, 2);  
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

void ConfigureFastLed() 
{
  delay(3000); // sanity delay
  Serial.println("Configuring led strip");
  NUM_LEDS = atoi( StringValuesParam);  
  
  #ifdef __FASTLED__
    leds = (CRGB *)calloc( NUM_LEDS, sizeof(CRGB)  );
    //CRGB ledtemp[NUM_LEDS];
    //leds = ledtemp;    
    FastLED.addLeds<CHIPSET, PIN,COLOR_ORDER>(leds,NUM_LEDS).setCorrection( TypicalLEDStrip );
    //FastLED.addLeds<WS2812Controller800Khz, const int(PIN)>(leds, NUM_LEDS); 
    
    FastLED.clear();
    FastLED.show();
    Serial.println("FastLed Configured");

  #else    
    leds = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_RGB + NEO_KHZ800); 
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

///////////////////////////////////////////////////////////////////////
////                 ARDUINO
///////////////////////////////////////////////////////////////////////
