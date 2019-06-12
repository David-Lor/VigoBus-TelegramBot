
""" CLIENTDATA.ENCODING
Funciones que sirven para codificar y decodificar la información que se guarda en la base de datos,
  en caso de que la opción de codificación esté habilitada.
El objetivo es no guardar los datos de clientes en plano en la base de datos.
Realmente no se aporta una encriptación efectiva, sino más bien ofuscación.
Los datos que se guardan no son extremadamente sensibles, siendo los siguientes junto a cómo se alteran:
- userIDs de Telegram: hash SHA256 con SALT configurable. Orden de aplicación diferente según paridad del UserID.
- IDs de paradas: no alterados (raw int)
- nombres de paradas guardadas: Fernet con key basada en el UserID hasheado
"""

# Librerías nativas
import base64
from hashlib import sha256

# Librerías instaladas
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import Hash, SHA256
from cryptography.hazmat.backends import default_backend

# Proyecto
from vigobusbot.settings import config


__all__ = ("hash_userid", "hash_userid_to_key", "encrypt", "decrypt")
__SALT = config.ClientsDB.Salt.encode()


def hash_userid(userid: int) -> str:
    """Crea un hash con el ID de usuario proporcionado para guardar en la base de datos.
    :param userid: ID de usuario a hashear
    :type userid: int
    :return: ID de usuario hasheado
    :rtype: str
    """
    sha = sha256()
    uid = str(userid).encode()
    if userid % 2 == 0:
        sha.update(__SALT)
        sha.update(uid)
    else:
        sha.update(uid)
        sha.update(__SALT)
    return sha.hexdigest()


def hash_userid_to_key(userid: int) -> bytes:
    """Crea una key para Fernet, basada en el UserID proporcionado.
    Los datos que codificará esta key pueden ser nombres personalizados de paradas guardadas.
    :param userid: ID de usuario de Telegram
    :type userid: int
    :return: key en bytes
    :rtype: bytes
    """
    sha = Hash(SHA256(), backend=default_backend())
    uid = str(userid).encode()
    if userid % 2 == 0:
        sha.update(uid)
        sha.update(__SALT)
    else:
        sha.update(__SALT)
        sha.update(uid)
    return base64.urlsafe_b64encode(sha.finalize())


def encrypt(key: bytes, text: str) -> str:
    """Codifica el texto proporcionado con la key proporcionada.
    La key debe generarse con el método 'hash_userid_to_key', y el contenido debe estar relacionado con un user concreto.
    El mensaje codificado que devuelve puede guardarse en la base de datos de clientes.
    :param key: key generada por el método 'hash_userid_to_key'
    :param text: mensaje, texto o contenido a codificar
    :type key: bytes
    :type text: str
    :return: text codificado como string
    :rtype: str
    """
    fernet = Fernet(key)
    return fernet.encrypt(bytes(text.encode())).decode()


def decrypt(key: bytes, encrypted_text: str) -> str:
    """Decodifica el texto proporcionado con la key proporcionada.
    La key debe generarse con el 'método hash_userid_to_key', y el contenido debe estar relacionado con un user concreto.
    El mensaje codificado que se proporciona se obtiene presumiblemente de la base de datos de clientes.
    :param key: key generada por el método 'hash_userid_to_key'
    :param encrypted_text: mensaje codificado previamente por el método 'encrypt'
    :type key: bytes
    :type encrypted_text: str
    :return: mensaje plano (original)
    :rtype: str
    """
    fernet = Fernet(key)
    return fernet.decrypt(bytes(encrypted_text.encode())).decode()
