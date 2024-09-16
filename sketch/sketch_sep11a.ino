#include <WiFi.h>
#include <WiFiUdp.h>
#include <Mouse.h>

// Configurações da rede WiFi
const char* ssid = "Cristian";
const char* password = "lohran123";

// Configurações do servidor UDP
WiFiUDP Udp;
unsigned int localUdpPort = 5005;  // Porta local para escutar
char incomingPacket[255];  // Buffer para os dados recebidos

void setup() {
  // Conecta à rede WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }

  // Inicializa o servidor UDP
  Udp.begin(localUdpPort);

  // Inicializa o Mouse
  Mouse.begin();
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // Recebe o pacote UDP
    int len = Udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = 0;
    }

    // Parseia as coordenadas recebidas
    int x, y;
    sscanf(incomingPacket, "%d,%d", &x, &y);

    // Move o mouse para as coordenadas recebidas
    Mouse.move(x, y);
  }
}
