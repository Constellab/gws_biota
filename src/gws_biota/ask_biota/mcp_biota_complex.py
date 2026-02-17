"""
MCP Biota Complex Query Functions
==================================

Complex multi-table join, cross-entity, and hierarchical traversal functions
for the Biota database. These functions combine data from 2-5 tables.

Categories:
- Cross-entity functions (2 functions)
- Enzyme-centric joins (8 functions)
- Reaction-centric joins (8 functions)
- Compound-centric joins (6 functions)
- Taxonomy/Pathway/Ontology joins (8 functions)
- Multi-table lookups (4 functions)
"""

from typing import Optional, List, Dict, Any, Union

from mcp_biota_simple import _ensure_initialized, _entity_to_dict, _entities_to_list


# ============================================================================
# MULTI-TABLE LOOKUP FUNCTIONS (6, 20-21, 24, 27, 63, 67)
# ============================================================================

@_ensure_initialized
def get_enzyme_tissue_sources(ec_number: str) -> Dict[str, Any]:
    """
    6. Récupère les tissus (BTO) où l'enzyme est exprimé.

    Args:
        ec_number: Numéro EC de l'enzyme

    Returns:
        Dict avec la liste des tissus/organes
    """
    from gws_biota import Enzyme, BTO
    from gws_biota.enzyme.enzyme import EnzymeBTO

    # Get enzymes with this EC number
    enzymes = list(Enzyme.select().where(Enzyme.ec_number == ec_number))

    if not enzymes:
        return {"error": f"No enzyme found with EC number {ec_number}"}

    # Get BTO associations
    tissues = []
    for enzyme in enzymes:
        enzyme_btos = EnzymeBTO.select().where(EnzymeBTO.enzyme == enzyme)
        for eb in enzyme_btos:
            bto = eb.bto
            if bto:
                tissues.append({
                    "bto_id": bto.bto_id,
                    "name": bto.name,
                    "enzyme_uniprot_id": enzyme.uniprot_id
                })

    return {
        "ec_number": ec_number,
        "enzyme_count": len(enzymes),
        "tissue_count": len(tissues),
        "tissues": tissues
    }


@_ensure_initialized
def get_reaction_substrates_products(rhea_id: str) -> Dict[str, Any]:
    """
    20. Substrats et produits d'une réaction.

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec les substrats et produits détaillés
    """
    from gws_biota import Reaction

    # Normalize Rhea ID
    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)

    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    substrates = []
    for s in reaction.substrates:
        substrates.append({
            "chebi_id": s.chebi_id,
            "name": s.name,
            "formula": s.formula,
            "mass": s.mass
        })

    products = []
    for p in reaction.products:
        products.append({
            "chebi_id": p.chebi_id,
            "name": p.name,
            "formula": p.formula,
            "mass": p.mass
        })

    return {
        "rhea_id": rhea_id,
        "reaction_name": reaction.name,
        "direction": reaction.direction,
        "substrate_count": len(substrates),
        "product_count": len(products),
        "substrates": substrates,
        "products": products
    }


@_ensure_initialized
def search_reactions_by_compound(chebi_id: str, role: str = "both") -> Dict[str, Any]:
    """
    21. Réactions impliquant un composé.

    Args:
        chebi_id: ChEBI identifier
        role: "substrate", "product", ou "both"

    Returns:
        Dict avec la liste des réactions
    """
    from gws_biota import Reaction, Compound
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct

    # Normalize ChEBI ID
    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    reactions_as_substrate = []
    reactions_as_product = []

    if role in ["substrate", "both"]:
        substrate_links = ReactionSubstrate.select().where(
            ReactionSubstrate.compound == compound
        )
        for link in substrate_links:
            r = link.reaction
            reactions_as_substrate.append({
                "rhea_id": r.rhea_id,
                "name": r.name,
                "direction": r.direction
            })

    if role in ["product", "both"]:
        product_links = ReactionProduct.select().where(
            ReactionProduct.compound == compound
        )
        for link in product_links:
            r = link.reaction
            reactions_as_product.append({
                "rhea_id": r.rhea_id,
                "name": r.name,
                "direction": r.direction
            })

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "role_filter": role,
        "as_substrate_count": len(reactions_as_substrate),
        "as_product_count": len(reactions_as_product),
        "reactions_as_substrate": reactions_as_substrate,
        "reactions_as_product": reactions_as_product
    }


@_ensure_initialized
def get_taxonomy_ancestors(tax_id: str) -> Dict[str, Any]:
    """
    24. Récupère la lignée taxonomique (ancêtres).

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        Dict avec la lignée complète
    """
    from gws_biota import Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)

    if not taxonomy:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    lineage = []
    current = taxonomy

    # Build lineage by following ancestor_tax_id
    visited = set()
    while current and current.tax_id not in visited:
        visited.add(current.tax_id)
        lineage.append({
            "tax_id": current.tax_id,
            "name": current.name,
            "rank": current.rank
        })

        if current.ancestor_tax_id:
            current = Taxonomy.get_or_none(Taxonomy.tax_id == current.ancestor_tax_id)
        else:
            break

    return {
        "tax_id": tax_id,
        "name": taxonomy.name,
        "lineage_length": len(lineage),
        "lineage": lineage
    }


@_ensure_initialized
def get_pathway_compounds(reactome_id: str) -> Dict[str, Any]:
    """
    27. Composés impliqués dans un pathway.

    Args:
        reactome_id: Reactome pathway identifier

    Returns:
        Dict avec la liste des composés
    """
    from gws_biota import Pathway, PathwayCompound, Compound

    pathway = Pathway.get_or_none(Pathway.reactome_pathway_id == reactome_id)

    if not pathway:
        return {"error": f"No pathway found with Reactome ID {reactome_id}"}

    # Get pathway compounds
    pathway_compounds = list(PathwayCompound.select().where(
        PathwayCompound.reactome_pathway_id == reactome_id
    ))

    compounds = []
    for pc in pathway_compounds:
        compound = Compound.get_or_none(Compound.chebi_id == pc.chebi_id)
        if compound:
            compounds.append({
                "chebi_id": compound.chebi_id,
                "name": compound.name,
                "formula": compound.formula,
                "species": pc.species
            })

    return {
        "reactome_id": reactome_id,
        "pathway_name": pathway.name,
        "compound_count": len(compounds),
        "compounds": compounds
    }


@_ensure_initialized
def get_enzymes_by_tissue(bto_id: str, tax_id: str = None, limit: int = 100) -> Dict[str, Any]:
    """
    63. Récupère tous les enzymes exprimés dans un tissu donné (reverse lookup).

    Args:
        bto_id: BTO identifier du tissu
        tax_id: Optionnel - filtrer par taxon
        limit: Nombre maximum de résultats

    Returns:
        Dict avec les enzymes exprimés dans ce tissu
    """
    from gws_biota import Enzyme, BTO
    from gws_biota.enzyme.enzyme import EnzymeBTO

    bto = BTO.get_or_none(BTO.bto_id == bto_id)
    if not bto:
        return {"error": f"No BTO term found with ID {bto_id}"}

    ebto_links = list(EnzymeBTO.select().where(EnzymeBTO.bto == bto).limit(limit * 2))

    enzymes_data = []
    seen = set()
    for link in ebto_links:
        enzyme = link.enzyme
        if not enzyme:
            continue

        key = f"{enzyme.ec_number}_{enzyme.uniprot_id}"
        if key in seen:
            continue

        if tax_id and enzyme.tax_id != tax_id:
            continue

        seen.add(key)
        enzymes_data.append({
            "ec_number": enzyme.ec_number,
            "name": enzyme.name,
            "uniprot_id": enzyme.uniprot_id,
            "tax_id": enzyme.tax_id
        })

        if len(enzymes_data) >= limit:
            break

    return {
        "bto_id": bto_id,
        "tissue_name": bto.name,
        "tax_filter": tax_id,
        "enzyme_count": len(enzymes_data),
        "enzymes": enzymes_data
    }


