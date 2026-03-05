"""
Biota Database Tools
====================

Pure database functions extracted from mcp_biota_v3.py (no MCP dependency).
Provides 4 tools:
    1. get_schema           - Returns database schema
    2. query                - Execute a read-only SQL SELECT (limit 10, max 20 rows)
    3. export_to_csv        - Execute a SQL SELECT and write results to CSV
    4. get_database_statistics - Database overview with entity counts
"""

import csv
import os
import re
import time
from typing import Optional

from gws_core import Settings

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

DATABASE_SCHEMA = """
## Biota Database Schema (MariaDB)

All tables use an auto-increment `id` INTEGER PRIMARY KEY.
Inherited fields from base classes are listed once and apply to all tables that inherit them.

### Base Fields (present in most tables)
- `id` INTEGER PRIMARY KEY AUTO_INCREMENT
- `name` VARCHAR (nullable, indexed) - entity name
- `data` JSON (default {}) - additional metadata

### BaseFT Fields (adds full-text search, inherits Base)
- `ft_names` TEXT (nullable) - full-text searchable names

### Ontology Fields (inherits BaseFT)
- Same as BaseFT (name, data, ft_names)

---

### PRIMARY ENTITIES

**biota_compound** (inherits BaseFT)
- `chebi_id` VARCHAR (nullable, indexed) - ChEBI identifier, e.g. "CHEBI:15377"
- `kegg_id` VARCHAR (nullable, indexed) - KEGG compound ID, e.g. "C00001"
- `metacyc_id` VARCHAR (nullable, indexed)
- `formula` VARCHAR (nullable, indexed) - chemical formula, e.g. "C6H12O6"
- `charge` FLOAT (nullable, indexed)
- `mass` DOUBLE (nullable, indexed) - molecular mass in Da
- `monoisotopic_mass` DOUBLE (nullable, indexed)
- `inchi` VARCHAR (nullable, indexed)
- `inchikey` VARCHAR (nullable, indexed)
- `smiles` VARCHAR (nullable, indexed)
- `chebi_star` VARCHAR (nullable, indexed)

**biota_enzymes** (inherits BaseFT)
- `ec_number` VARCHAR (nullable, indexed) - EC classification, e.g. "1.1.1.1"
- `uniprot_id` VARCHAR (nullable, indexed) - UniProt accession, e.g. "P12345"
- `tax_id` VARCHAR (nullable, indexed) - NCBI taxonomy ID, e.g. "9606"
- `tax_species` VARCHAR (nullable, indexed) - e.g. "Homo sapiens"
- `tax_genus` VARCHAR (nullable, indexed)
- `tax_family` VARCHAR (nullable, indexed)
- `tax_order` VARCHAR (nullable, indexed)
- `tax_class` VARCHAR (nullable, indexed)
- `tax_phylum` VARCHAR (nullable, indexed)
- `tax_subphylum` VARCHAR (nullable, indexed)
- `tax_kingdom` VARCHAR (nullable, indexed)
- `tax_subkingdom` VARCHAR (nullable, indexed)
- `tax_clade` VARCHAR (nullable, indexed)
- `tax_superkingdom` VARCHAR (nullable, indexed)

**biota_reaction** (inherits BaseFT)
- `rhea_id` VARCHAR (nullable, indexed) - Rhea identifier, e.g. "RHEA:10000"
- `master_id` VARCHAR (nullable, indexed)
- `direction` VARCHAR (nullable, indexed) - LR, RL, BI, or UN
- `kegg_id` VARCHAR (nullable, indexed) - KEGG reaction ID, e.g. "R00001"
- `metacyc_id` VARCHAR (nullable, indexed)
- `biocyc_ids` VARCHAR (nullable, indexed)
- `sabio_rk_id` VARCHAR (nullable, indexed)
- `ft_tax_ids` TEXT (nullable) - full-text taxonomy IDs
- `ft_ec_numbers` TEXT (nullable) - full-text EC numbers

**biota_protein** (inherits Base)
- `uniprot_id` TEXT (nullable, indexed) - UniProt accession
- `uniprot_db` VARCHAR (not null) - "sp" (Swiss-Prot) or "tr" (TrEMBL)
- `uniprot_gene` VARCHAR (nullable, indexed) - gene name
- `evidence_score` INTEGER (nullable, indexed) - 1 (best) to 5 (lowest)
- `tax_id` VARCHAR (nullable, indexed) - NCBI taxonomy ID

**biota_pathways** (inherits Ontology)
- `reactome_pathway_id` VARCHAR (nullable, indexed) - e.g. "R-HSA-109582"

**biota_taxonomy** (inherits Ontology)
- `tax_id` VARCHAR (nullable, indexed) - NCBI taxonomy ID
- `rank` VARCHAR (nullable, indexed) - species, genus, family, order, class, phylum, kingdom, superkingdom
- `division` VARCHAR (nullable, indexed)
- `ancestor_tax_id` VARCHAR (nullable, indexed) - parent taxon ID (for tree traversal)

---

### CLASSIFICATION & ENZYME TABLES

**biota_enzyme_class** (inherits Base)
- `ec_number` VARCHAR (nullable, indexed, UNIQUE) - EC class prefix, e.g. "1.1"

**biota_enzyme_pathway** (inherits Base)
- `ec_number` VARCHAR (nullable, indexed)

**biota_enzo** (enzyme orthologs, inherits BaseFT)
- `ec_number` VARCHAR (nullable, indexed, UNIQUE)
- `pathway_id` INTEGER (nullable, FK -> biota_enzyme_pathway.id)

**biota_deprecated_enzymes** (inherits Base)
- `ec_number` VARCHAR (nullable, indexed) - old/deprecated EC number
- `new_ec_number` VARCHAR (nullable, indexed) - current EC number

---

### ONTOLOGY TABLES

**biota_go** (Gene Ontology, inherits Ontology)
- `go_id` VARCHAR (nullable, indexed) - e.g. "GO:0008150"
- `namespace` VARCHAR (nullable, indexed) - "molecular_function", "biological_process", "cellular_component"

**biota_bto** (BRENDA Tissue Ontology, inherits Ontology)
- `bto_id` VARCHAR (nullable, indexed) - e.g. "BTO_0000142"

**biota_sbo** (Systems Biology Ontology, inherits Ontology)
- `sbo_id` VARCHAR (nullable, indexed)

**biota_eco** (Evidence Ontology, inherits Ontology)
- `eco_id` VARCHAR (nullable, indexed)

---

### JUNCTION / RELATIONSHIP TABLES

**biota_reaction_substrates** - links reactions to substrate compounds
- `compound_id` INTEGER (FK -> biota_compound.id)
- `reaction_id` INTEGER (FK -> biota_reaction.id)

**biota_reaction_products** - links reactions to product compounds
- `compound_id` INTEGER (FK -> biota_compound.id)
- `reaction_id` INTEGER (FK -> biota_reaction.id)

**biota_reaction_enzymes** - links reactions to enzymes
- `enzyme_id` INTEGER (FK -> biota_enzymes.id)
- `reaction_id` INTEGER (FK -> biota_reaction.id)

**biota_enzyme_btos** - links enzymes to tissues (BTO)
- `enzyme_id` INTEGER (FK -> biota_enzymes.id)
- `bto_id` INTEGER (FK -> biota_bto.id)

**biota_pathway_compounds** (inherits Base) - links pathways to compounds by species
- `reactome_pathway_id` VARCHAR (nullable, indexed)
- `chebi_id` VARCHAR (nullable, indexed)
- `species` VARCHAR (nullable, indexed) - e.g. "Homo sapiens"

**biota_compound_ancestors** - compound ChEBI ontology tree
- `compound_id` INTEGER (FK -> biota_compound.id)
- `ancestor_id` INTEGER (FK -> biota_compound.id)
- UNIQUE(compound_id, ancestor_id)

**biota_pathway_ancestors** - pathway hierarchy
- `pathway_id` INTEGER (FK -> biota_pathways.id)
- `ancestor_id` INTEGER (FK -> biota_pathways.id)
- UNIQUE(pathway_id, ancestor_id)

**biota_go_ancestors** - GO term hierarchy
- `go_id` INTEGER (FK -> biota_go.id)
- `ancestor_id` INTEGER (FK -> biota_go.id)
- UNIQUE(go_id, ancestor_id)

**biota_bto_ancestors** - BTO tissue hierarchy
- `bto_id` INTEGER (FK -> biota_bto.id)
- `ancestor_id` INTEGER (FK -> biota_bto.id)
- UNIQUE(bto_id, ancestor_id)

**biota_sbo_ancestors** - SBO hierarchy
- `sbo_id` INTEGER (FK -> biota_sbo.id)
- `ancestor_id` INTEGER (FK -> biota_sbo.id)

**biota_eco_ancestors** - ECO hierarchy
- `eco_id` INTEGER (FK -> biota_eco.id)
- `ancestor_id` INTEGER (FK -> biota_eco.id)

---

### OTHER TABLES

**biota_organism** (inherits Base)
- `taxonomy_id` INTEGER (nullable, FK -> biota_taxonomy.id)

**biota_unicell** (inherits BaseFT) - metabolic network graphs (BlobFields, not queryable via SQL)

**biota_biomass_reaction** (inherits BaseFT)
- `biomass_rxn_id` VARCHAR (nullable, indexed)

---

### COMMON JOIN PATTERNS

-- Enzyme -> Reactions -> Substrates/Products:
SELECT e.ec_number, e.name AS enzyme_name, r.rhea_id, r.name AS reaction_name,
       cs.name AS substrate, cp.name AS product
FROM biota_enzymes e
JOIN biota_reaction_enzymes re ON re.enzyme_id = e.id
JOIN biota_reaction r ON r.id = re.reaction_id
LEFT JOIN biota_reaction_substrates rs ON rs.reaction_id = r.id
LEFT JOIN biota_compound cs ON cs.id = rs.compound_id
LEFT JOIN biota_reaction_products rp ON rp.reaction_id = r.id
LEFT JOIN biota_compound cp ON cp.id = rp.compound_id
WHERE e.ec_number = '1.1.1.1'

-- Taxon -> Enzymes:
SELECT e.ec_number, e.name, e.uniprot_id
FROM biota_enzymes e
WHERE e.tax_id = '9606'

-- Compound -> Reactions (as substrate or product):
SELECT r.rhea_id, r.name, 'substrate' AS role
FROM biota_compound c
JOIN biota_reaction_substrates rs ON rs.compound_id = c.id
JOIN biota_reaction r ON r.id = rs.reaction_id
WHERE c.chebi_id = 'CHEBI:15377'
UNION ALL
SELECT r.rhea_id, r.name, 'product' AS role
FROM biota_compound c
JOIN biota_reaction_products rp ON rp.compound_id = c.id
JOIN biota_reaction r ON r.id = rp.reaction_id
WHERE c.chebi_id = 'CHEBI:15377'

-- Enzyme -> Tissues (BTO):
SELECT e.ec_number, b.bto_id, b.name AS tissue_name
FROM biota_enzymes e
JOIN biota_enzyme_btos eb ON eb.enzyme_id = e.id
JOIN biota_bto b ON b.id = eb.bto_id
WHERE e.ec_number = '1.1.1.1'

-- Pathway -> Compounds -> Reactions:
SELECT p.name AS pathway, c.chebi_id, c.name AS compound, r.rhea_id, r.name AS reaction
FROM biota_pathways p
JOIN biota_pathway_compounds pc ON pc.reactome_pathway_id = p.reactome_pathway_id
JOIN biota_compound c ON c.chebi_id = pc.chebi_id
LEFT JOIN biota_reaction_substrates rs ON rs.compound_id = c.id
LEFT JOIN biota_reaction r ON r.id = rs.reaction_id
WHERE p.reactome_pathway_id = 'R-HSA-109582'
"""

