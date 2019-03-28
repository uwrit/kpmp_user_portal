import unittest
from modules.app.schemas import validate_user, validate_client, validate_org
import uuid


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
        self.assertTrue(res['ok'])

    def test_invalid_user(self):
        data = {
            "_id": "123456",
            "email": "jdoe@@example.com",
            "phone_numbers": ["123-456-7890"],
            "role": "research coordinator"
        }
        res = validate_user(data)
        self.assertFalse(res['ok'])


class TestClientSchema(unittest.TestCase):
    def test_valid_client(self):
        data = {
            "_id": "123456",
            "name": "some-app.kpmp.org",
            "owner": "John",
            "owner_email": "jdoe@email.tld",
            "token": str(uuid.uuid4())
        }
        res = validate_client(data)
        self.assertTrue(res['ok'])

    def test_invalid_client(self):
        data = {
            "_id": "123456",
            "name": "some-app.kpmp.org",
            "token": str(uuid.uuid4())
        }
        res = validate_client(data)
        self.assertFalse(res['ok'])


class TestOrganizationSchema(unittest.TestCase):
    def test_valid_org(self):
        data = {
            "_id": "12345656",
            "name": "Tissue Collection Site #1"
        }
        res = validate_org(data)
        self.assertTrue(res['ok'])

    def test_invalid_org(self):
        data = {
            "_id": "12345656",
            "street": "Tissue Collection Site #1"
        }
        res = validate_org(data)
        self.assertFalse(res['ok'])


if __name__ == "__main__":
    unittest.main()
