import unittest
from app import app

class MyTestCase(unittest.TestCase):

    # Trying to see if the registration is the correct method for registering a user (POST method required)
    def test_register(self):
        test = app.test_client(self)
        response = test.get('/registration/')
        status = response.status_code
        self.assertEqual(status, 405)

    # Check to see if the correct method is being used for adding products (POST method required)
    def test_add_product(self):
        test = app.test_client(self)
        response = test.get('/add_products/')
        status = response.status_code
        self.assertEqual(status, 405)

    # Check to see if the route to view products exists
    def test_view_products(self):
        test = app.test_client(self)
        response = test.get('/view_products/')
        status = response.status_code
        self.assertEqual(status, 200)

    # Check to see if a product exists by it's id 
    def test_view_product(self, id):
        test = app.test_client(self)
        response = test.get('/view_product/' + id)
        status = response.status_code
        self.assertEqual(status, 200)

    # Check to see if user is not logged in (Authorization Required)
    def test_not_logged_in(self):
        test = app.test_client(self)
        response = test.get('/protected/')
        status = response.status_code
        self.assertEqual(status, 401)

    # Check if user is logged in (has JWT token in header)
    def test_logged_in(self):
        test = app.test_client(self)
        response = test.get('/protected/')
        status = response.status_code
        self.assertEqual(status, 200)

    # Check to see if the correct method is being used for updating a product (PUT method required)
    def test_update(self):
        test = app.test_client(self)
        response = test.get('/edit/1/')
        status = response.status_code
        self.assertEqual(status, 405)


if __name__ == '__main__':
    unittest.main()
