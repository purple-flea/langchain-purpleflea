"""LangChain tools for the Purple Flea Casino API."""

from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from purpleflea import CasinoClient


def _client(api_key: str, base_url: str | None = None) -> CasinoClient:
    return CasinoClient(api_key, base_url=base_url)


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class CasinoPlayInput(BaseModel):
    game_id: str = Field(
        description="The ID of the casino game to play (e.g. 'coin_flip', 'dice', 'roulette', 'crash')."
    )
    bet_amount: float = Field(
        description="The amount to wager in USD. Must be a positive number."
    )
    options: Optional[dict[str, Any]] = Field(
        default=None,
        description=(
            "Game-specific options as a JSON object. Examples: "
            '{"side": "heads"} for coin flip, '
            '{"target": 50, "direction": "over"} for dice, '
            '{"bet_type": "red"} for roulette.'
        ),
    )


class CasinoDepositInput(BaseModel):
    amount: float = Field(description="The amount to deposit in the given currency.")
    currency: str = Field(
        default="USD",
        description="The currency to deposit (e.g. 'USD', 'USDC', 'ETH', 'BTC').",
    )


class CasinoWithdrawInput(BaseModel):
    amount: float = Field(description="The amount to withdraw in the given currency.")
    currency: str = Field(
        default="USD",
        description="The currency to withdraw (e.g. 'USD', 'USDC', 'ETH', 'BTC').",
    )


class GameIdInput(BaseModel):
    game_id: str = Field(description="The unique identifier of the casino game.")


class GameHistoryInput(BaseModel):
    limit: Optional[int] = Field(
        default=None, description="Maximum number of history entries to return."
    )
    game_id: Optional[str] = Field(
        default=None, description="Filter history to a specific game ID."
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class CasinoPlay(BaseTool):
    """Play a casino game on the Purple Flea platform."""

    name: str = "purpleflea_casino_play"
    description: str = (
        "Place a bet and play a round of a Purple Flea casino game. "
        "Supports coin flip, dice, roulette, crash, and custom-odds games. "
        "All games are provably fair with cryptographic verification. "
        "Returns the game result, payout amount, and a fairness proof hash. "
        "You MUST specify game_id and bet_amount. Optionally pass game-specific "
        "options (e.g. side for coin flip, target for dice)."
    )
    args_schema: Type[BaseModel] = CasinoPlayInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, game_id: str, bet_amount: float, options: dict[str, Any] | None = None) -> str:
        with _client(self.api_key, self.base_url) as c:
            kwargs = options or {}
            result = c.play(game_id, bet_amount, **kwargs)
        return json.dumps(result)


class CasinoGetBalance(BaseTool):
    """Check the Purple Flea casino wallet balance."""

    name: str = "purpleflea_casino_get_balance"
    description: str = (
        "Retrieve the current wallet balance for the authenticated Purple Flea casino account. "
        "Returns the balance amount and currency. Use this before placing bets to check "
        "available funds, or after a game to see updated totals."
    )
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.get_balance()
        return json.dumps(result)


class CasinoDeposit(BaseTool):
    """Deposit funds into the Purple Flea casino wallet."""

    name: str = "purpleflea_casino_deposit"
    description: str = (
        "Deposit funds into the Purple Flea casino wallet. "
        "Specify the amount and currency (defaults to USD). "
        "Supported currencies include USD, USDC, ETH, BTC, and SOL. "
        "Returns the updated wallet balance after the deposit."
    )
    args_schema: Type[BaseModel] = CasinoDepositInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, amount: float, currency: str = "USD") -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.deposit(amount, currency=currency)
        return json.dumps(result)


class CasinoWithdraw(BaseTool):
    """Withdraw funds from the Purple Flea casino wallet."""

    name: str = "purpleflea_casino_withdraw"
    description: str = (
        "Withdraw funds from the Purple Flea casino wallet to your external wallet. "
        "Specify the amount and currency (defaults to USD). "
        "Returns the updated wallet balance after the withdrawal."
    )
    args_schema: Type[BaseModel] = CasinoWithdrawInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, amount: float, currency: str = "USD") -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.withdraw(amount, currency=currency)
        return json.dumps(result)


class CasinoListGames(BaseTool):
    """List available Purple Flea casino games."""

    name: str = "purpleflea_casino_list_games"
    description: str = (
        "List all available casino games on the Purple Flea platform. "
        "Returns game IDs, names, descriptions, min/max bets, and house edge for each game. "
        "Use this to discover which games are available before placing a bet."
    )
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.list_games()
        return json.dumps(result)


class CasinoGetGame(BaseTool):
    """Get details for a specific Purple Flea casino game."""

    name: str = "purpleflea_casino_get_game"
    description: str = (
        "Get detailed information about a specific Purple Flea casino game, "
        "including rules, payout multipliers, house edge, min/max bet limits, "
        "and accepted options. Provide the game_id (e.g. 'coin_flip', 'dice')."
    )
    args_schema: Type[BaseModel] = GameIdInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, game_id: str) -> str:
        with _client(self.api_key, self.base_url) as c:
            result = c.get_game(game_id)
        return json.dumps(result)


class CasinoGetGameHistory(BaseTool):
    """Retrieve past Purple Flea casino game results."""

    name: str = "purpleflea_casino_get_game_history"
    description: str = (
        "Retrieve the history of past casino game results for the authenticated account. "
        "Returns bet amounts, outcomes, payouts, and timestamps. "
        "Optionally filter by game_id or limit the number of results."
    )
    args_schema: Type[BaseModel] = GameHistoryInput
    api_key: str = ""
    base_url: Optional[str] = None

    def _run(self, limit: int | None = None, game_id: str | None = None) -> str:
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs["limit"] = limit
        if game_id is not None:
            kwargs["game_id"] = game_id
        with _client(self.api_key, self.base_url) as c:
            result = c.get_game_history(**kwargs)
        return json.dumps(result)
