"""
MCP Biota V2 - Consolidated Tools
===================================

Optimized MCP server with 5 consolidated tools instead of 70+.
Reduces token usage, improves tool selection accuracy, and adds
pagination/summary support for large result sets.

Tools:
    1. search          - Full-text search any entity by name
    2. get_by_id       - Get detailed info on a specific entity by ID
    3. list_by_filter  - List entities matching filters (taxon, formula, mass, etc.)
    4. explore_relationships - Complex multi-table joins and relationship queries
    5. get_database_statistics - Database overview and counts
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP


def init_gws_core():
    from gws_core_loader import load_gws_core

    load_gws_core()

    from gws_core.manage import AppManager

    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="ERROR")


init_gws_core()

from mcp_biota_complex import (
    get_enzyme_protein_taxon_table,
    get_enzyme_tissue_sources,
    get_enzymes_by_tissue,
    get_enzymes_for_protein,
    get_metabolic_network_for_taxon,
    get_pathway_compounds,
    get_reaction_substrates_products,
    get_taxonomy_ancestors,
    join_compare_two_taxa_enzymes,
    join_compound_ancestors_tree,
    join_compound_common_reactions,
    join_compound_consuming_enzymes_by_taxon,
    join_compound_pathway_species,
    join_compound_producing_enzymes_by_taxon,
    join_compound_reactions_enzymes,
    join_enzyme_all_tissues_by_taxon,
    join_enzyme_bto_ancestors,
    join_enzyme_class_hierarchy,
    join_enzyme_deprecated_to_reactions,
    join_enzyme_ortholog_pathway,
    join_enzyme_protein_taxonomy,
    join_enzyme_reactions_by_taxon,
    join_enzyme_reactions_compounds,
    join_go_ancestors_tree,
    join_organism_full_profile,
    join_pathway_ancestor_compounds,
    join_pathway_reactions_enzymes,
    join_reaction_cross_references,
    join_reaction_enzymes_by_taxon,
    join_reaction_full_detail,
    join_reaction_mass_balance,
    join_reaction_shared_compounds,
    join_reaction_taxonomy_distribution,
    join_reactions_between_two_compounds,
    join_reactions_by_enzyme_pair,
    join_taxonomy_children_enzyme_stats,
    join_taxonomy_enzymes_proteins_count,
    join_taxonomy_reactions_compounds,
    search_reactions_by_compound,
)
from mcp_biota_simple import (
    count_proteins_by_taxon,
    get_bto_by_id,
    get_compound_by_chebi_id,
    get_compound_by_inchikey,
    get_compound_by_kegg_id,
    get_compounds_by_formula,
    get_compounds_by_mass_range,
    get_database_statistics,
    get_enzyme_by_ec_number,
    get_enzymes_by_taxon,
    get_enzymes_by_taxonomy_rank,
    get_enzymes_by_uniprot_id,
    get_go_by_id,
    get_pathway_by_reactome_id,
    get_pathways_by_species,
    get_protein_by_uniprot_id,
    get_proteins_by_evidence_score,
    get_proteins_by_gene_name,
    get_proteins_by_taxon,
    get_reaction_by_kegg_id,
    get_reaction_by_rhea_id,
    get_reactions_by_ec_number,
    get_reactions_by_taxon,
    get_taxonomy_by_id,
    get_taxonomy_children,
    search_bto_by_name,
    search_compounds_by_name,
    search_enzymes_by_name,
    search_go_by_name,
    search_pathways_by_name,
    search_taxonomy_by_name,
)

VALID_ENTITIES = ["enzyme", "protein", "compound", "reaction", "pathway", "taxonomy", "bto", "go"]

# ============================================================================
# HELPERS
# ============================================================================


def _truncate_list(items, limit: int, offset: int = 0):
    """Apply offset and limit to a list, returning truncated items + metadata."""
    total = len(items) if isinstance(items, list) else 0
    sliced = items[offset:offset + limit] if total > 0 else items
    return sliced, total


def _safe_model_dump(obj):
    """Safely convert a result to a dict, handling Pydantic models and Peewee entities."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__data__"):
        # Peewee model
        data = {}
        for field_name in obj._meta.fields.keys():
            value = getattr(obj, field_name, None)
            if hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool, list, dict)):
                value = str(value)
            data[field_name] = value
        return data
    if isinstance(obj, dict):
        return obj
    return str(obj)


