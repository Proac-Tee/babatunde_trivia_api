from dotenv import load_dotenv
import os

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
load_dotenv()
DB_HOST = os.getenv("DB_HOST", "127.0.0.1:5432")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PATH = f"postgresql+psycopg2://{DB_USER}:@{DB_HOST}/{DB_NAME}"
