# Group69-AgileWebProject

| UWA ID          | 23102103   | 23668796    | 23857608          | 24280806    |
| --------------- | ---------- | ----------- | ----------------- | ----------- |
| Name            | Imran Elmi | Glenn Fudge | Saayella Saayella | Zi Fung Tan |
| Github username | IceBearSYK | fudgeg      | Saayella          | ZFUNG14     |

## About the website : Soul Maps

Purpose:

- Soul Maps is a personal media tracker and social sharing web application. It allows users to log, rate and share the books they read, Tv Shows/Movies they watch and Music they listen to. It then turns this data into personlised insights. Soul Maps also encourages connections by letting you add friends, share your media snapshots (incluing charts and summaries) allowing you to discover each other's tastes.

Design:

- Modular Flask App: Uses an application-factory (create_app) and a main blueprint for clean, testable routing.
- Config via .env: Loads secrets (e.g. SECRET_KEY, database URL) from a .env into a Config class, keeping credentials out of code.

- SQLAlchemy Models: Polymorphic MediaEntry subclasses (Book, Movie, TVShow, Music), plus User, friendships, friend-requests, snapshots, and activity logs.
- Forms & CSRF: All user inputs handled by Flask-WTF form classes (with built-in CSRF), plus client-side JS for dynamic upload fields.
- Templates & Assets: Jinja2 templates extend a shared layout; Chart.js and html2canvas power the “For You” snapshots; SCSS/CSS ensures responsive styling.

- Authentication: Flask-Login secures /home and /upload, redirecting unauthenticated users to login.

- Testing: Pytest for unit logic, Selenium end-to-end tests verify login protection and upload workflows.

Note:

Parts of this project were developed with the assistance from generative AI tools (e.g., ChatGPT, copilot) and online resources such as tutorial web sites (e.g., GeeksforGeeks), and forums (e.g., Stack Overflow). All code was reviewed and adapted to ensure understanding and functionality within the project.


Use:

- First, register with your full name, username, email address and password. Your account will be verified to see if your credentials are valid, then you can log in for the first time.
- After logging in you will be on the Home page. However, in the top right banner you will see some icons. From left to right they are Home, For You Page, Notifications, Friends and Settings.
- You will be directed to the home page. This is where you can upload the media you want by clicking on the import button. You can then select a media type: Book, Movie, TV Show, or Music. Then you can fill in other fields such as the title, rating, the date you consumed this media and any other comments you wish. These field are type-specific fields (e.g. author and genre for books). Now you can submit the entry to save it.
- Next icon is the For You page. This is where you will see your media “identity” headline which gives you a personalised description depending on what media you consumed the most. You can see the number of Books, Movies, TV Shows, and Music consumed in various visual forms. Your top-genre can been seen in pie charts per media type. Your consumption of media can be seen in a timeline chart that tracks when and how frequent you consumed different types of media. You will also see a Book
  Reading Insights where you can find your completion rate and average time spent on a book. Export & Share Snapshots

- The Notifications page will show any snapshots or friend requests where you can approve or reject any you have received. You can generate a full-page snapshot and export it as an image or share via email using the Share via Email button or connect with friends where your friend will received the snapshot.

- Search for users by username and send friend requests in the Friends page, where you can browse recommended connections, share individual media entries through the Share Media form
- In Settings, you can manage your account, update your profile picture, username, or email. You can also change your password with built-in validation. Permanently delete your account if desired

## Instruction to run

1. Clone the repo
   - git clone https://github.com/fudgeg/Group69-AgileWebProject
   - cd Group69-AgileWebProject
2. Install dependencies
   - pip install -r requirements.txt
3. Set environment variables
   - Option 1: Use a .env file
   - Option 2: Run following:
   - export FLASK_APP=run.py (or on windows set FLASK_APP=run.py)
   - export FLASK_ENV=development (or on windows set FLASK_ENV=development)
4. Set up database
   - flask db init (can be skipped if migration exists)
   - flask db migrate -m "initial" (can be skipped if migration exists)
   - flask db upgrade
5. Run the app

- flask run

## Running the test suites

### Important:

Run Selenium tests before seeding the database or running unit tests. This ensures a clean environment for UI-based validations (like fresh signup/login flows)

- Make sure the flask app is running. Then in another terminal,
- pytest tests_e2e/ : This includes six selenium tests
- pytest tests/ : This includes six unit tests.

## Instructions to re-run the server

1. rm -f app.db soulmaps.db
2. rm -rf migrations/
3. flask db init (can be skipped if migration exists)
4. flask db migrate -m "initial" (can be skipped if migration exists)
5. flask db upgrade
6. flask run

## Unit Tests

to run Unit Tests use: pytest tests/

1. Authentication Tests (tests/test_auth.py) - Duplicate signup is rejected
2. User Model Tests (tests/test_users.py) - Creating, querying, and deleting users
3. User Model Tests (tests/test_users.py) - Email uniqueness and data integrity
4. Book Model Tests (tests/test_books.py) -Add, retrieve, and delete book entries
5. Movie Model Tests (tests/test_movies.py) - CRUD operations and genre field validation
6. TVShow Model Tests (tests/test_tvshows.py) - Verify listing and removal functions
7. Music Model Tests (tests/test_music.py)- Ensure music entries persist correctly

## Selenium Tests

to run Selenium Tests use: pytest tests_e2e/

### Note: These tests run reliably on Windows. Mac users may encounter issues.

1. Invaid login (test_invalid_login.py)--> Verifies that logging in with incorrect credentials shows an error and denies access
2. Signup flow (test_signup_flow.py) --> Ensures a new user can successfully sign up and is redirected to the login page.
3. protected routes (test_upload_requires_login.py) --> Confirms that unauthenticated users are redirected to /login when trying to access the upload page.
4. protected routes (test_home_requires_login.py) --> Confirms that unauthenticated users are redirected to /login when trying to access the home page.
5. media display count (test_media_display_count.py) --> checks if the media analysis is working correctly
6. upload media flow (test_upload_media.py)--> checks if media is correctly uploaded and shown under entries

**To run the website after performing selenium tests, you will need to re-run the server**

## Open Tasks

- 🔔 **Notification popup appears on Settings icon** instead of the bell icon. (UI alignment issue)
- 🖼️ **Snapshot image dimensions are inconsistent** across different screen sizes. Needs fixed aspect ratio or responsive scaling.
