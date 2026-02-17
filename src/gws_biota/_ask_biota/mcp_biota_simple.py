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

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from gws_biota import BTO, Compound, Enzyme, Pathway, Protein, Reaction, Taxonomy
    from gws_biota.go.go import GO


# ============================================================================
# DTOs - Summary types for list results
# ============================================================================


class EnzymeSummary(BaseModel):
    """Summary of an enzyme entry."""

    ec_number: Optional[str] = None
    uniprot_id: Optional[str] = None
    name: Optional[str] = None
    tax_id: Optional[str] = None
    tax_species: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> EnzymeSummary:
        return cls(
            ec_number=getattr(entity, "ec_number", None),
            uniprot_id=getattr(entity, "uniprot_id", None),
            name=getattr(entity, "name", None),
            tax_id=getattr(entity, "tax_id", None),
            tax_species=getattr(entity, "tax_species", None),
        )


class ProteinSummary(BaseModel):
    """Summary of a protein entry."""

    uniprot_id: Optional[str] = None
    uniprot_gene: Optional[str] = None
    tax_id: Optional[str] = None
    evidence_score: Optional[int] = None

    @classmethod
    def from_entity(cls, entity) -> ProteinSummary:
        return cls(
            uniprot_id=getattr(entity, "uniprot_id", None),
            uniprot_gene=getattr(entity, "uniprot_gene", None),
            tax_id=getattr(entity, "tax_id", None),
            evidence_score=getattr(entity, "evidence_score", None),
        )


class CompoundSummary(BaseModel):
    """Summary of a compound entry."""

    chebi_id: Optional[str] = None
    kegg_id: Optional[str] = None
    name: Optional[str] = None
    formula: Optional[str] = None
    mass: Optional[float] = None
    monoisotopic_mass: Optional[float] = None
    charge: Optional[float] = None
    inchi: Optional[str] = None
    inchikey: Optional[str] = None
    smiles: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> CompoundSummary:
        return cls(
            chebi_id=getattr(entity, "chebi_id", None),
            kegg_id=getattr(entity, "kegg_id", None),
            name=getattr(entity, "name", None),
            formula=getattr(entity, "formula", None),
            mass=getattr(entity, "mass", None),
            monoisotopic_mass=getattr(entity, "monoisotopic_mass", None),
            charge=getattr(entity, "charge", None),
            inchi=getattr(entity, "inchi", None),
            inchikey=getattr(entity, "inchikey", None),
            smiles=getattr(entity, "smiles", None),
        )


class ReactionSummary(BaseModel):
    """Summary of a reaction entry."""

    rhea_id: Optional[str] = None
    name: Optional[str] = None
    direction: Optional[str] = None
    kegg_id: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> ReactionSummary:
        return cls(
            rhea_id=getattr(entity, "rhea_id", None),
            name=getattr(entity, "name", None),
            direction=getattr(entity, "direction", None),
            kegg_id=getattr(entity, "kegg_id", None),
        )


class TaxonomySummary(BaseModel):
    """Summary of a taxonomy entry."""

    tax_id: Optional[str] = None
    name: Optional[str] = None
    rank: Optional[str] = None
    division: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> TaxonomySummary:
        return cls(
            tax_id=getattr(entity, "tax_id", None),
            name=getattr(entity, "name", None),
            rank=getattr(entity, "rank", None),
            division=getattr(entity, "division", None),
        )


class PathwaySummary(BaseModel):
    """Summary of a pathway entry."""

    reactome_pathway_id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> PathwaySummary:
        return cls(
            reactome_pathway_id=getattr(entity, "reactome_pathway_id", None),
            name=getattr(entity, "name", None),
        )


class BTOSummary(BaseModel):
    """Summary of a BTO tissue/organ entry."""

    bto_id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> BTOSummary:
        return cls(
            bto_id=getattr(entity, "bto_id", None),
            name=getattr(entity, "name", None),
        )


class GOSummary(BaseModel):
    """Summary of a GO term entry."""

    go_id: Optional[str] = None
    name: Optional[str] = None
    namespace: Optional[str] = None

    @classmethod
    def from_entity(cls, entity) -> GOSummary:
        return cls(
            go_id=getattr(entity, "go_id", None),
            name=getattr(entity, "name", None),
            namespace=getattr(entity, "namespace", None),
        )


# ============================================================================
# DTOs - Result types for list/search functions
# ============================================================================


