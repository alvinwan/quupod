from queue import db
from .default_settings import default_settings
from queue.models import Setting, add_obj

db.drop_all()
db.create_all()

# Add all settings to database
for setting in default_settings:
    if not Setting.query.filter_by(name=setting['name']).first():
        add_obj(Setting(**setting))

print("""---

[OK] Database refresh complete.
Use 'make run' to launch server.
""")
