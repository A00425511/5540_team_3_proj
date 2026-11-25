import os
import getpass
from pymongo import MongoClient
import mysql.connector

# Database configuration
USERNAME = os.environ.get("DB_USER", "u23")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "u23")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "u23")

MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")

if MYSQL_PASSWORD is None:
    MYSQL_PASSWORD = getpass.getpass("MySQL password: ")

if MONGO_PASSWORD is None:
    MONGO_PASSWORD = getpass.getpass("MongoDB password: ")

# Connect to MongoDB
mongo_client = MongoClient(
    host="localhost",
    port=27017,
    username=USERNAME,
    password=MONGO_PASSWORD,
    authSource="admin"
)

mongo_db = mongo_client[MONGO_DATABASE]
collection = mongo_db["proj5540"]

# Connect to MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

cursor = mysql_conn.cursor()

try:
    # Read cleaned MongoDB documents
    documents = list(collection.find())

    print(f"Found {len(documents)} software documents.")

    if not documents:
        raise ValueError("MongoDB collection proj5540 is empty.")

    # Insert product categories
    type_ids = {}

    for doc in documents:
        type_name = doc["product_type"]

        if type_name not in type_ids:
            cursor.execute(
                "INSERT INTO ProductType (TypeName) VALUES (%s)",
                (type_name,)
            )
            type_ids[type_name] = cursor.lastrowid

    # Insert software and evaluations
    software_count = 0
    evaluation_count = 0

    for doc in documents:
        brand = doc["brand"]
        type_id = type_ids[doc["product_type"]]

        cursor.execute(
            """
            INSERT INTO Software (Brand, TypeID)
            VALUES (%s, %s)
            """,
            (brand, type_id)
        )

        software_id = cursor.lastrowid
        software_count += 1

        for score in doc["scores"]:
            # Each MongoDB user_id is local to a software product.
            # Create a globally unique MySQL UserID for each review.
            cursor.execute(
                "INSERT INTO `User` (Email) VALUES (NULL)"
            )

            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO Evaluation (
                    UserID,
                    SoftwareID,
                    Friendliness,
                    Price,
                    Features,
                    Accuracy
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    software_id,
                    score["friendliness"],
                    score["price"],
                    score["features"],
                    score["accuracy"]
                )
            )

            evaluation_count += 1

    mysql_conn.commit()

    print("Data imported successfully!")
    print(f"Software products: {software_count}")
    print(f"Evaluations: {evaluation_count}")
    print(f"Product types: {len(type_ids)}")

except Exception:
    mysql_conn.rollback()
    raise

finally:
    cursor.close()
    mysql_conn.close()
    mongo_client.close()
