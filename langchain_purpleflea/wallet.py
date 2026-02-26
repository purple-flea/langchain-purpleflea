"""Purple Flea Wallet tools for LangChain agents."""

import json
import requests
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class WalletInput(BaseModel):
    action: str = Field(
        description="Action: create, deposit_addresses, transactions, referral_stats"
    )


class SwapInput(BaseModel):
    from_chain: str = Field(description="Source chain (ethereum, base, solana, bitcoin, polygon, arbitrum)")
    from_token: str = Field(description="Source token (USDC, ETH, SOL, BTC, USDT)")
    to_chain: str = Field(description="Destination chain")
    to_token: str = Field(description="Destination token")
    amount: float = Field(description="Amount to swap")


class BalanceInput(BaseModel):
    chain: Optional[str] = Field(
        default=None,
        description="Chain to check (ethereum, base, solana, bitcoin). Leave empty for all balances."
    )


class WalletTool(BaseTool):
    """LangChain tool for Purple Flea multi-chain HD wallet management."""

    name: str = "purple_flea_wallet"
    description: str = (
        "Manage your Purple Flea multi-chain HD wallet. "
        "Supports Ethereum, Base, Arbitrum, Optimism, Polygon, Solana, Bitcoin, Lightning, Monero. "
        "Get deposit addresses for any supported chain and token. "
        "Your casino and trading accounts are all funded through this unified wallet. "
        "Actions: create (new wallet), deposit_addresses (get all chain addresses), "
        "transactions (transaction history), referral_stats (swap fee earnings)"
    )
    args_schema: Type[BaseModel] = WalletInput
    return_direct: bool = False

    api_key: Optional[str] = None
    referral_code: Optional[str] = None
    base_url: str = "https://wallet.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None, referral_code: Optional[str] = None,
                 base_url: str = "https://wallet.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.referral_code = referral_code
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str) -> str:
        try:
            if action == "create":
                payload = {}
                if self.referral_code:
                    payload["referral_code"] = self.referral_code
                r = requests.post(f"{self.base_url}/wallet/create",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "deposit_addresses":
                r = requests.get(f"{self.base_url}/wallet/addresses",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "transactions":
                r = requests.get(f"{self.base_url}/wallet/transactions",
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


class SwapTool(BaseTool):
    """LangChain tool for cross-chain token swaps via Purple Flea Wallet."""

    name: str = "purple_flea_swap"
    description: str = (
        "Execute cross-chain token swaps via Purple Flea Wallet (powered by Wagyu). "
        "Swap between any supported chains and tokens: "
        "Chains: ethereum, base, arbitrum, optimism, polygon, solana, bitcoin. "
        "Tokens: USDC, USDT, ETH, SOL, BTC, MATIC. "
        "Get a quote first, then execute. Agents who referred you earn 10% of swap fees."
    )
    args_schema: Type[BaseModel] = SwapInput
    return_direct: bool = False

    api_key: Optional[str] = None
    base_url: str = "https://wallet.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://wallet.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, from_chain: str, from_token: str, to_chain: str,
             to_token: str, amount: float) -> str:
        try:
            quote_payload = {
                "from_chain": from_chain,
                "from_token": from_token,
                "to_chain": to_chain,
                "to_token": to_token,
                "amount": amount,
            }
            quote_r = requests.post(f"{self.base_url}/swap/quote",
                                    json=quote_payload, headers=self._headers(), timeout=30)
            quote = quote_r.json()

            exec_r = requests.post(f"{self.base_url}/swap/execute",
                                   json=quote_payload, headers=self._headers(), timeout=60)
            return json.dumps({"quote": quote, "execution": exec_r.json()}, indent=2)

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


class BalanceTool(BaseTool):
    """LangChain tool for checking Purple Flea balances across all services."""

    name: str = "purple_flea_balance"
    description: str = (
        "Check your Purple Flea balances. Queries the casino balance (USD) "
        "and wallet addresses for depositing funds. Use chain parameter to filter "
        "to a specific chain, or leave empty to see all addresses."
    )
    args_schema: Type[BaseModel] = BalanceInput
    return_direct: bool = False

    api_key: Optional[str] = None
    casino_base_url: str = "https://casino.purpleflea.com/api/v1"

    def __init__(self, api_key: Optional[str] = None,
                 casino_base_url: str = "https://casino.purpleflea.com/api/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.casino_base_url = casino_base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, chain: Optional[str] = None) -> str:
        try:
            balance_r = requests.get(f"{self.casino_base_url}/auth/balance",
                                     headers=self._headers(), timeout=30)
            balance_data = balance_r.json()

            chains_r = requests.get(f"{self.casino_base_url}/auth/supported-chains",
                                    headers=self._headers(), timeout=30)
            chains_data = chains_r.json()

            return json.dumps({
                "casino_balance": balance_data,
                "supported_chains": chains_data,
            }, indent=2)

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})
