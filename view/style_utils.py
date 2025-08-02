"""Funzioni di utilità per applicare stili CSS nelle viste Streamlit.

Centralizza l'iniezione di CSS per favorirne il riuso tra le pagine.
"""

import streamlit as st


def add_global_styles():
    """Aggiunge stili globali all'applicazione."""
    st.markdown(
        """
    <style>
        /* Stile generale dell'app */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Stile dello sfondo per il contenuto principale */
        .main {
            background-color: #FAFBFF;
        }

        /* Stile dello sfondo per la barra laterale */
        .sidebar .sidebar-content {
            background-color: #F0F4FF;
        }

        /* Stile degli elementi di input */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"],
        .stMultiselect div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid #E0E5FF !important;
            background-color: white !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
            border-color: #4F6AF0 !important;
            box-shadow: 0 0 0 3px rgba(79, 106, 240, 0.2) !important;
        }

        /* Stile della casella di selezione */
        .stSelectbox,
        .stMultiselect {
            border-radius: 8px !important;
            width: 100% !important;
        }
        .stMultiselect span[data-baseweb="tag"] {
            max-width: 100%;
            white-space: normal !important;
            flex-wrap: wrap;
            overflow-wrap: anywhere;   /* optional safeguard for long tokens */
        }
        .stMultiselect span[data-baseweb="tag"] span {
            white-space: normal !important;
            word-break: break-word;
        }
        .stMultiselect .st-gz {
            max-width: none !important;
        }
        /* Consenti testo a capo all'interno di tutti i menu select */
        div[data-baseweb="select"] * {
            max-width: 100%;
            overflow-wrap: anywhere;  
            word-break: normal; 
        }
        div[data-baseweb="menu"] * {
            white-space: normal !important;
            word-break: break-word;
        }

        /* Stile dei pulsanti */
        .stButton > button {
            border-radius: 8px !important;
            border: 1px solid #4F6AF0 !important;
            background-color: #4F6AF0 !important;
            color: white !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            padding: 0.5rem 1rem !important;
            box-shadow: 0 2px 5px rgba(79, 106, 240, 0.2) !important;
        }

        .stButton > button:hover {
            background-color: #3A56E0 !important;
            box-shadow: 0 3px 10px rgba(79, 106, 240, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* Stile delle caselle di controllo e dei pulsanti di opzione */
        .stCheckbox label, .stRadio label {
            font-weight: 400 !important;
            color: #333333 !important;
        }

        .stCheckbox > div[role="radiogroup"] > label > div:first-child,
        .stRadio > div[role="radiogroup"] > label > div:first-child {
            background-color: white !important;
            border-color: #C0C9F1 !important;
        }

        /* Stile delle schede */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0 !important;
            background-color: #EAEEFF !important;
            color: #333333 !important;
            padding: 0.5rem 1rem !important;
            border: 1px solid #E0E5FF !important;
            border-bottom: none !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #4F6AF0 !important;
            font-weight: 600 !important;
            border-top: 2px solid #4F6AF0 !important;
        }

        /* Scheda con effetto ombra */
        .shadow-card {
            border-radius: 10px;
            background-color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def add_page_header(title: str, icon: str = "💡", description: str | None = None):
    """Aggiunge un'intestazione di pagina stilizzata."""
    add_global_styles()
    st.markdown(
        """
    <style>
        .page-header {
            margin-bottom: 1.5rem;
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(79, 106, 240, 0.1);
            border-left: 5px solid #4F6AF0;
        }
        .page-title {
            font-size: 2rem;
            font-weight: bold;
            color: #4F6AF0;
            margin-bottom: 0.5rem;
        }
        .page-description {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 0.5rem;
        }
        hr.header-divider {
            margin-top: 1rem;
            margin-bottom: 2rem;
            border: none;
            height: 1px;
            background: linear-gradient(to right, #4F6AF0, rgba(79, 106, 240, 0.1));
        }
        .section-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: #4F6AF0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(79, 106, 240, 0.2);
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        {f'<div class="page-description">{description}</div>' if description else ''}
    </div>
    <hr class="header-divider">
    """,
        unsafe_allow_html=True,
    )


def add_section_title(title: str, icon: str | None = None):
    """Aggiunge un titolo di sezione stilizzato."""
    icon_text = f"{icon} " if icon else ""
    st.markdown(
        f"<div class=\"section-title\">{icon_text}{title}</div>",
        unsafe_allow_html=True,
    )


def add_home_styles():
    """Applica gli stili CSS specifici della home page.

    Migliora la visibilità degli input nei temi chiaro e scuro e definisce
    l'aspetto degli elementi principali come box funzionali e sezioni di
    benvenuto.
    """
    st.markdown(
        """
    <style>
    /* TEMA SCURO: Input con sfondo CHIARO e testo NERO */
    [data-theme="dark"] div[data-testid="stTextInput"] input,
    .streamlit-dark div[data-testid="stTextInput"] input,
    [data-theme="dark"] div[data-baseweb="input"] input,
    .streamlit-dark div[data-baseweb="input"] input,
    [data-theme="dark"] div[data-testid="stTextArea"] textarea,
    .streamlit-dark div[data-testid="stTextArea"] textarea,
    [data-theme="dark"] div[data-baseweb="textarea"] textarea,
    .streamlit-dark div[data-baseweb="textarea"] textarea,
    [data-theme="dark"] div[data-testid="stNumberInput"] input,
    .streamlit-dark div[data-testid="stNumberInput"] input {
        color: #000000 !important; /* Testo NERO */
        background-color: #FFFFFF !important; /* Sfondo BIANCO */
        border: 1px solid #AAAAAA !important; /* Bordo grigio chiaro */
    }

    /* TEMA SCURO: Select box con testo NERO su sfondo BIANCO */
    /* Nota: lo stile dei select è più complesso da sovrascrivere completamente */
    [data-theme="dark"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .streamlit-dark div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #AAAAAA !important;
    }
    [data-theme="dark"] div[data-testid="stSelectbox"] svg,
    .streamlit-dark div[data-testid="stSelectbox"] svg {
        fill: #000000 !important; /* Icona freccia nera */
    }

    /* TEMA CHIARO: Input con sfondo BIANCO e testo NERO (standard) */
    [data-theme="light"] div[data-testid="stTextInput"] input,
    .streamlit-light div[data-testid="stTextInput"] input,
    [data-theme="light"] div[data-baseweb="input"] input,
    .streamlit-light div[data-baseweb="input"] input,
    [data-theme="light"] div[data-testid="stTextArea"] textarea,
    .streamlit-light div[data-testid="stTextArea"] textarea,
    [data-theme="light"] div[data-baseweb="textarea"] textarea,
    .streamlit-light div[data-baseweb="textarea"] textarea,
    [data-theme="light"] div[data-testid="stNumberInput"] input,
    .streamlit-light div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
    }

    [data-theme="light"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .streamlit-light div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
    }
    [data-theme="light"] div[data-testid="stSelectbox"] svg,
    .streamlit-light div[data-testid="stSelectbox"] svg {
        fill: #000000 !important;
    }

    /* Stili generali per tutti i componenti input (bordi, padding) */
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="textarea"] textarea,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 4px !important;
    }
    /* Mostra interamente il testo selezionato senza troncamento */
    div[data-baseweb="select"] * {
        white-space: normal !important;
    }

    /* Stili per i box delle funzionalità (mantenuti dal codice originale) */
    .feature-box {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        border-top: 4px solid #4F6AF0;
        box-shadow: 0 6px 18px rgba(79, 106, 240, 0.1);
        transition: all 0.3s ease;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(79, 106, 240, 0.15);
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: #333;
        display: flex;
        align-items: center;
    }
    .feature-description {
        font-size: 1rem;
        color: #555;
        line-height: 1.5;
    }
    .icon-large {
        font-size: 2rem;
        margin-right: 0.75rem;
        background: linear-gradient(135deg, #F0F4FF, #E6EBFF);
        width: 50px;
        height: 50px;
        line-height: 50px;
        text-align: center;
        border-radius: 50%;
        box-shadow: 0 4px 10px rgba(79, 106, 240, 0.1);
    }
    .welcome-section {
        margin-bottom: 2.5rem;
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4F6AF0;
    }
    .welcome-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #4F6AF0;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.3rem;
        color: #555;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .getting-started {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        border-left: 5px solid #4F6AF0;
    }
    .getting-started h3 {
        color: #4F6AF0;
        margin-bottom: 1rem;
    }
    .getting-started ol {
        padding-left: 1.5rem;
    }
    .getting-started li {
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
