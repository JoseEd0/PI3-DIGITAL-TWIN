// Nodo gas/humo (MQ-2) -> ESP-NOW -> Gateway ESP32 (v4 MQTT del docente o v5 con red propia)
// Índice Rs/R0 del aire del salón L-419 (nodo 3 de la arquitectura oficial del curso).
//
// Programa propio del Grupo 1 (PI3 2026-2, Sección 8). Sigue la estructura de los nodos del
// docente (nodo_co2.ino, nodo_luz.ino y nodo_magnetico.ino de vendor/gemelo_iot_profesor/).
// paquetes.h es del DOCENTE (vendor/gemelo_iot_profesor/) y espnow_nodo.h es su versión v2, la de
// los nodos instalados en el aula (vendor/gateway_ap_l419/, otro grupo del curso, 20/11/2026);
// los dos se copiaron SIN CAMBIOS: Arduino necesita los .h junto al .ino.
// Los dos Gateways decodifican PaqueteGas: el v4 publica en utec/gemelo/<grupo>/nodo3/gas y el v5
// (gateway_ap.ino) lo guarda y lo sirve por HTTP; el puente del grupo lo lleva al mismo tópico.
//
// Estado: compila con arduino-cli (esp32:esp32:esp32). SIN PROBAR en hardware: los valores
// eléctricos marcados como SUPUESTO se confirman al conectar el módulo (ver firmware/README.md).
//
// Conexión (supuesta para el módulo MQ-2 de 4 pines: VCC, GND, DO, AO):
//   VCC -> VIN del DevKit (5 V)        GND -> GND
//   AO  -> divisor 10 k / 15 k -> GPIO 34
//   DO  -> divisor 22 k / 47 k -> GPIO 27
#include <Arduino.h>
#include "paquetes.h"
#include "espnow_nodo.h"

// ================= RED =================
uint8_t MAC_GATEWAY[6] = {0x58, 0x2A, 0xBD, 0x72, 0x03, 0xDC}; // MAC STA del ESP32 v4 (la de los nodos del docente)
const char*   SSID_ROUTER   = "GEMELO-L419";   // red que crea gateway_ap.ino (solo para hallar el canal)
const uint8_t CANAL_DEFECTO = 1;
const uint8_t NODO_ID       = 3;

// ================= PINES =================
// AO debe ir a un pin de ADC1 (GPIO 32 a 39): los de ADC2 no funcionan con la radio activa.
#define PIN_AO 34
#define PIN_DO 27
// El comparador LM393 del módulo baja DO cuando el gas supera el umbral del potenciómetro
// (es cuando se enciende el LED). SUPUESTO: confirmarlo con el módulo real.
const bool DO_ACTIVO_EN_BAJO = true;

// ================= ELÉCTRICO (SUPUESTOS hasta revisar el módulo) =================
// El calefactor necesita 5 V, así que AO y DO llegan hasta 5 V y el ESP32 solo tolera 3.3 V:
// los dos pasan por un divisor.
// - AO: 10 k arriba y 15 k abajo dejan 5 V en 3.0 V, dentro del rango del ADC con atenuación de
//   11 dB (~0 a 3.1 V). AO sale de la RL del módulo (≤ 1 k), así que el divisor casi no la carga.
// - DO: la salida del LM393 tiene su propio pull-up a 5 V (~10 k en los FC-22) que queda en serie
//   con el divisor; con 22 k / 47 k el "1" llega a ~3.0 V, sobre el umbral del ESP32 (~2.5 V).
//   Solo se lee como digital, por eso no hay constantes para ese divisor.
const float VC_MODULO_V       = 5.0;    // alimentación del módulo: calefactor y su divisor interno
const float R_DIV_ARRIBA_KOHM = 10.0;   // divisor de AO
const float R_DIV_ABAJO_KOHM  = 15.0;
const float FACTOR_DIVISOR    = (R_DIV_ARRIBA_KOHM + R_DIV_ABAJO_KOHM) / R_DIV_ABAJO_KOHM;
// Resistencia de carga del módulo (la SMD "102" = 1 k en los módulos FC-22). Solo cambia Rs en kΩ,
// no el índice: en Rs/R0 = [(Vc - V) / V] / [(Vc - V0) / V0] la RL se cancela (y también la
// pequeña carga del divisor, que es la misma en la calibración y en la medición).
const float RL_MODULO_KOHM    = 1.0;

