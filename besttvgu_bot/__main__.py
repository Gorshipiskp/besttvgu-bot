import asyncio

from besttvgu_bot.app import start_besttvgu_bot


def main():
    try:
        asyncio.run(start_besttvgu_bot())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
