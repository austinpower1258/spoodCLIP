# spoodCLIP
This repository serves the purpose of allowing the user to SEED images from a Supabase database into a vector collection that will then in turn be used to perform the image searches. An additional feature of this repository is a FastAPI backend which allows for an HTTP endpoint for the frontend React web app to call the image search function and retrieve a JSON response object of the relevant images. This repository makes use of OpenAI's CLIP model, which is imperative to finding the closest relevant images based on searching a phrase in the database based on the vector encoding from the SEED function.

## Setup
1. Run `poetry install` to get the dependencies and Python packages that we will be using. You may need to use a virtualenv as this program requires Python v11. It will not work with the default Python version or Python v12. Run `poetry shell` for good measure after.
3. Run your Docker instance of Supabase Postgres server; a way to do this is to use Docker Desktop and monitor while it's running.
4. Now `cd spoodclip/image_search` in order to enter into the directory of spoodclip
5. You can run `poetry seed` to fetch the images from the Supabase Database and seed the images into a vector collection. This process can take a while, upwards of a few hours, depending on how many images you have in your Supabase database.
6. You can then start the backend server by running `poetry run main.py` and a FastAPI serer will be hosted, which can then get HTTP requests from frontend clients. There will be an endpoint `/search`.
