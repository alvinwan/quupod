from queue import db

db.drop_all()
db.create_all()

print("""---

[OK] Database refresh complete.
Use 'make run' to launch server.
""")
