"""
Chez l'humain (9606), identifie les réactions les plus spécifiques du foie.

Stratégie:
1. Trouver le BTO "liver"
2. Récupérer les enzymes humaines exprimées dans le foie
3. Pour chaque enzyme, compter le nombre total de tissus -> spécificité = 1/total_tissus
4. Sélectionner les enzymes "enrichies foie" (exprimées dans ≤ T tissus)
5. Récupérer les réactions de ces enzymes enrichies
6. Identifier les 10 métabolites non-currency les plus fréquents dans ces réactions
7. Donner 1 réaction exemple par métabolite
"""

import sys
from collections import defaultdict

sys.path.insert(0, '/lab/user/ask_biota')
from mcp_biota_functions import _init_gws_core
_init_gws_core()

from gws_biota import Enzyme, Reaction, Compound, BTO
from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct
from gws_biota.enzyme.enzyme import EnzymeBTO

TAX_ID = "9606"

# ============================================================
# CURRENCY METABOLITES BLACKLIST (même que l'analyse précédente)
# ============================================================
CURRENCY_EXACT_LOWER = {
    "hydron", "water", "h2o", "oxidane",
    "dioxygen", "carbon dioxide", "hydrogen peroxide",
    "phosphate", "orthophosphate", "hydrogenphosphate",
    "hydrogen phosphate", "diphosphate", "pyrophosphate",
    "ammonium", "ammonia",
    "s-adenosyl-l-methionine", "s-adenosyl-l-homocysteine",
    "ubiquinone", "ubiquinol",
    "tetrahydrofolate", "thiamine diphosphate", "biotin",
    "pyruvate",
}

# Prefix-based matching to catch charge-state variants (e.g., NADP(3-), ATP(4-))
CURRENCY_PREFIXES = [
    "nad", "nadp", "nadh", "nadph",
    "fad", "fadh", "fmn", "fmnh",
    "coenzyme a", "coa-sh",
    "acetyl-coa",
    "atp", "adp", "amp",
    "gtp", "gdp", "gmp",
    "utp", "udp", "ump",
    "ctp", "cdp", "cmp",
]

CURRENCY_SUBSTR_LOWER = [
    "adenosine 5'-triphosphate", "adenosine 5'-diphosphate",
    "adenosine 5'-monophosphate",
    "guanosine 5'-triphosphate", "guanosine 5'-diphosphate",
    "guanosine 5'-monophosphate",
    "uridine 5'-triphosphate", "uridine 5'-diphosphate",
    "uridine 5'-monophosphate",
    "cytidine 5'-triphosphate", "cytidine 5'-diphosphate",
    "cytidine 5'-monophosphate",
    "nicotinamide adenine dinucleotide",
    "flavin adenine dinucleotide",
    "s-adenosyl-l-methionin",   # catches zwitterion variants
    "s-adenosyl-l-homocystein", # catches zwitterion variants
]


def is_currency(name):
    if not name:
        return True
    low = name.lower().strip()
    if low in CURRENCY_EXACT_LOWER:
        return True
    # Prefix match for cofactors with charge states (NAD(1-), ATP(4-), etc.)
    for prefix in CURRENCY_PREFIXES:
        if low == prefix or low.startswith(prefix + "(") or low.startswith(prefix + "h"):
            return True
    for pat in CURRENCY_SUBSTR_LOWER:
        if pat in low:
            return True
    return False


# ==================================================================
# MAIN
# ==================================================================
print("=" * 80)
print("RÉACTIONS SPÉCIFIQUES DU FOIE HUMAIN (9606)")
print("=" * 80)

# ------------------------------------------------------------------
# Step 1: Find liver BTO
# ------------------------------------------------------------------
print("\n[1/6] Recherche du BTO 'liver'...")
liver_candidates = list(BTO.select().where(BTO.name.contains('liver')).limit(20))
liver_bto = None
for b in liver_candidates:
    if b.name and b.name.lower().strip() == 'liver':
        liver_bto = b
        break
if not liver_bto and liver_candidates:
    liver_bto = liver_candidates[0]

if not liver_bto:
    print("   ERREUR: Aucun BTO 'liver' trouvé!")
    sys.exit(1)

print(f"   -> BTO principal: {liver_bto.bto_id} — {liver_bto.name}")
print(f"   Autres entrées liver-related:")
for b in liver_candidates[:8]:
    tag = " <<<" if b.id == liver_bto.id else ""
    print(f"      {b.bto_id}: {b.name}{tag}")

