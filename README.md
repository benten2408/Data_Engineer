This the JobMarket project built during the DataEngineering bootcamp 
at DataScientest from January to April 2024.

To test our newly learned competences, our main goal is to build a complete
and efficient pipeline from the raw data, scraped from different sources,
to a fully functional dashboard.
We decided to focus the topic on the data engineering jobs offers published
in the last 30 days in France.

Our two sources are:
- the Welcome To The Jungle website, which agregates both jobs offers and
companies profiles
- Adzuna Api, which also aggregates jobs ads but does not provide any
company-specific information. It rather redirects the user towards the primary
url where the ad is available in full details.

To use our tool, please follow these steps:
1. clone this repository in a directory
2. you've been provided with a zipped .env file that needs to be located at the root
of the newly created directory 
3. create and run the containers thanks to the command docker-compose up --build -d
4. you will need to create a register JobMarket in  pgadmin (http://localhost:8888) 
5. then you can launch the database creation and data ingestion via python3 -m postgresql.db_main --function_name create_all


