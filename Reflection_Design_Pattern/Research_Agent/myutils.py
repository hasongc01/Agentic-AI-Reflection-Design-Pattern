import sys, os
from IPython.display import display, HTML

def show_output(title: str, content: str, background: str = "#ffffff", text_color: str = "#000000"):
    """
    Display formatted text output (e.g., essay draft, reflection, revision)
    with custom background and text color.

    Parameters
    ----------
    title : str
        Section title (e.g., 'Step 1 – Draft')
    content : str
        Text content to display (e.g., essay text)
    background : str, optional
        Background color in HEX (default: white)
    text_color : str, optional
        Text color in HEX (default: black)
    """

    html = f"""
    <div style="
        background-color: {background};
        color: {text_color};
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin-top: 0;">{title}</h3>
        <pre style="white-space: pre-wrap; font-size: 15px;">{content}</pre>
    </div>
    """
    display(HTML(html))
