"""LangChain tool integrations for the Purple Flea platform."""

from langchain_purpleflea.casino import (
    CasinoDeposit,
    CasinoGetBalance,
    CasinoGetGame,
    CasinoGetGameHistory,
    CasinoListGames,
    CasinoPlay,
    CasinoWithdraw,
)
from langchain_purpleflea.trading import (
    TradingClosePosition,
    TradingGetMarket,
    TradingGetOrderbook,
    TradingGetPosition,
    TradingListMarkets,
    TradingListPositions,
    TradingOpenPosition,
)

__all__ = [
    # Casino
    "CasinoDeposit",
    "CasinoGetBalance",
    "CasinoGetGame",
    "CasinoGetGameHistory",
    "CasinoListGames",
    "CasinoPlay",
    "CasinoWithdraw",
    # Trading
    "TradingClosePosition",
    "TradingGetMarket",
    "TradingGetOrderbook",
    "TradingGetPosition",
    "TradingListMarkets",
    "TradingListPositions",
    "TradingOpenPosition",
]

__version__ = "0.1.0"
