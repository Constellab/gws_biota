"""
MCP Biota Simple Query Functions
=================================

Simple lookup, search, and filter functions for the Biota database.
These functions typically query 1-2 tables with straightforward logic.

Categories:
- Enzyme lookups (5 functions)
- Protein lookups (5 functions)
- Compound lookups (5 functions)
- Reaction lookups (4 functions)
- Taxonomy lookups (3 functions)
- Pathway lookups (3 functions)
- BTO/GO lookups (4 functions)
- Other lookups (3 functions)
"""

from typing import Optional, List, Dict, Any, Union


# ============================================================================
# INITIALIZATION
# ============================================================================

_initialized = False


def _init_gws_core():
    """Initialize GWS Core environment (called once)."""
    global _initialized
    if _initialized:
        return

    from gws_core_loader import load_gws_core
    load_gws_core()
    from gws_core.manage import AppManager
    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="ERROR")
    _initialized = True


def _ensure_initialized(func):
    """Decorator to ensure GWS Core is initialized before function execution."""
    def wrapper(*args, **kwargs):
        _init_gws_core()
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _entity_to_dict(entity, fields: List[str] = None) -> Dict[str, Any]:
    """Convert a Peewee entity to a dictionary."""
    if entity is None:
        return None

    result = {}
    if fields:
        for field in fields:
            value = getattr(entity, field, None)
            # Handle special types
            if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict)):
                value = str(value)
            result[field] = value
    else:
        # Get all fields from model
        for field_name in entity._meta.fields.keys():
            value = getattr(entity, field_name, None)
            if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict)):
                value = str(value)
            result[field_name] = value

    return result


def _entities_to_list(entities, fields: List[str] = None, limit: int = None) -> List[Dict[str, Any]]:
    """Convert multiple Peewee entities to a list of dictionaries."""
    results = []
    for i, entity in enumerate(entities):
        if limit and i >= limit:
            break
        results.append(_entity_to_dict(entity, fields))
    return results


# ============================================================================
# ENZYME FUNCTIONS (1-5)
# ============================================================================

@_ensure_initialized
def get_enzyme_by_ec_number(ec_number: str) -> Dict[str, Any]:
    """
    1. Récupère un enzyme par son numéro EC.

    Args:
        ec_number: Numéro EC de l'enzyme (ex: "1.1.1.1")

    Returns:
        Dict avec les informations de l'enzyme ou None si non trouvé
    """
    from gws_biota import Enzyme

    enzyme = Enzyme.get_or_none(Enzyme.ec_number == ec_number)
    if enzyme:
        return _entity_to_dict(enzyme)

    # Try to find multiple enzymes with this EC number
    enzymes = list(Enzyme.select().where(Enzyme.ec_number == ec_number).limit(100))
    if enzymes:
        return {
            "count": len(enzymes),
            "enzymes": _entities_to_list(enzymes)
        }

    return {"error": f"No enzyme found with EC number {ec_number}"}


