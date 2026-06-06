from __future__ import annotations

import requests
import time

from .classyfire_result import ClassyFireResult


class ClassyFireNotFoundError(Exception):
    """Raised when ClassyFire returns an empty result."""


class ClassyFireRequestError(Exception):
    """Raised when ClassyFire request failed."""

def normalize_inchikey(
    inchikey: str | None,
) -> str | None:
    if inchikey is None:
        return None

    normalized = str(inchikey).strip()

    if not normalized:
        return None

    if normalized.startswith("InChIKey="):
        normalized = normalized.removeprefix("InChIKey=").strip()

    if not normalized:
        return None

    return normalized

def fetch_classyfire_json(
    inchikey: str,
    *,
    timeout: int = 30,
) -> dict:
    """Fetch raw ClassyFire JSON by InChIKey."""
    url = f"http://classyfire.wishartlab.com/entities/{inchikey}.json"

    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as error:
        raise ClassyFireRequestError(str(error)) from error

    if response.status_code != 200:
        raise ClassyFireRequestError(
            f"{response.reason}(status:{response.status_code})"
        )

    data = response.json()

    if data == {}:
        raise ClassyFireNotFoundError(
            "No result returned from ClassyFire API."
        )
    if 'inchikey' in data:
        data['inchikey'] = normalize_inchikey(data['inchikey'])
    time.sleep(5)  # Sleep to avoid hitting API rate limits

    return data


def fetch_classyfire_result(
    inchikey: str,
    *,
    timeout: int = 30,
) -> ClassyFireResult:
    """Fetch and parse ClassyFire result by InChIKey."""
    data = fetch_classyfire_json(inchikey, timeout=timeout)

    return ClassyFireResult.from_api_json(
        data=data,
    )

if __name__ == "__main__":
    result = fetch_classyfire_result("AAAFZMYJJHWUPN-TXICZTDVSA-N")

    print(result.kingdom.name if result.kingdom else None)
    print(result.class_.name if result.class_ else None)
    print(result.substituents)
    
    result = fetch_classyfire_result("AADVCYNFEREWOS-OBRABYBLSA-N")

    print(result.kingdom.name if result.kingdom else None)
    print(result.class_.name if result.class_ else None)
    print(result.substituents)