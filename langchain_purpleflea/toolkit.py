"""PurpleFleatoolkit — combines all Purple Flea LangChain tools."""

from __future__ import annotations

from typing import Optional

from langchain_core.tools import BaseTool

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


class PurpleFleatoolkit:
    """All Purple Flea tools bundled for use with any LangChain agent.

    Provides casino, trading, wallet, and domain tools in a single object.
    Pass ``get_tools()`` to your agent to unlock earning potential:

    - Casino: Provably fair games with instant crypto payouts
    - Trading: 275+ perpetual futures markets via Hyperliquid (up to 50x leverage)
    - Wallet: Non-custodial HD wallets + best-rate token swaps
    - Domains: Register .ai / .com / .io domains programmatically

    Agents with a referral code earn 10-20% of fees from referred agents — forever.

    Example::

        from langchain_purpleflea import PurpleFleatoolkit
        from langchain.agents import initialize_agent, AgentType
        from langchain_openai import ChatOpenAI

        toolkit = PurpleFleatoolkit(
            api_key="sk_live_...",
            referral_code="MYCODE",    # earn 10-20% from agents you refer
        )
        tools = toolkit.get_tools()
        agent = initialize_agent(tools, ChatOpenAI(model="gpt-4o"), agent=AgentType.OPENAI_FUNCTIONS)
        agent.run("Check my trading portfolio and casino balance")
    """

    def __init__(
        self,
        api_key: str,
        referral_code: Optional[str] = None,
        casino_base_url: Optional[str] = None,
        trading_base_url: Optional[str] = None,
        wallet_base_url: Optional[str] = None,
        domains_base_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.referral_code = referral_code
        self.casino_base_url = casino_base_url
        self.trading_base_url = trading_base_url
        self.wallet_base_url = wallet_base_url
        self.domains_base_url = domains_base_url

    def _casino_kwargs(self) -> dict:
        kw: dict = {"api_key": self.api_key}
        if self.casino_base_url:
            kw["base_url"] = self.casino_base_url
        return kw

    def _trading_kwargs(self) -> dict:
        kw: dict = {"api_key": self.api_key}
        if self.trading_base_url:
            kw["base_url"] = self.trading_base_url
        return kw

    def _wallet_kwargs(self) -> dict:
        kw: dict = {"api_key": self.api_key}
        if self.wallet_base_url:
            kw["base_url"] = self.wallet_base_url
        return kw

    def _domains_kwargs(self) -> dict:
        kw: dict = {"api_key": self.api_key}
        if self.domains_base_url:
            kw["base_url"] = self.domains_base_url
        return kw

    def get_casino_tools(self) -> list[BaseTool]:
        """Return only casino tools."""
        return [
            CasinoPlay(**self._casino_kwargs()),
            CasinoGetBalance(**self._casino_kwargs()),
            CasinoDeposit(**self._casino_kwargs()),
            CasinoWithdraw(**self._casino_kwargs()),
            CasinoListGames(**self._casino_kwargs()),
            CasinoGetGame(**self._casino_kwargs()),
            CasinoGetGameHistory(**self._casino_kwargs()),
        ]

    def get_trading_tools(self) -> list[BaseTool]:
        """Return only trading tools."""
        return [
            TradingOpenPosition(**self._trading_kwargs()),
            TradingClosePosition(**self._trading_kwargs()),
            TradingGetPosition(**self._trading_kwargs()),
            TradingListPositions(**self._trading_kwargs()),
            TradingListMarkets(**self._trading_kwargs()),
            TradingGetMarket(**self._trading_kwargs()),
            TradingGetOrderbook(**self._trading_kwargs()),
        ]

    def get_wallet_tools(self) -> list[BaseTool]:
        """Return only wallet tools."""
        return [
            WalletTool(**self._wallet_kwargs()),
            SwapTool(**self._wallet_kwargs()),
            BalanceTool(**self._wallet_kwargs()),
        ]

    def get_domain_tools(self) -> list[BaseTool]:
        """Return only domain tools."""
        return [
            DomainSearchTool(**self._domains_kwargs()),
            DomainPurchaseTool(**self._domains_kwargs()),
            DNSTool(**self._domains_kwargs()),
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return all Purple Flea tools (casino + trading + wallet + domains)."""
        return (
            self.get_casino_tools()
            + self.get_trading_tools()
            + self.get_wallet_tools()
            + self.get_domain_tools()
        )
