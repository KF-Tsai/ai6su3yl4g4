# ETF Market Making Simulation (Avellaneda-Stoikov Model)

This repository contains a Python simulation of an ETF Market Maker's quoting behavior, utilizing a modified version of the classic Avellaneda-Stoikov (2008) model. It specifically addresses the challenges of quoting overseas/thematic ETFs with high tracking error and historical premium/discount structures.

## 1. Core Mathematical Model 

Traditional high-frequency market making relies on the Avellaneda-Stoikov (AS) equations to calculate the **Reservation Price ($r$)** and the **Optimal Half-Spread ($\delta$)**.

### Reservation Price (Quoting Midpoint)
The reservation price is the inventory-adjusted fair value. It skews your quotes to manage inventory risk.

$$r(s, q) = s - q \cdot \gamma \cdot \sigma^2 \cdot T$$

Where:
*   $s$: Theoretical Fair Value (NAV).
*   $q$: Current Inventory (positive for long, negative for short).
*   $\gamma$: Market Maker's Risk Aversion parameter.
*   $\sigma^2$: Variance of the asset (tracking/hedging error volatility).
*   $T$: Time horizon (usually set to $1$ in continuous market making).

### Optimal Half-Spread
The spread compensates the market maker for inventory risk and order execution uncertainty.

$$\delta = \frac{\gamma \cdot \sigma^2}{2} + \frac{1}{\gamma} \ln\left(1 + \frac{\gamma}{k}\right)$$

Where:
*   $k$: Order book liquidity depth parameter. The probability of execution decays exponentially as quotes move further from the midpoint.

**Final Quotes:**
*   **Bid Price** = $r - \delta$
*   **Ask Price** = $r + \delta$

## 2. Adjusting for Historical Premium/Discount

Thematic or cross-border ETFs often exhibit structural premiums or discounts due to local capital preferences, taxes, or capital control costs. If a market maker centers their skew strictly around the theoretical NAV ($s$), they will suffer from adverse selection (e.g., constantly accumulating short inventory during a persistent premium).

**Adjustment: Baseline Shift**
Instead of skewing around $s$, we define an **Adjusted Fair Value ($s_{adj}$)** that represents the true market equilibrium:

$$s_{adj} = s \times (1 + \Pi)$$

Where $\Pi$ is the historical premium/discount percentage (e.g., $0.005$ for a $0.5\%$ premium).

**Modified Reservation Price:**
$$r = s \times (1 + \Pi) - q \cdot \gamma \cdot \sigma^2$$

This forces the quoting baseline to align with market realities before applying inventory-driven skew.

## 3. Python Simulation Code

The following script simulates the dynamic quoting process, including the random walk of the ETF NAV, premium adjustment, dynamic quote skewing, and inventory accumulation.

### Requirements
```bash
pip install numpy matplotlib
```

### `etf_mm_sim.py`

```python
import numpy as np
import matplotlib.pyplot as plt

def etf_market_making_sim(steps=1000, s0=100.0, sigma=0.2, gamma=0.1, k=1.5, premium_pct=0.005):
    """
    ETF Market Making Simulator (with Historical Premium and Inventory Skew)
    
    Parameters:
    :param s0: Initial theoretical NAV
    :param sigma: Volatility of hedging error
    :param gamma: Risk aversion coefficient
    :param k: Liquidity depth parameter
    :param premium_pct: Historical premium/discount (e.g., 0.005 = 0.5% premium)
    """
    np.random.seed(42)
    
    # Data arrays
    s = np.zeros(steps)         # Theoretical NAV
    s_adj = np.zeros(steps)     # Market Fair Value (Premium adjusted)
    r = np.zeros(steps)         # Reservation Price (Skewed Midpoint)
    ask = np.zeros(steps)
    bid = np.zeros(steps)
    q = np.zeros(steps)         # Inventory
    
    s[0] = s0
    
    # Pre-calculate half-spread (assuming constant volatility)
    half_spread = (gamma * sigma**2) / 2 + (1 / gamma) * np.log(1 + gamma / k)
    
    # Arrival rate parameter (controls trading frequency)
    A = 0.8 
    
    for t in range(1, steps):
        # 1. Simulate ETF theoretical NAV random walk (Brownian Motion)
        s[t] = s[t-1] + np.random.normal(0, sigma)
        
        # 2. Apply premium adjustment for market equilibrium
        s_adj[t] = s[t] * (1 + premium_pct)
        
        # 3. Calculate Reservation Price with inventory skew
        r[t] = s_adj[t] - q[t-1] * gamma * (sigma**2)
        
        # 4. Set Quotes
        ask[t] = r[t] + half_spread
        bid[t] = r[t] - half_spread
        
        # 5. Simulate market hitting the quotes
        # Market buys (MM sells at Ask, inventory decreases)
        prob_buy = A * np.exp(-k * max(0, ask[t] - s_adj[t]))
        # Market sells (MM buys at Bid, inventory increases)
        prob_sell = A * np.exp(-k * max(0, s_adj[t] - bid[t]))
        
        q[t] = q[t-1]
        
        # Execution logic
        if np.random.rand() < prob_buy:
            q[t] -= 1  # Market Maker gets short (sells)
        if np.random.rand() < prob_sell:
            q[t] += 1  # Market Maker gets long (buys)

    # Visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    # Price Chart
    ax1.plot(s, label='Theoretical NAV ($s$)', linestyle='--', color='gray')
    ax1.plot(s_adj, label=f'Market Fair Value with Premium ($s_{{adj}}$)', color='black', alpha=0.7)
    ax1.plot(r, label='Reservation Price ($r$)', color='blue')
    ax1.fill_between(range(steps), bid, ask, color='lightblue', alpha=0.3, label='Bid-Ask Spread')
    ax1.set_title('ETF Market Making Quote Skewing')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    
    # Inventory Chart
    ax2.plot(q, color='red', label='Inventory ($q$)')
    ax2.set_title('Market Maker Inventory')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Position')
    ax2.legend(loc='upper left')
    ax2.axhline(0, color='black', linestyle='--')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    etf_market_making_sim()
```