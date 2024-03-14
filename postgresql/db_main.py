import argparse
from postgresql.db_manager import DatabaseManager

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("--function_name", help='Create database and ingest data', required=True)

	args = parser.parse_args()
	db_manager = DatabaseManager()
	
	match args.function_name:
		case "create_all":
			db_manager.create_database()
			db_manager.create_schema()
			db_manager.ingest_data()
		case "create_database":
			db_manager.create_database()
			db_manager.create_schema()
		case "ingest_data":
			db_manager.ingest_data()
		case _:
			raise RuntimeError(f"Undefined {args.function_name}, Name of available functions : create_all, create_database or ingest_data")
      

	
