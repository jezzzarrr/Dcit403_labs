"""Tools for the Makola Market helper. The model only NAMES a tool; this code runs it."""
import ast
import operator as op

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
       ast.Div: op.truediv, ast.USub: op.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        expr = expression.replace(",", "")
        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


def wiki_lookup(title: str) -> str:
    import requests
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + title.strip().replace(" ", "_"))
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"})
    except Exception as e:
        return f"Error: could not reach Wikipedia ({e})."
    if r.status_code != 200:
        return f"No Wikipedia page found for '{title}'."
    return r.json().get("extract", "")[:800]


# Stretch task: a FIXED, made-up rate table (value of 1 unit in GHS). Not real market rates.
RATES_TO_GHS = {"GHS": 1.0, "USD": 15.0, "EUR": 16.0, "GBP": 19.0, "NGN": 0.01}


def convert_currency(args: str) -> str:
    """Input format: amount, FROM, TO   e.g.  7400, GHS, USD"""
    try:
        amount, src, dst = [p.strip() for p in args.split(",")]
        src, dst = src.upper(), dst.upper()
        if src not in RATES_TO_GHS or dst not in RATES_TO_GHS:
            return f"Error: supported currencies are {', '.join(RATES_TO_GHS)}."
        value = float(amount.replace(",", "")) * RATES_TO_GHS[src] / RATES_TO_GHS[dst]
        return f"{round(value, 2)} {dst} (fixed lab rates)"
    except Exception:
        return "Error: use the format 'amount, FROM, TO', for example '7400, GHS, USD'."


TOOLS = {"calculator": calculator, "wiki_lookup": wiki_lookup, "convert_currency": convert_currency}

if __name__ == "__main__":
    print(calculator("4*185 + 3*95"))               # 1025
    print(calculator("1,200 - 1025"))               # 175
    print(calculator("__import__('os')"))           # must be an Error
    print(convert_currency("7400, GHS, USD"))
    print(wiki_lookup("Techiman"))