class EnzymeListResult(BaseModel):
    """Result containing a list of enzymes."""

    enzymes: List[EnzymeSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class ProteinListResult(BaseModel):
    """Result containing a list of proteins."""

    proteins: List[ProteinSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class CompoundListResult(BaseModel):
    """Result containing a list of compounds."""

    compounds: List[CompoundSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class ReactionListResult(BaseModel):
    """Result containing a list of reactions."""

    reactions: List[ReactionSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class TaxonomyListResult(BaseModel):
    """Result containing a list of taxonomy entries."""

    taxonomies: List[TaxonomySummary] = []
    count: int = 0
    total_count: Optional[int] = None


class PathwayListResult(BaseModel):
    """Result containing a list of pathways."""

    pathways: List[PathwaySummary] = []
    count: int = 0
    total_count: Optional[int] = None


class BTOListResult(BaseModel):
    """Result containing a list of BTO entries."""

    tissues: List[BTOSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class GOListResult(BaseModel):
    """Result containing a list of GO terms."""

    go_terms: List[GOSummary] = []
    count: int = 0
    total_count: Optional[int] = None


class ProteinCountResult(BaseModel):
    """Result of protein count by taxon."""

    tax_id: str
    tax_name: str
    total_count: int
    by_evidence_score: Dict[str, int]


class DatabaseStatistics(BaseModel):
    """Database statistics overview."""

    primary_entities: Dict[str, int]
    classification: Dict[str, int]
    ontologies: Dict[str, int]
    junction_tables: Dict[str, int]
    total_entities: int
    total_relationships: int


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

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _init_gws_core()
        return func(*args, **kwargs)

    return wrapper


# ============================================================================
# HELPER FUNCTIONS (kept for backward compatibility with mcp_biota_complex.py)
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
            if hasattr(value, "__dict__") and not isinstance(
                value, (str, int, float, bool, list, dict)
            ):
                value = str(value)
            result[field] = value
    else:
        # Get all fields from model
        for field_name in entity._meta.fields.keys():
            value = getattr(entity, field_name, None)
            if hasattr(value, "__dict__") and not isinstance(
                value, (str, int, float, bool, list, dict)
            ):
                value = str(value)
            result[field_name] = value

    return result


def _entities_to_list(
    entities, fields: List[str] = None, limit: int = None
) -> List[Dict[str, Any]]:
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
def get_enzyme_by_ec_number(ec_number: str) -> Optional[Enzyme]:
    """
    1. Récupère un enzyme par son numéro EC.

    Args:
        ec_number: Numéro EC de l'enzyme (ex: "1.1.1.1")

    Returns:
        L'enzyme correspondant ou None si non trouvé
    """
    from gws_biota import Enzyme

    return Enzyme.get_or_none(Enzyme.ec_number == ec_number)


@_ensure_initialized
def get_enzymes_by_taxon(tax_id: str) -> EnzymeListResult:
    """
    2. Liste les enzymes d'un taxon donné.

    Args:
        tax_id: NCBI Taxonomy ID (ex: "9606" pour Homo sapiens)

    Returns:
        EnzymeListResult avec la liste des enzymes et le compte total
    """
    from gws_biota import Enzyme

    enzymes = list(Enzyme.select().where(Enzyme.tax_id == tax_id))
    total_count = len(enzymes)

    return EnzymeListResult(
        enzymes=[EnzymeSummary.from_entity(e) for e in enzymes],
        count=len(enzymes),
        total_count=total_count,
    )


@_ensure_initialized
def get_enzymes_by_uniprot_id(uniprot_id: str) -> EnzymeListResult:
    """
    3. Récupère les enzymes par UniProt ID.

    Args:
        uniprot_id: UniProt identifier (ex: "P12345")

    Returns:
        EnzymeListResult avec les enzymes correspondants
    """
    from gws_biota import Enzyme

    enzymes = list(Enzyme.select().where(Enzyme.uniprot_id == uniprot_id))

    return EnzymeListResult(
        enzymes=[EnzymeSummary.from_entity(e) for e in enzymes],
        count=len(enzymes),
    )


@_ensure_initialized
def search_enzymes_by_name(query: str) -> EnzymeListResult:
    """
    4. Recherche enzymes par nom (full-text search).

    Args:
        query: Terme de recherche

    Returns:
        EnzymeListResult avec la liste des enzymes correspondants
    """
    from gws_biota import Enzyme

    enzymes = list(Enzyme.select().where(Enzyme.name.contains(query)))

    return EnzymeListResult(
        enzymes=[EnzymeSummary.from_entity(e) for e in enzymes],
        count=len(enzymes),
    )


@_ensure_initialized
def get_enzymes_by_taxonomy_rank(rank: str, value: str) -> EnzymeListResult:
    """
    5. Récupère les enzymes par rang taxonomique.

    Args:
        rank: Rang taxonomique ("species", "genus", "family", "order", "class", "phylum", "kingdom")
        value: Valeur du rang (ex: "Homo sapiens", "Saccharomyces")

    Returns:
        EnzymeListResult avec la liste des enzymes

    Raises:
        ValueError: Si le rang taxonomique est invalide
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
        raise ValueError(f"Invalid rank '{rank}'. Valid ranks: {list(rank_mapping.keys())}")

    field = rank_mapping[rank.lower()]
    enzymes = list(Enzyme.select().where(field == value))
    total_count = len(enzymes)

    return EnzymeListResult(
        enzymes=[EnzymeSummary.from_entity(e) for e in enzymes],
        count=len(enzymes),
        total_count=total_count,
    )


# ============================================================================
# PROTEIN FUNCTIONS (7-11)
# ============================================================================


@_ensure_initialized
def get_protein_by_uniprot_id(uniprot_id: str) -> Optional[Protein]:
    """
    7. Récupère une protéine par UniProt ID.

    Args:
        uniprot_id: UniProt identifier (ex: "P12345")

    Returns:
        La protéine correspondante ou None si non trouvée
    """
    from gws_biota import Protein

    return Protein.get_or_none(Protein.uniprot_id == uniprot_id)


@_ensure_initialized
def get_proteins_by_taxon(tax_id: str) -> ProteinListResult:
    """
    8. Liste les protéines d'un organisme.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        ProteinListResult avec la liste des protéines
    """
    from gws_biota import Protein

    proteins = list(Protein.select().where(Protein.tax_id == tax_id))
    total_count = len(proteins)

    return ProteinListResult(
        proteins=[ProteinSummary.from_entity(p) for p in proteins],
        count=len(proteins),
        total_count=total_count,
    )


@_ensure_initialized
def get_proteins_by_gene_name(gene_name: str) -> ProteinListResult:
    """
    9. Recherche protéines par nom de gène.

    Args:
        gene_name: Nom du gène (ou partie)

    Returns:
        ProteinListResult avec la liste des protéines
    """
    from gws_biota import Protein

    proteins = list(Protein.select().where(Protein.uniprot_gene.contains(gene_name)))

    return ProteinListResult(
        proteins=[ProteinSummary.from_entity(p) for p in proteins],
        count=len(proteins),
    )


@_ensure_initialized
def get_proteins_by_evidence_score(min_score: int, tax_id: str = None) -> ProteinListResult:
    """
    10. Filtre les protéines par score d'évidence (1-5).

    Args:
        min_score: Score minimum (1=best, 5=lowest)
        tax_id: Optionnel - filtrer par taxon

    Returns:
        ProteinListResult avec la liste des protéines
    """
    from gws_biota import Protein

    query = Protein.select().where(Protein.evidence_score <= min_score)

    if tax_id:
        query = query.where(Protein.tax_id == tax_id)

    proteins = list(query)
    total_count = len(proteins)

    return ProteinListResult(
        proteins=[ProteinSummary.from_entity(p) for p in proteins],
        count=len(proteins),
        total_count=total_count,
    )


@_ensure_initialized
def count_proteins_by_taxon(tax_id: str) -> ProteinCountResult:
    """
    11. Compte les protéines par taxon.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        ProteinCountResult avec le compte et les statistiques
    """
    from gws_biota import Protein, Taxonomy

    taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
    tax_name = taxonomy.name if taxonomy else "Unknown"

    total_count = Protein.select().where(Protein.tax_id == tax_id).count()

    # Count by evidence score
    evidence_counts = {}
    for score in range(1, 6):
        count = (
            Protein.select()
            .where((Protein.tax_id == tax_id) & (Protein.evidence_score == score))
            .count()
        )
        evidence_counts[f"score_{score}"] = count

    return ProteinCountResult(
        tax_id=tax_id,
        tax_name=tax_name,
        total_count=total_count,
        by_evidence_score=evidence_counts,
    )


# ============================================================================
# COMPOUND FUNCTIONS (12-16)
# ============================================================================


@_ensure_initialized
def get_compound_by_chebi_id(chebi_id: str) -> Optional[Compound]:
    """
    12. Récupère un composé par ChEBI ID.

    Args:
        chebi_id: ChEBI identifier (ex: "CHEBI:15377")

    Returns:
        Le composé correspondant ou None si non trouvé
    """
    from gws_biota import Compound

    # Normalize ChEBI ID
    if not chebi_id.startswith("CHEBI:"):
        chebi_id = f"CHEBI:{chebi_id}"

    return Compound.get_or_none(Compound.chebi_id == chebi_id)


@_ensure_initialized
def get_compound_by_inchikey(inchikey: str) -> Optional[Compound]:
    """
    13. Récupère un composé par InChIKey.

    Args:
        inchikey: InChIKey identifier

    Returns:
        Le composé correspondant ou None si non trouvé
    """
    from gws_biota import Compound

    return Compound.get_or_none(Compound.inchikey == inchikey)


@_ensure_initialized
def search_compounds_by_name(query: str) -> CompoundListResult:
    """
    14. Recherche composés par nom.

    Args:
        query: Terme de recherche

    Returns:
        CompoundListResult avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(Compound.select().where(Compound.name.contains(query)))

    return CompoundListResult(
        compounds=[CompoundSummary.from_entity(c) for c in compounds],
        count=len(compounds),
    )


@_ensure_initialized
def get_compounds_by_formula(formula: str) -> CompoundListResult:
    """
    15. Recherche par formule chimique.

    Args:
        formula: Formule chimique (ex: "C6H12O6")

    Returns:
        CompoundListResult avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(Compound.select().where(Compound.formula == formula))

    return CompoundListResult(
        compounds=[CompoundSummary.from_entity(c) for c in compounds],
        count=len(compounds),
    )


@_ensure_initialized
def get_compounds_by_mass_range(min_mass: float, max_mass: float) -> CompoundListResult:
    """
    16. Composés dans une plage de masse.

    Args:
        min_mass: Masse minimale (Da)
        max_mass: Masse maximale (Da)

    Returns:
        CompoundListResult avec la liste des composés
    """
    from gws_biota import Compound

    compounds = list(
        Compound.select()
        .where((Compound.mass >= min_mass) & (Compound.mass <= max_mass))
        .order_by(Compound.mass)
    )

    total_count = len(compounds)

    return CompoundListResult(
        compounds=[CompoundSummary.from_entity(c) for c in compounds],
        count=len(compounds),
        total_count=total_count,
    )


# ============================================================================
# REACTION FUNCTIONS (17-19)
# ============================================================================


@_ensure_initialized
def get_reaction_by_rhea_id(rhea_id: str) -> Optional[Reaction]:
    """
    17. Récupère une réaction par Rhea ID.

    Args:
        rhea_id: Rhea identifier (ex: "RHEA:10000")

    Returns:
        La réaction correspondante ou None si non trouvée.
        Accéder aux substrats, produits et enzymes via les propriétés
        reaction.substrates, reaction.products, reaction.enzymes
    """
    from gws_biota import Reaction

    # Normalize Rhea ID
    if not rhea_id.startswith("RHEA:"):
        rhea_id = f"RHEA:{rhea_id}"

    return Reaction.get_or_none(Reaction.rhea_id == rhea_id)


@_ensure_initialized
def get_reactions_by_ec_number(ec_number: str) -> ReactionListResult:
    """
    18. Réactions catalysées par un EC.

    Args:
        ec_number: Numéro EC de l'enzyme

    Returns:
        ReactionListResult avec la liste des réactions
    """
    from gws_biota import Reaction

    reactions = list(Reaction.search_by_ec_numbers(ec_number))

    return ReactionListResult(
        reactions=[ReactionSummary.from_entity(r) for r in reactions],
        count=len(reactions),
    )


@_ensure_initialized
def get_reactions_by_taxon(tax_id: str) -> ReactionListResult:
    """
    19. Réactions associées à un taxon.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        ReactionListResult avec la liste des réactions
    """
    from gws_biota import Reaction

    reactions = list(Reaction.search_by_tax_ids(tax_id))

    return ReactionListResult(
        reactions=[ReactionSummary.from_entity(r) for r in reactions],
        count=len(reactions),
    )


# ============================================================================
# TAXONOMY FUNCTIONS (22-23, 25)
# ============================================================================


@_ensure_initialized
def get_taxonomy_by_id(tax_id: str) -> Optional[Taxonomy]:
    """
    22. Récupère un taxon par ID.

    Args:
        tax_id: NCBI Taxonomy ID

    Returns:
        Le taxon correspondant ou None si non trouvé
    """
    from gws_biota import Taxonomy

    return Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)


@_ensure_initialized
def search_taxonomy_by_name(query: str) -> TaxonomyListResult:
    """
    23. Recherche taxons par nom scientifique.

    Args:
        query: Terme de recherche

    Returns:
        TaxonomyListResult avec la liste des taxons
    """
    from gws_biota import Taxonomy

    taxonomies = list(Taxonomy.select().where(Taxonomy.name.contains(query)))

    return TaxonomyListResult(
        taxonomies=[TaxonomySummary.from_entity(t) for t in taxonomies],
        count=len(taxonomies),
    )


@_ensure_initialized
def get_taxonomy_children(tax_id: str, rank: str = None) -> TaxonomyListResult:
    """
    25. Récupère les taxons enfants.

    Args:
        tax_id: NCBI Taxonomy ID du parent
        rank: Optionnel - filtrer par rang

    Returns:
        TaxonomyListResult avec la liste des enfants
    """
    from gws_biota import Taxonomy

    query = Taxonomy.select().where(Taxonomy.ancestor_tax_id == tax_id)

    if rank:
        query = query.where(Taxonomy.rank == rank)

    children = list(query)
    total_count = len(children)

    return TaxonomyListResult(
        taxonomies=[TaxonomySummary.from_entity(t) for t in children],
        count=len(children),
        total_count=total_count,
    )


# ============================================================================
# PATHWAY FUNCTIONS (26, 28)
# ============================================================================


@_ensure_initialized
def get_pathway_by_reactome_id(reactome_id: str) -> Optional[Pathway]:
    """
    26. Récupère un pathway par Reactome ID.

    Args:
        reactome_id: Reactome pathway identifier (ex: "R-HSA-109582")

    Returns:
        Le pathway correspondant ou None si non trouvé
    """
    from gws_biota import Pathway

    return Pathway.get_or_none(Pathway.reactome_pathway_id == reactome_id)


@_ensure_initialized
def search_pathways_by_name(query: str) -> PathwayListResult:
    """
    28. Recherche pathways par nom.

    Args:
        query: Terme de recherche

    Returns:
        PathwayListResult avec la liste des pathways
    """
    from gws_biota import Pathway

    pathways = list(Pathway.select().where(Pathway.name.contains(query)))

    return PathwayListResult(
        pathways=[PathwaySummary.from_entity(p) for p in pathways],
        count=len(pathways),
    )


# ============================================================================
# BTO / GO / OTHER SIMPLE LOOKUPS (61-62, 64-66, 68-70)
# ============================================================================


@_ensure_initialized
def get_bto_by_id(bto_id: str) -> Optional[BTO]:
    """
    61. Récupère un tissu/organe par BTO ID.

    Args:
        bto_id: BTO identifier (ex: "BTO_0000142" pour brain)

    Returns:
        Le terme BTO correspondant ou None si non trouvé
    """
    from gws_biota import BTO

    return BTO.get_or_none(BTO.bto_id == bto_id)


@_ensure_initialized
def search_bto_by_name(query: str) -> BTOListResult:
    """
    62. Recherche tissus/organes par nom dans BTO.

    Args:
        query: Terme de recherche (ex: "liver", "brain", "blood")

    Returns:
        BTOListResult avec la liste des tissus correspondants
    """
    from gws_biota import BTO

    btos = list(BTO.select().where(BTO.name.contains(query)))

    return BTOListResult(
        tissues=[BTOSummary.from_entity(b) for b in btos],
        count=len(btos),
    )


@_ensure_initialized
def get_go_by_id(go_id: str) -> Optional[GO]:
    """
    64. Récupère un terme GO par son identifiant.

    Args:
        go_id: GO identifier (ex: "GO:0008150")

    Returns:
        Le terme GO correspondant ou None si non trouvé
    """
    from gws_biota.go.go import GO

    if not go_id.startswith("GO:"):
        go_id = f"GO:{go_id}"

    return GO.get_or_none(GO.go_id == go_id)


@_ensure_initialized
def search_go_by_name(query: str, namespace: str = None) -> GOListResult:
    """
    65. Recherche termes GO par nom, optionnellement filtré par namespace.

    Args:
        query: Terme de recherche
        namespace: Optionnel - "molecular_function", "biological_process", "cellular_component"

    Returns:
        GOListResult avec la liste des termes GO
    """
    from gws_biota.go.go import GO

    q = GO.select().where(GO.name.contains(query))
    if namespace:
        q = q.where(GO.namespace == namespace)

    go_terms = list(q)

    return GOListResult(
        go_terms=[GOSummary.from_entity(g) for g in go_terms],
        count=len(go_terms),
    )


@_ensure_initialized
def get_pathways_by_species(species: str) -> PathwayListResult:
    """
    66. Récupère les pathways pour une espèce donnée.

    Args:
        species: Nom de l'espèce (ex: "Homo sapiens", "Mus musculus")

    Returns:
        PathwayListResult avec la liste des pathways pour cette espèce
    """
    from gws_biota import Pathway, PathwayCompound

    # Get unique pathway IDs for this species
    pc_links = list(
        PathwayCompound.select(PathwayCompound.reactome_pathway_id)
        .where(PathwayCompound.species == species)
        .distinct()
    )

    pathways = []
    seen = set()
    for pc in pc_links:
        pid = pc.reactome_pathway_id
        if pid in seen:
            continue
        seen.add(pid)

        pw = Pathway.get_or_none(Pathway.reactome_pathway_id == pid)
        if pw:
            pathways.append(PathwaySummary.from_entity(pw))

    return PathwayListResult(
        pathways=pathways,
        count=len(pathways),
    )


@_ensure_initialized
def get_compound_by_kegg_id(kegg_id: str) -> Optional[Compound]:
    """
    68. Récupère un composé par KEGG ID.

    Args:
        kegg_id: KEGG compound identifier (ex: "C00001")

    Returns:
        Le composé correspondant ou None si non trouvé
    """
    from gws_biota import Compound

    return Compound.get_or_none(Compound.kegg_id == kegg_id)


@_ensure_initialized
def get_reaction_by_kegg_id(kegg_id: str) -> Optional[Reaction]:
    """
    69. Récupère une réaction par KEGG reaction ID.

    Args:
        kegg_id: KEGG reaction identifier (ex: "R00001")

    Returns:
        La réaction correspondante ou None si non trouvée.
        Accéder aux substrats, produits et enzymes via les propriétés
        reaction.substrates, reaction.products, reaction.enzymes
    """
    from gws_biota import Reaction

    return Reaction.get_or_none(Reaction.kegg_id == kegg_id)


@_ensure_initialized
def get_database_statistics() -> DatabaseStatistics:
    """
    70. Vue d'ensemble de la base de données Biota: nombre d'entités par table.

    Returns:
        DatabaseStatistics avec les statistiques globales de la base
    """
    from gws_biota import (
        BTO,
        Compound,
        DeprecatedEnzyme,
        Enzyme,
        EnzymeClass,
        EnzymeOrtholog,
        Pathway,
        PathwayCompound,
        Protein,
        Reaction,
        Taxonomy,
    )
    from gws_biota.enzyme.enzyme import EnzymeBTO
    from gws_biota.go.go import GO
    from gws_biota.reaction.reaction import ReactionEnzyme, ReactionProduct, ReactionSubstrate

    primary = {
        "enzymes": Enzyme.select().count(),
        "proteins": Protein.select().count(),
        "compounds": Compound.select().count(),
        "reactions": Reaction.select().count(),
        "taxonomies": Taxonomy.select().count(),
        "pathways": Pathway.select().count(),
    }

    classification = {
        "enzyme_classes": EnzymeClass.select().count(),
        "enzyme_orthologs": EnzymeOrtholog.select().count(),
        "deprecated_enzymes": DeprecatedEnzyme.select().count(),
    }

    ontologies = {
        "go_terms": GO.select().count(),
        "bto_tissues": BTO.select().count(),
    }

    junctions = {
        "reaction_substrates": ReactionSubstrate.select().count(),
        "reaction_products": ReactionProduct.select().count(),
        "reaction_enzymes": ReactionEnzyme.select().count(),
        "enzyme_bto_links": EnzymeBTO.select().count(),
        "pathway_compounds": PathwayCompound.select().count(),
    }

    return DatabaseStatistics(
        primary_entities=primary,
        classification=classification,
        ontologies=ontologies,
        junction_tables=junctions,
        total_entities=sum(primary.values()),
        total_relationships=sum(junctions.values()),
    )
