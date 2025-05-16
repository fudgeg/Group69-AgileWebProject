# Group69-AgileWebProject
|       UWA ID       |       23102103      |      23668796       |        23857608         |      24280806         |
|--------------------|---------------------|---------------------|-------------------------|-----------------------|
|       Name         |      Imran Elmi     |     Glenn Fudge     |    Saayella Saayella    |     Zi Fung Tan       |
|  Github username   |      IceBearSYK     |       fudgeg        |        Saayella         |     ZFUNG14           |


## About the website

## Instruction to run
1. Clone the repo
   - git clone https://github.com/fudgeg/Group69-AgileWebProject
   - cd Group69-AgileWebProject
2. Set up the environment
   - pip install -r requirements.txt
3. Set up app and database
  - export FLASK_APP=run.py
  - export FLASK_ENV=development
  - flask db init (can be skipped if migration exists)
  - flask db migrate -m "initial" (can be skipped if migration exists)
  - flask db upgrade
4. Run the app
  - flask run

## Running the test suites 


## selenium test
- Invaid login (test_invalid_login.py)--> Verifies that logging in with incorrect credentials shows an error and denies access
- Signup flow (test_signup_flow.py) --> Ensures a new user can successfully sign up and is redirected to the login page.
- protected routes (test_upload_requires_login.py) --> Confirms that unauthenticated users are redirected to /login when trying to access the upload page.
- protected routes (test_home_requires_login.py) --> Confirms that unauthenticated users are redirected to /login when trying to access the home page.
- media display count (test_media_display_count.py) --> checks if the media analysis is working correctly 
- upload media flow (test_upload_media.py)--> checks if media is correctly uploaded and shown under entries


### Important: 
Run Selenium tests before seeding the database or running unit tests. This ensures a clean environment for UI-based validations (like fresh signup/login flows)

- Make sure the flask app is running. Then in another terminal,
-  pytest tests_e2e/ : This includes four selenium tests
-  pytest tests_unit/ : This includes six unit tests.

## Instructions to re-run the server 
1. rm -f app.db soulmaps.db
2. rm -rf migrations/
3. flask db init (can be skipped if migration exists)
4. flask db migrate -m "initial" (can be skipped if migration exists)
5. flask db upgrade
6. flask run

