"""
Compare les 10 composés les plus centraux entre Homo sapiens (9606) et Mus musculus (10090).
"""

import sys
sys.path.insert(0, '/lab/user/ask_biota')
from mcp_biota_functions import _init_gws_core
_init_gws_core()

from gws_biota import Enzyme, Reaction, Compound, Taxonomy
from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct


def analyze_taxon(tax_id):
    """Return compound_reactions dict and ranked top for a taxon."""
    tax = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = tax.name if tax else "?"
    print(f"\n   Analyse de {tax_name} (tax_id={tax_id})...")

    # Get enzymes
    enzymes = list(Enzyme.select(Enzyme.id, Enzyme.ec_number).where(Enzyme.tax_id == tax_id))
    enzyme_ids = {e.id: e.ec_number for e in enzymes}
    print(f"   -> {len(enzyme_ids)} enzymes")

    # Get reactions
    reaction_ids = set()
    enzyme_by_reaction = {}
    for e in enzymes:
        for link in ReactionEnzyme.select(ReactionEnzyme.reaction).where(ReactionEnzyme.enzyme == e.id):
            rid = link.reaction_id
            reaction_ids.add(rid)
            if rid not in enzyme_by_reaction:
                enzyme_by_reaction[rid] = set()
            enzyme_by_reaction[rid].add(e.ec_number)

    print(f"   -> {len(reaction_ids)} réactions")

    # Count compound appearances
    compound_reactions = {}
    compound_role = {}

    for rid in reaction_ids:
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

    print(f"   -> {len(compound_reactions)} composés uniques")

    # Rank
    ranked = sorted(compound_reactions.items(), key=lambda x: len(x[1]), reverse=True)
    top10 = ranked[:10]

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "enzyme_count": len(enzyme_ids),
        "reaction_count": len(reaction_ids),
        "compound_count": len(compound_reactions),
        "compound_reactions": compound_reactions,
        "compound_role": compound_role,
        "enzyme_by_reaction": enzyme_by_reaction,
        "top10": top10,
    }


def print_top10(data):
    """Print top 10 table for a taxon."""
    print(f"\n{'Rang':<5} {'Composé':<30} {'ChEBI':<16} {'Rxns':<8} {'Enzymes':<8} {'Sub%':<6}")
    print("-" * 75)

    for rank, (chebi_id, rxn_ids) in enumerate(data["top10"], 1):
        comp = Compound.get_or_none(Compound.chebi_id == chebi_id)
        name = (comp.name[:28] if comp else "?")
        n_rxn = len(rxn_ids)
        roles = data["compound_role"][chebi_id]
        total_roles = roles["substrate"] + roles["product"]
        sub_pct = f"{roles['substrate']/total_roles*100:.0f}%" if total_roles else "?"

        # Count unique ECs
        all_ecs = set()
        for rid in rxn_ids:
            if rid in data["enzyme_by_reaction"]:
                all_ecs.update(data["enzyme_by_reaction"][rid])

        print(f"{rank:<5} {name:<30} {chebi_id:<16} {n_rxn:<8} {len(all_ecs):<8} {sub_pct:<6}")


# ==================================================================
# MAIN
# ==================================================================
print("=" * 80)
print("COMPARAISON DES COMPOSÉS CENTRAUX: Homo sapiens vs Mus musculus")
print("=" * 80)

print("\n[1/3] Analyse des deux taxons...")
human = analyze_taxon("9606")
mouse = analyze_taxon("10090")

# ==================================================================
# Print individual top 10s
# ==================================================================
print(f"\n{'=' * 80}")
print(f"TOP 10 - {human['tax_name']} ({human['enzyme_count']} enzymes, {human['reaction_count']} réactions)")
print(f"{'=' * 80}")
print_top10(human)

print(f"\n{'=' * 80}")
print(f"TOP 10 - {mouse['tax_name']} ({mouse['enzyme_count']} enzymes, {mouse['reaction_count']} réactions)")
print(f"{'=' * 80}")
print_top10(mouse)

