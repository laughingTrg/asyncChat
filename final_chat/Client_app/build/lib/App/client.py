from src.core import get_app_arguments
from client_config.runner import Client

_DESCRIPTOR = "client"


def main():
    args = get_app_arguments(_DESCRIPTOR)
    app = Client(host=args.host, port=args.port)
    app.run()


if __name__ == "__main__":
    main()
