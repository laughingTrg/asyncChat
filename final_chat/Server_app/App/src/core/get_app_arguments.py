import argparse


def get_app_arguments(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=8128)
    return parser.parse_args()
