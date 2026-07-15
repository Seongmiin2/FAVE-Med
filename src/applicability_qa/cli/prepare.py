import argparse

from .common import load_config, load_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--domain")
    args = parser.parse_args()
    config, root = load_config(args.config)
    items = load_items(config, root)
    print(f"validated {len(items)} {config['domain']} items")


if __name__ == "__main__":
    main()
