from queue import db
from default_settings import load_settings

db.drop_all()
db.create_all()
load_settings()

print("""---

[OK] Database refresh complete.
Use 'make run' to launch server.
""")
