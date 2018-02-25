import unittest

from spine.crypta import crypta, Crypta, IncorrectPassword, InvalidSignature


class CryptaTests(unittest.TestCase):
    def setUp(self):
        self.assertIsInstance(crypta, Crypta, 'cryptography unavailable')

    def testPasswords(self):
        password = 'my-password'

        first = crypta.scramble_password(password)
        second = crypta.scramble_password(password)

        self.assertNotEqual(first, second)  # Пароли должны солиться

        crypta.check_password(password, first)
        crypta.check_password(password, second)

        with self.assertRaises(IncorrectPassword):
            self.assertFalse(crypta.check_password('not-my-password', first))

    def testDigesting(self):
        message = 'some-message'

        signature = crypta.sign(message)

        crypta.verify(message, signature)

        with self.assertRaises(InvalidSignature):
            crypta.verify('another-message', signature)


if __name__ == '__main__':
    unittest.main()
