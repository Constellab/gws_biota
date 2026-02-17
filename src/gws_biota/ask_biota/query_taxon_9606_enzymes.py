def init_gws_core():
    from gws_core_loader import load_gws_core
    load_gws_core()
    from gws_core.manage import AppManager
    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="INFO")


def query_enzymes_and_reactions():
    from gws_biota import Enzyme, Reaction
    from gws_biota.reaction.reaction import ReactionEnzyme

    print("=" * 80)
    print("Recherche des enzymes pour le taxon 9606 (Homo sapiens)")
    print("=" * 80)

    # Query enzymes for taxon 9606 (Homo sapiens)
    enzymes_query = Enzyme.select().where(Enzyme.tax_id == "9606")
    enzyme_count = enzymes_query.count()
    print(f"\nNombre total d'enzymes trouvées: {enzyme_count}")

    if enzyme_count == 0:
        print("Aucune enzyme trouvée pour ce taxon.")
        return

    # Get unique EC numbers
    enzymes_list = list(enzymes_query)
    ec_numbers = {}
    for enzyme in enzymes_list:
        ec = enzyme.ec_number
        if ec not in ec_numbers:
            ec_numbers[ec] = []
        ec_numbers[ec].append(enzyme)

    print(f"Nombre d'EC numbers uniques: {len(ec_numbers)}")

    # Find reactions linked to human taxon using full-text search
    print("\n" + "=" * 80)
    print("Recherche des réactions associées au taxon 9606")
    print("=" * 80)

    reactions_for_taxon = list(Reaction.search_by_tax_ids("9606"))
    print(f"\nNombre de réactions trouvées pour le taxon 9606: {len(reactions_for_taxon)}")

    # Create a dictionary mapping EC numbers to reactions
    ec_to_reactions = {}
    for reaction in reactions_for_taxon:
        # Get enzymes for this reaction
        reaction_enzymes = list(reaction.enzymes)
        for enzyme in reaction_enzymes:
            ec = enzyme.ec_number
            if ec not in ec_to_reactions:
                ec_to_reactions[ec] = []
            if reaction not in ec_to_reactions[ec]:
                ec_to_reactions[ec].append(reaction)

    print(f"Nombre d'EC numbers avec réactions: {len(ec_to_reactions)}")

    print("\n" + "=" * 80)
    print("Liste des enzymes humaines avec leurs réactions")
    print("=" * 80)

    # Display enzymes that have reactions
    enzymes_with_reactions = 0
    for ec_number in sorted(ec_numbers.keys()):
        enzymes = ec_numbers[ec_number]
        reactions = ec_to_reactions.get(ec_number, [])

        if reactions:
            enzymes_with_reactions += 1
            print(f"\n{'─' * 60}")
            print(f"EC Number: {ec_number}")
            print(f"Nombre d'entrées UniProt: {len(enzymes)}")

            uniprot_ids = [e.uniprot_id for e in enzymes[:5] if e.uniprot_id]
            if uniprot_ids:
                print(f"UniProt IDs (exemples): {', '.join(uniprot_ids)}")

            print(f"Réactions associées ({len(reactions)}):")
            for reaction in reactions[:10]:
                substrates = list(reaction.substrates)
                products = list(reaction.products)

                substrate_names = [s.name for s in substrates if s.name][:3]
                product_names = [p.name for p in products if p.name][:3]

                direction_symbol = "→" if reaction.direction == "LR" else "←" if reaction.direction == "RL" else "⇌"

                print(f"  • Rhea ID: {reaction.rhea_id}")
                print(f"    {' + '.join(substrate_names) if substrate_names else '?'} {direction_symbol} {' + '.join(product_names) if product_names else '?'}")
                if reaction.kegg_id:
                    print(f"    KEGG: {reaction.kegg_id}")

            if len(reactions) > 10:
                print(f"    ... et {len(reactions) - 10} autres réactions")

    print(f"\n{'=' * 80}")
    print(f"Résumé:")
    print(f"  - Enzymes totales pour taxon 9606: {enzyme_count}")
    print(f"  - EC numbers uniques: {len(ec_numbers)}")
    print(f"  - Réactions pour taxon 9606: {len(reactions_for_taxon)}")
    print(f"  - EC numbers avec réactions: {enzymes_with_reactions}")


init_gws_core()
query_enzymes_and_reactions()
print("\n" + "=" * 80)
print("Requête terminée avec succès")