# ------------------------------------------------------------------
# Step 2: Get human enzymes expressed in liver
# ------------------------------------------------------------------
print("\n[2/6] Récupération des enzymes humaines du foie...")

# Get all human enzymes
human_enzymes = list(
    Enzyme.select(Enzyme.id, Enzyme.ec_number, Enzyme.name, Enzyme.uniprot_id)
    .where(Enzyme.tax_id == TAX_ID)
)
human_enzyme_map = {e.id: e for e in human_enzymes}
human_enzyme_id_set = set(human_enzyme_map.keys())
print(f"   -> {len(human_enzymes)} enzymes humaines au total")

# Get all enzyme IDs linked to liver BTO (all taxa)
liver_links = list(EnzymeBTO.select(EnzymeBTO.enzyme).where(EnzymeBTO.bto == liver_bto.id))
liver_all_ids = set(link.enzyme_id for link in liver_links)

# Intersection = human enzymes in liver
human_liver_ids = human_enzyme_id_set & liver_all_ids
print(f"   -> {len(human_liver_ids)} enzymes humaines exprimées dans le foie")

# ------------------------------------------------------------------
# Step 3: Compute tissue specificity for each liver enzyme
# ------------------------------------------------------------------
print("\n[3/6] Calcul de la spécificité tissulaire...")

enzyme_tissue_count = {}  # enzyme_id -> total tissue count
for i, eid in enumerate(human_liver_ids):
    total = EnzymeBTO.select().where(EnzymeBTO.enzyme == eid).count()
    enzyme_tissue_count[eid] = total
    if (i + 1) % 100 == 0:
        print(f"   ... {i+1}/{len(human_liver_ids)}")

# Distribution
buckets = [
    ("1 tissu (foie unique)", lambda c: c == 1),
    ("2-3 tissus", lambda c: 2 <= c <= 3),
    ("4-5 tissus", lambda c: 4 <= c <= 5),
    ("6-10 tissus", lambda c: 6 <= c <= 10),
    ("11-20 tissus", lambda c: 11 <= c <= 20),
    (">20 tissus", lambda c: c > 20),
]

