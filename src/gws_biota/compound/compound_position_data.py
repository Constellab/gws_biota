# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from ._position.fatty_acids_elongation import POS as FATTY_ACIDS_ELONGATION
from ._position.fatty_acids_synthesis import POS as FATTY_ACIDS_SYNTHESIS
from ._position.fructose_metabolism import POS as FRUCTOSE_METABOLISM
from ._position.glycerophospholipids import POS as GLYCEROPHOSPHOLIPIDS
from ._position.glycolysis import POS as GLYOCOLYSIS
from ._position.prpp import POS as PRPP
from ._position.pyruvate import POS as PYRUVATE
from ._position.sterol_metabolism import POS as STEROL_METABOLISM
from ._position.tca import POS as TCA

N = None
COMPOUND_POSITION_DATA = {

    "CHEBI:17378": {"x": N,     "y": N},  # D-glyceraldehyde
    "CHEBI:58248": {"x": -20,   "y": 20},  # 2,3-bisphosphonato-D-glycerate(5−)
    "CHEBI:16016": {"x": -10,   "y": 50},  # dihydroxyacetone

    **GLYOCOLYSIS,
    **PRPP,
    **TCA,
    **FATTY_ACIDS_ELONGATION,
    **FATTY_ACIDS_SYNTHESIS,
    **PYRUVATE,
    **GLYCEROPHOSPHOLIPIDS,
    **FRUCTOSE_METABOLISM,
    **STEROL_METABOLISM,

    # ***
    # Pyruvate Hub
    # ***


    # ***
    # Fatty acids
    # ***

    "CHEBI:30839": {"x": N,     "y": N},  # orotate
    "CHEBI:10983": {"x": N,     "y": N},  # (R)-3-hydroxybutyrate
    "CHEBI:11047": {"x": N,     "y": N},  # (S)-3-hydroxybutyrate
    "CHEBI:32372": {"x": N,     "y": N},  # palmitoleate
    "CHEBI:17268": {"x": N,     "y": N},  # myo-inositol
    "CHEBI:15354": {"x": N,     "y": N},  # choline
    "CHEBI:295975": {"x": N,    "y": N},  # choline phosphate(1-)
    "CHEBI:57643": {"x": N,     "y": N},  # 1,2-diacyl-sn-glycero-3-phosphocholine
    "CHEBI:17754": {"x": N,     "y": N},  # glycerol
    "CHEBI:64615": {"x": N,     "y": N},  # triacyl-sn-glycerol
    "CHEBI:17815": {"x": N,     "y": N},  # 1,2-diacyl-sn-glycerol
    "CHEBI:58608": {"x": N,     "y": N},  # 1,2-diacyl-sn-glycerol 3-phosphate(2-)
    "CHEBI:57262": {"x": N,     "y": N},  # 3-sn-phosphatidyl-L-serine(1-)
    "CHEBI:59996": {"x": N,     "y": N},  # 1,2-diacyl-sn-glycerol 3-diphosphate(3-)
    "CHEBI:57597": {"x": N,     "y": N},  # sn-glycerol 3-phosphate(2-)
    "CHEBI:16113": {"x": N,     "y": N},  # cholesterol
    "CHEBI:62237": {"x": N,     "y": N},  # cardiolipin(2-)

    # ***
    # AA
    # ***

    # L-glutamine zwitterion, L-Glutamine
    "CHEBI:58359": {"x": 25,    "y": -35, "alt": ["CHEBI:42943", "CHEBI:42899", "CHEBI:32679", "CHEBI:32678", "CHEBI:28300", "CHEBI:42812", "CHEBI:13110", "CHEBI:18050", "CHEBI:32666", "CHEBI:6227", "CHEBI:32665", "CHEBI:21308", "CHEBI:42814", "CHEBI:5432", "CHEBI:24316"]},
    # L-glutamate(1-), L-Glutamate
    "CHEBI:29985": {"x": 35,    "y": -40, "alt": ["CHEBI:76051", "CHEBI:21301", "CHEBI:29985", "CHEBI:42825", "CHEBI:29987", "CHEBI:18237", "CHEBI:24314", "CHEBI:16015", "CHEBI:13107", "CHEBI:5431", "CHEBI:21304", "CHEBI:6224", "CHEBI:14321", "CHEBI:29988"]},

    "CHEBI:60039": {"x": -100,     "y": 60},  # L-proline zwitterion
    "CHEBI:29991": {"x": -100,     "y": 50},  # L-aspartate(1-)
    "CHEBI:57844": {"x": -100,     "y": 50},  # L-methionine zwitterion
    "CHEBI:58048": {"x": -100,     "y": 30},  # L-asparagine zwitterion
    "CHEBI:57972": {"x": -100,     "y": 20},  # L-alanine zwitterion
    "CHEBI:57762": {"x": -100,     "y": 10},  # L-valine zwitterion
    "CHEBI:57427": {"x": -100,     "y": 0},  # L-leucine zwitterion
    "CHEBI:58045": {"x": -100,     "y": -10},  # L-isoleucine zwitterion
    "CHEBI:57305": {"x": -100,     "y": -20},  # L-threonine zwitterion
    "CHEBI:57926": {"x": -100,     "y": -30},  # L-threonine zwitterion
    "CHEBI:16467": {"x": -100,     "y": -40},  # L-arginine
    "CHEBI:33384": {"x": -100,     "y": -50},  # L-serine

    "CHEBI:17790": {"x": N,     "y": N},  # methanol
    "CHEBI:57880": {"x": N,     "y": N},  # 1-phosphatidyl-1D-myo-inositol(1-)

    "CHEBI:16199": {"x": -60,   "y": -70},  # urea
    "CHEBI:57743": {"x": -40,   "y": -40},  # L-citrulline zwitterion
    "CHEBI:46911": {"x": -60,   "y": -50},  # L-ornithinium(1+)
    "CHEBI:32682": {"x": -40,   "y": -60},  # L-argininium(1+)

    # acetaldehyde
    "CHEBI:15343": {"x": 20,     "y": 0, "is_major": True, "alt": ["CHEBI:40533", "CHEBI:13703", "CHEBI:2383", "CHEBI:22158"]},
    # ethanol
    "CHEBI:16236": {"x": 30,     "y": 0, "is_major": True, "alt": ["CHEBI:44594", "CHEBI:42377", "CHEBI:4879", "CHEBI:14222", "CHEBI:23978", "CHEBI:30878", "CHEBI:30880"]}
}
