import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from env_config import DATABASE, POSTGRES_USER, POSTGRES_PASSWORD, HOST, PORT

from postgresql.create_db_schema import create_database_query, create_schema_query
from postgresql.ingest_data import ingest_joboffers_query, ingest_skills_query, location_process, create_user

class DatabaseManager:
	def __init__(self, default=True):
		self.db_params = {
			"user": POSTGRES_USER,
			"password": POSTGRES_PASSWORD,
			"host": HOST,
			"port": PORT
		}
		if not default:
			self.db_params["database"] = DATABASE

	def connect(self):
		connection = psycopg2.connect(**self.db_params)
		connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		return connection

	def create_database(self):
		conn = self.connect()
		cur = conn.cursor()

		try:
			create_database_query(cur)
			print(f"Database '{DATABASE}' created successfully.")
		except psycopg2.Error as e:
			print(f"An error occurred: {e}")
		finally:
			cur.close()
			conn.close()
		
	def create_schema(self):
		self.db_params["database"] = DATABASE

		conn = self.connect()
		cur = conn.cursor()
		
		create_schema_query(cur)

		conn.commit()
		cur.close()
		conn.close()

		print(f"{DATABASE} database schema created successfully.")

	def ingest_data(self):
		self.db_params["database"] = DATABASE

		conn = self.connect()
		cur = conn.cursor()

		ingest_skills_query(cur)
		ingest_joboffers_query(cur)
		location_process(cur)
		create_user(cur)

		print(f"Data ingested in {DATABASE} successfully.")

		conn.commit()
		cur.close()
		conn.close()