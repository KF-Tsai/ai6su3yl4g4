# ETF 量化造市模擬 (基於 Avellaneda-Stoikov 模型)

本專案包含一個 Python 模擬程式，展示 ETF 造市商 (Market Maker) 如何動態調整報價。此模擬器基於經典的 **Avellaneda-Stoikov (2008) 模型** 進行改良，特別針對海外 ETF 或主題型 ETF 常見的「高追蹤誤差」與「歷史常態折溢價」結構進行了參數調整。

## 1. 核心數學模型

傳統的高頻造市模型主要依賴 Avellaneda-Stoikov (AS) 方程式來計算**保留價格 (Reservation Price, $r$)** 與**最佳半價差 (Optimal Half-Spread, $\delta$)**。

### 保留價格 (報價中樞)
保留價格是經過造市商庫存風險調整後的合理價格。造市商會圍繞此價格進行報價，藉由價格偏移 (Skew) 來管理庫存風險。

$$r(s, q) = s - q \cdot \gamma \cdot \sigma^2 \cdot T$$

參數說明：
*   $s$：理論淨值 (Fair Value / NAV)。
*   $q$：目前庫存 (正數代表持有部位/多單，負數代表放空部位/空單)。
*   $\gamma$：造市商的風險趨避係數 (Risk Aversion)。
*   $\sigma^2$：資產的變異數 (在此可視為避險誤差的波動率)。
*   $T$：時間跨度 (在連續造市中通常設為常數 $1$)。

### 最佳半價差
價差是造市商承擔庫存風險與訂單執行不確定性的補償。

$$\delta = \frac{\gamma \cdot \sigma^2}{2} + \frac{1}{\gamma} \ln\left(1 + \frac{\gamma}{k}\right)$$

參數說明：
*   $k$：訂單簿流動性深度參數。當報價越遠離中樞時，被市場打穿 (成交) 的機率會呈指數型衰減。

**最終報價：**
*   **買進報價 (Bid Price)** = $r - \delta$
*   **賣出報價 (Ask Price)** = $r + \delta$

---

## 2. 針對歷史常態折溢價的參數調整

主題型 ETF 或跨國 ETF 常因當地資金偏好、稅負或資金匯出入成本，存在結構性的常態折溢價。若造市商嚴格圍繞理論淨值 ($s$) 進行報價，將面臨嚴重的逆向選擇 (Adverse Selection)——例如在市場常態溢價時，造市商的賣價會顯得太便宜，導致累積大量空單庫存。

**調整方法：基準線偏移 (Baseline Shift)**
我們不直接使用 $s$，而是定義一個**市場均衡淨值 (Adjusted Fair Value, $s_{adj}$)**，以反映市場真實的供需平衡點：

$$s_{adj} = s \times (1 + \Pi)$$

其中 $\Pi$ 為歷史常態折溢價百分比 (例如 $0.005$ 代表 $0.5\%$ 的溢價)。

**修正後的保留價格公式：**
$$r = s \times (1 + \Pi) - q \cdot \gamma \cdot \sigma^2$$

這個微調迫使造市商的報價基準線先與市場現實對齊，隨後再套用庫存驅動的價格偏移 (Inventory Skew)。

---

## 3. Python 模擬器實作

以下 Python 腳本模擬了動態造市過程，包含 ETF 淨值的隨機漫步 (Random Walk)、折溢價調整、動態報價偏移，以及庫存的累積與消化。

### 安裝套件
執行此程式需要安裝 `numpy` 與 `matplotlib`：
```bash
pip install numpy matplotlib
```

### `etf_mm_sim.py` 程式碼

