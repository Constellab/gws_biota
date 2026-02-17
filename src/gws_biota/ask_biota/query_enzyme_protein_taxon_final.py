"""
Query enzymes with uniprot_id Q8I1I3 and taxon 7220
Build complete enzyme ↔ protein ↔ taxon table
"""

def init_gws_core():
    from gws_core_loader import load_gws_core
    load_gws_core()
    from gws_core.manage import AppManager
    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="INFO")

init_gws_core()

from gws_biota import Enzyme, Protein, Taxonomy
import csv

# Query parameters
uniprot_id = "Q8I1I3"
tax_id = "7220"

print(f"\n{'='*100}")
print(f"RÉSULTATS: ENZYME ↔ PROTEIN ↔ TAXON")
print(f"Critères: uniprot_id={uniprot_id}, tax_id={tax_id}")
print(f"{'='*100}")

# Get protein info
protein = Protein.get_or_none(Protein.uniprot_id == uniprot_id)
taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)

# Get all enzymes for this taxon
enzymes_for_taxon = list(Enzyme.select().where(Enzyme.tax_id == tax_id))

# Get all proteins for this taxon
proteins_for_taxon = list(Protein.select().where(Protein.tax_id == tax_id))

print(f"\n📋 RÉSUMÉ:")
print(f"   Protein Q8I1I3: {'✓ Trouvée' if protein else '✗ Non trouvée'}")
print(f"   Taxon 7220: {'✓ ' + taxonomy.name if taxonomy else '✗ Non trouvé'}")
print(f"   Enzymes pour taxon 7220: {len(enzymes_for_taxon)}")
print(f"   Proteins pour taxon 7220: {len(proteins_for_taxon)}")

# Table 1: Protein cible
print(f"\n{'='*100}")
print(f"TABLE 1: PROTEIN CIBLE (uniprot_id={uniprot_id})")
print(f"{'='*100}")

if protein:
    print(f"{'Champ':<25} {'Valeur':<75}")
    print("-" * 100)
    print(f"{'UniProt ID':<25} {protein.uniprot_id:<75}")
    print(f"{'Gene':<25} {protein.uniprot_gene:<75}")
    print(f"{'Tax ID':<25} {protein.tax_id:<75}")
    print(f"{'Taxon Name':<25} {taxonomy.name if taxonomy else 'N/A':<75}")
    print(f"{'Taxon Rank':<25} {taxonomy.rank if taxonomy else 'N/A':<75}")

# Table 2: Enzymes pour taxon 7220
print(f"\n{'='*100}")
print(f"TABLE 2: ENZYMES POUR TAXON {tax_id} ({taxonomy.name if taxonomy else 'N/A'})")
print(f"{'='*100}")

if enzymes_for_taxon:
    print(f"\n{'EC Number':<15} {'UniProt ID':<20} {'Name':<40} {'Tax Species':<20}")
    print("-" * 100)
    for e in enzymes_for_taxon:
        ec = e.ec_number or "N/A"
        uniprot = e.uniprot_id or "N/A"
        name = (e.name[:37] + "...") if e.name and len(e.name) > 40 else (e.name or "N/A")
        species = getattr(e, 'tax_species', 'N/A') or "N/A"
        print(f"{ec:<15} {uniprot:<20} {name:<40} {species:<20}")
else:
    print("Aucun enzyme trouvé.")

# Table 3: Relation enzyme ↔ protein ↔ taxon
print(f"\n{'='*100}")
print(f"TABLE 3: RELATION ENZYME ↔ PROTEIN ↔ TAXON (tax_id={tax_id})")
print(f"{'='*100}")

results = []

# Add enzymes with their potential protein matches
for enzyme in enzymes_for_taxon:
    matched_protein = None
    if enzyme.uniprot_id:
        matched_protein = Protein.get_or_none(Protein.uniprot_id == enzyme.uniprot_id)

    results.append({
        "type": "ENZYME",
        "enzyme_ec_number": enzyme.ec_number or "N/A",
        "enzyme_uniprot_id": enzyme.uniprot_id or "N/A",
        "protein_uniprot_id": matched_protein.uniprot_id if matched_protein else "N/A",
        "protein_gene": matched_protein.uniprot_gene if matched_protein else "N/A",
        "taxon_id": tax_id,
        "taxon_name": taxonomy.name if taxonomy else "N/A",
        "taxon_rank": taxonomy.rank if taxonomy else "N/A",
    })

# Add the target protein Q8I1I3 (even if no enzyme match)
results.append({
    "type": "PROTEIN",
    "enzyme_ec_number": "N/A (pas d'enzyme associé)",
    "enzyme_uniprot_id": "N/A",
    "protein_uniprot_id": protein.uniprot_id if protein else "N/A",
    "protein_gene": protein.uniprot_gene if protein else "N/A",
    "taxon_id": tax_id,
    "taxon_name": taxonomy.name if taxonomy else "N/A",
    "taxon_rank": taxonomy.rank if taxonomy else "N/A",
})

print(f"\n{'Type':<10} {'EC Number':<15} {'Enz. UniProt':<15} {'Prot. UniProt':<15} {'Gene':<15} {'Taxon ID':<10} {'Taxon Name':<20}")
print("-" * 100)
for r in results:
    print(f"{r['type']:<10} {r['enzyme_ec_number']:<15} {r['enzyme_uniprot_id']:<15} {r['protein_uniprot_id']:<15} {r['protein_gene']:<15} {r['taxon_id']:<10} {r['taxon_name']:<20}")

# Export to CSV
csv_file = "/lab/user/ask_biota/enzyme_protein_taxon_results.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)
print(f"\n✓ Résultats exportés vers: {csv_file}")

# Additional: Show all proteins for this taxon
print(f"\n{'='*100}")
print(f"TABLE 4: TOUTES LES PROTEINS POUR TAXON {tax_id} (20 premières)")
print(f"{'='*100}")
print(f"\n{'UniProt ID':<15} {'Gene':<25} {'Taxon ID':<10} {'Taxon Name':<30}")
print("-" * 80)
for p in proteins_for_taxon[:20]:
    print(f"{p.uniprot_id:<15} {p.uniprot_gene:<25} {p.tax_id:<10} {taxonomy.name if taxonomy else 'N/A':<30}")

print(f"\n{'='*100}")
print(f"FIN DU RAPPORT")
print(f"{'='*100}")
