
from gws_biota.compound.compound_layout import CompoundLayout
from gws_core import BaseTestCase


class TestCompoundLayout(BaseTestCase):

    def test_update_compound(self):

        CompoundLayout.update_compound_layout(
            chebi_id="CHEBI:16349",
            cluster_id="amino_acid_metabolism",
            level="2",
            x="1",
            y="1"
        )

        CompoundLayout.update_compound_layout(
            chebi_id="CHEBI:15361",
            cluster_id="carbohydrate_metabolism",
            level="2",
            x="0",
            y="0"
        )
