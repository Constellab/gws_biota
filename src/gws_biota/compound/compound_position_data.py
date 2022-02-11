# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from ._position.amino_acids_metabolism import POS as AMINO_ACIDS_METABOLISM
from ._position.ethanol_metabolism import POS as ETHANOL_METABOLISM
from ._position.fatty_acids_elongation import POS as FATTY_ACIDS_ELONGATION
from ._position.fatty_acids_synthesis import POS as FATTY_ACIDS_SYNTHESIS
from ._position.fructose_metabolism import POS as FRUCTOSE_METABOLISM
from ._position.glycerophospholipids import POS as GLYCEROPHOSPHOLIPIDS
from ._position.glycolysis import POS as GLYOCOLYSIS
from ._position.prpp import POS as PRPP
from ._position.pyruvate import POS as PYRUVATE
from ._position.sterol_metabolism import POS as STEROL_METABOLISM
from ._position.tca import POS as TCA
from ._position.urea_cycle import POS as UREA_CYCLE

N = None
COMPOUND_POSITION_DATA = {

    **AMINO_ACIDS_METABOLISM,
    **ETHANOL_METABOLISM,
    **FATTY_ACIDS_ELONGATION,
    **FATTY_ACIDS_SYNTHESIS,
    **FRUCTOSE_METABOLISM,
    **GLYCEROPHOSPHOLIPIDS,
    **GLYOCOLYSIS,
    **PRPP,
    **PYRUVATE,
    **STEROL_METABOLISM,
    **TCA,
    **UREA_CYCLE
}
