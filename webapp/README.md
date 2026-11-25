# Software Evaluation and Comparison System — Web App (MCDA 5540, Task 5)

Flask app on top of the team's MySQL database (see `create_tables.sql`).
It implements all three required functions from the project description:

1. **Show table** — home page lists all 10 tables; clicking one shows its
   contents (`/tables/<name>`).
2. **Add new data** — two forms, each writing to two or more tables in a
   single transaction, with an error message shown when a database
   constraint is violated:
   - **Add Evaluation** (`/add/evaluation`): registers a new user and saves
     their evaluation — writes to `User`, `RegisteredUser`, `Evaluation`.
   - **Add Software** (`/add/software`): adds a new product with its
     features — writes to `Software`, `SoftwareFeature`.
3. **Extract desirable information** — the goals from the intro:
   - **Rankings** (`/rankings`): N-best / N-worst software by friendliness,
     price, features, accuracy, or overall average, optionally filtered by
     product type (Chatbot, LLM, Image Generator, Recommender System).
   - **Compare** (`/compare`): average scores of two or more products side
     by side.
   - **Search** (`/search`): find software by brand and/or product type,
     with a minimum average score.

## Running it

```bash
pip install -r requirements.txt
export MYSQL_PASSWORD='<your mysql password>'
python app.py
```

Then open http://127.0.0.1:5000

Configuration is read from environment variables (defaults in brackets):

| Variable | Meaning | Default |
|---|---|---|
| `MYSQL_HOST` | MySQL host | `localhost` |
| `DB_USER` | MySQL user | `u23` |
| `MYSQL_PASSWORD` | MySQL password | (empty — must be set) |
| `MYSQL_DATABASE` | Database | `u23` |
| `FLASK_SECRET_KEY` | Flask session key | dev default — set a real one |

On the course server MySQL runs on `localhost`, so the defaults work there.
To run on a laptop, point `MYSQL_HOST` at the server (or an SSH tunnel).

## Files

- `app.py` — the whole app: routes, queries, transactions, error handling
- `templates/` — Jinja pages (one per screen, all extending `base.html`)
- `requirements.txt` — Flask + mysql-connector-python
