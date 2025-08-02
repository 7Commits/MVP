from dataclasses import dataclass


@dataclass
class SetPageState:
    """Transient UI state for the question set management page."""

    save_set_success: bool = False
    save_set_success_message: str = "Set aggiornato con successo!"
    save_set_error: bool = False
    save_set_error_message: str = "Errore durante l'aggiornamento del set."

    delete_set_success: bool = False
    delete_set_success_message: str = "Set eliminato con successo!"

    create_set_success: bool = False
    create_set_success_message: str = "Set creato con successo!"

    import_set_success: bool = False
    import_set_success_message: str = "Importazione completata con successo!"
    import_set_error: bool = False
    import_set_error_message: str = "Errore durante l'importazione."

    trigger_rerun: bool = False


@dataclass
class QuestionPageState:
    """Transient UI state for the question management page."""

    save_success: bool = False
    save_success_message: str = "Domanda aggiornata con successo!"
    save_error: bool = False
    save_error_message: str = "Impossibile aggiornare la domanda."

    delete_success: bool = False
    delete_success_message: str = "Domanda eliminata con successo!"

    add_success: bool = False
    add_success_message: str = "Domanda aggiunta con successo!"

    import_success: bool = False
    import_success_message: str = "Importazione completata con successo!"
    import_error: bool = False
    import_error_message: str = "Errore durante l'importazione."

    trigger_rerun: bool = False
