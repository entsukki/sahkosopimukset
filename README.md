# Kiinteähintaiset sähkösopimukset

Seurantatyökalu Suomen kiinteähintaisille sähkösopimuksille. Hakee päivittäin tarjoushinnat [sahkonhinta.fi](https://www.sahkonhinta.fi)-palvelusta ja näyttää ne selaimessa interaktiivisena dashboardina.

**Live-sivu:** [entsukki.github.io/sahkosopimukset](https://entsukki.github.io/sahkosopimukset/)

## Mitä tämä tekee

- **Hakee** kiinteähintaiset sähkösopimukset (12 kk, 13–23 kk, 24 kk, yli 24 kk) sahkonhinta.fi:n API:sta
- **Tallentaa** päivittäiset hinnat CSV-tiedostoon aikasarjaksi
- **Näyttää** halvimmat tarjoukset, hintakehityksen ja vertailutaulukon GitHub Pages -sivustolla
- **Suodattaa** sopimuskeston mukaan — voit valita yhden tai useamman keston, ja kaavio piirtää kullekin oman käyrän

## Rakenne

| Tiedosto | Tarkoitus |
|---|---|
| `fetch_prices.py` | Hakee hinnat API:sta ja lisää ne CSV:hen (ei hae uudelleen jos päivän data on jo tallessa) |
| `kiinteat_tarjoukset.csv` | Kerätty hintadata päivittäin |
| `index.html` | Dashboard-sivu (Chart.js) |
| `consumption.csv` | Oma sähkönkulutusdata |
| `consumption_with_prices.csv` | Kulutus yhdistettynä spot-hintoihin |
| `.github/workflows/daily_fetch.yml` | GitHub Actions: ajaa `fetch_prices.py` joka päivä klo 04:00 Suomen aikaa |

## Automaattinen päivitys

GitHub Actions ajaa `fetch_prices.py`-skriptin joka yö klo 04:00 (Suomen aikaa). Jos uusia tarjouksia löytyy, ne commitoidaan automaattisesti repoon ja sivu päivittyy.

Workflown voi ajaa myös käsin GitHubin Actions-välilehdeltä (workflow_dispatch).

## Käyttö paikallisesti

```bash
# Hae päivän hinnat
python3 fetch_prices.py

# Käynnistä paikallinen palvelin dashboardin katselua varten
python3 -m http.server 8000
# Avaa http://localhost:8000
```

## Datalähde

Hinnat haetaan [sahkonhinta.fi](https://www.sahkonhinta.fi)-palvelun API:sta. Hinnat sisältävät ALV 25,5 % mutta eivät sisällä sähkönsiirtoa.