// ================= ADC =================
const int   MUESTRAS_ADC      = 16;     // cada lectura promedia 16 conversiones (el ADC del ESP32 es ruidoso)
const int   ADC_PIN_MAX_MV    = 3100;   // tope de la atenuación de 11 dB: por encima satura
const float V_AO_MIN_VALIDO   = 0.10;   // V del módulo: por debajo, AO desconectado o calefactor apagado (Rs -> infinito)

// ================= CALENTAMIENTO Y CALIBRACIÓN DE R0 =================
// La hoja de datos (Hanwei) pide 24 h de precalentamiento la primera vez; en el uso diario el
// módulo da lecturas estables en 1-2 min. Se usan 60 s, igual que el simulador del grupo
// (GAS_CALENTAMIENTO_S en demo/servidor/gemelo/simulador.py), y R0 se calibra en los últimos 10 s.
// Este R0 es la Rs en el aire limpio del aula (por eso rs_r0 = 1 en aire limpio, como define
// paquetes.h). No es el R0 de la hoja de datos, que se define a 1000 ppm de H2 y está ~9.8 veces
// por debajo de la Rs en aire limpio.
const unsigned long CALENTAMIENTO_MS = 60000;   // calentando = 1 mientras dure (incluye la calibración)
const unsigned long CALIBRACION_MS   = 10000;   // ventana final del calentamiento donde se promedia Rs
const float CALIB_VARIACION_MAX = 0.10;  // (máx - mín) / media de Rs: si el aire no está estable se repite
const int   CALIB_MUESTRAS_MIN  = 5;
// R0 fijo en kΩ, medido una vez en aire limpio y anotado aquí. 0 = calibrar en cada arranque.
// Calibrar al arrancar falla si el nodo se enciende con humo en el aire: por eso, cuando haya un
// valor medido en el aula, conviene fijarlo.
const float R0_FIJO_KOHM = 0.0;

// ================= UMBRALES =================
// GAS_DETECTADO con el mismo umbral que el simulador (GAS_DETECTADO_RS_R0 = 0.70). RA-05 usa además
// alerta 0.75 y crítico 0.50 (config/requisitos_ra.yaml): esos los evalúa el servicio, no el nodo.
const float GAS_DETECTADO_RS_R0 = 0.70;  // por debajo: gas o humo
const float HIST_RS_R0          = 0.10;  // la alarma se apaga al volver sobre 0.80
const int   CONFIRMACIONES      = 3;     // lecturas seguidas para cambiar de estado (3 s)
const int   FALLOS_PARA_ALARMA  = 5;

// ================= PERIODOS =================
const unsigned long MUESTREO_MS      = 1000;   // una lectura por segundo
const unsigned long PERIODO_MS       = 5000;   // un envío cada 5 s (config/nodos.yaml, nodo 3)
const unsigned long MIN_ENTRE_ENVIOS = 200;    // envío rápido si aparece o desaparece el gas

// ================= ESTADO =================
// Fases del nodo. Se avanza con flags y no comparando millis() con una constante, para que el
// desborde de millis() (cada ~49 días) no devuelva el nodo al calentamiento.
enum Fase : uint8_t { FASE_CALENTANDO, FASE_CALIBRANDO, FASE_MIDIENDO };
Fase  fase = FASE_CALENTANDO;
float r0Kohm = R0_FIJO_KOHM;
double sumaCalib = 0;
float  minCalib = 1e9, maxCalib = 0;
int    nCalib = 0;

float vAo = NAN, rsKohm = NAN, rsR0 = NAN;
bool  doAlarma = false;
bool  gasDetectado = false;
int   contCand = 0;
int   fallosSeguidos = 0;
bool  fallo = false;
bool  hayEvento = false;
unsigned long tArranque = 0, tMuestra = 0, tUltEnvio = 0, tInicioCalib = 0;

