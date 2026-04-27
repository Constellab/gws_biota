

from brendapy import BrendaParser, BrendaSettings


# =============================================================================
# UTF-8 ENCODING PATCH FOR PRONTO
# =============================================================================
# Force UTF-8 encoding globally for pronto to prevent UnicodeDecodeError
# when brendapy loads ChEBI ontology. This must be applied BEFORE any
# brendapy operations that load ChEBI (e.g., get_substances()).
# =============================================================================
import pronto.ontology as pronto_ontology
import pronto.utils.io as pronto_io

_original_decompress = pronto_io.decompress

def _decompress_utf8(reader, path=None, encoding=None):
    """Force UTF-8 encoding for all pronto file operations"""
    return _original_decompress(reader, path, encoding="utf-8")

# Apply UTF-8 patch globally
pronto_io.decompress = _decompress_utf8
pronto_ontology.decompress = _decompress_utf8


# =============================================================================
# BRENDAPY TOKEN FILTERING PATCH
# =============================================================================
# Monkey-patch BrendaParser._store_item to handle empty reference tokens
# This fixes a bug in brendapy where refs like "1,2," or "1,,3" cause:
# ValueError: invalid literal for int() with base 10: ''
# =============================================================================
_original_store_item = BrendaParser._store_item


@staticmethod
def _patched_store_item(results, bid, item, ec):
    """
    Patched version of BrendaParser._store_item that filters empty tokens
    before converting to int. This prevents ValueError on malformed reference strings.

    This is a minimal patch that only fixes the bug without changing logic.
    """
    from collections import OrderedDict
    from brendapy.substances import get_substances

    if not BrendaParser.CHEBI:
        BrendaParser.CHEBI = get_substances()

    if bid == "ID":
        results[bid] = item
    elif bid in {"RN", "RE", "RT", "SN"}:
        if isinstance(results[bid], OrderedDict):
            results[bid] = {item}
        else:
            results[bid].add(item)
    elif bid == "RF":
        match = BrendaParser.PATTERN_RF.match(item)
        if match:
            rid, info, pubmed = match.group(1), match.group(2), match.group(3)
            rid = int(rid)
            results[bid][rid] = {'info': info}
            if pubmed and len(pubmed) > 0:
                pubmed = int(pubmed)
                results[bid][rid]['pubmed'] = pubmed
    else:
        match = BrendaParser.PATTERN_ALL.match(item)
        if match:
            ids, data_all, refs = match.group(1), match.group(2), match.group(3)
            ids = ids.replace(' ', ",")
            # PATCH: Filter empty tokens before converting to int
            ids = [int(token) for token in ids.split(',') if token.strip()]
            refs = refs.replace(' ', ",")

            comment = None
            tokens = data_all.split('(#')
            if len(tokens) == 1:
                data = tokens[0]
            elif len(tokens) == 2:
                data = tokens[0].strip()
                comment = "(#" + tokens[1].strip()
                comment = comment[1:-1]

            if len(data) == 0:
                pass
            elif data == "more":
                return

            # PATCH: Filter empty tokens before converting to int
            info = {
                'data': data.strip(),
                'refs': [int(token) for token in refs.split(',') if token.strip()]
            }
            if comment:
                info['comment'] = comment

            if bid in BrendaParser.UNITS:
                info["units"] = BrendaParser.UNITS[bid]
                if data.startswith("-999"):
                    pass
                else:
                    match_s = BrendaParser.PATTERN_VALUE.match(info["data"])
                    if match_s:
                        info['value'] = match_s.group(1)
                        substrate = match_s.group(2)
                        info['substrate'] = substrate
                        if substrate in BrendaParser.CHEBI:
                            info['chebi'] = BrendaParser.CHEBI[substrate]
                    else:
                        try:
                            info['value'] = info["data"]
                        except:
                            pass

            # Store results following original logic
            for pid in ids:
                if bid == "PR":
                    results[bid][pid] = info
                else:
                    if pid in results[bid]:
                        results[bid][pid].append(info)
                    else:
                        results[bid][pid] = [info]
        else:
            if bid == "SY" and item[0] != '#':
                pass


# Apply the patch
BrendaParser._store_item = _patched_store_item
BrendaParser._store_item = _patched_store_item


class Brenda:
    """
    This module allows to get list of dictionnaries where terms represents brenda proteins/enzymes
    """
    parser = None  # reuse parser

    def __init__(self, brenda_file, taxonomy_dir=None, bto_file=None, chebi_file=None):
        BrendaSettings.initialize_data_dir(
            brenda_file=brenda_file, taxonomy_dir=taxonomy_dir, bto_file=bto_file, chebi_file=chebi_file)
        self.parser = BrendaParser(brenda_file=brenda_file)

    def parse_all_enzyme_to_dict(self):
        """
        Uses the package brandapy to parses the brenda_download.txt file and returns a list of dictionnaries
        where terms represent proteins filled with their informations (experimental properties, citations, synonyms, etc...).

        :returns: list of all brenda proteins
        :rtype: list
        """
        list_proteins = []
        list_deprecated_ec = []
        for ec in self.parser.keys():
            proteins, deprecated_ec = self.parser.get_all_proteins(ec)

            if deprecated_ec:
                list_deprecated_ec.append(deprecated_ec)

            for p in proteins.values():
                for k in p.data:
                    if isinstance(p.data[k], set):
                        p.data[k] = list(p.data[k])
                        p.data[k].sort()

                    # only keep pubmed ids if possible
                    if k == 'references':
                        for idx in p.data[k]:
                            if "pubmed" in p.data[k][idx]:
                                p.data[k][idx] = p.data[k][idx]["pubmed"]
                            else:
                                p.data[k][idx] = p.data[k][idx]["info"]

                list_proteins.append(p.data)

        return list_proteins, list_deprecated_ec
