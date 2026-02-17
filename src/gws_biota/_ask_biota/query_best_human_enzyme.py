"""
Question: Quel est l'enzyme humain exprimé dans le plus de tissus ET
qui catalyse le plus de réactions impliquant des composés de masse > 500 Da ?

Stratégie:
1. Récupérer tous les EC uniques humains (tax_id=9606)
2. Pour chaque EC, compter les tissus BTO (via EnzymeBTO)
3. Pour chaque EC, compter les réactions avec composés > 500 Da
4. Score combiné = nb_tissus * nb_reactions_heavy → top 1
"""

import sys
sys.path.insert(0, '/lab/user/ask_biota')

from mcp_biota_functions import _init_gws_core

# Step 0: Initialize
_init_gws_core()

from gws_biota import Enzyme, Compound
from gws_biota.enzyme.enzyme import EnzymeBTO
from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct

# ==========================================================
# Step 1: Get all unique EC numbers for Homo sapiens
# ==========================================================
print("=" * 70)
print("RECHERCHE: Meilleur enzyme humain (tissus x reactions lourdes)")
print("=" * 70)

print("\n[1/4] Récupération des EC uniques humains...")
human_enzymes = list(Enzyme.select(Enzyme.ec_number, Enzyme.id).where(Enzyme.tax_id == "9606"))
ec_to_enzyme_ids = {}
for e in human_enzymes:
    if e.ec_number:
        if e.ec_number not in ec_to_enzyme_ids:
            ec_to_enzyme_ids[e.ec_number] = []
        ec_to_enzyme_ids[e.ec_number].append(e.id)

unique_ecs = list(ec_to_enzyme_ids.keys())
print(f"   -> {len(human_enzymes)} enzymes, {len(unique_ecs)} EC uniques")

# ==========================================================
# Step 2: Count BTO tissues per EC
# ==========================================================
print("\n[2/4] Comptage des tissus BTO par EC...")
ec_tissue_count = {}
for i, ec in enumerate(unique_ecs):
    enzyme_ids = ec_to_enzyme_ids[ec]
    bto_ids = set()
    for eid in enzyme_ids:
        for link in EnzymeBTO.select(EnzymeBTO.bto).where(EnzymeBTO.enzyme == eid):
            if link.bto_id:
                bto_ids.add(link.bto_id)
    ec_tissue_count[ec] = len(bto_ids)
    if (i + 1) % 200 == 0:
        print(f"   ... {i+1}/{len(unique_ecs)} EC traités")

# Filter ECs with at least 1 tissue
ecs_with_tissues = {ec: count for ec, count in ec_tissue_count.items() if count > 0}
print(f"   -> {len(ecs_with_tissues)} EC exprimés dans au moins 1 tissu")

# Show top 10 by tissue count
top_tissue = sorted(ecs_with_tissues.items(), key=lambda x: x[1], reverse=True)[:10]
print("   Top 10 par tissus:")
for ec, count in top_tissue:
    print(f"      EC {ec}: {count} tissus")

# ==========================================================
# Step 3: Count reactions with compounds > 500 Da (only for ECs with tissues)
# ==========================================================
print(f"\n[3/4] Comptage des réactions avec composés > 500 Da pour {len(ecs_with_tissues)} EC...")
ec_heavy_reaction_count = {}

for i, ec in enumerate(ecs_with_tissues.keys()):
    enzyme_ids = ec_to_enzyme_ids[ec]
    heavy_reactions = set()

    for eid in enzyme_ids:
        re_links = list(ReactionEnzyme.select(ReactionEnzyme.reaction).where(
            ReactionEnzyme.enzyme == eid
        ))
        for rel in re_links:
            reaction_id = rel.reaction_id
            # Check substrates
            has_heavy = False
            for sub in ReactionSubstrate.select(ReactionSubstrate.compound).where(
                ReactionSubstrate.reaction == reaction_id
            ):
                comp = sub.compound
                if comp and comp.mass and comp.mass > 500:
                    has_heavy = True
                    break

            if not has_heavy:
                for prod in ReactionProduct.select(ReactionProduct.compound).where(
                    ReactionProduct.reaction == reaction_id
                ):
                    comp = prod.compound
                    if comp and comp.mass and comp.mass > 500:
                        has_heavy = True
                        break

            if has_heavy:
                heavy_reactions.add(reaction_id)

    ec_heavy_reaction_count[ec] = len(heavy_reactions)
    if (i + 1) % 100 == 0:
        print(f"   ... {i+1}/{len(ecs_with_tissues)} EC traités")

