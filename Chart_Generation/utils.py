# utils.py

import os
import re
import base64
import mimetypes
import pandas as pd
from dotenv import load_dotenv


# --- Load .env so OPENAI_API_KEY becomes available ---
load_dotenv()

# --- Load CSV data
def load_and_prepare_data(filepath: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """
    Load a CSV dataset and perform basic cleaning/preparation.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    parse_dates : list[str], optional
        List of columns to parse as dates (e.g., ['date', 'Week (2008-2009)']).

    Returns
    -------
    pd.DataFrame
        Cleaned pandas DataFrame ready for analysis.
    """
    # --- Load data ---
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise FileNotFoundError(f"Could not load file: {filepath}\nError: {e}")

    # # --- Clean column names ---
    # df.columns = (
    #     df.columns
    #     .str.strip()              # remove leading/trailing spaces
    #     .str.replace(" ", "_")    # replace spaces with underscores
    #     .str.replace(r"[()/%]", "", regex=True)  # remove special chars
    #     .str.lower()              # lowercase for consistency
    # )

    # --- Drop fully empty columns ---
    df = df.dropna(axis=1, how="all")

    # --- Optionally parse date columns ---
    if parse_dates:
        for col in parse_dates:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- Handle missing values (simple approach) ---
    df = df.fillna(method="ffill").fillna(method="bfill")

    # --- Reset index for convenience ---
    df = df.reset_index(drop=True)

    print(f"[utils] Loaded dataset: {filepath} ({df.shape[0]} rows, {df.shape[1]} columns)")
    return df


# --- Load Excel data
def load_and_prepare_data_excel(filepath: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """
    Load a Excel dataset and perform basic cleaning/preparation.

    Parameters
    ----------
    filepath : str
        Path to the Excel file.
    parse_dates : list[str], optional
        List of columns to parse as dates (e.g., ['date', 'Week (2008-2009)']).

    Returns
    -------
    pd.DataFrame
        Cleaned pandas DataFrame ready for analysis.
    """
    # --- Load data ---
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        raise FileNotFoundError(f"Could not load file: {filepath}\nError: {e}")

    # # --- Clean column names ---
    # df.columns = (
    #     df.columns
    #     .str.strip()              # remove leading/trailing spaces
    #     .str.replace(" ", "_")    # replace spaces with underscores
    #     .str.replace(r"[()/%]", "", regex=True)  # remove special chars
    #     .str.lower()              # lowercase for consistency
    # )

    # --- Drop fully empty columns ---
    df = df.dropna(axis=1, how="all")

    # --- Optionally parse date columns ---
    if parse_dates:
        for col in parse_dates:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- Handle missing values (simple approach) ---
    df = df.fillna(method="ffill").fillna(method="bfill")

    # --- Reset index for convenience ---
    df = df.reset_index(drop=True)

    print(f"[utils] Loaded dataset: {filepath} ({df.shape[0]} rows, {df.shape[1]} columns)")
    return df

# ---------- Display helpers ----------
try:
    from IPython.display import display, HTML, Image
except Exception:
    display = HTML = Image = None

def print_html(content: str, title: str = "Output", is_image: bool = False):
    """Display formatted HTML or images in Jupyter."""
    if display is None:
        # Fallback: plain print if not in IPython
        print(f"[{title}]\n{content}")
        return
    if is_image:
        display(HTML(f"<h3>{title}</h3>"))
        display(Image(filename=content))
    else:
        display(HTML(f"<h3>{title}</h3><pre style='white-space:pre-wrap'>{content}</pre>"))

# ---------- Core: missing helpers you asked about ----------
def encode_image_b64(path: str) -> tuple[str, str]:
    """
    Read an image file and return (media_type, base64_str).
    media_type is a MIME type like 'image/png' or 'image/jpeg'.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        # default to PNG if we can't guess
        mime = "image/png"

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return mime, b64


def ensure_execute_python_tags(code_body: str) -> str:
    """
    Ensure the returned string is wrapped in <execute_python>...</execute_python>.
    If tags already exist, return as-is.
    """
    if re.search(r"<execute_python>[\s\S]*</execute_python>", code_body, flags=re.DOTALL):
        return code_body.strip()
    return f"<execute_python>\n{code_body.strip()}\n</execute_python>"


# ---------- OpenAI (vision) ----------
# Uses Chat Completions with a data: URL for the image.
# Requires: pip install openai (and OPENAI_API_KEY in env)
try:
    from openai import OpenAI
    _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"[utils] Warning: OpenAI client not initialized ({e})")
    _openai_client = None


def get_response(model: str, prompt: str) -> str:
    """Simple text-only call to OpenAI chat models."""
    if _openai_client is None:
        raise RuntimeError("OpenAI client not initialized.")
    resp = _openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
        # ,
        # temperature=0,
    )
    return resp.choices[0].message.content

def image_openai_call(model: str, prompt: str, media_type: str, b64: str) -> str:
    """
    Send an image + prompt to an OpenAI vision-capable chat model and return the text response.
    """
    if _openai_client is None:
        raise RuntimeError(
            "OpenAI client not initialized. Ensure 'openai' is installed and OPENAI_API_KEY is set."
        )

    data_url = f"data:{media_type};base64,{b64}"
    resp = _openai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )
    return resp.choices[0].message.content


# ---------- Anthropic (vision) ----------
# Requires: pip install anthropic (and ANTHROPIC_API_KEY in env)
def image_anthropic_call(model: str, prompt: str, media_type: str, b64: str) -> str:
    """
    Send an image + prompt to Anthropic Claude and return the text response.
    """
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError("anthropic package is not installed. `pip install anthropic`") from e

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                ],
            }
        ],
    )
    # Claude returns a list of ContentBlock objects; collect text blocks
    parts = []
    for blk in msg.content:
        if getattr(blk, "type", None) == "text":
            parts.append(blk.text)
    return "\n".join(parts).strip()
