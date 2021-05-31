import json
import unittest

from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app import create_app, Config


class AuthUserRegisterTestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.test_config = Config(is_testing=True)
        self.client = TestClient(create_app(self.test_config))

    def test_registered_user(self):
        new_user = {
            "username": "testuser1",
            "email_id": "testemail1@gmail.com",
            "password": "password",
            "firstname": "first",
            "lastname": "second",
            "is_active": True
        }

        ## Register User
        response = self.client.request(method="get", url="/register", json=new_user)
        self.assertEqual(200, response.status_code)
        ## Register Same User Again
        response = self.client.request(method="get", url="/register", json=new_user)
        self.assertEqual(400, response.status_code)


    def test_authenticated_user(self):
        new_user = {
            "username": "testuser",
            "email_id": "testemail@gmail.com",
            "password": "password",
            "firstname": "first",
            "lastname": "second",
            "is_active": True
        }

        response = self.client.request(method="get", url="/register", json=new_user, headers={"auth_token": ""})
        self.assertEqual(400, response.status_code)

    def test_unregistered_user(self):
        new_user = {
            "username": "testuser",
            "email_id": "testemail@gmail.com",
            "password": "password",
            "firstname": "first",
            "lastname": "second",
            "is_active": True,
            "is_anonymous": None,
            "is_authenticated": None,
        }

        response = self.client.request(method="get", url="/register", json=new_user)
        self.assertEqual(200, response.status_code)

        actual_response = response.json()
        actual_response.pop("id")
        new_user.pop("password")
        expected_response = new_user
        self.assertDictEqual(actual_response, expected_response)

    def test_empty_or_no_username(self):
        new_user = {
            "username": "",
            "email_id": "testemail@gmail.com",
            "password": "password",
            "firstname": "first",
            "lastname": "second",
            "is_active": True
        }

        response = self.client.request(method="get", url="/register", json=new_user)
        self.assertEqual(422, response.status_code)

        new_user.pop("username")
        response = self.client.request(method="get", url="/register", json=new_user)
        self.assertEqual(422, response.status_code)


class AuthTokenTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.test_config = Config(is_testing=True)
        self.client = TestClient(create_app(self.test_config))
        self.new_user = {
            "username": "someuser",
            "email_id": "testemail2@gmail.com",
            "password": "password"
        }
        response = self.client.request(method="get", url="/register", json=self.new_user)
        # self.assertEqual(200, response.status_code)

    def tearDown(self) -> None:
        # response = self.client.request(method="delete", url="/register", json=self.new_user)
        # self.assertEqual(200, response.status_code)
        pass

    def test_valid_login(self):
        old_user = {
            "email_id": "testemail2@gmail.com",
            "password": "password"
        }
        response = self.client.request(method="post", url="/auth/token", json=old_user)
        self.assertEqual(200, response.status_code)

        expected_response = {
            "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "token_type": "bearer"
        }
        self.assertListEqual(list(response.json().keys()), list(expected_response.keys()) )
        self.assertIsInstance(json.loads(response.text).get("access_token"), str)
        self.assertIsInstance(json.loads(response.text).get("token_type"), str)

    def test_invalid_email(self):
        old_user = {
            "email_id": "testemail2@yahoo.com",
            "password": "password"
        }
        response = self.client.request(method="post", url="/auth/token", json=old_user)
        self.assertEqual(404, response.status_code)

    def test_invalid_password(self):
        old_user = {
            "email_id": "testemail2@gmail.com",
            "password": "passwordeee"
        }
        response = self.client.request(method="post", url="/auth/token", json=old_user)
        self.assertEqual(401, response.status_code)