```python
import numpy as np
import matplotlib.pyplot as plt

def etf_market_making_sim(steps=1000, s0=100.0, sigma=0.2, gamma=0.1, k=1.5, premium_pct=0.005):
    """
    ETF 造市模擬器 (包含歷史溢價與庫存偏移)
    
    參數設定:
    :param s0: 初始理論淨值
    :param sigma: 避險誤差波動率
    :param gamma: 風險趨避係數
    :param k: 訂單簿流動性參數
    :param premium_pct: 歷史常態折溢價 (例如: 0.005 = 0.5% 溢價)
    """
    np.random.seed(42)
    
    # 資料儲存陣列
    s = np.zeros(steps)         # 理論淨值 (Theoretical NAV)
    s_adj = np.zeros(steps)     # 市場均衡淨值 (Premium adjusted)
    r = np.zeros(steps)         # 保留價格 (Skewed Midpoint)
    ask = np.zeros(steps)       # 賣價
    bid = np.zeros(steps)       # 買價
    q = np.zeros(steps)         # 造市商庫存
    
    s[0] = s0
    
    # 預先計算半價差 (假設波動率在模擬期間固定)
    half_spread = (gamma * sigma**2) / 2 + (1 / gamma) * np.log(1 + gamma / k)
    
    # 訂單到達率參數 (控制市場交易頻率)
    A = 0.8 
    
    for t in range(1, steps):
        # 1. 模擬 ETF 理論淨值隨機漫步 (布朗運動)
        s[t] = s[t-1] + np.random.normal(0, sigma)
        
        # 2. 套用常態折溢價，計算出市場均衡淨值
        s_adj[t] = s[t] * (1 + premium_pct)
        
        # 3. 計算保留價格 (加入庫存偏移)
        # 當庫存 (q) 為正，保留價格會向下偏移；當庫存為負，保留價格會向上偏移
        r[t] = s_adj[t] - q[t-1] * gamma * (sigma**2)
        
        # 4. 設定最終買賣報價
        ask[t] = r[t] + half_spread
        bid[t] = r[t] - half_spread
        
        # 5. 模擬市場對造市商報價的打擊
        # 市場買進 (造市商在 Ask 賣出，庫存減少)
        prob_buy = A * np.exp(-k * max(0, ask[t] - s_adj[t]))
        # 市場賣出 (造市商在 Bid 買進，庫存增加)
        prob_sell = A * np.exp(-k * max(0, s_adj[t] - bid[t]))
        
        q[t] = q[t-1]
        
        # 訂單執行邏輯
        if np.random.rand() < prob_buy:
            q[t] -= 1  # 造市商部位變空 (賣出)
        if np.random.rand() < prob_sell:
            q[t] += 1  # 造市商部位變多 (買進)

    # ==========================
    # 視覺化與繪圖
    # ==========================
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
    
    # 上半部：價格與報價走勢圖
    ax1.plot(s, label='理論淨值 ($s$)', linestyle='--', color='gray')
    ax1.plot(s_adj, label=f'市場均衡淨值 (含溢價) ($s_{{adj}}$)', color='black', alpha=0.7)
    ax1.plot(r, label='保留價格 ($r$)', color='blue')
    ax1.fill_between(range(steps), bid, ask, color='lightblue', alpha=0.3, label='買賣價差區間 (Spread)')
    ax1.set_title('ETF 造市報價與動態偏移模擬 (Market Making Quote Skewing)')
    ax1.set_ylabel('價格 (Price)')
    ax1.legend(loc='upper left')
    
    # 下半部：造市商庫存變化圖
    ax2.plot(q, color='red', label='造市商庫存 ($q$)')
    ax2.set_title('造市商庫存動態 (Market Maker Inventory)')
    ax2.set_xlabel('時間步長 (Time Step)')
    ax2.set_ylabel('庫存部位 (Position)')
    ax2.legend(loc='upper left')
    ax2.axhline(0, color='black', linestyle='--')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    etf_market_making_sim()
```

## 4. 視覺化說明
執行程式後，您會看到兩張連動的圖表：
1. **價格走勢圖 (上方)**：展示了理論淨值 (灰色虛線)、市場均衡淨值 (黑色實線) 以及造市商的保留價格中樞 (藍線)。淺藍色的區塊為造市商提供的買賣價差。您可以觀察到，當藍線偏離黑線時，表示造市商正在積極調整報價以管理風險。
2. **庫存變化圖 (下方)**：紅線顯示了造市商手上的淨庫存。您可以對照上下兩張圖，當紅線 (庫存) 大幅飆高時，上方的藍線 (報價中樞) 會隨之向下彎曲 (Skew)，藉此吸引買盤、阻擋賣盤，將庫存拉回健康水準。