# ==================================================================
# Compare
# ==================================================================
print(f"\n{'=' * 80}")
print("COMPARAISON")
print(f"{'=' * 80}")

human_top_ids = set(cid for cid, _ in human["top10"])
mouse_top_ids = set(cid for cid, _ in mouse["top10"])

intersection = human_top_ids & mouse_top_ids
only_human = human_top_ids - mouse_top_ids
only_mouse = mouse_top_ids - human_top_ids

# (i) Intersection
print(f"\n--- (i) INTERSECTION des top 10 ({len(intersection)} composés) ---")
print(f"{'Composé':<30} {'ChEBI':<16} {'Rxns H.sap':<12} {'Rxns M.mus':<12} {'Delta':<8}")
print("-" * 78)

for cid in sorted(intersection):
    comp = Compound.get_or_none(Compound.chebi_id == cid)
    name = comp.name[:28] if comp else "?"
    h_count = len(human["compound_reactions"].get(cid, set()))
    m_count = len(mouse["compound_reactions"].get(cid, set()))
    delta = h_count - m_count
    sign = "+" if delta > 0 else ""
    print(f"{name:<30} {cid:<16} {h_count:<12} {m_count:<12} {sign}{delta:<8}")

# (ii) Only human
print(f"\n--- (ii) UNIQUEMENT dans le top 10 de {human['tax_name']} ({len(only_human)}) ---")
if only_human:
    for cid in sorted(only_human):
        comp = Compound.get_or_none(Compound.chebi_id == cid)
        name = comp.name[:28] if comp else "?"
        h_count = len(human["compound_reactions"].get(cid, set()))
        # Where does it rank in mouse?
        m_count = len(mouse["compound_reactions"].get(cid, set()))
        # Find rank in mouse
        mouse_ranked = sorted(mouse["compound_reactions"].items(), key=lambda x: len(x[1]), reverse=True)
        m_rank = next((i+1 for i, (c, _) in enumerate(mouse_ranked) if c == cid), "absent")
        print(f"  {name:<28} {cid:<16} H.sap: {h_count} rxns | M.mus: {m_count} rxns (rang #{m_rank})")
else:
    print("  (aucun)")

# (iii) Only mouse
print(f"\n--- (iii) UNIQUEMENT dans le top 10 de {mouse['tax_name']} ({len(only_mouse)}) ---")
if only_mouse:
    for cid in sorted(only_mouse):
        comp = Compound.get_or_none(Compound.chebi_id == cid)
        name = comp.name[:28] if comp else "?"
        m_count = len(mouse["compound_reactions"].get(cid, set()))
        h_count = len(human["compound_reactions"].get(cid, set()))
        human_ranked = sorted(human["compound_reactions"].items(), key=lambda x: len(x[1]), reverse=True)
        h_rank = next((i+1 for i, (c, _) in enumerate(human_ranked) if c == cid), "absent")
        print(f"  {name:<28} {cid:<16} M.mus: {m_count} rxns | H.sap: {h_count} rxns (rang #{h_rank})")
else:
    print("  (aucun)")

# Global stats comparison
print(f"\n--- STATISTIQUES GLOBALES ---")
print(f"{'Métrique':<30} {'H. sapiens':<15} {'M. musculus':<15}")
print("-" * 60)
print(f"{'Enzymes':<30} {human['enzyme_count']:<15} {mouse['enzyme_count']:<15}")
print(f"{'Réactions':<30} {human['reaction_count']:<15} {mouse['reaction_count']:<15}")
print(f"{'Composés uniques':<30} {human['compound_count']:<15} {mouse['compound_count']:<15}")

# Overlap of all compounds
all_h = set(human["compound_reactions"].keys())
all_m = set(mouse["compound_reactions"].keys())
print(f"{'Composés partagés (tous)':<30} {len(all_h & all_m):<15}")
print(f"{'Composés uniques H. sapiens':<30} {len(all_h - all_m):<15}")
print(f"{'Composés uniques M. musculus':<30} {len(all_m - all_h):<15}")

print(f"\n{'=' * 80}")
print("DONE")
print(f"{'=' * 80}")
