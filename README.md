# HeartLink: An Online Dating Website
## Description
HeartLink is a social connection web application designed to help users in Australia discover and build meaningful relationships online. Users can register an account, complete their profile, add interests and stories, browse recommended profiles, search for other users, like profiles, view matches, and communicate through real-time messaging.

The platform focuses on creating a simple and engaging experience for online social discovery. It combines profile-based recommendations, location-based search, interactive profile pages, and messaging features to support more personal connections. The application is built with a modular Flask structure, making it suitable for collaborative development and future extension.

## Group Members

| Student ID | Name | GitHub Username |
|---|---|---|
| 24339091 | Zikun Hu | kumamoto24 |
| 24602792 | Ichirin Okamoto | ichirin0311 |
| 24370415 | Shakeel Jaumally | Shakeel-Droid |
> **Note:** `@UninformedShakeel` is another GitHub account of `Shakeel Jaumally`. It was used accidentally and only commited once in an early checkpoint demonstration.


## Features

- User registration, login, and logout with Flask-Login.
- Profile creation and editing with location, interests, bio, images, and story cards.
- Featured profiles on the public landing page.
- Profile recommendation based on compatibility, interests, distance, and completeness.
- Profile search with keyword, location, age, and interest filters.
- Detailed user profile pages with like and unlike functionality.
- Matches page showing mutual and one-way likes.
- Real-time messaging with conversation history and live updates.
- Security support with reCAPTCHA, CSRF protection, and password hashing.

## Technology Stack

This project uses a Flask-based web development stack with server-side templates, database migration support, user authentication, location services, and real-time messaging.

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Database | SQLAlchemy ORM, Flask-Migrate |
| Authentication | Flask-Login |
| Security | Flask-WTF CSRF protection, Werkzeug password hashing, Google reCAPTCHA |
| Real-time Communication | Flask-SocketIO, Socket.IO |
| Frontend | HTML, CSS, JavaScript, Jinja2 templates |
| Location Services | Google Maps Places API |
| Test | Pytest, Selenium |


## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/kumamoto24/AgileWebDev2026.git
cd AgileWebDev2026
```

2. Create and activate a virtual environment:


On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add the required environment variables:

```env
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
```

5. Apply database migrations:

```bash
flask db upgrade
```

6. Optional: seed the database with demo data:

```bash
python seed.py
```

7. Run the application:

```bash
python run.py
```

8. Run the test suite:

```bash
pytest -q
```

The application will be available at:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
AgileWebDev2026/
├── app/                         Main Flask application package.
│   ├── routes/                  Flask Blueprint modules grouped by feature.
│   │   ├── __init__.py          Registers all Blueprints for the app.
│   │   ├── auth.py              Signup, login, logout, and authentication routes.
│   │   ├── main.py              Index page and logged-in homepage routes.
│   │   ├── discovery.py         Profile search and recommendation APIs.
│   │   ├── profiles.py          Profile pages, image upload, and story routes.
│   │   ├── matches.py           Likes, matches page, and related APIs.
│   │   └── messages.py          Messages page route.
│   │
│   ├── static/                  Static files used by frontend pages.
│   │   ├── css/                 Stylesheets for page layout and visual design.
│   │   ├── images/              Default images, logos, and static assets.
│   │   ├── js/                  JavaScript for page interaction and API calls.
│   │   └── uploads/             Local storage for uploaded profile and story images.
│   │
│   ├── templates/               Jinja2 HTML templates rendered by Flask.
│   │
│   ├── __init__.py              Flask app creation and extension setup.
│   ├── models.py                Database models and relationships.
│   ├── helpers.py               Shared helper functions used across routes.
│   ├── decorators.py            Custom route guards such as profile_required.
│   ├── conversations.py         Conversation creation and lookup logic.
│   ├── sockets.py               Socket.IO events for real-time messaging.
│   └── user_loader.py           Flask-Login user loading logic.
│
├── migrations/                  Flask-Migrate and Alembic migration files.
│   └── versions/                Database schema migration scripts.
│
├── tests/                       Automated tests for the project.
│   ├── selenium/                Browser-based tests for user flows.
│   └── unit/                    Unit tests for backend logic and helpers.
│
├── config.py                    Flask configuration settings.
├── run.py                       Application entry point for running the server.
├── seed.py                      Script for inserting demo development data.
├── requirements.txt             Python package dependencies.
├── README.md                    Project documentation.
├── LICENSE                      Project license file.
└── .gitignore                   Files and folders ignored by Git.
```

## Contributing

This project was a collaborative effort with contributions from the following developers:

- [Zikun Hu](https://github.com/kumamoto24)
  - Developed the logged-in homepage, including both frontend layout and backend route logic.
  - Implemented the profile search feature with filters such as keyword, location, age range, and interests.
  - Integrated Google Places API in the profile search feature.
  - Developed the recommended profiles API using a match score based on compatibility, shared interests, distance, and profile completeness.
  - Developed the Messages page using SocketIO, including conversation loading and real-time message updates.
  - Implemented backend support for profile-related features, including story cards and image upload handling.
  - Set up the basic Flask server structure and organised the overall project structure.
  - Designed the main database schema and managed database migrations during development.
  - Developed unit tests and selenium tests for the homepage, messaging and related user flow features.
  - Introduced Flask Blueprints to organise routes and improve code maintainability.
  - Actively participated in issue discussions and pull request reviews throughout the project.

- [Ichirin Okamoto](https://github.com/ichirin0311)
  - Developed the frontend and backend logic for the My Profile and User Profile pages.
  - Implemented profile editing features, allowing users to update their personal information.
  - Added format checks of user inputs including age checks, word limitation in bio and location entry to align Google API suggestions
  - Integrated Google Places API in the profile editing page.
  - Added story cards to the profile page for displaying personal stories with images and descriptions, as well as and click-to-view popup models
  - Added a Like button on the User Profile page to record like relationships between users.
  - Designed and implemented the Matches page to show users liked by the current user and users who liked the current user.
  - Contributed to the database design for profile, story classes.
  - Developed unit tests and selenium end-to-end tests for profile, story, authentication, and matching features.
  - Actively participated in issue discussions and pull request reviews throughout the project.
- [Shakeel Jaumally](https://github.com/Shakeel-Droid)
  - Designed and implemented the frontend and backend logic for the login modal and signup page.
  - Implemented backend /signup route logic with secure user creation, password hashing, input validation, and duplicate email prevention.
  - Added password confirmation handling and validation logic across frontend and backend signup flow to ensure consistent and secure user registration.
  - Integrated Flask-Login to support user authentication and session management, replacing manual session handling with standardized authentication system.
  - Implemented CSRF tokens to protect authentication-related forms from cross-site request forgery attacks, including frontend integration for secure request handling.
  - Added Google reCAPTCHA verification to the login process to improve account security.
  - Wrote test files for authentication-related features, including unit tests for signup validation and password mismatch handling.
  - Developed selenium end-to-end tests to validate critical user flows including signup, login/logout, messaging, and matches functionality in a live test environment.
  - Actively participated in issue discussions and pull request reviews throughout the project.
> **Note:** The index page was completed collaboratively by all group members. The featured profiles feature was compeleted by [Zikun Hu](https://github.com/kumamoto24).

## License
This project is licensed under the MIT License.

