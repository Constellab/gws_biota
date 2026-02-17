"""
MCP Biota Complex Query DTOs
=============================

Data Transfer Objects for complex multi-table queries in Biota database.
All DTOs inherit from BaseModelDTO for consistent serialization.
"""

from typing import Optional, List
from gws_core import BaseModelDTO
from gws_biota import Enzyme, Reaction, Compound, Taxonomy, Protein, BTO, Pathway, GO


# ============================================================================
# HELPER DTOs (Nested objects)
# ============================================================================

class TissueInfo(BaseModelDTO):
    """Tissue information from BTO"""
    bto_id: str
    name: str
    enzyme_uniprot_id: Optional[str] = None


class CompoundInfo(BaseModelDTO):
    """Basic compound information"""
    chebi_id: str
    name: str
    formula: Optional[str] = None
    mass: Optional[float] = None


class ReactionInfo(BaseModelDTO):
    """Basic reaction information"""
    rhea_id: str
    name: str
    direction: Optional[str] = None
    kegg_id: Optional[str] = None


class EnzymeInfo(BaseModelDTO):
    """Basic enzyme information"""
    ec_number: str
    name: str
    uniprot_id: Optional[str] = None
    tax_id: Optional[str] = None


class TaxonomyInfo(BaseModelDTO):
    """Basic taxonomy information"""
    tax_id: str
    name: str
    rank: Optional[str] = None


class ProteinInfo(BaseModelDTO):
    """Basic protein information"""
    uniprot_id: str
    gene: Optional[str] = None
    evidence_score: Optional[int] = None


class PathwayInfo(BaseModelDTO):
    """Basic pathway information"""
    reactome_id: str
    name: str


class GOInfo(BaseModelDTO):
    """Basic GO term information"""
    go_id: str
    name: str
    namespace: Optional[str] = None


class BTOAncestorInfo(BaseModelDTO):
    """BTO ancestor information"""
    bto_id: str
    name: str


# ============================================================================
# MULTI-TABLE LOOKUP DTOs
# ============================================================================

class EnzymeTissueSources(BaseModelDTO):
    """Function 6: Enzyme tissue sources"""
    ec_number: str
    enzyme_count: int
    tissue_count: int
    tissues: List[TissueInfo]


class ReactionSubstratesProducts(BaseModelDTO):
    """Function 20: Reaction substrates and products"""
    rhea_id: str
    reaction_name: str
    direction: Optional[str]
    substrate_count: int
    product_count: int
    substrates: List[CompoundInfo]
    products: List[CompoundInfo]


class ReactionsByCompound(BaseModelDTO):
    """Function 21: Reactions involving a compound"""
    chebi_id: str
    compound_name: str
    role_filter: str
    as_substrate_count: int
    as_product_count: int
    reactions_as_substrate: List[ReactionInfo]
    reactions_as_product: List[ReactionInfo]


class TaxonomyAncestors(BaseModelDTO):
    """Function 24: Taxonomy lineage"""
    tax_id: str
    name: str
    lineage_length: int
    lineage: List[TaxonomyInfo]


class PathwayCompoundsResult(BaseModelDTO):
    """Function 27: Compounds in a pathway"""
    reactome_id: str
    pathway_name: str
    compound_count: int
    compounds: List[CompoundInfo]


class EnzymesByTissue(BaseModelDTO):
    """Function 63: Enzymes expressed in a tissue"""
    bto_id: str
    tissue_name: str
    tax_filter: Optional[str]
    enzyme_count: int
    enzymes: List[EnzymeInfo]


class EnzymesForProtein(BaseModelDTO):
    """Function 67: Enzymes for a protein"""
    uniprot_id: str
    protein_gene: Optional[str]
    protein_tax_id: Optional[str]
    enzyme_count: int
    enzymes: List[EnzymeInfo]


# ============================================================================
# CROSS-ENTITY DTOs
# ============================================================================

