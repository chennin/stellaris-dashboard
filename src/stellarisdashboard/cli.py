import logging
import multiprocessing as mp
import threading

import click
import sqlalchemy

from stellarisdashboard import config, save_parser, timeline, visualization_data, visualization_mpl, models

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


save_path_help_string = 'The path where the Stellaris save files are stored. This should be the path to the folder containing the save folders for each game.'
game_name_help_string = 'An identifier of the game that you want to visualize. It matches prefixes, such that "--game-name uni" matches the game id "unitednationsofearth_-15512622", but not "lokkenmechanists_1256936305"'
showeverything_help_string = 'Use this flag if you want to include all empires regardless of visibility.'
threads_help_string = 'The number of threads that run in parallel when reading save games.'


@cli.command()
@click.option('--game-name', default="", type=click.STRING, help=game_name_help_string)
@click.option('--showeverything', is_flag=True, help=showeverything_help_string)
def visualize(game_name, showeverything):
    f_visualize_mpl(game_name, show_everything=showeverything)


def f_visualize_mpl(game_name_prefix: str, show_everything=False):
    config.CONFIG.show_everything = show_everything
    matching_games = models.get_known_games(game_name_prefix)
    if not matching_games:
        logger.warning(f"No game matching {game_name_prefix} was found in the database!")
    match_games_string = ', '.join(matching_games)
    logger.info(f"Found matching games {match_games_string} for prefix \"{game_name_prefix}\"")
    for game_name in matching_games:
        try:
            plot_data = visualization_data.EmpireProgressionPlotData(game_name)
            plot_data.initialize()
            plot_data.update_with_new_gamestate()
            plot = visualization_mpl.MatplotLibVisualization(plot_data)
            plot.make_plots()
        except sqlalchemy.orm.exc.NoResultFound as e:
            logger.error(f'No game matching "{game_name}" was found in the database!')


@cli.command()
@click.option('--game-name', default="", type=click.STRING, help=game_name_help_string)
@click.option('--showeverything', is_flag=True, help=showeverything_help_string)
def visualize_game_comparison(game_name, showeverything):
    f_visualize_mpl_comparison(game_name, show_everything=showeverything)


def f_visualize_mpl_comparison(game_name_prefix: str, show_everything=True):
    config.CONFIG.show_everything = show_everything
    matching_games = models.get_known_games(game_name_prefix)
    if not matching_games:
        logger.warning(f"No game matching {game_name_prefix} was found in the database!")
        return
    match_games_string = ', '.join(matching_games)
    logger.info(f"Found matching games {match_games_string} for prefix \"{game_name_prefix}\"")
    plot = visualization_mpl.MatplotLibComparativeVisualization(
        comparison_id=game_name_prefix,

    )
    for game_name in matching_games:
        try:
            plot_data = visualization_data.EmpireProgressionPlotData(game_name)
            plot_data.initialize()
            plot_data.update_with_new_gamestate()

            plot.add_data(game_name, plot_data)

        except sqlalchemy.orm.exc.NoResultFound as e:
            logger.error(f'No game matching "{game_name}" was found in the database!')
    plot.make_plots()


@cli.command()
@click.option('--save-path', type=click.Path(exists=True, file_okay=False))
@click.option('--polling-interval', type=click.FLOAT, default=0.5)
def monitor_saves(save_path, polling_interval):
    f_monitor_saves(polling_interval, save_path=save_path)


def f_monitor_saves(polling_interval=None, save_path=None, stop_event: threading.Event = None):
    if save_path is None:
        save_path = config.CONFIG.save_file_path
    if polling_interval is None:
        polling_interval = 0.5
    if stop_event is None:
        stop_event = threading.Event()
    save_reader = save_parser.SavePathMonitor(save_path)
    save_reader.mark_all_existing_saves_processed()
    tle = timeline.TimelineExtractor()

    show_wait_message = True
    while not stop_event.is_set():
        nothing_new = True
        for game_name, gamestate_dict in save_reader.get_new_game_states():
            if stop_event.is_set():
                break
            show_wait_message = True
            nothing_new = False
            tle.process_gamestate(game_name, gamestate_dict)
            plot_data = visualization_data.get_current_execution_plot_data(game_name)
            plot_data.initialize()
            plot_data.update_with_new_gamestate()
            del gamestate_dict
        if nothing_new:
            if show_wait_message:
                show_wait_message = False
                logger.info(f"Waiting for new saves in {config.CONFIG.save_file_path}")
            stop_event.wait(polling_interval)


@cli.command()
@click.option('--threads', type=click.INT, help=threads_help_string)
@click.option('--save-path', type=click.Path(exists=True, file_okay=False), help=save_path_help_string)
@click.option('--game-name', type=click.STRING, help=game_name_help_string)
def parse_saves(threads, save_path, game_name):
    f_parse_saves(threads, save_path, game_name_prefix=game_name)


def f_parse_saves(threads=None, save_path=None, game_name_prefix=None) -> None:
    if threads is not None:
        # since this is usually used when the game is not running, let the user override the thread count
        config.CONFIG.threads = threads
    if save_path is None:
        save_path = config.CONFIG.save_file_path
    save_reader = save_parser.SavePathMonitor(save_path)
    if game_name_prefix is not None:
        save_reader.apply_game_name_filter(game_name_prefix)
    tle = timeline.TimelineExtractor()
    for game_name, gamestate_dict in save_reader.get_new_game_states():
        tle.process_gamestate(game_name, gamestate_dict)
        del gamestate_dict


if __name__ == '__main__':
    mp.freeze_support()
    cli()
