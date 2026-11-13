"""HGrid247 AI Assistant - Streamlit web interface."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from core.config import (
    GEMINI_MODEL,
    MAX_HISTORY_MESSAGES,
    QDRANT_COLLECTION,
    QDRANT_URL,
    SIMILARITY_TOP_K,
)
from core.rag import get_llm, get_vector_store, tanya_hgrid_with_memory_stream


PROJECT_ROOT = Path(__file__).resolve().parent


def font_data_uri(filename: str) -> str:
    font_path = PROJECT_ROOT / "assets" / "fonts" / filename
    encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
    return f"data:font/ttf;base64,{encoded}"


DISPLAY_FONT_REGULAR = font_data_uri("DejaVuSansCondensed.ttf")
DISPLAY_FONT_BOLD = font_data_uri("DejaVuSansCondensed-Bold.ttf")


st.set_page_config(
    page_title="HGrid247 AI Assistant",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<!--
THESIS: A glass RAG workbench where the question composer, retrieval state, and source evidence stay visible in the first operating surface.
OWN-WORLD: Pale lavender canvas, frosted command glass, restrained violet action, and cyan source evidence.
STORY: The user opens the assistant, asks a HGrid247 question, watches retrieval resolve, reads the answer, then audits source chunks.
FIRST VIEWPORT: Rounded glass app shell, compact nav, centered assistant identity, wide composer, quick prompt chips, and compact retrieval status.
FORM: Frosted HGrid247 command composer, no landing-page detour, no generic chatbot clone.
FINISH: checked with compile, detector, health, and responsive screenshots when available.
-->
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
    @font-face {
        font-family: "HGrid Condensed";
        src: url("__DISPLAY_FONT_REGULAR__") format("truetype");
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: "HGrid Condensed";
        src: url("__DISPLAY_FONT_BOLD__") format("truetype");
        font-weight: 700;
        font-style: normal;
        font-display: swap;
    }

    :root {
        --canvas: #f6f1fb;
        --canvas-deep: #e7dbf4;
        --glass: rgba(252, 249, 255, 0.52);
        --glass-strong: rgba(252, 249, 255, 0.78);
        --glass-border: rgba(255, 255, 255, 0.48);
        --text-main: #262033;
        --text-muted: #665d78;
        --accent: #8c64d9;
        --accent-strong: #6f38c9;
        --source: #23788b;
        --warning: #a66c21;
        --shadow-soft: 0 28px 90px rgba(117, 96, 149, 0.26);
        --shadow-panel: 0 16px 42px rgba(104, 86, 134, 0.15);
        --text-on-accent: #fbf7ff;
        --surface-solid: #fbf7ff;
        --line-soft: rgba(107, 91, 137, 0.18);
        --source-soft: rgba(35, 120, 139, 0.12);
        --warning-soft: rgba(166, 108, 33, 0.12);
        --scroll-track: #eee6f8;
        --scroll-thumb: #9b8bb9;
    }

    html, body, [data-testid="stAppViewContainer"] {
        min-height: 100dvh;
        background:
            radial-gradient(circle at 50% 24%, rgba(140, 100, 217, 0.24), transparent 23rem),
            radial-gradient(circle at 12% 8%, rgba(35, 120, 139, 0.09), transparent 18rem),
            linear-gradient(180deg, var(--canvas) 0%, var(--canvas-deep) 100%);
        color: var(--text-main);
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", "Helvetica Neue", sans-serif;
        overflow-x: hidden;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }

    [data-testid="stHeader"] {
        display: none;
        background: transparent;
    }

    #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    div[role="status"]:has(button[aria-label="Close"]),
    .stDeployButton {
        display: none !important;
    }

    .block-container {
        max-width: min(1180px, calc(100vw - 2rem));
        min-height: calc(100dvh - 2.5rem);
        margin: 1.25rem auto;
        padding: 1rem 1rem 5.5rem;
        border: 1px solid var(--glass-border);
        border-radius: 28px;
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.44), rgba(247, 241, 255, 0.32)),
            var(--canvas);
        box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255, 255, 255, 0.62);
        backdrop-filter: blur(26px) saturate(158%);
        -webkit-backdrop-filter: blur(26px) saturate(158%);
        overflow: hidden;
    }

    .block-container p,
    .block-container li,
    .block-container div {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(252, 249, 255, 0.88), rgba(240, 231, 251, 0.82)),
            var(--canvas);
        border-right: 1px solid var(--glass-border);
        box-shadow: 18px 0 60px rgba(102, 83, 132, 0.12);
        backdrop-filter: blur(18px) saturate(145%);
        -webkit-backdrop-filter: blur(18px) saturate(145%);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--text-muted);
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--line-soft);
    }

    [data-testid="stSidebar"] button {
        min-height: 2.75rem;
        border-radius: 999px;
        border: 1px solid var(--glass-border);
        background:
            linear-gradient(135deg, rgba(255, 255, 255, 0.58), rgba(247, 241, 255, 0.4)),
            var(--glass);
        color: var(--text-main);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.52);
        transition: transform 140ms ease-out, border-color 140ms ease-out, background-color 140ms ease-out, box-shadow 140ms ease-out;
    }

    [data-testid="stSidebar"] button p {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] button:hover {
        border-color: rgba(111, 56, 201, 0.36);
        background: rgba(255, 255, 255, 0.62);
        transform: translateY(-1px);
    }

    [data-testid="stSidebar"] button:active {
        transform: translateY(1px) scale(0.99);
    }

    .glass-shell {
        position: relative;
        overflow: hidden;
        min-height: 28rem;
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.38), rgba(246, 238, 255, 0.24)),
            rgba(250, 246, 255, 0.36);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
    }

    .glass-shell::before {
        content: "";
        position: absolute;
        inset: 4.5rem 8% auto;
        height: 25rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(140, 100, 217, 0.34) 0%, rgba(140, 100, 217, 0.16) 36%, transparent 72%);
        filter: blur(18px);
        pointer-events: none;
    }

    .glass-shell::after {
        content: "";
        position: absolute;
        inset: auto 10% 1.25rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.72), transparent);
        pointer-events: none;
    }

    .glass-nav {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: minmax(160px, 1fr) auto minmax(170px, 1fr);
        align-items: center;
        gap: 1rem;
        min-height: 3.5rem;
        margin: 0.65rem;
        padding: 0.42rem 0.55rem;
        border: 1px solid var(--glass-border);
        border-radius: 18px;
        background:
            linear-gradient(135deg, rgba(255, 255, 255, 0.58), rgba(248, 242, 255, 0.36)),
            var(--glass);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.58), 0 12px 34px rgba(111, 88, 145, 0.12);
        backdrop-filter: blur(22px) saturate(160%);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
    }

    .brand-lockup,
    .nav-links,
    .nav-tools,
    .composer-toolbar,
    .source-strip {
        display: flex;
        align-items: center;
    }

    .brand-lockup {
        gap: 0.6rem;
        min-width: 0;
        font-weight: 760;
        color: var(--text-main);
    }

    .brand-mark,
    .assistant-mark {
        display: inline-grid;
        place-items: center;
        flex: 0 0 auto;
        border: 1px solid rgba(255, 255, 255, 0.58);
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.58), rgba(140, 100, 217, 0.18)),
            rgba(250, 246, 255, 0.5);
        color: var(--accent-strong);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.64), 0 12px 28px rgba(111, 56, 201, 0.18);
        font-family: "HGrid Condensed", "DejaVu Sans Condensed", "Liberation Sans Narrow", sans-serif;
        font-weight: 900;
        letter-spacing: 0;
    }

    .brand-mark {
        width: 2.35rem;
        height: 2.35rem;
        border-radius: 50%;
        font-size: 1.05rem;
    }

    .nav-links {
        justify-content: center;
        gap: 0.3rem;
    }

    .nav-pill {
        display: inline-flex;
        align-items: center;
        min-height: 2.35rem;
        padding: 0 0.68rem;
        border-radius: 999px;
        color: var(--text-muted);
        font-size: 0.78rem;
        font-weight: 680;
        letter-spacing: 0;
        white-space: nowrap;
    }

    .nav-pill.is-active {
        background: rgba(111, 56, 201, 0.12);
        color: var(--accent-strong);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.44);
    }

    .nav-tools {
        justify-content: flex-end;
        gap: 0.5rem;
        min-width: 0;
    }

    .nav-status,
    .nav-search {
        min-height: 2.35rem;
        border: 1px solid var(--glass-border);
        background: rgba(255, 255, 255, 0.34);
        color: var(--text-muted);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.44);
    }

    .nav-status {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        max-width: 11rem;
        padding: 0 0.68rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 680;
        white-space: nowrap;
    }

    .status-dot {
        width: 0.48rem;
        height: 0.48rem;
        border-radius: 50%;
        background: var(--source);
        box-shadow: 0 0 0 4px rgba(35, 120, 139, 0.12);
    }

    .status-dot.is-warning {
        background: var(--warning);
        box-shadow: 0 0 0 4px rgba(166, 108, 33, 0.12);
    }

    .nav-search {
        position: relative;
        display: inline-flex;
        align-items: center;
        width: 9.5rem;
        padding: 0 0.75rem 0 2rem;
        border-radius: 999px;
        overflow: hidden;
        font-size: 0.73rem;
    }

    .nav-search::before {
        content: "";
        position: absolute;
        left: 0.78rem;
        width: 0.62rem;
        height: 0.62rem;
        border: 1.5px solid var(--text-muted);
        border-radius: 50%;
    }

    .nav-search::after {
        content: "";
        position: absolute;
        left: 1.27rem;
        width: 0.36rem;
        height: 1.5px;
        background: var(--text-muted);
        transform: rotate(45deg);
        transform-origin: left center;
    }

    .assistant-stage {
        position: relative;
        z-index: 1;
        display: flex;
        min-height: 20rem;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3.6rem 1.25rem 2.4rem;
        text-align: center;
    }

    .assistant-mark {
        width: 3rem;
        height: 3rem;
        border-radius: 1.05rem;
        margin-bottom: 0.9rem;
        font-size: 1.35rem;
    }

    .assistant-stage h1 {
        max-width: 15ch;
        margin: 0;
        color: var(--text-main);
        font-family: "HGrid Condensed", "DejaVu Sans Condensed", "Liberation Sans Narrow", sans-serif;
        font-size: clamp(2.15rem, 5vw, 4.25rem);
        font-weight: 900;
        line-height: 0.96;
        letter-spacing: 0;
    }

    .assistant-stage p {
        max-width: 54ch;
        margin: 0.85rem auto 0;
        color: var(--text-muted);
        font-size: 0.98rem;
        line-height: 1.6;
    }

    .glass-panel,
    .glass-composer,
    [data-testid="stForm"],
    .status-glass,
    .source-glass {
        border: 1px solid var(--glass-border);
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.5), rgba(247, 241, 255, 0.34)),
            var(--glass);
        box-shadow: var(--shadow-panel), inset 0 1px 0 rgba(255, 255, 255, 0.56);
        backdrop-filter: blur(22px) saturate(160%);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
    }

    [data-testid="stForm"] {
        max-width: 820px;
        margin: -3rem auto 0.65rem;
        padding: 0.8rem;
        border-radius: 23px;
    }

    [data-testid="stTextArea"] textarea {
        min-height: 5.8rem;
        padding: 0.92rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.54);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.3);
        color: var(--text-main);
        font-size: 0.97rem;
        line-height: 1.55;
        caret-color: var(--accent-strong);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.48);
        resize: vertical;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #756b87;
        opacity: 1;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(111, 56, 201, 0.54);
        box-shadow: 0 0 0 3px rgba(111, 56, 201, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.58);
    }

    .composer-toolbar {
        flex-wrap: wrap;
        gap: 0.45rem;
        padding: 0.1rem 0 0;
    }

    .glass-chip,
    .source-pill,
    div[data-testid="stButton"] button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 2.75rem;
        border: 1px solid var(--glass-border);
        border-radius: 999px;
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.46), rgba(248, 243, 255, 0.34)),
            rgba(252, 249, 255, 0.34);
        color: var(--text-main);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
        font-size: 0.78rem;
        font-weight: 680;
        line-height: 1.25;
        white-space: nowrap;
        transition: transform 140ms ease-out, border-color 140ms ease-out, background-color 140ms ease-out, box-shadow 140ms ease-out;
    }

    .glass-chip {
        padding: 0 0.72rem;
        min-height: 2rem;
        color: var(--text-muted);
    }

    div[data-testid="stButton"] button:hover {
        border-color: rgba(111, 56, 201, 0.34);
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(117, 96, 149, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.58);
    }

    div[data-testid="stButton"] button:active {
        transform: translateY(1px) scale(0.99);
    }

    .glass-action,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stForm"] button[kind="primary"] {
        min-height: 2.85rem;
        border: 1px solid rgba(255, 255, 255, 0.42) !important;
        border-radius: 999px !important;
        background:
            linear-gradient(145deg, var(--accent), var(--accent-strong)) !important;
        color: var(--text-on-accent) !important;
        box-shadow: 0 14px 34px rgba(111, 56, 201, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.34) !important;
        font-weight: 800 !important;
        white-space: nowrap;
        transition: transform 140ms ease-out, box-shadow 140ms ease-out, filter 140ms ease-out;
    }

    [data-testid="stFormSubmitButton"] button p {
        color: var(--text-on-accent) !important;
        white-space: nowrap;
    }

    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stForm"] button[kind="primary"]:hover {
        transform: translateY(-1px);
        filter: saturate(1.06);
        box-shadow: 0 17px 38px rgba(111, 56, 201, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.38) !important;
    }

    [data-testid="stFormSubmitButton"] button:active,
    [data-testid="stForm"] button[kind="primary"]:active {
        transform: translateY(1px) scale(0.99);
    }

    button:disabled,
    [data-testid="stFormSubmitButton"] button:disabled {
        cursor: not-allowed;
        filter: saturate(0.65);
        opacity: 0.58;
        transform: none;
    }

    .quick-chip-caption {
        max-width: 820px;
        margin: 0.2rem auto 0.38rem;
        color: var(--text-muted);
        font-size: 0.74rem;
        font-weight: 700;
    }

    .status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 1rem 0 1rem;
    }

    .status-cell {
        min-height: 5.1rem;
        border-radius: 18px;
        padding: 0.82rem 0.9rem;
    }

    .status-cell span {
        display: block;
        margin-bottom: 0.34rem;
        color: var(--text-muted);
        font-size: 0.73rem;
        font-weight: 740;
        letter-spacing: 0;
    }

    .status-cell strong {
        display: block;
        color: var(--text-main);
        font-size: 0.93rem;
        font-weight: 780;
        line-height: 1.25;
        overflow-wrap: anywhere;
    }

    .empty-state {
        margin: 0.7rem 0 1rem;
        border-radius: 18px;
        padding: 1rem 1.05rem;
        color: var(--text-muted);
        line-height: 1.58;
    }

    .resolution-steps {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.55rem;
    }

    .resolution-rail {
        margin: 0.15rem 0 0.9rem;
        border-radius: 18px;
        padding: 0.72rem;
    }

    .resolution-step {
        position: relative;
        min-height: 4.25rem;
        border: 1px solid rgba(255, 255, 255, 0.42);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.28);
        padding: 0.64rem;
    }

    .resolution-step::before {
        content: "";
        display: block;
        width: 100%;
        height: 3px;
        border-radius: 999px;
        margin-bottom: 0.48rem;
        background: rgba(102, 93, 120, 0.28);
    }

    .resolution-step.is-active::before,
    .resolution-step.is-complete::before {
        background: var(--accent-strong);
    }

    .resolution-step strong {
        display: block;
        color: var(--text-main);
        font-size: 0.83rem;
        font-weight: 760;
        line-height: 1.25;
    }

    .resolution-step span {
        color: var(--text-muted);
        font-size: 0.74rem;
    }

    .source-strip {
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.8rem;
    }

    .source-pill {
        min-height: 1.95rem;
        border-color: rgba(35, 120, 139, 0.22);
        background: var(--source-soft);
        color: #185c6b;
        padding: 0 0.68rem;
    }

    .source-panel {
        margin-top: 0.75rem;
        border-radius: 16px;
        padding: 0.78rem;
    }

    .source-panel-label {
        margin-bottom: 0.32rem;
        color: var(--text-muted);
        font-size: 0.74rem;
        font-weight: 760;
        letter-spacing: 0;
    }

    .source-list {
        display: grid;
        gap: 0.28rem;
    }

    .source-link {
        display: block;
        border-radius: 12px;
        padding: 0.58rem 0.66rem;
        color: #185c6b;
        background: rgba(255, 255, 255, 0.26);
        text-decoration: underline;
        text-decoration-thickness: 1px;
        text-underline-offset: 0.24em;
        overflow-wrap: anywhere;
        transition: background-color 120ms ease-out, color 120ms ease-out;
    }

    .source-link:hover {
        background: rgba(35, 120, 139, 0.12);
        color: #124d5b;
    }

    .chunk-preview {
        border-top: 1px solid rgba(107, 91, 137, 0.14);
        padding: 0.75rem 0;
        color: var(--text-muted);
        line-height: 1.55;
    }

    .chunk-preview b {
        color: var(--text-main);
    }

    [data-testid="stChatMessage"] {
        max-width: 74ch;
        margin-bottom: 0.85rem;
        border: 1px solid var(--glass-border);
        border-radius: 18px;
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.46), rgba(247, 241, 255, 0.3)),
            var(--glass);
        box-shadow: 0 12px 34px rgba(104, 86, 134, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.52);
        backdrop-filter: blur(18px) saturate(145%);
        -webkit-backdrop-filter: blur(18px) saturate(145%);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        line-height: 1.62;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
        color: var(--text-main);
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.32);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.42);
    }

    .warning-panel {
        border-color: rgba(166, 108, 33, 0.28);
        border-radius: 18px;
        padding: 1rem;
        margin: 0.5rem 0 1rem;
        background:
            linear-gradient(145deg, rgba(255, 255, 255, 0.54), rgba(255, 244, 228, 0.34)),
            var(--warning-soft);
    }

    .warning-panel strong {
        display: block;
        color: #6e4515;
        margin-bottom: 0.35rem;
    }

    .warning-panel p {
        max-width: 70ch;
        margin: 0;
        color: #5f4b34;
        line-height: 1.55;
    }

    button:focus-visible,
    a:focus-visible,
    textarea:focus-visible {
        outline: 3px solid rgba(111, 56, 201, 0.44);
        outline-offset: 2px;
    }

    ::selection {
        background: rgba(140, 100, 217, 0.24);
        color: var(--text-main);
    }

    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    ::-webkit-scrollbar-track {
        background: var(--scroll-track);
    }

    ::-webkit-scrollbar-thumb {
        border: 3px solid var(--scroll-track);
        border-radius: 999px;
        background: var(--scroll-thumb);
    }

    @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
        .glass-panel,
        .glass-composer,
        [data-testid="stForm"],
        .glass-nav,
        .status-glass,
        .source-glass {
            background: rgba(250, 247, 255, 0.96);
        }
    }

    @media (prefers-reduced-transparency: reduce) {
        .glass-panel,
        .glass-composer,
        [data-testid="stForm"],
        .glass-nav,
        .status-glass,
        .source-glass {
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
            background: rgba(250, 247, 255, 0.96);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 760px) {
        .block-container {
            max-width: calc(100vw - 0.75rem);
            min-height: calc(100dvh - 0.75rem);
            margin: 0.38rem auto;
            padding: 0.5rem 0.5rem 4.5rem;
            border-radius: 18px;
        }

        .glass-shell {
            min-height: 25rem;
            border-radius: 16px;
        }

        .glass-shell::before {
            inset: 4.5rem -15% auto;
            height: 19rem;
        }

        .glass-nav {
            grid-template-columns: 1fr;
            gap: 0.45rem;
            align-items: stretch;
            min-height: 0;
            margin: 0.4rem;
            padding: 0.5rem;
            border-radius: 14px;
        }

        .brand-lockup,
        .nav-links,
        .nav-tools {
            justify-content: space-between;
        }

        .nav-links {
            overflow-x: auto;
            justify-content: flex-start;
            padding-bottom: 0.1rem;
        }

        .nav-tools {
            justify-content: flex-start;
            flex-wrap: wrap;
        }

        .nav-search {
            width: 100%;
        }

        .assistant-stage {
            min-height: 17.8rem;
            padding: 2.2rem 0.85rem 2rem;
        }

        .assistant-mark {
            width: 2.7rem;
            height: 2.7rem;
            border-radius: 0.92rem;
        }

        .assistant-stage h1 {
            max-width: 13ch;
            font-size: 2.25rem;
            line-height: 0.98;
        }

        .assistant-stage p {
            margin-top: 0.65rem;
            font-size: 0.88rem;
            line-height: 1.45;
        }

        [data-testid="stForm"] {
            margin-top: -2.45rem;
            padding: 0.62rem;
            border-radius: 18px;
        }

        [data-testid="stTextArea"] textarea {
            min-height: 6.2rem;
            font-size: 0.92rem;
            border-radius: 14px;
        }

        div[data-testid="column"] {
            min-width: 0 !important;
        }

        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
        }

        .status-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.75rem 0 0.75rem;
        }

        .status-cell {
            min-height: 4.4rem;
            border-radius: 14px;
            padding: 0.65rem 0.7rem;
        }

        .status-cell span {
            margin-bottom: 0.2rem;
            font-size: 0.68rem;
        }

        .status-cell strong {
            font-size: 0.84rem;
        }

        .empty-state {
            margin: 0.5rem 0 0.7rem;
            padding: 0.68rem 0.78rem;
            line-height: 1.35;
        }

        .resolution-steps {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .resolution-step {
            min-height: 4rem;
        }
    }

    @media (max-width: 460px) {
        .status-grid,
        .resolution-steps {
            grid-template-columns: 1fr;
        }

        .nav-pill {
            min-height: 2.5rem;
        }

        .source-panel {
            padding: 0.62rem;
        }
    }


    /* Modern bottom chat redesign */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    .glass-shell,
    .quick-chip-caption,
    .status-grid {
        display: none !important;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        min-height: 100dvh !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 50% -18%, rgba(118, 112, 132, 0.08), transparent 26rem),
            linear-gradient(180deg, #f8f7fa 0%, #f0eef4 100%) !important;
    }

    .block-container {
        width: 100% !important;
        max-width: min(760px, calc(100vw - 2rem)) !important;
        min-height: 100dvh !important;
        margin: 0 auto !important;
        padding: clamp(1rem, 3vw, 2rem) 1rem 19rem !important;
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        overflow: visible !important;
    }

    .empty-state {
        max-width: 720px;
        margin: min(18vh, 7rem) auto 0 !important;
        border: 1px dashed rgba(103, 91, 128, 0.2) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.58) !important;
        box-shadow: none !important;
        color: var(--text-muted) !important;
        text-align: center;
    }

    .st-key-chat_history_view {
        width: 100%;
        min-height: calc(100dvh - 15rem);
        padding: clamp(0.75rem, 2vw, 1.4rem) 0 2rem;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 0.52rem !important;
        width: fit-content !important;
        max-width: min(82%, 720px) !important;
        margin: 0 0 1.05rem !important;
        padding: 0.78rem 0.86rem !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important;
        background: rgba(247, 246, 250, 0.78) !important;
        box-shadow:
            8px 10px 26px rgba(87, 80, 104, 0.1),
            -8px -8px 22px rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(12px) saturate(115%);
        -webkit-backdrop-filter: blur(12px) saturate(115%);
        overflow-wrap: anywhere;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        max-width: min(78%, 680px) !important;
        flex-direction: row !important;
        align-items: flex-start !important;
        gap: 0.55rem !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        border-color: rgba(255, 255, 255, 0.66) !important;
        border-radius: 20px 20px 6px 20px !important;
        background: rgba(235, 232, 242, 0.92) !important;
        box-shadow:
            7px 9px 22px rgba(87, 80, 104, 0.1),
            -6px -6px 18px rgba(255, 255, 255, 0.62) !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageAvatarCustom"] {
        flex: 0 0 auto !important;
        align-self: flex-start !important;
        margin-top: 0.04rem !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] {
        flex: 1 1 auto !important;
        width: auto !important;
        padding-top: 0.16rem !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
        margin-left: 0 !important;
        margin-right: auto !important;
        border-radius: 20px 20px 20px 6px !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        font-size: 0.98rem !important;
        line-height: 1.72 !important;
        overflow-wrap: anywhere;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"] p {
        margin-bottom: 0.55rem;
    }

    .st-key-chat_history_view [data-testid="stChatMessage"] p:last-child {
        margin-bottom: 0;
    }

    .st-key-chat_history_view [data-testid="stChatMessageAvatarCustom"] {
        width: 1.75rem !important;
        height: 1.75rem !important;
        margin: 0 !important;
        align-self: flex-start !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessageAvatarCustom"] span {
        width: 1.75rem !important;
        height: 1.75rem !important;
        min-width: 1.75rem !important;
        min-height: 1.75rem !important;
        display: inline-grid !important;
        place-items: center !important;
    }

    .st-key-chat_history_view [data-testid="stChatMessageContent"] {
        width: 100% !important;
        max-width: none !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    #chat-bottom-anchor {
        display: block;
        min-height: 7rem;
        height: 7rem;
    }

    .resolution-rail {
        border-radius: 14px !important;
        background: rgba(246, 241, 252, 0.72) !important;
        box-shadow: none !important;
    }

    .source-panel,
    [data-testid="stExpander"] {
        background: rgba(246, 251, 253, 0.78) !important;
        border-color: rgba(35, 120, 139, 0.18) !important;
        box-shadow: none !important;
    }

    .focus-status {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        max-width: 760px;
        margin: 0 auto;
        color: var(--text-muted);
        font-size: 0.82rem;
        font-weight: 700;
    }

    .focus-status strong {
        color: var(--text-main);
        margin-right: auto;
    }

    .focus-status span:not(.brand-mark) {
        display: inline-flex;
        align-items: center;
        min-height: 2rem;
        padding: 0 0.65rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.48);
        border: 1px solid rgba(255, 255, 255, 0.58);
    }

    [data-testid="stBottomBlockContainer"] {
        position: fixed !important;
        inset: auto 0 0 0 !important;
        z-index: 9999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: flex-end !important;
        padding: 0.55rem 1rem calc(0.75rem + env(safe-area-inset-bottom)) !important;
        background:
            linear-gradient(180deg, rgba(248, 246, 251, 0), rgba(248, 246, 251, 0.9) 36%, rgba(248, 246, 251, 0.98) 100%) !important;
        pointer-events: none;
    }

    [data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"],
    [data-testid="stBottomBlockContainer"] .st-key-hgrid_chat_input,
    [data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] {
        width: min(760px, calc(100vw - 2rem)) !important;
        max-width: min(760px, calc(100vw - 2rem)) !important;
        flex: none !important;
        margin-left: auto !important;
        margin-right: auto !important;
        pointer-events: auto;
    }

    [data-testid="stChatInput"] {
        width: 100% !important;
        min-height: 4rem !important;
        border: 1px solid rgba(255, 255, 255, 0.78) !important;
        border-radius: 20px !important;
        background: linear-gradient(145deg, rgba(250, 249, 252, 0.94), rgba(235, 233, 241, 0.88)) !important;
        box-shadow:
            10px 14px 34px rgba(86, 80, 102, 0.16),
            -10px -10px 28px rgba(255, 255, 255, 0.76),
            inset 1px 1px 0 rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(14px) saturate(112%);
        -webkit-backdrop-filter: blur(14px) saturate(112%);
        transform: translateY(0);
    }

    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div:focus-within {
        position: relative !important;
        border: 0 !important;
        outline: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] > div > div {
        position: relative !important;
    }

    [data-testid="stChatInput"] > div > div > div:last-child {
        position: absolute !important;
        right: 0 !important;
        top: 50% !important;
        bottom: auto !important;
        transform: translateY(-50%);
        width: auto !important;
        height: 2.55rem !important;
        min-height: 2.55rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        pointer-events: auto;
    }

    [data-testid="stChatInput"].hgrid-multiline > div > div > div:last-child {
        top: auto !important;
        bottom: 0.72rem !important;
        transform: none;
    }

    @media (prefers-reduced-motion: no-preference) {
        [data-testid="stChatInput"] {
            transition: transform 220ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 220ms ease-out, border-color 140ms ease-out, opacity 140ms ease-out;
        }

        .st-key-chat_history_view [data-testid="stChatMessage"] {
            animation: answer-rise 220ms ease-out both;
        }
    }

    [data-testid="stChatInput"]:has(textarea:focus),
    [data-testid="stChatInput"]:has(textarea:not(:placeholder-shown)) {
        border-color: rgba(255, 255, 255, 0.9) !important;
        box-shadow:
            14px 18px 46px rgba(82, 76, 98, 0.2),
            -12px -12px 30px rgba(255, 255, 255, 0.84),
            inset 0 0 0 1px rgba(92, 86, 106, 0.08) !important;
        transform: translateY(-1.45rem);
    }

    body:has([data-testid="stSpinner"]) [data-testid="stChatInput"],
    [data-testid="stChatInput"]:has(textarea:disabled) {
        border-color: rgba(255, 255, 255, 0.72) !important;
        box-shadow:
            7px 10px 26px rgba(86, 80, 102, 0.12),
            -7px -7px 22px rgba(255, 255, 255, 0.68),
            inset 1px 1px 0 rgba(255, 255, 255, 0.74) !important;
        opacity: 0.92;
        transform: translateY(0) !important;
    }

    body:has([data-testid="stSpinner"]) [data-testid="stChatInput"] textarea {
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    body:has([data-testid="stSpinner"]) [data-testid="stChatInput"] button,
    [data-testid="stChatInput"].hgrid-answering button {
        pointer-events: none !important;
        opacity: 0.54 !important;
    }

    [data-testid="stChatInput"] textarea,
    textarea[data-testid="stChatInputTextArea"] {
        min-height: 2.75rem !important;
        max-height: 11rem !important;
        padding: 0.75rem 3.2rem 0.75rem 1rem !important;
        border: 0 !important;
        border-radius: 18px !important;
        background: transparent !important;
        color: var(--text-main) !important;
        font-size: 0.98rem !important;
        line-height: 1.55 !important;
        box-shadow: none !important;
        resize: none !important;
        overflow-y: auto !important;
        caret-color: #4a4653;
    }

    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] textarea:focus-visible,
    textarea[data-testid="stChatInputTextArea"]:focus,
    textarea[data-testid="stChatInputTextArea"]:focus-visible {
        outline: 0 !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"]:has(textarea:placeholder-shown),
    [data-testid="stChatInput"].hgrid-empty {
        height: auto !important;
        min-height: 4rem !important;
    }

    [data-testid="stChatInput"]:has(textarea:placeholder-shown) textarea,
    [data-testid="stChatInput"].hgrid-empty textarea {
        height: 2.75rem !important;
        overflow-y: hidden !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #6d6877 !important;
        opacity: 1;
    }

    [data-testid="stChatInput"] button,
    button[data-testid="stChatInputSubmitButton"] {
        width: 2.55rem !important;
        min-width: 2.55rem !important;
        height: 2.55rem !important;
        min-height: 2.55rem !important;
        border-radius: 999px !important;
        background: linear-gradient(145deg, #4a4653, #2f2b38) !important;
        color: var(--text-on-accent) !important;
        box-shadow:
            6px 8px 18px rgba(66, 60, 80, 0.22),
            -2px -2px 8px rgba(255, 255, 255, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
    }

    [data-testid="stChatInput"] button:disabled,
    button[data-testid="stChatInputSubmitButton"]:disabled {
        background: #d8d5df !important;
        color: rgba(47, 43, 56, 0.48) !important;
        box-shadow:
            inset 2px 2px 5px rgba(104, 97, 120, 0.12),
            inset -2px -2px 5px rgba(255, 255, 255, 0.72) !important;
    }

    [data-testid="stChatInput"] button:focus-visible,
    button[data-testid="stChatInputSubmitButton"]:focus-visible {
        outline: 3px solid rgba(74, 70, 83, 0.34) !important;
        outline-offset: 2px !important;
    }

    @keyframes answer-rise {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 760px) {
        .block-container {
            max-width: 100vw !important;
            padding: 0.75rem 0.75rem 18rem !important;
        }

        .st-key-chat_history_view {
            min-height: calc(100dvh - 18rem);
        }

        .st-key-chat_history_view [data-testid="stChatMessage"] {
            max-width: 92% !important;
        }

        .st-key-chat_history_view [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
            max-width: 88% !important;
        }

        [data-testid="stBottomBlockContainer"] {
            padding: 0.45rem 0.6rem calc(0.55rem + env(safe-area-inset-bottom)) !important;
        }

        [data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"],
        [data-testid="stBottomBlockContainer"] .st-key-hgrid_chat_input,
        [data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] {
            width: min(100%, calc(100vw - 1rem)) !important;
            max-width: min(100%, calc(100vw - 1rem)) !important;
            flex: none !important;
        }

        [data-testid="stChatInput"] {
            border-radius: 18px !important;
        }

        [data-testid="stChatInput"] textarea,
        textarea[data-testid="stChatInputTextArea"] {
            max-height: 9.5rem !important;
            font-size: 0.95rem !important;
        }
    }

</style>
""".replace("__DISPLAY_FONT_REGULAR__", DISPLAY_FONT_REGULAR).replace(
        "__DISPLAY_FONT_BOLD__", DISPLAY_FONT_BOLD
    ),
    unsafe_allow_html=True,
)