ecs_with_heavy = {ec: count for ec, count in ec_heavy_reaction_count.items() if count > 0}
print(f"   -> {len(ecs_with_heavy)} EC avec au moins 1 réaction impliquant un composé > 500 Da")

# ==========================================================
# Step 4: Combined score and final answer
# ==========================================================
print("\n[4/4] Calcul du score combiné (tissus x réactions_lourdes)...")
scores = []
for ec in ecs_with_heavy:
    tissues = ec_tissue_count[ec]
    heavy_rxns = ec_heavy_reaction_count[ec]
    score = tissues * heavy_rxns
    scores.append((ec, tissues, heavy_rxns, score))

scores.sort(key=lambda x: x[3], reverse=True)

print("\n" + "=" * 70)
print("TOP 10 ENZYMES HUMAINS (score = tissus x réactions_lourdes)")
print("=" * 70)
print(f"{'Rang':<5} {'EC Number':<15} {'Tissus':<10} {'Rxns>500Da':<12} {'Score':<10}")
print("-" * 52)

for rank, (ec, tissues, heavy_rxns, score) in enumerate(scores[:10], 1):
    print(f"{rank:<5} {ec:<15} {tissues:<10} {heavy_rxns:<12} {score:<10}")

# Get details on the winner
if scores:
    winner_ec = scores[0][0]
    print(f"\n{'=' * 70}")
    print(f"REPONSE: EC {winner_ec}")
    print(f"{'=' * 70}")

    # Get enzyme name
    winner_enzyme = Enzyme.get_or_none(
        (Enzyme.ec_number == winner_ec) & (Enzyme.tax_id == "9606")
    )
    if winner_enzyme:
        print(f"  Nom: {winner_enzyme.name}")
        print(f"  UniProt ID: {winner_enzyme.uniprot_id}")

    print(f"  Tissus BTO: {scores[0][1]}")
    print(f"  Réactions avec composés > 500 Da: {scores[0][2]}")
    print(f"  Score combiné: {scores[0][3]}")

    # Show tissue details using existing function
    from mcp_biota_functions import get_enzyme_tissue_sources
    tissue_result = get_enzyme_tissue_sources(winner_ec)
    if tissue_result.get("tissues"):
        print(f"\n  Tissus d'expression:")
        for t in tissue_result["tissues"][:15]:
            print(f"    - {t['bto_id']}: {t['name']}")

    # Show heavy compound reactions
    from mcp_biota_functions import join_enzyme_reactions_compounds
    rxn_result = join_enzyme_reactions_compounds(winner_ec, limit=50)
    if rxn_result.get("reactions"):
        print(f"\n  Réactions avec composés > 500 Da:")
        shown = 0
        for r in rxn_result["reactions"]:
            heavy_compounds = []
            for c in r.get("substrates", []) + r.get("products", []):
                # Need to check mass
                comp = Compound.get_or_none(Compound.chebi_id == c.get("chebi_id"))
                if comp and comp.mass and comp.mass > 500:
                    heavy_compounds.append(f"{comp.name} ({comp.mass:.1f} Da)")
            if heavy_compounds:
                print(f"    - {r['rhea_id']}: {', '.join(heavy_compounds[:3])}")
                shown += 1
                if shown >= 5:
                    break

print(f"\n{'=' * 70}")
