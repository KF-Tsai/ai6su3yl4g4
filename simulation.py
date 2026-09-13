import numpy as np
import matplotlib.pyplot as plt

def etf_market_making_sim(steps=1000, s0=100.0, sigma=0.2, gamma=0.1, k=1.5, premium_pct=0.005):
    """
    ETF 造市模擬器 (包含歷史溢價與庫存偏移)
    :param s0: 初始理論淨值
    :param sigma: 避險誤差波動率
    :param gamma: 風險趨避係數
    :param k: 訂單簿流動性參數
    :param premium_pct: 歷史常態折溢價 (e.g., 0.005 = 0.5% 溢價)
    """
    np.random.seed(42)
    
    # 儲存陣列
    s = np.zeros(steps)         # 理論淨值
    s_adj = np.zeros(steps)     # 調整溢價後的市場均衡淨值
    r = np.zeros(steps)         # 保留價格 (報價中樞)
    ask = np.zeros(steps)
    bid = np.zeros(steps)
    q = np.zeros(steps)         # 庫存
    
    s[0] = s0
    
    # 預先計算半價差 (假設波動率固定)
    half_spread = (gamma * sigma**2) / 2 + (1 / gamma) * np.log(1 + gamma / k)
    
    # 到達率控制參數 (控制交易頻率)
    A = 0.8 
    
    for t in range(1, steps):
        # 1. 模擬 ETF 理論淨值隨機漫步 (Brownian Motion)
        s[t] = s[t-1] + np.random.normal(0, sigma)
        
        # 2. 加上常態折溢價，算出市場均衡淨值
        s_adj[t] = s[t] * (1 + premium_pct)
        
        # 3. 計算保留價格 (加入庫存偏移 Skew)
        r[t] = s_adj[t] - q[t-1] * gamma * (sigma**2)
        
        # 4. 設定買賣報價
        ask[t] = r[t] + half_spread
        bid[t] = r[t] - half_spread
        
        # 5. 模擬市場對造市商報價的打擊 (成交機率依賴於報價與均衡價格的距離)
        # 市場向造市商買 (造市商賣出 Ask，庫存減少)
        prob_buy = A * np.exp(-k * max(0, ask[t] - s_adj[t]))
        # 市場向造市商賣 (造市商買入 Bid，庫存增加)
        prob_sell = A * np.exp(-k * max(0, s_adj[t] - bid[t]))
        
        q[t] = q[t-1]
        
        # 執行交易判定
        if np.random.rand() < prob_buy:
            q[t] -= 1  # 造市商賣出
        if np.random.rand() < prob_sell:
            q[t] += 1  # 造市商買入

    # 視覺化圖表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    ax1.plot(s, label='Theoretical NAV (s)', linestyle='--', color='gray')
    ax1.plot(s_adj, label=f'Market Fair Value with Premium (s_adj)', color='black', alpha=0.7)
    ax1.plot(r, label='Reservation Price (r)', color='blue')
    ax1.fill_between(range(steps), bid, ask, color='lightblue', alpha=0.3, label='Bid-Ask Spread')
    ax1.set_title('ETF Market Making Quote Skewing')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    
    ax2.plot(q, color='red', label='Inventory (q)')
    ax2.set_title('Market Maker Inventory')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Position')
    ax2.legend(loc='upper left')
    ax2.axhline(0, color='black', linestyle='--')
    
    plt.tight_layout()
    plt.show()

# 執行模擬
etf_market_making_sim()