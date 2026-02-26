"""Purple Flea Domains tools for LangChain agents."""

import json
import requests
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class DomainSearchInput(BaseModel):
    query: str = Field(description="Domain name to search (e.g. 'myagent.com' or just 'myagent')")
    check_only: bool = Field(default=False, description="If True, just check availability of exact domain")


class DomainPurchaseInput(BaseModel):
    action: str = Field(description="Action: register (purchase domain), list (your domains), account, referral_stats")
    domain: Optional[str] = Field(default=None, description="Domain to register (e.g. 'myagent.com')")


class DNSInput(BaseModel):
    action: str = Field(description="Action: add, list, update, delete")
    domain_id: Optional[str] = Field(default=None, description="Domain ID from your domains list")
    record_type: Optional[str] = Field(default=None, description="DNS record type: A, AAAA, CNAME, MX, TXT")
    name: Optional[str] = Field(default=None, description="Record name (e.g. '@', 'www', 'mail')")
    content: Optional[str] = Field(default=None, description="Record value (IP, hostname, text)")
    record_id: Optional[str] = Field(default=None, description="Record ID for update/delete")


class DomainSearchTool(BaseTool):
    """LangChain tool for searching domain availability via Purple Flea Domains."""

    name: str = "purple_flea_domain_search"
    description: str = (
        "Search for available domain names via Purple Flea Domains (powered by Njalla). "
        "Privacy-first domain registration — no personal data required. "
        "Search returns availability and pricing. 20% markup on Njalla base prices. "
        "Referral system: earn 15% of domain purchases from referred agents. "
        "Perfect for agents that need a web presence or handle web3 infrastructure."
    )
    args_schema: Type[BaseModel] = DomainSearchInput
    return_direct: bool = False

    api_key: Optional[str] = None
    base_url: str = "https://domains.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://domains.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, query: str, check_only: bool = False) -> str:
        try:
            if check_only:
                r = requests.get(f"{self.base_url}/domains/check",
                                 params={"domain": query},
                                 headers=self._headers(), timeout=30)
            else:
                r = requests.get(f"{self.base_url}/domains/search",
                                 params={"q": query},
                                 headers=self._headers(), timeout=30)
            return json.dumps(r.json(), indent=2)

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


class DomainPurchaseTool(BaseTool):
    """LangChain tool for purchasing and managing domains via Purple Flea."""

    name: str = "purple_flea_domain_purchase"
    description: str = (
        "Register and manage domains via Purple Flea Domains. "
        "Register available domains, list your existing domains, check account balance. "
        "Privacy-first: no personal data required for registration. "
        "Actions: register (domain param required), list, account, referral_stats"
    )
    args_schema: Type[BaseModel] = DomainPurchaseInput
    return_direct: bool = False

    api_key: Optional[str] = None
    referral_code: Optional[str] = None
    base_url: str = "https://domains.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None, referral_code: Optional[str] = None,
                 base_url: str = "https://domains.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.referral_code = referral_code
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str, domain: Optional[str] = None) -> str:
        try:
            if action == "register":
                if not self.api_key:
                    payload = {}
                    if self.referral_code:
                        payload["referral_code"] = self.referral_code
                    reg_r = requests.post(f"{self.base_url}/auth/register", json=payload, timeout=30)
                    return json.dumps({"message": "Register first to get API key", "result": reg_r.json()}, indent=2)
                payload = {"domain": domain}
                r = requests.post(f"{self.base_url}/domains/register",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "list":
                r = requests.get(f"{self.base_url}/domains",
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "account":
                r = requests.get(f"{self.base_url}/auth/account",
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


class DNSTool(BaseTool):
    """LangChain tool for managing DNS records via Purple Flea Domains."""

    name: str = "purple_flea_dns"
    description: str = (
        "Manage DNS records for your Purple Flea domains. "
        "Supported record types: A, AAAA, CNAME, MX, TXT. "
        "Actions: add (requires domain_id, record_type, name, content), "
        "list (requires domain_id), update (requires record_id + new values), "
        "delete (requires record_id)"
    )
    args_schema: Type[BaseModel] = DNSInput
    return_direct: bool = False

    api_key: Optional[str] = None
    base_url: str = "https://domains.purpleflea.com/v1"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://domains.purpleflea.com/v1", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, action: str, domain_id: Optional[str] = None,
             record_type: Optional[str] = None, name: Optional[str] = None,
             content: Optional[str] = None, record_id: Optional[str] = None) -> str:
        try:
            if action == "add":
                payload = {
                    "domain_id": domain_id,
                    "type": record_type,
                    "name": name,
                    "content": content,
                }
                r = requests.post(f"{self.base_url}/dns/records",
                                  json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "list":
                r = requests.get(f"{self.base_url}/dns/records",
                                 params={"domain_id": domain_id},
                                 headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "update":
                payload = {}
                if record_type:
                    payload["type"] = record_type
                if name:
                    payload["name"] = name
                if content:
                    payload["content"] = content
                r = requests.put(f"{self.base_url}/dns/records/{record_id}",
                                 json=payload, headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            elif action == "delete":
                r = requests.delete(f"{self.base_url}/dns/records/{record_id}",
                                    headers=self._headers(), timeout=30)
                return json.dumps(r.json(), indent=2)

            else:
                return json.dumps({"error": f"Unknown action: {action}"})

        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})
