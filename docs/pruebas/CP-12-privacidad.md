# CP-12 · Privacidad, instalación no invasiva y seguridad eléctrica

> Ejecutada el 11/11/2026 sobre la rama `jose`. Tiene dos partes con rótulo distinto:
>
> - **Privacidad (RNF-02): real (revisión de código).** Se revisaron el firmware del docente
>   (`vendor/gemelo_iot_profesor/`), el `.ino` propio y los servicios del grupo. No depende del
>   hardware.
> - **Instalación y seguridad eléctrica (RNF-01): pendiente.** Se verifica en el aula durante la
>   instalación de S15.

## Privacidad: qué sale de cada nodo sensible

| Revisión | Criterio | Resultado |
|---|---|---|
| Nodo térmico (MLX90640, nodo 5) | La matriz de 32×24 no sale del nodo | ✅ `PaqueteTermico` solo lleva entradas, salidas, ocupación estimada, personas en vista, cruces dudosos, temperatura de fondo y máxima, y bits de anomalía. No hay ningún arreglo de píxeles en el paquete ni en el JSON del Gateway |
| Mapa de depuración del nodo térmico | No se transmite | ✅ `imprimirMapa()` dibuja un mapa ASCII por el Monitor Serie (USB), solo si `DEBUG_MAPA` vale 1. En el código del docente vale **0**. Aun encendido, no pasa por ESP-NOW y es un mapa de 32×24 caracteres que no identifica a nadie |
| Nodo de audio (INMP441, nodo 2) | El audio no sale del nodo ni se guarda | ✅ El nodo lee bloques de 512 muestras a 16 kHz (32 ms) en `bufI2S`, que se sobrescribe en cada lectura. `PaqueteAudio` solo lleva niveles (Leq, Lmax, pico y fondo en dB), la frecuencia dominante, un índice tonal y bits de anomalía. No hay muestras en el paquete |
| Gateway | No reconstruye señales | ✅ Solo traduce cada paquete a su JSON, campo por campo (`gateway.ino.example`) |
| Servicios del grupo | No guardan datos personales | ✅ El log (`events.jsonl` y `campustwin_evento`) y los RA (`campustwin_ra`) guardan magnitudes agregadas: ocupación, eventos de puerta y niveles. Ningún servicio recibe audio ni imagen, y no hay usuarios ni registro de quién consulta el tablero |
| Ocupación | Agregada | ✅ Se reporta como número de personas en el aula, nunca por individuo |
| Copiloto de voz (RF-09) | El audio se procesa en memoria y se descarta | **Pendiente**: el copiloto se construye en S16 y se revisa entonces |

**Conclusión:** RNF-02 se cumple por diseño en todo lo que existe hoy. El riesgo que queda es
operativo: si alguien compila el nodo térmico con `DEBUG_MAPA 1` y deja una laptop conectada por
USB, vería el mapa ASCII. Por eso la instalación debe dejar el valor en 0.

## Instalación no invasiva y seguridad eléctrica (pendiente, S15)

Cuando se instalen los nodos en el L-419 se verifica esta lista:

- [ ] Ninguna caja perfora paredes, techo ni mobiliario: se usa cinta VHB o bridas.
- [ ] Ningún nodo se conecta a 220 V: se alimentan con la 18650 de la caja o con un cargador USB
      de 5 V enchufado a un tomacorriente existente.
- [ ] Ningún cable cruza zonas de paso sin canaleta ni queda colgando a la altura de la cabeza.
- [ ] El nodo de gas (MQ-2) no queda en contacto con material inflamable: el calefactor trabaja a
      unos 0.75 W.
- [ ] La matriz térmica apunta al marco de la puerta, no a los asientos.
- [ ] `DEBUG_MAPA` vale 0 en el nodo térmico instalado.

## Comandos para repetir la revisión

```bash
grep -n "DEBUG_MAPA" vendor/gemelo_iot_profesor/nodo_termico/nodo_termico.ino
sed -n '/struct __attribute__((packed)) PaqueteTermico/,/};/p' vendor/gemelo_iot_profesor/nodo_termico/paquetes.h
sed -n '/struct __attribute__((packed)) PaqueteAudio/,/};/p' vendor/gemelo_iot_profesor/nodo_termico/paquetes.h
grep -n "bufI2S\|const int N\|const int FS" vendor/gemelo_iot_profesor/nodo_audio/nodo_audio.ino
```
