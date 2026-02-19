"""
MCP Biota V3 - SQL-Based Tools
===============================

Minimal MCP server with 4 tools:
    1. get_schema           - Returns database schema (tables, columns, relationships)
    2. query                - Execute a read-only SQL SELECT (limit 10, max 20 rows)
    3. export_to_csv        - Execute a SQL SELECT and write results to CSV (no row limit)
    4. get_database_statistics - Database overview with entity counts

This approach lets Claude write any SQL query, making it far more flexible
than pre-defined tools while keeping the tool count minimal.
"""

import csv
import os
import re
import time
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ============================================================================
# INITIALIZATION
# ============================================================================


def init_gws_core():
    from gws_core_loader import load_gws_core

    load_gws_core()

    from gws_core.manage import AppManager

    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="ERROR")


init_gws_core()

from mcp_biota_simple import get_database_statistics

# ============================================================================
# DATABASE ACCESS
# ============================================================================


def _get_db():
    """Get the Peewee database proxy for raw SQL execution."""
    from gws_biota.db.biota_db_manager import BiotaDbManager

    return BiotaDbManager.db


def _validate_readonly(sql: str):
    """Ensure the SQL query is read-only. Raises ValueError if not."""
    stripped = sql.strip().upper()

    # Only allow SELECT and SHOW/DESCRIBE
    allowed_prefixes = ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN")
    if not stripped.startswith(allowed_prefixes):
        raise ValueError(
            "Only SELECT queries are allowed. "
            "INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE are forbidden."
        )

    # Block dangerous patterns even inside SELECT
    dangerous = [
        r"\bINTO\s+OUTFILE\b",
        r"\bINTO\s+DUMPFILE\b",
        r"\bLOAD_FILE\b",
        r"\bBENCHMARK\b",
        r"\bSLEEP\b",
    ]
    for pattern in dangerous:
        if re.search(pattern, stripped):
            raise ValueError(f"Query contains forbidden pattern: {pattern}")


def _execute_sql(sql: str, limit: int = None):
    """Execute a read-only SQL query and return results as list of dicts."""
    _validate_readonly(sql)

    # Inject LIMIT if not present and limit is specified
    if limit is not None:
        stripped_upper = sql.strip().upper()
        if "LIMIT" not in stripped_upper:
            sql = sql.rstrip().rstrip(";") + f" LIMIT {limit}"
        else:
            # Replace existing LIMIT if it exceeds our max
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
# SCHEMA DEFINITION
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
# CSV EXPORT DIRECTORY
# ============================================================================

CSV_EXPORT_DIR = "/lab/user/data"


def _ensure_export_dir():
    """Ensure the CSV export directory exists."""
    os.makedirs(CSV_EXPORT_DIR, exist_ok=True)


# ============================================================================
# HELPERS
# ============================================================================


def _safe_model_dump(obj):
    """Safely convert a result to a dict."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    return str(obj)


# ============================================================================
# MCP SERVER
# ============================================================================

mcp = FastMCP(
    "biota-database",
    instructions="""Constellab Biota database: comprehensive biological knowledge base.

You have 4 tools:
1. **get_schema** - Call this FIRST to understand tables, columns, and join patterns.
2. **query** - Execute SELECT queries. Returns max 20 rows. Use for exploration and answering questions.
3. **export_to_csv** - Execute SELECT queries and save ALL results to CSV. Use when the user wants large datasets, exports, or full lists.
4. **get_database_statistics** - Quick overview of entity counts.

WORKFLOW:
1. Call get_schema once at the start of a conversation to learn the database structure.
2. Write SQL queries to answer user questions. Start with COUNT(*) if unsure about data size.
3. If the user wants all data or a large export, use export_to_csv instead of query.

IMPORTANT:
- Only SELECT queries are allowed (no INSERT, UPDATE, DELETE).
- The query tool returns max 20 rows. If the user needs more, use export_to_csv.
- Always include a LIMIT in your queries unless you specifically want a count.
- Use the join patterns from get_schema as templates.
""",
)


# ============================================================================
# TOOL 1: GET SCHEMA
# ============================================================================


@mcp.tool()
def get_schema():
    """Returns the complete database schema: all tables, columns with types,
    foreign key relationships, and common SQL join patterns as examples.

    Call this once at the start of a conversation to understand the database structure.
    """
    return DATABASE_SCHEMA


# ============================================================================
# TOOL 1b: GET SCHEMA FROM DB (live introspection)
# ============================================================================


# @mcp.tool()
# def get_schema_from_db():
#     """Extract the live database schema directly from MariaDB INFORMATION_SCHEMA.

