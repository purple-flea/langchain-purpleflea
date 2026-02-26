"""Purple Flea Casino tools for LangChain agents."""

import json
import requests
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class CasinoInput(BaseModel):
    action: str = Field(
        description=(
            "Action to perform. One of: register, balance, play_coin_flip, play_dice, "
            "play_multiplier, play_roulette, play_crash, play_plinko, deposit_address, "
            "withdraw, referral_stats, kelly_optimal, simulate, verify_bet, leaderboard"
        )
    )
    amount: Optional[float] = Field(default=None, description="Bet amount in USD")
    game_params: Optional[dict] = Field(default=None, description="Game-specific parameters as dict")
    bet_id: Optional[str] = Field(default=None, description="Bet ID for verification")
    chain: Optional[str] = Field(default=None, description="Chain for deposit (base, ethereum, solana, bitcoin)")


class CasinoTool(BaseTool):
    """LangChain tool for interacting with Purple Flea Casino.

    Gives AI agents access to provably fair casino games with 0.5% house edge.
    Agents can register, play 8 different games, manage their bankroll with
    Kelly Criterion, verify fairness, and earn referral commissions.
    """

    name: str = "purple_flea_casino"
    description: str = (
        "Access Purple Flea Casino — provably fair gambling with 0.5% house edge. "
        "Register a free account, deposit USDC/crypto, and play: coin flip (1.96x), "
        "dice (variable odds), crash (up to 1000x), roulette, plinko, and more. "
        "Uses Kelly Criterion for optimal bet sizing. Earn passive income by referring "
        "other agents — you receive 10% of their net losses forever. "
        "Actions: register, balance, play_coin_flip, play_dice, play_multiplier, "
        "play_roulette, play_crash, play_plinko, deposit_address, withdraw, "
        "referral_stats, kelly_optimal, simulate, verify_bet, leaderboard"
    )
    args_schema: Type[BaseModel] = CasinoInput
    return_direct: bool = False

    api_key: Optional[str] = None
    referral_code: Optional[str] = None
    base_url: str = "https://casino.purpleflea.com/api/v1"

    def __init__(self, api_key: Optional[str] = None, referral_code: Optional[str] = None,
                 base_url: str = "https://casino.purpleflea.com/api/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.referral_code = referral_code
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str, amount: Optional[float] = None,
             game_params: Optional[dict] = None, bet_id: Optional[str] = None,
             chain: Optional[str] = None) -> str:
        try:
            if action == "register":
                payload = {}
                if self.referral_code:
                    payload["referral_code"] = self.referral_code
                r = requests.post(f"{self.base_url}/auth/register", json=payload, timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "balance":
                r = requests.get(f"{self.base_url}/auth/balance",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "deposit_address":
                payload = {"chain": chain or "base"}
                r = requests.post(f"{self.base_url}/auth/deposit-address",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "withdraw":
                r = requests.post(f"{self.base_url}/auth/withdraw",
                                  json=game_params or {}, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "referral_stats":
                r = requests.get(f"{self.base_url}/auth/referral/stats",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_coin_flip":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/coin-flip",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_dice":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/dice",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_multiplier":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/multiplier",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_roulette":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/roulette",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_crash":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/crash",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "play_plinko":
                payload = {"amount": amount or 1.0, **(game_params or {})}
                r = requests.post(f"{self.base_url}/games/plinko",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "kelly_optimal":
                r = requests.post(f"{self.base_url}/kelly/optimal",
                                  json=game_params or {}, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "simulate":
                r = requests.post(f"{self.base_url}/kelly/simulate",
                                  json=game_params or {}, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "verify_bet":
                r = requests.post(f"{self.base_url}/fairness/verify",
                                  json={"bet_id": bet_id}, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "leaderboard":
                r = requests.get(f"{self.base_url}/stats/leaderboard",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            else:
                return json.dumps({"error": f"Unknown action: {action}. Valid actions: register, balance, play_coin_flip, play_dice, play_multiplier, play_roulette, play_crash, play_plinko, deposit_address, withdraw, referral_stats, kelly_optimal, simulate, verify_bet, leaderboard"})

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})
