# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota.db.bto import BTO as _BTO
from biota.db.chebi_ontology import ChebiOntology as _ChebiOntology
from biota.db.compound import Compound as _Compound
from biota.db.eco import ECO as _ECO
from biota.db.enzyme import Enzyme as _Enzyme
from biota.db.enzyme_function import EnzymeFunction as _EnzymeFunction
from biota.db.gene import Gene as _Gene
from biota.db.go import Go as _Go
from biota.db.organism import Organism as _Organism
from biota.db.protein import Protein as _Protein
from biota.db.pwo import PWO as _PWO
from biota.db.reaction import Reaction as _Reaction
from biota.db.sbo import SBO as _SBO
from biota.db.taxonomy import Taxonomy as _Taxonomy

class BTO(_BTO):
    pass

class ChebiOntology(_ChebiOntology):
    pass

class Compound(_Compound):
    pass

class ECO(_ECO):
    pass

class Enzyme(_Enzyme):
    pass

class EnzymeFunction(_EnzymeFunction):
    pass

class Gene(_Gene):
    pass

class Go(_Go):
    pass

class Organism(_Organism):
    pass

class Protein(_Protein):
    pass

class PWO(_PWO):
    pass

class Reaction(_Reaction):
    pass

class SBO(_SBO):
    pass

class Taxonomy(_Taxonomy):
    pass