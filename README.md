# langchain-purpleflea

LangChain tool integrations for the [Purple Flea](https://purpleflea.com) platform — provably-fair casino games and 275+ perpetual futures markets, built for autonomous AI agents.

## Installation

```bash
pip install langchain-purpleflea
```

## Tools

### Casino

| Tool | Description |
|------|-------------|
| `CasinoPlay` | Place a bet and play a round (coin flip, dice, roulette, crash) |
| `CasinoGetBalance` | Check casino wallet balance |
| `CasinoDeposit` | Deposit funds into casino wallet |
| `CasinoWithdraw` | Withdraw funds from casino wallet |
| `CasinoListGames` | List all available casino games |
| `CasinoGetGame` | Get rules and details for a specific game |
| `CasinoGetGameHistory` | Retrieve past game results |

### Trading

| Tool | Description |
|------|-------------|
| `TradingOpenPosition` | Open a long/short perpetual futures position |
| `TradingClosePosition` | Close an open position |
| `TradingGetPosition` | Get details of a specific position |
| `TradingListPositions` | List all open positions |
| `TradingListMarkets` | List all 275+ available markets |
| `TradingGetMarket` | Get price, volume, and details for a market |
| `TradingGetOrderbook` | Get the order book (bids/asks) for a market |

## Quick Start — LangChain Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from langchain_purpleflea import (
    CasinoGetBalance,
    CasinoListGames,
    CasinoPlay,
    TradingListMarkets,
    TradingOpenPosition,
    TradingListPositions,
    TradingClosePosition,
)

PURPLEFLEA_API_KEY = "sk_live_..."

# Instantiate the tools you need
tools = [
    CasinoGetBalance(api_key=PURPLEFLEA_API_KEY),
    CasinoListGames(api_key=PURPLEFLEA_API_KEY),
    CasinoPlay(api_key=PURPLEFLEA_API_KEY),
    TradingListMarkets(api_key=PURPLEFLEA_API_KEY),
    TradingOpenPosition(api_key=PURPLEFLEA_API_KEY),
    TradingListPositions(api_key=PURPLEFLEA_API_KEY),
    TradingClosePosition(api_key=PURPLEFLEA_API_KEY),
]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a trading agent with access to Purple Flea casino and trading tools."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

llm = ChatOpenAI(model="gpt-4o")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "Check my casino balance, then list available markets"})
print(result["output"])
```

## Quick Start — CrewAI

```python
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool as CrewBaseTool

from langchain_purpleflea import (
    CasinoGetBalance,
    CasinoPlay,
    TradingListMarkets,
    TradingOpenPosition,
    TradingClosePosition,
    TradingListPositions,
)

PURPLEFLEA_API_KEY = "sk_live_..."

# CrewAI accepts LangChain tools directly
langchain_tools = [
    CasinoGetBalance(api_key=PURPLEFLEA_API_KEY),
    CasinoPlay(api_key=PURPLEFLEA_API_KEY),
    TradingListMarkets(api_key=PURPLEFLEA_API_KEY),
    TradingOpenPosition(api_key=PURPLEFLEA_API_KEY),
    TradingClosePosition(api_key=PURPLEFLEA_API_KEY),
    TradingListPositions(api_key=PURPLEFLEA_API_KEY),
]

# Define a trading analyst agent
analyst = Agent(
    role="Trading Analyst",
    goal="Identify and execute profitable short-term trades on Purple Flea",
    backstory=(
        "You are an experienced quantitative trader with access to "
        "275+ perpetual futures markets via Purple Flea."
    ),
    tools=langchain_tools,
    verbose=True,
)

# Define a casino strategist agent
strategist = Agent(
    role="Casino Strategist",
    goal="Play provably-fair casino games using optimal Kelly Criterion bet sizing",
    backstory=(
        "You are a probability expert who uses the Kelly Criterion "
        "to size bets optimally on provably-fair casino games."
    ),
    tools=langchain_tools,
    verbose=True,
)

# Create tasks
scan_markets = Task(
    description=(
        "Scan available Purple Flea markets and identify the top 3 "
        "most volatile markets suitable for a short-term long position."
    ),
    expected_output="A list of 3 market IDs with reasoning for each pick.",
    agent=analyst,
)

play_casino = Task(
    description=(
        "Check the casino balance. If balance is above $50, play a "
        "coin flip game with a $10 bet."
    ),
    expected_output="The game result and updated balance.",
    agent=strategist,
)

# Run the crew
crew = Crew(agents=[analyst, strategist], tasks=[scan_markets, play_casino])
result = crew.kickoff()
print(result)
```

## Configuration

All tools accept these parameters:

| Parameter | Description |
|-----------|-------------|
| `api_key` | Your Purple Flea API key (`sk_live_...`) |
| `base_url` | Optional custom API base URL (default: `https://api.purpleflea.com`) |

## Development

```bash
git clone https://github.com/Purple-flea/langchain-purpleflea.git
cd langchain-purpleflea
pip install -e ".[dev]"
pytest
```

## License

MIT