# ============================================================================
# CONSTANTS
# ============================================================================

MAX_QUERY_LIMIT = 20
DEFAULT_QUERY_LIMIT = 10

# Tables to count for database statistics
STATISTICS_TABLES = [
    ("biota_enzymes", "Enzymes"),
    ("biota_protein", "Proteins"),
    ("biota_compound", "Compounds"),
    ("biota_reaction", "Reactions"),
    ("biota_taxonomy", "Taxonomy"),
    ("biota_pathways", "Pathways"),
    ("biota_go", "Gene Ontology (GO)"),
    ("biota_bto", "BRENDA Tissue Ontology (BTO)"),
]

# ============================================================================
# DATABASE ACCESS
# ============================================================================


def _get_db():
    """Get the Peewee database proxy for raw SQL execution."""
    from gws_biota.db.biota_db_manager import BiotaDbManager

    return BiotaDbManager.db


def _validate_readonly(sql: str):
    """Ensure the SQL query is read-only and contains only a single statement.

    Raises ValueError if the query is not safe.
    """
    stripped = sql.strip()
    stripped_upper = stripped.upper()

    # Reject SQL comments that could hide malicious payloads
    if re.search(r"--|/\*", stripped):
        raise ValueError("SQL comments (-- and /* */) are not allowed.")

    # Reject multiple statements: strip a single optional trailing semicolon,
    # then ensure no semicolons remain in the query.
    body = stripped.rstrip(";")
    if ";" in body:
        raise ValueError(
            "Multiple SQL statements are not allowed. Please provide a single SELECT query."
        )

    allowed_prefixes = ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN")
    if not stripped_upper.startswith(allowed_prefixes):
        raise ValueError(
            "Only SELECT queries are allowed. "
            "INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE are forbidden."
        )

    dangerous = [
        r"\bINTO\s+OUTFILE\b",
        r"\bINTO\s+DUMPFILE\b",
        r"\bLOAD_FILE\b",
        r"\bBENCHMARK\b",
        r"\bSLEEP\b",
    ]
    for pattern in dangerous:
        if re.search(pattern, stripped_upper):
            raise ValueError(f"Query contains forbidden pattern: {pattern}")


