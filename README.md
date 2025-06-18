# Option High Strategy using Shoonya API

This repository features the **Option High strategy** developed using the **Shoonya trading API**. The strategy is based on identifying option strikes that align with the **previous day's close** and the **current day's high**. These strikes are **sold early in the session** with the objective of **buying them back later as theta decay erodes their value**, aiming for a net profit.

## ⚙️ Strategy Logic
- Identify option strikes based on:
  - 📌 Previous day’s close
  - 📈 Current day’s high (open)
- Execute short (sell) positions on these strikes
- Rely on **theta decay** and price correction over the trading session
- Monitor and exit with defined profit or stop conditions

## 🔍 Key Features
- Real-time market data integration via Shoonya API
- Smart strike selection logic
- Order placement and tracking
- Logging and modular Python code
- Focused on intraday risk-managed trades

## 🤝 Learn & Contribute
This strategy is now public to help traders and developers learn about option selling strategies, time decay exploitation, and market behavior analysis. Contributions, feedback, and forks are welcome!

---

> **Disclaimer**: This code is for educational purposes only. Use responsibly and test thoroughly before deploying in live markets.