@_ensure_initialized
def get_enzymes_by_taxon(tax_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    2. Liste les enzymes d'un taxon donné.

    Args:
        tax_id: NCBI Taxonomy ID (ex: "9606" pour Homo sapiens)
        limit: Nombre maximum de résultats (défaut: 100)

    Returns:
        Dict avec la liste des enzymes et le compte total
    """
    from gws_biota import Enzyme, Taxonomy

    # Get taxonomy info
    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    enzymes = list(Enzyme.select().where(Enzyme.tax_id == tax_id).limit(limit))
    total_count = Enzyme.select().where(Enzyme.tax_id == tax_id).count()

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "total_count": total_count,
        "returned_count": len(enzymes),
        "enzymes": _entities_to_list(enzymes,
            fields=["ec_number", "uniprot_id", "name", "tax_species"])
    }


@_ensure_initialized
def get_enzymes_by_uniprot_id(uniprot_id: str) -> Dict[str, Any]:
    """
    3. Récupère les enzymes par UniProt ID.

    Args:
        uniprot_id: UniProt identifier (ex: "P12345")

    Returns:
        Dict avec les informations des enzymes
    """
    from gws_biota import Enzyme

    enzymes = list(Enzyme.select().where(Enzyme.uniprot_id == uniprot_id))

    if not enzymes:
        return {"error": f"No enzyme found with UniProt ID {uniprot_id}", "count": 0}

    return {
        "uniprot_id": uniprot_id,
        "count": len(enzymes),
        "enzymes": _entities_to_list(enzymes)
    }


@_ensure_initialized
def search_enzymes_by_name(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    4. Recherche enzymes par nom (full-text search).

    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats (défaut: 50)

    Returns:
        Dict avec la liste des enzymes correspondants
    """
    from gws_biota import Enzyme

    # Search in name field using LIKE
    enzymes = list(Enzyme.select().where(
        Enzyme.name.contains(query)
    ).limit(limit))

    return {
        "query": query,
        "count": len(enzymes),
        "enzymes": _entities_to_list(enzymes,
            fields=["ec_number", "uniprot_id", "name", "tax_id", "tax_species"])
    }


@_ensure_initialized
def get_enzymes_by_taxonomy_rank(rank: str, value: str, limit: int = 100) -> Dict[str, Any]:
    """
    5. Récupère les enzymes par rang taxonomique.

    Args:
        rank: Rang taxonomique ("species", "genus", "family", "order", "class", "phylum", "kingdom")
        value: Valeur du rang (ex: "Homo sapiens", "Saccharomyces")
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des enzymes
    """
    from gws_biota import Enzyme

    rank_mapping = {
        "species": Enzyme.tax_species,
        "genus": Enzyme.tax_genus,
        "family": Enzyme.tax_family,
        "order": Enzyme.tax_order,
        "class": Enzyme.tax_class,
        "phylum": Enzyme.tax_phylum,
        "kingdom": Enzyme.tax_kingdom,
        "superkingdom": Enzyme.tax_superkingdom,
    }

    if rank.lower() not in rank_mapping:
        return {"error": f"Invalid rank. Valid ranks: {list(rank_mapping.keys())}"}

    field = rank_mapping[rank.lower()]
    enzymes = list(Enzyme.select().where(field == value).limit(limit))
    total_count = Enzyme.select().where(field == value).count()

    return {
        "rank": rank,
        "value": value,
        "total_count": total_count,
        "returned_count": len(enzymes),
        "enzymes": _entities_to_list(enzymes,
            fields=["ec_number", "uniprot_id", "name", "tax_id", "tax_species"])
    }


# ============================================================================
# PROTEIN FUNCTIONS (7-11)
# ============================================================================

@_ensure_initialized
def get_protein_by_uniprot_id(uniprot_id: str) -> Dict[str, Any]:
    """
    7. Récupère une protéine par UniProt ID.

    Args:
        uniprot_id: UniProt identifier (ex: "P12345")

    Returns:
        Dict avec les informations de la protéine
    """
    from gws_biota import Protein, Taxonomy

    protein = Protein.get_or_none(Protein.uniprot_id == uniprot_id)

    if not protein:
        return {"error": f"No protein found with UniProt ID {uniprot_id}"}

    result = _entity_to_dict(protein)

    # Add taxonomy info
    if protein.tax_id:
        taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == protein.tax_id)
        if taxonomy:
            result["tax_name"] = taxonomy.name
            result["tax_rank"] = taxonomy.rank

    return result


