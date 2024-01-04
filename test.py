import unittest
import warnings
from flask import Flask, jsonify
from api import app


class MyAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

        warnings.simplefilter("ignore", category=DeprecationWarning)

    def tearDown(self):
        pass
    
    def test_login_valid_credentials(self):
        response = self.app.post('/api/auth', json={'username': 'user123', 'password': 'qwerty'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', data)

    def test_login_invalid_credentials(self):
        response = self.app.post('/api/auth', json={'username': 'user12345', 'password': 'qwerty123'})
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertIn('Error', data)
    
    def test_protected_route_with_token(self):
        response = self.app.get('/api/data/protected', headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDM4Mzk4MSwianRpIjoiYWNiODI3ZTEtZTA3ZC00Y2Y2LTg4YjUtNWYwNmJlYzkwOGIzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXIxMjMiLCJuYmYiOjE3MDQzODM5ODEsImNzcmYiOiI5MGNkNjFjMS1jYzVlLTRmMzAtYjU4OC0wM2EzNzE0MjY1ZWQiLCJleHAiOjE3MDQzODQ4ODF9.uyiqnEJ_2mZhoZCmbubizTPuF5EgQTxUNuUIlJSihQc'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('logged_in_as', data)

    def test_protected_route_without_token(self):
        response = self.app.get('/api/data/protected')
        self.assertEqual(response.status_code, 401)

    def test_get_customer(self):
        response = self.app.get('/api/data/customers')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

if __name__ == "__main__":
    unittest.main()
