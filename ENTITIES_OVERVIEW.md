# GWS Biota - Peewee Entities Overview

This document provides an overview of all Peewee entities in the `gws_biota` project, their columns, and relationships.

## Table of Contents

- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Base Classes](#base-classes)
- [Primary Entities](#primary-entities)
  - [Compound](#compound)
  - [Enzyme](#enzyme)
  - [Reaction](#reaction)
  - [Protein](#protein)
  - [Pathway](#pathway)
  - [Taxonomy](#taxonomy)
  - [Organism](#organism)
  - [Unicell](#unicell)
  - [BiomassReaction](#biomassreaction)
- [Ontology Entities](#ontology-entities)
  - [GO (Gene Ontology)](#go-gene-ontology)
  - [SBO (Systems Biology Ontology)](#sbo-systems-biology-ontology)
  - [ECO (Evidence and Conclusion Ontology)](#eco-evidence-and-conclusion-ontology)
  - [BTO (BRENDA Tissue Ontology)](#bto-brenda-tissue-ontology)
- [Junction Tables](#junction-tables)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CORE ENTITIES                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   Compound   │
                                    │──────────────│
                                    │ chebi_id     │
                                    │ kegg_id      │
                                    │ formula      │
                                    │ mass         │
                                    │ inchikey     │
                                    └──────┬───────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │ReactionSubstrate│         │ ReactionProduct │         │CompoundAncestor │
    └────────┬────────┘         └────────┬────────┘         └─────────────────┘
             │                           │                        (self-ref)
             └───────────┬───────────────┘
                         ▼
                  ┌──────────────┐
                  │   Reaction   │◄────────────────┐
                  │──────────────│                 │
                  │ rhea_id      │         ┌──────┴────────┐
                  │ kegg_id      │         │ReactionEnzyme │
                  │ direction    │         └──────┬────────┘
                  └──────────────┘                │
                                                  ▼
                                          ┌──────────────┐
                                          │    Enzyme    │
                                          │──────────────│
                                          │ ec_number    │
                                          │ uniprot_id   │◄─────┐
                                          │ tax_id       │      │
                                          └──────┬───────┘      │
                                                 │              │
                    ┌────────────────────────────┼──────────────┤
                    │                            │              │
                    ▼                            ▼              │
           ┌──────────────┐            ┌──────────────┐  ┌──────┴───────┐
           │  EnzymeBTO   │            │ EnzymeClass  │  │   Protein    │
           └──────┬───────┘            │──────────────│  │──────────────│
                  │                    │ ec_number    │  │ uniprot_id   │
                  ▼                    └──────────────┘  │ uniprot_gene │
           ┌──────────────┐                              └──────────────┘
           │     BTO      │
           │──────────────│
           │ bto_id       │
           └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  PATHWAY & TAXONOMY                                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
    │   Pathway    │◄───────►│ PathwayCompound  │         │   Taxonomy   │
    │──────────────│         │──────────────────│         │──────────────│
    │ reactome_id  │         │ reactome_id      │         │ tax_id       │
    └──────┬───────┘         │ chebi_id         │         │ rank         │
           │                 └──────────────────┘         │ division     │
           ▼                                              └──────┬───────┘
    ┌──────────────────┐                                         │
    │ PathwayAncestor  │                                         ▼
    └──────────────────┘                                  ┌──────────────┐
        (self-ref)                                        │   Organism   │
                                                          │──────────────│
                                                          │ taxonomy FK  │
                                                          └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ONTOLOGIES                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │      GO      │    │     SBO      │    │     ECO      │    │     BTO      │
    │──────────────│    │──────────────│    │──────────────│    │──────────────│
    │ go_id        │    │ sbo_id       │    │ eco_id       │    │ bto_id       │
    │ namespace    │    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
    └──────┬───────┘           │                   │                   │
           │                   ▼                   ▼                   ▼
           ▼            ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    ┌─────────────┐     │ SBOAncestor │     │ ECOAncestor │     │ BTOAncestor │
    │ GOAncestor  │     └─────────────┘     └─────────────┘     └─────────────┘
    └─────────────┘       (self-ref)          (self-ref)          (self-ref)
      (self-ref)
```

---

## Base Classes

These abstract base classes are not directly queryable but provide common fields to child entities.

### ProtectedBaseModel
- **Table**: N/A (abstract)
- **Description**: Base model that prevents database modifications in production/notebook environments

### Base
- **Table**: N/A (abstract)
- **Description**: Base model with common fields and full-text search support

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `name` | CharField | Yes | Yes | Entity name |
| `data` | JSONField | No | No | Additional JSON data |

### BaseFT
- **Table**: N/A (abstract)
- **Description**: Full-text searchable base model for ontology terms

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `ft_names` | TextField | Yes | No | Full-text searchable names |
| + inherited from Base |

### Ontology
- **Table**: `biota_ontology`
- **Description**: Base ontology class for all ontology terms
- **Inherits**: All fields from BaseFT

---

## Primary Entities

### Compound
- **Table**: `biota_compound`
- **Source**: ChEBI (Chemical Entities of Biological Interest)
- **Description**: Chemical compounds and metabolites

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `chebi_id` | CharField | Yes | Yes | ChEBI identifier |
| `kegg_id` | CharField | Yes | Yes | KEGG compound ID |
| `metacyc_id` | CharField | Yes | Yes | MetaCyc compound ID |
| `formula` | CharField | Yes | Yes | Chemical formula |
| `charge` | FloatField | Yes | Yes | Molecular charge |
| `mass` | DoubleField | Yes | Yes | Molecular mass |
| `monoisotopic_mass` | DoubleField | Yes | Yes | Monoisotopic mass |
| `inchi` | CharField | Yes | Yes | InChI string |
| `inchikey` | CharField | Yes | Yes | InChIKey |
| `smiles` | CharField | Yes | Yes | SMILES notation |
| `chebi_star` | CharField | Yes | Yes | ChEBI star rating |
| + inherited from BaseFT |

**Relationships**:
- `ancestors` → CompoundAncestor (self-referential many-to-many)

**Example Query**:
```python
from gws_biota.compound.compound import Compound

# Find compound by ChEBI ID
compound = Compound.get_or_none(Compound.chebi_id == "CHEBI:15377")

# Search by name
compounds = Compound.select().where(Compound.name.contains("glucose"))

# Get by InChIKey
compound = Compound.get_or_none(Compound.inchikey == "WQZGKKKJIJFFOK-GASJEMHNSA-N")
```

---

### Enzyme
- **Table**: `biota_enzymes`
- **Source**: BRENDA, BKMS, UniProt
- **Description**: Enzyme entities with EC classification and taxonomic information

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `ec_number` | CharField | Yes | Yes | EC classification number |
| `uniprot_id` | CharField | Yes | Yes | UniProt identifier |
| `tax_superkingdom` | CharField | Yes | Yes | Taxonomic superkingdom |
| `tax_clade` | CharField | Yes | Yes | Taxonomic clade |
| `tax_kingdom` | CharField | Yes | Yes | Taxonomic kingdom |
| `tax_subkingdom` | CharField | Yes | Yes | Taxonomic subkingdom |
| `tax_class` | CharField | Yes | Yes | Taxonomic class |
| `tax_phylum` | CharField | Yes | Yes | Taxonomic phylum |
| `tax_subphylum` | CharField | Yes | Yes | Taxonomic subphylum |
| `tax_order` | CharField | Yes | Yes | Taxonomic order |
| `tax_genus` | CharField | Yes | Yes | Taxonomic genus |
| `tax_family` | CharField | Yes | Yes | Taxonomic family |
| `tax_species` | CharField | Yes | Yes | Taxonomic species |
| `tax_id` | CharField | Yes | Yes | NCBI taxonomy ID |
| + inherited from BaseFT |

**Relationships**:
- `bto` → BTO via EnzymeBTO (many-to-many)
- `reactions` → Reaction via ReactionEnzyme (many-to-many)

**Example Query**:
```python
from gws_biota.enzyme.enzyme import Enzyme

# Find enzyme by EC number
enzyme = Enzyme.get_or_none(Enzyme.ec_number == "1.1.1.1")

# Find enzymes from specific organism
enzymes = Enzyme.select().where(Enzyme.tax_species == "Homo sapiens")
```

---

### EnzymeClass
- **Table**: `biota_enzyme_class`
- **Description**: EC enzyme classification hierarchy

| Column | Type | Nullable | Indexed | Unique | Description |
|--------|------|----------|---------|--------|-------------|
| `ec_number` | CharField | Yes | Yes | Yes | EC classification number |
| + inherited from Base |

---

### EnzymeOrtholog
- **Table**: `biota_enzo`
- **Description**: Enzyme orthologs with pathway information

| Column | Type | Nullable | Indexed | Unique | Description |
|--------|------|----------|---------|--------|-------------|
| `ec_number` | CharField | Yes | Yes | Yes | EC classification number |
| `pathway` | ForeignKey | Yes | Yes | No | Reference to EnzymePathway |
| + inherited from BaseFT |

---

### EnzymePathway
- **Table**: `biota_enzyme_pathway`
- **Description**: Pathway information for enzymes

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `ec_number` | CharField | Yes | Yes | EC classification number |
| + inherited from Base |

---

### DeprecatedEnzyme
- **Table**: `biota_deprecated_enzymes`
- **Description**: Maps deprecated EC numbers to current replacements

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `ec_number` | CharField | Yes | Yes | Old/deprecated EC number |
| `new_ec_number` | CharField | Yes | Yes | New/current EC number |
| + inherited from Base |

---

### Reaction
- **Table**: `biota_reaction`
- **Source**: Rhea database
- **Description**: Metabolic reactions with substrates, products, and enzymes

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `rhea_id` | CharField | Yes | Yes | Rhea reaction ID |
| `master_id` | CharField | Yes | Yes | Master Rhea ID |
| `direction` | CharField | Yes | Yes | Reaction direction (LR, RL, BI) |
| `biocyc_ids` | CharField | Yes | Yes | BioCyc IDs |
| `metacyc_id` | CharField | Yes | Yes | MetaCyc reaction ID |
| `kegg_id` | CharField | Yes | Yes | KEGG reaction ID |
| `sabio_rk_id` | CharField | Yes | Yes | SABIO-RK ID |
| `ft_tax_ids` | TextField | Yes | No | Full-text taxonomy IDs |
| `ft_ec_numbers` | TextField | Yes | No | Full-text EC numbers |
| + inherited from BaseFT |

**Relationships**:
- `substrates` → Compound via ReactionSubstrate (many-to-many)
- `products` → Compound via ReactionProduct (many-to-many)
- `enzymes` → Enzyme via ReactionEnzyme (many-to-many)

**Example Query**:
```python
from gws_biota.reaction.reaction import Reaction

# Find reaction by Rhea ID
reaction = Reaction.get_or_none(Reaction.rhea_id == "RHEA:10000")

# Get substrates for a reaction
substrates = reaction.substrates

# Get products for a reaction
products = reaction.products
```

---

### Protein
- **Table**: `biota_protein`
- **Source**: UniProt
- **Description**: Gene/protein entities

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `uniprot_id` | TextField | Yes | Yes | UniProt accession |
| `uniprot_db` | CharField | No | No | UniProt database (Swiss-Prot/TrEMBL) |
| `uniprot_gene` | CharField | Yes | Yes | Gene name |
| `evidence_score` | IntegerField | Yes | Yes | Evidence score (1-5) |
| `tax_id` | CharField | Yes | Yes | NCBI taxonomy ID |
| + inherited from Base |

**Example Query**:
```python
from gws_biota.protein.protein import Protein

# Find protein by UniProt ID
protein = Protein.get_or_none(Protein.uniprot_id == "P12345")

# Find proteins from specific organism
proteins = Protein.select().where(Protein.tax_id == "9606")
```

---

### Pathway
- **Table**: `biota_pathways`
- **Source**: Reactome
- **Description**: Biological pathways

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `reactome_pathway_id` | CharField | Yes | Yes | Reactome pathway identifier |
| + inherited from Ontology |

**Relationships**:
- `ancestors` → Pathway via PathwayAncestor (self-referential many-to-many)

**Example Query**:
```python
from gws_biota.pathway.pathway import Pathway

# Find pathway by Reactome ID
pathway = Pathway.get_or_none(Pathway.reactome_pathway_id == "R-HSA-109582")
```

---

### PathwayCompound
- **Table**: `biota_pathway_compounds`
- **Description**: Links pathways to their compound participants

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `reactome_pathway_id` | CharField | Yes | Yes | Reactome pathway ID |
| `chebi_id` | CharField | Yes | Yes | ChEBI compound ID |
| `species` | CharField | Yes | Yes | Species (e.g., "Homo sapiens") |
| + inherited from Base |

---

### Taxonomy
- **Table**: `biota_taxonomy`
- **Source**: NCBI Taxonomy
- **Description**: Taxonomic classification terms

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `tax_id` | CharField | Yes | Yes | NCBI taxonomy ID |
| `rank` | CharField | Yes | Yes | Taxonomic rank (species, genus, etc.) |
| `division` | CharField | Yes | Yes | Division code |
| `name` | CharField | Yes | Yes | Scientific name |
| `ancestor_tax_id` | CharField | Yes | Yes | Parent taxonomy ID |
| + inherited from Ontology |

**Example Query**:
```python
from gws_biota.taxonomy.taxonomy import Taxonomy

# Find by taxonomy ID
taxonomy = Taxonomy.get_or_none(Taxonomy.tax_id == "9606")  # Homo sapiens

# Find by rank
species = Taxonomy.select().where(Taxonomy.rank == "species")
```

---

### Organism
- **Table**: `biota_organism`
- **Description**: Living organisms with taxonomic classification

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `name` | CharField | Yes | Yes | Organism name |
| `taxonomy` | ForeignKey | Yes | Yes | Reference to Taxonomy |
| + inherited from Base |

**Relationships**:
- `taxonomy` → Taxonomy (foreign key)

---

### Unicell
- **Table**: `biota_unicell`
- **Description**: Universal cell metabolic network model

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `compound_id_list` | BlobField | Yes | No | Pickled list of compound IDs |
| `reaction_id_list` | BlobField | Yes | No | Pickled list of reaction IDs |
| `compound_x_list` | BlobField | Yes | No | Pickled X coordinates |
| `compound_y_list` | BlobField | Yes | No | Pickled Y coordinates |
| `rhea_edge_map` | BlobField | Yes | No | Pickled edge mapping |
| `graph` | BlobField | Yes | No | Pickled NetworkX graph |
| + inherited from BaseFT |

---

### BiomassReaction
- **Table**: `biota_biomass_reaction`
- **Description**: Biomass reactions from metabolic models

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `biomass_rxn_id` | CharField | Yes | Yes | Biomass reaction identifier |
| + inherited from BaseFT |

---

## Ontology Entities

### GO (Gene Ontology)
- **Table**: `biota_go`
- **Source**: Gene Ontology Consortium
- **Description**: Gene Ontology terms (molecular function, biological process, cellular component)

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `go_id` | CharField | Yes | Yes | GO identifier (GO:XXXXXXX) |
| `namespace` | CharField | Yes | Yes | Namespace (MF, BP, CC) |
| + inherited from Ontology |

**Relationships**:
- `ancestors` → GO via GOAncestor (self-referential many-to-many)

**Example Query**:
```python
from gws_biota.go.go import GO

# Find GO term by ID
go_term = GO.get_or_none(GO.go_id == "GO:0008150")

# Find all biological process terms
bp_terms = GO.select().where(GO.namespace == "biological_process")
```

---

### SBO (Systems Biology Ontology)
- **Table**: `biota_sbo`
- **Description**: Systems Biology Ontology terms for computational modeling

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `sbo_id` | CharField | Yes | Yes | SBO identifier |
| + inherited from Ontology |

**Relationships**:
- `ancestors` → SBO via SBOAncestor (self-referential many-to-many)

---

### ECO (Evidence and Conclusion Ontology)
- **Table**: `biota_eco`
- **Description**: Evidence ontology terms for biocuration

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `eco_id` | CharField | Yes | Yes | ECO identifier |
| + inherited from Ontology |

**Relationships**:
- `ancestors` → ECO via ECOAncestor (self-referential many-to-many)

---

### BTO (BRENDA Tissue Ontology)
- **Table**: `biota_bto`
- **Source**: BRENDA
- **Description**: Tissue/organ ontology for enzyme sources

| Column | Type | Nullable | Indexed | Description |
|--------|------|----------|---------|-------------|
| `bto_id` | CharField | Yes | Yes | BTO identifier |
| + inherited from Ontology |

**Relationships**:
- `ancestors` → BTO via BTOAncestor (self-referential many-to-many)
- `enzymes` → Enzyme via EnzymeBTO (many-to-many)

---

## Junction Tables

These tables handle many-to-many relationships between entities.

### CompoundAncestor
- **Table**: `biota_compound_ancestors`
- **Description**: Compound hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `compound` | ForeignKey | Reference to child Compound |
| `ancestor` | ForeignKey | Reference to ancestor Compound |

**Unique constraint**: (compound, ancestor)

---

### ReactionSubstrate
- **Table**: `biota_reaction_substrates`
- **Description**: Links reactions to substrate compounds

| Column | Type | Description |
|--------|------|-------------|
| `compound` | ForeignKey | Reference to Compound |
| `reaction` | ForeignKey | Reference to Reaction |

---

### ReactionProduct
- **Table**: `biota_reaction_products`
- **Description**: Links reactions to product compounds

| Column | Type | Description |
|--------|------|-------------|
| `compound` | ForeignKey | Reference to Compound |
| `reaction` | ForeignKey | Reference to Reaction |

---

### ReactionEnzyme
- **Table**: `biota_reaction_enzymes`
- **Description**: Links reactions to enzymes

| Column | Type | Description |
|--------|------|-------------|
| `enzyme` | ForeignKey | Reference to Enzyme |
| `reaction` | ForeignKey | Reference to Reaction |

---

### EnzymeBTO
- **Table**: `biota_enzyme_btos`
- **Description**: Links enzymes to tissue/organ sources

| Column | Type | Description |
|--------|------|-------------|
| `enzyme` | ForeignKey | Reference to Enzyme |
| `bto` | ForeignKey | Reference to BTO |

---

### PathwayAncestor
- **Table**: `biota_pathway_ancestors`
- **Description**: Pathway hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `pathway` | ForeignKey | Reference to child Pathway |
| `ancestor` | ForeignKey | Reference to ancestor Pathway |

**Unique constraint**: (pathway, ancestor)

---

### GOAncestor
- **Table**: `biota_go_ancestors`
- **Description**: GO term hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `go` | ForeignKey | Reference to child GO term |
| `ancestor` | ForeignKey | Reference to ancestor GO term |

**Unique constraint**: (go, ancestor)

---

### SBOAncestor
- **Table**: `biota_sbo_ancestors`
- **Description**: SBO term hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `sbo` | ForeignKey | Reference to child SBO term |
| `ancestor` | ForeignKey | Reference to ancestor SBO term |

**Unique constraint**: (sbo, ancestor)

---

### ECOAncestor
- **Table**: `biota_eco_ancestors`
- **Description**: ECO term hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `eco` | ForeignKey | Reference to child ECO term |
| `ancestor` | ForeignKey | Reference to ancestor ECO term |

**Unique constraint**: (eco, ancestor)

---

### BTOAncestor
- **Table**: `biota_bto_ancestors`
- **Description**: BTO term hierarchy relationships

| Column | Type | Description |
|--------|------|-------------|
| `bto` | ForeignKey | Reference to child BTO term |
| `ancestor` | ForeignKey | Reference to ancestor BTO term |

**Unique constraint**: (bto, ancestor)

---

## Summary

| Category | Count | Tables |
|----------|-------|--------|
| Base Classes | 4 | (abstract, not queryable) |
| Primary Entities | 12 | Compound, Enzyme, EnzymeClass, EnzymeOrtholog, EnzymePathway, DeprecatedEnzyme, Reaction, Protein, Pathway, PathwayCompound, Taxonomy, Organism, Unicell, BiomassReaction |
| Ontology Entities | 4 | GO, SBO, ECO, BTO |
| Junction Tables | 9 | CompoundAncestor, ReactionSubstrate, ReactionProduct, ReactionEnzyme, EnzymeBTO, PathwayAncestor, GOAncestor, SBOAncestor, ECOAncestor, BTOAncestor |
| **Total** | **29** | |

## Import Paths

Import all from `gws_biota` as follows:

```python
# Compounds
from gws_biota import Compound, CompoundAncestor
```