def _truncate_result(result, limit: int = 20, offset: int = 0):
    """Truncate list fields in a Pydantic model result to save tokens."""
    if result is None:
        return {"found": False, "message": "Not found"}

    data = _safe_model_dump(result)
    if data is None:
        return {"found": False, "message": "Not found"}

    # Find list fields and truncate them
    for key, value in data.items():
        if isinstance(value, list) and len(value) > limit:
            total = len(value)
            data[key] = value[offset:offset + limit]
            data[f"{key}_total"] = total
            data[f"{key}_showing"] = f"{offset}-{min(offset + limit, total)} of {total}"
            if offset + limit < total:
                data[f"{key}_has_more"] = True

    return data


def _error_response(message: str):
    """Return a structured error instead of raising ValueError."""
    return {"found": False, "error": message}


# ============================================================================
# MCP SERVER
# ============================================================================

mcp = FastMCP(
    "biota-database",
    instructions="""Constellab Biota database: comprehensive biological knowledge base.

ENTITY TYPES: enzyme, protein, compound, reaction, pathway, taxonomy, bto (tissue/organ), go (gene ontology)

IDENTIFIER FORMATS:
- enzyme: EC number (e.g., "1.1.1.1")
- protein: UniProt ID (e.g., "P12345")
- compound: ChEBI ID ("CHEBI:15377" or "15377"), KEGG ID ("C00001"), or InChIKey
- reaction: Rhea ID ("RHEA:10000" or "10000") or KEGG ID ("R00001")
- pathway: Reactome ID (e.g., "R-HSA-109582")
- taxonomy: NCBI Taxonomy ID (e.g., "9606" for Homo sapiens)
- bto: BTO ID (e.g., "BTO_0000142" for brain)
- go: GO ID (e.g., "GO:0008150")

WORKFLOW GUIDE:
1. Start with 'search' to find entities by name
2. Use 'get_by_id' to get details on a specific entity
3. Use 'list_by_filter' to get entities matching criteria (by taxon, formula, mass, etc.)
4. Use 'explore_relationships' for complex queries crossing multiple entity types
5. Use 'get_database_statistics' for a database overview

IMPORTANT:
- All list results are paginated. Use limit/offset to browse large result sets.
- Default limit is 20 items. Ask for more only if the user needs it.
- Prefer the most specific query. Do NOT call multiple tools if one covers the answer.
- For organism overviews, use explore_relationships with query_type="organism_profile".
""",
)


# ============================================================================
# TOOL 1: SEARCH
# ============================================================================


@mcp.tool()
def search(entity: str, query: str, limit: int = 10, offset: int = 0):
    """Search any biological entity by name (full-text search).

    Args:
        entity: One of "enzyme", "protein", "compound", "reaction", "pathway", "taxonomy", "bto", "go"
        query: Search term (e.g., "glucose", "kinase", "Homo sapiens")
        limit: Max results to return (default 10)
        offset: Skip first N results for pagination (default 0)
    """
    entity = entity.lower().strip()
    if entity not in VALID_ENTITIES:
        return _error_response(f"Invalid entity '{entity}'. Must be one of: {VALID_ENTITIES}")

    try:
        search_map = {
            "enzyme": search_enzymes_by_name,
            "compound": search_compounds_by_name,
            "pathway": search_pathways_by_name,
            "taxonomy": search_taxonomy_by_name,
            "bto": search_bto_by_name,
        }

        if entity == "protein":
            result = get_proteins_by_gene_name(query)
            return _truncate_result(result, limit, offset)

        if entity == "reaction":
            # Reactions don't have a name search — search by EC number as fallback
            result = get_reactions_by_ec_number(query)
            return _truncate_result(result, limit, offset)

        if entity == "go":
            result = search_go_by_name(query)
            return _truncate_result(result, limit, offset)

        if entity in search_map:
            result = search_map[entity](query)
            return _truncate_result(result, limit, offset)

        return _error_response(f"Search not available for entity '{entity}'")
    except ValueError as e:
        return _error_response(str(e))


# ============================================================================
# TOOL 2: GET BY ID
# ============================================================================


