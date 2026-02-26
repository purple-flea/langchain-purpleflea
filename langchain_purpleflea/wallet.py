"""LangChain tools for the Purple Flea Wallet & Swap API."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

BASE_URL = "https://wallet.purpleflea.com"


def _post(base_url: str, path: str, api_key: str, payload: dict) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.reason, "status": e.code, "body": e.read().decode()}


def _get(base_url: str, path: str, api_key: str) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.reason, "status": e.code, "body": e.read().decode()}


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class WalletCreateInput(BaseModel):
    chain: str = Field(
        description=(
            "The blockchain to create a wallet on. Supported: 'ethereum', 'bitcoin', "
            "'solana', 'tron', 'polygon', 'arbitrum', 'base', 'bnb'."
        )
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional human-readable label for the wallet.",
    )
    referral_code: Optional[str] = Field(
        default=None,
        description="Referral code of the agent who referred you. Earns them 10% of your swap fees forever.",
    )


class WalletBalanceInput(BaseModel):
    wallet_id: str = Field(description="The wallet ID to check balance for.")


class SwapInput(BaseModel):
    wallet_id: str = Field(description="The wallet ID to execute the swap from.")
    from_token: str = Field(
        description="The token to swap from (e.g. 'ETH', 'USDC', 'BTC', 'SOL')."
    )
    to_token: str = Field(
        description="The token to swap to (e.g. 'USDC', 'ETH', 'SOL', 'BTC')."
    )
    amount: float = Field(
        description="The amount of from_token to swap. Must be a positive number."
    )
    slippage: Optional[float] = Field(
        default=0.5,
        description="Maximum acceptable slippage percentage (default 0.5%). Range: 0.1–5.0.",
    )


class BalanceInput(BaseModel):
    address: str = Field(description="The blockchain address to check balance for.")
    chain: str = Field(
        description="The blockchain (e.g. 'ethereum', 'bitcoin', 'solana')."
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class WalletTool(BaseTool):
    """Create a new multi-chain HD wallet on Purple Flea."""

    name: str = "purpleflea_wallet_create"
    description: str = (
        "Create a new HD (hierarchical deterministic) wallet on Purple Flea for any supported chain. "
        "Supported chains: Ethereum, Bitcoin, Solana, Tron, Polygon, Arbitrum, Base, BNB Chain. "
        "Returns wallet ID, public address, and derivation path. "
        "The wallet is non-custodial — only you hold the private keys. "
        "Use this when you need a fresh blockchain address for receiving funds, executing swaps, "
        "or storing assets autonomously."
    )
    args_schema: Type[BaseModel] = WalletCreateInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(self, chain: str, label: Optional[str] = None, referral_code: Optional[str] = None) -> str:
        payload: dict[str, Any] = {"chain": chain}
        if label:
            payload["label"] = label
        if referral_code:
            payload["referral_code"] = referral_code
        result = _post(self.base_url, "/v1/wallets", self.api_key, payload)
        return json.dumps(result)


class SwapTool(BaseTool):
    """Execute a token swap via Purple Flea Wallet."""

    name: str = "purpleflea_wallet_swap"
    description: str = (
        "Execute a token swap using a Purple Flea wallet. "
        "Swap between any supported tokens: ETH, BTC, SOL, USDC, USDT, and 500+ others. "
        "Uses best-rate routing across DEXes (Uniswap, Jupiter, etc). "
        "Returns the swap transaction hash, output amount received, and effective rate. "
        "A 10% commission is earned by your referrer on each swap fee. "
        "Use this to rebalance holdings, convert profits to stablecoins, or acquire assets."
    )
    args_schema: Type[BaseModel] = SwapInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(
        self,
        wallet_id: str,
        from_token: str,
        to_token: str,
        amount: float,
        slippage: float = 0.5,
    ) -> str:
        payload = {
            "wallet_id": wallet_id,
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount,
            "slippage": slippage,
        }
        result = _post(self.base_url, "/v1/swap", self.api_key, payload)
        return json.dumps(result)


class BalanceTool(BaseTool):
    """Check the token balance of any blockchain address."""

    name: str = "purpleflea_wallet_balance"
    description: str = (
        "Check the token balance of any blockchain address via Purple Flea Wallet API. "
        "Returns native token balance plus all ERC-20/SPL token balances with USD values. "
        "Works on Ethereum, Bitcoin, Solana, Tron, Polygon, Arbitrum, Base, and BNB Chain. "
        "Use this to monitor wallet balances, verify deposits, or assess your portfolio value."
    )
    args_schema: Type[BaseModel] = BalanceInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(self, address: str, chain: str) -> str:
        result = _get(self.base_url, f"/v1/balance/{chain}/{address}", self.api_key)
        return json.dumps(result)
