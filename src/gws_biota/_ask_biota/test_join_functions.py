"""Test all 30 JOIN functions in mcp_biota_functions.py."""

import sys
import traceback
sys.path.insert(0, '/lab/user/ask_biota')

from mcp_biota_functions import (
    # Enzyme-centric joins (31-38)
    join_enzyme_reactions_compounds,
    join_enzyme_protein_taxonomy,
    join_enzyme_bto_ancestors,
    join_enzyme_reactions_by_taxon,
    join_enzyme_class_hierarchy,
    join_enzyme_deprecated_to_reactions,
    join_enzyme_ortholog_pathway,
    join_enzyme_all_tissues_by_taxon,
    # Reaction-centric joins (39-46)
    join_reaction_full_detail,
    join_reaction_enzymes_by_taxon,
    join_reaction_shared_compounds,
    join_reactions_between_two_compounds,
    join_reaction_taxonomy_distribution,
    join_reaction_cross_references,
    join_reaction_mass_balance,
    join_reactions_by_enzyme_pair,
    # Compound-centric joins (47-52)
    join_compound_reactions_enzymes,
    join_compound_pathway_species,
    join_compound_ancestors_tree,
    join_compound_common_reactions,
    join_compound_producing_enzymes_by_taxon,
    join_compound_consuming_enzymes_by_taxon,
    # Taxonomy/Pathway/Ontology joins (53-60)
    join_taxonomy_enzymes_proteins_count,
    join_taxonomy_children_enzyme_stats,
    join_taxonomy_reactions_compounds,
    join_pathway_reactions_enzymes,
    join_pathway_ancestor_compounds,
    join_go_ancestors_tree,
    join_organism_full_profile,
    join_compare_two_taxa_enzymes,
)

passed = 0
failed = 0
errors = []

def run_test(num, name, func, *args, **kwargs):
    global passed, failed
    try:
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            has_error = "error" in result and not any(k for k in result if k != "error" and k != "count")
            status = "OK" if not has_error else f"OK (no data: {result.get('error', '')})"
            print(f"  [{num:2d}] {name}: {status}")
            # Print a summary key
            for key in ["count", "reaction_count", "enzyme_count", "tissue_count",
                        "shared_count", "ancestor_count", "ortholog_count",
                        "compound_count", "pathway_count", "children_count",
                        "total_enzymes", "unique_tissue_count", "taxon_count",
                        "producing_enzyme_count", "consuming_enzyme_count",
                        "protein_count", "shared_ec_count", "mapping_count",
                        "class_count", "unique_compound_count"]:
                if key in result:
                    print(f"       -> {key}: {result[key]}")
                    break
            passed += 1
        else:
            print(f"  [{num:2d}] {name}: UNEXPECTED TYPE {type(result)}")
            failed += 1
    except Exception as e:
        print(f"  [{num:2d}] {name}: FAILED - {e}")
        traceback.print_exc()
        failed += 1
        errors.append((num, name, str(e)))

print("=" * 70)
print("TEST DES 30 FONCTIONS DE JOINTURE")
print("=" * 70)

# === ENZYME-CENTRIC ===
print("\n--- ENZYME-CENTRIC (31-38) ---")
run_test(31, "join_enzyme_reactions_compounds('1.1.1.1')", join_enzyme_reactions_compounds, "1.1.1.1")
run_test(32, "join_enzyme_protein_taxonomy('3.2.1.51')", join_enzyme_protein_taxonomy, "3.2.1.51")
run_test(33, "join_enzyme_bto_ancestors('1.1.1.1')", join_enzyme_bto_ancestors, "1.1.1.1")
run_test(34, "join_enzyme_reactions_by_taxon('9606')", join_enzyme_reactions_by_taxon, "9606", limit=10)
run_test(35, "join_enzyme_class_hierarchy('1.1')", join_enzyme_class_hierarchy, "1.1")
run_test(36, "join_enzyme_deprecated_to_reactions('1.1.1.5')", join_enzyme_deprecated_to_reactions, "1.1.1.5")
run_test(37, "join_enzyme_ortholog_pathway('1.1.1.1')", join_enzyme_ortholog_pathway, "1.1.1.1")
run_test(38, "join_enzyme_all_tissues_by_taxon('9606')", join_enzyme_all_tissues_by_taxon, "9606", limit=10)

