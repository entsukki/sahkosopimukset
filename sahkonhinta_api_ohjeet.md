# Sahkonhinta.fi API — Ohjeet kiinteähintaisten sopimusten hakuun

## API-endpoint

```
GET https://ev-shv-prod-app-wa-consumerapi1.azurewebsites.net/api/productlist/
```

Palauttaa JSON-taulukon kaikista sahkonhinta.fi:ssä listatuista sähkötuotteista.  
Ei vaadi autentikointia eikä parametreja.

---

## Kentät joilla suodatetaan

| Kenttä | Sijainti | Arvo kiinteähintaiselle ≥ 12 kk kotitaloussopimukselle |
|--------|----------|--------------------------------------------------------|
| `PricingModel` | `Details.PricingModel` | `"FixedPrice"` |
| `ContractType` | `Details.ContractType` | `"FixedTerm"` |
| `FixedTimeRange` | `Details.FixedTimeRange` | `"Fixed12"`, `"Between1323"`, `"Fixed24"`, `"Over24"` |
| `TargetGroup` | `Details.TargetGroup` | `"Household"` tai `"Both"` |

### Kaikki FixedTimeRange-arvot
- `Below6` — alle 6 kk
- `Fixed6` — 6 kk
- `Fixed12` — 12 kk
- `Between1323` — 13–23 kk
- `Fixed24` — 24 kk
- `Over24` — yli 24 kk
- `Other` — muu

---

## Hintatiedot

Hinnat löytyvät kentästä `Details.Pricing.PriceComponents` (taulukko).

| `PriceComponentType` | Merkitys | Yksikkö (`PaymentUnit`) |
|----------------------|----------|--------------------------|
| `General` | Energian yksikköhinta | `CentPerKiwattHour` (snt/kWh) |
| `Monthly` | Perusmaksu | `EurPerMonth` (€/kk) |

Hinta löytyy kentästä `OriginalPayment.Price`.  
Alennukset tarkistetaan kentästä `HasDiscount` ja `Discount`.

---

## JavaScript-esimerkki (selainkonsolissa tai Claude in Chrome -työkalulla)

```javascript
(async () => {
  const resp = await fetch('https://ev-shv-prod-app-wa-consumerapi1.azurewebsites.net/api/productlist/');
  const data = await resp.json();

  // Muuta tätä tarpeen mukaan:
  const validRanges = new Set(['Fixed12', 'Between1323', 'Fixed24', 'Over24']); // ≥ 12 kk
  // const validRanges = new Set(['Fixed12']); // vain 12 kk

  const filtered = data.filter(p =>
    p.Details?.PricingModel === 'FixedPrice' &&
    validRanges.has(p.Details?.FixedTimeRange) &&
    p.Details?.ContractType === 'FixedTerm' &&
    (p.Details?.TargetGroup === 'Household' || p.Details?.TargetGroup === 'Both')
  );

  const results = filtered.map(p => {
    const pricing = p.Details?.Pricing?.PriceComponents || [];
    const energyComp = pricing.find(c => c.PriceComponentType === 'General');
    const monthlyComp = pricing.find(c => c.PriceComponentType === 'Monthly');
    const kestoLabel = {
      Fixed12: '12 kk', Between1323: '13–23 kk',
      Fixed24: '24 kk', Over24: 'yli 24 kk'
    }[p.Details?.FixedTimeRange];

    return {
      yhtiö: p.Company?.Name,
      tuote: p.Name,
      kesto: kestoLabel,
      snt_kWh: energyComp?.OriginalPayment?.Price,
      eur_kk: monthlyComp?.OriginalPayment?.Price,
      perusmaksuAlennus: (monthlyComp?.HasDiscount && monthlyComp.Discount?.DiscountType !== 'NoDiscount')
        ? `0 € ensimmäiset ${monthlyComp.Discount.NfirstMonths} kk` : null
    };
  })
  .filter(r => r.snt_kWh)
  .sort((a, b) => a.snt_kWh - b.snt_kWh);

  console.table(results);
  return results;
})();
```

---

## Huomioita

- **Hinnat sisältävät ALV 25,5%** (kuluttajahinnat).
- **Hinnat eivät sisällä sähkönsiirtoa** (siirtoyhtiön hinnoittelu erikseen).
- Osa tuotteista on **alueellisia** — saatavuus vaihtelee postinumeron mukaan.
- API ei vaadi postinumeroa tai kulutustietoa — palauttaa kaikki tuotteet.
- Virallinen vertailupalvelu: [sahkonhinta.fi/results](https://www.sahkonhinta.fi/results)