@_ensure_initialized
def get_enzymes_for_protein(uniprot_id: str) -> Dict[str, Any]:
    """
    67. Récupère les enzymes associés à une protéine (reverse lookup Protein → Enzymes).

    Args:
        uniprot_id: UniProt identifier de la protéine

    Returns:
        Dict avec les enzymes partageant cet UniProt ID
    """
    from gws_biota import Enzyme, Protein, Taxonomy

    protein = Protein.get_or_none(Protein.uniprot_id == uniprot_id)
    if not protein:
        return {"error": f"No protein found with UniProt ID {uniprot_id}", "count": 0}

    # Find enzymes with this uniprot_id
    enzymes = list(Enzyme.select().where(Enzyme.uniprot_id == uniprot_id))

    enzymes_data = []
    for e in enzymes:
        tax_name = None
        if e.tax_id:
            tax = Taxonomy.get_or_none(Taxonomy.tax_id == e.tax_id)
            tax_name = tax.name if tax else None

        enzymes_data.append({
            "ec_number": e.ec_number,
            "name": e.name,
            "tax_id": e.tax_id,
            "tax_name": tax_name
        })

    return {
        "uniprot_id": uniprot_id,
        "protein_gene": protein.uniprot_gene,
        "protein_tax_id": protein.tax_id,
        "enzyme_count": len(enzymes_data),
        "enzymes": enzymes_data
    }


# ============================================================================
# CROSS-ENTITY FUNCTIONS (29-30)
# ============================================================================

@_ensure_initialized
def get_enzyme_protein_taxon_table(
    tax_id: str = None,
    uniprot_id: str = None,
    ec_number: str = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    29. Table enzyme ↔ protein ↔ taxon.

    Args:
        tax_id: Optionnel - filtrer par taxon
        uniprot_id: Optionnel - filtrer par UniProt ID
        ec_number: Optionnel - filtrer par EC number
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la table de relations
    """
    from gws_biota import Enzyme, Protein, Taxonomy

    # Build query
    query = Enzyme.select()

    if tax_id:
        query = query.where(Enzyme.tax_id == tax_id)
    if uniprot_id:
        query = query.where(Enzyme.uniprot_id == uniprot_id)
    if ec_number:
        query = query.where(Enzyme.ec_number == ec_number)

    enzymes = list(query.limit(limit))

    # Build result table
    results = []
    for enzyme in enzymes:
        # Get protein
        protein = None
        if enzyme.uniprot_id:
            protein = Protein.get_or_none(Protein.uniprot_id == enzyme.uniprot_id)

        # Get taxonomy
        taxonomy = None
        if enzyme.tax_id:
            taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == enzyme.tax_id)

        results.append({
            "enzyme_ec_number": enzyme.ec_number,
            "enzyme_name": enzyme.name,
            "enzyme_uniprot_id": enzyme.uniprot_id,
            "protein_uniprot_id": protein.uniprot_id if protein else None,
            "protein_gene": protein.uniprot_gene if protein else None,
            "protein_evidence_score": protein.evidence_score if protein else None,
            "taxon_id": enzyme.tax_id,
            "taxon_name": taxonomy.name if taxonomy else None,
            "taxon_rank": taxonomy.rank if taxonomy else None
        })

    return {
        "filters": {
            "tax_id": tax_id,
            "uniprot_id": uniprot_id,
            "ec_number": ec_number
        },
        "count": len(results),
        "table": results
    }


@_ensure_initialized
def get_metabolic_network_for_taxon(tax_id: str, limit: int = 500) -> Dict[str, Any]:
    """
    30. Réseau métabolique complet (enzymes + réactions + composés) pour un taxon.

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum de réactions

    Returns:
        Dict avec le réseau métabolique complet
    """
    from gws_biota import Enzyme, Reaction, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    # Get reactions for this taxon
    reactions = list(Reaction.search_by_tax_ids(tax_id))[:limit]

    # Collect unique enzymes, compounds
    enzymes_set = {}
    compounds_set = {}
    reaction_list = []

    for reaction in reactions:
        # Add reaction
        reaction_data = {
            "rhea_id": reaction.rhea_id,
            "name": reaction.name,
            "direction": reaction.direction,
            "substrates": [],
            "products": [],
            "enzymes": []
        }

        # Add substrates
        for s in reaction.substrates:
            reaction_data["substrates"].append(s.chebi_id)
            if s.chebi_id not in compounds_set:
                compounds_set[s.chebi_id] = {
                    "chebi_id": s.chebi_id,
                    "name": s.name,
                    "formula": s.formula
                }

        # Add products
        for p in reaction.products:
            reaction_data["products"].append(p.chebi_id)
            if p.chebi_id not in compounds_set:
                compounds_set[p.chebi_id] = {
                    "chebi_id": p.chebi_id,
                    "name": p.name,
                    "formula": p.formula
                }

        # Add enzymes
        for e in reaction.enzymes:
            reaction_data["enzymes"].append(e.ec_number)
            if e.ec_number not in enzymes_set:
                enzymes_set[e.ec_number] = {
                    "ec_number": e.ec_number,
                    "name": e.name
                }

        reaction_list.append(reaction_data)

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "statistics": {
            "reaction_count": len(reaction_list),
            "enzyme_count": len(enzymes_set),
            "compound_count": len(compounds_set)
        },
        "enzymes": list(enzymes_set.values()),
        "compounds": list(compounds_set.values()),
        "reactions": reaction_list
    }


# ============================================================================
# JOIN FUNCTIONS - ENZYME-CENTRIC (31-38)
# ============================================================================

@_ensure_initialized
def join_enzyme_reactions_compounds(ec_number: str, limit: int = 50) -> Dict[str, Any]:
    """
    31. Enzyme → Reactions → Substrats/Produits (3 tables).

    Args:
        ec_number: Numéro EC de l'enzyme
        limit: Nombre maximum de réactions

    Returns:
        Dict avec les réactions et leurs composés pour cet enzyme
    """
    from gws_biota import Enzyme, Reaction, Compound
    from gws_biota.reaction.reaction import ReactionEnzyme

    enzymes = list(Enzyme.select().where(Enzyme.ec_number == ec_number).limit(10))
    if not enzymes:
        return {"error": f"No enzyme found with EC number {ec_number}"}

    reactions_data = []
    seen_rhea = set()

    for enzyme in enzymes:
        re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.enzyme == enzyme).limit(limit))
        for link in re_links:
            reaction = link.reaction
            if reaction.rhea_id in seen_rhea:
                continue
            seen_rhea.add(reaction.rhea_id)

            substrates = [{"chebi_id": s.chebi_id, "name": s.name, "formula": s.formula}
                          for s in reaction.substrates]
            products = [{"chebi_id": p.chebi_id, "name": p.name, "formula": p.formula}
                        for p in reaction.products]

            reactions_data.append({
                "rhea_id": reaction.rhea_id,
                "reaction_name": reaction.name,
                "direction": reaction.direction,
                "substrates": substrates,
                "products": products
            })

    return {
        "ec_number": ec_number,
        "enzyme_count": len(enzymes),
        "reaction_count": len(reactions_data),
        "reactions": reactions_data
    }


@_ensure_initialized
def join_enzyme_protein_taxonomy(ec_number: str, limit: int = 100) -> Dict[str, Any]:
    """
    32. Enzyme → Protein → Taxonomy avec lignée complète (3 tables).

    Args:
        ec_number: Numéro EC
        limit: Nombre maximum de résultats

    Returns:
        Dict avec enzymes, protéines associées et lignée taxonomique
    """
    from gws_biota import Enzyme, Protein, Taxonomy

    enzymes = list(Enzyme.select().where(Enzyme.ec_number == ec_number).limit(limit))
    if not enzymes:
        return {"error": f"No enzyme found with EC number {ec_number}"}

    results = []
    for enzyme in enzymes:
        protein = None
        if enzyme.uniprot_id:
            protein = Protein.get_or_none(Protein.uniprot_id == enzyme.uniprot_id)

        taxonomy = None
        lineage = []
        if enzyme.tax_id:
            taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == enzyme.tax_id)
            if taxonomy:
                current = taxonomy
                visited = set()
                while current and current.tax_id not in visited:
                    visited.add(current.tax_id)
                    lineage.append({"tax_id": current.tax_id, "name": current.name, "rank": current.rank})
                    if current.ancestor_tax_id:
                        current = Taxonomy.get_or_none(Taxonomy.tax_id == current.ancestor_tax_id)
                    else:
                        break

        results.append({
            "enzyme_ec": enzyme.ec_number,
            "enzyme_uniprot_id": enzyme.uniprot_id,
            "enzyme_name": enzyme.name,
            "protein_gene": protein.uniprot_gene if protein else None,
            "protein_evidence": protein.evidence_score if protein else None,
            "taxon_id": enzyme.tax_id,
            "taxon_name": taxonomy.name if taxonomy else None,
            "lineage": lineage
        })

    return {
        "ec_number": ec_number,
        "count": len(results),
        "entries": results
    }


@_ensure_initialized
def join_enzyme_bto_ancestors(ec_number: str, limit: int = 50) -> Dict[str, Any]:
    """
    33. Enzyme → BTO tissus → BTO ancêtres (3 tables).

    Args:
        ec_number: Numéro EC
        limit: Nombre maximum de tissus

    Returns:
        Dict avec tissus et leur hiérarchie ontologique
    """
    from gws_biota import Enzyme, BTO
    from gws_biota.enzyme.enzyme import EnzymeBTO
    from gws_biota.bto.bto import BTOAncestor

    enzymes = list(Enzyme.select().where(Enzyme.ec_number == ec_number).limit(10))
    if not enzymes:
        return {"error": f"No enzyme found with EC number {ec_number}"}

    tissues_data = []
    for enzyme in enzymes:
        ebto_links = list(EnzymeBTO.select().where(EnzymeBTO.enzyme == enzyme).limit(limit))
        for link in ebto_links:
            bto = link.bto
            if not bto:
                continue

            ancestors = []
            bto_ancestors = list(BTOAncestor.select().where(BTOAncestor.bto == bto).limit(20))
            for ba in bto_ancestors:
                anc = ba.ancestor
                if anc:
                    ancestors.append({"bto_id": anc.bto_id, "name": anc.name})

            tissues_data.append({
                "bto_id": bto.bto_id,
                "tissue_name": bto.name,
                "enzyme_uniprot_id": enzyme.uniprot_id,
                "ancestor_count": len(ancestors),
                "ancestors": ancestors
            })

    return {
        "ec_number": ec_number,
        "tissue_count": len(tissues_data),
        "tissues": tissues_data
    }


@_ensure_initialized
def join_enzyme_reactions_by_taxon(tax_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    34. Taxon → Enzymes → Réactions (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum d'enzymes

    Returns:
        Dict avec les enzymes du taxon et leurs réactions
    """
    from gws_biota import Enzyme, Reaction, Taxonomy
    from gws_biota.reaction.reaction import ReactionEnzyme

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    enzymes = list(Enzyme.select().where(Enzyme.tax_id == tax_id).limit(limit))

    enzyme_reactions = []
    for enzyme in enzymes:
        re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.enzyme == enzyme).limit(20))
        reactions = []
        for link in re_links:
            r = link.reaction
            reactions.append({
                "rhea_id": r.rhea_id,
                "name": r.name,
                "direction": r.direction
            })

        if reactions:
            enzyme_reactions.append({
                "ec_number": enzyme.ec_number,
                "enzyme_name": enzyme.name,
                "uniprot_id": enzyme.uniprot_id,
                "reaction_count": len(reactions),
                "reactions": reactions
            })

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "enzyme_count": len(enzyme_reactions),
        "total_reactions": sum(e["reaction_count"] for e in enzyme_reactions),
        "enzymes": enzyme_reactions
    }