// ================= LECTURA =================
// Voltaje de AO en la escala del módulo (antes del divisor). analogReadMilliVolts usa la
// calibración de fábrica del ADC (eFuse), más lineal que convertir analogRead a mano.
float leerVoltajeModulo(bool &saturado) {
  long sumaMv = 0;
  for (int i = 0; i < MUESTRAS_ADC; i++) sumaMv += analogReadMilliVolts(PIN_AO);
  float mvPin = (float)sumaMv / MUESTRAS_ADC;
  saturado = mvPin >= ADC_PIN_MAX_MV;
  return mvPin / 1000.0f * FACTOR_DIVISOR;
}

// Rs a partir del divisor interno del módulo: V = Vc * RL / (Rs + RL).
float resistenciaSensor(float v) {
  if (v < V_AO_MIN_VALIDO || v >= VC_MODULO_V) return NAN;
  return RL_MODULO_KOHM * (VC_MODULO_V - v) / v;
}

bool leerDo() {
  return (digitalRead(PIN_DO) == LOW) == DO_ACTIVO_EN_BAJO;
}

bool calentando() {
  return fase != FASE_MIDIENDO;
}

// ================= CALIBRACIÓN =================
void reiniciarCalibracion(unsigned long ahora) {
  sumaCalib = 0; nCalib = 0;
  minCalib = 1e9; maxCalib = 0;
  tInicioCalib = ahora;
}

// Promedia Rs durante CALIBRACION_MS. Devuelve true cuando R0 queda fijado. Si el aire no estuvo
// estable o no hubo lecturas válidas, vuelve a empezar: es preferible seguir "calentando" a
// fijar un R0 falso (con humo en el aire, R0 saldría bajo y el índice no bajaría nunca de 1).
bool calibrar(float rs, unsigned long ahora) {
  if (!isnan(rs)) {
    sumaCalib += rs; nCalib++;
    minCalib = fminf(minCalib, rs);
    maxCalib = fmaxf(maxCalib, rs);
  }
  if (ahora - tInicioCalib < CALIBRACION_MS) return false;

  float media = nCalib > 0 ? sumaCalib / nCalib : 0;
  if (nCalib >= CALIB_MUESTRAS_MIN && (maxCalib - minCalib) <= CALIB_VARIACION_MAX * media) {
    r0Kohm = media;
    Serial.printf("# R0 calibrado: %.2f kOhm (%d lecturas)\n", r0Kohm, nCalib);
    return true;
  }
  Serial.printf("# Calibracion repetida: %d lecturas, variacion %.0f %%\n",
                nCalib, media > 0 ? 100.0f * (maxCalib - minCalib) / media : 0.0f);
  reiniciarCalibracion(ahora);
  return false;
}

// Con R0 fijo se calienta los 60 s completos; si no, los últimos 10 s se usan para calibrar.
void avanzarFase(float rs, unsigned long ahora) {
  bool conR0Fijo = R0_FIJO_KOHM > 0;
  unsigned long finCalentamiento = conR0Fijo ? CALENTAMIENTO_MS : CALENTAMIENTO_MS - CALIBRACION_MS;
  if (fase == FASE_CALENTANDO && ahora - tArranque >= finCalentamiento) {
    fase = conR0Fijo ? FASE_MIDIENDO : FASE_CALIBRANDO;
    reiniciarCalibracion(ahora);
    if (conR0Fijo) hayEvento = true;
    return;
  }
  if (fase == FASE_CALIBRANDO && calibrar(rs, ahora)) {
    fase = FASE_MIDIENDO;
    hayEvento = true;
  }
}

// ================= ANOMALÍAS =================
// Histéresis + confirmaciones, como el nivel del nodo CO2: un soplo o un pico de ruido del ADC
// no dispara la alarma, y la alarma no parpadea alrededor del umbral.
void evaluarGas(float indice) {
  bool cand = gasDetectado ? indice < GAS_DETECTADO_RS_R0 + HIST_RS_R0
                           : indice < GAS_DETECTADO_RS_R0;
  if (cand == gasDetectado) { contCand = 0; return; }
  if (++contCand < CONFIRMACIONES) return;
  gasDetectado = cand;
  contCand = 0;
  hayEvento = true;
}

