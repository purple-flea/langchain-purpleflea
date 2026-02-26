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
from langchain_purpleflea.wallet import BalanceTool, SwapTool, WalletTool
from langchain_purpleflea.domains import DomainSearchTool, DomainPurchaseTool, DNSTool
from langchain_purpleflea.toolkit import PurpleFleatoolkit

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
    # Wallet
    "WalletTool",
    "SwapTool",
    "BalanceTool",
    # Domains
    "DomainSearchTool",
    "DomainPurchaseTool",
    "DNSTool",
    # Toolkit
    "PurpleFleatoolkit",
]

__version__ = "0.1.1"
