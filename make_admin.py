import sqlite3

email = input("Enter email: ")

db = sqlite3.connect("fraudshield.db")
cursor = db.cursor()

cursor.execute(
    "UPDATE app_users SET role=? WHERE email=?",
    ("admin", email),
)

db.commit()

print("Admin role assigned successfully.")

db.close()