def _execute_sql(sql: str, limit: int = None):
    """Execute a read-only SQL query and return results as list of dicts."""
    _validate_readonly(sql)

    if limit is not None:
        stripped_upper = sql.strip().upper()
        if "LIMIT" not in stripped_upper:
            sql = sql.rstrip().rstrip(";") + f" LIMIT {limit}"
        else:
            sql = _enforce_max_limit(sql, limit)

    db = _get_db()
    cursor = db.execute_sql(sql)
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def _enforce_max_limit(sql: str, max_limit: int) -> str:
    """If the query has a LIMIT > max_limit, cap it."""
    match = re.search(r"\bLIMIT\s+(\d+)", sql, re.IGNORECASE)
    if match:
        current_limit = int(match.group(1))
        if current_limit > max_limit:
            sql = sql[: match.start(1)] + str(max_limit) + sql[match.end(1) :]
    return sql


# ============================================================================
# TOOL 1: GET SCHEMA
# ============================================================================


def get_schema() -> str:
    """Returns the complete database schema: all tables, columns with types,
    foreign key relationships, and common SQL join patterns as examples.
    """
    return DATABASE_SCHEMA


# ============================================================================
# TOOL 2: QUERY (limited rows)
# ============================================================================


def query(sql: str, limit: int = DEFAULT_QUERY_LIMIT) -> dict:
    """Execute a read-only SQL SELECT query against the Biota database.

    Returns results as a dict with row_count, limit_applied, and rows.
    Max 20 rows for exploration. Use export_to_csv for large exports.

    Args:
        sql: A SELECT query (INSERT/UPDATE/DELETE are forbidden).
        limit: Max rows to return (default 10, maximum 20).
    """
    try:
        _validate_readonly(sql)

        effective_limit = min(max(1, limit), MAX_QUERY_LIMIT)

        stripped_upper = sql.strip().upper()
        is_aggregate = any(
            agg in stripped_upper for agg in ["COUNT(", "SUM(", "AVG(", "MIN(", "MAX(", "GROUP BY"]
        )

        if is_aggregate:
            rows = _execute_sql(sql)
        else:
            rows = _execute_sql(sql, limit=effective_limit)

        return {
            "row_count": len(rows),
            "limit_applied": effective_limit if not is_aggregate else None,
            "rows": rows,
        }
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"SQL execution failed: {str(e)}"}


