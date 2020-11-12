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

void decodeLedLevel( byte* payload,unsigned int length );
void connectToWifi() ;
void onWifiConnect(const WiFiEventStationModeGotIP& event) ;
void onWifiDisconnect(const WiFiEventStationModeDisconnected& event);
void connectToMqtt() ;
void onMqttConnect(bool sessionPresent);
void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) ;
void onMqttSubscribe(uint16_t packetId, uint8_t qos);
void onMqttUnsubscribe(uint16_t packetId);
void onMqttMessage(char* topic, char* payload, AsyncMqttClientMessageProperties properties, size_t len, size_t index, size_t total);
void ConfigureLed() ;
void writeLeds( int level);
void offLeds();