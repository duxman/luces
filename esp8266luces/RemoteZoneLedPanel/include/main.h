bool decodeled( pb_istream_t *stream, const pb_field_t *field, void **arg);
void decodedisplay( byte* payload,unsigned int length );
//void callback(char* topic, byte* payload, unsigned int length);
//void setup_wifi() ;
//void reconnect();

void connectToWifi() ;
void onWifiConnect(const WiFiEventStationModeGotIP& event) ;
void onWifiDisconnect(const WiFiEventStationModeDisconnected& event);
void connectToMqtt() ;
void onMqttConnect(bool sessionPresent);
void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) ;
void onMqttSubscribe(uint16_t packetId, uint8_t qos);
void onMqttUnsubscribe(uint16_t packetId);
void onMqttMessage(char* topic, char* payload, AsyncMqttClientMessageProperties properties, size_t len, size_t index, size_t total);
void ConfigureFastLed() ;