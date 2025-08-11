import pandas as pd
from typing import Any, Dict, List, Tuple


def format_questions_for_view(
    questions_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, str]], List[str]]:
    """Normalizza il DataFrame delle domande per la visualizzazione.

    Garantisce che la colonna ``categoria`` esista e sia riempita con ``N/A`` quando
    mancante. Restituisce il DataFrame normalizzato, una mappa degli ID delle domande
    ai rispettivi testi e categorie e l'elenco ordinato delle categorie.
    """
    if questions_df is None or questions_df.empty:
        df = pd.DataFrame(columns=["id", "domanda", "risposta_attesa", "categoria"])
        categories: List[str] = []
    else:
        df = questions_df.copy()
        if "categoria" not in df.columns:
            df["categoria"] = "N/A"
        else:
            df["categoria"] = df["categoria"].fillna("N/A")
        categories = sorted(list(df["categoria"].astype(str).unique()))

    question_map: Dict[str, Dict[str, str]] = {
        str(row.get("id", "")): {
            "domanda": row.get("domanda", ""),
            "categoria": row.get("categoria", "N/A"),
        }
        for _, row in df.iterrows()
    }

    return df, question_map, categories


def build_questions_detail(
    question_map: Dict[str, Dict[str, str]],
    q_ids: Any,
) -> List[Dict[str, str]]:
    """Restituisce i dettagli delle domande per ``q_ids`` usando ``question_map``.

    Ogni elemento della lista restituita contiene ``id``, ``domanda`` e ``categoria``
    della domanda. Gli ID non corrispondenti producono testo vuoto con categoria
    ``N/A``. Se ``q_ids`` non è una lista, viene restituita una lista vuota.
    """

    details: List[Dict[str, str]] = []
    if isinstance(q_ids, list):
        for q_id in q_ids:
            info = question_map.get(str(q_id), {})
            details.append(
                {
                    "id": str(q_id),
                    "domanda": info.get("domanda", ""),
                    "categoria": info.get("categoria", "N/A"),
                }
            )
    return details
