from dotenv import load_dotenv
import os

def load_environment():
    if(os.getenv("RUN_IN_DOCKER","false").lower() == "false"):
        env_path = os.getenv("ENV_PATH",".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            print(f".env not found at {env_path}")