@_ensure_initialized
def join_enzyme_class_hierarchy(ec_prefix: str) -> Dict[str, Any]:
    """
    35. EnzymeClass → Enzymes associés (2 tables).

    Args:
        ec_prefix: Préfixe EC (ex: "1.1" pour toutes les oxydoréductases alcohol)

    Returns:
        Dict avec la hiérarchie des classes et les enzymes
    """
    from gws_biota import Enzyme, EnzymeClass

    # Find matching enzyme classes
    classes = list(EnzymeClass.select().where(
        EnzymeClass.ec_number.startswith(ec_prefix)
    ).limit(50))

    results = []
    for ec_class in classes:
        enzymes = list(Enzyme.select().where(
            Enzyme.ec_number.startswith(ec_class.ec_number)
        ).limit(20))

        results.append({
            "class_ec": ec_class.ec_number,
            "class_name": ec_class.name,
            "enzyme_count": len(enzymes),
            "enzymes": [{"ec_number": e.ec_number, "name": e.name, "uniprot_id": e.uniprot_id}
                        for e in enzymes[:10]]
        })

    return {
        "ec_prefix": ec_prefix,
        "class_count": len(results),
        "classes": results
    }


@_ensure_initialized
def join_enzyme_deprecated_to_reactions(old_ec_number: str) -> Dict[str, Any]:
    """
    36. DeprecatedEnzyme → Nouvel EC → Réactions (3 tables).

    Args:
        old_ec_number: Ancien numéro EC (déprécié)

    Returns:
        Dict avec le mapping ancien→nouveau EC et les réactions du nouveau
    """
    from gws_biota import Enzyme, Reaction, DeprecatedEnzyme
    from gws_biota.reaction.reaction import ReactionEnzyme

    deprecated = list(DeprecatedEnzyme.select().where(
        DeprecatedEnzyme.ec_number == old_ec_number
    ))

    if not deprecated:
        return {"error": f"No deprecated enzyme found with EC {old_ec_number}"}

    results = []
    for dep in deprecated:
        new_enzymes = list(Enzyme.select().where(Enzyme.ec_number == dep.new_ec_number).limit(20))

        reactions = []
        for enzyme in new_enzymes:
            re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.enzyme == enzyme).limit(10))
            for link in re_links:
                r = link.reaction
                reactions.append({
                    "rhea_id": r.rhea_id,
                    "name": r.name,
                    "direction": r.direction
                })

        results.append({
            "old_ec": dep.ec_number,
            "new_ec": dep.new_ec_number,
            "new_enzyme_count": len(new_enzymes),
            "reaction_count": len(reactions),
            "reactions": reactions
        })

    return {
        "old_ec_number": old_ec_number,
        "mapping_count": len(results),
        "mappings": results
    }


