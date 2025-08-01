import pandas as pd
from models.api_preset import APIPreset


def load_presets() -> pd.DataFrame:
    return APIPreset.load_all()


def save_presets(df: pd.DataFrame) -> None:
    APIPreset.save_df(df)


def delete_preset(preset_id: str) -> None:
    APIPreset.delete(preset_id)
