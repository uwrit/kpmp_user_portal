import unittest
from modules.app.schemas import validate_user


class TestUserSchema(unittest.TestCase):
    def test_valid_user(self):
        data = {
            "_id": "123456",
            "first_name": "John",
            "last_name": "Doe",
            "email": "jdoe@example.com",
            "phone_numbers": ["123-456-7890"],
            "role": "research coordinator"
        }
        res = validate_user(data)
        self.assertEqual(res['ok'], True)

    def test_invalid_user(self):
        data = {
            "_id": "123456",
            "email": "jdoe@@example.com",
            "phone_numbers": ["123-456-7890"],
            "role": "research coordinator"
        }
        res = validate_user(data)
        self.assertEqual(res['ok'], False)


if __name__ == "__main__":
    unittest.main()
