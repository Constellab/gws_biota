"""
Répartition des réactions humaines (9606) par grandes classes métaboliques,
en excluant les currency metabolites.

Classes: Glucides, Acides aminés, Acides carboxyliques/TCA, Lipides, Nucléotides, Stéroïdes.
Top 3 classes avec 5 métabolites et 5 réactions exemples par classe.
"""

import sys
from collections import defaultdict

sys.path.insert(0, '/lab/user/ask_biota')
from mcp_biota_functions import _init_gws_core
_init_gws_core()

from gws_biota import Enzyme, Reaction, Compound
from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct

TAX_ID = "9606"

# ============================================================
# CURRENCY METABOLITES BLACKLIST
# ============================================================
CURRENCY_EXACT_LOWER = {
    # Proton, water
    "hydron", "water", "h2o", "oxidane",
    # O2, CO2, H2O2
    "dioxygen", "carbon dioxide", "hydrogen peroxide",
    # Inorganic phosphate / pyrophosphate
    "phosphate", "orthophosphate", "hydrogenphosphate",
    "hydrogen phosphate", "diphosphate", "pyrophosphate",
    # Nitrogen
    "ammonium", "ammonia",
    # NAD/NADP
    "nad(+)", "nadh", "nad+", "nadp(+)", "nadp+", "nadph",
    # FAD/FMN
    "fad", "fadh2", "fmn", "fmnh2",
    # CoA
    "coenzyme a", "coa", "acetyl-coa",
    # SAM/SAH
    "s-adenosyl-l-methionine", "s-adenosyl-l-homocysteine",
    # Electron carriers
    "ubiquinone", "ubiquinol",
    # Misc cofactors
    "tetrahydrofolate", "thiamine diphosphate",
    "biotin",
}

# Substring patterns for long-form names (NTPs, coenzyme variants)
CURRENCY_SUBSTR_LOWER = [
    "adenosine 5'-triphosphate", "adenosine 5'-diphosphate",
    "adenosine 5'-monophosphate",
    "guanosine 5'-triphosphate", "guanosine 5'-diphosphate",
    "guanosine 5'-monophosphate",
    "uridine 5'-triphosphate", "uridine 5'-diphosphate",
    "uridine 5'-monophosphate",
    "cytidine 5'-triphosphate", "cytidine 5'-diphosphate",
    "cytidine 5'-monophosphate",
    "nicotinamide adenine dinucleotide",  # catches NAD+/NADH/NADP+/NADPH variants
    "flavin adenine dinucleotide",  # FAD variants
]


def is_currency(name):
    """Check if a compound is a currency metabolite."""
    if not name:
        return True  # unknown -> skip
    low = name.lower().strip()
    if low in CURRENCY_EXACT_LOWER:
        return True
    for pat in CURRENCY_SUBSTR_LOWER:
        if pat in low:
            return True
    return False


# ============================================================
# METABOLIC CLASS KEYWORDS (substring matching on compound name)
# ============================================================
CLASS_KEYWORDS = {
    "Glucides (sucres)": [
        "glucose", "fructose", "galactose", "mannose", "ribose", "xylose",
        "saccharid", "hexose", "pentose", "glucuronate", "glucuronide",
        "glycosid", "fucos", "sialic", "neuraminic", "maltos", "lactos",
        "sucros", "trehalo", "glucosamin", "galactosamin", "mannosamin",
        "erythrose", "sedoheptulo", "ribulos", "gluconat", "sorbitol",
        "glyceraldehyde", "dihydroxyacetone", "glycogen", "starch",
        "cellulose", "chitin", "deoxyribos",
    ],
    "Acides aminés": [
        "alanin", "glycin", "valin", "leucin", "isoleucin",
        "prolin", "phenylalan", "tryptoph", "serin", "threonin",
        "cystein", "tyrosin", "asparagin", "glutamin", "aspartat",
        "glutamat", "lysin", "arginin", "histidin", "methionin",
        "homocystein", "ornithin", "citrullin",
        "taurin", "creatin", "sarcosin", "amino acid",
    ],
    "Acides carboxyliques / TCA": [
        "citrat", "citric", "isocitrat", "succinat", "succinyl",
        "fumarat", "fumaric", "malat", "malic",
        "oxaloacetat", "pyruvat", "pyruvic", "lactat", "lactic",
        "oxoglutarat", "ketoglutarat", "glyoxylat", "oxalosuccinat",
    ],
    "Lipides": [
        "fatty acid", "acyl-coa", "phospholipid",
        "sphingo", "ceramid", "phosphatidyl", "diacylglycer",
        "triacylglycer", "palmitoyl", "stearoyl", "oleoyl", "linoleoyl",
        "arachidon", "eicosa", "prostaglandin", "leukotriene", "thromboxane",
        "palmitat", "stearat", "oleat", "linoleat", "arachidonat",
        "cardiolipin", "gangliosid", "cerebrosid",
        "palmitic", "stearic", "oleic", "linoleic", "myristic",
        "lauric", "malonyl-coa", "glycerol", "lyso",
        "acylglycer", "phosphatidat",
    ],
    "Nucléotides": [
        "nucleotid", "nucleosid",
        "adenin", "guanin", "cytosin", "uracil", "thymin",
        "adenosin", "guanosin", "cytidin", "uridin", "thymidin",
        "deoxyadenosin", "deoxyguanosin", "deoxycytidin",
        "inosin", "xanthin", "hypoxanthin", "xanthosin",
        "purin", "pyrimidin",
    ],
    "Stéroïdes": [
        "steroid", "sterol", "cholester", "testoster", "estradiol",
        "estron", "estriol", "progesteron", "cortisol", "cortison",
        "aldosteron", "pregnenolon", "dehydroepiandrosteron",
        "androst", "corticoster", "bile acid", "cholat",
        "chenodeoxychol", "lithochol", "deoxychol",
        "ergoster", "calciferol", "calcidiol", "calcitriol",
    ],
}