# ============================================================================
# TOOL 3: EXPORT TO CSV (no row limit)
# ============================================================================


def export_to_csv(sql: str, filename: Optional[str] = None) -> dict:
    """Execute a SQL SELECT query and write ALL results to a CSV file.

    Use this when the user requests large datasets, full exports, or complete lists.
    There is no row limit.

    Args:
        sql: A SELECT query. Should include specific columns (avoid SELECT *).
        filename: Optional CSV filename (without path). Auto-generated if not provided.

    Returns:
        Dict with file_path, row_count, columns, and message.
    """
    try:
        _validate_readonly(sql)

        temp_dir = Settings.make_temp_dir()

        db = _get_db()
        cursor = db.execute_sql(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        if not filename:
            timestamp = int(time.time())
            filename = f"biota_export_{timestamp}.csv"
        else:
            # Ensure we only use a basename and not a user-supplied path
            filename = os.path.basename(str(filename))
        # Basic allowlist: letters, numbers, underscore, hyphen, dot
        if not filename or not re.match(r"^[A-Za-z0-9_.-]+$", filename):
            raise ValueError(
                "Invalid filename; only letters, numbers, '_', '-', and '.' are allowed."
            )
        if not filename.endswith(".csv"):
            filename += ".csv"
        filepath = os.path.join(temp_dir, filename)
        # Ensure the resolved path stays within temp_dir
        temp_dir_abs = os.path.abspath(temp_dir)
        filepath_abs = os.path.abspath(filepath)
        if os.path.commonpath([temp_dir_abs, filepath_abs]) != temp_dir_abs:
            raise ValueError(
                "Invalid filename; path traversal outside the temp directory is not allowed."
            )

        row_count = 0
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            while True:
                rows = cursor.fetchmany(1000)
                if not rows:
                    break
                for row in rows:
                    writer.writerow(row)
                    row_count += 1

        return {
            "file_path": filepath,
            "row_count": row_count,
            "columns": columns,
            "message": f"Exported {row_count} rows to {filepath}",
        }
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}


# ============================================================================
# TOOL 4: DATABASE STATISTICS (raw SQL counts)
# ============================================================================


def get_database_statistics() -> dict:
    """Get an overview of the Biota database: total counts per entity type.

    Uses raw SQL COUNT(*) for each entity table to avoid importing ORM models.

    Returns:
        Dict with entity counts.
    """
    try:
        db = _get_db()
        statistics = {}

        for table_name, label in STATISTICS_TABLES:
            try:
                cursor = db.execute_sql(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                statistics[label] = count
            except Exception:
                statistics[label] = "N/A"

        return {"statistics": statistics}
    except Exception as e:
        return {"error": f"Failed to get database statistics: {str(e)}"}
