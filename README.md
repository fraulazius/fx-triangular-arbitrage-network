# FX Triangular Arbitrage Network

A graph-based Python project for detecting triangular arbitrage opportunities in a synthetic foreign-exchange network.

The model represents currencies as nodes and exchange rates as directed edges, then searches for profitable three-currency loops of the form:

```text
Currency A -> Currency B -> Currency C -> Currency A
```

> **Research / educational project.** Exchange rates in this repository are synthetic and do not represent live FX market prices.

## Overview

The project builds a directed foreign-exchange network containing:

- 100 currencies;
- 500 currency pairs;
- 1,000 directed conversion edges;
- simulated bid/ask friction through a per-conversion spread;
- deliberately injected arbitrage opportunities for validation.

The algorithm evaluates triangular currency cycles and identifies those for which the final capital exceeds the initial capital after all three conversions.

## Network Representation

Each currency is represented as a node in a directed graph.

Each available conversion is represented by an edge:

```text
USD -> EUR
EUR -> GBP
GBP -> USD
```

Every edge stores:

- the simulated exchange rate;
- a logarithmic edge weight.

The logarithmic transformation is defined as:

```text
weight = -log(exchange_rate)
```

This converts multiplication of exchange rates along a cycle into addition of edge weights, linking arbitrage detection to standard graph-theory formulations based on negative cycles.

## Synthetic FX Market

Each currency receives a synthetic reference value generated from a log-normal distribution.

A theoretically consistent exchange rate between currencies A and B is derived from their relative reference values. A spread is then applied to each conversion so that a simple round trip is normally unprofitable.

The project intentionally injects several pricing inconsistencies into selected currency triangles. These anomalies provide known test cases for checking whether the arbitrage-detection logic works as expected.

## Arbitrage Detection

For each combination of three currencies, the algorithm evaluates both possible cycle directions.

For a cycle:

```text
A -> B -> C -> A
```

the final capital is:

```text
final_capital = initial_capital * rate_AB * rate_BC * rate_CA
```

The cycle is considered an arbitrage opportunity when the resulting profit exceeds the configured minimum threshold.

Detected opportunities are ranked by percentage profit.

## Validation

With the default random seed and parameters, the model successfully detects the deliberately injected arbitrage opportunities.

Because one modified exchange-rate edge can participate in additional triangles when other edges are present in the network, the algorithm may also identify profitable cycles beyond the three originally injected test triangles.

## Network Analysis

The project also reports basic network statistics:

- number of nodes;
- number of directed edges;
- network density;
- average degree.

Two visualizations are produced:

1. the FX network using a spring-layout representation;
2. the adjacency matrix of the directed currency network.

## Project Structure

```text
fx-triangular-arbitrage-network/
├── fx_triangular_arbitrage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Create a virtual environment if desired, then install the dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python fx_triangular_arbitrage.py
```

The script prints detected arbitrage cycles and network statistics, then displays the network and adjacency-matrix visualizations.

## Main Parameters

The main simulation parameters can be changed directly in the script:

```python
INITIAL_CAPITAL = 1.0
NUM_PAIRS = 500
SPREAD = 0.001
MIN_PROFIT_PERCENT = 0.0001
```

The random seed is fixed to make the simulation reproducible.

## Technology

- Python
- NumPy
- NetworkX
- Matplotlib

## Limitations

This project is a synthetic market simulation rather than a live arbitrage system.

In particular:

- exchange rates are simulated rather than downloaded from FX venues;
- the spread is modeled with a simplified constant parameter;
- execution latency, market depth, commissions, slippage, and liquidity constraints are not modeled;
- the search is restricted to triangular cycles;
- detected theoretical opportunities should not be interpreted as executable market trades.

A natural extension would be to replace the synthetic rates with synchronized bid/ask quotes and evaluate opportunities after realistic transaction and execution costs.

## Disclaimer

This repository is for educational and research purposes only and does not constitute investment advice.