def classify_compound(name):
    """Return set of metabolic classes for a compound based on its name."""
    if not name:
        return set()
    low = name.lower()
    classes = set()
    for cls, keywords in CLASS_KEYWORDS.items():
        for kw in keywords:
            if kw in low:
                classes.add(cls)
                break
    return classes


# ==================================================================
# MAIN
# ==================================================================
print("=" * 80)
print("RÉPARTITION DES RÉACTIONS HUMAINES (9606) PAR CLASSE MÉTABOLIQUE")
print("=" * 80)

# ------------------------------------------------------------------
# Step 1: Get all human reaction IDs
# ------------------------------------------------------------------
print("\n[1/5] Récupération des réactions humaines...")
enzymes = list(Enzyme.select(Enzyme.id).where(Enzyme.tax_id == TAX_ID))
reaction_ids = set()
for e in enzymes:
    for link in ReactionEnzyme.select(ReactionEnzyme.reaction).where(
        ReactionEnzyme.enzyme == e.id
    ):
        reaction_ids.add(link.reaction_id)
print(f"   -> {len(enzymes)} enzymes, {len(reaction_ids)} réactions")

# ------------------------------------------------------------------
# Step 2: Collect compounds per reaction
# ------------------------------------------------------------------
print("\n[2/5] Collecte des composés par réaction...")
rxn_compounds = defaultdict(list)  # rid -> [(chebi_id, name, role), ...]
compound_names = {}                # chebi_id -> name
compound_rxn_sets = defaultdict(set)  # chebi_id -> set of reaction_ids

