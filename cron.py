import requests
import json
import environ

from time import sleep
from websocket import create_connection

env = environ.Env()
env.read_env(".env")

HTTP_WS_SERVER = env("HTTP_WS_SERVER")
print(HTTP_WS_SERVER)


sources_info_url = f"http://{HTTP_WS_SERVER}/source/sources-info"
genres_info_url = f"http://{HTTP_WS_SERVER}/source/genres-info"


def main():
    while True:
        response = requests.get(sources_info_url)
        for source in response.json():
            if source.get("name", "") != "truyenfull.vn":
                continue
            genres_info = requests.get(
                f"{genres_info_url}/?source=truyenfull.vn"
            ).json()

            print("Connecting to websocket...")
            ws = create_connection(f"ws://{HTTP_WS_SERVER}/ws/source/truyenfull.vn/")
            print("Connected to websocket...")

            ws.send(json.dumps({"message": {**source, "genres": genres_info}}))

            ws.close()

        sleep(10)


def test():
    genres_info = requests.get(f"{genres_info_url}/?source=truyenfull.vn")
    print(genres_info)


if __name__ == "__main__":
    main()
    # test()
