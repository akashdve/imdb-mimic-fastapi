import unittest

from fastapi.testclient import TestClient

from app import Config, create_app
from app.models.movie import Genre, Director


class DirectorsTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.test_config = Config(is_testing=True)
        self.client = TestClient(create_app(self.test_config))
        self.new_user = {
            "username": "someuser",
            "email_id": "testemail2@gmail.com",
            "password": "password"
        }
        # response = self.client.request(method="get", url="/register", json=self.new_user)
        # self.assertEqual(200, response.status_code)
        #
        # self.new_user.pop("username")
        # response = self.client.request(method="post", url="/auth/token", json=self.new_user)
        # self.assertEqual(200, response.status_code)
        # self.auth_token = json.loads(response.text).get("auth_token")

    def tearDown(self) -> None:
        # response = self.client.request(method="delete", url="/register", json=self.new_user)
        # self.assertEqual(200, response.status_code)
        pass

    def test_add_directors(self):
        directors = [Director(name="Victor Fleming"), Director(name="George Lucas")]
        raise

    def test_list_all_directors(self):
        expected_response = {
            "data": [
                "Victor Fleming",
                "George Lucas",
                "Giovanni Pastrone",
                "Alfred Hitchcock",
                "Merian C. Cooper",
            ],
            "size": 10,
            "page": 1
        }
        response = self.client.request(method="get", url="/directors")
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response.get("data"), list)
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_directors_pagination(self):
        expected_response = {
            "data": [
                "Victor Fleming",
                "George Lucas",
                "Giovanni Pastrone",
                "Alfred Hitchcock",
                "Merian C. Cooper",
            ],
            "size": 10,
            "page": 1
        }

        size = 20
        response = self.client.request(method="get", url="/directors", params={"size": str(size)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(1, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

        size=20; page=2
        response = self.client.request(method="get", url="/directors", params={"size": str(size), "page": str(page)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(page, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_directors_by_keyword(self):
        keyword = "music"
        response = self.client.request(method="get", url="/directors", params={"keyword": keyword})

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        if len(response.get("data")) > 0:
            self.assertIn(keyword, response.get("data")[0].get("name"))
