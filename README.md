# VigoBus-TelegramBot

(Este repositorio contiene una versión en desarrollo, actualmente desplegada en [@vigobustestbot](https://t.me/vigobustestbot))
(Posiblemente se comience un desarrollo de otra versión reestructurizada)

Bot para Telegram que permite consultar los autobuses que se dirigen a una parada junto a su tiempo restante en tiempo real, con características adicionales que facilitan el transporte por la ciudad sin necesidad de descargar ninguna aplicación adicional.

Este bot ha sido escrito para ser utilizado con la red de autobuses de la ciudad de Vigo, pero el código puede adaptarse a, teóricamente, cualquier otra ciudad o medio de transporte que funcione de forma similar.

El conjunto del bot se compone de tres partes esenciales, desarrolladas por separado:
- El bot (este repositorio)
- PyBuses, un framework para gestionar los autobuses y paradas
- La API que obtiene la información en tiempo real

## Dependencias

- Se recomienda desplegar con Docker
- Python 3.7
- Librerías Python:
    - PyBuses
    - pyTelegramBotApi
    - requests
    - cryptography

## Despliegue y almacenamiento

Se debe especificar una variable de entorno llamada `DATA_DIR`, donde se guardarán las configuraciones y bases de datos.

Al desplegarse desde Docker (lo recomendable), se define esta variable como un ENV Variable, apuntando a una ubicación dentro del container, que debería estar montada como volumen o bind en el host.

Los ficheros almacenados en esta ubicación son:

- `settings.ini`: configuraciones
- `clients.sqlite`: base de datos con datos de clientes (p.ej. paradas guardadas)
- `vigobus.sqlite`: base de datos usada por PyBuses para guardar paradas
