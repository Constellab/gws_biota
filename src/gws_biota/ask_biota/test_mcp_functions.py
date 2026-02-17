"""Quick test of MCP Biota functions."""

import sys
sys.path.insert(0, '/lab/user/ask_biota')

from mcp_biota_functions import (
    get_taxonomy_by_id,
    get_protein_by_uniprot_id,
    search_compounds_by_name,
    get_enzyme_protein_taxon_table
)

print("=" * 60)
print("TEST RAPIDE DES FONCTIONS MCP BIOTA")
print("=" * 60)

# Test 1
print("\n1. get_taxonomy_by_id('9606') - Homo sapiens:")
result = get_taxonomy_by_id("9606")
print(f"   Résultat: {result}")

# Test 2
print("\n2. get_protein_by_uniprot_id('Q8I1I3'):")
result = get_protein_by_uniprot_id("Q8I1I3")
print(f"   Résultat: {result}")

# Test 3
print("\n3. search_compounds_by_name('water', limit=3):")
result = search_compounds_by_name("water", limit=3)
print(f"   Count: {result['count']}")
if result['compounds']:
    for c in result['compounds'][:3]:
        print(f"   - {c.get('chebi_id')}: {c.get('name')}")

# Test 4
print("\n4. get_enzyme_protein_taxon_table(tax_id='7220', limit=5):")
result = get_enzyme_protein_taxon_table(tax_id="7220", limit=5)
print(f"   Count: {result['count']}")
for row in result['table'][:3]:
    print(f"   - EC: {row['enzyme_ec_number']}, Taxon: {row['taxon_name']}")

print("\n" + "=" * 60)
print("TESTS OK!")
print("=" * 60)