@mcp.tool()
def get_by_id(entity: str, id: str):
    """Get detailed information about a specific biological entity by its identifier.

    Args:
        entity: One of "enzyme", "protein", "compound", "reaction", "pathway", "taxonomy", "bto", "go"
        id: The identifier. Format depends on entity type:
            - enzyme: EC number (e.g., "1.1.1.1")
            - protein: UniProt ID (e.g., "P12345")
            - compound: ChEBI ID ("CHEBI:15377" or "15377"), KEGG ID ("C00001"), or InChIKey
            - reaction: Rhea ID ("RHEA:10000" or "10000") or KEGG ID ("R00001")
            - pathway: Reactome ID (e.g., "R-HSA-109582")
            - taxonomy: NCBI Taxonomy ID (e.g., "9606")
            - bto: BTO ID (e.g., "BTO_0000142")
            - go: GO ID (e.g., "GO:0008150" or "0008150")
    """
    entity = entity.lower().strip()
    if entity not in VALID_ENTITIES:
        return _error_response(f"Invalid entity '{entity}'. Must be one of: {VALID_ENTITIES}")

    try:
        if entity == "enzyme":
            result = get_enzyme_by_ec_number(id)
        elif entity == "protein":
            result = get_protein_by_uniprot_id(id)
        elif entity == "compound":
            result = _get_compound_by_any_id(id)
        elif entity == "reaction":
            result = _get_reaction_by_any_id(id)
        elif entity == "pathway":
            result = get_pathway_by_reactome_id(id)
        elif entity == "taxonomy":
            result = get_taxonomy_by_id(id)
        elif entity == "bto":
            result = get_bto_by_id(id)
        elif entity == "go":
            result = get_go_by_id(id)
        else:
            return _error_response(f"Unknown entity type: {entity}")

        if result is None:
            return {"found": False, "message": f"No {entity} found with ID '{id}'"}

        data = _safe_model_dump(result)
        data["found"] = True
        return data
    except ValueError as e:
        return _error_response(str(e))


def _get_compound_by_any_id(id: str):
    """Try to find a compound by ChEBI, KEGG, or InChIKey."""
    # Try ChEBI
    result = get_compound_by_chebi_id(id)
    if result:
        return result

    # Try KEGG (starts with C)
    if id.upper().startswith("C") and id[1:].isdigit():
        result = get_compound_by_kegg_id(id)
        if result:
            return result

    # Try InChIKey (27 chars, uppercase, with hyphens)
    if len(id) == 27 and "-" in id:
        result = get_compound_by_inchikey(id)
        if result:
            return result

    return None


def _get_reaction_by_any_id(id: str):
    """Try to find a reaction by Rhea or KEGG ID."""
    # Try Rhea
    result = get_reaction_by_rhea_id(id)
    if result:
        return result

    # Try KEGG (starts with R)
    if id.upper().startswith("R") and id[1:].isdigit():
        result = get_reaction_by_kegg_id(id)
        if result:
            return result

    return None


# ============================================================================
# TOOL 3: LIST BY FILTER
# ============================================================================