void actualizarFallo(bool lecturaValida) {
  fallosSeguidos = lecturaValida ? 0 : fallosSeguidos + 1;
  bool antes = fallo;
  fallo = fallosSeguidos >= FALLOS_PARA_ALARMA;
  if (fallo != antes) hayEvento = true;
}

// ================= MUESTRA =================
void muestrear(unsigned long ahora) {
  bool saturado = false;
  vAo    = leerVoltajeModulo(saturado);
  rsKohm = saturado ? NAN : resistenciaSensor(vAo);
  actualizarFallo(!isnan(rsKohm));

  avanzarFase(rsKohm, ahora);

  bool preparando = calentando();
  // Con el calefactor frío Rs es baja y el comparador marca gas: DO no se informa hasta terminar.
  bool doAhora = !preparando && leerDo();
  if (doAhora != doAlarma) { doAlarma = doAhora; hayEvento = true; }

  rsR0 = (!preparando && !isnan(rsKohm)) ? rsKohm / r0Kohm : NAN;
  if (!isnan(rsR0)) evaluarGas(rsR0);
}

// ================= ENVÍO =================
void enviar(unsigned long ahora) {
  uint8_t an = 0;
  if (fallo)        an |= GAS_BIT_FALLO;
  if (gasDetectado) an |= GAS_BIT_GAS_DETECTADO;

  PaqueteGas p = {};
  llenarCabecera(p.h, TIPO_GAS, NODO_ID);
  p.v_ao       = vAo;
  p.rs_r0      = rsR0;               // NAN mientras calienta o si la lectura no es válida
  p.do_alarma  = doAlarma ? 1 : 0;
  p.calentando = calentando() ? 1 : 0;
  p.anomalias  = an;
  espnowEnviar(&p, sizeof(p));

  // Depuración por USB (envio_ok corresponde al envío anterior)
  Serial.printf("%lu,%.3f,%.2f,%.2f,%.3f,%u,%u,0x%02X,%d\n",
                ahora, vAo, rsKohm, r0Kohm, rsR0, p.do_alarma, p.calentando, an,
                g_ultimoOk ? 1 : 0);

  hayEvento = false;
  tUltEnvio = ahora;
}

// ================= SETUP / LOOP =================
void setup() {
  Serial.begin(115200);
  delay(500);
  analogReadResolution(12);              // 0-4095
  analogSetAttenuation(ADC_11db);        // rango de entrada ~0-3.1 V
  pinMode(PIN_DO, INPUT);                // el módulo ya trae resistencia de pull-up hacia su VCC

  if (!espnowIniciar(MAC_GATEWAY, SSID_ROUTER, CANAL_DEFECTO))
    Serial.println("# ERROR: no se pudo iniciar ESP-NOW");
  Serial.printf("# Nodo gas (MQ-2) id=%d  MAC=%s  canal=%d\n",
                NODO_ID, WiFi.macAddress().c_str(), g_canal);
  if (R0_FIJO_KOHM > 0) Serial.printf("# R0 fijo: %.2f kOhm\n", R0_FIJO_KOHM);
  Serial.printf("# Primeros %lu s: calentamiento%s, no se evaluan anomalias de gas.\n",
                CALENTAMIENTO_MS / 1000, R0_FIJO_KOHM > 0 ? "" : " y calibracion de R0 en aire limpio");
  Serial.println("ms,v_ao,rs_kohm,r0_kohm,rs_r0,do_alarma,calentando,anomalias,envio_ok");

  tArranque = tMuestra = tUltEnvio = millis();
  nodoVigilanteIniciar();   // reinicio automático si el loop se traba > 5 s (espnow_nodo.h v2)
}

void loop() {
  unsigned long ahora = millis();
  if (ahora - tMuestra >= MUESTREO_MS) {
    tMuestra = ahora;
    muestrear(ahora);
  }

  bool porPeriodo = ahora - tUltEnvio >= PERIODO_MS;
  bool porEvento  = hayEvento && ahora - tUltEnvio >= MIN_ENTRE_ENVIOS;
  if (porPeriodo || porEvento) enviar(ahora);
}
