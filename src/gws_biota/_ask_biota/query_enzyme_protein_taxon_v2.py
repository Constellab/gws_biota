"""
Query enzymes with uniprot_id Q8I1I3 and taxon 7220
Explore data more thoroughly
"""

def init_gws_core():
    from gws_core_loader import load_gws_core
    load_gws_core()
    from gws_core.manage import AppManager
    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="INFO")

init_gws_core()

from gws_biota import Enzyme, Protein, Taxonomy

# Query parameters
uniprot_id = "Q8I1I3"
tax_id = "7220"

print(f"\n{'='*80}")
print(f"EXPLORATION DES DONNÉES BIOTA")
print(f"{'='*80}")

# 1. Check if protein exists
print(f"\n1. RECHERCHE PROTEIN avec uniprot_id={uniprot_id}")
protein = Protein.get_or_none(Protein.uniprot_id == uniprot_id)
if protein:
    print(f"   ✓ Protein trouvée:")
    print(f"     UniProt ID: {protein.uniprot_id}")
    print(f"     Gene: {protein.uniprot_gene}")
    print(f"     Tax ID: {protein.tax_id}")
else:
    print(f"   ✗ Aucune protein avec uniprot_id={uniprot_id}")

# 2. Check taxonomy
print(f"\n2. RECHERCHE TAXONOMY avec tax_id={tax_id}")
taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
if taxonomy:
    print(f"   ✓ Taxonomy trouvée:")
    print(f"     Tax ID: {taxonomy.tax_id}")
    print(f"     Name: {taxonomy.name}")
    print(f"     Rank: {taxonomy.rank}")
else:
    print(f"   ✗ Aucun taxon avec tax_id={tax_id}")

# 3. List all enzymes for tax_id 7220
print(f"\n3. TOUS LES ENZYMES avec tax_id={tax_id}")
enzymes_tax = list(Enzyme.select().where(Enzyme.tax_id == tax_id))
print(f"   Nombre d'enzymes: {len(enzymes_tax)}")
for e in enzymes_tax:
    print(f"   - EC: {e.ec_number}, UniProt: {e.uniprot_id}, Species: {getattr(e, 'tax_species', 'N/A')}")

# 4. Search for enzymes with similar uniprot_id pattern
print(f"\n4. RECHERCHE ENZYMES avec uniprot_id LIKE 'Q8I%'")
enzymes_like = list(Enzyme.select().where(Enzyme.uniprot_id.startswith('Q8I')).limit(10))
print(f"   Nombre trouvé (max 10): {len(enzymes_like)}")
for e in enzymes_like:
    print(f"   - EC: {e.ec_number}, UniProt: {e.uniprot_id}, Tax ID: {e.tax_id}")

# 5. Search proteins with similar pattern
print(f"\n5. RECHERCHE PROTEINS avec uniprot_id LIKE 'Q8I%'")
proteins_like = list(Protein.select().where(Protein.uniprot_id.startswith('Q8I')).limit(10))
print(f"   Nombre trouvé (max 10): {len(proteins_like)}")
for p in proteins_like:
    print(f"   - UniProt: {p.uniprot_id}, Gene: {p.uniprot_gene}, Tax ID: {p.tax_id}")

# 6. Get proteins for taxon 7220
print(f"\n6. RECHERCHE PROTEINS avec tax_id={tax_id}")
proteins_tax = list(Protein.select().where(Protein.tax_id == tax_id).limit(20))
print(f"   Nombre trouvé (max 20): {len(proteins_tax)}")
for p in proteins_tax:
    print(f"   - UniProt: {p.uniprot_id}, Gene: {p.uniprot_gene}")

# 7. Build enzyme ↔ protein ↔ taxon table for tax_id 7220
print(f"\n{'='*80}")
print(f"TABLE: ENZYME ↔ PROTEIN ↔ TAXON pour tax_id={tax_id}")
print(f"{'='*80}")

results = []
for enzyme in enzymes_tax:
    protein = Protein.get_or_none(Protein.uniprot_id == enzyme.uniprot_id)
    result = {
        "enzyme_ec": enzyme.ec_number,
        "enzyme_uniprot": enzyme.uniprot_id,
        "protein_uniprot": protein.uniprot_id if protein else "N/A",
        "protein_gene": protein.uniprot_gene if protein else "N/A",
        "taxon_id": tax_id,
        "taxon_name": taxonomy.name if taxonomy else "N/A",
        "taxon_rank": taxonomy.rank if taxonomy else "N/A",
    }
    results.append(result)

if results:
    # Print as formatted table
    print(f"\n{'EC Number':<15} {'Enzyme UniProt':<15} {'Protein UniProt':<15} {'Gene':<15} {'Taxon ID':<10} {'Taxon Name':<30}")
    print("-" * 100)
    for r in results:
        print(f"{r['enzyme_ec']:<15} {r['enzyme_uniprot']:<15} {r['protein_uniprot']:<15} {r['protein_gene']:<15} {r['taxon_id']:<10} {r['taxon_name']:<30}")

    # Export to CSV
    import csv
    csv_file = "/lab/user/ask_biota/enzyme_protein_taxon_7220.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nRésultats exportés vers: {csv_file}")
else:
    print("Aucun résultat trouvé.")