# === REACTION-CENTRIC ===
print("\n--- REACTION-CENTRIC (39-46) ---")
run_test(39, "join_reaction_full_detail('RHEA:10000')", join_reaction_full_detail, "RHEA:10000")
run_test(40, "join_reaction_enzymes_by_taxon('RHEA:10000')", join_reaction_enzymes_by_taxon, "RHEA:10000")
run_test(41, "join_reaction_shared_compounds('RHEA:10000','RHEA:10004')", join_reaction_shared_compounds, "RHEA:10000", "RHEA:10004")
run_test(42, "join_reactions_between_two_compounds('CHEBI:15377','CHEBI:15378')", join_reactions_between_two_compounds, "CHEBI:15377", "CHEBI:15378")
run_test(43, "join_reaction_taxonomy_distribution('RHEA:10000')", join_reaction_taxonomy_distribution, "RHEA:10000")
run_test(44, "join_reaction_cross_references('RHEA:10000')", join_reaction_cross_references, "RHEA:10000")
run_test(45, "join_reaction_mass_balance('RHEA:10000')", join_reaction_mass_balance, "RHEA:10000")
run_test(46, "join_reactions_by_enzyme_pair('1.1.1.1','1.1.1.2')", join_reactions_by_enzyme_pair, "1.1.1.1", "1.1.1.2")

# === COMPOUND-CENTRIC ===
print("\n--- COMPOUND-CENTRIC (47-52) ---")
run_test(47, "join_compound_reactions_enzymes('CHEBI:15377')", join_compound_reactions_enzymes, "CHEBI:15377")
run_test(48, "join_compound_pathway_species('CHEBI:15377')", join_compound_pathway_species, "CHEBI:15377")
run_test(49, "join_compound_ancestors_tree('CHEBI:15377')", join_compound_ancestors_tree, "CHEBI:15377")
run_test(50, "join_compound_common_reactions('CHEBI:15377','CHEBI:15378')", join_compound_common_reactions, "CHEBI:15377", "CHEBI:15378")
run_test(51, "join_compound_producing_enzymes('CHEBI:15377')", join_compound_producing_enzymes_by_taxon, "CHEBI:15377")
run_test(52, "join_compound_consuming_enzymes('CHEBI:15377')", join_compound_consuming_enzymes_by_taxon, "CHEBI:15377")

# === TAXONOMY/PATHWAY/ONTOLOGY ===
print("\n--- TAXONOMY/PATHWAY/ONTOLOGY (53-60) ---")
run_test(53, "join_taxonomy_enzymes_proteins_count('9606')", join_taxonomy_enzymes_proteins_count, "9606")
run_test(54, "join_taxonomy_children_enzyme_stats('9605')", join_taxonomy_children_enzyme_stats, "9605")
run_test(55, "join_taxonomy_reactions_compounds('9606')", join_taxonomy_reactions_compounds, "9606", limit=10)
run_test(56, "join_pathway_reactions_enzymes('R-HSA-109582')", join_pathway_reactions_enzymes, "R-HSA-109582")
run_test(57, "join_pathway_ancestor_compounds('R-HSA-109582')", join_pathway_ancestor_compounds, "R-HSA-109582")
run_test(58, "join_go_ancestors_tree('GO:0008150')", join_go_ancestors_tree, "GO:0008150")
run_test(59, "join_organism_full_profile('9606')", join_organism_full_profile, "9606", limit=10)
run_test(60, "join_compare_two_taxa_enzymes('9606','10090')", join_compare_two_taxa_enzymes, "9606", "10090")

print("\n" + "=" * 70)
print(f"RESULTATS: {passed} PASSED, {failed} FAILED sur 30")
if errors:
    print("\nERREURS:")
    for num, name, err in errors:
        print(f"  [{num}] {name}: {err}")
print("=" * 70)
