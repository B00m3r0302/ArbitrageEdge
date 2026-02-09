"""Application configuration."""
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings, NamedTuple

class Sport(NamedTuple):
    key: str
    group: str
    title: str
    description: str
    active: bool = False
    has_outrights: bool = False

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

    odds_api_key: str = Field(..., alias="ODDS_API_KEY")

    # Sports List
    sports = (
        "americanfootball_cfl",
        "americanfootball_ncaaf",
        "americanfootball_ncaaf_championship_winner",
        "americanfootball_nfl",
        "americanfootball_nfl_preseason",
        "americanfootball_nfl_super_bowl_winner",
        "americanfootball_ufl", "baseball_milb",
        "baseball_mlb", "baseball_mlb_preseason",
        "baseball_mlb_world_series_winner",
        "baseball_ncaa", "basketball_nba",
        "basketball_nba_championship_winner",
        "basketball_nba_preseason",
        "basketball_nba_summer_league",
        "basketball_ncaab",
        "basketball_ncaab_championship_winner",
        "boxing_boxing",
        "golf_masters_tournament_winner",
        "golf_pga_championship_winner",
        "golf_the_open_championship_winner",
        "golf_us_open_winner",
        "icehockey_nhl",
        "icehockey_nhl_championship_winner",
        "icehockey_nhl_preseason",
        "mma_mixed_martial_arts",
        "politics_us_presidential_election_winner",
        "rugbyleague_nrl",
        "rugbyleague_nrl_state_of_origin",
        "rugbyunion_six_nations",
        "soccer_africa_cup_of_nations",
        "soccer_concacaf_gold_cup",
        "soccer_concacaf_leagues_cup",
        "soccer_efl_champ",
        "soccer_england_efl_cup",
        "soccer_epl",
        "soccer_fa_cup",
        "soccer_fifa_club_world_cup",
        "soccer_fifa_world_cup",
        "soccer_fifa_world_cup_qualifiers_europe",
        "soccer_fifa_world_cup_qualifiers_south_america",
        "soccer_fifa_world_cup_winner",
        "soccer_fifa_world_cup_womens",
        "soccer_france_ligue_one",
        "soccer_germany_bundesliga",
        "soccer_italy_serie_a",
        "soccer_spain_la_liga",
        "soccer_uefa_champs_league",
        "soccer_uefa_champs_league_qualification",
        "soccer_uefa_euro_qualification",
        "soccer_uefa_europa_conference_league",
        "soccer_uefa_europa_league",
        "soccer_uefa_european_championship",
        "soccer_uefa_nations_league",
        "soccer_usa_mls",
        "tennis_atp_aus_open_singles",
        "tennis_atp_canadian_open",
        "tennis_atp_china_open",
        "tennis_atp_cincinnati_open",
        "tennis_atp_dubai",
        "tennis_atp_french_open",
        "tennis_atp_indian_wells",
        "tennis_atp_italian_open",
        "tennis_atp_madrid_open",
        "tennis_atp_miami_open",
        "tennis_atp_monte_carlo_masters",
        "tennis_atp_paris_masters",
        "tennis_atp_qatar_open",
        "tennis_atp_shanghai_masters",
        "tennis_atp_us_open",
        "tennis_atp_wimbledon",
        "tennis_wta_aus_open_singles",
        "tennis_wta_canadian_open",
        "tennis_wta_china_open",
        "tennis_wta_cincinnati_open",
        "tennis_wta_dubai",
        "tennis_wta_french_open",
        "tennis_wta_indian_wells",
        "tennis_wta_italian_open",
        "tennis_wta_madrid_open",
        "tennis_wta_miami_open",
        "tennis_wta_qatar_open",
        "tennis_wta_us_open",
        "tennis_wta_wimbledon",
        "tennis_wta_wuhan_open"
    )

settings = Settings()