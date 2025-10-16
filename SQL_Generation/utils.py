
import os
import sqlite3
import random
import datetime as dt
from pathlib import Path
from typing import Optional, Iterable
from IPython.display import HTML, display
from dotenv import load_dotenv
import pandas as pd
import re


# ai suite: https://github.com/andrewyng/aisuite


# --- Load .env so OPENAI_API_KEY becomes available ---
load_dotenv()


import aisuite as ai

client = ai.Client()

# ---------- OpenAI (vision) ----------
# Uses Chat Completions with a data: URL for the image.
# Requires: pip install openai (and OPENAI_API_KEY in env)
try:
    from openai import OpenAI
    _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"[utils] Warning: OpenAI client not initialized ({e})")
    _openai_client = None


# -----------------------------
# Public API
# -----------------------------

def create_transactions_db(
    db_path: str = "products.db",
    n_products: int = 100,
    n_events: int = 2000,
    seed: int = 42,
    overwrite: bool = True
) -> str:
    """
    Create a local SQLite database pre-populated with randomized product transaction events.
    
    Table: transactions
        id INTEGER PRIMARY KEY AUTOINCREMENT
        product_id INTEGER
        product_name TEXT
        brand TEXT
        category TEXT
        color TEXT
        action TEXT                -- one of: insert, restock, sale, price_update
        qty_delta INTEGER          -- + for insert/restock, – for sale, 0 for price updates
        unit_price REAL            -- price at that moment (NULL for restock)
        notes TEXT
        ts DATETIME                -- event timestamp
    
    Returns: absolute path to the created database file.
    """
    rng = random.Random(seed)
    db_path = str(Path(db_path))
    db_file = Path(db_path).resolve()

    if overwrite and db_file.exists():
        db_file.unlink()

    # Ensure parent directory exists
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_file.as_posix())
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT,
            brand TEXT,
            category TEXT,
            color TEXT,
            action TEXT,
            qty_delta INTEGER,
            unit_price REAL,
            notes TEXT,
            ts DATETIME
        );
    """)
    conn.commit()

    # Synthetic vocabularies
    brands = ["Acme", "Nimbus", "Vertex", "Zenith", "Orbit", "Pulse", "Aurora", "Quantum"]
    categories = ["Headphones", "Keyboard", "Mouse", "Monitor", "Laptop Stand", "Charger", "Backpack", "Webcam"]
    colors = ["Black", "White", "Space Gray", "Silver", "Blue", "Red", "Green", "Purple"]

    # Build product catalog
    products = []
    for pid in range(1, n_products + 1):
        brand = rng.choice(brands)
        category = rng.choice(categories)
        color = rng.choice(colors)
        # Product name pattern
        product_name = f"{brand} {category} {color} {pid:03d}"
        # Base price per category (roughly)
        base_price = {
            "Headphones": 79,
            "Keyboard": 99,
            "Mouse": 49,
            "Monitor": 249,
            "Laptop Stand": 39,
            "Charger": 29,
            "Backpack": 89,
            "Webcam": 69,
        }[category]
        # Add some variation
        base_price = round(base_price * (0.8 + 0.4 * rng.random()), 2)
        products.append({
            "product_id": pid,
            "product_name": product_name,
            "brand": brand,
            "category": category,
            "color": color,
            "price": base_price,
            "stock": 0
        })

    # Helper to insert an event
    def insert_event(prod, action, qty_delta, price_or_none, note, ts):
        cur.execute(
            """
            INSERT INTO transactions (
                product_id, product_name, brand, category, color,
                action, qty_delta, unit_price, notes, ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prod["product_id"],
                prod["product_name"],
                prod["brand"],
                prod["category"],
                prod["color"],
                action,
                qty_delta,
                price_or_none,
                note,
                ts.strftime("%Y-%m-%d %H:%M:%S")
            )
        )

    # Start time window: last ~120 days
    now = dt.datetime.now()
    start = now - dt.timedelta(days=120)

    # Seed every product with an initial "insert" event (initial inventory & price)
    for prod in products:
        ts0 = start + dt.timedelta(days=int(rng.random() * 30), hours=int(rng.random() * 24), minutes=int(rng.random() * 60))
        initial_qty = rng.randint(10, 200)
        prod["stock"] += initial_qty
        insert_event(prod, "insert", initial_qty, prod["price"], "Initial catalog load", ts0)

    # Create remaining randomized events
    # We already inserted n_products events; create (n_events - n_products) more
    remaining = max(0, n_events - n_products)
    for _ in range(remaining):
        prod = rng.choice(products)

        # Draw a timestamp between start and now
        delta_sec = int(rng.random() * (now - start).total_seconds())
        ts = start + dt.timedelta(seconds=delta_sec)

        # Decide action with weighted probabilities
        # - sale is most frequent, then restock, then price_update
        action = rng.choices(
            population=["sale", "restock", "price_update"],
            weights=[0.6, 0.25, 0.15],
            k=1
        )[0]

        if action == "sale":
            if prod["stock"] <= 0:
                # If no stock, convert to restock instead
                action = "restock"

        if action == "sale":
            # sell between 1 and 5 units, but not more than in stock
            qty = min(prod["stock"], rng.randint(1, 5))
            if qty == 0:
                continue  # skip impossible sale
            prod["stock"] -= qty
            insert_event(prod, "sale", -qty, prod["price"], "Customer purchase", ts)

        elif action == "restock":
            qty = rng.randint(5, 50)
            prod["stock"] += qty
            # unit_price is NULL for restock per spec
            insert_event(prod, "restock", qty, None, "Warehouse restock", ts)

        else:  # price_update
            # price move by ±(0%..10%)
            change = 1.0 + rng.uniform(-0.10, 0.10)
            prod["price"] = round(max(0.5, prod["price"] * change), 2)
            insert_event(prod, "price_update", 0, prod["price"], "Pricing update", ts)

    conn.commit()

    # Optional: create indexes for faster querying
    cur.executescript("""
        CREATE INDEX IF NOT EXISTS idx_transactions_pid ON transactions(product_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_action ON transactions(action);
        CREATE INDEX IF NOT EXISTS idx_transactions_ts ON transactions(ts);
    """)
    conn.commit()
    conn.close()
    return db_file.as_posix()