class EnzymeProteinTaxonEntry(BaseModelDTO):
    """Entry in enzyme-protein-taxon table"""
    enzyme_ec_number: str
    enzyme_name: str
    enzyme_uniprot_id: Optional[str]
    protein_uniprot_id: Optional[str]
    protein_gene: Optional[str]
    protein_evidence_score: Optional[int]
    taxon_id: Optional[str]
    taxon_name: Optional[str]
    taxon_rank: Optional[str]


class EnzymeProteinTaxonTableFilters(BaseModelDTO):
    """Filters for enzyme-protein-taxon table"""
    tax_id: Optional[str]
    uniprot_id: Optional[str]
    ec_number: Optional[str]


class EnzymeProteinTaxonTable(BaseModelDTO):
    """Function 29: Enzyme-protein-taxon table"""
    filters: EnzymeProteinTaxonTableFilters
    count: int
    table: List[EnzymeProteinTaxonEntry]


class MetabolicNetworkStatistics(BaseModelDTO):
    """Statistics for metabolic network"""
    reaction_count: int
    enzyme_count: int
    compound_count: int


class MetabolicReactionData(BaseModelDTO):
    """Reaction data in metabolic network"""
    rhea_id: str
    name: str
    direction: Optional[str]
    substrates: List[str]  # ChEBI IDs
    products: List[str]  # ChEBI IDs
    enzymes: List[str]  # EC numbers


class MetabolicNetworkForTaxon(BaseModelDTO):
    """Function 30: Complete metabolic network for taxon"""
    tax_id: str
    tax_name: str
    statistics: MetabolicNetworkStatistics
    enzymes: List[EnzymeInfo]
    compounds: List[CompoundInfo]
    reactions: List[MetabolicReactionData]


# ============================================================================
# ENZYME-CENTRIC JOIN DTOs
# ============================================================================

class EnzymeReactionWithCompounds(BaseModelDTO):
    """Reaction with its substrates and products"""
    rhea_id: str
    reaction_name: str
    direction: Optional[str]
    substrates: List[CompoundInfo]
    products: List[CompoundInfo]


class EnzymeReactionsCompounds(BaseModelDTO):
    """Function 31: Enzyme -> Reactions -> Compounds"""
    ec_number: str
    enzyme_count: int
    reaction_count: int
    reactions: List[EnzymeReactionWithCompounds]


class EnzymeProteinTaxonomyEntry(BaseModelDTO):
    """Entry with enzyme, protein and taxonomy lineage"""
    enzyme_ec: str
    enzyme_uniprot_id: Optional[str]
    enzyme_name: str
    protein_gene: Optional[str]
    protein_evidence: Optional[int]
    taxon_id: Optional[str]
    taxon_name: Optional[str]
    lineage: List[TaxonomyInfo]


class EnzymeProteinTaxonomy(BaseModelDTO):
    """Function 32: Enzyme -> Protein -> Taxonomy"""
    ec_number: str
    count: int
    entries: List[EnzymeProteinTaxonomyEntry]


class TissueWithAncestors(BaseModelDTO):
    """Tissue with its BTO ancestors"""
    bto_id: str
    tissue_name: str
    enzyme_uniprot_id: Optional[str]
    ancestor_count: int
    ancestors: List[BTOAncestorInfo]


class EnzymeBTOAncestors(BaseModelDTO):
    """Function 33: Enzyme -> BTO tissues -> Ancestors"""
    ec_number: str
    tissue_count: int
    tissues: List[TissueWithAncestors]


class EnzymeWithReactions(BaseModelDTO):
    """Enzyme with its reactions"""
    ec_number: str
    enzyme_name: str
    uniprot_id: Optional[str]
    reaction_count: int
    reactions: List[ReactionInfo]


class EnzymeReactionsByTaxon(BaseModelDTO):
    """Function 34: Taxon -> Enzymes -> Reactions"""
    tax_id: str
    tax_name: str
    enzyme_count: int
    total_reactions: int
    enzymes: List[EnzymeWithReactions]


