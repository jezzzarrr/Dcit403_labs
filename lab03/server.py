"""Pharmacy stock MCP server. Read tools = percepts; record_sale = the only actuator.
Run from anywhere; the data path is resolved relative to this file."""
import csv
from datetime import date, timedelta
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pharmacy-stock")
DATA = Path(__file__).parent / "data" / "pharmacy_stock.csv"


def load():
    with open(DATA, newline="") as f:
        return list(csv.DictReader(f))


def save(rows, fieldnames):
    with open(DATA, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _expiry(row):
    try:
        return date.fromisoformat(row["expiry_date"].strip())
    except Exception:
        return None


# ---------- READ TOOLS (percepts) ----------
@mcp.tool()
def check_stock(item: str, strength: str = "") -> list[dict]:
    """Return stock rows whose item name contains `item` (and whose strength contains `strength`, if given).
    Use for questions like 'Do we have amoxicillin 500mg?'. Read-only."""
    rows = [r for r in load() if item.lower() in r["item"].lower()]
    if strength:
        rows = [r for r in rows if strength.lower() in r["strength"].lower()]
    return rows


@mcp.tool()
def search_items(query: str) -> list[dict]:
    """Free-text search across item name, strength and form (for example 'syrup' or 'cough').
    Use when the user does not name an exact medicine, e.g. 'cough', 'syrup' or 'antibiotic'. Read-only."""
    q = query.lower()
    return [r for r in load() if q in (r["item"] + " " + r["strength"] + " " + r["form"]).lower()]


@mcp.tool()
def list_expiring(days: int) -> list[dict]:
    """List items that have already expired or will expire within `days` days from today.
    Each row gets a 'status' field. Use for 'Which items expire within 60 days?'. Read-only."""
    limit = date.today() + timedelta(days=days)
    out = []
    for r in load():
        e = _expiry(r)
        if e and e <= limit:
            r = dict(r)
            r["status"] = "EXPIRED" if e < date.today() else f"expires in {(e - date.today()).days} days"
            out.append(r)
    return sorted(out, key=lambda r: r["expiry_date"])


@mcp.tool()
def price_quote(item: str, strength: str, qty: int) -> dict:
    """Work out the cost of `qty` packs of one medicine (unit price x qty). Does NOT change stock.
    Use for 'What do 2 packs of paracetamol cost?'. Read-only."""
    rows = [r for r in load() if item.lower() in r["item"].lower()
            and (not strength or strength.lower() in r["strength"].lower())]
    if not rows:
        return {"error": f"No item matching '{item} {strength}'."}
    if len(rows) > 1:
        return {"error": "More than one match; ask which one.", "matches": [f"{r['item']} {r['strength']} ({r['form']})" for r in rows]}
    r = rows[0]
    return {"item": r["item"], "strength": r["strength"], "qty": qty,
            "unit_price_ghs": float(r["unit_price_ghs"]), "total_ghs": round(float(r["unit_price_ghs"]) * qty, 2)}


# ---------- WRITE TOOL (actuator) ----------
@mcp.tool()
def record_sale(item: str, strength: str, qty: int) -> str:
    """CHANGES STOCK. Record a sale of `qty` packs of ONE specific medicine and reduce its quantity.
    Call this ONLY when the user clearly asks to record or sell something, never to answer a question.
    It refuses if qty is not positive, if the item is not found or ambiguous, if the item is expired,
    or if there is not enough stock."""
    if qty <= 0:
        return "REFUSED: quantity must be a positive whole number."
    rows = load()
    fieldnames = list(rows[0].keys()) if rows else []
    matches = [r for r in rows if item.lower() in r["item"].lower()
               and (not strength or strength.lower() in r["strength"].lower())]
    if not matches:
        return f"REFUSED: no item matching '{item} {strength}'. Nothing was recorded."
    if len(matches) > 1:
        names = ", ".join(f"{r['item']} {r['strength']} ({r['form']})" for r in matches)
        return f"REFUSED: more than one match ({names}). Ask the user which one."
    row = matches[0]
    e = _expiry(row)
    if e and e < date.today():
        return f"REFUSED: {row['item']} {row['strength']} expired on {row['expiry_date']} and cannot be sold."
    have = int(float(row["quantity"]))
    if qty > have:
        return f"REFUSED: only {have} in stock, cannot sell {qty}. Nothing was recorded."
    row["quantity"] = str(have - qty)
    save(rows, fieldnames)
    return f"OK: sold {qty} x {row['item']} {row['strength']}. {have - qty} left in stock."


# ---------- Stretch: a resource and a prompt ----------
@mcp.resource("stock://summary")
def stock_summary() -> str:
    """Read-only overview of the whole stock list."""
    rows = load()
    low = [f"{r['item']} {r['strength']} ({r['quantity']})" for r in rows if int(float(r["quantity"])) < 10]
    return f"{len(rows)} stock lines. Low stock (<10): {', '.join(low) or 'none'}."


@mcp.prompt()
def pharmacy_assistant() -> str:
    """Reusable system prompt for a pharmacy stock assistant."""
    return ("You are a careful community-pharmacy stock assistant. Answer only from tool results. "
            "Use record_sale only when the user clearly asks to record a sale, and relay any refusal plainly.")


if __name__ == "__main__":
    mcp.run()