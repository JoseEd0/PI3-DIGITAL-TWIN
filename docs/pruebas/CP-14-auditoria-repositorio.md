# CP-14 · Auditoría de costos, configuración y credenciales del repositorio

> Ejecutada el 10/11/2026 sobre la rama `jose`. **Rótulo: real** (es una revisión del repositorio,
> no depende del hardware). Los comandos quedan abajo para repetirla antes de cada entrega.

## Resultado

| Revisión | Criterio | Resultado |
|---|---|---|
| Credenciales del docente fuera de git | `servidor_iot/.env` y `gateway/gateway.ino` ignorados y nunca commiteados | ✅ Ignorados (`.gitignore`), 0 commits en el historial |
| Credenciales locales del grupo | `deploy/.env` ignorado; solo se versiona `deploy/.env.example` | ✅ |
| Plantillas `.example` | Existe una por cada archivo con credenciales y solo trae marcadores `CAMBIA…` | ✅ `deploy/.env.example`, `servidor_iot/.env.example`, `gateway.ino.example` |
| Secretos en archivos versionados | Ningún token, contraseña o clave con valor real | ✅ Solo aparecen los marcadores de las plantillas. El nombre de la red Wi-Fi del curso está en `gateway.ino.example`, pero el nombre no es secreto; la contraseña es un marcador |
| Secretos en todo el historial | Ninguna línea `WIFI_PASS`, `INFLUX_TOKEN` o `ADMIN_TOKEN` con valor real | ✅ 0 coincidencias |
| Endpoints y umbrales en configuración | Sin direcciones ni umbrales escritos en el código del servicio | ✅ Broker, InfluxDB y grupo en `config/nodos.yaml`, con variables de entorno que los reemplazan. Umbrales en `config/requisitos_ra.yaml` y datos del aula en `config/aula_l419.yaml` |
| Originales del curso y datos pesados | `docs/curso/originales/`, `logs/` y `grabaciones/` fuera de git | ✅ Ignorados. El archivo versionado más grande pesa unos 450 KB (un SVG del modelo) |
| Código del docente sin cambios | `vendor/gemelo_iot_profesor/` igual al ZIP entregado, salvo los `.example` agregados | ✅ Verificado el 10/11 |
| Costos | El hardware lo compró el curso (OC-UTEC-004033-26) y el grupo no compró nada | ✅ La lista está en `docs/curso/texto/lista-de-compra.md`. La planilla no trae precios: el costo queda **pendiente** de que el curso lo publique. El BOM propio anterior (S/ 2808) quedó como histórico |

## Observaciones

- Antes de un `git push`, repetir la sección "Comandos". Las credenciales reales solo existen en la
  laptop.
- Si el Gateway del curso cambia de red o de broker, se edita `gateway.ino`, que es local, y nunca
  `gateway.ino.example` con datos reales.
- Ni el reporte ni Asana copian valores de los `.env`.

## Comandos

Ninguno de estos comandos imprime valores secretos: solo muestran nombres de archivo o conteos.

```bash
git check-ignore -v vendor/gemelo_iot_profesor/servidor_iot/.env vendor/gemelo_iot_profesor/gateway/gateway.ino deploy/.env
git log --all --oneline -- vendor/gemelo_iot_profesor/servidor_iot/.env vendor/gemelo_iot_profesor/gateway/gateway.ino deploy/.env | wc -l
git ls-files -z | xargs -0 grep -l -I -E "(TOKEN|PASSWORD|PASS|API_KEY|secret)\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{8,}"
git log --all -p -G "(WIFI_PASS|INFLUX_TOKEN|ADMIN_TOKEN)\s*=\s*[\"']?[A-Za-z0-9]{8,}" --format="%h %s" | grep -cE "^[0-9a-f]{7} "
```

El tercer comando solo debe listar `gateway.ino.example`, que trae marcadores.
