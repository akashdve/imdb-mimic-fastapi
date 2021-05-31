import unittest

from fastapi.testclient import TestClient

from app import Config, create_app
from app.models.movie import Genre


class GenresTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.added_genres_objs = []
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

    def test_add_genres(self):
        new_genres = [{
            "name": "New Genre 1"
        }]
        response = self.client.request(method="post", url="/genres", headers={"access-token": self.access_token},
                                       json=new_genres)
        self.assertEqual(200, response.status_code)
        return response.json()

    def test_list_all_genres(self):
        expected_response = {
            "data": [
                "Adventure",
                "Family",
                "Fantasy",
                "Musical"
            ],
            "size": 10,
            "page": 1
        }
        response = self.client.request(method="get", url="/genres")
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response.get("data"), list)
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_genres_pagination(self):
        expected_response = {
            "data": [
                "Adventure",
                "Family",
                "Fantasy",
                "Musical"
            ],
            "size": 10,
            "page": 1
        }

        size = 20
        response = self.client.request(method="get", url="/genres", params={"size": str(size)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(1, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

        size=20; page=2
        response = self.client.request(method="get", url="/genres", params={"size": str(size), "page": str(page)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(page, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_genres_by_keyword(self):
        keyword = "music"
        response = self.client.request(method="get", url="/genres", params={"keyword": keyword})

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        if len(response.get("data")) > 0:
            self.assertIn(keyword, response.get("data")[0].get("name"))

    def test_edit_genre_by_id(self):
        list_of_added_genres = self.test_add_genres()
        genre_id = list_of_added_genres[0].get("uid")
        updated_genre = {
            "name": "New Genre 1 Edited"
        }
        response = self.client.request(method="put", url=f"/genres/{genre_id}", headers={"access-token": self.access_token},
                                       json=updated_genre)
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(genre_id, response)

    def test_delete_genre_by_id(self):
        list_of_added_genres = self.test_add_genres()
        for added_genre in list_of_added_genres:
            genre_id = added_genre.get("uid")
            response = self.client.request(method="delete", url=f"/genres/{genre_id}", headers={"access-token": self.access_token})
            self.assertEqual(200, response.status_code)
