"""LangChain tools for the Purple Flea Domains API."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

BASE_URL = "https://domains.purpleflea.com"


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


class DomainSearchInput(BaseModel):
    query: str = Field(
        description="Domain name to search for availability (e.g. 'myagent.ai', 'myagent'). "
                    "Can be a full domain with TLD or just a name to check across multiple TLDs."
    )
    tlds: Optional[list[str]] = Field(
        default=None,
        description="Optional list of TLDs to check (e.g. ['com', 'ai', 'io', 'xyz']). "
                    "If not specified, checks all supported TLDs.",
    )


class DomainPurchaseInput(BaseModel):
    domain: str = Field(
        description="The full domain name to purchase (e.g. 'myagent.ai')."
    )
    years: Optional[int] = Field(
        default=1,
        description="Number of years to register the domain (1-10). Default: 1.",
    )
    auto_renew: Optional[bool] = Field(
        default=True,
        description="Whether to automatically renew the domain before expiry. Default: True.",
    )


class DNSAddRecordInput(BaseModel):
    domain: str = Field(description="The domain to add a DNS record to (e.g. 'myagent.ai').")
    record_type: str = Field(
        description="DNS record type: 'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SRV'."
    )
    name: str = Field(
        description="Record name (subdomain). Use '@' for root domain, or 'www', 'api', etc."
    )
    value: str = Field(
        description="Record value (e.g. IP address for A records, hostname for CNAME)."
    )
    ttl: Optional[int] = Field(
        default=3600,
        description="TTL in seconds. Default: 3600 (1 hour).",
    )


class DomainNameInput(BaseModel):
    domain: str = Field(description="The full domain name (e.g. 'myagent.ai').")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class DomainSearchTool(BaseTool):
    """Search domain name availability via Purple Flea Domains."""

    name: str = "purpleflea_domain_search"
    description: str = (
        "Search for domain name availability using the Purple Flea Domains API. "
        "Check if a domain is available for registration across .com, .ai, .io, .xyz, .app, and 500+ TLDs. "
        "Returns availability status, registration price, and renewal cost for each TLD. "
        "Use this to find a unique domain for a project, service, or autonomous agent identity."
    )
    args_schema: Type[BaseModel] = DomainSearchInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(self, query: str, tlds: Optional[list[str]] = None) -> str:
        payload: dict[str, Any] = {"query": query}
        if tlds:
            payload["tlds"] = tlds
        result = _post(self.base_url, "/v1/domains/search", self.api_key, payload)
        return json.dumps(result)


class DomainPurchaseTool(BaseTool):
    """Register a domain name via Purple Flea Domains."""

    name: str = "purpleflea_domain_purchase"
    description: str = (
        "Register (purchase) a domain name using the Purple Flea Domains API. "
        "Supports 500+ TLDs including .com, .ai, .io, .xyz, .app, .dev, .agent, .bot. "
        "Returns confirmation, expiry date, and nameserver details. "
        "Use this to claim a domain identity for an agent, project, or service. "
        "Auto-renewal is enabled by default to prevent expiry."
    )
    args_schema: Type[BaseModel] = DomainPurchaseInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(
        self,
        domain: str,
        years: int = 1,
        auto_renew: bool = True,
    ) -> str:
        payload: dict[str, Any] = {
            "domain": domain,
            "years": years,
            "auto_renew": auto_renew,
        }
        result = _post(self.base_url, "/v1/domains/register", self.api_key, payload)
        return json.dumps(result)


class DNSTool(BaseTool):
    """Add a DNS record to a Purple Flea managed domain."""

    name: str = "purpleflea_domain_add_dns_record"
    description: str = (
        "Add a DNS record to a domain managed via Purple Flea Domains. "
        "Supports A, AAAA, CNAME, MX, TXT, NS, and SRV record types. "
        "Changes propagate globally within 60 seconds. "
        "Use this to point a domain to a server, configure email, verify ownership, "
        "or set up any DNS-based service for an agent-owned domain."
    )
    args_schema: Type[BaseModel] = DNSAddRecordInput
    api_key: str = ""
    base_url: str = BASE_URL

    def _run(
        self,
        domain: str,
        record_type: str,
        name: str,
        value: str,
        ttl: int = 3600,
    ) -> str:
        payload: dict[str, Any] = {
            "domain": domain,
            "type": record_type,
            "name": name,
            "value": value,
            "ttl": ttl,
        }
        result = _post(self.base_url, f"/v1/domains/{domain}/records", self.api_key, payload)
        return json.dumps(result)
