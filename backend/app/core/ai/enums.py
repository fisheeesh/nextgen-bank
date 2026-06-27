from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Every transaction is going to analyzed and evaluated across multiple risk factors such as
Amount -> where we shall evalute both the absolute amount and amounts related to the user's history
Time -> where we shall consider the banking hours and unusual transaction times
Frequency -> where we shall monitor how often a transaction occurs
Pattern -> where we shall look for suspicious patterns like round numbers or repeated amounts
Velocity -> where we shall rack the total transactin volume in 24 hour period
"""


class AISettings(BaseSettings):
    RISK_SCORE_THRESHOLD: float = 0.7
    MODEL_VERSION: str = "1.0.0"
    ANALYSIS_WINDOW_DAYS: int = 90
    RISK_WEIGHTS: dict[str, float] = {
        # ? assigning 30% of the risk to the amount of the transaction
        "amount": 0.3,
        # ? 10% of the risk to the time of the day the transaction was made
        "time": 0.1,
        # ? 20% to frequency
        "frequency": 0.2,
        # ? a combination of the round amounts, repeat amounts and velocity of the amounts
        "pattern": 0.2,
        "velocity_amount": 0.2,
    }
    PATTERN_WEIGHTS: dict[str, float] = {
        "round_amounts": 0.2,
        "repeated_amounts": 0.2,
        "velocity": 0.6,
    }
    TIME_RISK_WEIGHTS: dict[str, float] = {
        "time_of_day": 0.7,
        "day_of_week": 0.3,
    }
    HIGH_AMOUNT_THRESHOLD: float = 10000.0
    VELOCITY_THRESHOLD: float = 50000.0
    # ? within a timeframe of 24 hours if the user makes more than 5 transactions then this value is gonna triggered
    FREQUENCE_THRESHOLD: int = 5
    HIGH_RISK_SCORE_THRESHOLD: float = 0.7
    BANK_HOURS_START: int = 9
    BANKING_HOURS_END: int = 17
    BANKING_HOURS_RISK: float = 0.1
    OFF_HOURS_RISK: float = 0.5
    LATE_HOURS_RISK: float = 0.9

    model_config = SettingsConfigDict(
        env_file="../../.envs/.env.local",
        env_ignore_empty=True,
        extra="ignore",
        env_prefix="AI_",
    )


ai_settings = AISettings()
