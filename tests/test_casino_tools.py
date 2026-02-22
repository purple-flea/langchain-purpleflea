"""Tests for the Casino LangChain tools."""

import json

import responses

from langchain_purpleflea.casino import (
    CasinoDeposit,
    CasinoGetBalance,
    CasinoGetGame,
    CasinoGetGameHistory,
    CasinoListGames,
    CasinoPlay,
    CasinoWithdraw,
)

BASE = "https://api.purpleflea.com"
PREFIX = "/api/v1"
API_KEY = "sk_test_key"


def _url(path: str) -> str:
    return f"{BASE}{PREFIX}/{path.lstrip('/')}"


# -- CasinoPlay -------------------------------------------------------------


@responses.activate
def test_casino_play_basic():
    responses.post(
        _url("games/coin_flip/play"),
        json={"result": "win", "payout": 19.6, "proof": "abc123"},
    )
    tool = CasinoPlay(api_key=API_KEY)
    result = json.loads(tool.invoke({"game_id": "coin_flip", "bet_amount": 10.0}))
    assert result["result"] == "win"
    assert result["payout"] == 19.6


@responses.activate
def test_casino_play_with_options():
    responses.post(
        _url("games/dice/play"),
        json={"result": "win", "roll": 72, "payout": 20.0},
    )
    tool = CasinoPlay(api_key=API_KEY)
    result = json.loads(
        tool.invoke({
            "game_id": "dice",
            "bet_amount": 10.0,
            "options": {"target": 50, "direction": "over"},
        })
    )
    assert result["roll"] == 72


# -- CasinoGetBalance -------------------------------------------------------


@responses.activate
def test_casino_get_balance():
    responses.get(_url("wallet/balance"), json={"balance": 250.0, "currency": "USD"})
    tool = CasinoGetBalance(api_key=API_KEY)
    result = json.loads(tool.invoke({}))
    assert result["balance"] == 250.0


# -- CasinoDeposit ----------------------------------------------------------


@responses.activate
def test_casino_deposit():
    responses.post(_url("wallet/deposit"), json={"balance": 350.0})
    tool = CasinoDeposit(api_key=API_KEY)
    result = json.loads(tool.invoke({"amount": 100.0, "currency": "USDC"}))
    assert result["balance"] == 350.0


# -- CasinoWithdraw ---------------------------------------------------------


@responses.activate
def test_casino_withdraw():
    responses.post(_url("wallet/withdraw"), json={"balance": 150.0})
    tool = CasinoWithdraw(api_key=API_KEY)
    result = json.loads(tool.invoke({"amount": 100.0}))
    assert result["balance"] == 150.0


# -- CasinoListGames --------------------------------------------------------


@responses.activate
def test_casino_list_games():
    responses.get(_url("games"), json={"games": [{"id": "coin_flip"}, {"id": "dice"}]})
    tool = CasinoListGames(api_key=API_KEY)
    result = json.loads(tool.invoke({}))
    assert len(result["games"]) == 2


# -- CasinoGetGame ----------------------------------------------------------


@responses.activate
def test_casino_get_game():
    responses.get(
        _url("games/coin_flip"),
        json={"id": "coin_flip", "name": "Coin Flip", "house_edge": 0.02},
    )
    tool = CasinoGetGame(api_key=API_KEY)
    result = json.loads(tool.invoke({"game_id": "coin_flip"}))
    assert result["name"] == "Coin Flip"


# -- CasinoGetGameHistory ---------------------------------------------------


@responses.activate
def test_casino_get_game_history():
    responses.get(_url("games/history"), json={"history": [{"id": "b1", "result": "win"}]})
    tool = CasinoGetGameHistory(api_key=API_KEY)
    result = json.loads(tool.invoke({}))
    assert len(result["history"]) == 1


@responses.activate
def test_casino_get_game_history_with_filters():
    responses.get(_url("games/history"), json={"history": []})
    tool = CasinoGetGameHistory(api_key=API_KEY)
    result = json.loads(tool.invoke({"limit": 5, "game_id": "dice"}))
    assert result["history"] == []


# -- Tool metadata -----------------------------------------------------------


def test_tool_names_are_unique():
    tools = [
        CasinoPlay(api_key=API_KEY),
        CasinoGetBalance(api_key=API_KEY),
        CasinoDeposit(api_key=API_KEY),
        CasinoWithdraw(api_key=API_KEY),
        CasinoListGames(api_key=API_KEY),
        CasinoGetGame(api_key=API_KEY),
        CasinoGetGameHistory(api_key=API_KEY),
    ]
    names = [t.name for t in tools]
    assert len(names) == len(set(names)), "Duplicate tool names found"


def test_all_tools_have_descriptions():
    tools = [
        CasinoPlay(api_key=API_KEY),
        CasinoGetBalance(api_key=API_KEY),
        CasinoDeposit(api_key=API_KEY),
        CasinoWithdraw(api_key=API_KEY),
        CasinoListGames(api_key=API_KEY),
        CasinoGetGame(api_key=API_KEY),
        CasinoGetGameHistory(api_key=API_KEY),
    ]
    for tool in tools:
        assert len(tool.description) > 20, f"{tool.name} has a too-short description"
