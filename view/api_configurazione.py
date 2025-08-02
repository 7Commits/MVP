import streamlit as st

from controllers.openai_controller import test_api_connection
from view.style_utils import add_page_header, add_section_title
from controllers.api_preset_controller import (
    save_preset,
    delete_preset,
    load_presets,
    list_presets,
    get_preset_by_id,
    validate_preset,
    get_default_api_settings,
)

DEFAULT_API_SETTINGS = get_default_api_settings()
DEFAULT_MODEL = DEFAULT_API_SETTINGS["model"]
DEFAULT_ENDPOINT = DEFAULT_API_SETTINGS["endpoint"]


# Funzioni di callback per i pulsanti del form
def start_new_preset_edit():
    st.session_state.editing_preset = True
    st.session_state.current_preset_edit_id = None  # Indica nuovo preset
    st.session_state.preset_form_data = {
        "name": "",
        "endpoint": DEFAULT_ENDPOINT,
        "api_key": "",
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000
    }


def start_existing_preset_edit(preset_id):
    preset_to_edit = get_preset_by_id(preset_id, st.session_state.api_presets)
    if not preset_to_edit:
        st.error("Preset non trovato.")
        return
    st.session_state.editing_preset = True
    st.session_state.current_preset_edit_id = preset_id
    st.session_state.preset_form_data = preset_to_edit.copy()
    # Assicura che i campi numerici siano del tipo corretto per gli slider/number_input
    st.session_state.preset_form_data["temperature"] = float(
        st.session_state.preset_form_data.get("temperature", 0.0)
    )
    st.session_state.preset_form_data["max_tokens"] = int(
        st.session_state.preset_form_data.get("max_tokens", 1000)
    )
    if "endpoint" not in st.session_state.preset_form_data:
        st.session_state.preset_form_data["endpoint"] = DEFAULT_ENDPOINT


def cancel_preset_edit():
    st.session_state.editing_preset = False
    st.session_state.current_preset_edit_id = None
    st.session_state.preset_form_data = {}


