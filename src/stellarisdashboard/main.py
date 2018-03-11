import logging
import pathlib
import sys
import threading
import time
import multiprocessing as mp
from stellarisdashboard import cli, dash_server, save_parser

BASE_DIR = pathlib.Path.home() / ".local/share/stellaristimeline/"
STELLARIS_SAVE_DIR = pathlib.Path.home() / ".local/share/Paradox Interactive/Stellaris/save games/"
logging.basicConfig(level=logging.INFO, filename=BASE_DIR / "stellaris_dashboard.log")

logger = logging.getLogger(__name__)

# Add a stream handler for stdout output
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root_logger.addHandler(ch)


def main():
    threads = max(1, mp.cpu_count() // 2 - 1)
    t_save_monitor = threading.Thread(target=cli.f_monitor_saves, daemon=False, args=(threads, 10))
    t_save_monitor.start()
    t_dash = threading.Thread(target=dash_server.start_server, daemon=False, args=())
    t_dash.start()
    while True:
        # update the selected game when a save game from a different game is detected.
        # This is a workaround since the game selection dropdown
        # from dash does not seem to work in the in-game browser.
        time.sleep(5)
        if save_parser.MOST_RECENTLY_UPDATED_GAME is not None and save_parser.MOST_RECENTLY_UPDATED_GAME != dash_server.SELECTED_GAME_NAME:
            logger.debug("Updating selected game in dash!")
            logger.debug(save_parser.MOST_RECENTLY_UPDATED_GAME)
            dash_server.update_selected_game(save_parser.MOST_RECENTLY_UPDATED_GAME)


if __name__ == '__main__':
    main()