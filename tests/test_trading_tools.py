"""Tests for the Trading LangChain tools."""

import json

import responses

from langchain_purpleflea.trading import (
    TradingClosePosition,
    TradingGetMarket,
    TradingGetOrderbook,
    TradingGetPosition,
    TradingListMarkets,
    TradingListPositions,
    TradingOpenPosition,
)

BASE = "https://api.purpleflea.com"
PREFIX = "/v1"
API_KEY = "sk_test_key"


def _url(path: str) -> str:
    return f"{BASE}{PREFIX}/{path.lstrip('/')}"


# -- TradingOpenPosition -----------------------------------------------------


@responses.activate
def test_open_position_basic():
    responses.post(
        _url("positions"),
        json={"position_id": "p1", "status": "open", "entry_price": 50000},
    )
    tool = TradingOpenPosition(api_key=API_KEY)
    result = json.loads(
        tool.invoke({"market_id": "BTC-USD", "side": "long", "size": 100.0})
    )
    assert result["position_id"] == "p1"
    assert result["status"] == "open"


@responses.activate
def test_open_position_with_leverage():
    responses.post(
        _url("positions"),
        json={"position_id": "p2", "status": "open", "leverage": 10},
    )
    tool = TradingOpenPosition(api_key=API_KEY)
    result = json.loads(
        tool.invoke({
            "market_id": "ETH-USD",
            "side": "short",
            "size": 500.0,
            "leverage": 10,
        })
    )
    assert result["leverage"] == 10


# -- TradingClosePosition ---------------------------------------------------


@responses.activate
def test_close_position():
    responses.post(
        _url("positions/p1/close"),
        json={"position_id": "p1", "status": "closed", "realized_pnl": 42.5},
    )
    tool = TradingClosePosition(api_key=API_KEY)
    result = json.loads(tool.invoke({"position_id": "p1"}))
    assert result["status"] == "closed"
    assert result["realized_pnl"] == 42.5


# -- TradingGetPosition -----------------------------------------------------


@responses.activate
def test_get_position():
    responses.get(
        _url("positions/p1"),
        json={"position_id": "p1", "unrealized_pnl": 15.0, "market_id": "BTC-USD"},
    )
    tool = TradingGetPosition(api_key=API_KEY)
    result = json.loads(tool.invoke({"position_id": "p1"}))
    assert result["unrealized_pnl"] == 15.0


# -- TradingListPositions ---------------------------------------------------


@responses.activate
def test_list_positions():
    responses.get(
        _url("positions"),
        json={"positions": [{"position_id": "p1"}, {"position_id": "p2"}]},
    )
    tool = TradingListPositions(api_key=API_KEY)
    result = json.loads(tool.invoke({}))
    assert len(result["positions"]) == 2


@responses.activate
def test_list_positions_with_filter():
    responses.get(_url("positions"), json={"positions": []})
    tool = TradingListPositions(api_key=API_KEY)
    result = json.loads(tool.invoke({"status": "closed"}))
    assert result["positions"] == []


# -- TradingListMarkets -----------------------------------------------------


@responses.activate
def test_list_markets():
    responses.get(
        _url("markets"),
        json={"markets": [{"id": "BTC-USD"}, {"id": "TSLA-PERP"}]},
    )
    tool = TradingListMarkets(api_key=API_KEY)
    result = json.loads(tool.invoke({}))
    assert len(result["markets"]) == 2


# -- TradingGetMarket -------------------------------------------------------


@responses.activate
def test_get_market():
    responses.get(
        _url("markets/BTC-USD"),
        json={"id": "BTC-USD", "price": 50000, "volume_24h": 1_000_000},
    )
    tool = TradingGetMarket(api_key=API_KEY)
    result = json.loads(tool.invoke({"market_id": "BTC-USD"}))
    assert result["price"] == 50000


# -- TradingGetOrderbook ----------------------------------------------------


@responses.activate
def test_get_orderbook():
    responses.get(
        _url("markets/BTC-USD/orderbook"),
        json={"bids": [[49990, 1.5]], "asks": [[50010, 2.0]]},
    )
    tool = TradingGetOrderbook(api_key=API_KEY)
    result = json.loads(tool.invoke({"market_id": "BTC-USD"}))
    assert len(result["bids"]) == 1
    assert len(result["asks"]) == 1


# -- Tool metadata -----------------------------------------------------------


def test_tool_names_are_unique():
    tools = [
        TradingOpenPosition(api_key=API_KEY),
        TradingClosePosition(api_key=API_KEY),
        TradingGetPosition(api_key=API_KEY),
        TradingListPositions(api_key=API_KEY),
        TradingListMarkets(api_key=API_KEY),
        TradingGetMarket(api_key=API_KEY),
        TradingGetOrderbook(api_key=API_KEY),
    ]
    names = [t.name for t in tools]
    assert len(names) == len(set(names)), "Duplicate tool names found"


def test_all_tools_have_descriptions():
    tools = [
        TradingOpenPosition(api_key=API_KEY),
        TradingClosePosition(api_key=API_KEY),
        TradingGetPosition(api_key=API_KEY),
        TradingListPositions(api_key=API_KEY),
        TradingListMarkets(api_key=API_KEY),
        TradingGetMarket(api_key=API_KEY),
        TradingGetOrderbook(api_key=API_KEY),
    ]
    for tool in tools:
        assert len(tool.description) > 20, f"{tool.name} has a too-short description"
