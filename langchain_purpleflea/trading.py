"""Purple Flea Trading tools for LangChain agents."""

import json
import requests
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class TradingInput(BaseModel):
    action: str = Field(
        description=(
            "Action to perform. One of: register, account, open_position, close_position, "
            "positions, history, portfolio, referral_stats"
        )
    )
    coin: Optional[str] = Field(default=None, description="Market symbol e.g. BTC, TSLA, GOLD")
    side: Optional[str] = Field(default=None, description="long or short")
    size_usd: Optional[float] = Field(default=None, description="Position size in USD")
    leverage: Optional[int] = Field(default=None, description="Leverage multiplier (1-50)")
    position_id: Optional[str] = Field(default=None, description="Position ID for closing")
    hl_wallet_address: Optional[str] = Field(default=None, description="Hyperliquid wallet address for registration")
    hl_signing_key: Optional[str] = Field(default=None, description="Hyperliquid signing key for registration")


class MarketsInput(BaseModel):
    category: Optional[str] = Field(
        default=None,
        description="Market category: stocks, commodities, crypto, forex, rwa, or leave empty for all"
    )
    coin: Optional[str] = Field(default=None, description="Specific coin symbol for details/price")


class PositionsInput(BaseModel):
    action: str = Field(description="One of: list, portfolio, history")
    limit: Optional[int] = Field(default=50, description="Number of history entries (max 200)")


class TradingTool(BaseTool):
    """LangChain tool for autonomous trading via Purple Flea Trading API."""

    name: str = "purple_flea_trading"
    description: str = (
        "Trade 275+ perpetual futures markets via Purple Flea Trading (powered by Hyperliquid). "
        "Markets include stocks (TSLA, NVDA, AAPL), commodities (GOLD, SILVER, OIL), "
        "crypto (BTC, ETH, SOL), forex (EUR, JPY), and indices (SPX, JP225). "
        "Leverage up to 50x. Real on-chain execution. Earn 20% of referred agents' trading fees. "
        "Actions: register (needs hl_wallet_address + hl_signing_key), account, open_position "
        "(coin, side, size_usd, leverage), close_position (position_id), positions, history, "
        "portfolio, referral_stats"
    )
    args_schema: Type[BaseModel] = TradingInput
    return_direct: bool = False

    api_key: Optional[str] = None
    referral_code: Optional[str] = None
    base_url: str = "https://trading.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None, referral_code: Optional[str] = None,
                 base_url: str = "https://trading.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.referral_code = referral_code
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str, coin: Optional[str] = None, side: Optional[str] = None,
             size_usd: Optional[float] = None, leverage: Optional[int] = None,
             position_id: Optional[str] = None, hl_wallet_address: Optional[str] = None,
             hl_signing_key: Optional[str] = None) -> str:
        try:
            if action == "register":
                payload = {
                    "hl_wallet_address": hl_wallet_address,
                    "hl_signing_key": hl_signing_key,
                }
                if self.referral_code:
                    payload["referral_code"] = self.referral_code
                r = requests.post(f"{self.base_url}/auth/register", json=payload, timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "account":
                r = requests.get(f"{self.base_url}/auth/account",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "open_position":
                payload = {
                    "coin": coin,
                    "side": side,
                    "size_usd": size_usd,
                    "leverage": leverage or 1,
                }
                r = requests.post(f"{self.base_url}/trade/open",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "close_position":
                r = requests.post(f"{self.base_url}/trade/close",
                                  json={"position_id": position_id},
                                  headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "positions":
                r = requests.get(f"{self.base_url}/trade/positions",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "history":
                r = requests.get(f"{self.base_url}/trade/history",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "portfolio":
                r = requests.get(f"{self.base_url}/trade/portfolio",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "referral_stats":
                r = requests.get(f"{self.base_url}/referral/stats",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            else:
                return json.dumps({"error": f"Unknown action: {action}"})

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


class MarketsTool(BaseTool):
    """LangChain tool for browsing Purple Flea Trading markets."""

    name: str = "purple_flea_markets"
    description: str = (
        "Browse 275+ perpetual futures markets on Purple Flea Trading. "
        "Get real-time prices, market details, and trading signals. "
        "Categories: stocks, commodities, crypto, forex, rwa (real-world assets). "
        "Use category parameter to filter, or coin parameter for specific market info/price."
    )
    args_schema: Type[BaseModel] = MarketsInput
    return_direct: bool = False

    api_key: Optional[str] = None
    base_url: str = "https://trading.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://trading.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, category: Optional[str] = None, coin: Optional[str] = None) -> str:
        try:
            if coin:
                r = requests.get(f"{self.base_url}/markets/{coin.upper()}",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)
            elif category:
                r = requests.get(f"{self.base_url}/markets/{category}",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)
            else:
                r = requests.get(f"{self.base_url}/markets",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


class PositionsTool(BaseTool):
    """LangChain tool for viewing Purple Flea Trading positions."""

    name: str = "purple_flea_positions"
    description: str = (
        "View and manage your Purple Flea Trading positions. "
        "List open positions with unrealized P&L, view trade history, "
        "or get full portfolio snapshot with exposure metrics."
    )
    args_schema: Type[BaseModel] = PositionsInput
    return_direct: bool = False

    api_key: Optional[str] = None
    base_url: str = "https://trading.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://trading.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str, limit: Optional[int] = 50) -> str:
        try:
            if action == "list":
                r = requests.get(f"{self.base_url}/trade/positions",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)
            elif action == "portfolio":
                r = requests.get(f"{self.base_url}/trade/portfolio",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)
            elif action == "history":
                r = requests.get(f"{self.base_url}/trade/history",
                                 params={"limit": limit}, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})
