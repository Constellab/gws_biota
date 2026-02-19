from typing import Optional

from mcp.server.fastmcp import FastMCP


def init_gws_core():
    from gws_core_loader import load_gws_core

    load_gws_core()

    from gws_core.manage import AppManager

    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="ERROR")


init_gws_core()

# Import all complex functions from mcp_biota_complex
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

# Import all functions and DTOs from mcp_biota_simple
from mcp_biota_simple import (
    BTOListResult,
    BTOSummary,
    CompoundListResult,
    CompoundSummary,
    DatabaseStatistics,
    EnzymeListResult,
    # DTOs
    EnzymeSummary,
    GOListResult,
    GOSummary,
    PathwayListResult,
    PathwaySummary,
    ProteinCountResult,
    ProteinListResult,
    ProteinSummary,
    ReactionListResult,
    ReactionSummary,
    TaxonomyListResult,
    TaxonomySummary,
    count_proteins_by_taxon,
    get_bto_by_id,
    get_compound_by_chebi_id,
    get_compound_by_inchikey,
    get_compound_by_kegg_id,
    get_compounds_by_formula,
    get_compounds_by_mass_range,
    get_database_statistics,
    # Functions
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

mcp = FastMCP(
    "biota-database",
    instructions=(
        "This server provides access to the Constellab Biota database, "
        "a comprehensive biological knowledge base including enzymes, proteins, "
        "compounds, reactions, pathways, and taxonomic information."
    ),
)


# ============================================================================
# ENZYME TOOLS
# ============================================================================


@mcp.tool(description="Get an enzyme by its EC number")
def tool_get_enzyme_by_ec_number(ec_number: str):
    """Get an enzyme by its EC number.

    Args:
        ec_number: EC number (e.g., "1.1.1.1")
    """
    return get_enzyme_by_ec_number(ec_number)


@mcp.tool(description="List enzymes for a given taxon")
def tool_get_enzymes_by_taxon(tax_id: str):
    """List enzymes for a given taxon.

    Args:
        tax_id: NCBI Taxonomy ID (e.g., "9606" for Homo sapiens)
    """
    return get_enzymes_by_taxon(tax_id)


@mcp.tool(description="Get enzymes by UniProt ID")
def tool_get_enzymes_by_uniprot_id(uniprot_id: str):
    """Get enzymes by UniProt ID.

    Args:
        uniprot_id: UniProt identifier (e.g., "P12345")
    """
    return get_enzymes_by_uniprot_id(uniprot_id)


@mcp.tool(description="Search enzymes by name")
def tool_search_enzymes_by_name(query: str):
    """Search enzymes by name (full-text search).

    Args:
        query: Search term
    """
    return search_enzymes_by_name(query)


@mcp.tool(description="Get enzymes by taxonomic rank")
def tool_get_enzymes_by_taxonomy_rank(rank: str, value: str):
    """Get enzymes by taxonomic rank.

    Args:
        rank: Taxonomic rank ("species", "genus", "family", "order", "class", "phylum", "kingdom", "superkingdom")
        value: Value for the rank (e.g., "Homo sapiens", "Saccharomyces")
    """
    return get_enzymes_by_taxonomy_rank(rank, value)


# ============================================================================
# PROTEIN TOOLS
# ============================================================================


@mcp.tool(description="Get a protein by UniProt ID")
def tool_get_protein_by_uniprot_id(uniprot_id: str):
    """Get a protein by UniProt ID.

    Args:
        uniprot_id: UniProt identifier (e.g., "P12345")
    """
    return get_protein_by_uniprot_id(uniprot_id)


@mcp.tool(description="List proteins for an organism")
def tool_get_proteins_by_taxon(tax_id: str):
    """List proteins for an organism.

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return get_proteins_by_taxon(tax_id)


@mcp.tool(description="Search proteins by gene name")
def tool_get_proteins_by_gene_name(gene_name: str):
    """Search proteins by gene name.

    Args:
        gene_name: Gene name (or part of it)
    """
    return get_proteins_by_gene_name(gene_name)


@mcp.tool(description="Filter proteins by evidence score")
def tool_get_proteins_by_evidence_score(min_score: int, tax_id: Optional[str] = None):
    """Filter proteins by evidence score (1-5).

    Args:
        min_score: Minimum score (1=best, 5=lowest)
        tax_id: Optional - filter by taxon
    """
    return get_proteins_by_evidence_score(min_score, tax_id)


@mcp.tool(description="Count proteins by taxon")
def tool_count_proteins_by_taxon(tax_id: str):
    """Count proteins by taxon.

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return count_proteins_by_taxon(tax_id)


# ============================================================================
# COMPOUND TOOLS
# ============================================================================


@mcp.tool(description="Get a compound by ChEBI ID")
def tool_get_compound_by_chebi_id(chebi_id: str):
    """Get a compound by ChEBI ID.

    Args:
        chebi_id: ChEBI identifier (e.g., "CHEBI:15377" or "15377")
    """
    return get_compound_by_chebi_id(chebi_id)


@mcp.tool(description="Get a compound by InChIKey")
def tool_get_compound_by_inchikey(inchikey: str):
    """Get a compound by InChIKey.

    Args:
        inchikey: InChIKey identifier
    """
    return get_compound_by_inchikey(inchikey)


@mcp.tool(description="Search compounds by name")
def tool_search_compounds_by_name(query: str):
    """Search compounds by name.

    Args:
        query: Search term
    """
    return search_compounds_by_name(query)


@mcp.tool(description="Search compounds by chemical formula")
def tool_get_compounds_by_formula(formula: str):
    """Search compounds by chemical formula.

    Args:
        formula: Chemical formula (e.g., "C6H12O6")
    """
    return get_compounds_by_formula(formula)


@mcp.tool(description="Get compounds within a mass range")
def tool_get_compounds_by_mass_range(min_mass: float, max_mass: float):
    """Get compounds within a mass range.

    Args:
        min_mass: Minimum mass (Da)
        max_mass: Maximum mass (Da)
    """
    return get_compounds_by_mass_range(min_mass, max_mass)


# ============================================================================
# REACTION TOOLS
# ============================================================================


@mcp.tool(description="Get a reaction by Rhea ID")
def tool_get_reaction_by_rhea_id(rhea_id: str):
    """Get a reaction by Rhea ID.

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return get_reaction_by_rhea_id(rhea_id)


@mcp.tool(description="Get reactions catalyzed by an enzyme (EC number)")
def tool_get_reactions_by_ec_number(ec_number: str):
    """Get reactions catalyzed by an enzyme.

    Args:
        ec_number: EC number of the enzyme
    """
    return get_reactions_by_ec_number(ec_number)


@mcp.tool(description="Get reactions associated with a taxon")
def tool_get_reactions_by_taxon(tax_id: str):
    """Get reactions associated with a taxon.

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return get_reactions_by_taxon(tax_id)


# ============================================================================
# TAXONOMY TOOLS
# ============================================================================


@mcp.tool(description="Get a taxon by ID")
def tool_get_taxonomy_by_id(tax_id: str):
    """Get a taxon by ID.

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return get_taxonomy_by_id(tax_id)


@mcp.tool(description="Search taxa by scientific name")
def tool_search_taxonomy_by_name(query: str):
    """Search taxa by scientific name.

    Args:
        query: Search term
    """
    return search_taxonomy_by_name(query)


@mcp.tool(description="Get child taxa")
def tool_get_taxonomy_children(tax_id: str, rank: Optional[str] = None):
    """Get child taxa.

    Args:
        tax_id: NCBI Taxonomy ID of the parent
        rank: Optional - filter by rank
    """
    return get_taxonomy_children(tax_id, rank)


# ============================================================================
# PATHWAY TOOLS
# ============================================================================


@mcp.tool(description="Get a pathway by Reactome ID")
def tool_get_pathway_by_reactome_id(reactome_id: str):
    """Get a pathway by Reactome ID.

    Args:
        reactome_id: Reactome pathway identifier (e.g., "R-HSA-109582")
    """
    return get_pathway_by_reactome_id(reactome_id)


@mcp.tool(description="Search pathways by name")
def tool_search_pathways_by_name(query: str):
    """Search pathways by name.

    Args:
        query: Search term
    """
    return search_pathways_by_name(query)


@mcp.tool(description="Get pathways for a species")
def tool_get_pathways_by_species(species: str):
    """Get pathways for a species.

    Args:
        species: Species name (e.g., "Homo sapiens", "Mus musculus")
    """
    return get_pathways_by_species(species)


# ============================================================================
# BTO (TISSUE/ORGAN) TOOLS
# ============================================================================


@mcp.tool(description="Get a tissue/organ by BTO ID")
def tool_get_bto_by_id(bto_id: str):
    """Get a tissue/organ by BTO ID.

    Args:
        bto_id: BTO identifier (e.g., "BTO_0000142" for brain)
    """
    return get_bto_by_id(bto_id)


@mcp.tool(description="Search tissues/organs by name in BTO")
def tool_search_bto_by_name(query: str):
    """Search tissues/organs by name in BTO.

    Args:
        query: Search term (e.g., "liver", "brain", "blood")
    """
    return search_bto_by_name(query)


# ============================================================================
# GO (GENE ONTOLOGY) TOOLS
# ============================================================================


@mcp.tool(description="Get a GO term by ID")
def tool_get_go_by_id(go_id: str):
    """Get a GO term by ID.

    Args:
        go_id: GO identifier (e.g., "GO:0008150" or "0008150")
    """
    return get_go_by_id(go_id)


@mcp.tool(description="Search GO terms by name")
def tool_search_go_by_name(query: str, namespace: Optional[str] = None):
    """Search GO terms by name, optionally filtered by namespace.

    Args:
        query: Search term
        namespace: Optional - "molecular_function", "biological_process", "cellular_component"
    """
    return search_go_by_name(query, namespace)


# ============================================================================
# OTHER TOOLS
# ============================================================================


@mcp.tool(description="Get a compound by KEGG ID")
def tool_get_compound_by_kegg_id(kegg_id: str):
    """Get a compound by KEGG ID.

    Args:
        kegg_id: KEGG compound identifier (e.g., "C00001")
    """
    return get_compound_by_kegg_id(kegg_id)


@mcp.tool(description="Get a reaction by KEGG reaction ID")
def tool_get_reaction_by_kegg_id(kegg_id: str):
    """Get a reaction by KEGG reaction ID.

    Args:
        kegg_id: KEGG reaction identifier (e.g., "R00001")
    """
    return get_reaction_by_kegg_id(kegg_id)


@mcp.tool(description="Get database statistics overview")
def tool_get_database_statistics():
    """Get an overview of the Biota database: entity counts per table."""
    return get_database_statistics()


# ============================================================================
# COMPLEX QUERY TOOLS - MULTI-TABLE LOOKUPS
# ============================================================================


@mcp.tool(description="Get tissue sources where an enzyme is expressed")
def tool_get_enzyme_tissue_sources(ec_number: str):
    """Get tissues (BTO) where an enzyme is expressed.

    Args:
        ec_number: EC number of the enzyme
    """
    return get_enzyme_tissue_sources(ec_number)


@mcp.tool(description="Get substrates and products of a reaction")
def tool_get_reaction_substrates_products(rhea_id: str):
    """Get substrates and products of a reaction.

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return get_reaction_substrates_products(rhea_id)


@mcp.tool(description="Search reactions involving a compound")
def tool_search_reactions_by_compound(chebi_id: str, role: str = "both"):
    """Search reactions involving a compound.

    Args:
        chebi_id: ChEBI identifier (e.g., "CHEBI:15377" or "15377")
        role: Role filter - "substrate", "product", or "both" (default: "both")
    """
    return search_reactions_by_compound(chebi_id, role)


@mcp.tool(description="Get taxonomic lineage (ancestors)")
def tool_get_taxonomy_ancestors(tax_id: str):
    """Get taxonomic lineage (ancestors).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return get_taxonomy_ancestors(tax_id)


@mcp.tool(description="Get compounds involved in a pathway")
def tool_get_pathway_compounds(reactome_id: str):
    """Get compounds involved in a pathway.

    Args:
        reactome_id: Reactome pathway identifier (e.g., "R-HSA-109582")
    """
    return get_pathway_compounds(reactome_id)


@mcp.tool(description="Get enzymes expressed in a tissue")
def tool_get_enzymes_by_tissue(bto_id: str, tax_id: Optional[str] = None):
    """Get enzymes expressed in a tissue.

    Args:
        bto_id: BTO identifier of the tissue
        tax_id: Optional - filter by taxon
    """
    return get_enzymes_by_tissue(bto_id, tax_id)


@mcp.tool(description="Get enzymes associated with a protein")
def tool_get_enzymes_for_protein(uniprot_id: str):
    """Get enzymes associated with a protein (reverse lookup Protein → Enzymes).

    Args:
        uniprot_id: UniProt identifier of the protein
    """
    return get_enzymes_for_protein(uniprot_id)


# ============================================================================
# COMPLEX QUERY TOOLS - CROSS-ENTITY FUNCTIONS
# ============================================================================


@mcp.tool(description="Get enzyme-protein-taxon relationship table")
def tool_get_enzyme_protein_taxon_table(
    tax_id: Optional[str] = None, uniprot_id: Optional[str] = None, ec_number: Optional[str] = None
):
    """Get enzyme-protein-taxon relationship table.

    Args:
        tax_id: Optional - filter by taxon
        uniprot_id: Optional - filter by UniProt ID
        ec_number: Optional - filter by EC number
    """
    return get_enzyme_protein_taxon_table(tax_id, uniprot_id, ec_number)


@mcp.tool(description="Get complete metabolic network for a taxon")
def tool_get_metabolic_network_for_taxon(tax_id: str):
    """Get complete metabolic network for a taxon.

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return get_metabolic_network_for_taxon(tax_id)


# ============================================================================
# COMPLEX QUERY TOOLS - ENZYME-CENTRIC JOINS
# ============================================================================


@mcp.tool(description="Get enzyme reactions with substrates and products")
def tool_join_enzyme_reactions_compounds(ec_number: str):
    """Enzyme → Reactions → Substrates/Products (3 tables).

    Args:
        ec_number: EC number of the enzyme
    """
    return join_enzyme_reactions_compounds(ec_number)


@mcp.tool(description="Get enzyme with protein and full taxonomy")
def tool_join_enzyme_protein_taxonomy(ec_number: str):
    """Enzyme → Protein → Taxonomy with full lineage (3 tables).

    Args:
        ec_number: EC number
    """
    return join_enzyme_protein_taxonomy(ec_number)


@mcp.tool(description="Get enzyme tissues with BTO ancestors")
def tool_join_enzyme_bto_ancestors(ec_number: str):
    """Enzyme → BTO tissues → BTO ancestors (3 tables).

    Args:
        ec_number: EC number
    """
    return join_enzyme_bto_ancestors(ec_number)


@mcp.tool(description="Get enzymes and reactions for a taxon")
def tool_join_enzyme_reactions_by_taxon(tax_id: str):
    """Taxon → Enzymes → Reactions (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return join_enzyme_reactions_by_taxon(tax_id)


@mcp.tool(description="Get enzyme class hierarchy")
def tool_join_enzyme_class_hierarchy(ec_prefix: str):
    """EnzymeClass → Associated enzymes (2 tables).

    Args:
        ec_prefix: EC prefix (e.g., "1.1" for all oxidoreductases acting on alcohols)
    """
    return join_enzyme_class_hierarchy(ec_prefix)


@mcp.tool(description="Map deprecated enzyme to current reactions")
def tool_join_enzyme_deprecated_to_reactions(old_ec_number: str):
    """DeprecatedEnzyme → New EC → Reactions (3 tables).

    Args:
        old_ec_number: Old (deprecated) EC number
    """
    return join_enzyme_deprecated_to_reactions(old_ec_number)


@mcp.tool(description="Get enzyme orthologs with pathways")
def tool_join_enzyme_ortholog_pathway(ec_number: str):
    """EnzymeOrtholog → EnzymePathway (2 tables).

    Args:
        ec_number: EC number
    """
    return join_enzyme_ortholog_pathway(ec_number)


@mcp.tool(description="Get all tissues expressing enzymes from a taxon")
def tool_join_enzyme_all_tissues_by_taxon(tax_id: str):
    """Taxon → Enzymes → BTO tissues (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return join_enzyme_all_tissues_by_taxon(tax_id)


# ============================================================================
# COMPLEX QUERY TOOLS - REACTION-CENTRIC JOINS
# ============================================================================


@mcp.tool(description="Get complete reaction details")
def tool_join_reaction_full_detail(rhea_id: str):
    """Complete reaction: Substrates + Products + Enzymes + Taxonomy (5 tables).

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return join_reaction_full_detail(rhea_id)


@mcp.tool(description="Get reaction enzymes grouped by taxon")
def tool_join_reaction_enzymes_by_taxon(rhea_id: str):
    """Reaction → Enzymes grouped by taxon (3 tables).

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return join_reaction_enzymes_by_taxon(rhea_id)


@mcp.tool(description="Get shared compounds between two reactions")
def tool_join_reaction_shared_compounds(rhea_id_1: str, rhea_id_2: str):
    """Shared compounds between two reactions (3 tables).

    Args:
        rhea_id_1: First Rhea ID
        rhea_id_2: Second Rhea ID
    """
    return join_reaction_shared_compounds(rhea_id_1, rhea_id_2)


@mcp.tool(description="Find reactions converting substrate to product")
def tool_join_reactions_between_two_compounds(chebi_substrate: str, chebi_product: str):
    """Reactions converting a substrate to a product (3 tables).

    Args:
        chebi_substrate: ChEBI ID of substrate
        chebi_product: ChEBI ID of product
    """
    return join_reactions_between_two_compounds(chebi_substrate, chebi_product)


@mcp.tool(description="Get taxonomic distribution of a reaction")
def tool_join_reaction_taxonomy_distribution(rhea_id: str):
    """Taxonomic distribution of a reaction (3 tables).

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return join_reaction_taxonomy_distribution(rhea_id)


@mcp.tool(description="Get complete cross-references for a reaction")
def tool_join_reaction_cross_references(rhea_id: str):
    """Complete cross-references: reaction + enzymes + compounds (4 tables).

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return join_reaction_cross_references(rhea_id)


@mcp.tool(description="Get mass balance of a reaction")
def tool_join_reaction_mass_balance(rhea_id: str):
    """Mass balance of a reaction: substrates vs products (2 tables).

    Args:
        rhea_id: Rhea identifier (e.g., "RHEA:10000" or "10000")
    """
    return join_reaction_mass_balance(rhea_id)


@mcp.tool(description="Get reactions catalyzed by two enzymes")
def tool_join_reactions_by_enzyme_pair(ec_number_1: str, ec_number_2: str):
    """Reactions catalyzed by both EC numbers (3 tables).

    Args:
        ec_number_1: First EC number
        ec_number_2: Second EC number
    """
    return join_reactions_by_enzyme_pair(ec_number_1, ec_number_2)


# ============================================================================
# COMPLEX QUERY TOOLS - COMPOUND-CENTRIC JOINS
# ============================================================================


@mcp.tool(description="Get compound with reactions and enzymes")
def tool_join_compound_reactions_enzymes(chebi_id: str):
    """Compound → Reactions (substrate/product) → Enzymes (4 tables).

    Args:
        chebi_id: ChEBI identifier (e.g., "CHEBI:15377" or "15377")
    """
    return join_compound_reactions_enzymes(chebi_id)


@mcp.tool(description="Get compound pathways by species")
def tool_join_compound_pathway_species(chebi_id: str):
    """Compound → Pathways → Species (3 tables).

    Args:
        chebi_id: ChEBI identifier (e.g., "CHEBI:15377" or "15377")
    """
    return join_compound_pathway_species(chebi_id)


@mcp.tool(description="Get compound ancestors tree")
def tool_join_compound_ancestors_tree(chebi_id: str, max_depth: int = 10):
    """Compound → ChEBI ancestor tree (2 tables).

    Args:
        chebi_id: ChEBI identifier (e.g., "CHEBI:15377" or "15377")
        max_depth: Maximum depth of the tree
    """
    return join_compound_ancestors_tree(chebi_id, max_depth)


@mcp.tool(description="Get common reactions between two compounds")
def tool_join_compound_common_reactions(chebi_id_1: str, chebi_id_2: str):
    """Common reactions between two compounds (3 tables).

    Args:
        chebi_id_1: First ChEBI ID
        chebi_id_2: Second ChEBI ID
    """
    return join_compound_common_reactions(chebi_id_1, chebi_id_2)


@mcp.tool(description="Get enzymes producing a compound by taxon")
def tool_join_compound_producing_enzymes_by_taxon(chebi_id: str, tax_id: Optional[str] = None):
    """Enzymes producing a compound, optionally filtered by taxon (4 tables).

    Args:
        chebi_id: ChEBI identifier of the product
        tax_id: Optional - filter by taxon
    """
    return join_compound_producing_enzymes_by_taxon(chebi_id, tax_id)


@mcp.tool(description="Get enzymes consuming a compound by taxon")
def tool_join_compound_consuming_enzymes_by_taxon(chebi_id: str, tax_id: Optional[str] = None):
    """Enzymes consuming a compound, optionally filtered by taxon (4 tables).

    Args:
        chebi_id: ChEBI identifier of the substrate
        tax_id: Optional - filter by taxon
    """
    return join_compound_consuming_enzymes_by_taxon(chebi_id, tax_id)


# ============================================================================
# COMPLEX QUERY TOOLS - TAXONOMY/PATHWAY/ONTOLOGY JOINS
# ============================================================================


@mcp.tool(description="Get enzyme and protein statistics for a taxon")
def tool_join_taxonomy_enzymes_proteins_count(tax_id: str):
    """Enzymes + proteins statistics for a taxon (3 tables).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return join_taxonomy_enzymes_proteins_count(tax_id)


@mcp.tool(description="Get enzyme statistics for taxonomy children")
def tool_join_taxonomy_children_enzyme_stats(tax_id: str):
    """Taxonomic children and their enzyme statistics (2 tables).

    Args:
        tax_id: NCBI Taxonomy ID of the parent
    """
    return join_taxonomy_children_enzyme_stats(tax_id)


@mcp.tool(description="Get reactions and compounds for a taxon")
def tool_join_taxonomy_reactions_compounds(tax_id: str):
    """Taxon → Reactions → Compounds (substrates + products) (4 tables).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return join_taxonomy_reactions_compounds(tax_id)


@mcp.tool(description="Get pathway reactions and enzymes")
def tool_join_pathway_reactions_enzymes(reactome_id: str):
    """Pathway → Compounds → Reactions → Enzymes (5 tables).

    Args:
        reactome_id: Reactome pathway identifier
    """
    return join_pathway_reactions_enzymes(reactome_id)


@mcp.tool(description="Get pathway ancestors with compounds")
def tool_join_pathway_ancestor_compounds(reactome_id: str):
    """Pathway → ancestors → compounds of each ancestor (3 tables).

    Args:
        reactome_id: Reactome pathway identifier
    """
    return join_pathway_ancestor_compounds(reactome_id)


@mcp.tool(description="Get GO term ancestors tree")
def tool_join_go_ancestors_tree(go_id: str):
    """GO term → complete ancestor tree (2 tables).

    Args:
        go_id: GO identifier (e.g., "GO:0008150" or "0008150")
    """
    return join_go_ancestors_tree(go_id)


@mcp.tool(description="Get complete organism profile")
def tool_join_organism_full_profile(tax_id: str):
    """Complete organism profile: enzymes + proteins + reactions + compounds (5 tables).

    Args:
        tax_id: NCBI Taxonomy ID
    """
    return join_organism_full_profile(tax_id)


@mcp.tool(description="Compare enzyme profiles of two taxa")
def tool_join_compare_two_taxa_enzymes(tax_id_1: str, tax_id_2: str):
    """Compare enzymatic profiles of two taxa (2 tables).

    Args:
        tax_id_1: First NCBI Taxonomy ID
        tax_id_2: Second NCBI Taxonomy ID
    """
    return join_compare_two_taxa_enzymes(tax_id_1, tax_id_2)


# ============================================================================
# RUN SERVER
# ============================================================================

mcp.run(transport="stdio")