EXAMPLE_PROMPTS = [
    ("Definisi HGrid247", "Apa itu HGrid247-3.5 DE?"),
    ("Workflow dasar", "Jelaskan alur Source, Assembly, dan Sink di HGrid247."),
    ("Build target", "Engine atau build target apa saja yang didukung HGrid247?"),
    ("Troubleshooting", "Bagaimana cara mulai troubleshooting workflow HGrid247?"),
]


@st.cache_resource(show_spinner=False)
def init_resources() -> tuple[Any, Any]:
    """Initialize resources once per Streamlit process."""
    return get_vector_store(), get_llm()


def render_header(error: Exception | None = None) -> None:
    nav_state = "RAG ready" if error is None else "Setup check"
    dot_class = "status-dot" if error is None else "status-dot is-warning"

    st.markdown(
        f"""
<section class="glass-shell" aria-label="HGrid247 AI chat workbench">
    <nav class="glass-nav" aria-label="HGrid247 AI navigation">
        <div class="brand-lockup">
            <span class="brand-mark" aria-hidden="true">H</span>
            <span>HGrid247 AI</span>
        </div>
        <div class="nav-links" aria-label="Workbench sections">
            <span class="nav-pill is-active">Chat</span>
            <span class="nav-pill">Sources</span>
            <span class="nav-pill">Config</span>
            <span class="nav-pill">Run</span>
        </div>
        <div class="nav-tools">
            <span class="nav-search" aria-hidden="true">Search docs</span>
            <span class="nav-status"><span class="{dot_class}" aria-hidden="true"></span>{html.escape(nav_state)}</span>
        </div>
    </nav>
    <div class="assistant-stage">
        <span class="assistant-mark" aria-hidden="true">H</span>
        <h1>Hi, I'm HGrid247 AI</h1>
        <p>Tanyakan dokumentasi HGrid247-3.5 DE. Jawaban berbasis RAG dengan status retrieval dan tautan sumber.</p>
    </div>
</section>
""",
        unsafe_allow_html=True,
    )


