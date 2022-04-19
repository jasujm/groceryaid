# Grocery Aid

App aiding grocery shopping in Finland

## Running

To run locally:

* Create environment files from samples:

      $ cp .env.sample .env
      $ cp .env.backend.sample .env.backend
      $ cp .env.db.sample .env.db

* Edit the newly created environment files to fill in the necessary details (see
  the comments in the files)

* Build and run

      $ docker-compose build --pull
      $ docker-compose up

* Initialize

      $ docker-compose run backend groceryaid init
      $ docker-compose run backend groceryaid fetch-stores
