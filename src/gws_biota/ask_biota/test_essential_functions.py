"""Test the 10 essential missing functions (61-70)."""

import sys
import traceback
sys.path.insert(0, '/lab/user/ask_biota')

from mcp_biota_functions import (
    get_bto_by_id,
    search_bto_by_name,
    get_enzymes_by_tissue,
    get_go_by_id,
    search_go_by_name,
    get_pathways_by_species,
    get_enzymes_for_protein,
    get_compound_by_kegg_id,
    get_reaction_by_kegg_id,
    get_database_statistics,
)

passed = 0
failed = 0
errors = []

def run_test(num, name, func, *args, **kwargs):
    global passed, failed
    try:
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            print(f"  [{num}] {name}: OK")
            # Print key metrics
            for key in ["count", "enzyme_count", "pathway_count", "total_entities",
                        "total_relationships"]:
                if key in result:
                    print(f"       -> {key}: {result[key]}")
                    break
            # Show a sample value
            if "name" in result and "error" not in result:
                print(f"       -> name: {result['name']}")
            elif "tissues" in result and result["tissues"]:
                print(f"       -> first: {result['tissues'][0]}")
            elif "go_terms" in result and result["go_terms"]:
                print(f"       -> first: {result['go_terms'][0]}")
            elif "pathways" in result and result["pathways"]:
                print(f"       -> first: {result['pathways'][0]}")
            elif "enzymes" in result and result.get("enzymes"):
                print(f"       -> first: {result['enzymes'][0]}")
            elif "primary_entities" in result:
                for k, v in result["primary_entities"].items():
                    print(f"       -> {k}: {v}")
            elif "error" in result:
                print(f"       -> {result['error']}")
            passed += 1
        else:
            print(f"  [{num}] {name}: UNEXPECTED TYPE")
            failed += 1
    except Exception as e:
        print(f"  [{num}] {name}: FAILED - {e}")
        traceback.print_exc()
        failed += 1
        errors.append((num, name, str(e)))

print("=" * 70)
print("TEST DES 10 FONCTIONS ESSENTIELLES (61-70)")
print("=" * 70)

run_test(61, "get_bto_by_id('BTO_0000142')", get_bto_by_id, "BTO_0000142")
run_test(62, "search_bto_by_name('liver')", search_bto_by_name, "liver")
run_test(63, "get_enzymes_by_tissue('BTO_0000142')", get_enzymes_by_tissue, "BTO_0000142", limit=10)
run_test(64, "get_go_by_id('GO:0008150')", get_go_by_id, "GO:0008150")
run_test(65, "search_go_by_name('kinase', 'molecular_function')", search_go_by_name, "kinase", "molecular_function")
run_test(66, "get_pathways_by_species('Homo sapiens')", get_pathways_by_species, "Homo sapiens", limit=10)
run_test(67, "get_enzymes_for_protein('P54802')", get_enzymes_for_protein, "P54802")
run_test(68, "get_compound_by_kegg_id('C00001')", get_compound_by_kegg_id, "C00001")
run_test(69, "get_reaction_by_kegg_id('R00001')", get_reaction_by_kegg_id, "R00001")
run_test(70, "get_database_statistics()", get_database_statistics)

print(f"\n{'=' * 70}")
print(f"RESULTATS: {passed} PASSED, {failed} FAILED sur 10")
if errors:
    print("\nERREURS:")
    for num, name, err in errors:
        print(f"  [{num}] {name}: {err}")
print("=" * 70)
