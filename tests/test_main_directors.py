import unittest
import uuid
from datetime import datetime

from fastapi.testclient import TestClient

from app import Config, create_app
from app.models.movie import Genre, Director


class DirectorsTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_config = Config(is_testing=True)
        cls.client = TestClient(create_app(cls.test_config))
        cls.new_user = {
            "username": "someuser",
            "email_id": "testemail2@gmail.com",
            "password": "password"
        }
        response = cls.client.request(method="get", url="/register", json=cls.new_user)
        cls.new_user.pop("username")
        response = cls.client.request(method="post", url="/auth/token", json=cls.new_user)
        cls.access_token = response.json().get("access_token")

    def tearDown(self) -> None:
        pass

    def test_add_directors(self):
        new_directors = [
            {
                "name":"test Victor Fleming 1",
            },
            {
                "name":"test Victor Fleming 2",
            }
        ]

        response = self.client.request(method="post", url="/directors", headers={"access_token": self.access_token}, json=new_directors)
        self.assertEqual(200, response.status_code)
        return response.json()

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

    def test_edit_director_by_id(self):
        list_of_added_directors = self.test_add_directors()
        uid = list_of_added_directors[0].get("uid")

        response = self.client.request(method="put", url=f"/directors/{uid}", json={"name": "test edit First Name"})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(uid, response)

    def test_delete_director_by_id(self):
        list_of_added_directors = self.test_add_directors()
        for added_director in list_of_added_directors:
            uid = added_director.get("uid")
            response = self.client.request(method="delete", url=f"/directors/{uid}")
            self.assertEqual(200, response.status_code)
            response = response.json()
            self.assertEqual(uid, response.get("uid"))