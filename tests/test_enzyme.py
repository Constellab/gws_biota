from gws_biota import BTO, DeprecatedEnzyme, Enzyme, EnzymeClass
from gws_biota.enzyme.enzyme_service import EnzymeService
from gws_core import BaseTestCase, Settings


class TestEnzyme(BaseTestCase):

    def test_enzyme(self):
        self.print("Enzyme")
        settings = Settings.get_instance()
        testdata_path = settings.get_variable("gws_biota:testdata_dir")
        params = dict(
            biodata_dir=testdata_path,
            brenda_file="brenda_test.txt",
            bkms_file="bkms_test.csv",
            expasy_enzclass_file="enzclass_test.txt"
        )
        bto = BTO(bto_id='BTO:0000214')
        bto.save()

        EnzymeService.create_enzyme_db(**params)
        enzymes = Enzyme.select().where(Enzyme.ec_number == '1.4.3.7')
        for enzyme in enzymes:
            if enzyme.organism == 'Candida boidinii':
                break

        n = len(enzyme.params('ST'))
        bto_ids = []
        for i in range(0, n):
            bto_ids.append(enzyme.params('ST')[i].get("bto"))

        print(bto_ids)

        self.assertEqual(enzyme.bto[0].bto_id, 'BTO:0000214')

        self.assertEqual(enzyme.organism, 'Candida boidinii')
        self.assertEqual(enzyme.name, 'D-glutamate oxidase')

        self.assertEqual(len(enzyme.params('CF')), 1)
        self.assertEqual(enzyme.params('CF')[0].value, "FAD")
        self.assertEqual(enzyme.params('CF')[0].refs, [1, 3])
        self.assertEqual(
            enzyme.params('CF')[0].full_refs,
            {'1': 4387700,
             '2':
             'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.',
             '3': 13583997})
        self.assertEqual(enzyme.params('CF')[0].comments, "#1,2# cannot be replaced by FMN <1,3>")
        self.assertEqual(enzyme.params('CF')[0].what, "cofactor")

        self.assertEqual(enzyme.params('MW')[0].value, "43000")
        self.assertEqual(enzyme.params('MW')[0].refs, [1])
        self.assertEqual(
            enzyme.params('MW')[0].full_refs,
            {'1': 4387700,
             '2':
             'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.',
             '3': 13583997})
        self.assertEqual(enzyme.params('MW')[0].comments, "#1# gel filtration <1>")
        self.assertEqual(enzyme.params('MW')[0].what, "molecular weight")

        self.assertEqual(enzyme.params('RE')[0].value, "D-glutamate + H2O + O2 = 2-oxoglutarate + NH3 + H2O2")
        self.assertEqual(enzyme.params('RE')[0].what, "reaction catalyzed")
        self.assertEqual(enzyme.params('RE')[0].comments, None)

        self.assertEqual(enzyme.params('RT')[0].value, "oxidation")
        self.assertEqual(enzyme.params('RT')[0].what, "reaction type")
        self.assertEqual(enzyme.params('RT')[0].comments, None)

        self.assertEqual(enzyme.params('RT')[1].value, "oxidative deamination")
        self.assertEqual(enzyme.params('RT')[1].what, "reaction type")
        self.assertEqual(enzyme.params('RT')[1].comments, None)

        self.assertEqual(enzyme.params('RT')[2].value, "redox reaction")
        self.assertEqual(enzyme.params('RT')[3].value, "reduction")
        self.assertEqual(enzyme.params('RT')[1000].value, None)

        self.assertEqual(enzyme.params('ST')[0].value, "cell culture")
        self.assertEqual(enzyme.params('ST')[0].get("bto"), "BTO:0000214")

        self.assertEqual(enzyme.params('UknownParam')[0].value, None)
        self.assertEqual(enzyme.params('UknownParam')[1000].value, None)

        enzymes = Enzyme.select().where(Enzyme.ec_number == '3.5.1.43')
        for enzyme in enzymes:
            if enzyme.organism == 'Bacillus circulans':
                break

        self.assertEqual(enzyme.organism, 'Bacillus circulans')

        Q = Enzyme.search_by_name("glutaminase")
        self.assertEqual(len(Q), 0)
        Q = Enzyme.search_by_name("%glutaminase")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].name, 'peptidyl-glutaminase')

        # Show all deprecated
        print("\nDeprecated enzymes map")
        Q = DeprecatedEnzyme.select()
        for e in Q:
            print(f"deprecated = {e.ec_number} -> {e.new_ec_number}")

        # Test deprecated ids
        # enzyme 1.1.1.109 is tranferred to {1.3.1.28 and 1.1.1.119}
        print("Deprecated enzymes")
        Q = DeprecatedEnzyme.select().where(DeprecatedEnzyme.ec_number == '1.1.1.109')
        self.assertEqual(len(Q), 2)
        self.assertEqual(Q[0].ec_number, '1.1.1.109')
        self.assertTrue(Q[0].new_ec_number in ['1.3.1.28', '1.1.1.119'])
        self.assertEqual(Q[0].reason, 'transferred;transferred')

        self.assertEqual(Q[1].ec_number, '1.1.1.109')
        self.assertTrue(Q[1].new_ec_number in ['1.3.1.28', '1.1.1.119'])
        self.assertEqual(Q[1].reason, 'transferred;transferred')

        self.assertNotEqual(Q[0].new_ec_number, Q[1].new_ec_number)

        # Test enzyme class
        enzyme_class = EnzymeClass.get(EnzymeClass.ec_number == '1.1.-.-')
        self.assertEqual(enzyme_class.get_name(), 'Acting on the CH-OH group of donors')

        # Follow deprecated enzymes
        print("\nResolve deprecated enzymes")
        Q = Enzyme.select_and_follow_if_deprecated(ec_number='1.1.1.109')
        self.assertEqual(len(Q), 15)
        for e in Q:
            print(e.ec_number)
            self.assertTrue(e.ec_number in ['1.1.1.119', '1.3.1.28'])
            # self.assertEqual(e.related_deprecated_enzyme.ec_number, '1.1.1.109')

        # Multiple deprecated
        print("\nFollow multiple deprecated enzymes")
        Q = DeprecatedEnzyme.select().where(DeprecatedEnzyme.ec_number == '1.1.0.10')
        for e in Q:
            for ne in e.select_new_enzymes():
                print(f"deprecated = {e.ec_number} -> {ne.ec_number}")

        # Multiple deprecated
        # These fake enzymes are deprecated: 1.1.0.10 -> 1.3.1.45 -> 1.3.1.18 -> {1.3.1.28 and 1.1.1.119}
        print("\nResolve multiple deprecated enzymes")
        Q = Enzyme.select().where(Enzyme.ec_number.in_(['1.1.0.10', '1.3.1.45', '1.3.1.18']))
        self.assertEqual(len(Q), 0)
        Q = Enzyme.select_and_follow_if_deprecated(ec_number='1.1.0.10')
        # self.assertEqual(len(Q), 15)
        for e in Q:
            print(e.ec_number)
            self.assertTrue(e.ec_number in ['1.1.1.119', '1.3.1.28'])
