

#include <Arduino.h>

///////////////////////////////////////////////////////////////////////
////                 DEFINES
///////////////////////////////////////////////////////////////////////
#define NUM_LEDS 96
#define PIN D1
#define COLOR_ORDER RGB



#define MQTT_HOST IPAddress(192, 168, 1, 196)
#define MQTT_PORT 1883
///////////////////////////////////////////////////////////////////////
////                 DEFINES
///////////////////////////////////////////////////////////////////////

#include <ESP8266WiFi.h>
//#include <PubSubClient.h>
#include <Ticker.h>
#include <AsyncMqttClient.h>
#include <pb_decode.h>
#define __FASTLED__ 1
#ifdef __FASTLED__
  #define FASTLED_ESP8266_RAW_PIN_ORDER
  #include <FastLED.h>
  CRGB leds[NUM_LEDS];
#else
  #define NEO_KHZ400 0x0100 ///< 400 KHz data transmission
  #include <Adafruit_NeoPixel.h>
  #ifdef __AVR__
    #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
  #endif
  Adafruit_NeoPixel leds(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ400); 
#endif

#include "protocol.proto.pb.h"
#include "main.h"


///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////
const char* ssid = "BUBU_DUXMAN_WLAN";
const char* password = "2005070400";
display msgdisplay = display_init_zero;        
led msgled = led_init_zero;

AsyncMqttClient mqttClient;
Ticker mqttReconnectTimer;
WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;
Ticker wifiReconnectTimer;
///////////////////////////////////////////////////////////////////////
////                 VARIABLES
///////////////////////////////////////////////////////////////////////





///////////////////////////////////////////////////////////////////////
////                 DECODIFICACION
///////////////////////////////////////////////////////////////////////
void decodedisplay( byte* payload,unsigned int length )
{       
    //Serial.printf("try decoding display \n %d",length);          
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
        leds.clear();    
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
  WiFi.begin(ssid, password);
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
  ConfigureFastLed();
  Serial.print("Session present: ");
  
  Serial.println(sessionPresent);
  
  uint16_t packetIdSub = mqttClient.subscribe("InData", 2);  
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
  Serial.printf("Publish received. len %d  index %d total %d\r\n", (int)len, (int)index, (int)total);
  decodedisplay((byte *)payload,len);     
}
///////////////////////////////////////////////////////////////////////
////                 MQTT
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 FASTLED
///////////////////////////////////////////////////////////////////////

void ConfigureFastLed() 
{
  #ifdef __FASTLED__
    FastLED.addLeds<WS2812Controller800Khz, PIN>(leds, NUM_LEDS); 
    FastLED.clear();
    FastLED.show();
    Serial.println("FastLed Configured");
  #else
    leds.clear();   
    leds.show();        
    Serial.println("Adafruit Configure Configured");
  #endif
}
///////////////////////////////////////////////////////////////////////
////                 FASTLED
///////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////
////                 ARDUINO
///////////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(74880);
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

/*
void setup_wifi() 
{

  delay(10);
  // We start by connecting to a WiFi network  
  Serial.printf("Connecting to %s\n",ssid);
  

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int blink =0;
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(200);
    Serial.print(".");  

  }  
  Serial.printf("WiFi connected IP address:");Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) 
{  
    Serial.printf("Message arrived [%s] = %d\r\n", topic,value++);   
    decodedisplay(payload,length);    
    //Serial.println("Show");
    
}
void reconnect()
 {
  // Loop until we're reconnected
  while (!client.connected()) 
  {
    Serial.print("Attempting MQTT connection...\n");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) 
    {     
      Serial.printf("connected !!");      
      client.subscribe("InData");
    } 
    else 
    {
      Serial.printf("failed, rc= %d\nTry again in 5 seconds",client.state());           
      delay(5000);
    }
  }
}


void setup() 
{
  Serial.begin(74880);
  
  setup_wifi();
  Serial.printf("Create mqtt");  
  client.setBufferSize(4096);
  Serial.printf("set Server");  
  client.setServer(mqtt_server, 1883);
  Serial.printf("set Callback");  
  client.setCallback(callback);    
  FastLED.addLeds<WS2812B, PIN>(leds, NUM_LEDS); 
}

void loop() 
{
 //  pixels.clear();
  if (!client.connected()) 
  {
    reconnect();
  }
  client.loop();  
}
*/