@_ensure_initialized
def get_proteins_by_taxon(tax_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    8. Liste les protéines d'un organisme.

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des protéines
    """
    from gws_biota import Protein, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    proteins = list(Protein.select().where(Protein.tax_id == tax_id).limit(limit))
    total_count = Protein.select().where(Protein.tax_id == tax_id).count()

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "total_count": total_count,
        "returned_count": len(proteins),
        "proteins": _entities_to_list(proteins,
            fields=["uniprot_id", "uniprot_gene", "evidence_score"])
    }


@_ensure_initialized
def get_proteins_by_gene_name(gene_name: str, limit: int = 50) -> Dict[str, Any]:
    """
    9. Recherche protéines par nom de gène.

    Args:
        gene_name: Nom du gène (ou partie)
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des protéines
    """
    from gws_biota import Protein

    proteins = list(Protein.select().where(
        Protein.uniprot_gene.contains(gene_name)
    ).limit(limit))

    return {
        "query": gene_name,
        "count": len(proteins),
        "proteins": _entities_to_list(proteins,
            fields=["uniprot_id", "uniprot_gene", "tax_id", "evidence_score"])
    }


@_ensure_initialized
def get_proteins_by_evidence_score(min_score: int, tax_id: str = None) -> Dict[str, Any]:
    """
    10. Filtre les protéines par score d'évidence (1-5).

    Args:
        min_score: Score minimum (1=best, 5=lowest)
        tax_id: Optionnel - filtrer par taxon

    Returns:
        Dict avec la liste des protéines
    """
    from gws_biota import Protein

    query = Protein.select().where(Protein.evidence_score <= min_score)

    if tax_id:
        query = query.where(Protein.tax_id == tax_id)

    proteins = list(query.limit(100))
    total_count = query.count()

    return {
        "min_score": min_score,
        "tax_id": tax_id,
        "total_count": total_count,
        "returned_count": len(proteins),
        "proteins": _entities_to_list(proteins,
            fields=["uniprot_id", "uniprot_gene", "tax_id", "evidence_score"])
    }


@_ensure_initialized
def count_proteins_by_taxon(tax_id: str) -> Dict[str, Any]:
    """
    11. Compte les protéines par taxon.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        Dict avec le compte et les statistiques
    """
    from gws_biota import Protein, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    total_count = Protein.select().where(Protein.tax_id == tax_id).count()

    # Count by evidence score
    evidence_counts = {}
    for score in range(1, 6):
        count = Protein.select().where(
            (Protein.tax_id == tax_id) &
            (Protein.evidence_score == score)
        ).count()
        evidence_counts[f"score_{score}"] = count

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "total_count": total_count,
        "by_evidence_score": evidence_counts
    }


# ============================================================================
# COMPOUND FUNCTIONS (12-16)
# ============================================================================

@_ensure_initialized
def get_compound_by_chebi_id(chebi_id: str) -> Dict[str, Any]:
    """
    12. Récupère un composé par ChEBI ID.

    Args:
        chebi_id: ChEBI identifier (ex: "CHEBI:15377")

    Returns:
        Dict avec les informations du composé
    """
    from gws_biota import Compound

    # Normalize ChEBI ID
    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    compound = Compound.get_or_none(Compound.chebi_id == chebi_id)

    if not compound:
        return {"error": f"No compound found with ChEBI ID {chebi_id}"}

    return _entity_to_dict(compound,
        fields=["chebi_id", "kegg_id", "name", "formula", "mass",
                "monoisotopic_mass", "charge", "inchi", "inchikey", "smiles"])


@_ensure_initialized
def get_compound_by_inchikey(inchikey: str) -> Dict[str, Any]:
    """
    13. Récupère un composé par InChIKey.

    Args:
        inchikey: InChIKey identifier

    Returns:
        Dict avec les informations du composé
    """
    from gws_biota import Compound

    compound = Compound.get_or_none(Compound.inchikey == inchikey)

    if not compound:
        return {"error": f"No compound found with InChIKey {inchikey}"}

    return _entity_to_dict(compound,
        fields=["chebi_id", "kegg_id", "name", "formula", "mass",
                "monoisotopic_mass", "charge", "inchi", "inchikey", "smiles"])


@_ensure_initialized
def search_compounds_by_name(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    14. Recherche composés par nom.

    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(Compound.select().where(
        Compound.name.contains(query)
    ).limit(limit))

    return {
        "query": query,
        "count": len(compounds),
        "compounds": _entities_to_list(compounds,
            fields=["chebi_id", "kegg_id", "name", "formula", "mass"])
    }


@_ensure_initialized
def get_compounds_by_formula(formula: str) -> Dict[str, Any]:
    """
    15. Recherche par formule chimique.

    Args:
        formula: Formule chimique (ex: "C6H12O6")

    Returns:
        Dict avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(Compound.select().where(
        Compound.formula == formula
    ).limit(100))

    return {
        "formula": formula,
        "count": len(compounds),
        "compounds": _entities_to_list(compounds,
            fields=["chebi_id", "kegg_id", "name", "formula", "mass", "inchikey"])
    }


@_ensure_initialized
def get_compounds_by_mass_range(min_mass: float, max_mass: float, limit: int = 100) -> Dict[str, Any]:
    """
    16. Composés dans une plage de masse.

    Args:
        min_mass: Masse minimale (Da)
        max_mass: Masse maximale (Da)
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(Compound.select().where(
        (Compound.mass >= min_mass) &
        (Compound.mass <= max_mass)
    ).order_by(Compound.mass).limit(limit))

    total_count = Compound.select().where(
        (Compound.mass >= min_mass) &
        (Compound.mass <= max_mass)
    ).count()

    return {
        "min_mass": min_mass,
        "max_mass": max_mass,
        "total_count": total_count,
        "returned_count": len(compounds),
        "compounds": _entities_to_list(compounds,
            fields=["chebi_id", "name", "formula", "mass"])
    }


# ============================================================================
# REACTION FUNCTIONS (17-19)
# ============================================================================

@_ensure_initialized
def get_reaction_by_rhea_id(rhea_id: str) -> Dict[str, Any]:
    """
    17. Récupère une réaction par Rhea ID.

    Args:
        rhea_id: Rhea identifier (ex: "RHEA:10000")

    Returns:
        Dict avec les informations de la réaction
    """
    from gws_biota import Reaction

    # Normalize Rhea ID
    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    reaction = Reaction.get_or_none(Reaction.rhea_id == rhea_id)

    if not reaction:
        return {"error": f"No reaction found with Rhea ID {rhea_id}"}

    result = _entity_to_dict(reaction,
        fields=["rhea_id", "master_id", "name", "direction", "kegg_id", "metacyc_id"])

    # Add substrates and products
    result["substrates"] = [
        {"chebi_id": s.chebi_id, "name": s.name}
        for s in reaction.substrates
    ]
    result["products"] = [
        {"chebi_id": p.chebi_id, "name": p.name}
        for p in reaction.products
    ]

    # Add enzymes
    result["enzymes"] = [
        {"ec_number": e.ec_number, "name": e.name}
        for e in reaction.enzymes
    ]

    return result


@_ensure_initialized
def get_reactions_by_ec_number(ec_number: str, limit: int = 100) -> Dict[str, Any]:
    """
    18. Réactions catalysées par un EC.

    Args:
        ec_number: Numéro EC de l'enzyme
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des réactions
    """
    from gws_biota import Reaction

    reactions = list(Reaction.search_by_ec_numbers(ec_number))[:limit]

    results = []
    for r in reactions:
        results.append({
            "rhea_id": r.rhea_id,
            "name": r.name,
            "direction": r.direction,
            "kegg_id": r.kegg_id
        })

    return {
        "ec_number": ec_number,
        "count": len(results),
        "reactions": results
    }


@_ensure_initialized
def get_reactions_by_taxon(tax_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    19. Réactions associées à un taxon.

    Args:
        tax_id: NCBI Taxonomy ID
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des réactions
    """
    from gws_biota import Reaction, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    reactions = list(Reaction.search_by_tax_ids(tax_id))[:limit]

    results = []
    for r in reactions:
        results.append({
            "rhea_id": r.rhea_id,
            "name": r.name,
            "direction": r.direction,
            "kegg_id": r.kegg_id
        })

    return {
        "tax_id": tax_id,
        "tax_name": tax_name,
        "count": len(results),
        "reactions": results
    }


# ============================================================================
# TAXONOMY FUNCTIONS (22-23, 25)
# ============================================================================

@_ensure_initialized
def get_taxonomy_by_id(tax_id: str) -> Dict[str, Any]:
    """
    22. Récupère un taxon par ID.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        Dict avec les informations du taxon
    """
    from gws_biota import Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)

    if not taxonomy:
        return {"error": f"No taxonomy found with ID {tax_id}"}

    return _entity_to_dict(taxonomy,
        fields=["tax_id", "name", "rank", "division", "ancestor_tax_id"])


