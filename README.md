# ECE 461L Project Info
Software Engineering Team Project
# Project Overview

This project is a web application for managing users, projects, and shared resources. The application uses React for the front end, Flask for the back end, and MongoDB for data storage. The main functionality includes user authentication, project management, resource availability, resource checkout/check-in, and automated testing.

Live app: Heroku Url will be here soon

## 1. Technology Stack

Front End: React.js

Back End: Python / Flask

Database: MongoDB

Testing: Pytest

Version Control: Git / GitHub

Deployment: Heroku

## 2. Application Components

**User Management:**
Handles user accounts and authentication.
Main functions:

-Create a user account

-Log in and log out

-Securely store user credentials

-Authenticate users

**Project Management**
Handles project creation and membership.
Main functions:

-Create a new project

-Access an existing project

-Join a project using a project ID

-Store project name, description, and project ID

-Track users associated with a project

**Resource Management**
Handles the application's shared resources.
Main functions:

-View resource capacity

-View current resource availability

-Request available resource units

-Check out resource units

-Reject requests exceeding available capacity

-Check resource units back in

-Prevent users from checking in more units than their project has checked out

-Update resource availability after checkout/check-in

**Database**
MongoDB stores persistent application data.
Main data collections include:

-Users

-Projects

-Resources

The database is accessed through the Flask API.

**Back-end API**
The Flask backend provides the API between the React front end and MongoDB.
Main functions:

-Handle user authentication

-Manage users

-Create and access projects

-Manage project membership

-Check resource availability

-Process resource check-in and checkout

**Front-end**
The React front end provides the user interface for the application.
Main screens/functionality include:

-User sign-in and account creation

-Project creation and access

-Project resource management

-Resource availability

-Resource check-in and checkout

## 3. Testing
Pytest is used for automated testing.
Testing includes:

-API endpoints

-Database logic

-Check-in and checkout functionality

The tests run automatically on every push and pull request (GitHub Actions).

## 4. Running Locally

```bash
pip install -r requirements.txt
npm install

cd server
USE_MOCK_DB=1 python app.py   # in-memory database, no MongoDB needed
```

In a second terminal, from the repo root:

```bash
npm run dev
```

Then open http://localhost:3000.

To use a real database instead, put `MONGODB_SERVER=<connection string>` and `FLASK_ENV=development` in `server/.env` and run `python app.py`. Heroku also needs `SESSION_SECRET` and `USERID_SECRET` set as config vars.

To run the tests:

```bash
cd server
python -m pytest tests
```
