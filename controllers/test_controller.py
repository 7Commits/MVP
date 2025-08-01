import pandas as pd
from typing import Dict, Tuple
import json
import uuid
from datetime import datetime
from models.test_result import TestResult


def load_results() -> pd.DataFrame:
    return TestResult.load_all()


def add_result(set_id: str, results_data: Dict) -> str:
    return TestResult.add(set_id, results_data)


def save_results(df: pd.DataFrame) -> None:
    TestResult.save_df(df)


def import_results_from_file(file) -> Tuple[bool, str]:
    """Importa risultati di test da un file JSON."""
    try:
        data = json.load(file)
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return False, "Il file JSON deve contenere un oggetto o una lista di risultati."

        results_df = load_results()
        added_count = 0

        for item in data:
            if not isinstance(item, dict):
                continue

            result_id = str(item.get('id', uuid.uuid4()))
            if result_id in results_df['id'].astype(str).values:
                continue

            set_id = str(item.get('set_id', ''))
            timestamp = str(item.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            results_content = item.get('results', {})

            new_row = {
                'id': result_id,
                'set_id': set_id,
                'timestamp': timestamp,
                'results': results_content if isinstance(results_content, dict) else {}
            }

            results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)
            added_count += 1

        if added_count > 0:
            save_results(results_df)
            message = f"Importati {added_count} risultati."
        else:
            message = "Nessun nuovo risultato importato."

        return True, message
    except Exception as e:
        return False, f"Errore durante l'importazione dei risultati: {str(e)}"
