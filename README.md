# VigoBus-TelegramBot

Bot de Telegram que permite consultar las paradas y autobuses que se dirigen a las mismas -junto a su tiempo restante de llegada, en tiempo real-, en la red de transporte urbano de la ciudad de Vigo.

## ¿Cómo usarlo? - Historia y Ramas

#### Bot estable

El bot en su versión estable y soportada se encuentra en funcionamiento bajo [@vigobusbot](https://t.me/vigobusbot). Esta versión fue desarrollada y puesta en marcha sobre abril del 2017, permitiendo buscar paradas por ID y guardándolas en listados de paradas favoritas.

Desde entonces se han realizado diversas refactorizaciones, con el fin de mejorar el código, el funcionamiento del bot y dar cabida a nuevas funcionalidades.

#### Bot beta

Una segunda versión se desplegó en abril del 2019 bajo [@vigobustestbot](https://t.me/vigobustestbot), con su código fuente disponible bajo la rama [wip0](https://github.com/David-Lor/VigoBus-TelegramBot/tree/wip0).

Este bot puede utilizarse, pero dado su carácter temporal, podrá dejar de funcionar en cualquier momento, y los datos guardados ser borrados. En la medida de lo posible, se intentarán migrar a la futura versión. 
Como principales mejoras, cuenta con algunos cambios estéticos y la posibilidad de renombrar paradas.

#### Bot alpha (desarrollo actual)

De la rama [development](https://github.com/David-Lor/VigoBus-TelegramBot/tree/development) (y subramas feature) parte el desarrollo de la nueva versión del bot, que principalmente tendrá como mejoras base el funcionamiento asíncrono y una mejor estructura de proyecto.

Así mismo, al contrario que hasta ahora se había planteado (con ligeras adaptaciones), la responsabilidad del backend del bot se limita al máximo a las propias tareas del bot, sirviéndose de dos proyectos adicionales que sirven como API para gestionar información externa:

- [VigoBusAPI](https://github.com/David-Lor/Python_VigoBusAPI) obtiene la información de paradas y autobuses que los usuarios del bot soliciten. Para ello consulta fuentes de datos externas y locales (caché y base de datos).
- [DataManager](https://github.com/David-Lor/Telegram-BusBot-DataManager) gestiona los datos persistentes requeridos por el bot, que por el momento se limitan a las paradas guardadas de los usuarios.

Entre las novedades prácticas a incorporar, se pueden destacar: renombrar paradas, búsqueda de paradas por nombre, por ubicación, y modo inline.

## Microservice structure

![VigoBusBot microservice structure](VigoBusTelegramBot_Structure.svg)

## Requirements

- Python >= 3.6
- [VigoBusAPI](https://github.com/David-Lor/Python_VigoBusAPI)
- [DataManager (Persistence API)](https://github.com/David-Lor/Telegram-BusBot-DataManager)
- requirements listed in [requirements.txt](requirements.txt)
- A Telegram bot created with BotFather
- Docker recommended for deployment

## Changelog

- 0.1.6 - Add logging
- 0.1.5:
    - fix: stop rename crashing
    - add error handler for uncatched global, generic exceptions
    - switch from requests_async to httpx
    - add retries on HTTP requests
    - add user request rate limit (amount per time)
- 0.1.4 - Button on Stop messages to show More/Less buses
- 0.1.3 - Support for setting custom stop names on user saved stops
- 0.1.2 - Support for Saved Stops and working command to list all of them
- 0.1.1 - Inline keyboard markup with callback support for Refreshing Stop messages
- 0.1.0 - Initial async version (basic Get Stop messages)

## Disclaimer

This project is not endorsed by, directly affiliated with, maintained by, sponsored by or in any way officially connected with the company, companies and/or entities responsible for the public transport service of the city of Vigo.

_Este proyecto no cuenta con soporte de, no está afiliado con, mantenido por, patrocinado por ni en cualquier otra manera oficialmente conectado con la compañía, compañías y/o entidades responsables del sistema de transporte público de la ciudad de Vigo._