class EnzymeClassHierarchyEntry(BaseModelDTO):
    """Enzyme class with associated enzymes"""
    class_ec: str
    class_name: str
    enzyme_count: int
    enzymes: List[EnzymeInfo]


class EnzymeClassHierarchy(BaseModelDTO):
    """Function 35: Enzyme class hierarchy"""
    ec_prefix: str
    class_count: int
    classes: List[EnzymeClassHierarchyEntry]


class DeprecatedEnzymeMapping(BaseModelDTO):
    """Mapping from deprecated to new enzyme"""
    old_ec: str
    new_ec: str
    new_enzyme_count: int
    reaction_count: int
    reactions: List[ReactionInfo]


class DeprecatedEnzymeToReactions(BaseModelDTO):
    """Function 36: Deprecated enzyme -> New EC -> Reactions"""
    old_ec_number: str
    mapping_count: int
    mappings: List[DeprecatedEnzymeMapping]


class EnzymeOrthologEntry(BaseModelDTO):
    """Ortholog with pathway information"""
    ortholog_ec: str
    ortholog_name: str
    pathway: Optional[PathwayInfo]


class EnzymeOrthologPathway(BaseModelDTO):
    """Function 37: Enzyme ortholog -> Pathway"""
    ec_number: str
    ortholog_count: int
    orthologs: List[EnzymeOrthologEntry]


class TissueWithEnzymes(BaseModelDTO):
    """Tissue with enzyme EC numbers"""
    bto_id: str
    name: str
    enzyme_count: int
    enzyme_ec_numbers: List[str]


class EnzymeAllTissuesByTaxon(BaseModelDTO):
    """Function 38: Taxon -> Enzymes -> Tissues"""
    tax_id: str
    tax_name: str
    enzyme_count: int
    unique_tissue_count: int
    tissues: List[TissueWithEnzymes]


# ============================================================================
# REACTION-CENTRIC JOIN DTOs
# ============================================================================

class EnzymeWithTaxonomy(BaseModelDTO):
    """Enzyme with taxonomy information"""
    ec_number: str
    name: str
    uniprot_id: Optional[str]
    taxonomy: Optional[TaxonomyInfo]


class ReactionFullDetail(BaseModelDTO):
    """Function 39: Complete reaction details"""
    rhea_id: str
    reaction_name: str
    direction: Optional[str]
    kegg_id: Optional[str]
    metacyc_id: Optional[str]
    substrates: List[CompoundInfo]
    products: List[CompoundInfo]
    enzyme_count: int
    enzymes: List[EnzymeWithTaxonomy]


class TaxonEnzymeGroup(BaseModelDTO):
    """Enzymes grouped by taxon"""
    tax_id: str
    tax_name: str
    enzyme_count: int
    enzymes: List[EnzymeInfo]


class ReactionEnzymesByTaxon(BaseModelDTO):
    """Function 40: Reaction -> Enzymes by taxon"""
    rhea_id: str
    reaction_name: str
    taxon_count: int
    total_enzymes: int
    taxon_groups: List[TaxonEnzymeGroup]


class ReactionSharedCompounds(BaseModelDTO):
    """Function 41: Shared compounds between reactions"""
    reaction_1: str
    reaction_2: str
    compounds_r1: int
    compounds_r2: int
    shared_count: int
    shared_compounds: List[CompoundInfo]


class CompoundPair(BaseModelDTO):
    """Pair of compounds"""
    chebi_id: str
    name: str


class ReactionsBetweenCompounds(BaseModelDTO):
    """Function 42: Reactions between two compounds"""
    substrate: CompoundPair
    product: CompoundPair
    reaction_count: int
    reactions: List[ReactionInfo]


class ReactionTaxonomyDistribution(BaseModelDTO):
    """Function 43: Taxonomy distribution of reaction"""
    rhea_id: str
    reaction_name: str
    total_enzymes: int
    rank_distribution: dict  # rank -> count
    species_count: int
    species: List[TaxonomyInfo]


class CompoundXRef(BaseModelDTO):
    """Compound cross-reference"""
    chebi_id: str
    kegg_id: Optional[str]
    inchikey: Optional[str]
    role: str


