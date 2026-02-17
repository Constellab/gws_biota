"""
Test complet des 30 fonctions MCP Biota
=======================================
"""

import sys
import json
sys.path.insert(0, '/lab/user/ask_biota')

from mcp_biota_functions import (
    # Enzyme (6)
    get_enzyme_by_ec_number,
    get_enzymes_by_taxon,
    get_enzymes_by_uniprot_id,
    search_enzymes_by_name,
    get_enzymes_by_taxonomy_rank,
    get_enzyme_tissue_sources,
    # Protein (5)
    get_protein_by_uniprot_id,
    get_proteins_by_taxon,
    get_proteins_by_gene_name,
    get_proteins_by_evidence_score,
    count_proteins_by_taxon,
    # Compound (5)
    get_compound_by_chebi_id,
    get_compound_by_inchikey,
    search_compounds_by_name,
    get_compounds_by_formula,
    get_compounds_by_mass_range,
    # Reaction (5)
    get_reaction_by_rhea_id,
    get_reactions_by_ec_number,
    get_reactions_by_taxon,
    get_reaction_substrates_products,
    search_reactions_by_compound,
    # Taxonomy (4)
    get_taxonomy_by_id,
    search_taxonomy_by_name,
    get_taxonomy_ancestors,
    get_taxonomy_children,
    # Pathway (3)
    get_pathway_by_reactome_id,
    get_pathway_compounds,
    search_pathways_by_name,
    # Cross-entity (2)
    get_enzyme_protein_taxon_table,
    get_metabolic_network_for_taxon,
)


def print_result(name: str, result: dict, max_items: int = 3):
    """Pretty print a test result."""
    print(f"\n{'─'*70}")
    print(f"✓ {name}")
    print(f"{'─'*70}")

    if "error" in result:
        print(f"  ⚠ Error: {result['error']}")
        return False

    # Print key metrics
    for key in ["count", "total_count", "returned_count"]:
        if key in result:
            print(f"  {key}: {result[key]}")

    # Print main data (limited)
    for key, value in result.items():
        if key in ["count", "total_count", "returned_count", "filters", "statistics"]:
            continue
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
            for item in value[:max_items]:
                if isinstance(item, dict):
                    summary = ", ".join(f"{k}={v}" for k, v in list(item.items())[:4])
                    print(f"    - {summary}")
                else:
                    print(f"    - {item}")
            if len(value) > max_items:
                print(f"    ... et {len(value) - max_items} de plus")
        elif isinstance(value, dict):
            print(f"  {key}: {json.dumps(value, default=str)[:100]}...")
        else:
            val_str = str(value)
            if len(val_str) > 80:
                val_str = val_str[:80] + "..."
            print(f"  {key}: {val_str}")

    return True


