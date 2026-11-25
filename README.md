# MCDA 5540 Team 3 — Software Evaluation and Comparison System

A database for exploring, evaluating, and comparing AI software products
(Chatbots, LLMs, Image Generators, Recommender Systems), rated 1–10 on
friendliness, price, features, and accuracy.

## Structure

- `create_tables.sql` — MySQL table definitions (10 tables, 3NF)
- `data2mongo2sql.sh` — pipeline: creates the MySQL tables, loads
  `project.json` into MongoDB (`project_raw`), cleans it into `proj5540`
  (emails masked to per-software user IDs), then transfers it into MySQL
- `clean_mongo.js` — the MongoDB aggregation that filters and masks the data
- `process_data.py` — moves the cleaned MongoDB documents into MySQL
- `webapp/` — the Flask web app (Task 5): browse tables, add users /
  evaluations / software, rankings, comparison, search. See
  `webapp/README.md` for how to run it.

## Running the pipeline

```bash
./data2mongo2sql.sh
```

It prompts for the MySQL and MongoDB passwords; database user/database are
`u23` by default (see the variables at the top of the script).

## Running the web app

```bash
cd webapp
pip install -r requirements.txt
MYSQL_PASSWORD='<your mysql password>' python app.py
```

Then open http://127.0.0.1:5000
