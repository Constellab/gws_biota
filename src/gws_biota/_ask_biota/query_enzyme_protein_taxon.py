"""
Query enzymes with uniprot_id Q8I1I3 and taxon 7220
Returns table enzyme ↔ protein ↔ taxon
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

print(f"\n=== Recherche enzymes avec uniprot_id={uniprot_id} et tax_id={tax_id} ===\n")

# Find enzymes matching both criteria
enzymes = Enzyme.select().where(
    (Enzyme.uniprot_id == uniprot_id) &
    (Enzyme.tax_id == tax_id)
)

enzyme_count = enzymes.count()
print(f"Nombre d'enzymes trouvées: {enzyme_count}\n")

# Prepare results table
results = []

for enzyme in enzymes:
    # Get associated protein
    protein = Protein.get_or_none(Protein.uniprot_id == enzyme.uniprot_id)

    # Get associated taxonomy
    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == enzyme.tax_id)

    result = {
        # Enzyme info
        "enzyme_ec_number": enzyme.ec_number,
        "enzyme_name": enzyme.name if hasattr(enzyme, 'name') else None,
        "enzyme_uniprot_id": enzyme.uniprot_id,
        "enzyme_tax_id": enzyme.tax_id,
        "enzyme_tax_species": enzyme.tax_species if hasattr(enzyme, 'tax_species') else None,

        # Protein info
        "protein_uniprot_id": protein.uniprot_id if protein else None,
        "protein_gene": protein.uniprot_gene if protein else None,
        "protein_tax_id": protein.tax_id if protein else None,

        # Taxonomy info
        "taxon_id": taxonomy.tax_id if taxonomy else None,
        "taxon_name": taxonomy.name if taxonomy else None,
        "taxon_rank": taxonomy.rank if taxonomy else None,
    }
    results.append(result)

# Display results as table
if results:
    print("=" * 120)
    print("TABLE: ENZYME ↔ PROTEIN ↔ TAXON")
    print("=" * 120)

    for i, r in enumerate(results, 1):
        print(f"\n--- Résultat {i} ---")
        print(f"ENZYME:")
        print(f"  EC Number:    {r['enzyme_ec_number']}")
        print(f"  Name:         {r['enzyme_name']}")
        print(f"  UniProt ID:   {r['enzyme_uniprot_id']}")
        print(f"  Tax ID:       {r['enzyme_tax_id']}")
        print(f"  Species:      {r['enzyme_tax_species']}")

        print(f"PROTEIN:")
        print(f"  UniProt ID:   {r['protein_uniprot_id']}")
        print(f"  Gene:         {r['protein_gene']}")
        print(f"  Tax ID:       {r['protein_tax_id']}")

        print(f"TAXON:")
        print(f"  Tax ID:       {r['taxon_id']}")
        print(f"  Name:         {r['taxon_name']}")
        print(f"  Rank:         {r['taxon_rank']}")

    print("\n" + "=" * 120)

    # Export to CSV
    import csv
    csv_file = "/lab/user/ask_biota/enzyme_protein_taxon_results.csv"

    fieldnames = list(results[0].keys())
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nRésultats exportés vers: {csv_file}")
else:
    print("Aucun enzyme trouvé avec ces critères.")

    # Try to find enzymes with just uniprot_id
    enzymes_by_uniprot = Enzyme.select().where(Enzyme.uniprot_id == uniprot_id)
    print(f"\nEnzymes avec uniprot_id={uniprot_id}: {enzymes_by_uniprot.count()}")

    # Try to find enzymes with just tax_id
    enzymes_by_tax = Enzyme.select().where(Enzyme.tax_id == tax_id).limit(5)
    print(f"Enzymes avec tax_id={tax_id} (premiers 5): {enzymes_by_tax.count()}")
