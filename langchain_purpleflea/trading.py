"""LangChain tools for the Purple Flea Trading API."""

from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from purpleflea import TradingClient


def _client(api_key: str, base_url: str | None = None) -> TradingClient:
    return TradingClient(api_key, base_url=base_url)


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class OpenPositionInput(BaseModel):
    market_id: str = Field(
        description=(
            "The market to trade on (e.g. 'BTC-USD', 'ETH-USD', 'TSLA-PERP', 'GOLD-PERP'). "
            "Use the list_markets tool to see all available markets."
        )
    )
    side: str = Field(
        description="Trade direction: 'long' to bet on price going up, 'short' to bet on price going down."
    )
    size: float = Field(
        description="Position size in USD notional value. Must be a positive number."
    )
    leverage: Optional[int] = Field(
        default=None,
        description="Leverage multiplier (1-50). Higher leverage amplifies both gains and losses. Defaults to 1 (no leverage).",
    )


class ClosePositionInput(BaseModel):
    position_id: str = Field(
        description="The unique ID of the open position to close. Get this from open_position or list_positions."
    )


class MarketIdInput(BaseModel):
    market_id: str = Field(
        description="The market identifier (e.g. 'BTC-USD', 'TSLA-PERP')."
    )


class PositionIdInput(BaseModel):
    position_id: str = Field(description="The unique ID of the position to look up.")


class ListPositionsInput(BaseModel):
    status: Optional[str] = Field(
        default=None,
        description="Filter by position status: 'open', 'closed', or 'all'. Defaults to 'open'.",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class TradingOpenPosition(BaseTool):
    """Open a leveraged trading position on Purple Flea."""

    name: str = "purpleflea_trading_open_position"
    description: str = (
        "Open a new perpetual futures trading position on the Purple Flea platform. "
        "Supports 275+ markets including stocks (TSLA, NVDA, AAPL), crypto (BTC, ETH, SOL), "
        "commodities (GOLD, OIL), and forex (EUR/USD). "
        "Specify market_id, side ('long' or 'short'), size in USD, and optional leverage (1-50x). "
        "Returns the position ID, entry price, liquidation price, and margin required."
    )
    args_schema: Type[BaseModel] = OpenPositionInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(
        self,
        market_id: str,
        side: str,
        size: float,
        leverage: int | None = None,
    ) -> str:
        kwargs: dict[str, Any] = {}
        if leverage is not None:
            kwargs["leverage"] = leverage
        with _client(self.api_key, self.base_url) as c:
            result = c.open_position(market_id, side, size, **kwargs)
        return json.dumps(result)


class TradingClosePosition(BaseTool):
    """Close an open trading position on Purple Flea."""

    name: str = "purpleflea_trading_close_position"
    description: str = (
        "Close an existing perpetual futures position on Purple Flea. "
        "Provide the position_id obtained from open_position or list_positions. "
        "Returns the closing price, realized PnL, and final settlement details."
    )
    args_schema: Type[BaseModel] = ClosePositionInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, position_id: str) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.close_position(position_id)
        return json.dumps(result)


class TradingGetPosition(BaseTool):
    """Get details of a specific trading position."""

    name: str = "purpleflea_trading_get_position"
    description: str = (
        "Get detailed information about a specific Purple Flea trading position, "
        "including entry price, current price, unrealized PnL, margin, leverage, "
        "and liquidation price. Provide the position_id."
    )
    args_schema: Type[BaseModel] = PositionIdInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, position_id: str) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.get_position(position_id)
        return json.dumps(result)


class TradingListPositions(BaseTool):
    """List open trading positions on Purple Flea."""

    name: str = "purpleflea_trading_list_positions"
    description: str = (
        "List all trading positions on the authenticated Purple Flea account. "
        "Returns position IDs, markets, sides, sizes, entry prices, and unrealized PnL. "
        "Optionally filter by status ('open', 'closed', 'all'). "
        "Use this to review your portfolio before opening or closing positions."
    )
    args_schema: Type[BaseModel] = ListPositionsInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, status: str | None = None) -> str:
        kwargs: dict[str, Any] = {}
        if status is not None:
            kwargs["status"] = status
        with _client(self.api_key, self.base_url) as c:
            result = c.list_positions(**kwargs)
        return json.dumps(result)


class TradingListMarkets(BaseTool):
    """List available trading markets on Purple Flea."""

    name: str = "purpleflea_trading_list_markets"
    description: str = (
        "List all available perpetual futures markets on Purple Flea. "
        "Returns market IDs, names, current prices, 24h volume, and funding rates. "
        "Covers 275+ markets: stocks (TSLA-PERP, NVDA-PERP), crypto (BTC-USD, ETH-USD), "
        "commodities (GOLD-PERP), and forex. "
        "Use this to discover tradeable markets before opening a position."
    )
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.list_markets()
        return json.dumps(result)


class TradingGetMarket(BaseTool):
    """Get details for a specific trading market."""

    name: str = "purpleflea_trading_get_market"
    description: str = (
        "Get detailed information about a specific Purple Flea trading market, "
        "including current price, 24h high/low, volume, funding rate, open interest, "
        "and available leverage. Provide the market_id (e.g. 'BTC-USD')."
    )
    args_schema: Type[BaseModel] = MarketIdInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, market_id: str) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.get_market(market_id)
        return json.dumps(result)


class TradingGetOrderbook(BaseTool):
    """Get the order book for a Purple Flea trading market."""

    name: str = "purpleflea_trading_get_orderbook"
    description: str = (
        "Retrieve the current order book (bids and asks) for a Purple Flea trading market. "
        "Returns price levels and quantities for both buy and sell sides. "
        "Useful for assessing market depth and liquidity before placing a trade."
    )
    args_schema: Type[BaseModel] = MarketIdInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, market_id: str) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.get_orderbook(market_id)
        return json.dumps(result)