def get_schema(db_path: str = "products.db") -> str:
    """
    Return an HTML snippet summarizing the schema of the 'transactions' table.
    """
    db_file = Path(db_path).resolve()
    conn = sqlite3.connect(db_file.as_posix())
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(transactions);")
    cols = cur.fetchall()
    conn.close()

    # cols: [(cid, name, type, notnull, dflt_value, pk), ...]
    headers = ["cid", "name", "type", "notnull", "default", "pk"]
    html = ["<h3>Schema: transactions</h3>"]
    html.append("<table border='1' cellpadding='6' cellspacing='0'>")
    html.append("<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>")
    html.append("<tbody>")
    for cid, name, coltype, notnull, dflt, pk in cols:
        html.append("<tr>" +
                    f"<td>{cid}</td><td>{name}</td><td>{coltype}</td><td>{notnull}</td><td>{dflt}</td><td>{pk}</td>"
                    + "</tr>")
    html.append("</tbody></table>")
    # Add overview
    overview = """
    <p><b>Schema overview</b>:</p>
    <ul>
      <li><b>id</b> → unique event ID (autoincrement).</li>
      <li><b>product_id, product_name, brand, category, color</b> → identify the product.</li>
      <li><b>action</b> → type of event (<i>insert, restock, sale, price_update</i>).</li>
      <li><b>qty_delta</b> → stock change (+ for insert/restock, – for sale, 0 for price updates).</li>
      <li><b>unit_price</b> → price at that moment (NULL for restock).</li>
      <li><b>notes</b> → optional description of the event.</li>
      <li><b>ts</b> → timestamp when the event was logged.</li>
    </ul>
    """
    html.append(overview)
    return "\n".join(html)

# ------ HTML ---- 

# def print_html(html: str) -> None:
#     """Display raw HTML in notebooks/REPLs that support rich output."""
#     display(HTML(html))
from IPython.display import HTML, display

def print_html(content: str, title: str = None) -> None:
    """
    Display nicely formatted HTML in Jupyter or IPython environments.

    Args:
        content (str): The main content (HTML or plain text) to display.
        title (str, optional): Optional title to display above the content.
    """
    # Escape plain text to HTML if necessary
    def _escape_html(text):
        import html
        return html.escape(text)

    # If the content doesn't look like HTML, escape it
    if not any(tag in content for tag in ("<p", "<div", "<table", "<ul", "<ol", "<h", "<br", "<tr", "<td", "<th")):
        content = f"<pre>{_escape_html(content)}</pre>"

    # Add title if provided
    if title:
        html = f"""
        <div style='font-family:Arial, sans-serif; margin:10px 0;'>
            <h3 style='color:#2F4F4F;'>{_escape_html(title)}</h3>
            {content}
        </div>
        """
    else:
        html = content

    display(HTML(html))


# ----- SQL generation ---- 

def generate_sql(question: str, schema: str, model: str) -> str:
    prompt = f"""
    You are a SQL assistant. Given the schema and the user's question, write a SQL query for SQLite.

    Schema:
    {schema}

    User question:
    {question}

    Respond with the SQL only.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()

# ----- Execute SQL ----

def execute_sql(sql: str, db_path: str = "products.db") -> pd.DataFrame:
    """
    Execute a SQL query on the given SQLite database and return the result as a pandas DataFrame.
    Automatically cleans out Markdown formatting (like ```sql ... ```).
    """
    # --- Clean SQL text ---
    # Remove Markdown-style code block fences and extra spaces
    sql = re.sub(r"^```[a-zA-Z]*|```$", "", sql.strip(), flags=re.MULTILINE).strip()

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        error_html = f"""
        <div style='color:#B22222; font-family:monospace;'>
            <b>SQL Execution Error:</b> {e}
        </div>
        """
        display(HTML(error_html))
        return pd.DataFrame()