"""Sets the data store depending on ULHACKS_ENV"""

import os

def setup_local(bot):
    import store.json
    filename = os.environ.get("ULHACKS_JSON_STORE_FILENAME", None)
    bot.store = store.json.JsonStore(filename=filename)

def setup_heroku(bot):
    import store.postgresql
    address = os.environ["DATABASE_URL"]
    bot.store = store.postgresql.PostgresqlStore(address=address)

def setup(bot):
    env = os.environ.get("ULHACKS_ENV", "local")
    globals()[f"setup_{env}"](bot)
