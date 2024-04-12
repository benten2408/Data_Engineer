This is the repository for the JobMarket project built during the DataEngineering bootcamp 
at DataScientest from January to April 2024.

To test our newly learned competences, our main goal is to build a complete
and efficient pipeline from the raw data, scraped from different sources,
to a fully functional dashboard.
We decided to focus the topic on the data engineering jobs offers published
in the last 30 days in France (as of February 24th 2024).

Our two sources are:
- the Welcome To The Jungle website, which agregates both jobs offers and
companies profiles
- Adzuna API, which also aggregates jobs ads but does not provide any
company-specific information. It rather redirects the user towards the primary
url where the ad is available in full details.

To use our tool, please follow these steps:
1. clone this repository in a directory
2. you have been provided with a zipped .env file that needs to be located at the root
of the newly created directory 
3. create and run the containers thanks to the command docker-compose up --build (-d if you want it to be detached)
4. you will need to create a register named JobMarket in  pgadmin (http://localhost:8888) (Object > Register > Server … : in the General tab, complete the name field with JobMarket, in the Connection tab fill in the host name/address field with host.docker.internal)
5. then you can launch the database creation and data ingestion via python3 -m postgresql.db_main --function_name create_all
6. you are now free to visit all three pages :
- our FastAPI at http://localhost:8000/docs
- our Streamlit app at http://localhost:8501/
- our PGAdmin platform to access our Postgresql database at http://localhost:8888 