class EnzymeXRef(BaseModelDTO):
    """Enzyme cross-reference"""
    ec_number: str
    uniprot_id: Optional[str]


class ReactionXRef(BaseModelDTO):
    """Reaction cross-references"""
    rhea_id: str
    master_id: Optional[str]
    kegg_id: Optional[str]
    metacyc_id: Optional[str]
    biocyc_ids: Optional[List[str]]
    sabio_rk_id: Optional[str]


class ReactionCrossReferences(BaseModelDTO):
    """Function 44: Complete cross-references for reaction"""
    reaction_xrefs: ReactionXRef
    compound_xrefs: List[CompoundXRef]
    enzyme_xrefs: List[EnzymeXRef]


class ReactionMassBalance(BaseModelDTO):
    """Function 45: Mass balance of reaction"""
    rhea_id: str
    reaction_name: str
    substrates: List[CompoundInfo]
    products: List[CompoundInfo]
    total_substrate_mass: float
    total_product_mass: float
    mass_difference: float


class ReactionsByEnzymePair(BaseModelDTO):
    """Function 46: Reactions by enzyme pair"""
    ec_number_1: str
    ec_number_2: str
    reactions_ec1_only: int
    reactions_ec2_only: int
    shared_count: int
    shared_reactions: List[ReactionInfo]


# ============================================================================
# COMPOUND-CENTRIC JOIN DTOs
# ============================================================================

class ReactionWithEnzymes(BaseModelDTO):
    """Reaction with enzyme list"""
    rhea_id: str
    name: str
    role: str  # "substrate" or "product"
    enzyme_count: int
    enzymes: List[EnzymeInfo]


class CompoundReactionsEnzymes(BaseModelDTO):
    """Function 47: Compound -> Reactions -> Enzymes"""
    chebi_id: str
    compound_name: str
    reaction_count: int
    reactions: List[ReactionWithEnzymes]


class PathwayWithSpecies(BaseModelDTO):
    """Pathway with species list"""
    reactome_id: str
    pathway_name: str
    species: List[str]


class CompoundPathwaySpecies(BaseModelDTO):
    """Function 48: Compound -> Pathways -> Species"""
    chebi_id: str
    compound_name: str
    pathway_count: int
    unique_species: List[str]
    pathways: List[PathwayWithSpecies]


class CompoundAncestorsTree(BaseModelDTO):
    """Function 49: Compound ancestors tree"""
    chebi_id: str
    compound_name: str
    ancestor_count: int
    ancestors: List[CompoundInfo]


class CompoundInfoPair(BaseModelDTO):
    """Information about two compounds"""
    chebi_id: str
    name: str


class CompoundCommonReactions(BaseModelDTO):
    """Function 50: Common reactions between compounds"""
    compound_1: CompoundInfoPair
    compound_2: CompoundInfoPair
    reactions_c1: int
    reactions_c2: int
    shared_count: int
    shared_reactions: List[ReactionInfo]


class EnzymeProducingCompound(BaseModelDTO):
    """Enzyme that produces a compound"""
    ec_number: str
    uniprot_id: Optional[str]
    name: str
    tax_id: Optional[str]
    reaction_rhea_id: str


class CompoundProducingEnzymesByTaxon(BaseModelDTO):
    """Function 51: Producing enzymes by taxon"""
    chebi_id: str
    compound_name: str
    tax_filter: Optional[str]
    producing_enzyme_count: int
    enzymes: List[EnzymeProducingCompound]


class EnzymeConsumingCompound(BaseModelDTO):
    """Enzyme that consumes a compound"""
    ec_number: str
    uniprot_id: Optional[str]
    name: str
    tax_id: Optional[str]
    reaction_rhea_id: str


class CompoundConsumingEnzymesByTaxon(BaseModelDTO):
    """Function 52: Consuming enzymes by taxon"""
    chebi_id: str
    compound_name: str
    tax_filter: Optional[str]
    consuming_enzyme_count: int
    enzymes: List[EnzymeConsumingCompound]