print(f"\n   Distribution tissulaire des {len(human_liver_ids)} enzymes du foie:")
for label, predicate in buckets:
    count = sum(1 for c in enzyme_tissue_count.values() if predicate(c))
    bar = "█" * (count // 2)
    print(f"      {label:<25} {count:>4}  {bar}")

# ------------------------------------------------------------------
# Step 4: Select liver-enriched enzymes (≤ 5 tissues)
# ------------------------------------------------------------------
THRESHOLD = 5
enriched_ids = [eid for eid, c in enzyme_tissue_count.items() if c <= THRESHOLD]
print(f"\n   -> {len(enriched_ids)} enzymes enrichies foie (≤ {THRESHOLD} tissus)")

# If too few, adjust
if len(enriched_ids) < 10:
    THRESHOLD = 10
    enriched_ids = [eid for eid, c in enzyme_tissue_count.items() if c <= THRESHOLD]
    print(f"   -> Seuil ajusté à {THRESHOLD}: {len(enriched_ids)} enzymes enrichies")

# Show top 15 most specific
print(f"\n   Top 15 enzymes les plus spécifiques du foie:")
sorted_spec = sorted(
    [(eid, enzyme_tissue_count[eid]) for eid in enriched_ids],
    key=lambda x: x[1]
)
print(f"   {'EC Number':<15} {'Nom':<40} {'Tissus':<8} {'Spécif.':<8}")
print(f"   {'-'*71}")
for eid, tc in sorted_spec[:15]:
    e = human_enzyme_map[eid]
    name = (e.name[:38] if e.name else "?")
    spec = f"{1/tc:.2f}" if tc > 0 else "?"
    print(f"   {e.ec_number:<15} {name:<40} {tc:<8} {spec:<8}")

# ------------------------------------------------------------------
# Step 5: Get reactions for liver-enriched enzymes
# ------------------------------------------------------------------
print(f"\n[4/6] Récupération des réactions des enzymes enrichies...")
enriched_reactions = set()
rxn_enzymes = defaultdict(list)  # rid -> [(ec, name, tissue_count)]

for eid in enriched_ids:
    e = human_enzyme_map[eid]
    tc = enzyme_tissue_count[eid]
    for link in ReactionEnzyme.select(ReactionEnzyme.reaction).where(
        ReactionEnzyme.enzyme == eid
    ):
        rid = link.reaction_id
        enriched_reactions.add(rid)
        rxn_enzymes[rid].append((e.ec_number, e.name, tc))

print(f"   -> {len(enriched_reactions)} réactions catalysées par des enzymes enrichies foie")

# Compute reaction-level specificity = min tissue count of its enzymes
rxn_specificity = {}
for rid, enzs in rxn_enzymes.items():
    min_tc = min(tc for _, _, tc in enzs)
    rxn_specificity[rid] = min_tc

# Show distribution of reaction specificity
rxn_spec_dist = defaultdict(int)
for rid, spec in rxn_specificity.items():
    if spec == 1:
        rxn_spec_dist["1 tissu"] += 1
    elif spec <= 3:
        rxn_spec_dist["2-3 tissus"] += 1
    elif spec <= 5:
        rxn_spec_dist["4-5 tissus"] += 1
    else:
        rxn_spec_dist[">5 tissus"] += 1

print(f"\n   Spécificité des réactions (min tissus parmi enzymes):")
for label in ["1 tissu", "2-3 tissus", "4-5 tissus", ">5 tissus"]:
    if label in rxn_spec_dist:
        print(f"      {label}: {rxn_spec_dist[label]} réactions")

# ------------------------------------------------------------------
# Step 6: Get non-currency metabolites from enriched reactions
# ------------------------------------------------------------------
print(f"\n[5/6] Collecte des métabolites non-currency...")

metabolite_rxns = defaultdict(set)    # chebi_id -> set of reaction_ids
metabolite_names = {}                  # chebi_id -> name
metabolite_first_rxn = {}              # chebi_id -> first reaction_id

# Sort reactions by specificity (most specific first) so examples are the best ones
sorted_rxns = sorted(enriched_reactions, key=lambda r: rxn_specificity.get(r, 999))

for rid in sorted_rxns:
    for link in ReactionSubstrate.select(ReactionSubstrate.compound).where(
        ReactionSubstrate.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id and not is_currency(comp.name):
            cid = comp.chebi_id
            metabolite_rxns[cid].add(rid)
            metabolite_names[cid] = comp.name
            if cid not in metabolite_first_rxn:
                metabolite_first_rxn[cid] = rid

    for link in ReactionProduct.select(ReactionProduct.compound).where(
        ReactionProduct.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id and not is_currency(comp.name):
            cid = comp.chebi_id
            metabolite_rxns[cid].add(rid)
            metabolite_names[cid] = comp.name
            if cid not in metabolite_first_rxn:
                metabolite_first_rxn[cid] = rid

print(f"   -> {len(metabolite_names)} métabolites non-currency trouvés")

# ------------------------------------------------------------------
# Step 7: Top 10 metabolites
# ------------------------------------------------------------------
print(f"\n[6/6] Classement des métabolites...")

ranked = sorted(metabolite_rxns.items(), key=lambda x: len(x[1]), reverse=True)
top10 = ranked[:10]

print("\n" + "=" * 80)
print(f"TOP 10 MÉTABOLITES NON-CURRENCY DES RÉACTIONS ENRICHIES FOIE")
print(f"(enzymes humaines exprimées dans ≤ {THRESHOLD} tissus dont le foie)")
print("=" * 80)

for rank, (cid, rxn_ids) in enumerate(top10, 1):
    name = metabolite_names.get(cid, "?")
    n_rxns = len(rxn_ids)

    # Get compound details
    comp = Compound.get_or_none(Compound.chebi_id == cid)
    formula = comp.formula if comp and comp.formula else "?"
    mass = f"{comp.mass:.1f}" if comp and comp.mass else "?"

    # Collect enzymes and their specificities
    met_enzymes = []
    for rid in rxn_ids:
        for ec, ename, tc in rxn_enzymes.get(rid, []):
            met_enzymes.append((ec, ename, tc))
    # Unique ECs, sorted by specificity
    seen_ecs = set()
    unique_enzymes = []
    for ec, ename, tc in sorted(met_enzymes, key=lambda x: x[2]):
        if ec not in seen_ecs:
            seen_ecs.add(ec)
            unique_enzymes.append((ec, ename, tc))

    # Best example reaction (most specific)
    best_rid = metabolite_first_rxn.get(cid)
    best_rxn = Reaction.get_or_none(Reaction.id == best_rid) if best_rid else None

    print(f"\n{'─' * 80}")
    print(f"  #{rank}  {name}")
    print(f"{'─' * 80}")
    print(f"  ChEBI     : {cid}")
    print(f"  Formule   : {formula}")
    print(f"  Masse     : {mass} Da")
    print(f"  Réactions : {n_rxns} (foie-enrichies)")
    print(f"  Enzymes   : {len(unique_enzymes)} EC uniques")

    for ec, ename, tc in unique_enzymes[:3]:
        ename_short = (ename[:35] if ename else "?")
        print(f"              EC {ec:<12} ({tc} tissu{'s' if tc > 1 else ''}) — {ename_short}")
    if len(unique_enzymes) > 3:
        print(f"              ... et {len(unique_enzymes) - 3} autres")

    # Example reaction
    if best_rxn and best_rxn.rhea_id:
        # Get non-currency substrates and products
        try:
            subs = [s for s in best_rxn.substrates if not is_currency(s.name)]
            prods = [p for p in best_rxn.products if not is_currency(p.name)]
            sub_str = " + ".join(s.name[:30] for s in subs[:3]) if subs else "..."
            prod_str = " + ".join(p.name[:30] for p in prods[:3]) if prods else "..."
            best_spec = rxn_specificity.get(best_rid, "?")
            print(f"\n  Réaction exemple: {best_rxn.rhea_id}  (enzyme la + spécifique: {best_spec} tissu{'s' if best_spec != 1 else ''})")
            print(f"    {sub_str}")
            print(f"      → {prod_str}")
        except Exception:
            print(f"\n  Réaction exemple: {best_rxn.rhea_id}")

# ==================================================================
# BONUS: Breakdown by metabolic function
# ==================================================================
print(f"\n{'=' * 80}")
print("ANALYSE FONCTIONNELLE DES RÉACTIONS FOIE-ENRICHIES")
print(f"{'=' * 80}")

# Quick keyword classification of the liver metabolites
LIVER_FUNCTIONS = {
    "Métabolisme des acides biliaires": [
        "bile", "cholat", "chenodeoxychol", "taurochol", "glycochol",
        "lithochol", "deoxychol", "ursodeoxychol",
    ],
    "Métabolisme du cholestérol/stéroïdes": [
        "cholester", "sterol", "steroid", "pregnenolon", "progesteron",
        "testoster", "estradiol", "cortisol", "aldosteron", "androst",
    ],
    "Détoxification / Cytochrome P450": [
        "cytochrome", "glutathion", "glucuronide", "sulfotransferase",
        "epoxide", "hydroxylat",
    ],
    "Cycle de l'urée": [
        "ornithin", "citrullin", "argininosuccinat", "urea", "urée",
        "carbamoyl", "arginin",
    ],
    "Métabolisme des acides aminés": [
        "amino acid", "alanin", "glutamat", "aspartat", "serin",
        "glycin", "tyrosin", "phenylalan", "tryptoph", "methionin",
        "homocystein", "cystein",
    ],
    "Glycolyse / Gluconéogenèse": [
        "glucose", "fructose", "pyruvat", "glyceraldehyde",
        "dihydroxyacetone", "phosphoenolpyruvat",
    ],
    "Métabolisme lipidique": [
        "fatty acid", "acyl", "phospholipid", "sphingo", "ceramid",
        "glycerol", "triacylglycer", "phosphatidyl",
    ],
}

func_rxns = defaultdict(set)
for cid, name in metabolite_names.items():
    if not name:
        continue
    low = name.lower()
    for func, keywords in LIVER_FUNCTIONS.items():
        for kw in keywords:
            if kw in low:
                func_rxns[func].update(metabolite_rxns.get(cid, set()))
                break

print(f"\n{'Fonction hépatique':<45} {'Réactions':<10}")
print("-" * 55)
for func, rxns in sorted(func_rxns.items(), key=lambda x: -len(x[1])):
    print(f"{func:<45} {len(rxns):<10}")

# Count unclassified
classified_rxns = set()
for rxns in func_rxns.values():
    classified_rxns.update(rxns)
unclassified = len(enriched_reactions) - len(classified_rxns)
print(f"{'(autres / non classifié)':<45} {unclassified:<10}")

print(f"\n{'=' * 80}")
print("DONE")
print(f"{'=' * 80}")
