// Circuito lógico da colônia Aurora Siger (SIFSM - Fase 7)
// ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa
// Responsável: Victor

// ----- Pinos -----
const int PINO_CONSUMO = A0;   // potenciômetro = leitura de consumo
const int PINO_CRITICO = 2;    // botão = módulo crítico
const int PINO_BATERIA = A1;   // sensor de luminosidade = nível da bateria
const int PINO_LED = 13;       // LED = atuador de alerta

// ----- Limites (leitura analógica vai de 0 a 1023) -----
const int LIMITE_CONSUMO_ALTO = 700;   // acima disso, consumo alto (~70% do giro)
const int LIMITE_BATERIA_BAIXA = 205;  // abaixo disso, bateria baixa (~20% de 1023)

void setup() {
  pinMode(PINO_CRITICO, INPUT_PULLUP);  // botão ligado ao GND: apertado = LOW
  pinMode(PINO_LED, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // 1) Ler os três sensores e transformar em verdadeiro/falso
  bool consumoAlto = analogRead(PINO_CONSUMO) > LIMITE_CONSUMO_ALTO;
  bool moduloCritico = digitalRead(PINO_CRITICO) == LOW;
  bool bateriaBaixa = analogRead(PINO_BATERIA) < LIMITE_BATERIA_BAIXA;

  // 2) Aplicar a regra booleana
  bool alerta = (consumoAlto && moduloCritico) || bateriaBaixa;

  // 3) Acender ou apagar o LED
  digitalWrite(PINO_LED, alerta ? HIGH : LOW);

  // 4) Mostrar no monitor serial (para o print do relatório)
  Serial.print("consumo_alto=");
  Serial.print(consumoAlto);
  Serial.print(" modulo_critico=");
  Serial.print(moduloCritico);
  Serial.print(" bateria_baixa=");
  Serial.print(bateriaBaixa);
  Serial.print(" -> ALERTA=");
  Serial.println(alerta);

  delay(200);
}
