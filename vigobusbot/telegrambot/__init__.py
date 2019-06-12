
"""TELEGRAMBOT
Todo lo relacionado con el bot de Telegram, la comunicación con Telegram y procesar contenidos entrantes y salientes.
El bot funciona con polling ('start_polling') o webhook ('start_webhook').
En todo caso es necesario llamar a 'register_handlers'.
"""

# Paquete
from .polling import start_polling, stop_polling
from .webhook import start_webhook
from .handlers import register_handlers
