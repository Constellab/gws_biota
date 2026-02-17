"""
Question: Chez le taxon 9606, quels sont les 10 composés les plus centraux
(apparaissant dans le plus de réactions) et quelles sont les enzymes associées ?
+ 1 réaction exemple par composé.

Tables traversées: Enzyme → ReactionEnzyme → Reaction → ReactionSubstrate/Product → Compound
"""

import sys
sys.path.insert(0, '/lab/user/ask_biota')
from mcp_biota_functions import _init_gws_core
_init_gws_core()

from gws_biota import Enzyme, Reaction, Compound, Taxonomy
from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct

TAX_ID = "9606"

# ==========================================================
# Step 1: Get all reactions for taxon 9606
# ==========================================================
print("=" * 80)
print(f"TOP 10 COMPOSÉS CENTRAUX - Homo sapiens (tax_id={TAX_ID})")
print("=" * 80)

print("\n[1/4] Récupération des réactions du taxon 9606...")
# Get all enzyme IDs for this taxon
human_enzymes = list(Enzyme.select(Enzyme.id, Enzyme.ec_number).where(Enzyme.tax_id == TAX_ID))
enzyme_ids = {e.id: e.ec_number for e in human_enzymes}
print(f"   -> {len(enzyme_ids)} enzymes humains")

# Get all reaction IDs linked to these enzymes
reaction_ids = set()
enzyme_by_reaction = {}  # reaction_id -> set of ec_numbers

for e in human_enzymes:
    re_links = list(ReactionEnzyme.select(ReactionEnzyme.reaction).where(ReactionEnzyme.enzyme == e.id))
    for link in re_links:
        rid = link.reaction_id
        reaction_ids.add(rid)
        if rid not in enzyme_by_reaction:
            enzyme_by_reaction[rid] = set()
        enzyme_by_reaction[rid].add(e.ec_number)

print(f"   -> {len(reaction_ids)} réactions associées")

# ==========================================================
# Step 2: Count compound appearances across these reactions
# ==========================================================
print("\n[2/4] Comptage des apparitions de chaque composé...")

compound_reactions = {}   # chebi_id -> set of reaction_ids
compound_role = {}        # chebi_id -> {"substrate": count, "product": count}

for rid in reaction_ids:
    # Substrates
    for link in ReactionSubstrate.select(ReactionSubstrate.compound).where(
        ReactionSubstrate.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id:
            cid = comp.chebi_id
            if cid not in compound_reactions:
                compound_reactions[cid] = set()
                compound_role[cid] = {"substrate": 0, "product": 0}
            compound_reactions[cid].add(rid)
            compound_role[cid]["substrate"] += 1

    # Products
    for link in ReactionProduct.select(ReactionProduct.compound).where(
        ReactionProduct.reaction == rid
    ):
        comp = link.compound
        if comp and comp.chebi_id:
            cid = comp.chebi_id
            if cid not in compound_reactions:
                compound_reactions[cid] = set()
                compound_role[cid] = {"substrate": 0, "product": 0}
            compound_reactions[cid].add(rid)
            compound_role[cid]["product"] += 1

print(f"   -> {len(compound_reactions)} composés uniques trouvés")

# ==========================================================
# Step 3: Rank and get top 10
# ==========================================================
print("\n[3/4] Classement par nombre de réactions...")

ranked = sorted(compound_reactions.items(), key=lambda x: len(x[1]), reverse=True)
top10 = ranked[:10]

# ==========================================================
# Step 4: For each top compound, get details + enzymes + 1 example reaction
# ==========================================================
print("\n[4/4] Détails des top 10 composés...\n")

print("=" * 80)
for rank, (chebi_id, rxn_ids) in enumerate(top10, 1):
    comp = Compound.get_or_none(Compound.chebi_id == chebi_id)
    comp_name = comp.name if comp else "?"
    comp_formula = comp.formula if comp else "?"
    comp_mass = comp.mass if comp else "?"

    n_reactions = len(rxn_ids)
    roles = compound_role[chebi_id]

    # Collect all EC numbers from these reactions
    all_ecs = set()
    for rid in rxn_ids:
        if rid in enzyme_by_reaction:
            all_ecs.update(enzyme_by_reaction[rid])

    # Get 1 example reaction
    example_rid = list(rxn_ids)[0]
    example_rxn = Reaction.get_or_none(Reaction.id == example_rid)

    print(f"\n{'─' * 80}")
    print(f"  #{rank}  {comp_name}")
    print(f"{'─' * 80}")
    print(f"  ChEBI ID  : {chebi_id}")
    print(f"  Formule   : {comp_formula}")
    print(f"  Masse     : {comp_mass} Da")
    print(f"  Réactions : {n_reactions} (substrat: {roles['substrate']}, produit: {roles['product']})")
    print(f"  Enzymes   : {len(all_ecs)} EC uniques")

    # Show top 5 enzymes with names
    shown_ecs = sorted(all_ecs)[:5]
    for ec in shown_ecs:
        enz = Enzyme.get_or_none((Enzyme.ec_number == ec) & (Enzyme.tax_id == TAX_ID))
        enz_name = enz.name if enz else "?"
        print(f"              - EC {ec}: {enz_name}")
    if len(all_ecs) > 5:
        print(f"              ... et {len(all_ecs) - 5} autres")

    # Example reaction
    if example_rxn:
        subs = [f"{s.name} ({s.chebi_id})" for s in example_rxn.substrates]
        prods = [f"{p.name} ({p.chebi_id})" for p in example_rxn.products]
        print(f"\n  Réaction exemple: {example_rxn.rhea_id}")
        print(f"    {' + '.join(subs[:3])}")
        print(f"      → {' + '.join(prods[:3])}")

print(f"\n{'=' * 80}")
print("DONE")
print(f"{'=' * 80}")
