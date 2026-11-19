# 淨值與掛單公式推導

## 1. 期貨與指數關係

$$
F(t)(1 - b) = I(t)(1 + r \, dt - q \, dt)
$$

---

## 2. 淨值 $\text{NAV}(t)$ 推導

將 $I(t)$ 代入淨值公式，並忽略高階微小項（如 $d(r \, dt - q \, dt)$）：

$$
\begin{aligned}
\text{NAV}(t) &= \text{NAV}(0) \cdot \frac{I(t)}{I(0)(1 - d)} \cdot (1 + e) \\
&= \text{NAV}(0) \cdot \frac{F(t)(1 - b)}{I(0)(1 - d)(1 + r \, dt - q \, dt)} \cdot (1 + e) \\
&= \text{NAV}(0) \cdot \frac{F(t)}{I(0)} \cdot \left[ \frac{1 - b}{(1 - d)(1 + r \, dt - q \, dt)} \right] \cdot (1 + e) \\
&\approx \text{NAV}(0) \cdot \frac{F(t)}{I(0)} \cdot \left( \frac{1 - b}{1 + r \, dt - q \, dt - d} \right) \cdot (1 + e)
\end{aligned}
$$

---

## 3. $\text{ED}(t)$ 關係式推導

將上式兩邊同乘 $(1 + b)$，並利用 $(1 + b)(1 - b) = 1 - b^2 \approx 1$：

$$
\begin{aligned}
\text{NAV}(t)(1 + b) &= \text{NAV}(0) \cdot \frac{F(t)}{I(0)} \cdot \left[ \frac{(1 + b)(1 - b)}{1 + r \, dt - q \, dt - d} \right] \cdot (1 + e) \\
&\approx \left[ \frac{\text{NAV}(0) \cdot \frac{F(t)}{I(0)}}{1 + r \, dt - q \, dt - d} \right] \cdot (1 + e) \\
&= \text{ED}(t)(1 + e)
\end{aligned}
$$

移項整理可得 $\text{ED}(t)$：

$$
\text{ED}(t) = \frac{\text{NAV}(t)(1 + b)}{1 + e}
$$

---

## 4. 掛單公式推導

已知市價 $P(t)$ 與淨值 $\text{NAV}(t)$ 的關係為：

$$
P(t) = \text{NAV}(t)(1 + a)
$$

代入掛單公式，並在展開與除法中進行一階近似（忽略 $ae$ 與分母中的高階項）：

$$
\begin{aligned}
\text{掛單} &= \frac{P(t)}{\text{ED}(t)} - 1 \\
&= \frac{(1 + a)(1 + e)}{1 + b} - 1 \\
&\approx \frac{(1 + a + e) - (1 + b)}{1 + b} \\
&= \frac{a + e - b}{1 + b} \\
&\approx a + e - b
\end{aligned}
$$