@mcp.tool()
def list_by_filter(
    entity: str,
    tax_id: Optional[str] = None,
    ec_number: Optional[str] = None,
    uniprot_id: Optional[str] = None,
    formula: Optional[str] = None,
    min_mass: Optional[float] = None,
    max_mass: Optional[float] = None,
    rank: Optional[str] = None,
    rank_value: Optional[str] = None,
    gene_name: Optional[str] = None,
    min_evidence_score: Optional[int] = None,
    parent_tax_id: Optional[str] = None,
    species: Optional[str] = None,
    bto_id: Optional[str] = None,
    chebi_id: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List biological entities matching one or more filters.

    Args:
        entity: One of "enzyme", "protein", "compound", "reaction", "pathway", "taxonomy"
        tax_id: Filter by NCBI Taxonomy ID (for enzyme, protein, reaction)
        ec_number: Filter reactions by EC number
        uniprot_id: Filter enzymes by UniProt ID
        formula: Filter compounds by chemical formula (e.g., "C6H12O6")
        min_mass: Filter compounds by minimum mass (Da)
        max_mass: Filter compounds by maximum mass (Da)
        rank: Taxonomic rank for enzyme filtering ("species", "genus", "family", "order", "class", "phylum", "kingdom")
        rank_value: Value for the rank (e.g., "Homo sapiens") - requires rank parameter
        gene_name: Filter proteins by gene name
        min_evidence_score: Filter proteins by evidence score (1=best, 5=lowest)
        parent_tax_id: Get child taxa of this parent taxonomy ID
        species: Filter pathways by species name (e.g., "Homo sapiens")
        bto_id: Filter enzymes by tissue BTO ID
        chebi_id: Find reactions involving this compound (ChEBI ID)
        role: Role of compound in reaction: "substrate", "product", or "both" (default "both")
        limit: Max results to return (default 20)
        offset: Skip first N results for pagination (default 0)
    """
    entity = entity.lower().strip()

    try:
        # ENZYME
        if entity == "enzyme":
            if tax_id:
                result = get_enzymes_by_taxon(tax_id)
            elif uniprot_id:
                result = get_enzymes_by_uniprot_id(uniprot_id)
            elif rank and rank_value:
                result = get_enzymes_by_taxonomy_rank(rank, rank_value)
            elif bto_id:
                result = _safe_model_dump(get_enzymes_by_tissue(bto_id, tax_id))
                return _truncate_result_dict(result, limit, offset)
            else:
                return _error_response("Provide at least one filter: tax_id, uniprot_id, rank+rank_value, or bto_id")
            return _truncate_result(result, limit, offset)

        # PROTEIN
        elif entity == "protein":
            if tax_id:
                result = get_proteins_by_taxon(tax_id)
            elif gene_name:
                result = get_proteins_by_gene_name(gene_name)
            elif min_evidence_score is not None:
                result = get_proteins_by_evidence_score(min_evidence_score, tax_id)
            elif tax_id:
                return _safe_model_dump(count_proteins_by_taxon(tax_id))
            else:
                return _error_response("Provide at least one filter: tax_id, gene_name, or min_evidence_score")
            return _truncate_result(result, limit, offset)

        # COMPOUND
        elif entity == "compound":
            if formula:
                result = get_compounds_by_formula(formula)
            elif min_mass is not None and max_mass is not None:
                result = get_compounds_by_mass_range(min_mass, max_mass)
            else:
                return _error_response("Provide at least one filter: formula, or min_mass+max_mass")
            return _truncate_result(result, limit, offset)

        # REACTION
        elif entity == "reaction":
            if ec_number:
                result = get_reactions_by_ec_number(ec_number)
            elif tax_id:
                result = get_reactions_by_taxon(tax_id)
            elif chebi_id:
                result = search_reactions_by_compound(chebi_id, role or "both")
                return _truncate_result(result, limit, offset)
            else:
                return _error_response("Provide at least one filter: ec_number, tax_id, or chebi_id")
            return _truncate_result(result, limit, offset)

        # PATHWAY
        elif entity == "pathway":
            if species:
                result = get_pathways_by_species(species)
            else:
                return _error_response("Provide at least one filter: species")
            return _truncate_result(result, limit, offset)

        # TAXONOMY
        elif entity == "taxonomy":
            if parent_tax_id:
                result = get_taxonomy_children(parent_tax_id, rank)
            else:
                return _error_response("Provide at least one filter: parent_tax_id")
            return _truncate_result(result, limit, offset)

        else:
            return _error_response(f"list_by_filter not supported for entity '{entity}'. Use search instead.")

    except ValueError as e:
        return _error_response(str(e))


def _truncate_result_dict(data: dict, limit: int, offset: int):
    """Truncate list fields in a dict result."""
    if data is None:
        return {"found": False, "message": "Not found"}
    for key, value in data.items():
        if isinstance(value, list) and len(value) > limit:
            total = len(value)
            data[key] = value[offset:offset + limit]
            data[f"{key}_total"] = total
            data[f"{key}_showing"] = f"{offset}-{min(offset + limit, total)} of {total}"
            if offset + limit < total:
                data[f"{key}_has_more"] = True
    return data


# ============================================================================
# TOOL 4: EXPLORE RELATIONSHIPS
# ============================================================================


@mcp.tool()
def explore_relationships(
    query_type: str,
    id: str,
    target_id: Optional[str] = None,
    tax_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """Explore relationships between biological entities (multi-table joins).

    Args:
        query_type: The relationship query type. One of:

          ENZYME-CENTRIC:
            "enzyme_reactions"        - EC -> reactions with substrates/products
            "enzyme_proteins"         - EC -> proteins with full taxonomy lineage
            "enzyme_tissues"          - EC -> tissues (BTO) where expressed
            "enzyme_tissue_ancestors" - EC -> tissues with BTO ancestor hierarchy
            "enzyme_class_hierarchy"  - EC prefix -> enzyme classification tree
            "enzyme_orthologs"        - EC -> orthologs with pathways
            "deprecated_enzyme"       - old EC -> new EC -> current reactions
            "enzyme_protein_taxon"    - cross-table: enzyme-protein-taxon (filterable)

          REACTION-CENTRIC:
            "reaction_substrates_products" - Rhea -> substrates and products only
            "reaction_detail"          - Rhea -> full detail (enzymes + compounds + taxonomy)
            "reaction_by_taxon"        - Rhea -> enzymes grouped by organism
            "reaction_mass_balance"    - Rhea -> substrate vs product mass comparison
            "reaction_cross_refs"      - Rhea -> all cross-references (KEGG, MetaCyc, etc.)
            "reaction_taxonomy_dist"   - Rhea -> taxonomic distribution
            "shared_compounds"         - two Rhea IDs -> common compounds (use target_id)
            "reactions_between"        - two ChEBI IDs -> connecting reactions (use target_id)
            "reactions_by_enzyme_pair" - two EC numbers -> shared reactions (use target_id)

          COMPOUND-CENTRIC:
            "compound_reactions"        - ChEBI -> reactions -> enzymes
            "compound_pathways"         - ChEBI -> pathways by species
            "compound_ancestors"        - ChEBI -> ChEBI ontology tree
            "compound_common_reactions" - two ChEBI IDs -> shared reactions (use target_id)
            "compound_producers"        - ChEBI -> enzymes that produce it (use tax_id to filter)
            "compound_consumers"        - ChEBI -> enzymes that consume it (use tax_id to filter)

          ORGANISM / TAXONOMY:
            "organism_profile"          - tax_id -> full profile (enzymes + proteins + reactions + compounds)
            "metabolic_network"         - tax_id -> complete metabolic network
            "taxon_enzymes_reactions"   - tax_id -> enzymes -> reactions
            "taxon_tissues"             - tax_id -> all tissues expressing enzymes
            "taxon_stats"               - tax_id -> enzyme/protein counts
            "taxon_children_stats"      - tax_id -> children with enzyme statistics
            "taxon_ancestors"           - tax_id -> full taxonomic lineage
            "taxon_reactions_compounds" - tax_id -> reactions -> compounds (substrates + products)
            "compare_taxa"              - two tax IDs -> enzyme comparison (use target_id)
            "protein_enzymes"           - UniProt ID -> associated enzymes (reverse lookup)

          PATHWAY / ONTOLOGY:
            "pathway_enzymes"    - Reactome -> reactions -> enzymes
            "pathway_compounds"  - Reactome -> compounds
            "pathway_ancestors"  - Reactome -> ancestor pathways with compounds
            "go_ancestors"       - GO ID -> ancestor tree

        id: Primary identifier (EC number, ChEBI ID, Rhea ID, tax_id, Reactome ID, GO ID, UniProt ID...)
        target_id: Second identifier for comparison queries (e.g., second tax_id, second ChEBI ID, etc.)
        tax_id: Optional taxon filter for compound producer/consumer queries
        limit: Max items per list field in results (default 20)
        offset: Skip first N items in list fields (default 0)
    """
    query_type = query_type.lower().strip()

    try:
        result = _dispatch_relationship(query_type, id, target_id, tax_id)
        return _truncate_result(result, limit, offset)
    except ValueError as e:
        return _error_response(str(e))


def _require_target_id(target_id, query_type, label):
    """Validate that target_id is provided for comparison queries."""
    if not target_id:
        raise ValueError(f"target_id ({label}) is required for {query_type}")


# Dispatch tables: query_type -> callable(id, target_id, tax_id)
# "id_only" queries take just the primary id
_DISPATCH_ID_ONLY = {
    # Enzyme-centric
    "enzyme_reactions": join_enzyme_reactions_compounds,
    "enzyme_proteins": join_enzyme_protein_taxonomy,
    "enzyme_tissues": get_enzyme_tissue_sources,
    "enzyme_tissue_ancestors": join_enzyme_bto_ancestors,
    "enzyme_class_hierarchy": join_enzyme_class_hierarchy,
    "enzyme_orthologs": join_enzyme_ortholog_pathway,
    "deprecated_enzyme": join_enzyme_deprecated_to_reactions,
    # Reaction-centric
    "reaction_substrates_products": get_reaction_substrates_products,
    "reaction_detail": join_reaction_full_detail,
    "reaction_by_taxon": join_reaction_enzymes_by_taxon,
    "reaction_mass_balance": join_reaction_mass_balance,
    "reaction_cross_refs": join_reaction_cross_references,
    "reaction_taxonomy_dist": join_reaction_taxonomy_distribution,
    # Compound-centric
    "compound_reactions": join_compound_reactions_enzymes,
    "compound_pathways": join_compound_pathway_species,
    "compound_ancestors": join_compound_ancestors_tree,
    # Organism / Taxonomy
    "organism_profile": join_organism_full_profile,
    "metabolic_network": get_metabolic_network_for_taxon,
    "taxon_enzymes_reactions": join_enzyme_reactions_by_taxon,
    "taxon_tissues": join_enzyme_all_tissues_by_taxon,
    "taxon_stats": join_taxonomy_enzymes_proteins_count,
    "taxon_children_stats": join_taxonomy_children_enzyme_stats,
    "taxon_ancestors": get_taxonomy_ancestors,
    "taxon_reactions_compounds": join_taxonomy_reactions_compounds,
    "protein_enzymes": get_enzymes_for_protein,
    # Pathway / Ontology
    "pathway_enzymes": join_pathway_reactions_enzymes,
    "pathway_compounds": get_pathway_compounds,
    "pathway_ancestors": join_pathway_ancestor_compounds,
    "go_ancestors": join_go_ancestors_tree,
}

# "id + target_id" queries require both ids
_DISPATCH_TWO_IDS = {
    "shared_compounds": (join_reaction_shared_compounds, "second Rhea ID"),
    "reactions_between": (join_reactions_between_two_compounds, "product ChEBI ID"),
    "reactions_by_enzyme_pair": (join_reactions_by_enzyme_pair, "second EC number"),
    "compound_common_reactions": (join_compound_common_reactions, "second ChEBI ID"),
    "compare_taxa": (join_compare_two_taxa_enzymes, "second tax_id"),
}

# "id + optional tax_id" queries
_DISPATCH_WITH_TAX = {
    "compound_producers": join_compound_producing_enzymes_by_taxon,
    "compound_consumers": join_compound_consuming_enzymes_by_taxon,
}


def _dispatch_relationship(query_type: str, id: str, target_id: str = None, tax_id: str = None):
    """Route query_type to the appropriate function."""
    # Special case: enzyme_protein_taxon uses named kwargs
    if query_type == "enzyme_protein_taxon":
        return get_enzyme_protein_taxon_table(tax_id=tax_id, uniprot_id=target_id, ec_number=id)

    if query_type in _DISPATCH_ID_ONLY:
        return _DISPATCH_ID_ONLY[query_type](id)

    if query_type in _DISPATCH_TWO_IDS:
        func, label = _DISPATCH_TWO_IDS[query_type]
        _require_target_id(target_id, query_type, label)
        return func(id, target_id)

    if query_type in _DISPATCH_WITH_TAX:
        return _DISPATCH_WITH_TAX[query_type](id, tax_id)

    all_types = sorted(
        list(_DISPATCH_ID_ONLY) + list(_DISPATCH_TWO_IDS)
        + list(_DISPATCH_WITH_TAX) + ["enzyme_protein_taxon"]
    )
    raise ValueError(f"Unknown query_type '{query_type}'. Valid types: {all_types}")


# ============================================================================
# TOOL 5: DATABASE STATISTICS
# ============================================================================


@mcp.tool()
def database_statistics():
    """Get an overview of the Biota database: total counts per entity type
    (enzymes, proteins, compounds, reactions, pathways, taxa, BTO tissues, GO terms, etc.).
    Use this to understand what data is available before querying.
    """
    return _safe_model_dump(get_database_statistics())


# ============================================================================
# RUN SERVER
# ============================================================================

mcp.run(transport="stdio")
