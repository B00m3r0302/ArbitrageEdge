"""Application configuration."""
from dataclasses import field

from prompt_toolkit.key_binding.bindings.named_commands import self_insert
from pydantic import (
    ConfigDict,
    Field,
    BaseModel,
    field_validator,
    model_validator
)
from pydantic_settings import BaseSettings
from typing import Optional, Self
from enum import Enum

class Sports(Enum):
    americanfootball_cfl = "americanfootball_cfl"
    americanfootball_ncaaf ="americanfootball_ncaaf"
    americanfootball_ncaaf_championship_winner ="americanfootball_ncaaf_championship_winner"
    americanfootball_nfl = "americanfootball_nfl"
    americanfootball_nfl_preseason = "americanfootball_nfl_preseason"
    americanfootball_nfl_super_bowl_winner = "americanfootball_nfl_super_bowl_winner"
    americanfootball_ufl = "americanfootball_ufl"
    baseball_milb ="baseball_milb"
    baseball_mlb = "baseball_mlb"
    baseball_mlb_preseason ="baseball_mlb_preseason"
    baseball_mlb_world_series_winner = "baseball_mlb_world_series_winner"
    basketball_ncaa = "baseball_ncaa"
    baskbetball_nba = "basketball_nba"
    basketball_nba_championship_winner = "basketball_nba_championship_winner"
    basketball_nba_preseason = "basketball_nba_preseason"
    basketball_nba_summer_league ="basketball_nba_summer_league"
    basketball_ncaab = "basketball_ncaab"
    basketball_ncaab_championship_winner ="basketball_ncaab_championship_winner"
    boxing_boxing = "boxing_boxing"
    golf_masters_tournament_winner = "golf_masters_tournament_winner"
    golf_pga_championship_winner = "golf_pga_championship_winner"
    golf_the_open_championship_winner = "golf_the_open_championship_winner"
    golf_us_open_winner = "golf_us_open_winner"
    icehockey_nhl = "icehockey_nhl"
    icehockey_nhl_championship_winner = "icehockey_nhl_championship_winner"
    icehockey_nhl_preseason ="icehockey_nhl_preseason"
    mma_mixed_martial_arts = "mma_mixed_martial_arts"
    politics_us_presidential_election_winner = "politics_us_presidential_election_winner"
    rugbyleague_nrl = "rugbyleague_nrl"
    rugbyleague_nrl_state_of_origin = "rugbyleague_nrl_state_of_origin"
    rugbyunion_six_nations = "rugbyunion_six_nations"
    soccer_africa_cup_of_nations = "soccer_africa_cup_of_nations"
    soccer_concacaf_gold_cup = "soccer_concacaf_gold_cup"
    soccer_concacaf_leagues_cup = "soccer_concacaf_leagues_cup"
    soccer_efl_champ = "soccer_efl_champ"
    soccer_england_efl_cup = "soccer_england_efl_cup"
    soccer_epl = "soccer_epl"
    soccer_fa_cup = "soccer_fa_cup"
    soccer_fifa_club_world_cup = "soccer_fifa_club_world_cup"
    soccer_fifa_world_cup = "soccer_fifa_world_cup"
    soccer_fifa_world_cup_qualifiers_europe = "soccer_fifa_world_cup_qualifiers_europe"
    soccer_fifa_world_cup_qualifiers_south_america = "soccer_fifa_world_cup_qualifiers_south_america"
    soccer_fifa_world_cup_winner = "soccer_fifa_world_cup_winner"
    soccer_fifa_world_cup_womens = "soccer_fifa_world_cup_womens"
    soccer_france_ligue_one = "soccer_france_ligue_one"
    soccer_germany_bundesliga = "soccer_germany_bundesliga"
    soccer_italy_serie_a = "soccer_italy_serie_a"
    soccer_spain_la_liga = "soccer_spain_la_liga"
    soccer_uefa_champs_league = "soccer_uefa_champs_league"
    soccer_uefa_champs_league_qualification = "soccer_uefa_champs_league_qualification"
    soccer_uefa_euro_qualification = "soccer_uefa_euro_qualification"
    soccer_uefa_europa_conference_league = "soccer_uefa_europa_conference_league"
    soccer_uefa_europa_league = "soccer_uefa_europa_league"
    soccer_uefa_european_championship = "soccer_uefa_european_championship"
    soccer_uefa_nations_league = "soccer_uefa_nations_league"
    soccer_usa_mls = "soccer_usa_mls"
    tennis_atp_aus_open_singles = "tennis_atp_aus_open_singles"
    tennis_atp_canadian_open = "tennis_atp_canadian_open"
    tennis_atp_china_open = "tennis_atp_china_open"
    tennis_atp_cincinnati_open = "tennis_atp_cincinnati_open"
    tennis_atp_dubai = "tennis_atp_dubai"
    tennis_atp_french_open = "tennis_atp_french_open"
    tennis_arp_indian_wells = "tennis_atp_indian_wells"
    tennis_atp_italian_open = "tennis_atp_italian_open"
    tennis_atp_madrid_open = "tennis_atp_madrid_open"
    tennis_atp_miami_open = "tennis_atp_miami_open"
    tennis_atp_monte_carlo_masters = "tennis_atp_monte_carlo_masters"
    tennis_atp_paris_masters = "tennis_atp_paris_masters"
    tennis_atp_qatar_open = "tennis_atp_qatar_open"
    tennis_atp_shanghai_masters = "tennis_atp_shanghai_masters"
    tennis_atp_us_open = "tennis_atp_us_open"
    tennis_atp_wimbledon = "tennis_atp_wimbledon"
    tennis_wta_aus_open_singles = "tennis_wta_aus_open_singles"
    tennis_wta_canadian_open = "tennis_wta_canadian_open"
    tennis_wta_china_open = "tennis_wta_china_open"
    tennis_wta_cincinnati_open = "tennis_wta_cincinnati_open"
    tennis_wta_dubai = "tennis_wta_dubai"
    tennis_wta_french_open = "tennis_wta_french_open"
    tennis_wta_indian_wells = "tennis_wta_indian_wells"
    tennis_wta_italian_open = "tennis_wta_italian_open"
    tennis_wta_madrid_open = "tennis_wta_madrid_open"
    tennis_wta_miami_open = "tennis_wta_miami_open"
    tennis_wta_qatar_opem = "tennis_wta_qatar_open"
    tennis_wta_us_open = "tennis_wta_us_open"
    tennis_wta_wimbledon = "tennis_wta_wimbledon"
    tennis_wta_wuhan_open = "tennis_wta_wuhan_open"
    upcoming = "upcoming"

