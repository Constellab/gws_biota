"""
MCP Biota Query Functions
=========================

70 fonctions pour requêter la base de données Biota via MCP.

This module re-exports all functions from:
- mcp_biota_simple: Simple lookups, searches, and filters (1-2 tables)
- mcp_biota_complex: Multi-table joins, cross-entity relations, hierarchical traversals

Usage:
    from mcp_biota_functions import BiodataQueryService

    service = BiodataQueryService()
    result = service.get_enzyme_by_ec_number("1.1.1.1")
"""

# Import all simple functions
from mcp_biota_simple import (
    get_enzyme_by_ec_number,
    get_enzymes_by_taxon,
    get_enzymes_by_uniprot_id,
    search_enzymes_by_name,
    get_enzymes_by_taxonomy_rank,
    # Protein simple
    get_protein_by_uniprot_id,
    get_proteins_by_taxon,
    get_proteins_by_gene_name,
    get_proteins_by_evidence_score,
    count_proteins_by_taxon,
    # Compound simple
    get_compound_by_chebi_id,
    get_compound_by_inchikey,
    search_compounds_by_name,
    get_compounds_by_formula,
    get_compounds_by_mass_range,
    # Reaction simple
    get_reaction_by_rhea_id,
    get_reactions_by_ec_number,
    get_reactions_by_taxon,
    # Taxonomy simple
    get_taxonomy_by_id,
    search_taxonomy_by_name,
    get_taxonomy_children,
    # Pathway simple
    get_pathway_by_reactome_id,
    search_pathways_by_name,
    # BTO/GO/Other simple
    get_bto_by_id,
    search_bto_by_name,
    get_go_by_id,
    search_go_by_name,
    get_pathways_by_species,
    get_compound_by_kegg_id,
    get_reaction_by_kegg_id,
    get_database_statistics,
)

# Import all complex functions
from mcp_biota_complex import (
    # Multi-table lookups
    get_enzyme_tissue_sources,
    get_reaction_substrates_products,
    search_reactions_by_compound,
    get_taxonomy_ancestors,
    get_pathway_compounds,
    get_enzymes_by_tissue,
    get_enzymes_for_protein,
    # Cross-entity
    get_enzyme_protein_taxon_table,
    get_metabolic_network_for_taxon,
    # JOIN - Enzyme-centric
    join_enzyme_reactions_compounds,
    join_enzyme_protein_taxonomy,
    join_enzyme_bto_ancestors,
    join_enzyme_reactions_by_taxon,
    join_enzyme_class_hierarchy,
    join_enzyme_deprecated_to_reactions,
    join_enzyme_ortholog_pathway,
    join_enzyme_all_tissues_by_taxon,
    # JOIN - Reaction-centric
    join_reaction_full_detail,
    join_reaction_enzymes_by_taxon,
    join_reaction_shared_compounds,
    join_reactions_between_two_compounds,
    join_reaction_taxonomy_distribution,
    join_reaction_cross_references,
    join_reaction_mass_balance,
    join_reactions_by_enzyme_pair,
    # JOIN - Compound-centric
    join_compound_reactions_enzymes,
    join_compound_pathway_species,
    join_compound_ancestors_tree,
    join_compound_common_reactions,
    join_compound_producing_enzymes_by_taxon,
    join_compound_consuming_enzymes_by_taxon,
    # JOIN - Taxonomy/Pathway/Ontology
    join_taxonomy_enzymes_proteins_count,
    join_taxonomy_children_enzyme_stats,
    join_taxonomy_reactions_compounds,
    join_pathway_reactions_enzymes,
    join_pathway_ancestor_compounds,
    join_go_ancestors_tree,
    join_organism_full_profile,
    join_compare_two_taxa_enzymes,
)


# ============================================================================
# MCP SERVICE CLASS
# ============================================================================