def run_tests():
    """Run all 30 function tests."""

    results = {"passed": 0, "failed": 0, "errors": []}

    print("=" * 70)
    print("TEST COMPLET DES 30 FONCTIONS MCP BIOTA")
    print("=" * 70)

    # =========================================================================
    # ENZYME FUNCTIONS (1-6)
    # =========================================================================
    print("\n" + "=" * 70)
    print("ENZYME FUNCTIONS (1-6)")
    print("=" * 70)

    # 1. get_enzyme_by_ec_number
    try:
        result = get_enzyme_by_ec_number("1.1.1.1")
        if print_result("1. get_enzyme_by_ec_number('1.1.1.1')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 1. get_enzyme_by_ec_number - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzyme_by_ec_number", str(e)))

    # 2. get_enzymes_by_taxon
    try:
        result = get_enzymes_by_taxon("9606", limit=5)
        if print_result("2. get_enzymes_by_taxon('9606', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 2. get_enzymes_by_taxon - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzymes_by_taxon", str(e)))

    # 3. get_enzymes_by_uniprot_id
    try:
        result = get_enzymes_by_uniprot_id("P00352")
        if print_result("3. get_enzymes_by_uniprot_id('P00352')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 3. get_enzymes_by_uniprot_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzymes_by_uniprot_id", str(e)))

    # 4. search_enzymes_by_name
    try:
        result = search_enzymes_by_name("dehydrogenase", limit=5)
        if print_result("4. search_enzymes_by_name('dehydrogenase', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 4. search_enzymes_by_name - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("search_enzymes_by_name", str(e)))

    # 5. get_enzymes_by_taxonomy_rank
    try:
        result = get_enzymes_by_taxonomy_rank("genus", "Saccharomyces", limit=5)
        if print_result("5. get_enzymes_by_taxonomy_rank('genus', 'Saccharomyces', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 5. get_enzymes_by_taxonomy_rank - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzymes_by_taxonomy_rank", str(e)))

    # 6. get_enzyme_tissue_sources
    try:
        result = get_enzyme_tissue_sources("1.1.1.1")
        if print_result("6. get_enzyme_tissue_sources('1.1.1.1')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 6. get_enzyme_tissue_sources - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzyme_tissue_sources", str(e)))

    # =========================================================================
    # PROTEIN FUNCTIONS (7-11)
    # =========================================================================
    print("\n" + "=" * 70)
    print("PROTEIN FUNCTIONS (7-11)")
    print("=" * 70)

    # 7. get_protein_by_uniprot_id
    try:
        result = get_protein_by_uniprot_id("P00352")
        if print_result("7. get_protein_by_uniprot_id('P00352')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 7. get_protein_by_uniprot_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_protein_by_uniprot_id", str(e)))

    # 8. get_proteins_by_taxon
    try:
        result = get_proteins_by_taxon("9606", limit=5)
        if print_result("8. get_proteins_by_taxon('9606', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 8. get_proteins_by_taxon - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_proteins_by_taxon", str(e)))

    # 9. get_proteins_by_gene_name
    try:
        result = get_proteins_by_gene_name("ALDH", limit=5)
        if print_result("9. get_proteins_by_gene_name('ALDH', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 9. get_proteins_by_gene_name - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_proteins_by_gene_name", str(e)))

    # 10. get_proteins_by_evidence_score
    try:
        result = get_proteins_by_evidence_score(1, tax_id="9606")
        if print_result("10. get_proteins_by_evidence_score(1, tax_id='9606')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 10. get_proteins_by_evidence_score - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_proteins_by_evidence_score", str(e)))

    # 11. count_proteins_by_taxon
    try:
        result = count_proteins_by_taxon("9606")
        if print_result("11. count_proteins_by_taxon('9606')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 11. count_proteins_by_taxon - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("count_proteins_by_taxon", str(e)))

    # =========================================================================
    # COMPOUND FUNCTIONS (12-16)
    # =========================================================================
    print("\n" + "=" * 70)
    print("COMPOUND FUNCTIONS (12-16)")
    print("=" * 70)

    # 12. get_compound_by_chebi_id
    try:
        result = get_compound_by_chebi_id("CHEBI:15377")  # water
        if print_result("12. get_compound_by_chebi_id('CHEBI:15377')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 12. get_compound_by_chebi_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_compound_by_chebi_id", str(e)))

    # 13. get_compound_by_inchikey
    try:
        result = get_compound_by_inchikey("XLYOFNOQVPJJNP-UHFFFAOYSA-N")  # water
        if print_result("13. get_compound_by_inchikey('XLYOFNOQVPJJNP-UHFFFAOYSA-N')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 13. get_compound_by_inchikey - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_compound_by_inchikey", str(e)))

    # 14. search_compounds_by_name
    try:
        result = search_compounds_by_name("glucose", limit=5)
        if print_result("14. search_compounds_by_name('glucose', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 14. search_compounds_by_name - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("search_compounds_by_name", str(e)))

    # 15. get_compounds_by_formula
    try:
        result = get_compounds_by_formula("C6H12O6")
        if print_result("15. get_compounds_by_formula('C6H12O6')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 15. get_compounds_by_formula - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_compounds_by_formula", str(e)))

    # 16. get_compounds_by_mass_range
    try:
        result = get_compounds_by_mass_range(180.0, 182.0, limit=5)
        if print_result("16. get_compounds_by_mass_range(180.0, 182.0, limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 16. get_compounds_by_mass_range - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_compounds_by_mass_range", str(e)))

    # =========================================================================
    # REACTION FUNCTIONS (17-21)
    # =========================================================================
    print("\n" + "=" * 70)
    print("REACTION FUNCTIONS (17-21)")
    print("=" * 70)

    # 17. get_reaction_by_rhea_id
    try:
        result = get_reaction_by_rhea_id("RHEA:10000")
        if print_result("17. get_reaction_by_rhea_id('RHEA:10000')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 17. get_reaction_by_rhea_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_reaction_by_rhea_id", str(e)))

    # 18. get_reactions_by_ec_number
    try:
        result = get_reactions_by_ec_number("1.1.1.1", limit=5)
        if print_result("18. get_reactions_by_ec_number('1.1.1.1', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 18. get_reactions_by_ec_number - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_reactions_by_ec_number", str(e)))

    # 19. get_reactions_by_taxon
    try:
        result = get_reactions_by_taxon("9606", limit=5)
        if print_result("19. get_reactions_by_taxon('9606', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 19. get_reactions_by_taxon - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_reactions_by_taxon", str(e)))

    # 20. get_reaction_substrates_products
    try:
        result = get_reaction_substrates_products("RHEA:10000")
        if print_result("20. get_reaction_substrates_products('RHEA:10000')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 20. get_reaction_substrates_products - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_reaction_substrates_products", str(e)))

    # 21. search_reactions_by_compound
    try:
        result = search_reactions_by_compound("CHEBI:15377", role="both")  # water
        if print_result("21. search_reactions_by_compound('CHEBI:15377', role='both')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 21. search_reactions_by_compound - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("search_reactions_by_compound", str(e)))

    # =========================================================================
    # TAXONOMY FUNCTIONS (22-25)
    # =========================================================================
    print("\n" + "=" * 70)
    print("TAXONOMY FUNCTIONS (22-25)")
    print("=" * 70)

    # 22. get_taxonomy_by_id
    try:
        result = get_taxonomy_by_id("9606")
        if print_result("22. get_taxonomy_by_id('9606')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 22. get_taxonomy_by_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_taxonomy_by_id", str(e)))

    # 23. search_taxonomy_by_name
    try:
        result = search_taxonomy_by_name("Escherichia", limit=5)
        if print_result("23. search_taxonomy_by_name('Escherichia', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 23. search_taxonomy_by_name - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("search_taxonomy_by_name", str(e)))

    # 24. get_taxonomy_ancestors
    try:
        result = get_taxonomy_ancestors("9606")
        if print_result("24. get_taxonomy_ancestors('9606')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 24. get_taxonomy_ancestors - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_taxonomy_ancestors", str(e)))

    # 25. get_taxonomy_children
    try:
        result = get_taxonomy_children("9605", limit=5)  # Homo genus
        if print_result("25. get_taxonomy_children('9605', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 25. get_taxonomy_children - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_taxonomy_children", str(e)))

    # =========================================================================
    # PATHWAY FUNCTIONS (26-28)
    # =========================================================================
    print("\n" + "=" * 70)
    print("PATHWAY FUNCTIONS (26-28)")
    print("=" * 70)

    # 26. get_pathway_by_reactome_id
    try:
        result = get_pathway_by_reactome_id("R-HSA-109582")
        if print_result("26. get_pathway_by_reactome_id('R-HSA-109582')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 26. get_pathway_by_reactome_id - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_pathway_by_reactome_id", str(e)))

    # 27. get_pathway_compounds
    try:
        result = get_pathway_compounds("R-HSA-109582")
        if print_result("27. get_pathway_compounds('R-HSA-109582')", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 27. get_pathway_compounds - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_pathway_compounds", str(e)))

    # 28. search_pathways_by_name
    try:
        result = search_pathways_by_name("glycolysis", limit=5)
        if print_result("28. search_pathways_by_name('glycolysis', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 28. search_pathways_by_name - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("search_pathways_by_name", str(e)))

    # =========================================================================
    # CROSS-ENTITY FUNCTIONS (29-30)
    # =========================================================================
    print("\n" + "=" * 70)
    print("CROSS-ENTITY FUNCTIONS (29-30)")
    print("=" * 70)

    # 29. get_enzyme_protein_taxon_table
    try:
        result = get_enzyme_protein_taxon_table(tax_id="9606", limit=5)
        if print_result("29. get_enzyme_protein_taxon_table(tax_id='9606', limit=5)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 29. get_enzyme_protein_taxon_table - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_enzyme_protein_taxon_table", str(e)))

    # 30. get_metabolic_network_for_taxon
    try:
        result = get_metabolic_network_for_taxon("562", limit=10)  # E. coli
        if print_result("30. get_metabolic_network_for_taxon('562', limit=10)", result):
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"\n✗ 30. get_metabolic_network_for_taxon - ERROR: {e}")
        results["failed"] += 1
        results["errors"].append(("get_metabolic_network_for_taxon", str(e)))

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)
    print(f"\n✓ Passés:  {results['passed']}/30")
    print(f"✗ Échoués: {results['failed']}/30")

    if results["errors"]:
        print("\nErreurs détaillées:")
        for func_name, error in results["errors"]:
            print(f"  - {func_name}: {error}")

    print("\n" + "=" * 70)

    return results


if __name__ == "__main__":
    run_tests()