#     Returns all tables with their columns (name, type, nullable, key) and
#     all foreign key relationships. Use this to verify or complement get_schema.
#     """
#     try:
#         db = _get_db()

#         # Get current database name
#         cursor = db.execute_sql("SELECT DATABASE()")
#         db_name = cursor.fetchone()[0]

#         # Get all tables and columns
#         columns_sql = """
#             SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT
#             FROM INFORMATION_SCHEMA.COLUMNS
#             WHERE TABLE_SCHEMA = %s
#             ORDER BY TABLE_NAME, ORDINAL_POSITION
#         """
#         cursor = db.execute_sql(columns_sql, (db_name,))
#         columns_rows = cursor.fetchall()

#         # Get foreign keys
#         fk_sql = """
#             SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
#             FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
#             WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
#             ORDER BY TABLE_NAME, COLUMN_NAME
#         """
#         cursor = db.execute_sql(fk_sql, (db_name,))
#         fk_rows = cursor.fetchall()

#         # Get row counts per table
#         tables_sql = """
#             SELECT TABLE_NAME, TABLE_ROWS
#             FROM INFORMATION_SCHEMA.TABLES
#             WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
#             ORDER BY TABLE_NAME
#         """
#         cursor = db.execute_sql(tables_sql, (db_name,))
#         table_rows = cursor.fetchall()

#         # Build structured result
#         tables = {}
#         for table_name, approx_rows in table_rows:
#             tables[table_name] = {"approx_rows": approx_rows, "columns": [], "foreign_keys": []}

#         for table, col, col_type, nullable, key, _default in columns_rows:
#             if table in tables:
#                 tables[table]["columns"].append(
#                     {
#                         "name": col,
#                         "type": col_type,
#                         "nullable": nullable == "YES",
#                         "key": key if key else None,
#                     }
#                 )

#         for table, col, ref_table, ref_col in fk_rows:
#             if table in tables:
#                 tables[table]["foreign_keys"].append(
#                     {
#                         "column": col,
#                         "references": f"{ref_table}.{ref_col}",
#                     }
#                 )

#         return {"database": db_name, "table_count": len(tables), "tables": tables}
#     except Exception as e:
#         return {"error": f"Schema extraction failed: {str(e)}"}


# ============================================================================
# TOOL 2: QUERY (limited rows)
# ============================================================================

MAX_QUERY_LIMIT = 20
DEFAULT_QUERY_LIMIT = 10


@mcp.tool()
def query(sql: str, limit: int = DEFAULT_QUERY_LIMIT):
    """Execute a read-only SQL SELECT query against the Biota database.

    Returns results as a list of row dictionaries. Use for exploration, counts,
    and answering user questions. For large exports, use export_to_csv instead.

    Args:
        sql: A SELECT query (INSERT/UPDATE/DELETE are forbidden).
             Always include relevant columns rather than SELECT *.
        limit: Max rows to return (default 10, maximum 20).
               Does not apply if the query is a COUNT/aggregate.
    """
    try:
        _validate_readonly(sql)

        # Clamp limit
        effective_limit = min(max(1, limit), MAX_QUERY_LIMIT)

        # Don't inject LIMIT on aggregate queries (COUNT, SUM, AVG, etc.)
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


@mcp.tool()
def export_to_csv(sql: str, filename: Optional[str] = None):
    """Execute a SQL SELECT query and write ALL results to a CSV file.

    Use this when the user requests large datasets, full exports, or complete lists.
    There is no row limit — all matching rows are written to the file.

    Args:
        sql: A SELECT query. Should include specific columns (avoid SELECT *).
        filename: Optional CSV filename (without path). If not provided, one is auto-generated.
                  The file is saved to /lab/user/data/.

    Returns:
        The file path, row count, and column names.
    """
    try:
        _validate_readonly(sql)
        _ensure_export_dir()

        db = _get_db()
        cursor = db.execute_sql(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        if not filename:
            timestamp = int(time.time())
            filename = f"biota_export_{timestamp}.csv"

        if not filename.endswith(".csv"):
            filename += ".csv"

        filepath = os.path.join(CSV_EXPORT_DIR, filename)

        row_count = 0
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            # Stream rows in batches to avoid loading everything in memory
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
# TOOL 4: DATABASE STATISTICS
# ============================================================================


@mcp.tool()
def database_statistics():
    """Get an overview of the Biota database: total counts per entity type
    (enzymes, proteins, compounds, reactions, pathways, taxa, BTO tissues, GO terms, etc.).
    Use this to understand what data is available before writing queries.
    """
    return _safe_model_dump(get_database_statistics())


# ============================================================================
# RUN SERVER
# ============================================================================

mcp.run(transport="stdio")