@_ensure_initialized
def join_enzyme_ortholog_pathway(ec_number: str) -> Dict[str, Any]:
    """
    37. EnzymeOrtholog → EnzymePathway (2 tables).

    Args:
        ec_number: Numéro EC

    Returns:
        Dict avec les orthologues et leurs pathways
    """
    from gws_biota import EnzymeOrtholog, EnzymePathway

    orthologs = list(EnzymeOrtholog.select().where(
        EnzymeOrtholog.ec_number == ec_number
    ))

    if not orthologs:
        return {"error": f"No ortholog found with EC {ec_number}", "count": 0}

    results = []
    for orth in orthologs:
        pathway_info = None
        if orth.pathway:
            pw = orth.pathway
            pathway_info = {"ec_number": pw.ec_number, "name": pw.name}

        results.append({
            "ortholog_ec": orth.ec_number,
            "ortholog_name": orth.name,
            "pathway": pathway_info
        })

    return {
        "ec_number": ec_number,
        "ortholog_count": len(results),
        "orthologs": results
    }


@_ensure_initialized
def join_enzyme_all_tissues_by_taxon(tax_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    38. Taxon → Enzymes → BTO tissus (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum d'enzymes

    Returns:
        Dict avec tous les tissus exprimant les enzymes du taxon
    """
    from gws_biota import Enzyme, BTO, Taxonomy
    from gws_biota.enzyme.enzyme import EnzymeBTO

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    enzymes = list(Enzyme.select().where(Enzyme.tax_id == tax_id).limit(limit))

    tissue_map = {}
    for enzyme in enzymes:
        ebto_links = list(EnzymeBTO.select().where(EnzymeBTO.enzyme == enzyme).limit(20))
        for link in ebto_links:
            bto = link.bto
            if bto and bto.bto_id:
                if bto.bto_id not in tissue_map:
                    tissue_map[bto.bto_id] = {
                        "bto_id": bto.bto_id,
                        "name": bto.name,
                        "enzyme_ec_numbers": []
                    }
                tissue_map[bto.bto_id]["enzyme_ec_numbers"].append(enzyme.ec_number)

    tissues = list(tissue_map.values())
    for t in tissues:
        t["enzyme_count"] = len(t["enzyme_ec_numbers"])

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "enzyme_count": len(enzymes),
        "unique_tissue_count": len(tissues),
        "tissues": tissues
    }


# ============================================================================
# JOIN FUNCTIONS - REACTION-CENTRIC (39-46)
# ============================================================================

@_ensure_initialized
def join_reaction_full_detail(rhea_id: str) -> Dict[str, Any]:
    """
    39. Réaction complète: Substrats + Produits + Enzymes + Taxonomie (5 tables).

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec détails complets de la réaction
    """
    from gws_biota import Reaction, Enzyme, Taxonomy
    from gws_biota.reaction.reaction import ReactionEnzyme

    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)
    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    substrates = [{"chebi_id": s.chebi_id, "name": s.name, "formula": s.formula, "mass": s.mass}
                  for s in reaction.substrates]
    products = [{"chebi_id": p.chebi_id, "name": p.name, "formula": p.formula, "mass": p.mass}
                for p in reaction.products]

    enzymes_data = []
    re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
    for link in re_links:
        enzyme = link.enzyme
        tax_info = None
        if enzyme.tax_id:
            tax = Taxonomy.get_or_none(Taxonomy.tax_id == enzyme.tax_id)
            if tax:
                tax_info = {"tax_id": tax.tax_id, "name": tax.name, "rank": tax.rank}

        enzymes_data.append({
            "ec_number": enzyme.ec_number,
            "name": enzyme.name,
            "uniprot_id": enzyme.uniprot_id,
            "taxonomy": tax_info
        })

    return {
        "rhea_id": rhea_id,
        "reaction_name": reaction.name,
        "direction": reaction.direction,
        "kegg_id": reaction.kegg_id,
        "metacyc_id": reaction.metacyc_id,
        "substrates": substrates,
        "products": products,
        "enzyme_count": len(enzymes_data),
        "enzymes": enzymes_data
    }


@_ensure_initialized
def join_reaction_enzymes_by_taxon(rhea_id: str) -> Dict[str, Any]:
    """
    40. Réaction → Enzymes groupés par taxon (3 tables).

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec les enzymes groupés par organisme
    """
    from gws_biota import Reaction, Enzyme, Taxonomy
    from gws_biota.reaction.reaction import ReactionEnzyme

    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)
    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    taxon_groups = {}
    re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
    for link in re_links:
        enzyme = link.enzyme
        tax_id = enzyme.tax_id or "unknown"

        if tax_id not in taxon_groups:
            tax = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id) if tax_id != "unknown" else None
            taxon_groups[tax_id] = {
                "tax_id": tax_id,
                "tax_name": tax.name if tax else "Unknown",
                "enzymes": []
            }

        taxon_groups[tax_id]["enzymes"].append({
            "ec_number": enzyme.ec_number,
            "uniprot_id": enzyme.uniprot_id,
            "name": enzyme.name
        })

    groups = list(taxon_groups.values())
    for g in groups:
        g["enzyme_count"] = len(g["enzymes"])

    return {
        "rhea_id": rhea_id,
        "reaction_name": reaction.name,
        "taxon_count": len(groups),
        "total_enzymes": sum(g["enzyme_count"] for g in groups),
        "taxon_groups": groups
    }


@_ensure_initialized
def join_reaction_shared_compounds(rhea_id_1: str, rhea_id_2: str) -> Dict[str, Any]:
    """
    41. Composés partagés entre deux réactions (3 tables).

    Args:
        rhea_id_1: Premier Rhea ID
        rhea_id_2: Deuxième Rhea ID

    Returns:
        Dict avec les composés en commun
    """
    from gws_biota import Reaction
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct

    if not rhea_id_1.startswith("RHEA:"):
        rhea_id_1 = f"RHEA:{rhea_id_1}"
    if not rhea_id_2.startswith("RHEA:"):
        rhea_id_2 = f"RHEA:{rhea_id_2}"

    r1 = Reaction.get_or_none(Reaction.rhea_id == rhea_id_1)
    r2 = Reaction.get_or_none(Reaction.rhea_id == rhea_id_2)

    if not r1 or not r2:
        return {"error": "One or both reactions not found"}

    def get_compounds(reaction):
        compounds = set()
        for s in reaction.substrates:
            compounds.add(s.chebi_id)
        for p in reaction.products:
            compounds.add(p.chebi_id)
        return compounds

    c1 = get_compounds(r1)
    c2 = get_compounds(r2)
    shared = c1 & c2

    from gws_biota import Compound
    shared_details = []
    for chebi_id in shared:
        comp = Compound.get_or_none(Compound.chebi_id == chebi_id)
        if comp:
            shared_details.append({"chebi_id": chebi_id, "name": comp.name, "formula": comp.formula})

    return {
        "reaction_1": rhea_id_1,
        "reaction_2": rhea_id_2,
        "compounds_r1": len(c1),
        "compounds_r2": len(c2),
        "shared_count": len(shared),
        "shared_compounds": shared_details
    }


@_ensure_initialized
def join_reactions_between_two_compounds(chebi_substrate: str, chebi_product: str) -> Dict[str, Any]:
    """
    42. Réactions convertissant un substrat en produit (3 tables).

    Args:
        chebi_substrate: ChEBI ID du substrat
        chebi_product: ChEBI ID du produit

    Returns:
        Dict avec les réactions reliant les deux composés
    """
    from gws_biota import Reaction, Compound
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct

    if not chebi_substrate.startswith("CHEBI:"):
        chebi_substrate = f"CHEBI:{chebi_substrate}"
    if not chebi_product.startswith("CHEBI:"):
        chebi_product = f"CHEBI:{chebi_product}"

    sub_comp = Compound.get_or_none(Compound.chebi_id == chebi_substrate)
    prod_comp = Compound.get_or_none(Compound.chebi_id == chebi_product)

    if not sub_comp or not prod_comp:
        return {"error": "One or both compounds not found"}

    # Get reactions where chebi_substrate is a substrate
    sub_reactions = set()
    for link in ReactionSubstrate.select().where(ReactionSubstrate.compound == sub_comp):
        sub_reactions.add(link.reaction_id)

    # Get reactions where chebi_product is a product
    prod_reactions = set()
    for link in ReactionProduct.select().where(ReactionProduct.compound == prod_comp):
        prod_reactions.add(link.reaction_id)

    # Intersection
    common_ids = sub_reactions & prod_reactions
    reactions = []
    for rid in common_ids:
        r = Reaction.get_or_none(Reaction.id == rid)
        if r:
            reactions.append({
                "rhea_id": r.rhea_id,
                "name": r.name,
                "direction": r.direction,
                "kegg_id": r.kegg_id
            })

    return {
        "substrate": {"chebi_id": chebi_substrate, "name": sub_comp.name},
        "product": {"chebi_id": chebi_product, "name": prod_comp.name},
        "reaction_count": len(reactions),
        "reactions": reactions
    }


@_ensure_initialized
def join_reaction_taxonomy_distribution(rhea_id: str) -> Dict[str, Any]:
    """
    43. Distribution taxonomique d'une réaction (3 tables).

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec la distribution par rang taxonomique
    """
    from gws_biota import Reaction, Enzyme, Taxonomy
    from gws_biota.reaction.reaction import ReactionEnzyme

    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)
    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    rank_distribution = {}
    species_list = []

    re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
    for link in re_links:
        enzyme = link.enzyme
        if enzyme.tax_id:
            tax = Taxonomy.get_or_none(Taxonomy.tax_id == enzyme.tax_id)
            if tax:
                rank = tax.rank or "unknown"
                rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
                if rank == "species":
                    species_list.append({"tax_id": tax.tax_id, "name": tax.name})

    return {
        "rhea_id": rhea_id,
        "reaction_name": reaction.name,
        "total_enzymes": len(re_links),
        "rank_distribution": rank_distribution,
        "species_count": len(species_list),
        "species": species_list[:50]
    }


@_ensure_initialized
def join_reaction_cross_references(rhea_id: str) -> Dict[str, Any]:
    """
    44. Références croisées complètes d'une réaction + enzymes + composés (4 tables).

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec toutes les références croisées
    """
    from gws_biota import Reaction
    from gws_biota.reaction.reaction import ReactionEnzyme

    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)
    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    # Cross references
    xrefs = {
        "rhea_id": reaction.rhea_id,
        "master_id": reaction.master_id,
        "kegg_id": reaction.kegg_id,
        "metacyc_id": reaction.metacyc_id,
        "biocyc_ids": reaction.biocyc_ids,
        "sabio_rk_id": reaction.sabio_rk_id,
    }

    # Compound cross-refs
    compound_xrefs = []
    for s in reaction.substrates:
        compound_xrefs.append({
            "chebi_id": s.chebi_id, "kegg_id": s.kegg_id,
            "inchikey": s.inchikey, "role": "substrate"
        })
    for p in reaction.products:
        compound_xrefs.append({
            "chebi_id": p.chebi_id, "kegg_id": p.kegg_id,
            "inchikey": p.inchikey, "role": "product"
        })

    # Enzyme cross-refs
    enzyme_xrefs = []
    re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
    for link in re_links:
        e = link.enzyme
        enzyme_xrefs.append({"ec_number": e.ec_number, "uniprot_id": e.uniprot_id})

    return {
        "reaction_xrefs": xrefs,
        "compound_xrefs": compound_xrefs,
        "enzyme_xrefs": enzyme_xrefs
    }


@_ensure_initialized
def join_reaction_mass_balance(rhea_id: str) -> Dict[str, Any]:
    """
    45. Bilan de masse d'une réaction: substrats vs produits (2 tables).

    Args:
        rhea_id: Rhea identifier

    Returns:
        Dict avec les masses des substrats et produits
    """
    from gws_biota import Reaction

    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)
    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    substrates = []
    total_sub_mass = 0.0
    for s in reaction.substrates:
        mass = s.mass or 0.0
        total_sub_mass += mass
        substrates.append({"chebi_id": s.chebi_id, "name": s.name, "formula": s.formula, "mass": mass})

    products = []
    total_prod_mass = 0.0
    for p in reaction.products:
        mass = p.mass or 0.0
        total_prod_mass += mass
        products.append({"chebi_id": p.chebi_id, "name": p.name, "formula": p.formula, "mass": mass})

    return {
        "rhea_id": rhea_id,
        "reaction_name": reaction.name,
        "substrates": substrates,
        "products": products,
        "total_substrate_mass": round(total_sub_mass, 4),
        "total_product_mass": round(total_prod_mass, 4),
        "mass_difference": round(total_prod_mass - total_sub_mass, 4)
    }


@_ensure_initialized
def join_reactions_by_enzyme_pair(ec_number_1: str, ec_number_2: str) -> Dict[str, Any]:
    """
    46. Réactions catalysées par les deux EC (3 tables).

    Args:
        ec_number_1: Premier numéro EC
        ec_number_2: Deuxième numéro EC

    Returns:
        Dict avec les réactions partagées
    """
    from gws_biota import Enzyme, Reaction
    from gws_biota.reaction.reaction import ReactionEnzyme

    enzymes_1 = list(Enzyme.select().where(Enzyme.ec_number == ec_number_1))
    enzymes_2 = list(Enzyme.select().where(Enzyme.ec_number == ec_number_2))

    if not enzymes_1 or not enzymes_2:
        return {"error": "One or both EC numbers not found"}

    reactions_1 = set()
    for e in enzymes_1:
        for link in ReactionEnzyme.select().where(ReactionEnzyme.enzyme == e):
            reactions_1.add(link.reaction_id)

    reactions_2 = set()
    for e in enzymes_2:
        for link in ReactionEnzyme.select().where(ReactionEnzyme.enzyme == e):
            reactions_2.add(link.reaction_id)

    shared_ids = reactions_1 & reactions_2
    only_1 = reactions_1 - reactions_2
    only_2 = reactions_2 - reactions_1

    shared_reactions = []
    for rid in shared_ids:
        r = Reaction.get_or_none(Reaction.id == rid)
        if r:
            shared_reactions.append({"rhea_id": r.rhea_id, "name": r.name, "direction": r.direction})

    return {
        "ec_number_1": ec_number_1,
        "ec_number_2": ec_number_2,
        "reactions_ec1_only": len(only_1),
        "reactions_ec2_only": len(only_2),
        "shared_count": len(shared_reactions),
        "shared_reactions": shared_reactions
    }


# ============================================================================
# JOIN FUNCTIONS - COMPOUND-CENTRIC (47-52)
# ============================================================================

@_ensure_initialized
def join_compound_reactions_enzymes(chebi_id: str) -> Dict[str, Any]:
    """
    47. Composé → Réactions (substrat/produit) → Enzymes (4 tables).

    Args:
        chebi_id: ChEBI identifier

    Returns:
        Dict avec les réactions et enzymes associés au composé
    """
    from gws_biota import Compound, Reaction
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct, ReactionEnzyme

    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    reactions_data = []
    seen_rhea = set()

    # As substrate
    for link in ReactionSubstrate.select().where(ReactionSubstrate.compound == compound):
        r = link.reaction
        if r.rhea_id not in seen_rhea:
            seen_rhea.add(r.rhea_id)
            enzymes = []
            for re_link in ReactionEnzyme.select().where(ReactionEnzyme.reaction == r):
                e = re_link.enzyme
                enzymes.append({"ec_number": e.ec_number, "name": e.name})
            reactions_data.append({
                "rhea_id": r.rhea_id, "name": r.name, "role": "substrate",
                "enzyme_count": len(enzymes), "enzymes": enzymes
            })

    # As product
    for link in ReactionProduct.select().where(ReactionProduct.compound == compound):
        r = link.reaction
        if r.rhea_id not in seen_rhea:
            seen_rhea.add(r.rhea_id)
            enzymes = []
            for re_link in ReactionEnzyme.select().where(ReactionEnzyme.reaction == r):
                e = re_link.enzyme
                enzymes.append({"ec_number": e.ec_number, "name": e.name})
            reactions_data.append({
                "rhea_id": r.rhea_id, "name": r.name, "role": "product",
                "enzyme_count": len(enzymes), "enzymes": enzymes
            })

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "reaction_count": len(reactions_data),
        "reactions": reactions_data
    }


@_ensure_initialized
def join_compound_pathway_species(chebi_id: str) -> Dict[str, Any]:
    """
    48. Composé → Pathways → Espèces (3 tables).

    Args:
        chebi_id: ChEBI identifier

    Returns:
        Dict avec les pathways et espèces associés au composé
    """
    from gws_biota import Compound, Pathway, PathwayCompound

    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    pc_links = list(PathwayCompound.select().where(PathwayCompound.chebi_id == chebi_id))

    pathway_species = {}
    for pc in pc_links:
        pw = Pathway.get_or_none(Pathway.reactome_pathway_id == pc.reactome_pathway_id)
        pw_name = pw.name if pw else "Unknown"
        key = pc.reactome_pathway_id

        if key not in pathway_species:
            pathway_species[key] = {
                "reactome_id": pc.reactome_pathway_id,
                "pathway_name": pw_name,
                "species": []
            }
        if pc.species and pc.species not in pathway_species[key]["species"]:
            pathway_species[key]["species"].append(pc.species)

    pathways = list(pathway_species.values())
    all_species = set()
    for p in pathways:
        all_species.update(p["species"])

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "pathway_count": len(pathways),
        "unique_species": sorted(all_species),
        "pathways": pathways
    }


@_ensure_initialized
def join_compound_ancestors_tree(chebi_id: str, max_depth: int = 10) -> Dict[str, Any]:
    """
    49. Composé → arbre d'ancêtres ChEBI (2 tables).

    Args:
        chebi_id: ChEBI identifier
        max_depth: Profondeur maximale de l'arbre

    Returns:
        Dict avec l'arbre d'ancêtres du composé
    """
    from gws_biota import Compound
    from gws_biota.compound.compound import CompoundAncestor

    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    ancestors = []
    ca_links = list(CompoundAncestor.select().where(CompoundAncestor.compound == compound).limit(100))
    for link in ca_links:
        anc = link.ancestor
        if anc:
            ancestors.append({
                "chebi_id": anc.chebi_id,
                "name": anc.name,
                "formula": anc.formula
            })

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "ancestor_count": len(ancestors),
        "ancestors": ancestors
    }


@_ensure_initialized
def join_compound_common_reactions(chebi_id_1: str, chebi_id_2: str) -> Dict[str, Any]:
    """
    50. Réactions en commun entre deux composés (3 tables).

    Args:
        chebi_id_1: Premier ChEBI ID
        chebi_id_2: Deuxième ChEBI ID

    Returns:
        Dict avec les réactions impliquant les deux composés
    """
    from gws_biota import Compound, Reaction
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct

    if not chebi_id_1.startswith("CHEBI:"):
        chebi_id_1 = f"CHEBI:{chebi_id_1}"
    if not chebi_id_2.startswith("CHEBI:"):
        chebi_id_2 = f"CHEBI:{chebi_id_2}"

    c1 = Compound.get_or_none(Compound.chebi_id == chebi_id_1)
    c2 = Compound.get_or_none(Compound.chebi_id == chebi_id_2)

    if not c1 or not c2:
        return {"error": "One or both compounds not found"}

    def get_reaction_ids(compound):
        ids = set()
        for link in ReactionSubstrate.select().where(ReactionSubstrate.compound == compound):
            ids.add(link.reaction_id)
        for link in ReactionProduct.select().where(ReactionProduct.compound == compound):
            ids.add(link.reaction_id)
        return ids

    r1 = get_reaction_ids(c1)
    r2 = get_reaction_ids(c2)
    shared = r1 & r2

    shared_reactions = []
    for rid in shared:
        r = Reaction.get_or_none(Reaction.id == rid)
        if r:
            shared_reactions.append({"rhea_id": r.rhea_id, "name": r.name, "direction": r.direction})

    return {
        "compound_1": {"chebi_id": chebi_id_1, "name": c1.name},
        "compound_2": {"chebi_id": chebi_id_2, "name": c2.name},
        "reactions_c1": len(r1),
        "reactions_c2": len(r2),
        "shared_count": len(shared_reactions),
        "shared_reactions": shared_reactions
    }


@_ensure_initialized
def join_compound_producing_enzymes_by_taxon(chebi_id: str, tax_id: str = None, limit: int = 50) -> Dict[str, Any]:
    """
    51. Enzymes produisant un composé, optionnellement filtré par taxon (4 tables).

    Args:
        chebi_id: ChEBI identifier du produit
        tax_id: Optionnel - filtrer par taxon
        limit: Nombre maximum de résultats

    Returns:
        Dict avec les enzymes produisant ce composé
    """
    from gws_biota import Compound, Reaction, Enzyme, Taxonomy
    from gws_biota.reaction.reaction import ReactionProduct, ReactionEnzyme

    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    # Find reactions that produce this compound
    prod_links = list(ReactionProduct.select().where(ReactionProduct.compound == compound))

    enzymes_data = []
    seen_enzymes = set()
    for pl in prod_links:
        reaction = pl.reaction
        re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
        for rel in re_links:
            enzyme = rel.enzyme
            key = f"{enzyme.ec_number}_{enzyme.uniprot_id}"
            if key in seen_enzymes:
                continue

            if tax_id and enzyme.tax_id != tax_id:
                continue

            seen_enzymes.add(key)
            enzymes_data.append({
                "ec_number": enzyme.ec_number,
                "uniprot_id": enzyme.uniprot_id,
                "name": enzyme.name,
                "tax_id": enzyme.tax_id,
                "reaction_rhea_id": reaction.rhea_id
            })

            if len(enzymes_data) >= limit:
                break
        if len(enzymes_data) >= limit:
            break

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "tax_filter": tax_id,
        "producing_enzyme_count": len(enzymes_data),
        "enzymes": enzymes_data
    }


@_ensure_initialized
def join_compound_consuming_enzymes_by_taxon(chebi_id: str, tax_id: str = None, limit: int = 50) -> Dict[str, Any]:
    """
    52. Enzymes consommant un composé, optionnellement filtré par taxon (4 tables).

    Args:
        chebi_id: ChEBI identifier du substrat
        tax_id: Optionnel - filtrer par taxon
        limit: Nombre maximum de résultats

    Returns:
        Dict avec les enzymes consommant ce composé
    """
    from gws_biota import Compound, Reaction, Enzyme, Taxonomy
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionEnzyme

    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)
    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    sub_links = list(ReactionSubstrate.select().where(ReactionSubstrate.compound == compound))

    enzymes_data = []
    seen_enzymes = set()
    for sl in sub_links:
        reaction = sl.reaction
        re_links = list(ReactionEnzyme.select().where(ReactionEnzyme.reaction == reaction))
        for rel in re_links:
            enzyme = rel.enzyme
            key = f"{enzyme.ec_number}_{enzyme.uniprot_id}"
            if key in seen_enzymes:
                continue

            if tax_id and enzyme.tax_id != tax_id:
                continue

            seen_enzymes.add(key)
            enzymes_data.append({
                "ec_number": enzyme.ec_number,
                "uniprot_id": enzyme.uniprot_id,
                "name": enzyme.name,
                "tax_id": enzyme.tax_id,
                "reaction_rhea_id": reaction.rhea_id
            })

            if len(enzymes_data) >= limit:
                break
        if len(enzymes_data) >= limit:
            break

    return {
        "chebi_id": chebi_id,
        "compound_name": compound.name,
        "tax_filter": tax_id,
        "consuming_enzyme_count": len(enzymes_data),
        "enzymes": enzymes_data
    }


# ============================================================================
# JOIN FUNCTIONS - TAXONOMY/PATHWAY/ONTOLOGY (53-60)
# ============================================================================

@_ensure_initialized
def join_taxonomy_enzymes_proteins_count(tax_id: str) -> Dict[str, Any]:
    """
    53. Statistiques enzymes + protéines pour un taxon (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        Dict avec les comptages d'enzymes et protéines
    """
    from gws_biota import Enzyme, Protein, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    if not taxonomy:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    enzyme_count = Enzyme.select().where(Enzyme.tax_id == tax_id).count()
    protein_count = Protein.select().where(Protein.tax_id == tax_id).count()

    # Unique EC numbers
    enzymes = list(Enzyme.select(Enzyme.ec_number).where(Enzyme.tax_id == tax_id).distinct())
    unique_ec = len(set(e.ec_number for e in enzymes if e.ec_number))

    return {
        "tax_id": tax_id,
        "tax_name": taxonomy.name,
        "tax_rank": taxonomy.rank,
        "enzyme_count": enzyme_count,
        "unique_ec_numbers": unique_ec,
        "protein_count": protein_count
    }


@_ensure_initialized
def join_taxonomy_children_enzyme_stats(tax_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    54. Enfants taxonomiques et leurs statistiques enzymes (2 tables).

    Args:
        tax_id: NCBI Taxonomy ID du parent
        limit: Nombre maximum d'enfants

    Returns:
        Dict avec les enfants et leur nombre d'enzymes
    """
    from gws_biota import Enzyme, Taxonomy

    parent = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    if not parent:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    children = list(Taxonomy.select().where(
        Taxonomy.ancestor_tax_id == tax_id
    ).limit(limit))

    children_stats = []
    for child in children:
        enzyme_count = Enzyme.select().where(Enzyme.tax_id == child.tax_id).count()
        children_stats.append({
            "tax_id": child.tax_id,
            "name": child.name,
            "rank": child.rank,
            "enzyme_count": enzyme_count
        })

    children_stats.sort(key=lambda x: x["enzyme_count"], reverse=True)

    return {
        "parent_tax_id": tax_id,
        "parent_name": parent.name,
        "children_count": len(children_stats),
        "total_enzymes_in_children": sum(c["enzyme_count"] for c in children_stats),
        "children": children_stats
    }


@_ensure_initialized
def join_taxonomy_reactions_compounds(tax_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    55. Taxon → Réactions → Composés (substrats + produits) (4 tables).

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum de réactions

    Returns:
        Dict avec réactions et composés du taxon
    """
    from gws_biota import Reaction, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    if not taxonomy:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    reactions = list(Reaction.search_by_tax_ids(tax_id))[:limit]

    compounds_set = {}
    reaction_list = []

    for r in reactions:
        subs = [{"chebi_id": s.chebi_id, "name": s.name} for s in r.substrates]
        prods = [{"chebi_id": p.chebi_id, "name": p.name} for p in r.products]

        for s in r.substrates:
            if s.chebi_id and s.chebi_id not in compounds_set:
                compounds_set[s.chebi_id] = {"chebi_id": s.chebi_id, "name": s.name, "as_substrate": True, "as_product": False}
            elif s.chebi_id:
                compounds_set[s.chebi_id]["as_substrate"] = True

        for p in r.products:
            if p.chebi_id and p.chebi_id not in compounds_set:
                compounds_set[p.chebi_id] = {"chebi_id": p.chebi_id, "name": p.name, "as_substrate": False, "as_product": True}
            elif p.chebi_id:
                compounds_set[p.chebi_id]["as_product"] = True

        reaction_list.append({
            "rhea_id": r.rhea_id,
            "name": r.name,
            "substrates": subs,
            "products": prods
        })

    return {
        "tax_id": tax_id,
        "tax_name": taxonomy.name,
        "reaction_count": len(reaction_list),
        "unique_compound_count": len(compounds_set),
        "compounds": list(compounds_set.values()),
        "reactions": reaction_list
    }


@_ensure_initialized
def join_pathway_reactions_enzymes(reactome_id: str) -> Dict[str, Any]:
    """
    56. Pathway → Composés → Réactions → Enzymes (5 tables).

    Args:
        reactome_id: Reactome pathway identifier

    Returns:
        Dict avec les réactions et enzymes du pathway
    """
    from gws_biota import Pathway, PathwayCompound, Compound
    from gws_biota.reaction.reaction import ReactionSubstrate, ReactionProduct, ReactionEnzyme

    pathway = Pathway.get_or_none(Pathway.reactome_pathway_id == reactome_id)
    if not pathway:
        return {"error": f"No pathway found with Reactome ID {reactome_id}"}

    pc_links = list(PathwayCompound.select().where(
        PathwayCompound.reactome_pathway_id == reactome_id
    ))

    reactions_map = {}
    enzymes_map = {}

    for pc in pc_links:
        compound = Compound.get_or_none(Compound.chebi_id == pc.chebi_id)
        if not compound:
            continue

        # Find reactions involving this compound
        for link in ReactionSubstrate.select().where(ReactionSubstrate.compound == compound):
            r = link.reaction
            if r.rhea_id not in reactions_map:
                reactions_map[r.rhea_id] = {"rhea_id": r.rhea_id, "name": r.name, "enzymes": []}
                for re_link in ReactionEnzyme.select().where(ReactionEnzyme.reaction == r):
                    e = re_link.enzyme
                    reactions_map[r.rhea_id]["enzymes"].append(e.ec_number)
                    enzymes_map[e.ec_number] = {"ec_number": e.ec_number, "name": e.name}

        for link in ReactionProduct.select().where(ReactionProduct.compound == compound):
            r = link.reaction
            if r.rhea_id not in reactions_map:
                reactions_map[r.rhea_id] = {"rhea_id": r.rhea_id, "name": r.name, "enzymes": []}
                for re_link in ReactionEnzyme.select().where(ReactionEnzyme.reaction == r):
                    e = re_link.enzyme
                    reactions_map[r.rhea_id]["enzymes"].append(e.ec_number)
                    enzymes_map[e.ec_number] = {"ec_number": e.ec_number, "name": e.name}

    return {
        "reactome_id": reactome_id,
        "pathway_name": pathway.name,
        "compound_count": len(pc_links),
        "reaction_count": len(reactions_map),
        "enzyme_count": len(enzymes_map),
        "reactions": list(reactions_map.values()),
        "enzymes": list(enzymes_map.values())
    }


@_ensure_initialized
def join_pathway_ancestor_compounds(reactome_id: str) -> Dict[str, Any]:
    """
    57. Pathway → ancêtres → composés de chaque ancêtre (3 tables).

    Args:
        reactome_id: Reactome pathway identifier

    Returns:
        Dict avec la hiérarchie des pathways et leurs composés
    """
    from gws_biota import Pathway, PathwayCompound, Compound
    from gws_biota.pathway.pathway import PathwayAncestor

    pathway = Pathway.get_or_none(Pathway.reactome_pathway_id == reactome_id)
    if not pathway:
        return {"error": f"No pathway found with Reactome ID {reactome_id}"}

    # Get ancestors
    pa_links = list(PathwayAncestor.select().where(PathwayAncestor.pathway == pathway).limit(50))

    ancestors_data = []
    for link in pa_links:
        anc = link.ancestor
        if not anc:
            continue

        # Get compounds of ancestor pathway
        compounds = []
        pc_links = list(PathwayCompound.select().where(
            PathwayCompound.reactome_pathway_id == anc.reactome_pathway_id
        ).limit(20))
        for pc in pc_links:
            comp = Compound.get_or_none(Compound.chebi_id == pc.chebi_id)
            if comp:
                compounds.append({"chebi_id": comp.chebi_id, "name": comp.name})

        ancestors_data.append({
            "reactome_id": anc.reactome_pathway_id,
            "name": anc.name,
            "compound_count": len(compounds),
            "compounds": compounds
        })

    return {
        "reactome_id": reactome_id,
        "pathway_name": pathway.name,
        "ancestor_count": len(ancestors_data),
        "ancestors": ancestors_data
    }


@_ensure_initialized
def join_go_ancestors_tree(go_id: str) -> Dict[str, Any]:
    """
    58. GO term → arbre complet des ancêtres (2 tables).

    Args:
        go_id: GO identifier (ex: "GO:0008150")

    Returns:
        Dict avec l'arbre des ancêtres GO
    """
    from gws_biota.go.go import GO, GOAncestor

    if not go_id.startswith("GO:"):
        go_id = f"GO:{go_id}"

    go_term = GO.get_or_none(GO.go_id == go_id)
    if not go_term:
        return {"error": f"No GO term found with ID {go_id}"}

    ancestors = []
    ga_links = list(GOAncestor.select().where(GOAncestor.go == go_term).limit(200))
    for link in ga_links:
        anc = link.ancestor
        if anc:
            ancestors.append({
                "go_id": anc.go_id,
                "name": anc.name,
                "namespace": anc.namespace
            })

    # Group by namespace
    by_namespace = {}
    for a in ancestors:
        ns = a.get("namespace", "unknown")
        if ns not in by_namespace:
            by_namespace[ns] = []
        by_namespace[ns].append(a)

    return {
        "go_id": go_id,
        "go_name": go_term.name,
        "namespace": go_term.namespace,
        "ancestor_count": len(ancestors),
        "by_namespace": by_namespace,
        "ancestors": ancestors
    }


@_ensure_initialized
def join_organism_full_profile(tax_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    59. Profil complet d'un organisme: enzymes + protéines + réactions + composés (5 tables).

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum par catégorie

    Returns:
        Dict avec le profil complet de l'organisme
    """
    from gws_biota import Enzyme, Protein, Reaction, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    if not taxonomy:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    # Enzymes
    enzymes = list(Enzyme.select().where(Enzyme.tax_id == tax_id).limit(limit))
    enzyme_data = [{"ec_number": e.ec_number, "name": e.name, "uniprot_id": e.uniprot_id}
                   for e in enzymes]

    # Proteins
    proteins = list(Protein.select().where(Protein.tax_id == tax_id).limit(limit))
    protein_data = [{"uniprot_id": p.uniprot_id, "gene": p.uniprot_gene, "evidence": p.evidence_score}
                    for p in proteins]

    # Reactions
    reactions = list(Reaction.search_by_tax_ids(tax_id))[:limit]
    reaction_data = [{"rhea_id": r.rhea_id, "name": r.name, "direction": r.direction}
                     for r in reactions]

    # Unique compounds from reactions
    compounds_set = {}
    for r in reactions:
        for s in r.substrates:
            if s.chebi_id and s.chebi_id not in compounds_set:
                compounds_set[s.chebi_id] = {"chebi_id": s.chebi_id, "name": s.name}
        for p in r.products:
            if p.chebi_id and p.chebi_id not in compounds_set:
                compounds_set[p.chebi_id] = {"chebi_id": p.chebi_id, "name": p.name}

    return {
        "tax_id": tax_id,
        "tax_name": taxonomy.name,
        "tax_rank": taxonomy.rank,
        "statistics": {
            "enzyme_count": Enzyme.select().where(Enzyme.tax_id == tax_id).count(),
            "protein_count": Protein.select().where(Protein.tax_id == tax_id).count(),
            "reaction_count": len(reaction_data),
            "compound_count": len(compounds_set)
        },
        "enzymes": enzyme_data,
        "proteins": protein_data,
        "reactions": reaction_data,
        "compounds": list(compounds_set.values())
    }


@_ensure_initialized
def join_compare_two_taxa_enzymes(tax_id_1: str, tax_id_2: str) -> Dict[str, Any]:
    """
    60. Compare les profils enzymatiques de deux taxons (2 tables).

    Args:
        tax_id_1: Premier NCBI Taxonomy ID
        tax_id_2: Deuxième NCBI Taxonomy ID

    Returns:
        Dict avec les EC partagés et uniques à chaque taxon
    """
    from gws_biota import Enzyme, Taxonomy

    tax1 = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id_1)
    tax2 = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id_2)

    if not tax1 or not tax2:
        return {"error": "One or both taxa not found"}

    # Get EC numbers for each taxon
    ec_set_1 = set()
    for e in Enzyme.select(Enzyme.ec_number).where(Enzyme.tax_id == tax_id_1):
        if e.ec_number:
            ec_set_1.add(e.ec_number)

    ec_set_2 = set()
    for e in Enzyme.select(Enzyme.ec_number).where(Enzyme.tax_id == tax_id_2):
        if e.ec_number:
            ec_set_2.add(e.ec_number)

    shared = ec_set_1 & ec_set_2
    only_1 = ec_set_1 - ec_set_2
    only_2 = ec_set_2 - ec_set_1

    # Jaccard similarity
    union = ec_set_1 | ec_set_2
    jaccard = len(shared) / len(union) if union else 0.0

    return {
        "taxon_1": {"tax_id": tax_id_1, "name": tax1.name, "ec_count": len(ec_set_1)},
        "taxon_2": {"tax_id": tax_id_2, "name": tax2.name, "ec_count": len(ec_set_2)},
        "shared_ec_count": len(shared),
        "only_taxon1_count": len(only_1),
        "only_taxon2_count": len(only_2),
        "jaccard_similarity": round(jaccard, 4),
        "shared_ec_numbers": sorted(shared)[:100],
        "only_taxon1_ec": sorted(only_1)[:50],
        "only_taxon2_ec": sorted(only_2)[:50]
    }