class BiodataQueryService:
    """
    Service class exposing all Biota query functions for MCP.

    Usage:
        service = BiodataQueryService()
        result = service.get_enzyme_by_ec_number("1.1.1.1")
    """

    # === Simple functions (from mcp_biota_simple) ===

    # Enzyme functions
    get_enzyme_by_ec_number = staticmethod(get_enzyme_by_ec_number)
    get_enzymes_by_taxon = staticmethod(get_enzymes_by_taxon)
    get_enzymes_by_uniprot_id = staticmethod(get_enzymes_by_uniprot_id)
    search_enzymes_by_name = staticmethod(search_enzymes_by_name)
    get_enzymes_by_taxonomy_rank = staticmethod(get_enzymes_by_taxonomy_rank)

    # Protein functions
    get_protein_by_uniprot_id = staticmethod(get_protein_by_uniprot_id)
    get_proteins_by_taxon = staticmethod(get_proteins_by_taxon)
    get_proteins_by_gene_name = staticmethod(get_proteins_by_gene_name)
    get_proteins_by_evidence_score = staticmethod(get_proteins_by_evidence_score)
    count_proteins_by_taxon = staticmethod(count_proteins_by_taxon)

    # Compound functions
    get_compound_by_chebi_id = staticmethod(get_compound_by_chebi_id)
    get_compound_by_inchikey = staticmethod(get_compound_by_inchikey)
    search_compounds_by_name = staticmethod(search_compounds_by_name)
    get_compounds_by_formula = staticmethod(get_compounds_by_formula)
    get_compounds_by_mass_range = staticmethod(get_compounds_by_mass_range)

    # Reaction functions
    get_reaction_by_rhea_id = staticmethod(get_reaction_by_rhea_id)
    get_reactions_by_ec_number = staticmethod(get_reactions_by_ec_number)
    get_reactions_by_taxon = staticmethod(get_reactions_by_taxon)

    # Taxonomy functions
    get_taxonomy_by_id = staticmethod(get_taxonomy_by_id)
    search_taxonomy_by_name = staticmethod(search_taxonomy_by_name)
    get_taxonomy_children = staticmethod(get_taxonomy_children)

    # Pathway functions
    get_pathway_by_reactome_id = staticmethod(get_pathway_by_reactome_id)
    search_pathways_by_name = staticmethod(search_pathways_by_name)

    # BTO/GO/Other simple
    get_bto_by_id = staticmethod(get_bto_by_id)
    search_bto_by_name = staticmethod(search_bto_by_name)
    get_go_by_id = staticmethod(get_go_by_id)
    search_go_by_name = staticmethod(search_go_by_name)
    get_pathways_by_species = staticmethod(get_pathways_by_species)
    get_compound_by_kegg_id = staticmethod(get_compound_by_kegg_id)
    get_reaction_by_kegg_id = staticmethod(get_reaction_by_kegg_id)
    get_database_statistics = staticmethod(get_database_statistics)

    # === Complex functions (from mcp_biota_complex) ===

    # Multi-table lookups
    get_enzyme_tissue_sources = staticmethod(get_enzyme_tissue_sources)
    get_reaction_substrates_products = staticmethod(get_reaction_substrates_products)
    search_reactions_by_compound = staticmethod(search_reactions_by_compound)
    get_taxonomy_ancestors = staticmethod(get_taxonomy_ancestors)
    get_pathway_compounds = staticmethod(get_pathway_compounds)
    get_enzymes_by_tissue = staticmethod(get_enzymes_by_tissue)
    get_enzymes_for_protein = staticmethod(get_enzymes_for_protein)

    # Cross-entity functions
    get_enzyme_protein_taxon_table = staticmethod(get_enzyme_protein_taxon_table)
    get_metabolic_network_for_taxon = staticmethod(get_metabolic_network_for_taxon)

    # JOIN - Enzyme-centric
    join_enzyme_reactions_compounds = staticmethod(join_enzyme_reactions_compounds)
    join_enzyme_protein_taxonomy = staticmethod(join_enzyme_protein_taxonomy)
    join_enzyme_bto_ancestors = staticmethod(join_enzyme_bto_ancestors)
    join_enzyme_reactions_by_taxon = staticmethod(join_enzyme_reactions_by_taxon)
    join_enzyme_class_hierarchy = staticmethod(join_enzyme_class_hierarchy)
    join_enzyme_deprecated_to_reactions = staticmethod(join_enzyme_deprecated_to_reactions)
    join_enzyme_ortholog_pathway = staticmethod(join_enzyme_ortholog_pathway)
    join_enzyme_all_tissues_by_taxon = staticmethod(join_enzyme_all_tissues_by_taxon)

    # JOIN - Reaction-centric
    join_reaction_full_detail = staticmethod(join_reaction_full_detail)
    join_reaction_enzymes_by_taxon = staticmethod(join_reaction_enzymes_by_taxon)
    join_reaction_shared_compounds = staticmethod(join_reaction_shared_compounds)
    join_reactions_between_two_compounds = staticmethod(join_reactions_between_two_compounds)
    join_reaction_taxonomy_distribution = staticmethod(join_reaction_taxonomy_distribution)
    join_reaction_cross_references = staticmethod(join_reaction_cross_references)
    join_reaction_mass_balance = staticmethod(join_reaction_mass_balance)
    join_reactions_by_enzyme_pair = staticmethod(join_reactions_by_enzyme_pair)

    # JOIN - Compound-centric
    join_compound_reactions_enzymes = staticmethod(join_compound_reactions_enzymes)
    join_compound_pathway_species = staticmethod(join_compound_pathway_species)
    join_compound_ancestors_tree = staticmethod(join_compound_ancestors_tree)
    join_compound_common_reactions = staticmethod(join_compound_common_reactions)
    join_compound_producing_enzymes_by_taxon = staticmethod(join_compound_producing_enzymes_by_taxon)
    join_compound_consuming_enzymes_by_taxon = staticmethod(join_compound_consuming_enzymes_by_taxon)

    # JOIN - Taxonomy/Pathway/Ontology
    join_taxonomy_enzymes_proteins_count = staticmethod(join_taxonomy_enzymes_proteins_count)
    join_taxonomy_children_enzyme_stats = staticmethod(join_taxonomy_children_enzyme_stats)
    join_taxonomy_reactions_compounds = staticmethod(join_taxonomy_reactions_compounds)
    join_pathway_reactions_enzymes = staticmethod(join_pathway_reactions_enzymes)
    join_pathway_ancestor_compounds = staticmethod(join_pathway_ancestor_compounds)
    join_go_ancestors_tree = staticmethod(join_go_ancestors_tree)
    join_organism_full_profile = staticmethod(join_organism_full_profile)
    join_compare_two_taxa_enzymes = staticmethod(join_compare_two_taxa_enzymes)
