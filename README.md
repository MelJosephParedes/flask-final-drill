## Hello, this project is using Flask framework building for REST API CRUD.

## The project is composed of API for Create, Read, Update and Delete, test for test case and templates for the search functionality

## Installation Instructions:
    - Clone the project to your computer
    - Inside the project folder create a virtual environment
        python -m virtualenv venv
    - Activate the virtual environment
        Windows:
            venv\Scripts\activate
        Linux:
            source bin/activate

    - Install the modules
        pip install Flask Flask-MySQLdb Flask-JWT-Extended

## Usage:
We are using Postman for this project but if you want to use alternatives you can use curl, etc...

    -Install Postman and open, click lightweight api client

## Example usage:

# Authentication

Before making request to protected endpoints, you need to obtain an access token by sending a POST
request to '/api/auth'

    '/api/auth' (POST)
    Request:

    Method: POST
    Request Body: 
    {
        "username": "your_username",
        "password": "your_password
    }

    Response:
    Success(200 OK):
    {
        "access_token": "your_access_token"
    }

    Error (Unauthorized 401):
    {
        "Error": "Invalid Credentials"
    }

    Error (Internal Server Error 500):
    {
        "Error": "Internal Server Error"
    }

# You can do it with the other endpoints just like the example that I mentioned.






