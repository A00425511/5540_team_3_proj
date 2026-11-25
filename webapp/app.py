"""Software Evaluation and Comparison System — web app (MCDA 5540 Team Project).

Flask app on top of the team's MySQL database (see create_tables.sql).
Tables: User, RegisteredUser, Admin, ProductType, Software, Evaluation,
        Feature, SoftwareFeature, Collection, CollectionItem.

Run:
    pip install -r requirements.txt
    export MYSQL_PASSWORD='<your mysql password>'
    python app.py
Then open http://127.0.0.1:5000

On the course server MySQL runs on localhost, so the defaults work there.
If you run this on your laptop, point MYSQL_HOST at the server (or an
SSH tunnel) and set DB_USER / MYSQL_DATABASE accordingly.
"""

import os

from flask import Flask, flash, redirect, render_template, request, url_for
import mysql.connector
from mysql.connector import Error as MySQLError

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-me")

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "u23"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "u23"),
}

# Allowlist for the "show table" page — table names can't be passed as
# query parameters, so we only ever run SELECTs on names from this list.
TABLES = [
    "User", "RegisteredUser", "Admin", "ProductType", "Software",
    "Evaluation", "Feature", "SoftwareFeature", "Collection",
    "CollectionItem",
]

# Ranking criteria: form value -> SQL expression + display label.
CRITERIA = {
    "friendliness": ("AVG(E.Friendliness)", "Friendliness"),
    "price": ("AVG(E.Price)", "Price"),
    "features": ("AVG(E.Features)", "Features"),
    "accuracy": ("AVG(E.Accuracy)", "Accuracy"),
    "overall": ("(AVG(E.Friendliness) + AVG(E.Price) + AVG(E.Features)"
                " + AVG(E.Accuracy)) / 4", "Overall average"),
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------- home
@app.route("/")
def index():
    return render_template("index.html", tables=TABLES)


# ------------------------------------------------- Task 5.1: show table
@app.route("/tables/<name>")
def show_table(name):
    if name not in TABLES:
        flash(f"Unknown table: {name}")
        return redirect(url_for("index"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM `{name}` LIMIT 200")
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("table.html", table=name,
                           columns=columns, rows=rows)


# --------------------------------------- Task 5.2a: user + their evaluation
@app.route("/add/evaluation", methods=["GET", "POST"])
def add_evaluation():
    conn = get_db()
    cur = conn.cursor()
    # Software dropdown for the form.
    cur.execute("SELECT SoftwareID, Brand FROM Software ORDER BY Brand")
    software_list = cur.fetchall()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip() or None
        software_id = request.form.get("software_id")
        try:
            scores = {
                k: int(request.form.get(k, 0))
                for k in ("friendliness", "price", "features", "accuracy")
            }
        except ValueError:
            flash("All four scores must be whole numbers.")
            return render_template("add_evaluation.html",
                                   software_list=software_list)
        if not username or not software_id:
            flash("Username and software are required.")
            return render_template("add_evaluation.html",
                                   software_list=software_list)
        if any(v < 1 or v > 10 for v in scores.values()):
            flash("Scores must be between 1 and 10.")
            return render_template("add_evaluation.html",
                                   software_list=software_list)
        try:
            # One transaction, two tables: User (+ RegisteredUser) and
            # Evaluation. Any failure rolls the whole thing back.
            cur.execute(
                "INSERT INTO `User` (Email, RegisterDate) "
                "VALUES (%s, CURDATE())", (email,))
            user_id = cur.lastrowid
            cur.execute(
                "INSERT INTO RegisteredUser (UserID, Username) "
                "VALUES (%s, %s)", (user_id, username))
            cur.execute(
                """INSERT INTO Evaluation
                       (UserID, SoftwareID, Friendliness, Price,
                        Features, Accuracy, EvalDate)
                   VALUES (%s, %s, %s, %s, %s, %s, CURDATE())""",
                (user_id, software_id, scores["friendliness"],
                 scores["price"], scores["features"], scores["accuracy"]))
            conn.commit()
            flash(f"Evaluation saved — user '{username}' and their "
                  f"review are in the database.")
            return redirect(url_for("show_table", name="Evaluation"))
        except MySQLError as e:
            conn.rollback()
            flash(f"Could not save: {e.msg}")
    cur.close()
    conn.close()
    return render_template("add_evaluation.html",
                           software_list=software_list)


# --------------------------------------- Task 5.2b: software + its features
@app.route("/add/software", methods=["GET", "POST"])
def add_software():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT TypeID, TypeName FROM ProductType ORDER BY TypeName")
    types = cur.fetchall()
    cur.execute("SELECT FeatureID, FeatureName FROM Feature ORDER BY FeatureName")
    features = cur.fetchall()

    if request.method == "POST":
        brand = request.form.get("brand", "").strip()
        type_id = request.form.get("type_id")
        release_date = request.form.get("release_date") or None
        feature_ids = request.form.getlist("feature_ids")
        if not brand or not type_id:
            flash("Brand and product type are required.")
            return render_template("add_software.html",
                                   types=types, features=features)
        try:
            # One transaction, two tables: Software and SoftwareFeature.
            cur.execute(
                "INSERT INTO Software (Brand, TypeID, ReleaseDate) "
                "VALUES (%s, %s, %s)", (brand, type_id, release_date))
            software_id = cur.lastrowid
            for fid in feature_ids:
                cur.execute(
                    "INSERT INTO SoftwareFeature (SoftwareID, FeatureID) "
                    "VALUES (%s, %s)", (software_id, fid))
            conn.commit()
            flash(f"Software '{brand}' added with "
                  f"{len(feature_ids)} feature(s).")
            return redirect(url_for("show_table", name="Software"))
        except MySQLError as e:
            conn.rollback()
            flash(f"Could not save: {e.msg}")
    cur.close()
    conn.close()
    return render_template("add_software.html", types=types,
                           features=features)


# --------------------------------- Task 5.3: N-best / N-worst + compare
@app.route("/rankings", methods=["GET", "POST"])
def rankings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT TypeID, TypeName FROM ProductType ORDER BY TypeName")
    types = cur.fetchall()
    results = None
    params = {"n": 5, "criterion": "overall", "direction": "best",
              "type_id": "0"}
    if request.method == "POST":
        try:
            n = int(request.form.get("n", 5))
        except ValueError:
            n = 5
        n = max(1, min(n, 50))
        criterion = request.form.get("criterion", "overall")
        if criterion not in CRITERIA:
            criterion = "overall"
        direction = "DESC" if request.form.get("direction",
                                               "best") == "best" else "ASC"
        type_id = request.form.get("type_id", "0")
        expr, label = CRITERIA[criterion]
        query = f"""
            SELECT S.Brand, PT.TypeName,
                   AVG(E.Friendliness) AS avg_friendliness,
                   AVG(E.Price) AS avg_price,
                   AVG(E.Features) AS avg_features,
                   AVG(E.Accuracy) AS avg_accuracy,
                   {expr} AS score
            FROM Software S
            JOIN ProductType PT ON S.TypeID = PT.TypeID
            JOIN Evaluation E ON E.SoftwareID = S.SoftwareID
            WHERE (%s = '0' OR S.TypeID = %s)
            GROUP BY S.SoftwareID, S.Brand, PT.TypeName
            ORDER BY score {direction}
            LIMIT %s
        """
        curd = conn.cursor(dictionary=True)
        curd.execute(query, (type_id, type_id, n))
        results = curd.fetchall()
        curd.close()
        params = {"n": n, "criterion": criterion,
                  "direction": "best" if direction == "DESC" else "worst",
                  "type_id": type_id,
                  "label": label}
    cur.close()
    conn.close()
    return render_template("rankings.html", types=types,
                           results=results, params=params,
                           criteria=CRITERIA)


@app.route("/compare", methods=["GET", "POST"])
def compare():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SoftwareID, Brand FROM Software ORDER BY Brand")
    software_list = cur.fetchall()
    results = None
    if request.method == "POST":
        ids = [i for i in request.form.getlist("software_ids") if i.isdigit()]
        if len(ids) < 2:
            flash("Pick at least two products to compare.")
        else:
            placeholders = ", ".join(["%s"] * len(ids))
            curd = conn.cursor(dictionary=True)
            curd.execute(f"""
                SELECT S.Brand,
                       COUNT(E.EvaluationID) AS num_reviews,
                       AVG(E.Friendliness) AS avg_friendliness,
                       AVG(E.Price) AS avg_price,
                       AVG(E.Features) AS avg_features,
                       AVG(E.Accuracy) AS avg_accuracy,
                       (AVG(E.Friendliness) + AVG(E.Price)
                        + AVG(E.Features) + AVG(E.Accuracy)) / 4 AS overall
                FROM Software S
                LEFT JOIN Evaluation E ON E.SoftwareID = S.SoftwareID
                WHERE S.SoftwareID IN ({placeholders})
                GROUP BY S.SoftwareID, S.Brand
            """, ids)
            results = curd.fetchall()
            curd.close()
    cur.close()
    conn.close()
    return render_template("compare.html", software_list=software_list,
                           results=results)


@app.route("/search", methods=["GET", "POST"])
def search():
    results = None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT TypeID, TypeName FROM ProductType ORDER BY TypeName")
    types = cur.fetchall()
    if request.method == "POST":
        brand = "%" + request.form.get("brand", "").strip() + "%"
        type_id = request.form.get("type_id", "0")
        min_score = request.form.get("min_score", "").strip()
        try:
            min_score = float(min_score) if min_score else None
        except ValueError:
            min_score = None
        curd = conn.cursor(dictionary=True)
        curd.execute("""
            SELECT S.Brand, PT.TypeName,
                   AVG(E.Friendliness) AS avg_friendliness,
                   AVG(E.Price) AS avg_price,
                   AVG(E.Features) AS avg_features,
                   AVG(E.Accuracy) AS avg_accuracy
            FROM Software S
            JOIN ProductType PT ON S.TypeID = PT.TypeID
            LEFT JOIN Evaluation E ON E.SoftwareID = S.SoftwareID
            WHERE S.Brand LIKE %s AND (%s = '0' OR S.TypeID = %s)
            GROUP BY S.SoftwareID, S.Brand, PT.TypeName
            HAVING (%s IS NULL OR
                    (AVG(E.Friendliness) + AVG(E.Price) + AVG(E.Features)
                     + AVG(E.Accuracy)) / 4 >= %s)
            ORDER BY S.Brand
        """, (brand, type_id, type_id, min_score, min_score))
        results = curd.fetchall()
        curd.close()
    cur.close()
    conn.close()
    return render_template("search.html", types=types, results=results)


if __name__ == "__main__":
    app.run(debug=True)