def save_preset_from_form():
    """Salva un preset leggendo i valori direttamente dagli input della form."""
    # Recupera sempre i valori correnti dei widget dal session_state
    preset_name = st.session_state.get("preset_name", "").strip()
    endpoint = st.session_state.get("preset_endpoint", DEFAULT_ENDPOINT)
    api_key = st.session_state.get("preset_api_key", "")
    model = st.session_state.get("preset_model", DEFAULT_MODEL)
    temperature = float(
        st.session_state.get(
            "preset_temperature",
            st.session_state.preset_form_data.get("temperature", 0.0),
        )
    )
    max_tokens = int(
        st.session_state.get(
            "preset_max_tokens",
            st.session_state.preset_form_data.get("max_tokens", 1000),
        )
    )

    # Aggiorna il dizionario del form in sessione con i valori raccolti
    st.session_state.preset_form_data.update(
        {
            "name": preset_name,
            "endpoint": endpoint,
            "api_key": api_key,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    )

    form_data = st.session_state.preset_form_data.copy()
    current_id = st.session_state.current_preset_edit_id

    is_valid, validation_message = validate_preset(form_data, current_id)
    if not is_valid:
        st.error(validation_message)
        return

    success, message, updated_df = save_preset(form_data, current_id)
    if success:
        st.session_state.api_presets = updated_df
        st.success(message)
        cancel_preset_edit()  # Chiudi il form
    else:
        st.error(message)


def delete_preset_callback(preset_id):
    success, message, updated_df = delete_preset(preset_id)
    if success:
        st.session_state.api_presets = updated_df
        st.success(message)
        if st.session_state.current_preset_edit_id == preset_id:
            cancel_preset_edit()  # Se stavamo modificando il preset eliminato, chiudi il form
    else:
        st.error(message)


def render():
    add_page_header(
        "Gestione Preset API",
        icon="⚙️",
        description="Crea, visualizza, testa ed elimina i preset di configurazione API per LLM."
    )

    # Stato della sessione per la gestione del form di creazione/modifica preset
    if "editing_preset" not in st.session_state:
        st.session_state.editing_preset = False
    if "current_preset_edit_id" not in st.session_state:
        st.session_state.current_preset_edit_id = None  # None per nuovo, ID per modifica
    if "preset_form_data" not in st.session_state:
        st.session_state.preset_form_data = {}

    # Carica i preset API utilizzando la cache
    if 'api_presets' not in st.session_state:
        st.session_state.api_presets = load_presets()

    # Sezione per visualizzare/modificare i preset
    if st.session_state.editing_preset:
        add_section_title("Modifica/Crea Preset API", icon="✏️")
        form_data = st.session_state.preset_form_data

        with st.form(key="preset_form"):
            # Usa un key specifico per il campo nome e aggiorna il form_data
            form_data["name"] = st.text_input(
                "Nome del Preset",
                value=form_data.get("name", ""),
                key="preset_name",  # Key esplicita per il campo nome
                help="Un nome univoco per questo preset."
            )

            # Campo chiave API con key esplicita
            form_data["api_key"] = st.text_input(
                "Chiave API",
                value=form_data.get("api_key", ""),
                type="password",
                key="preset_api_key",  # Key esplicita per la chiave API
                help="La tua chiave API per il provider selezionato."
            )

            # Campo endpoint con key esplicita
            form_data["endpoint"] = st.text_input(
                "Provider Endpoint",
                value=form_data.get("endpoint", DEFAULT_ENDPOINT),
                placeholder="https://api.openai.com/v1",
                key="preset_endpoint",  # Key esplicita per l'endpoint
                help="Inserisci l'endpoint del provider API (es: https://api.openai.com/v1)"
            )

            # Modello sempre personalizzabile
            form_data["model"] = st.text_input(
                "Modello",
                value=form_data.get("model", DEFAULT_MODEL),
                placeholder="gpt-4o",
                key="preset_model",  # Key esplicita per il modello
                help="Inserisci il nome del modello (es: gpt-4o, claude-3-sonnet, ecc.)"
            )

            form_data["temperature"] = st.slider(
                "Temperatura",
                0.0,
                2.0,
                float(form_data.get("temperature", 0.0)),
                0.1,
                key="preset_temperature",
            )
            form_data["max_tokens"] = st.number_input(
                "Max Tokens",
                min_value=50,
                max_value=8000,
                value=int(form_data.get("max_tokens", 1000)),
                step=50,
                key="preset_max_tokens",
            )

            # Campo Test Connessione e pulsanti di salvataggio/annullamento
            # Pulsante Test Connessione
            if st.form_submit_button("⚡ Testa Connessione API"):
                # Usa direttamente i valori dal session_state per il test
                api_key_to_test = st.session_state.get("preset_api_key", "")
                endpoint_to_test = st.session_state.get("preset_endpoint", DEFAULT_ENDPOINT)
                model_to_test = st.session_state.get("preset_model", DEFAULT_MODEL)

                with st.spinner("Test in corso..."):
                    success, message = test_api_connection(
                        api_key=api_key_to_test,
                        endpoint=endpoint_to_test,
                        model=model_to_test,
                        temperature=form_data.get("temperature", 0.0),
                        max_tokens=form_data.get("max_tokens", 1000)
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

            # Pulsanti Salva e Annulla
            cols_form_buttons = st.columns(2)
            with cols_form_buttons[0]:
                if st.form_submit_button(
                    "💾 Salva Preset",
                    on_click=save_preset_from_form,
                    type="primary",
                    use_container_width=True,
                ):
                    pass  # Il callback gestisce il salvataggio
            with cols_form_buttons[1]:
                if st.form_submit_button(
                    "❌ Annulla",
                    on_click=cancel_preset_edit,
                    use_container_width=True,
                ):
                    pass  # Il callback gestisce il cambio di stato
    else:
        add_section_title("Preset API Salvati", icon="🗂️")
        if st.button("➕ Crea Nuovo Preset", on_click=start_new_preset_edit, use_container_width=True):
            pass  # Il callback gestisce il cambio di stato

        preset_list = list_presets(st.session_state.api_presets)
        if not preset_list:
            st.info(
                "Nessun preset API salvato. Clicca su 'Crea Nuovo Preset' per iniziare."
            )
        else:
            for preset in preset_list:
                with st.container():
                    st.markdown(f"#### {preset['name']}")
                    cols_preset_details = st.columns([3, 1, 1])
                    with cols_preset_details[0]:
                        st.caption(f"Modello: {preset.get('model', 'N/A')}")
                        st.caption(f"Endpoint: {preset.get('endpoint', 'N/A')}")
                    with cols_preset_details[1]:
                        if st.button(
                            "✏️ Modifica",
                            key=f"edit_{preset['id']}",
                            on_click=start_existing_preset_edit,
                            args=(preset['id'],),
                            use_container_width=True,
                        ):
                            pass
                    with cols_preset_details[2]:
                        if st.button(
                            "🗑️ Elimina",
                            key=f"delete_{preset['id']}",
                            on_click=delete_preset_callback,
                            args=(preset['id'],),
                            type="secondary",
                            use_container_width=True,
                        ):
                            pass
                    st.divider()

    # Mostra messaggi di conferma dopo il ricaricamento della pagina (se impostati dai callback)
    if "preset_applied_message" in st.session_state:  # Questo non dovrebbe più essere usato qui
        st.success(st.session_state.preset_applied_message)
        del st.session_state.preset_applied_message

    if "preset_saved_message" in st.session_state:
        st.success(st.session_state.preset_saved_message)
        del st.session_state.preset_saved_message

    if "preset_deleted_message" in st.session_state:
        st.success(st.session_state.preset_deleted_message)
        del st.session_state.preset_deleted_message