# ============================================================================
# TAXONOMY/PATHWAY/ONTOLOGY JOIN DTOs
# ============================================================================

class TaxonomyEnzymesProteinsCount(BaseModelDTO):
    """Function 53: Enzyme/protein statistics for taxon"""
    tax_id: str
    tax_name: str
    tax_rank: Optional[str]
    enzyme_count: int
    unique_ec_numbers: int
    protein_count: int


class TaxonomyChildStats(BaseModelDTO):
    """Statistics for taxonomy child"""
    tax_id: str
    name: str
    rank: Optional[str]
    enzyme_count: int


class TaxonomyChildrenEnzymeStats(BaseModelDTO):
    """Function 54: Children taxonomy enzyme stats"""
    parent_tax_id: str
    parent_name: str
    children_count: int
    total_enzymes_in_children: int
    children: List[TaxonomyChildStats]


class CompoundRole(BaseModelDTO):
    """Compound with role information"""
    chebi_id: str
    name: str
    as_substrate: bool
    as_product: bool


class ReactionWithCompounds(BaseModelDTO):
    """Reaction with substrate/product lists"""
    rhea_id: str
    name: str
    substrates: List[CompoundInfo]
    products: List[CompoundInfo]


class TaxonomyReactionsCompounds(BaseModelDTO):
    """Function 55: Taxon -> Reactions -> Compounds"""
    tax_id: str
    tax_name: str
    reaction_count: int
    unique_compound_count: int
    compounds: List[CompoundRole]
    reactions: List[ReactionWithCompounds]


class ReactionWithEnzymeList(BaseModelDTO):
    """Reaction with enzyme EC list"""
    rhea_id: str
    name: str
    enzymes: List[str]  # EC numbers


class PathwayReactionsEnzymes(BaseModelDTO):
    """Function 56: Pathway -> Reactions -> Enzymes"""
    reactome_id: str
    pathway_name: str
    compound_count: int
    reaction_count: int
    enzyme_count: int
    reactions: List[ReactionWithEnzymeList]
    enzymes: List[EnzymeInfo]


class AncestorPathwayWithCompounds(BaseModelDTO):
    """Ancestor pathway with compounds"""
    reactome_id: str
    name: str
    compound_count: int
    compounds: List[CompoundInfo]


class PathwayAncestorCompounds(BaseModelDTO):
    """Function 57: Pathway ancestors with compounds"""
    reactome_id: str
    pathway_name: str
    ancestor_count: int
    ancestors: List[AncestorPathwayWithCompounds]


class GOAncestorsTree(BaseModelDTO):
    """Function 58: GO ancestors tree"""
    go_id: str
    go_name: str
    namespace: Optional[str]
    ancestor_count: int
    by_namespace: dict  # namespace -> list of GO terms
    ancestors: List[GOInfo]


class OrganismStatistics(BaseModelDTO):
    """Statistics for organism profile"""
    enzyme_count: int
    protein_count: int
    reaction_count: int
    compound_count: int


class OrganismFullProfile(BaseModelDTO):
    """Function 59: Complete organism profile"""
    tax_id: str
    tax_name: str
    tax_rank: Optional[str]
    statistics: OrganismStatistics
    enzymes: List[EnzymeInfo]
    proteins: List[ProteinInfo]
    reactions: List[ReactionInfo]
    compounds: List[CompoundInfo]


class TaxonInfo(BaseModelDTO):
    """Information about a taxon for comparison"""
    tax_id: str
    name: str
    ec_count: int


class CompareTwoTaxaEnzymes(BaseModelDTO):
    """Function 60: Compare enzyme profiles of two taxa"""
    taxon_1: TaxonInfo
    taxon_2: TaxonInfo
    shared_ec_count: int
    only_taxon1_count: int
    only_taxon2_count: int
    jaccard_similarity: float
    shared_ec_numbers: List[str]
    only_taxon1_ec: List[str]
    only_taxon2_ec: List[str]
