# Group69-AgileWebProject

| UWA ID          | 23102103   | 23668796    | 23857608          | 24280806    |
| --------------- | ---------- | ----------- | ----------------- | ----------- |
| Name            | Imran Elmi | Glenn Fudge | Saayella Saayella | Zi Fung Tan |
| Github username | IceBearSYK | fudgeg      | Saayella          | ZFUNG14     |

The creation of the web application should be done in a private GitHub repository that includes a README containing:

- a description of the purpose of the application, explaining its design and use.
  multimedia application that allows users to upload their watch history (ie. Netflix, Spotify, YouTube etc.)

- a table with with each row containing the i) UWA ID ii) name and iii) Github user name of the group members.

- instructions for how to launch the application.

- instructions for how to run the tests for the application.

## Instruction to run

- git clone https://github.com/your-username/soulmaps.git
- cd soulmaps
- pip install -r requirements.txt
- flask shell
- Type
  "
  from app import create_app
  from app.models import db
  app = create_app()

          with app.app_context():
              db.create_all()

  "

- flask run
