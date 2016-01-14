from queue import db
from default_settings import load_settings

db.create_all()
load_settings()

print("""---

[OK] Database creation complete.
Use 'make run' to launch server.
""")
