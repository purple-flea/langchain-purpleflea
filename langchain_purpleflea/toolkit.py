"""Purple Flea LangChain Toolkit — all tools in one place."""

from typing import List, Optional
from langchain.tools import BaseTool

from .casino import CasinoTool
from .trading import TradingTool, MarketsTool, PositionsTool
from .wallet import WalletTool, SwapTool, BalanceTool
from .domains import DomainSearchTool, DomainPurchaseTool, DNSTool


class PurpleFleatoolkit:
    """Toolkit that bundles all Purple Flea tools for LangChain agents.

    Usage:
        from langchain_purpleflea import PurpleFleatoolkit
        from langchain.agents import initialize_agent, AgentType
        from langchain_openai import ChatOpenAI

        toolkit = PurpleFleatoolkit(
            api_key="sk_live_your_casino_key",
            trading_api_key="sk_trade_your_trading_key",
            referral_code="ref_yourcode",
        )
        tools = toolkit.get_tools()
        llm = ChatOpenAI(model="gpt-4")
        agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)
        agent.run("Check my casino balance and place a $5 coin flip bet")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        trading_api_key: Optional[str] = None,
        domains_api_key: Optional[str] = None,
        referral_code: Optional[str] = None,
        casino_base_url: str = "https://casino.purpleflea.com/api/v1",
        trading_base_url: str = "https://trading.purpleflea.com/v1",
        wallet_base_url: str = "https://wallet.purpleflea.com/v1",
        domains_base_url: str = "https://domains.purpleflea.com/v1",
    ):
        self.api_key = api_key
        self.trading_api_key = trading_api_key or api_key
        self.domains_api_key = domains_api_key or api_key
        self.referral_code = referral_code
        self.casino_base_url = casino_base_url
        self.trading_base_url = trading_base_url
        self.wallet_base_url = wallet_base_url
        self.domains_base_url = domains_base_url

    def get_tools(self) -> List[BaseTool]:
        """Return all Purple Flea tools configured with this toolkit's credentials."""
        return [
            CasinoTool(
                api_key=self.api_key,
                referral_code=self.referral_code,
                base_url=self.casino_base_url,
            ),
            TradingTool(
                api_key=self.trading_api_key,
                referral_code=self.referral_code,
                base_url=self.trading_base_url,
            ),
            MarketsTool(
                api_key=self.trading_api_key,
                base_url=self.trading_base_url,
            ),
            PositionsTool(
                api_key=self.trading_api_key,
                base_url=self.trading_base_url,
            ),
            WalletTool(
                api_key=self.api_key,
                referral_code=self.referral_code,
                base_url=self.wallet_base_url,
            ),
            SwapTool(
                api_key=self.api_key,
                base_url=self.wallet_base_url,
            ),
            BalanceTool(
                api_key=self.api_key,
                casino_base_url=self.casino_base_url,
            ),
            DomainSearchTool(
                api_key=self.domains_api_key,
                base_url=self.domains_base_url,
            ),
            DomainPurchaseTool(
                api_key=self.domains_api_key,
                referral_code=self.referral_code,
                base_url=self.domains_base_url,
            ),
            DNSTool(
                api_key=self.domains_api_key,
                base_url=self.domains_base_url,
            ),
        ]

    def get_casino_tools(self) -> List[BaseTool]:
        """Return only casino tools."""
        return [
            CasinoTool(api_key=self.api_key, referral_code=self.referral_code,
                       base_url=self.casino_base_url),
            BalanceTool(api_key=self.api_key, casino_base_url=self.casino_base_url),
        ]

    def get_trading_tools(self) -> List[BaseTool]:
        """Return only trading tools."""
        return [
            TradingTool(api_key=self.trading_api_key, referral_code=self.referral_code,
                        base_url=self.trading_base_url),
            MarketsTool(api_key=self.trading_api_key, base_url=self.trading_base_url),
            PositionsTool(api_key=self.trading_api_key, base_url=self.trading_base_url),
        ]

    def get_wallet_tools(self) -> List[BaseTool]:
        """Return only wallet tools."""
        return [
            WalletTool(api_key=self.api_key, referral_code=self.referral_code,
                       base_url=self.wallet_base_url),
            SwapTool(api_key=self.api_key, base_url=self.wallet_base_url),
            BalanceTool(api_key=self.api_key, casino_base_url=self.casino_base_url),
        ]

    def get_domain_tools(self) -> List[BaseTool]:
        """Return only domain tools."""
        return [
            DomainSearchTool(api_key=self.domains_api_key, base_url=self.domains_base_url),
            DomainPurchaseTool(api_key=self.domains_api_key, referral_code=self.referral_code,
                               base_url=self.domains_base_url),
            DNSTool(api_key=self.domains_api_key, base_url=self.domains_base_url),
        ]