for i, rid in enumerate(reaction_ids):
    for link in ReactionSubstrate.select(ReactionSubstrate.compound).where(
        ReactionSubstrate.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id:
            rxn_compounds[rid].append((comp.chebi_id, comp.name, "S"))
            compound_names[comp.chebi_id] = comp.name
            compound_rxn_sets[comp.chebi_id].add(rid)

    for link in ReactionProduct.select(ReactionProduct.compound).where(
        ReactionProduct.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id:
            rxn_compounds[rid].append((comp.chebi_id, comp.name, "P"))
            compound_names[comp.chebi_id] = comp.name
            compound_rxn_sets[comp.chebi_id].add(rid)

    if (i + 1) % 300 == 0:
        print(f"   ... {i+1}/{len(reaction_ids)}")

print(f"   -> {len(compound_names)} composés uniques dans {len(rxn_compounds)} réactions")

# ------------------------------------------------------------------
# Step 3: Filter currency metabolites
# ------------------------------------------------------------------
print("\n[3/5] Filtrage des currency metabolites...")
currency_ids = set()
for cid, name in compound_names.items():
    if is_currency(name):
        currency_ids.add(cid)

# Also flag by frequency: top compounds (>200 reactions) that look like cofactors
top_freq = sorted(compound_rxn_sets.items(), key=lambda x: len(x[1]), reverse=True)
for cid, rxns in top_freq[:25]:
    name = compound_names.get(cid, "")
    if len(rxns) > 200:
        currency_ids.add(cid)

print(f"   -> {len(currency_ids)} currency metabolites exclus:")
for cid in sorted(currency_ids, key=lambda c: -len(compound_rxn_sets[c])):
    name = compound_names.get(cid, "?")
    n = len(compound_rxn_sets[cid])
    print(f"      - {name[:40]:<42} ({cid}) — {n} rxns")

# ------------------------------------------------------------------
# Step 4: Classify non-currency compounds
# ------------------------------------------------------------------
print("\n[4/5] Classification des composés non-currency...")
compound_classes = {}  # chebi_id -> set of class names
unclassified = 0

for cid, name in compound_names.items():
    if cid in currency_ids:
        continue
    classes = classify_compound(name)
    if classes:
        compound_classes[cid] = classes
    else:
        unclassified += 1

classified = len(compound_classes)
print(f"   -> {classified} composés classifiés, {unclassified} non classifiés (hors périmètre)")

# Per-class summary
for cls in CLASS_KEYWORDS:
    n = sum(1 for cc in compound_classes.values() if cls in cc)
    print(f"      {cls}: {n} composés")

# ------------------------------------------------------------------
# Step 5: Aggregate reactions by class
# ------------------------------------------------------------------
print("\n[5/5] Agrégation des réactions par classe...")
class_reactions = defaultdict(set)      # class -> set of reaction_ids
class_compounds = defaultdict(set)      # class -> set of chebi_ids
class_comp_freq = defaultdict(lambda: defaultdict(int))  # class -> {chebi_id: count}
class_example_rxns = defaultdict(list)  # class -> [(rid, non_currency_comps)]

for rid, comps in rxn_compounds.items():
    non_currency = [(cid, name, role) for cid, name, role in comps if cid not in currency_ids]
    rxn_classes = set()

    for cid, name, role in non_currency:
        if cid in compound_classes:
            for cls in compound_classes[cid]:
                rxn_classes.add(cls)
                class_compounds[cls].add(cid)
                class_comp_freq[cls][cid] += 1

    for cls in rxn_classes:
        class_reactions[cls].add(rid)
        if len(class_example_rxns[cls]) < 30:
            class_example_rxns[cls].append((rid, non_currency))

# ==================================================================
# RESULTS
# ==================================================================
print("\n" + "=" * 80)
print("RÉSULTATS: Répartition par classe")
print("=" * 80)

ranked = sorted(class_reactions.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\n{'Rang':<6} {'Classe':<35} {'Réactions':<12} {'Composés':<12}")
print("-" * 65)
for rank, (cls, rxns) in enumerate(ranked, 1):
    n_comps = len(class_compounds[cls])
    marker = " <<<" if rank <= 3 else ""
    print(f"{rank:<6} {cls:<35} {len(rxns):<12} {n_comps:<12}{marker}")

total_classified_rxns = set()
for rxns in class_reactions.values():
    total_classified_rxns.update(rxns)
non_currency_rxns = set()
for rid, comps in rxn_compounds.items():
    if any(cid not in currency_ids for cid, _, _ in comps):
        non_currency_rxns.add(rid)

print(f"\nTotal réactions classifiées: {len(total_classified_rxns)} / {len(non_currency_rxns)} "
      f"({len(total_classified_rxns)/max(len(non_currency_rxns),1)*100:.1f}%)")

# ==================================================================
# TOP 3 DETAILS
# ==================================================================
print("\n" + "=" * 80)
print("DÉTAILS DES TOP 3 CLASSES")
print("=" * 80)

for rank, (cls, rxn_ids_set) in enumerate(ranked[:3], 1):
    n_rxn = len(rxn_ids_set)
    n_comp = len(class_compounds[cls])

    print(f"\n{'━' * 80}")
    print(f"  #{rank}  {cls}  —  {n_rxn} réactions, {n_comp} composés")
    print(f"{'━' * 80}")

    # --- 5 metabolites exemples (les plus fréquents dans cette classe) ---
    freq = class_comp_freq[cls]
    top_comps = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n  ▸ 5 métabolites exemples (plus fréquents):")
    for i, (cid, count) in enumerate(top_comps, 1):
        name = compound_names.get(cid, "?")
        total = len(compound_rxn_sets.get(cid, set()))
        print(f"    {i}. {name[:45]:<47} ({cid}) — {count} apparitions")

    # --- 5 reactions exemples ---
    print(f"\n  ▸ 5 réactions exemples:")
    shown = 0
    seen_rhea = set()
    for rid, non_currency in class_example_rxns[cls]:
        rxn = Reaction.get_or_none(Reaction.id == rid)
        if not rxn or not rxn.rhea_id or rxn.rhea_id in seen_rhea:
            continue

        # Build non-currency substrates/products for this reaction
        subs_names = []
        prods_names = []
        for cid, name, role in non_currency:
            if name:
                if role == "S":
                    subs_names.append(name[:25])
                else:
                    prods_names.append(name[:25])

        if not subs_names and not prods_names:
            continue

        seen_rhea.add(rxn.rhea_id)
        shown += 1
        sub_str = " + ".join(subs_names[:3]) if subs_names else "..."
        prod_str = " + ".join(prods_names[:3]) if prods_names else "..."
        print(f"    {shown}. {rxn.rhea_id}")
        print(f"       {sub_str}")
        print(f"         → {prod_str}")

        if shown >= 5:
            break

    if shown == 0:
        print("    (aucune réaction avec Rhea ID trouvée)")

# ==================================================================
# CROSS-CLASS OVERLAP
# ==================================================================
print(f"\n{'=' * 80}")
print("CHEVAUCHEMENT ENTRE CLASSES (réactions partagées)")
print(f"{'=' * 80}")
class_names = [cls for cls, _ in ranked[:6]]
print(f"\n{'':>35}", end="")
for cn in class_names:
    short = cn[:8]
    print(f" {short:>8}", end="")
print()

for cn1 in class_names:
    short1 = cn1[:35]
    print(f"{short1:>35}", end="")
    for cn2 in class_names:
        overlap = len(class_reactions[cn1] & class_reactions[cn2])
        print(f" {overlap:>8}", end="")
    print()

print(f"\n{'=' * 80}")
print("DONE")
print(f"{'=' * 80}")
