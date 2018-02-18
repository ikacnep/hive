import os

from spine.Game.Utils.Exceptions import HiveError

try:
    import cryptography.exceptions
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import constant_time, hashes, hmac
    from cryptography.hazmat.backends import default_backend

    make_dumb_crypta = False
except:
    print('cryptography is not available, will make dumb crypta')
    make_dumb_crypta = True


class CryptaException(HiveError):
    pass


class IncorrectPassword(CryptaException):
    pass


class InvalidSignature(CryptaException):
    pass


class CryptaIface:
    def scramble_password(self, password):
        pass

    def check_password(self, password, encrypted_password):
        pass

    def sign(self, text):
        pass

    def verify(self, text, signature):
        pass


class NotReallyCrypta(CryptaIface):
    def scramble_password(self, password):
        return password

    def check_password(self, password, encrypted_password):
        return password == encrypted_password

    def sign(self, text):
        return b''

    def verify(self, text, signature):
        return signature == b''


class Crypta:
    def __init__(self, key_path):
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                self.key = key_file.read()
        else:
            self.key = Fernet.generate_key()

            with open(key_path, 'wb') as key_file:
                key_file.write(self.key)

        self.fernet = Fernet(self.key)

    def scramble_password(self, password):
        return self.fernet.encrypt(password.encode('utf-8')).decode('utf-8')

    def check_password(self, password, encrypted_password):
        decrypted_password = self.fernet.decrypt(encrypted_password.encode('utf-8'))

        if not constant_time.bytes_eq(password.encode('utf-8'), decrypted_password):
            raise IncorrectPassword('Provided password is incorrect')

    def sign(self, text):
        hasher = self._get_hasher()
        hasher.update(text.encode('utf-8'))
        return hasher.finalize()

    def verify(self, text, signature):
        hasher = self._get_hasher()
        hasher.update(text.encode('utf-8'))

        try:
            hasher.verify(signature)
        except cryptography.exceptions.InvalidSignature:
            raise InvalidSignature('Invalid signature')

    def _get_hasher(self):
        return hmac.HMAC(self.key, hashes.SHA256(), backend=default_backend())


crypta = NotReallyCrypta()

if not make_dumb_crypta:
    crypta = Crypta('conf/crypta.key')