#include <IotWebConf.h>
/*****************************************/
//	 DEFINES
/*****************************************/
#define INITIAL_SSID "DUXMAN_ESP_WLAN"
#define INITIAL_PASS "1234567890"
#define STRING_LEN 128
#define NUMBER_LEN 6
#define CONFIG_VERSION "V0.1'"
/*****************************************/
//	 DEFINES
/*****************************************/

/*****************************************/
//	 VARIABLES
/*****************************************/
DNSServer dnsServer;
WebServer server(80);
IotWebConf webConfig = IotWebConf(INITIAL_SSID, &dnsServer, &server, INITIAL_PASS, CONFIG_VERSION);
boolean needMqttConnect = false;
/*****************************************/
//	 VARIABLES
/*****************************************/

/*****************************************/
//	 VARIABLES CONFIGURACION
/*****************************************/
IotWebConfParameter MqttServerParam;
IotWebConfParameter MqttPortParam;
IotWebConfParameter MqttTokenParam;
IotWebConfSeparator separator; 
IotWebConfParameter PinsParam;
IotWebConfParameter ValuesParam;

char StringMqttServerParam[STRING_LEN];
char  IntMqttPortParam[NUMBER_LEN];
char StringMqttTokenParam[STRING_LEN];
char StringPinsParam[NUMBER_LEN];
char StringValuesParam[NUMBER_LEN];


/*****************************************/
//	 VARIABLES CONFIGURACION
/*****************************************/

/*****************************************/
//	 DECLARATIONS
/*****************************************/
void configSaved();
void configureWifi();
void wifiConnected();
void handleRoot();
/*****************************************/
//	 DECLARATIONS
/*****************************************/