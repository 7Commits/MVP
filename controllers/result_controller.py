import logging
from typing import Dict

import pandas as pd

from .test_controller import load_results
from .question_set_controller import load_sets
from .api_preset_controller import load_presets

logger = logging.getLogger(__name__)


def get_results(filter_set: str | None, filter_model: str | None) -> pd.DataFrame:
    """Carica i risultati e applica eventuali filtri per set e modello LLM."""
    df = load_results()

    if filter_set:
        sets_df = load_sets()
        set_ids = (
            sets_df[sets_df["name"] == filter_set]["id"].astype(str).tolist()
            if not sets_df.empty
            else []
        )
        df = df[df["set_id"].astype(str).isin(set_ids)]

    if filter_model:
        presets_df = load_presets()
        preset_models: Dict[str, str] = (
            presets_df.set_index("name")["model"].to_dict()
            if not presets_df.empty
            else {}
        )

        def matches_model(res: dict) -> bool:
            model = res.get("generation_llm")
            if not model:
                preset_name = res.get("generation_preset")
                model = preset_models.get(preset_name) if preset_name else None
            return model == filter_model

        df = df[df["results"].apply(matches_model)]

    return df


def list_set_names(results_df: pd.DataFrame, question_sets_df: pd.DataFrame) -> list[str]:
    """Elenca i nomi dei set disponibili nei risultati."""
    if results_df.empty or question_sets_df.empty:
        return []
    set_name_map = {
        str(row["id"]): row["name"]
        for row in question_sets_df.to_dict("records")
    }
    names = {set_name_map.get(str(sid), "Set Sconosciuto") for sid in results_df["set_id"]}
    return sorted(names)


def list_model_names(results_df: pd.DataFrame) -> list[str]:
    """Elenca i nomi dei modelli LLM presenti nei risultati."""
    if results_df.empty:
        return []
    presets_df = load_presets()
    preset_models: Dict[str, str] = (
        presets_df.set_index("name")["model"].to_dict() if not presets_df.empty else {}
    )
    models = set()
    for res in results_df["results"]:
        model = res.get("generation_llm")
        if not model and res.get("generation_preset"):
            model = preset_models.get(res.get("generation_preset"))
        if model:
            models.add(model)
    return sorted(models)


def prepare_select_options(
    results_df: pd.DataFrame, question_sets_df: pd.DataFrame
) -> Dict[str, str]:
    """Prepara le opzioni del selectbox dei risultati."""
    if results_df.empty:
        return {}
    set_name_map = {
        str(row["id"]): row["name"]
        for row in question_sets_df.to_dict("records")
    }
    processed = []
    for _, row in results_df.iterrows():
        result_data = row["results"]
        set_name = set_name_map.get(str(row["set_id"]), "Set Sconosciuto")
        avg_score = result_data.get("avg_score", 0)
        method = result_data.get("method", "N/A")
        method_icon = "🤖" if method == "LLM" else "📊"
        processed.append(
            {
                "id": row["id"],
                "display_name": f"{row['timestamp']} - {method_icon} {set_name} (Avg: {avg_score:.2f}%) - {method}",
            }
        )
    processed.sort(key=lambda x: x["display_name"].split(" - ")[0], reverse=True)
    return {p["id"]: p["display_name"] for p in processed}
