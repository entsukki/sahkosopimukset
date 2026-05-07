"""
Hakee kiinteähintaiset sähkösopimukset (>= 12 kk) sahkonhinta.fi API:sta
ja tallentaa tulokset kiinteat_tarjoukset.csv -tiedostoon.

Skriptiä käytetään sekä GitHub Actionsin kautta (ajastus klo 04:00)
että manuaalisesti. Jos kuluvan päivän data on jo tallennettu, skripti ei tee mitään.
"""

import urllib.request
import json
import csv
import os
from datetime import date

API_URL = "https://ev-shv-prod-app-wa-consumerapi1.azurewebsites.net/api/productlist/"
CSV_PATH = "kiinteat_tarjoukset.csv"
CSV_FIELDS = ["pvm", "yhtiö", "tuote", "kesto", "snt_kWh", "eur_kk", "perusmaksuAlennus"]

VALID_RANGES = {"Fixed12", "Between1323", "Fixed24", "Over24"}
KESTO_MAP = {
    "Fixed12": "12 kk",
    "Between1323": "13-23 kk",
    "Fixed24": "24 kk",
    "Over24": "yli 24 kk",
}


def already_fetched_today():
    today = str(date.today())
    if not os.path.exists(CSV_PATH):
        return False
    with open(CSV_PATH, encoding="utf-8") as f:
        for line in f:
            if line.startswith(today):
                return True
    return False


def fetch_and_filter():
    with urllib.request.urlopen(API_URL, timeout=30) as resp:
        products = json.loads(resp.read().decode("utf-8"))

    results = []
    for p in products:
        d = p.get("Details", {})
        if not (
            d.get("PricingModel") == "FixedPrice"
            and d.get("FixedTimeRange") in VALID_RANGES
            and d.get("ContractType") == "FixedTerm"
            and d.get("TargetGroup") in ("Household", "Both")
        ):
            continue

        pricing = d.get("Pricing", {}).get("PriceComponents", [])
        energy = next((c for c in pricing if c.get("PriceComponentType") == "General"), None)
        monthly = next((c for c in pricing if c.get("PriceComponentType") == "Monthly"), None)

        snt_kwh = energy["OriginalPayment"]["Price"] if energy else None
        if snt_kwh is None:
            continue

        eur_kk = monthly["OriginalPayment"]["Price"] if monthly else ""

        alennus = ""
        if (
            monthly
            and monthly.get("HasDiscount")
            and monthly.get("Discount", {}).get("DiscountType") != "NoDiscount"
        ):
            n = monthly["Discount"].get("NfirstMonths", "")
            alennus = f"0€ ensimmäiset {n} kk"

        results.append({
            "pvm": str(date.today()),
            "yhtiö": p.get("Company", {}).get("Name", ""),
            "tuote": p.get("Name", ""),
            "kesto": KESTO_MAP.get(d["FixedTimeRange"], ""),
            "snt_kWh": snt_kwh,
            "eur_kk": eur_kk,
            "perusmaksuAlennus": alennus,
        })

    results.sort(key=lambda x: x["snt_kWh"])
    return results


def save_to_csv(results):
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)


def main():
    if already_fetched_today():
        print(f"Tänään ({date.today()}) on jo haettu — ei tehdä uutta hakua.")
        return

    print("Haetaan hintatiedot API:sta...")
    results = fetch_and_filter()
    save_to_csv(results)
    print(f"Valmis. Tallennettu {len(results)} tarjousta ({date.today()}).")


if __name__ == "__main__":
    main()
