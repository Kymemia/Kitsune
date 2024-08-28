import os
from dotenv import load_dotenv
from models.engine.storage import Storage

# load environment variables
load_dotenv()

host = os.getenv("MAIN_DB_HOST", "localhost")
database = os.getenv("MAIN_DB", "DataDome")
username = os.getenv("MAIN_DB_USER", "root")
password = os.getenv("MAIN_DB_USER_PASSWORD", "")
port = os.getenv("MAIN_DB_PORT", "3306")
driver = os.getenv("MAIN_DB_DRIVER", "mysql+pymysql")

storage = Storage(
        host=host,
        database=database,
        username=username,
        password=password,
        port=port,
        drivername=driver
        )
