# CITS3403 Group Project: Heart Link
## Description
Heart Link is a web application designed to help users build meaningful social connections through a simple, interactive online experience. The platform supports user registration, login, and real-time communication features, creating a foundation for connecting people in a more personal and engaging way. Built with a modular Flask structure and supported by automated testing, Heart Link is designed to be maintainable, scalable, and suitable for collaborative development.

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

The application will be available at:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
AgileWebDev2026/
├── app/                         Main Flask application package.
│   ├── static/                  Static frontend assets used by the web pages.
│   │   ├── css/                 CSS stylesheets for layout and page styling.
│   │   ├── images/              Default images, logos, and static image assets.
│   │   ├── js/                  JavaScript files for frontend interactions and API requests.
│   │   └── uploads/             Local storage for user-uploaded profile and story images.
│   │
│   ├── templates/               Jinja2 HTML templates for application pages.
│   │
│   ├── __init__.py              Creates and configures the Flask application instance.
│   ├── models.py                Defines the database models.
│   ├── routes.py                Defines page routes and API endpoints.
│   ├── sockets.py               Handles real-time messaging events.
│   └── user_loader.py           Loads users for Flask-Login.
│
├── migrations/                  Database migration files managed by Flask-Migrate and Alembic.
│   └── versions/                Migration scripts for database schema updates.
│
├── tests/                       Unit tests and Selenium tests.
│
├── config.py                    Stores Flask configuration settings.
├── run.py                       Application entry point.
├── seed.py                      Inserts demo data for local development.
├── requirements.txt             Lists Python package dependencies.
├── README.md                    Project documentation.
├── .env                         Local environment variables, not committed to Git.
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
  - Wrote test files for the homepage and related user flow features.
  - Actively participated in issue discussions and pull request reviews throughout the project.

- [Ichirin Okamoto](https://github.com/ichirin0311)
  - Developed the frontend and backend logic for the My Profile and User Profile pages.
  - Implemented profile editing features, allowing users to update their personal information.
  - Integrated Google Places API in the profile editing page.
  - Added story cards to the profile page for displaying personal stories with images and descriptions, as well as and click-to-view popup models
  - Added a Like button on the User Profile page to record like relationships between users.
  - Designed and implemented the Matches page to show users liked by the current user and users who liked the current user.
  - Contributed to the database design for profile, story.
  - Developed unit tests and Selenium end-to-end tests for profile, story, authentication, and matching features.
  - Actively participated in issue discussions and pull request reviews throughout the project.
- [Shakeel Jaumally](https://github.com/Shakeel-Droid)
  - Designed and implemented the frontend and backend logic for the login modal and signup page.
  - Integrated Flask-Login to support user authentication and session management.
  - Implemented CSRF tokens to protect authentication-related forms from cross-site request forgery attacks.
  - Added Google reCAPTCHA verification to the login process to improve account security.
  - Wrote test files for the authentication-related features he developed.
  - Actively participated in issue discussions and pull request reviews throughout the project.
> **Note:** The index page was completed collaboratively by all group members. The featured profiles feature was compeleted by [Zikun Hu](https://github.com/kumamoto24).

## License
This project is licensed under the MIT License.

