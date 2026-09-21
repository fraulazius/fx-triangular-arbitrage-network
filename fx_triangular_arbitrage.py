import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations


# ============================================================
# 1. PARAMETERS
# ============================================================

np.random.seed(42)

INITIAL_CAPITAL = 1.0

# Number of currency pairs in the network.
# Each pair generates two directed edges.
NUM_PAIRS = 500

# Spread applied to every conversion
SPREAD = 0.001

# Minimum arbitrage profit considered relevant
MIN_PROFIT_PERCENT = 0.0001


# ============================================================
# 2. 100 CURRENCIES
# ============================================================

currencies = [
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
    "CNY", "HKD", "SGD", "SEK", "NOK", "DKK", "PLN", "CZK",
    "HUF", "RON", "BGN", "TRY", "RUB", "INR", "KRW", "BRL",
    "MXN", "ZAR", "AED", "SAR", "QAR", "KWD", "BHD", "OMR",
    "ILS", "THB", "MYR", "IDR", "PHP", "VND", "PKR", "BDT",
    "LKR", "NPR", "KZT", "UZS", "GEL", "AMD", "AZN", "MAD",
    "TND", "DZD", "EGP", "NGN", "GHS", "KES", "UGX", "TZS",
    "RWF", "XOF", "XAF", "ETB", "MUR", "SCR", "BWP", "NAD",
    "ZMW", "AOA", "MZN", "MGA", "ISK", "ALL", "MKD", "RSD",
    "BAM", "MDL", "UAH", "BYN", "JOD", "LBP", "IQD", "IRR",
    "AFN", "MNT", "KHR", "LAK", "MMK", "BND", "FJD", "PGK",
    "WST", "TOP", "SBD", "VUV", "XPF", "JMD", "TTD", "BBD",
    "BSD", "DOP", "CRC", "GTQ"
]

print("Number of currencies:", len(currencies))


# ============================================================
# 3. SYNTHETIC VALUE OF EACH CURRENCY
# ============================================================

# Each currency receives a synthetic reference value relative to
# a common unit. These are NOT real market prices.

base_value = {}

for currency in currencies:
    base_value[currency] = np.exp(
        np.random.normal(0, 1)
    )

# USD is used as reference
base_value["USD"] = 1.0


# ============================================================
# 4. CHOOSE WHICH CURRENCY PAIRS EXIST
# ============================================================

pairs = set()

# First ensure the network is connected
for i in range(len(currencies)):
    currency_a = currencies[i]
    currency_b = currencies[
        (i + 1) % len(currencies)
    ]

    pair = tuple(
        sorted((currency_a, currency_b))
    )

    pairs.add(pair)

# Pairs required for selected injected arbitrage cycles
injected_triangles = [
    ("EUR", "USD", "GBP"),
    ("JPY", "CHF", "CAD"),
    ("AUD", "NZD", "SGD")
]

for a, b, c in injected_triangles:
    pairs.add(tuple(sorted((a, b))))
    pairs.add(tuple(sorted((b, c))))
    pairs.add(tuple(sorted((c, a))))

# Add random pairs until NUM_PAIRS is reached
while len(pairs) < NUM_PAIRS:
    a, b = np.random.choice(
        currencies,
        size=2,
        replace=False
    )

    pair = tuple(sorted((a, b)))
    pairs.add(pair)

print("Number of currency pairs:", len(pairs))


# ============================================================
# 5. BUILD THE NETWORK
# ============================================================

G = nx.DiGraph()
G.add_nodes_from(currencies)

for a, b in pairs:
    mid_ab = base_value[a] / base_value[b]
    mid_ba = 1 / mid_ab

    # Apply spread so a simple A -> B -> A round trip loses money.
    rate_ab = mid_ab * (1 - SPREAD)
    rate_ba = mid_ba * (1 - SPREAD)

    G.add_edge(
        a,
        b,
        rate=rate_ab,
        log_weight=-np.log(rate_ab)
    )

    G.add_edge(
        b,
        a,
        rate=rate_ba,
        log_weight=-np.log(rate_ba)
    )

print("Number of nodes:", G.number_of_nodes())
print("Number of directed edges:", G.number_of_edges())


# ============================================================
# 6. INJECT SOME ARBITRAGE OPPORTUNITIES
# ============================================================

target_profits = [
    0.012,    # 1.2%
    0.008,    # 0.8%
    0.005     # 0.5%
]

