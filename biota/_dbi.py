# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota._db.bto import BTO as _BTO
from biota._db.chebi_ontology import ChebiOntology as _ChebiOntology
from biota._db.compound import Compound as _Compound
from biota._db.eco import ECO as _ECO
from biota._db.enzyme import Enzyme as _Enzyme
from biota._db.enzyme_function import EnzymeFunction as _EnzymeFunction
from biota._db.gene import Gene as _Gene
from biota._db.go import GO as _GO
from biota._db.organism import Organism as _Organism
from biota._db.protein import Protein as _Protein
from biota._db.pathway import Pathway as _Pathway
from biota._db.pwo import PWO as _PWO
from biota._db.reaction import Reaction as _Reaction
from biota._db.sbo import SBO as _SBO
from biota._db.taxonomy import Taxonomy as _Taxonomy

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

class GO(_GO):
    pass

class Organism(_Organism):
    pass

class Protein(_Protein):
    pass

class Pathway(_Pathway):
    pass

class PWO(_PWO):
    pass

class Reaction(_Reaction):
    pass

class SBO(_SBO):
    pass

class Taxonomy(_Taxonomy):
    pass