@_ensure_initialized
def search_taxonomy_by_name(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    23. Recherche taxons par nom scientifique.

    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des taxons
    """
    from gws_biota import Taxonomy

    taxonomies = list(Taxonomy.select().where(
        Taxonomy.name.contains(query)
    ).limit(limit))

    return {
        "query": query,
        "count": len(taxonomies),
        "taxonomies": _entities_to_list(taxonomies,
            fields=["tax_id", "name", "rank", "division"])
    }


@_ensure_initialized
def get_taxonomy_children(tax_id: str, rank: str = None, limit: int = 100) -> Dict[str, Any]:
    """
    25. Récupère les taxons enfants.

    Args:
        tax_id: NCBI Taxonomy ID du parent
        rank: Optionnel - filtrer par rang
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des enfants
    """
    from gws_biota import Taxonomy

    query = Taxonomy.select().where(Taxonomy.ancestor_tax_id == tax_id)

    if rank:
        query = query.where(Taxonomy.rank == rank)

    children = list(query.limit(limit))
    total_count = query.count()

    return {
        "parent_tax_id": tax_id,
        "rank_filter": rank,
        "total_count": total_count,
        "returned_count": len(children),
        "children": _entities_to_list(children,
            fields=["tax_id", "name", "rank", "division"])
    }


# ============================================================================
# PATHWAY FUNCTIONS (26, 28)
# ============================================================================

@_ensure_initialized
def get_pathway_by_reactome_id(reactome_id: str) -> Dict[str, Any]:
    """
    26. Récupère un pathway par Reactome ID.

    Args:
        reactome_id: Reactome pathway identifier (ex: "R-HSA-109582")

    Returns:
        Dict avec les informations du pathway
    """
    from gws_biota import Pathway

    pathway = Pathway.get_or_none(Pathway.reactome_pathway_id == reactome_id)

    if not pathway:
        return {"error": f"No pathway found with Reactome ID {reactome_id}"}

    return _entity_to_dict(pathway,
        fields=["reactome_pathway_id", "name"])


@_ensure_initialized
def search_pathways_by_name(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    28. Recherche pathways par nom.

    Args:
        query: Terme de recherche
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des pathways
    """
    from gws_biota import Pathway

    pathways = list(Pathway.select().where(
        Pathway.name.contains(query)
    ).limit(limit))

    return {
        "query": query,
        "count": len(pathways),
        "pathways": _entities_to_list(pathways,
            fields=["reactome_pathway_id", "name"])
    }


# ============================================================================
# BTO / GO / OTHER SIMPLE LOOKUPS (61-62, 64-66, 68-70)
# ============================================================================

@_ensure_initialized
def get_bto_by_id(bto_id: str) -> Dict[str, Any]:
    """
    61. Récupère un tissu/organe par BTO ID.

    Args:
        bto_id: BTO identifier (ex: "BTO_0000142" pour brain)

    Returns:
        Dict avec les informations du tissu
    """
    from gws_biota import BTO

    bto = BTO.get_or_none(BTO.bto_id == bto_id)
    if not bto:
        return {"error": f"No BTO term found with ID {bto_id}"}

    return _entity_to_dict(bto, fields=["bto_id", "name"])


@_ensure_initialized
def search_bto_by_name(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    62. Recherche tissus/organes par nom dans BTO.

    Args:
        query: Terme de recherche (ex: "liver", "brain", "blood")
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des tissus correspondants
    """
    from gws_biota import BTO

    btos = list(BTO.select().where(BTO.name.contains(query)).limit(limit))

    return {
        "query": query,
        "count": len(btos),
        "tissues": _entities_to_list(btos, fields=["bto_id", "name"])
    }


@_ensure_initialized
def get_go_by_id(go_id: str) -> Dict[str, Any]:
    """
    64. Récupère un terme GO par son identifiant.

    Args:
        go_id: GO identifier (ex: "GO:0008150")

    Returns:
        Dict avec les informations du terme GO
    """
    from gws_biota.go.go import GO

    if not go_id.startswith("GO:"):
        go_id = f"GO:{go_id}"

    go_term = GO.get_or_none(GO.go_id == go_id)
    if not go_term:
        return {"error": f"No GO term found with ID {go_id}"}

    return _entity_to_dict(go_term, fields=["go_id", "name", "namespace"])


@_ensure_initialized
def search_go_by_name(query: str, namespace: str = None, limit: int = 50) -> Dict[str, Any]:
    """
    65. Recherche termes GO par nom, optionnellement filtré par namespace.

    Args:
        query: Terme de recherche
        namespace: Optionnel - "molecular_function", "biological_process", "cellular_component"
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des termes GO
    """
    from gws_biota.go.go import GO

    q = GO.select().where(GO.name.contains(query))
    if namespace:
        q = q.where(GO.namespace == namespace)

    go_terms = list(q.limit(limit))

    return {
        "query": query,
        "namespace_filter": namespace,
        "count": len(go_terms),
        "go_terms": _entities_to_list(go_terms, fields=["go_id", "name", "namespace"])
    }


@_ensure_initialized
def get_pathways_by_species(species: str, limit: int = 100) -> Dict[str, Any]:
    """
    66. Récupère les pathways pour une espèce donnée.

    Args:
        species: Nom de l'espèce (ex: "Homo sapiens", "Mus musculus")
        limit: Nombre maximum de résultats

    Returns:
        Dict avec la liste des pathways pour cette espèce
    """
    from gws_biota import Pathway, PathwayCompound

    # Get unique pathway IDs for this species
    pc_links = list(PathwayCompound.select(PathwayCompound.reactome_pathway_id).where(
        PathwayCompound.species == species
    ).distinct().limit(limit))

    pathways = []
    seen = set()
    for pc in pc_links:
        pid = pc.reactome_pathway_id
        if pid in seen:
            continue
        seen.add(pid)

        pw = Pathway.get_or_none(Pathway.reactome_pathway_id == pid)
        if pw:
            pathways.append({
                "reactome_id": pw.reactome_pathway_id,
                "name": pw.name
            })

    return {
        "species": species,
        "pathway_count": len(pathways),
        "pathways": pathways
    }


@_ensure_initialized
def get_compound_by_kegg_id(kegg_id: str) -> Dict[str, Any]:
    """
    68. Récupère un composé par KEGG ID.

    Args:
        kegg_id: KEGG compound identifier (ex: "C00001")

    Returns:
        Dict avec les informations du composé
    """
    from gws_biota import Compound

    compound = Compound.get_or_none(Compound.kegg_id == kegg_id)
    if not compound:
        return {"error": f"No compound found with KEGG ID {kegg_id}"}

    return _entity_to_dict(compound,
        fields=["chebi_id", "kegg_id", "name", "formula", "mass",
                "monoisotopic_mass", "charge", "inchi", "inchikey", "smiles"])


@_ensure_initialized
def get_reaction_by_kegg_id(kegg_id: str) -> Dict[str, Any]:
    """
    69. Récupère une réaction par KEGG reaction ID.

    Args:
        kegg_id: KEGG reaction identifier (ex: "R00001")

    Returns:
        Dict avec les informations de la réaction
    """
    from gws_biota import Reaction

    reaction = Reaction.get_or_none(Reaction.kegg_id == kegg_id)
    if not reaction:
        return {"error": f"No reaction found with KEGG ID {kegg_id}"}

    result = _entity_to_dict(reaction,
        fields=["rhea_id", "master_id", "name", "direction", "kegg_id", "metacyc_id"])

    result["substrates"] = [{"chebi_id": s.chebi_id, "name": s.name} for s in reaction.substrates]
    result["products"] = [{"chebi_id": p.chebi_id, "name": p.name} for p in reaction.products]
    result["enzymes"] = [{"ec_number": e.ec_number, "name": e.name} for e in reaction.enzymes]

    return result


@_ensure_initialized
def get_database_statistics() -> Dict[str, Any]:
    """
    70. Vue d'ensemble de la base de données Biota: nombre d'entités par table.

    Returns:
        Dict avec les statistiques globales de la base
    """
    from gws_biota import Enzyme, Protein, Compound, Reaction, Taxonomy, Pathway, PathwayCompound
    from gws_biota import EnzymeClass, EnzymeOrtholog, DeprecatedEnzyme
    from gws_biota import BTO
    from gws_biota.go.go import GO
    from gws_biota.enzyme.enzyme import EnzymeBTO
    from gws_biota.reaction.reaction import ReactionEnzyme, ReactionSubstrate, ReactionProduct

    stats = {
        "primary_entities": {
            "enzymes": Enzyme.select().count(),
            "proteins": Protein.select().count(),
            "compounds": Compound.select().count(),
            "reactions": Reaction.select().count(),
            "taxonomies": Taxonomy.select().count(),
            "pathways": Pathway.select().count(),
        },
        "classification": {
            "enzyme_classes": EnzymeClass.select().count(),
            "enzyme_orthologs": EnzymeOrtholog.select().count(),
            "deprecated_enzymes": DeprecatedEnzyme.select().count(),
        },
        "ontologies": {
            "go_terms": GO.select().count(),
            "bto_tissues": BTO.select().count(),
        },
        "junction_tables": {
            "reaction_substrates": ReactionSubstrate.select().count(),
            "reaction_products": ReactionProduct.select().count(),
            "reaction_enzymes": ReactionEnzyme.select().count(),
            "enzyme_bto_links": EnzymeBTO.select().count(),
            "pathway_compounds": PathwayCompound.select().count(),
        }
    }

    stats["total_entities"] = sum(stats["primary_entities"].values())
    stats["total_relationships"] = sum(stats["junction_tables"].values())

    return stats