for triangle, target_profit in zip(
    injected_triangles,
    target_profits
):
    a, b, c = triangle

    current_product = (
        G[a][b]["rate"]
        * G[b][c]["rate"]
        * G[c][a]["rate"]
    )

    target_product = 1 + target_profit

    adjustment = (
        target_product
        / current_product
    )

    # Modify one edge to inject a pricing inconsistency.
    G[c][a]["rate"] *= adjustment

    G[c][a]["log_weight"] = -np.log(
        G[c][a]["rate"]
    )


# ============================================================
# 7. FIND TRIANGULAR ARBITRAGE
# ============================================================

arbitrages = []

# combinations() considers each group of 3 currencies once.
# For each triple, evaluate both possible cycle directions.
for a, b, c in combinations(currencies, 3):
    possible_cycles = [
        (a, b, c),
        (a, c, b)
    ]

    for cycle in possible_cycles:
        x, y, z = cycle

        if not (
            G.has_edge(x, y)
            and G.has_edge(y, z)
            and G.has_edge(z, x)
        ):
            continue

        rate_1 = G[x][y]["rate"]
        rate_2 = G[y][z]["rate"]
        rate_3 = G[z][x]["rate"]

        final_capital = (
            INITIAL_CAPITAL
            * rate_1
            * rate_2
            * rate_3
        )

        profit_percentage = (
            (final_capital - INITIAL_CAPITAL)
            / INITIAL_CAPITAL
        ) * 100

        total_log_weight = (
            G[x][y]["log_weight"]
            + G[y][z]["log_weight"]
            + G[z][x]["log_weight"]
        )

        if profit_percentage > MIN_PROFIT_PERCENT:
            arbitrages.append(
                {
                    "cycle": (
                        x,
                        y,
                        z,
                        x
                    ),
                    "final_capital": final_capital,
                    "profit": profit_percentage,
                    "log_weight": total_log_weight
                }
            )


# ============================================================
# 8. SORT ARBITRAGE BY PROFIT
# ============================================================

arbitrages.sort(
    key=lambda x: x["profit"],
    reverse=True
)


# ============================================================
# 9. PRINT RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("ARBITRAGE OPPORTUNITIES")
print("=" * 70)

if len(arbitrages) == 0:
    print("No arbitrage opportunities found.")

else:
    print(
        f"Total arbitrage opportunities: "
        f"{len(arbitrages)}"
    )

    print()

    for i, arb in enumerate(arbitrages, start=1):
        path = " -> ".join(
            arb["cycle"]
        )

        print(f"{i}. {path}")
        print(
            f"   Final capital: "
            f"{arb['final_capital']:.6f}"
        )
        print(
            f"   Profit: "
            f"{arb['profit']:.4f}%"
        )
        print(
            f"   Log weight: "
            f"{arb['log_weight']:.6f}"
        )
        print()


# ============================================================
# 10. NETWORK STATISTICS
# ============================================================

print("=" * 70)
print("NETWORK STATISTICS")
print("=" * 70)

print(
    "Nodes:",
    G.number_of_nodes()
)

print(
    "Edges:",
    G.number_of_edges()
)

print(
    "Density:",
    round(nx.density(G), 4)
)

print(
    "Average degree:",
    round(
        sum(dict(G.degree()).values())
        / G.number_of_nodes(),
        2
    )
)


# ============================================================
# 11. PLOT THE NETWORK
# ============================================================

plt.figure(
    figsize=(14, 14)
)

pos = nx.spring_layout(
    G,
    seed=42,
    k=0.3
)

nx.draw_networkx_nodes(
    G,
    pos,
    node_size=120,
    alpha=0.9
)

nx.draw_networkx_edges(
    G,
    pos,
    width=0.3,
    alpha=0.12,
    arrows=False
)

nx.draw_networkx_labels(
    G,
    pos,
    font_size=5
)

plt.title(
    "FX Network - 100 currencies"
)

plt.axis("off")
plt.tight_layout()
plt.show()


# ============================================================
# 12. ADJACENCY MATRIX
# ============================================================

node_order = currencies

A = nx.to_numpy_array(
    G,
    nodelist=node_order,
    weight=None
)

plt.figure(
    figsize=(12, 12)
)

plt.imshow(
    A,
    interpolation="nearest",
    aspect="auto"
)

plt.title(
    "Adjacency Matrix - FX Network"
)

plt.xlabel(
    "Destination currency"
)

plt.ylabel(
    "Origin currency"
)

# Show one label every 5 currencies to reduce clutter.
step = 5

positions = range(
    0,
    len(node_order),
    step
)

labels = [
    node_order[i]
    for i in positions
]

plt.xticks(
    positions,
    labels,
    rotation=90,
    fontsize=7
)

plt.yticks(
    positions,
    labels,
    fontsize=7
)

plt.colorbar(
    label="Edge exists"
)

plt.tight_layout()
plt.show()
