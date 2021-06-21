from datetime import datetime, timedelta

import data.layout as layout
import debug
from data.final import Final
from data.headlines import Headlines
from data.pregame import Pregame
from data.schedule import Schedule
from data.scoreboard import Scoreboard
from data.standings import Standings
from data.status import Status
from data.update import UpdateStatus
from data.weather import Weather


class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        # Parse today's date and see if we should use today or yesterday
        self.today = self.__parse_today()

        # get schedule
        self.schedule = Schedule(self.today, config)
        # NB: Can return none, but shouldn't matter?
        self.current_game = self.schedule.get_preferred_game()

        # Fetch all standings data for today
        # (Good to have in case we add a standings screen while rotating scores)
        self.standings = Standings(self.today, config.preferred_divisions)

        # Weather info
        self.weather = Weather(config)

        # News headlines
        self.headlines = Headlines(config)

        # Network status state - we use headlines and weather condition as a sort of sentinial value
        self.network_issues = (self.weather.conditions == "Error") and (not self.headlines.feed_data)

    def __parse_today(self):
        if self.config.demo_date:
            today = datetime.strptime(self.config.demo_date, "%Y-%m-%d")
        else:
            today = datetime.today()
            end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            if end_of_day > datetime.now():
                today -= timedelta(days=1)
        return today

    def refresh_game(self):
        status = self.current_game.update()
        if status == UpdateStatus.SUCCESS:
            self.__update_layout_state()
            self.print_game_data_debug()
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True

    def advance_to_next_game(self):
        game = self.schedule.next_game()
        if game is not None:
            self.current_game = game
            self.__update_layout_state()
            self.print_game_data_debug()
            self.network_issues = False
        else:
            self.network_issues = True

    def refresh_standings(self):
        self.__process_network_status(self.standings.update())

    def refresh_weather(self):

        self.__process_network_status(self.weather.update())

    def refresh_news_ticker(self):
        self.__process_network_status(self.headlines.update())

    def refresh_schedule(self, force=False):
        self.__process_network_status(self.schedule.update(force))

    def __process_network_status(self, status):
        if status == UpdateStatus.SUCCESS:
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True

    def __update_layout_state(self):
        self.config.layout.set_state()
        if self.current_game.status() == Status.WARMUP:
            self.config.layout.set_state(layout.LAYOUT_STATE_WARMUP)

        if self.current_game.is_no_hitter():
            self.config.layout.set_state(layout.LAYOUT_STATE_NOHIT)

        if self.current_game.is_perfect_game():
            self.config.layout.set_state(layout.LAYOUT_STATE_PERFECT)

    def print_game_data_debug(self):
        debug.log("Game Data Refreshed: %s", self.current_game._data["gameData"]["game"]["id"])
        debug.log("Pre: %s", Pregame(self.current_game, self.config.time_format))
        debug.log("Live: %s", Scoreboard(self.current_game))
        debug.log("Final: %s", Final(self.current_game))
