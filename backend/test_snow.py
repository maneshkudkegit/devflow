
import sys
sys.path.append('d:/projects/devflow/backend/app')
from core.config import get_settings
import snowflake.connector
settings = get_settings()

try:
    conn = snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        role=settings.SNOWFLAKE_ROLE
    )
    cur = conn.cursor()
    print("Connected.")
except Exception as e:
    print("Connection error:", e)
    sys.exit(1)

try:
    cur.execute("CREATE USER IF NOT EXISTS test2 PASSWORD='ChangeMe123!' MUST_CHANGE_PASSWORD=TRUE")
    print("Query 1 success.")
except Exception as e:
    print('ERROR 1:', e)

try:
    cur.execute("CREATE USER test3 PASSWORD='ChangeMe123!' MUST_CHANGE_PASSWORD=TRUE")
    print("Query 2 success.")
except Exception as e:
    print('ERROR 2:', e)

try:
    cur.execute("CREATE USER IF NOT EXISTS test4 PASSWORD = 'ChangeMe123!' MUST_CHANGE_PASSWORD = TRUE")
    print("Query 3 success.")
except Exception as e:
    print('ERROR 3:', e)

try:
    cur.execute("CREATE OR REPLACE USER test5 PASSWORD='ChangeMe123!' MUST_CHANGE_PASSWORD=TRUE")
    print("Query 4 success.")
except Exception as e:
    print('ERROR 4:', e)

try:
    cur.execute("CREATE USER test6")
    cur.execute("ALTER USER test6 SET PASSWORD='ChangeMe123!'")
    print("Query 5 success.")
except Exception as e:
    print('ERROR 5:', e)
