# langchain-purpleflea

LangChain tools for [Purple Flea](https://purpleflea.com) — casino, trading, wallet, and domain APIs built for autonomous AI agents.

## Installation

```bash
pip install langchain-purpleflea
```

## What's Inside

| Module | Tools | Description |
|--------|-------|-------------|
| `casino` | 7 tools | Provably fair games: coin flip, dice, roulette, crash |
| `trading` | 7 tools | 275+ perpetual futures markets via Hyperliquid (1-50x leverage) |
| `wallet` | 3 tools | Non-custodial HD wallets + best-rate DEX swaps |
| `domains` | 3 tools | Register .ai/.com/.io domains, manage DNS |
| `toolkit` | all | `PurpleFleatoolkit` bundles everything |

## Quickstart — Toolkit

```python
from langchain_purpleflea import PurpleFleatoolkit
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

toolkit = PurpleFleatoolkit(
    api_key="sk_live_...",
    referral_code="YOUR_CODE",   # earn 10-20% of fees from agents you refer
)
tools = toolkit.get_tools()

agent = initialize_agent(
    tools,
    ChatOpenAI(model="gpt-4o"),
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)
agent.run("Check my casino balance, scan trading markets for opportunities, and list my open positions")
```

## Quickstart — Individual Tools

```python
from langchain_purpleflea import (
    CasinoPlay, CasinoGetBalance, CasinoListGames,
    TradingOpenPosition, TradingListMarkets, TradingClosePosition, TradingListPositions,
    WalletTool, SwapTool, BalanceTool,
    DomainSearchTool, DomainPurchaseTool,
)

API_KEY = "sk_live_..."

tools = [
    CasinoGetBalance(api_key=API_KEY),
    CasinoListGames(api_key=API_KEY),
    CasinoPlay(api_key=API_KEY),
    TradingListMarkets(api_key=API_KEY),
    TradingOpenPosition(api_key=API_KEY),
    TradingListPositions(api_key=API_KEY),
    TradingClosePosition(api_key=API_KEY),
    WalletTool(api_key=API_KEY),
    SwapTool(api_key=API_KEY),
    BalanceTool(api_key=API_KEY),
    DomainSearchTool(api_key=API_KEY),
    DomainPurchaseTool(api_key=API_KEY),
]
```

## Tool Reference

### Casino Tools

| Tool | name | Description |
|------|------|-------------|
| `CasinoPlay` | `purpleflea_casino_play` | Play a game round (coin flip, dice, roulette, crash) |
| `CasinoGetBalance` | `purpleflea_casino_get_balance` | Check casino wallet balance |
| `CasinoDeposit` | `purpleflea_casino_deposit` | Deposit funds |
| `CasinoWithdraw` | `purpleflea_casino_withdraw` | Withdraw funds |
| `CasinoListGames` | `purpleflea_casino_list_games` | List available games with house edges |
| `CasinoGetGame` | `purpleflea_casino_get_game` | Get rules and payout info for a game |
| `CasinoGetGameHistory` | `purpleflea_casino_get_game_history` | Retrieve past bets and outcomes |

### Trading Tools

| Tool | name | Description |
|------|------|-------------|
| `TradingOpenPosition` | `purpleflea_trading_open_position` | Open long/short position (1-50x leverage) |
| `TradingClosePosition` | `purpleflea_trading_close_position` | Close a position and realize P&L |
| `TradingGetPosition` | `purpleflea_trading_get_position` | Get unrealized P&L, entry price, margin |
| `TradingListPositions` | `purpleflea_trading_list_positions` | List all open/closed positions |
| `TradingListMarkets` | `purpleflea_trading_list_markets` | Browse 275+ markets with prices and volume |
| `TradingGetMarket` | `purpleflea_trading_get_market` | Get funding rate, OI, price for a market |
| `TradingGetOrderbook` | `purpleflea_trading_get_orderbook` | Get bids/asks depth for a market |

### Wallet Tools

| Tool | name | Description |
|------|------|-------------|
| `WalletTool` | `purpleflea_wallet_create` | Create HD wallet on any chain |
| `SwapTool` | `purpleflea_wallet_swap` | Swap tokens at best DEX rate |
| `BalanceTool` | `purpleflea_wallet_balance` | Check any address's token balances |

### Domain Tools

| Tool | name | Description |
|------|------|-------------|
| `DomainSearchTool` | `purpleflea_domain_search` | Search availability across 500+ TLDs |
| `DomainPurchaseTool` | `purpleflea_domain_purchase` | Register a domain |
| `DNSTool` | `purpleflea_domain_add_dns_record` | Add A/CNAME/TXT/MX DNS records |

## Referral Program

Every Purple Flea product has a referral program. Agents earn:

- **Casino**: 10% of referred agents' net losses
- **Trading**: 20% of referred agents' trading fees — forever
- **Wallet**: 10% of referred agents' swap fees

Pass `referral_code` to `PurpleFleatoolkit` or embed it in `WalletTool`/`DomainPurchaseTool` calls to activate.

## CrewAI Example

```python
from crewai import Agent, Task, Crew
from langchain_purpleflea import PurpleFleatoolkit

tools = PurpleFleatoolkit(api_key="sk_live_...").get_tools()

trader = Agent(
    role="Autonomous Trader",
    goal="Monitor 275 markets and execute profitable perpetual futures trades",
    backstory="You are a quantitative trader with access to all Hyperliquid markets via Purple Flea.",
    tools=tools,
)

task = Task(
    description="Identify the top trending market and open a $100 long position with 5x leverage.",
    expected_output="Position ID, entry price, and liquidation price.",
    agent=trader,
)

Crew(agents=[trader], tasks=[task]).kickoff()
```

## Links

- [Purple Flea](https://purpleflea.com)
- [API Docs](https://purpleflea.com/docs)
- [GitHub](https://github.com/purple-flea/langchain-purpleflea)
- [PyPI](https://pypi.org/project/langchain-purpleflea/)

## License

MIT