def render_status(error: Exception | None) -> None:
    qdrant_state = "Siap" if error is None else "Perlu cek"
    st.markdown(
        f"""
<div class="status-grid">
    <div class="status-cell status-glass"><span>Qdrant</span><strong>{html.escape(qdrant_state)}</strong></div>
    <div class="status-cell status-glass"><span>Collection</span><strong>{html.escape(QDRANT_COLLECTION)}</strong></div>
    <div class="status-cell status-glass"><span>Model</span><strong>{html.escape(GEMINI_MODEL)}</strong></div>
    <div class="status-cell status-glass"><span>Retrieval</span><strong>Top {SIMILARITY_TOP_K} chunks</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def resolution_markup(stage: str, chunks_used: int = 0, source_count: int = 0) -> str:
    if stage == "resolved":
        steps = [
            ("Question load", "locked", "is-complete"),
            ("Retrieval tension", f"{chunks_used} chunks", "is-complete"),
            ("Answer", "composed", "is-complete"),
            ("Source anchors", f"{source_count} pages", "is-complete"),
        ]
    else:
        steps = [
            ("Question load", "locked", "is-complete"),
            ("Retrieval tension", "matching docs", "is-active"),
            ("Answer", "waiting", "is-pending"),
            ("Source anchors", "waiting", "is-pending"),
        ]

    items = "".join(
        f'<div class="resolution-step {class_name}"><strong>{title}</strong><span>{detail}</span></div>'
        for title, detail, class_name in steps
    )
    return f'<div class="resolution-rail glass-panel status-glass" role="status" aria-live="polite" aria-label="Retrieval resolution state"><div class="resolution-steps">{items}</div></div>'


def render_quick_prompt_chips() -> None:
    st.markdown(
        '<div class="quick-chip-caption">Pertanyaan cepat</div>',
        unsafe_allow_html=True,
    )
    columns = st.columns(len(EXAMPLE_PROMPTS), gap="small")

    for index, ((label, prompt_text), column) in enumerate(zip(EXAMPLE_PROMPTS, columns)):
        with column:
            if st.button(label, key=f"quick_main_{index}", use_container_width=True):
                st.session_state.pending_prompt = prompt_text


def render_resource_warning(error: Exception) -> None:
    st.markdown(
        """
<div class="warning-panel glass-panel">
    <strong>Koneksi RAG belum siap</strong>
    <p>Periksa service Qdrant, pastikan collection sudah di-ingest, dan cek <code>GOOGLE_API_KEY</code> di <code>.env</code> sebelum mengirim pertanyaan.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.expander("Detail teknis error", expanded=False):
        st.code(str(error))


def render_sources(message: dict[str, Any]) -> None:
    sources = message.get("sumber", [])
    chunks_used = message.get("chunks_used", 0)
    chunks = message.get("retrieved_chunks", [])

    st.markdown(
        f"""
<div class="source-strip">
    <span class="source-pill">{chunks_used} chunks used</span>
    <span class="source-pill">{len(sources)} source pages</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if sources:
        links = []
        for index, source in enumerate(sources[:4], 1):
            safe_href = html.escape(source, quote=True)
            safe_label = html.escape(source)
            links.append(
                f'<a class="source-link" href="{safe_href}" target="_blank" rel="noreferrer">{index}. {safe_label}</a>'
            )

        st.markdown(
            f"""
<div class="source-panel source-glass">
    <div class="source-panel-label">Source anchors</div>
    <div class="source-list">{''.join(links)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    if chunks:
        with st.expander("Preview chunk retrieval", expanded=False):
            for index, chunk in enumerate(chunks, 1):
                source = html.escape(chunk.get("source", "Unknown"))
                preview = html.escape(chunk.get("preview", ""))
                st.markdown(
                    f'<div class="chunk-preview"><b>Chunk {index}</b><br>{preview}<br><small>{source}</small></div>',
                    unsafe_allow_html=True,
                )


def memory_history_from_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []

    for message in messages:
        role = message.get("role")
        raw_content = message.get("content", "")
        if raw_content is None:
            continue

        content = str(raw_content).strip()

        if role in {"user", "assistant"} and content:
            history.append({"role": role, "content": content})

    return history


def render_chat_history() -> None:
    if not st.session_state.messages:
        st.markdown(
            """
<div class="empty-state glass-panel">
    Pertanyaan awal yang cocok: operator, workflow, engine, dynamic parameter, plugin, atau troubleshooting.
</div>
""",
            unsafe_allow_html=True,
        )
        return

    for message in st.session_state.messages:
        role = message.get("role")

        if role == "user":
            with st.chat_message("user", avatar=":material/person:"):
                st.markdown(message.get("content", ""))
        elif role == "assistant":
            with st.chat_message("assistant", avatar=":material/hub:"):
                st.markdown(message.get("content", ""))
                render_sources(message)


def render_chat_anchor() -> None:
    st.markdown('<div id="chat-bottom-anchor" aria-hidden="true"></div>', unsafe_allow_html=True)


def scroll_to_latest() -> None:
    components.html(
        """
<script>
const parentWindow = window.parent;
const parentDocument = parentWindow.document;

function getScroller() {
  return parentDocument.querySelector('[data-testid="stAppScrollToBottomContainer"]')
    || parentDocument.scrollingElement
    || parentDocument.documentElement;
}

const DRAFT_KEY = "hgrid247-chat-draft";

function isAnswering() {
  return Boolean(parentDocument.querySelector('[data-testid="stSpinner"]'));
}

function scrollLatest(force = false) {
  const anchor = parentDocument.getElementById("chat-bottom-anchor");
  if (!anchor) return;

  const scroller = getScroller();
  const distanceFromBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
  if (!force && distanceFromBottom > 360) return;

  const composer = parentDocument.querySelector('[data-testid="stChatInput"]');
  const composerHeight = composer ? composer.getBoundingClientRect().height : 96;
  anchor.style.height = `${Math.ceil(composerHeight + 36)}px`;

  requestAnimationFrame(() => {
    scroller.scrollTo({ top: scroller.scrollHeight, behavior: "auto" });
  });
}

function updateComposerBusyState() {
  const composer = parentDocument.querySelector('[data-testid="stChatInput"]');
  const textarea = composer?.querySelector('textarea');
  const button = composer?.querySelector('button[data-testid="stChatInputSubmitButton"]');
  const busy = isAnswering();

  if (composer) {
    composer.classList.toggle("hgrid-answering", busy);
  }

  if (textarea && busy && textarea.disabled) {
    textarea.disabled = false;
    textarea.removeAttribute("disabled");
  }

  if (textarea) {
    syncComposerShape(textarea);
  }

  if (button && textarea) {
    const shouldDisable = busy || textarea.disabled || textarea.value.trim().length === 0;
    button.disabled = shouldDisable;
    button.setAttribute("aria-disabled", shouldDisable ? "true" : "false");
  }
}

function restoreDraft(textarea) {
  const draft = parentWindow.sessionStorage.getItem(DRAFT_KEY);
  if (draft && !textarea.value) {
    textarea.value = draft;
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  }
  syncComposerShape(textarea);
}

function clearDraft() {
  parentWindow.sessionStorage.removeItem(DRAFT_KEY);
}

function syncComposerShape(textarea) {
  if (!textarea) return;

  const composer = parentDocument.querySelector('[data-testid="stChatInput"]');
  const hasText = textarea.value.trim().length > 0;
  const minHeight = 44;
  const maxHeight = parentWindow.matchMedia("(max-width: 760px)").matches ? 152 : 176;

  textarea.style.height = "auto";
  const nextHeight = hasText
    ? Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)
    : minHeight;
  textarea.style.height = `${nextHeight}px`;
  textarea.style.overflowY = textarea.scrollHeight > maxHeight ? "auto" : "hidden";

  if (composer) {
    const isMultiline = nextHeight > minHeight + 8;
    composer.classList.toggle("hgrid-empty", !hasText);
    composer.classList.toggle("hgrid-has-text", hasText);
    composer.classList.toggle("hgrid-multiline", isMultiline);
  }
}

scrollLatest(true);
updateComposerBusyState();

if (!parentWindow.__hgridChatScrollInstalled) {
  parentWindow.__hgridChatScrollInstalled = true;

  const bindComposer = () => {
    const composer = parentDocument.querySelector('[data-testid="stChatInput"]');
    const textarea = composer?.querySelector('textarea');
    const button = composer?.querySelector('button[data-testid="stChatInputSubmitButton"]');
    if (!composer || !textarea) return;

    updateComposerBusyState();

    if (textarea.dataset.hgridScrollBound !== "true") {
      textarea.dataset.hgridScrollBound = "true";
      restoreDraft(textarea);

      textarea.addEventListener("focus", () => scrollLatest(false), { passive: true });
      textarea.addEventListener("input", () => {
        parentWindow.sessionStorage.setItem(DRAFT_KEY, textarea.value);
        syncComposerShape(textarea);
        scrollLatest(false);
        updateComposerBusyState();
      }, { passive: true });
      textarea.addEventListener("keydown", (event) => {
        const isSubmitKey = event.key === "Enter" && !event.shiftKey;
        if (!isSubmitKey) return;

        if (isAnswering()) {
          event.preventDefault();
          event.stopImmediatePropagation();
        } else {
          clearDraft();
        }
      }, true);

      if ("ResizeObserver" in parentWindow) {
        const observer = new parentWindow.ResizeObserver(() => {
          syncComposerShape(textarea);
          scrollLatest(false);
        });
        observer.observe(composer);
      }
    }

    if (button && button.dataset.hgridSubmitBound !== "true") {
      button.dataset.hgridSubmitBound = "true";
      button.addEventListener("click", (event) => {
        if (isAnswering()) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }
        clearDraft();
      }, true);
    }
  };

  bindComposer();
  parentWindow.addEventListener("resize", () => {
    const textarea = parentDocument.querySelector('[data-testid="stChatInput"] textarea');
    syncComposerShape(textarea);
    scrollLatest(false);
  }, { passive: true });

  const mutationObserver = new parentWindow.MutationObserver(() => {
    bindComposer();
    updateComposerBusyState();
    scrollLatest(false);
  });
  mutationObserver.observe(parentDocument.body, { childList: true, subtree: true });
}
</script>
""",
        height=0,
    )


def stream_prompt(
    prompt: str,
    chat_history: list[dict[str, str]],
    vector_store: Any,
    llm: Any,
) -> tuple[Any, dict[str, Any]]:
    return tanya_hgrid_with_memory_stream(
        prompt,
        chat_history=chat_history,
        vector_store=vector_store,
        llm=llm,
    )


def coerce_streamed_answer(streamed_answer: Any) -> str:
    if isinstance(streamed_answer, str):
        return streamed_answer.strip()
    if isinstance(streamed_answer, list):
        return "".join(str(part) for part in streamed_answer).strip()
    return str(streamed_answer).strip()


def assistant_message_from_answer(answer: str, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": answer,
        "sumber": metadata["sumber"],
        "chunks_used": metadata["chunks_used"],
        "retrieved_chunks": metadata["retrieved_chunks"],
    }


if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

resource_error: Exception | None = None
resources: tuple[Any, Any] | None = None

try:
    resources = init_resources()
except Exception as exc:  # surfaced in the app so setup issues are actionable
    resource_error = exc

chat_history_container = st.container(key="chat_history_view", border=False, autoscroll=True)

chat_prompt = st.chat_input(
    "Tanya workflow, operator, engine, parameter, atau troubleshooting HGrid247...",
    key="hgrid_chat_input",
    disabled=resources is None,
    submit_mode="submit",
    height="content",
)

pending_prompt = st.session_state.pending_prompt
if pending_prompt:
    st.session_state.pending_prompt = None

active_prompt = pending_prompt or (chat_prompt.strip() if isinstance(chat_prompt, str) else None)

if active_prompt and resources is not None:
    previous_history = memory_history_from_messages(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": active_prompt})

    with chat_history_container:
        if resource_error is not None:
            render_resource_warning(resource_error)
        render_chat_history()

    assistant_message = chat_history_container.chat_message("assistant", avatar=":material/hub:")
    with chat_history_container:
        render_chat_anchor()
    scroll_to_latest()

    with assistant_message:
        with st.spinner("Mencari jawaban dari dokumentasi HGrid247..."):
            answer_stream, metadata = stream_prompt(
                active_prompt,
                chat_history=previous_history,
                vector_store=resources[0],
                llm=resources[1],
            )
            answer_text = coerce_streamed_answer(st.write_stream(answer_stream))
        assistant_response = assistant_message_from_answer(answer_text, metadata)
        render_sources(assistant_response)

    st.session_state.messages.append(assistant_response)
    st.rerun()
else:
    with chat_history_container:
        if resource_error is not None:
            render_resource_warning(resource_error)
        render_chat_history()
        render_chat_anchor()

    scroll_to_latest()
