from server_config.runner import Server
from src.core import get_app_arguments


_DESCRIPTOR = "server"

def main():
    args = get_app_arguments(_DESCRIPTOR)
    app = Server(host=args.host, port=args.port)
    app.run()


if __name__ == "__main__":
    main()
