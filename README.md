# langchain-purpleflea

LangChain tools for Purple Flea — casino, trading, wallet, and domain APIs for AI agents.

## Install

```bash
pip install langchain-purpleflea
```

## Quick Start

```python
from langchain_purpleflea import PurpleFleatoolkit
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

# Initialize toolkit with your credentials
toolkit = PurpleFleatoolkit(
    api_key="sk_live_your_key",           # Casino + Wallet API key
    trading_api_key="sk_trade_your_key",  # Trading API key
    referral_code="ref_yourcode",         # Optional: earn on referred agents
)

# Get all tools
tools = toolkit.get_tools()

# Create agent
llm = ChatOpenAI(model="gpt-4o")
agent = initialize_agent(
    tools, llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Run
agent.run("Register a casino account, deposit to base chain, then play 3 coin flips at $2 each")
```

## Registration

Agents register automatically when calling `action="register"` on any tool:

```python
from langchain_purpleflea import CasinoTool

tool = CasinoTool(referral_code="ref_1234abcd")
result = tool._run(action="register")
# Returns: { "api_key": "sk_live_...", "referral_code": "ref_...", "balance": 0 }
```

## Tools

### Casino (8 games, 0.5% house edge)

```python
from langchain_purpleflea import CasinoTool

casino = CasinoTool(api_key="sk_live_...")

# Check balance
casino._run(action="balance")

# Play coin flip
casino._run(action="play_coin_flip", amount=5.0, game_params={"side": "heads"})

# Play dice
casino._run(action="play_dice", amount=2.0, game_params={"threshold": 50, "direction": "over"})

# Crash game
casino._run(action="play_crash", amount=10.0, game_params={"cashout_multiplier": 2.5})

# Kelly Criterion optimal bet
casino._run(action="kelly_optimal", game_params={"game": "coin_flip", "win_probability": 0.495})

# Referral earnings
casino._run(action="referral_stats")
```

### Trading (275+ perpetuals via Hyperliquid)

```python
from langchain_purpleflea import TradingTool, MarketsTool

# Register (one-time, requires Hyperliquid wallet)
trading = TradingTool(referral_code="ref_...")
trading._run(
    action="register",
    hl_wallet_address="0x...",
    hl_signing_key="0x..."
)

# Open position
trading = TradingTool(api_key="sk_trade_...")
trading._run(action="open_position", coin="TSLA", side="long", size_usd=1000, leverage=5)

# Browse markets
markets = MarketsTool(api_key="sk_trade_...")
markets._run(category="stocks")  # or "crypto", "commodities", "forex"
markets._run(coin="BTC")         # specific market
```

### Wallet (multi-chain, 9 networks)

```python
from langchain_purpleflea import BalanceTool, SwapTool

# Check balance + deposit addresses
balance = BalanceTool(api_key="sk_live_...")
balance._run()

# Cross-chain swap
swap = SwapTool(api_key="sk_live_...")
swap._run(from_chain="ethereum", from_token="ETH", to_chain="base", to_token="USDC", amount=0.1)
```

### Domains (via Njalla, privacy-first)

```python
from langchain_purpleflea import DomainSearchTool, DomainPurchaseTool, DNSTool

# Search availability
search = DomainSearchTool(api_key="your_key")
search._run(query="myagent.ai")

# Register domain
purchase = DomainPurchaseTool(api_key="your_key")
purchase._run(action="register", domain="myagent.ai")

# Add DNS record
dns = DNSTool(api_key="your_key")
dns._run(action="add", domain_id="dom_123", record_type="A", name="@", content="1.2.3.4")
```

## Referral System

All tools accept a `referral_code` parameter. When you refer other agents:

- **Casino**: Earn 10% of their net losses (forever)
- **Trading**: Earn 20% of their trading fees (forever)
- **Wallet**: Earn 10% of their swap fees
- **Domains**: Earn 15% of their domain purchases

3-level chain: you earn on your referrals, and on their referrals, recursively.

Get your referral code after registration:
```python
casino._run(action="referral_stats")  # includes your_referral_code field
```

## Subset Toolkits

```python
toolkit = PurpleFleatoolkit(api_key="sk_live_...")

casino_tools = toolkit.get_casino_tools()
trading_tools = toolkit.get_trading_tools()
wallet_tools = toolkit.get_wallet_tools()
domain_tools = toolkit.get_domain_tools()
```

## Links

- [Purple Flea](https://purpleflea.com)
- [Casino API docs](https://casino.purpleflea.com/docs)
- [Trading API docs](https://trading.purpleflea.com/docs)
- [For Agents guide](https://purpleflea.com/for-agents)
