import os
from gws_core import Settings, BaseTestCase
from gws_biota import Compound
from gws_biota.compound.compound_service import CompoundService

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = os.path.join(
    settings.get_variable("gws_biota:testdata_dir"),
    '../_helper/data/'
)

class TestCompound(BaseTestCase):

    def test_db_object(self):
        self.print("Compound")
        params = dict(
            biodata_dir = testdata_path,
            chebi_file = "chebi_test.obo",
        )
        CompoundService.create_compound_db(**params)
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:24431').get_name(), "chemical entity")
        self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:17051').get_name(), 'fluoride')
        
        comp = Compound.get(Compound.chebi_id == 'CHEBI:49499')
        self.assertEqual(comp.get_name(), 'beryllium difluoride')
        
        self.assertEqual(len(comp.ancestors), 1)
        self.assertEqual(comp.ancestors[0].get_name(), 'fluoride salt')

        pos = comp.position
        print(pos.x)
        print(pos.y)