# Group69-AgileWebProject
|       UWA ID       |       23102103      |      23668796       |        23857608         |      24280806         |
|--------------------|---------------------|---------------------|-------------------------|-----------------------|
|       Name         |      Imran Elmi     |     Glenn Fudge     |    Saayella Saayella    |     Zi Fung Tan       |
|  Github username   |      IceBearSYK     |       fudgeg        |        Saayella         |     ZFUNG14           |


The creation of the web application should be done in a private GitHub repository that includes a README containing:
  - a description of the purpose of the application, explaining its design and use.
    multimedia application that allows users to upload their watch history (ie. Netflix, Spotify, YouTube etc.)

  - a table with with each row containing the i) UWA ID ii) name and iii) Github user name of the group members.
  
  - instructions for how to launch the application.
  
  - instructions for how to run the tests for the application.


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
### Important: Run Selenium tests before seeding the database or running unit tests. This ensures a clean environment for UI-based validations (like fresh signup/login flows).

- Make sure the flask app is running. Then in another terminal,
-  pytest tests_e2e/ : This includes four selenium tests
-  pytest tests_unit/ : This includes six unit tests. 

