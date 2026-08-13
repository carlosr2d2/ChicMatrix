"""Generate a frozen multi-label style gold set (300–500 items).

Items mix:
- lexicon: wording F0 should catch
- paraphrase: human-true labels, synonyms F0 may miss (recall gap)
- overlap: multi-label (e.g. biker+rocker)
- negative: no style tags
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "fixtures" / "style_gold" / "gold_set.jsonl"

BRANDS = [
    "Maison Noir",
    "Urban Loom",
    "Atelier Vue",
    "North Line",
    "Rivet & Co",
    "Studio Hilo",
    "Cinder Road",
]


def item(
    idx: int,
    *,
    name: str,
    description: str,
    tags: list[str],
    subset: str,
    locale: str = "en",
    brand: str | None = None,
    category: str | None = None,
    color: str | None = None,
) -> dict:
    return {
        "id": f"gold-{idx:04d}",
        "name": name,
        "description": description,
        "brand": brand or BRANDS[idx % len(BRANDS)],
        "category": category,
        "color": color,
        "locale": locale,
        "gold_tags": sorted(set(tags)),
        "subset": subset,
    }


def build() -> list[dict]:
    rows: list[dict] = []
    i = 1

    def add(**kwargs):
        nonlocal i
        rows.append(item(i, **kwargs))
        i += 1

    # --- Formal (lexicon) ---
    formal_lex = [
        ("Structured Wool Blazer", "Tailored formal blazer for office evenings.", "outerwear", "black"),
        ("Pleated Silk Blouse", "Pleated silk blouse for formal office looks.", "office", "beige"),
        ("Silk Midi Dress", "Silk midi evening dress with elegant formal silhouette.", "evening", "black"),
        ("Draped Evening Gown", "Formal evening gown with elegant drape.", "evening", "black"),
        ("Tailored Wide Leg Trouser", "Formal office trouser with tailored drape.", "office", "grey"),
        ("Navy Suit Jacket", "Classic suit jacket tailored for office.", "office", "navy"),
        ("Sastre de Lana", "Chaqueta sastre elegante para oficina.", "office", "black"),
        ("Blazer Cropped", "Cropped blazer tailored for office days.", "office", "cream"),
        ("Gown Column", "Column evening gown in silk.", "evening", "ivory"),
        ("Office Sheath", "Tailored sheath for formal office.", "office", "navy"),
    ]
    for name, desc, cat, color in formal_lex:
        locale = "es" if "Sastre" in name or "oficina" in desc else "en"
        add(name=name, description=desc, tags=["formal"], subset="lexicon", category=cat, color=color, locale=locale)

    # Repeat with variants to reach volume without being identical
    for n in range(1, 21):
        add(
            name=f"Tailored Blazer {n:02d}",
            description=f"Formal tailored blazer {n} for office and evening.",
            tags=["formal"],
            subset="lexicon",
            category="office",
            color="black" if n % 2 else "navy",
        )

    # Formal paraphrase (F0 may miss)
    formal_para = [
        ("Tuxedo Dinner Jacket", "Peak-lapel tux for black-tie dinners.", ["formal"]),
        ("Oxford Dress Shirt", "Crisp poplin shirt for board meetings.", ["formal"]),
        ("Pencil Skirt", "Knee-length skirt for corporate wear.", ["formal"]),
        ("Traje de Noche", "Vestido largo para gala y cóctel.", ["formal"]),
        ("Camisa de Vestir", "Camisa almidonada para juntas.", ["formal"]),
        ("Corbata de Seda", "Accesorio clásico de traje ejecutivo.", ["formal"]),
        ("Cocktail Midi", "Knee cocktail look without saying gown.", ["formal"]),
        ("Cufflink Shirt", "French-cuff shirt for ceremonies.", ["formal"]),
        ("Palazzo Evening", "Floor palazzo for a gala dinner.", ["formal"]),
        ("Executive Wool Trouser", "Boardroom wool trousers, pressed crease.", ["formal"]),
    ]
    for n, (name, desc, tags) in enumerate(formal_para * 3, start=1):
        add(
            name=f"{name} {n:02d}" if n > 10 else name,
            description=desc,
            tags=tags,
            subset="paraphrase",
            locale="es" if any(c in name for c in "áéíóúñ") or name.startswith(("Traje", "Camisa", "Corbata")) else "en",
            category="evening" if "gala" in desc.lower() or "cocktail" in desc.lower() or "noche" in name.lower() else "office",
        )

    # --- Sport ---
    sport_lex = [
        ("Performance Running Tank", "Athletic dry-fit performance tank for gym training and running."),
        ("Gym Training Shorts", "Sport shorts for gym training sessions."),
        ("Athleisure Track Jacket", "Athletic athleisure jacket for sport days."),
        ("Running Tight", "Performance running tights, dry-fit."),
        ("Camiseta Deportiva", "Prenda de deporte para gym y running."),
        ("Sport Bra", "Athletic sport bra for training."),
        ("Sneakers Training", "Gym sneakers for athletic training."),
    ]
    for name, desc in sport_lex:
        add(name=name, description=desc, tags=["sport"], subset="lexicon", category="activewear")
    for n in range(1, 22):
        add(
            name=f"Running Tank {n:02d}",
            description=f"Athletic performance running top {n} for gym training.",
            tags=["sport"],
            subset="lexicon",
            category="activewear",
        )
    sport_para = [
        ("Marathon Split Shorts", "Lightweight shorts for 10k and half marathon."),
        ("Yoga Legging", "Four-way stretch for studio yoga."),
        ("Cycling Jersey", "Breathable jersey for road rides."),
        ("Sudadera de Entrenamiento", "Capa ligera para el gimnasio."),
        ("Swim Brief", "Competition swim brief."),
        ("Hiking Softshell", "Trail layer for weekend hikes."),
        ("Tennis Skort", "Court skort with built-in short."),
        ("Boxeo Shorts", "Shorts para sparring en el ring."),
    ]
    for n, (name, desc) in enumerate(sport_para * 3, start=1):
        add(
            name=f"{name} {n:02d}" if n > 8 else name,
            description=desc,
            tags=["sport"],
            subset="paraphrase",
            category="activewear",
            locale="es" if "Sudadera" in name or "Boxeo" in name else "en",
        )

    # --- Biker ---
    for n in range(1, 26):
        add(
            name=f"Leather Biker Jacket {n:02d}",
            description="Asymmetric leather biker jacket with harness details, motorcycle-ready.",
            tags=["biker"],
            subset="lexicon",
            category="outerwear",
            color="black",
        )
    for n in range(1, 16):
        add(
            name=f"Chaqueta Motociclista {n:02d}",
            description="Chaqueta moto de cuero para rider.",
            tags=["biker"],
            subset="lexicon",
            locale="es",
            category="outerwear",
        )
    biker_para = [
        ("Cafe Racer Jacket", "Cropped racer leather with zip cuffs, no biker word."),
        ("Engineer Boot", "Tall shaft boot with buckle, highway riding."),
        ("Chaleco de Cuero", "Chaleco con parches para ruta en moto.",),
    ]
    for n in range(1, 13):
        name, desc = biker_para[(n - 1) % 3]
        add(name=f"{name} {n:02d}", description=desc, tags=["biker"], subset="paraphrase", category="outerwear")

    # --- Rocker ---
    for n in range(1, 22):
        add(
            name=f"Studded Leather Jacket {n:02d}",
            description="Distressed rocker leather jacket with studded punk hardware.",
            tags=["rocker"],
            subset="lexicon",
            category="outerwear",
        )
    for n in range(1, 16):
        add(
            name=f"Band Tee {n:02d}",
            description="Vintage band tee with metal print, rock attitude.",
            tags=["rocker"],
            subset="lexicon",
            category="tops",
        )
    for n in range(1, 13):
        add(
            name=f"Grunge Flannel {n:02d}",
            description="Plaid flannel over a faded concert shirt.",
            tags=["rocker"],
            subset="paraphrase",
            category="tops",
        )

    # --- Casual ---
    for n in range(1, 22):
        add(
            name=f"Cashmere Crewneck {n:02d}",
            description="Everyday casual crewneck knit for weekend wear.",
            tags=["casual"],
            subset="lexicon",
            category="tops",
            color="beige",
        )
    for n in range(1, 16):
        add(
            name=f"Selvedge Straight Denim {n:02d}",
            description="Straight jeans in selvedge denim, relaxed casual staple.",
            tags=["casual"],
            subset="lexicon",
            category="tops",
            color="blue",
        )
    for n in range(1, 13):
        add(
            name=f"Chinos Weekend {n:02d}",
            description="Soft cotton chinos for Saturday errands.",
            tags=["casual"],
            subset="paraphrase",
            category="tops",
        )

    # --- Minimal ---
    for n in range(1, 22):
        add(
            name=f"Minimalist Wool Coat {n:02d}",
            description="Minimalist wool coat with clean lines and understated contemporary silhouette.",
            tags=["minimal"],
            subset="lexicon",
            category="outerwear",
            color="grey",
        )
    for n in range(1, 13):
        add(
            name=f"Capsule Tee {n:02d}",
            description="Unadorned crew in a quiet palette, no logos.",
            tags=["minimal"],
            subset="paraphrase",
            category="tops",
            color="ivory",
        )

    # --- Streetwear ---
    for n in range(1, 22):
        add(
            name=f"Oversized Graphic Hoodie {n:02d}",
            description="Oversized streetwear hoodie with drop shoulder and graphic tee energy for urban looks.",
            tags=["streetwear"],
            subset="lexicon",
            category="tops",
            color="black",
        )
    for n in range(1, 13):
        add(
            name=f"Cargo Baggy Pant {n:02d}",
            description="Skate-fit cargo with extra pockets, city layering.",
            tags=["streetwear"],
            subset="paraphrase",
            category="tops",
        )

    # --- Overlap multi-label ---
    for n in range(1, 21):
        add(
            name=f"Leather Biker Rocker Jacket {n:02d}",
            description="Leather biker jacket with harness, studded punk rocker edge and distressed finish.",
            tags=["biker", "rocker"],
            subset="overlap",
            category="outerwear",
            color="black",
        )
    for n in range(1, 11):
        add(
            name=f"Structured Minimal Blazer {n:02d}",
            description="Structured wool tailored blazer with clean lines, understated formal office look.",
            tags=["formal", "minimal"],
            subset="overlap",
            category="office",
        )
    for n in range(1, 11):
        add(
            name=f"Relaxed Denim Hoodie Look {n:02d}",
            description="Casual oversized hoodie over selvedge denim jeans, urban streetwear weekend.",
            tags=["casual", "streetwear"],
            subset="overlap",
            category="tops",
        )
    for n in range(1, 8):
        add(
            name=f"Athleisure Weekend Knit {n:02d}",
            description="Casual athletic athleisure knit for gym-to-weekend sport days.",
            tags=["sport", "casual"],
            subset="overlap",
            category="tops",
        )

    # --- Negatives: no closed-vocab style ---
    negatives = [
        ("Cotton Socks 3-Pack", "Basic ankle socks, no fashion styling claimed."),
        ("Umbrella Compact", "Black compact umbrella for rain."),
        ("Phone Case Clear", "Transparent protective case."),
        ("Belt Sizing Kit", "Hardware kit, not apparel styling."),
        ("Gift Card Envelope", "Store credit envelope."),
        ("Steamer Handheld", "Garment steamer accessory."),
        ("Lint Roller", "Household lint roller."),
        ("Care Card", "Washing instruction card."),
    ]
    for n in range(1, 25):
        name, desc = negatives[(n - 1) % len(negatives)]
        add(name=f"{name} {n:02d}", description=desc, tags=[], subset="negative", category=None)

    return rows


def main() -> None:
    rows = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["subset"]] = counts.get(row["subset"], 0) + 1
    print(f"Wrote {len(rows)} items to {OUTPUT}")
    print("subsets", counts)


if __name__ == "__main__":
    main()
