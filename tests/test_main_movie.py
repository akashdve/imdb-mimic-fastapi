import json
import unittest

from fastapi.testclient import TestClient

from app import create_app, Config


class MoviesTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.added_movies_objs = []
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

        cls.access_token = json.loads(response.text).get("access_token")

    def tearDown(self) -> None:
        pass

    def test_add_movies(self):
        new_movies = [{
            "popularity": 83.0,
            "director": "Victor Fleming",
            "genre": [
              "Adventure",
              " Family",
              " Fantasy",
              " Musical"
            ],
            "imdb_score": 8.3,
            "name": "The Wizard of Oz"
        }]
        response = self.client.request(method="post", url="/movies", headers={"access_token": self.access_token}, json=new_movies)
        self.assertEqual(200, response.status_code)
        response = response.json()
        return response

    def test_list_all_movies(self):
        expected_response = {
            "data": [{
                "popularity": 83.0,
                "director": "Victor Fleming",
                "genre": [
                  "Adventure",
                  " Family",
                  " Fantasy",
                  " Musical"
                ],
                "imdb_score": 8.3,
                "name": "The Wizard of Oz"
            }],
            "size": 10,
            "page": 1
        }
        response = self.client.request(method="get", url="/movies")
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response.get("data"), list)
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_movies_pagination(self):
        expected_response = {
            "data": [],
            "size": 10,
            "page": 1
        }

        size = 20
        response = self.client.request(method="get", url="/movies", params={"size": str(size)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(1, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

        size=20; page=2
        response = self.client.request(method="get", url="/movies", params={"size": str(size), "page": str(page)})
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        self.assertGreaterEqual(size, len(response.get("data")))
        self.assertIsInstance(response.get("data"), list)
        self.assertEqual(page, response.get("page"))
        self.assertListEqual(list(expected_response.keys()), list(response.keys()))

    def test_list_all_movies_by_keyword(self):
        keyword = "star war"
        response = self.client.request(method="get", url="/movies", params={"keyword": keyword})

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertIsInstance(response, dict)
        if len(response.get("data")) > 0:
            self.assertIn(keyword, response.get("data")[0].get("name"))

    def test_edit_movie_by_id(self):
        list_of_added_movies = self.test_add_movies()
        movie_id = list_of_added_movies[0].get("uid")
        updated_movie = {
            "popularity": 83.0,
            "director": "test edit John Wick",
            "genre": [
              "Adventure",
              " Family",
              " Fantasy",
              " Musical"
            ],
            "imdb_score": 8.3,
            "name": "The Wizard of Oz"
        }
        response = self.client.request(method="put", url=f"/movies/{movie_id}", headers={"access_token": self.access_token},
                                       json=updated_movie)
        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(movie_id, response)

    def test_delete_movie_by_id(self):
        list_of_added_movies = self.test_add_movies()
        for added_genre in list_of_added_movies:
            movie_id = added_genre.get("uid")
            response = self.client.request(method="delete", url=f"/movies/{movie_id}",
                                           headers={"access_token": self.access_token})
            self.assertEqual(200, response.status_code)
