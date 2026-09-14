import numpy as np
from scipy.stats import linregress

# 1. 盤口數據輸入
deltas = np.array([0.01, 0.02, 0.03, 0.04, 0.05])  # 掛單距離 (Spread from mid)
fills = np.array([120, 65, 36, 20, 11])            # 每小時平均成交次數 (Lambda)

# 2. 取自然對數
ln_fills = np.log(fills)

# 3. 執行線性迴歸 ( y = slope * x + intercept )
# 根據公式 ln(lambda) = -k * delta + ln(A)
# slope = -k, intercept = ln(A)
slope, intercept, r_value, p_value, std_err = linregress(deltas, ln_fills)

k = -slope
A = np.exp(intercept)

print(f"流動性深度參數 (k): {k:.2f}")
print(f"基準到達率 (A): {A:.2f} 次/小時")
print(f"R平方值 (配適度): {r_value**2:.4f}")