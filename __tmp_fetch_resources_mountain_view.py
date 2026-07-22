import json
import os
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup


OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY")
DEFAULT_HTTP_HEADERS = {"User-Agent": "CivicShieldPro/3.0"}


def geocode_address(address):
    if not address:
        return None

    url = (
        "https://api.opencagedata.com/geocode/v1/json"
        f"?q={address}&key={OPENCAGE_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("results"):
            loc = data["results"][0]["geometry"]
            return (loc["lat"], loc["lng"])

        return None
    except Exception:
        return None


def fetch_lawhelp_resources():
    base_url = "https://www.lawhelpca.org/find-legal-help/directory/area"
    try:
        response = requests.get(base_url, headers=DEFAULT_HTTP_HEADERS, timeout=10)
        response.raise_for_status()
    except Exception:
        return []

    resources = []
    seen_urls = set()

    soup = BeautifulSoup(response.text, "html.parser")
    page_urls = [base_url]
    for link in soup.select('a.page-link[href]'):
        href = link.get("href", "")
        if not href:
            continue

        page_url = urljoin(base_url, href)
        if page_url not in seen_urls:
            seen_urls.add(page_url)
            page_urls.append(page_url)

    for page_url in page_urls:
        try:
            page_response = requests.get(page_url, headers=DEFAULT_HTTP_HEADERS, timeout=10)
            page_response.raise_for_status()
        except Exception:
            continue

        page_soup = BeautifulSoup(page_response.text, "html.parser")

        for item in page_soup.select(".card.organization"):
            name_el = item.select_one(".card-title a")
            address_el = item.select_one(".adr")
            phone_el = item.select_one(".tel")
            website_el = item.select_one(".web a[href]")

            name = name_el.get_text(" ", strip=True) if name_el else ""
            if address_el:
                street_parts = [
                    part.get_text(" ", strip=True)
                    for part in address_el.select(".street-address, .extended-address")
                ]
                city = address_el.select_one(".locality")
                region = address_el.select_one(".region")
                postal = address_el.select_one(".postal-code")

                street = " ".join(part for part in street_parts if part)
                city_state_postal = " ".join(
                    part
                    for part in [
                        city.get_text(" ", strip=True) if city else "",
                        region.get_text(" ", strip=True).lstrip(",") if region else "",
                        postal.get_text(" ", strip=True) if postal else "",
                    ]
                    if part
                )
                address = ", ".join(part for part in [street, city_state_postal] if part)
            else:
                address = ""
            phone = phone_el.get_text(" ", strip=True) if phone_el else ""
            website = website_el["href"].strip() if website_el else ""

            if name and address:
                resources.append(
                    {
                        "name": name,
                        "category": "Legal Aid",
                        "address": address,
                        "phone": phone,
                        "website": website,
                        "hours": "",
                    }
                )

    return resources


def fetch_211_resources(city):
    url = f"https://api.211ca.org/search?city={quote_plus(city)}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception:
        return []

    resources = []
    for item in data.get("results", []):
        name = item.get("name")
        address = item.get("address")
        phone = item.get("phone")
        category = item.get("category")

        if name and address:
            resources.append(
                {
                    "name": name,
                    "category": category or "Community Resource",
                    "address": address,
                    "phone": phone or "",
                    "website": item.get("website", ""),
                    "hours": item.get("hours", ""),
                }
            )

    return resources


def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "CivicShieldPro/3.0"}, timeout=10)
        data = response.json()
        return data.get("display_name", f"{lat}, {lon}")
    except Exception:
        return f"{lat}, {lon}"


def fetch_osm_resources(lat, lon, radius_meters=5000):
    query = f"""
    [out:json];
    (
      node[\"amenity\"=\"community_centre\"](around:{radius_meters},{lat},{lon});
      node[\"social_facility\"](around:{radius_meters},{lat},{lon});
      node[\"office\"=\"ngo\"](around:{radius_meters},{lat},{lon});
    );
    out;
    """

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers=DEFAULT_HTTP_HEADERS,
            timeout=15,
        )
        data = response.json()
    except Exception:
        return []

    resources = []
    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name")
        if not name:
            continue

        lat2 = element.get("lat")
        lon2 = element.get("lon")
        address = reverse_geocode(lat2, lon2)

        resources.append(
            {
                "name": name,
                "category": "Community Center",
                "address": address,
                "phone": "",
                "website": "",
                "hours": "",
                "latitude": lat2,
                "longitude": lon2,
            }
        )

    return resources


coords = geocode_address("Mountain View, CA")
result = {
    "coords": coords,
    "fetch_lawhelp_resources": fetch_lawhelp_resources(),
    "fetch_211_resources": fetch_211_resources("Mountain View"),
    "fetch_osm_resources": fetch_osm_resources(coords[0], coords[1]) if coords else [],
}

with open("__tmp_fetch_resources_mountain_view_output.json", "w", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)

print("__tmp_fetch_resources_mountain_view_output.json")