# HaaS – Hardware as a Service

ECE 461L team project. Users sign up, create or join projects, and check hardware (HWSet1 and HWSet2) in and out for their projects.

Live app: _add Heroku URL here_

Stack: React (`client/`), Flask (`server/`), MongoDB, Pytest, Heroku.

## Running locally

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

To use a real database instead, put `MONGODB_SERVER=<connection string>` and `FLASK_ENV=development` in `server/.env` and run `python app.py`.

Heroku also needs `SESSION_SECRET` and `USERID_SECRET` set as config vars.

## Tests

```bash
cd server
python -m pytest tests
```

The tests use the in-memory database and run automatically on every push and pull request.

## Team

Jake Barnett, Rafael Perales, Larry Nguyen, Esha Gajula, Tanya Sayooj, Marco Martinez
