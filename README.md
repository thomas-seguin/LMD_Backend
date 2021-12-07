# LMD_backend

Our backend is supported by FASTapi
### Requirements
python_version = "3.7"
Check other requirements in `requirements.txt`

# Running the backend server locally
Once you install the correct python version, you can run
-  `pip install pipenv` (We will use this to create a pip environment, more on why to use python environment can be found here: https://opensource.com/article/18/2/why-python-devs-should-use-pipenv)
- Another good read - https://thoughtbot.com/blog/how-to-manage-your-python-projects-with-pipenv
Once installed create a virtual environment for this project using
- `pipenv install`
- `pipenv shell`
- `pipenv install -r requirements.txt`
- `python main.py`

# Database
We use MongoDb as our databse

# Connect locally
1. Install MongoDb Compass community edition and also install the mongosh
2. Once installed, open it and you will see a prompt to create a connection. To connect with a local instance of your mongoDb databse type in `mongodb://127.0.0.1:27017`
3. Create the `LastMileDelivery Database` and add a `drivers collection` to it (need to figure out how to automate this process)
4. Make a copy of `.env.example` and name it `.env. Replace the placeholders with the appropriate values