class Settings(BaseSettings):
    """
    Application settings
    """
    model_config = ConfigDict(
        env_file = ".env",
        case_sensitive = True,
        env_file_encoding = "utf-8",
        extra="ignore"
    )

    project_name: str = "ArbitrageEngine"
    version: str = "0.1.0"
    description: str = "Odds Engine/API for calculating sports betting odds"
    api_v1_str: str = "/api/v1"

    debug: bool = False

    odds_api_key: str = Field(..., repr=False, alias="ODDS_API_KEY", frozen=True)



settings = Settings()

class Sport(BaseModel):
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    key: Sports = Field(..., alias="sport")
    group: str = Field(..., alias="group")
    title: str = Field(..., alias="title")
    description: str = Field(..., alias="description")
    active: Optional[bool] = Field(default = False, alias="active")
    has_outrights: Optional[bool] = Field(default = False, alias="has_outrights")

    @model_validator(mode="after")
    def check_sport(self) -> Self:
        sport = self.key
        if not sport:
            raise ValueError("Sport not supported")

        return self


class Odds(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    regions: list[str] = Field(default="us", alias="region")
    markets: Optional[str] = Field(default = "")
    dateFormat: Optional[list[str]] = Field(default = "iso", alias="date_format", repr=False)
    oddsFormat: Optional[str] = Field(default = "", alias="odds_format", repr=False)
    eventIds: Optional[list[str]] = Field(default = "", alias="event_id", repr=False)
    bookmakers: Optional[str] = Field(default = "", alias="bookmaker", repr=False)
    commenceTimeFrom: Optional[str] = Field(default = "", repr=False)
    commenceTimeTo: Optional[str] = Field(default = "", repr=False)
    includeLinks: Optional[bool] = Field(default = False, repr=False)
    includeSids: Optional[bool] = Field(default = False, repr=False)
    includeBetLimits: Optional[bool] = Field(default = False, repr=False)
    includeRotationNumbers: Optional[bool] = Field(default = False, repr=False)

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class Scores(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    daysFrom: Optional[int] = Field(default=None, ge=1, le=3)
    dateFormat: Optional[list[str]] = Field(default = "iso", alias="date_format", repr=False)
    eventIds: Optional[list[str]] = Field(default = "", alias="event_id", repr=False)

    @field_validator("daysFrom")
    @classmethod
    def validate_days_from(cls, daysFrom: Optional[int]) -> int:
        if not 1 <= daysFrom <= 3:
            raise ValueError("daysFrom must be between 1 and 3")

        return daysFrom

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class Events(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    dateFormat: Optional[list[str]] = Field(default = "iso", alias="date_format", repr=False)
    eventIds: Optional[list[str]] = Field(default = "", alias="event_id", repr=False)
    commenceTimeFrom: Optional[str] = Field(default = "", repr=False)
    commenceTimeTo: Optional[str] = Field(default = "", repr=False)
    includeRotationNumbers: Optional[bool] = Field(default = False, repr=False)

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class EventOdds(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    regions: list[str] = Field(default="us", alias="region")
    markets: Optional[str] = Field(default="")
    dateFormat: Optional[list[str]] = Field(default="iso", alias="date_format", repr=False)
    oddsFormat: Optional[str] = Field(default="", alias="odds_format", repr=False)
    eventId: str = Field(..., alias="event_id")
    bookmakers: Optional[str] = Field(default="", alias="bookmaker", repr=False)
    commenceTimeFrom: Optional[str] = Field(default="", repr=False)
    commenceTimeTo: Optional[str] = Field(default="", repr=False)
    includeLinks: Optional[bool] = Field(default=False, repr=False)
    includeSids: Optional[bool] = Field(default=False, repr=False)
    includeBetLimits: Optional[bool] = Field(default=False, repr=False)
    includeRotationNumbers: Optional[bool] = Field(default=False, repr=False)
    includeMultipliers: Optional[bool] = Field(default=False, repr=False)

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class EventMarkets(BaseModel):
    sport: Sports = Field(..., alias="sport")
    eventId: str = Field(..., alias="event_id")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    regions: list[str] = Field(default="us", alias="region")
    bookmakers: Optional[str] = Field(default="", alias="bookmaker", repr=False)
    dateFormat: Optional[list[str]] = Field(default="iso", alias="date_format", repr=False)


    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class Participants(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class HistoricalOdds(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    regions: list[str] = Field(default="us", alias="region")
    markets: Optional[str] = Field(default="")
    dateFormat: Optional[list[str]] = Field(default="iso", alias="date_format", repr=False)
    oddsFormat: Optional[str] = Field(default="", alias="odds_format", repr=False)
    eventIds: Optional[list[str]] = Field(default="", alias="event_id", repr=False)
    bookmakers: Optional[str] = Field(default="", alias="bookmaker", repr=False)
    commenceTimeFrom: Optional[str] = Field(default="", repr=False)
    commenceTimeTo: Optional[str] = Field(default="", repr=False)
    includeLinks: Optional[bool] = Field(default=False, repr=False)
    includeSids: Optional[bool] = Field(default=False, repr=False)
    includeBetLimits: Optional[bool] = Field(default=False, repr=False)
    includeRotationNumbers: Optional[bool] = Field(default=False, repr=False)
    date: str = Field(..., alias="date")

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class HistoricalEvents(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    date: str = Field(..., alias="date")
    dateFormat: Optional[list[str]] = Field(default="iso", alias="date_format", repr=False)
    eventIds: Optional[list[str]] = Field(default="", alias="event_id", repr=False)
    commenceTimeFrom: Optional[str] = Field(default="", repr=False)
    commenceTimeTo: Optional[str] = Field(default="", repr=False)
    includeRotationNumbers: Optional[bool] = Field(default=False, repr=False)

    @model_validator(mode="before")
    def set_sport_from_enum(cls, values: dict) -> dict:
        # If someone passed a Sport instance, replace it with its key
        sport = values.get("sport")
        if isinstance(sport, Sport):
            values["sport"] = sport.key.value
        return values

class HistoricalEventOdds(BaseModel):
    sport: Sports = Field(..., alias="sport")
    api_key: str = Field(default=settings.odds_api_key, frozen=True, repr=False)
    regions: list[str] = Field(default="us", alias="region")
    eventId: str = Field(..., alias="event_id")
    date: str = Field(..., alias="date")
    markets: Optional[str] = Field(default="")
    dateFormat: Optional[list[str]] = Field(default="iso", alias="date_format", repr=False)
    oddsFormat: Optional[str] = Field(default="", alias="odds_format", repr=False)
    bookmakers: Optional[str] = Field(default="", alias="bookmaker", repr=False)
    commenceTimeFrom: Optional[str] = Field(default="", repr=False)
    commenceTimeTo: Optional[str] = Field(default="", repr=False)
    includeLinks: Optional[bool] = Field(default=False, repr=False)
    includeSids: Optional[bool] = Field(default=False, repr=False)
    includeBetLimits: Optional[bool] = Field(default=False, repr=False)
    includeRotationNumbers: Optional[bool] = Field(default=False, repr=False)
    includeMultipliers: Optional[bool] = Field(default=False, repr=False)
