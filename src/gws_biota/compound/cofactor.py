# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

class Cofactor:
    """ List of cofactors """
    COFACTORS = {
        # hydron, H+
        "CHEBI:15378": {"alt": ["CHEBI:5584", "CHEBI:10744", "CHEBI:13357"]},
        # water, H2O
        "CHEBI:15377": {"alt": ["CHEBI:5585", "CHEBI:42857", "CHEBI:42043", "CHEBI:44292", "CHEBI:44819", "CHEBI:43228", "CHEBI:44701", "CHEBI:10743", "CHEBI:13352", "CHEBI:27313"]},
        # hydrogen_peroxide, H2O2
        "CHEBI:16240": {"alt": ["CHEBI:44812", "CHEBI:5586", "CHEBI:13354", "CHEBI:13355", "CHEBI:24637"]},
        # hydrogenphosphate
        "CHEBI:43474": {"alt": ["CHEBI:43470", "CHEBI:29139"]},
        # diphosphate
        "CHEBI:33019": {"alt": ["CHEBI:45212", "CHEBI:45208", "CHEBI:33018", "CHEBI:33017", "CHEBI:35782"]},
        # phosphate
        "CHEBI:26078": {"alt": ["CHEBI:26078", "CHEBI:18367", "CHEBI:29139", "CHEBI:39739", "CHEBI:43470", "CHEBI:35780", "CHEBI:43474", "CHEBI:26020", "CHEBI:45024", "CHEBI:39745", "CHEBI:29137", "CHEBI:14791", "CHEBI:7793"]},
        # NAD
        "CHEBI:15846": {"alt": ["CHEBI:13394", "CHEBI:7422", "CHEBI:21901", "CHEBI:29867", "CHEBI:57540"]},
        # NADH
        "CHEBI:16908": {"alt": ["CHEBI:44216", "CHEBI:7423", "CHEBI:13395", "CHEBI:13396", "CHEBI:21902", "CHEBI:57945"]},
        # NADP
        "CHEBI:18009": {"alt": ["CHEBI:7424", "CHEBI:13398", "CHEBI:21903", "CHEBI:29868", "CHEBI:58349", "CHEBI:25524"]},
        # NADPH
        "CHEBI:16474": {"alt": ["CHEBI:44286", "CHEBI:7425", "CHEBI:13399", "CHEBI:13400", "CHEBI:21904", "CHEBI:57783"]},
        # dTMP
        "CHEBI:17013": {"alt": ["CHEBI:26999", "CHEBI:45926", "CHEBI:46036", "CHEBI:46013", "CHEBI:47711", "CHEBI:45759", "CHEBI:45762", "CHEBI:45772", "CHEBI:10529", "CHEBI:14092", "CHEBI:15246", "CHEBI:63549", "CHEBI:63528"]},
        # peroxol
        "CHEBI:35924": {"alt": []},
        # alcohol
        "CHEBI:30879": {"alt": ["CHEBI:22288", "CHEBI:2553", "CHEBI:13804"]},
        # ADP
        "CHEBI:16761": {"alt": ["CHEBI:40553", "CHEBI:13222", "CHEBI:2342", "CHEBI:22244", "CHEBI:456216"]},
        # ATP
        "CHEBI:15422": {"alt": ["CHEBI:40938", "CHEBI:10841", "CHEBI:10789", "CHEBI:2359", "CHEBI:13236", "CHEBI:22249", "CHEBI:30616"]},
        # dADP
        "CHEBI:16174": {"alt": ["CHEBI:19238", "CHEBI:42290", "CHEBI:10491", "CHEBI:14069", "CHEBI:57667", "CHEBI:61404"]},
        # AMP
        "CHEBI:16027": {"alt": ["CHEBI:13740", "CHEBI:40510", "CHEBI:22242", "CHEBI:40726", "CHEBI:40786", "CHEBI:40826", "CHEBI:47222", "CHEBI:12056", "CHEBI:2356", "CHEBI:13736", "CHEBI:13234", "CHEBI:13235", "CHEBI:22245", "CHEBI:456215"]},
        # CMP, cytidine 5'-monophosphate(2-)
        "CHEBI:17361": {"alt": ["CHEBI:58120", "CHEBI:41312", "CHEBI:41319", "CHEBI:41691", "CHEBI:41666", "CHEBI:47362", "CHEBI:48799", "CHEBI:3275", "CHEBI:13274", "CHEBI:23520", "CHEBI:60377"]},
        # FAD
        "CHEBI:16238": {"alt": ["CHEBI:42388", "CHEBI:4956", "CHEBI:13315", "CHEBI:21125", "CHEBI:57692"]},
        # FADH2
        "CHEBI:17877": {"alt": ["CHEBI:21126", "CHEBI:42427", "CHEBI:13316", "CHEBI:4957", "CHEBI:58307"]},
        # FMN
        "CHEBI:17621": {"alt": ["CHEBI:42587", "CHEBI:4960", "CHEBI:13317", "CHEBI:21127", "CHEBI:58210"]},
        # FMNH2
        "CHEBI:16048": {"alt": ["CHEBI:42517", "CHEBI:15017", "CHEBI:21128", "CHEBI:13318", "CHEBI:8782", "CHEBI:57618"]},
        # ammonium
        "CHEBI:28938": {"alt": ["CHEBI:22534", "CHEBI:49783", "CHEBI:7435"]},
        # ammonia
        "CHEBI:16134": {"alt": ["CHEBI:44284", "CHEBI:44269", "CHEBI:44404", "CHEBI:13405", "CHEBI:13406", "CHEBI:13407", "CHEBI:13771", "CHEBI:7434", "CHEBI:22533"]},
        # dioxygen, O2
        "CHEBI:15379": {"alt": ["CHEBI:44742", "CHEBI:7860", "CHEBI:10745", "CHEBI:13416", "CHEBI:23833", "CHEBI:25366", "CHEBI:29097", "CHEBI:30491"]},
        # carbon_dioxide, CO2
        "CHEBI:16526": {"alt": ["CHEBI:48829", "CHEBI:3283", "CHEBI:13282", "CHEBI:13283", "CHEBI:13285", "CHEBI:13284", "CHEBI:23011"]},
        # ca2+
        "CHEBI:29108": {"alt": ["CHEBI:3308", "CHEBI:22988", "CHEBI:48760"]},
        # coenzyme A
        "CHEBI:15346": {"alt": ["CHEBI:741566", "CHEBI:41631", "CHEBI:41597", "CHEBI:3771", "CHEBI:13294", "CHEBI:13295", "CHEBI:13298", "CHEBI:23355", "CHEBI:57287"]},

        # S_adenosyl_L_methionine
        "CHEBI:59789": {"alt": []},
        # S_adenosyl_L_homocysteine
        "CHEBI:57856": {"alt": []},

        # iron_2
        "CHEBI:29033": {"alt": ["CHEBI:34754", "CHEBI:49599", "CHEBI:13321", "CHEBI:13319", "CHEBI:21129", "CHEBI:24876"]},
        # iron_3
        "CHEBI:29034": {"alt": ["CHEBI:34755", "CHEBI:24877", "CHEBI:49595", "CHEBI:13320", "CHEBI:21130"]},

        # ITP
        "CHEBI:16039": {"alt": ["CHEBI:43508", "CHEBI:5851", "CHEBI:13374", "CHEBI:19272", "CHEBI:61402"]},
        # IDP
        "CHEBI:17808": {"alt": ["CHEBI:43252", "CHEBI:5848", "CHEBI:13371", "CHEBI:19270", "CHEBI:58280"]},
        # dITP
        "CHEBI:28807": {"alt": ["CHEBI:19251", "CHEBI:10499", "CHEBI:61382"]},

        # GDP
        "CHEBI:17552": {"alt": ["CHEBI:42738", "CHEBI:5212", "CHEBI:13327", "CHEBI:14379", "CHEBI:24448", "CHEBI:58189"]},
        # GTP
        "CHEBI:15996": {"alt": ["CHEBI:42934", "CHEBI:5234", "CHEBI:13342", "CHEBI:24451", "CHEBI:37565"]},
        # dGTP
        "CHEBI:16497": {"alt": ["CHEBI:10497", "CHEBI:19247", "CHEBI:14076", "CHEBI:61429"]},

        # UDP
        "CHEBI:17659": {"alt": ["CHEBI:46402", "CHEBI:9802", "CHEBI:13445", "CHEBI:27230", "CHEBI:58223"]},
        # UTP(4-)
        "CHEBI:15713": {"alt": ["CHEBI:13510", "CHEBI:9850", "CHEBI:27233", "CHEBI:46398"]},
        # dUTP
        "CHEBI:17625": {"alt": ["CHEBI:10533", "CHEBI:42215", "CHEBI:19264", "CHEBI:14095", "CHEBI:61555"]},

        # CDP
        "CHEBI:17239": {"alt": ["CHEBI:23519", "CHEBI:41451", "CHEBI:13254", "CHEBI:3260", "CHEBI:58069"]},
        # CTP
        "CHEBI:17677": {"alt": ["CHEBI:41675", "CHEBI:3285", "CHEBI:13286", "CHEBI:23522", "CHEBI:37563"]},
        # dCTP
        "CHEBI:16311": {"alt": ["CHEBI:19243", "CHEBI:41805", "CHEBI:10494", "CHEBI:14072", "CHEBI:61481"]},

        # ubiquinones
        "CHEBI:16389": {"alt": ["CHEBI:9852", "CHEBI:15279", "CHEBI:27186"]},
        # ubiquinol
        "CHEBI:17976": {"alt": ["CHEBI:9851", "CHEBI:27182", "CHEBI:15278"]},
        # ubiquinone-8
        "CHEBI:61683": {"alt": []},
        # ubiquinol-8
        "CHEBI:61682": {"alt": []},
        # hydroquinones
        "CHEBI:24646": {"alt": ["CHEBI:134188"]},
        # 1,4-benzoquinones
        "CHEBI:16509": {"alt": ["CHEBI:49820", "CHEBI:8730", "CHEBI:12837", "CHEBI:15009", "CHEBI:18927", "CHEBI:132124"]},

        # hydrogen donor
        "CHEBI:17499": {"alt": ["CHEBI:8785", "CHEBI:13233", "CHEBI:15018"]},
        # hydrogen acceptor
        "CHEBI:13193": {"alt": []},

        # L-cysteine residue
        "CHEBI:29950": {"alt": []},
        # L-lysinium residue
        "CHEBI:29969": {"alt": []},

        # Coblat 2-
        "CHEBI:48828": {"alt": ["CHEBI:48827", "CHEBI:23337"]},
        # Magnesium
        "CHEBI:18420": {"alt": ["CHEBI:49736", "CHEBI:6635", "CHEBI:13379", "CHEBI:25112"]},
        # Zinc 2+
        "CHEBI:29105": {"alt": ["CHEBI:49972", "CHEBI:49982", "CHEBI:10113", "CHEBI:27368"]},
    }

    COFACTOR_NAME_PATTERNS = ["residue"]
    _unfolded_cofactor_list = None

    @classmethod
    def get_factors_as_list(cls) -> list:
        """ Get factor list """
        if cls._unfolded_cofactor_list is None:
            ids = list(cls.COFACTORS.keys())
            alt = [idx for data in cls.COFACTORS.values() for idx in data["alt"]]
            cls._unfolded_cofactor_list = list(set([*ids, *alt]))
        return cls._unfolded_cofactor_list

    @classmethod
    def is_cofactor(cls, chebi_id: str, name: str = None, use_name_pattern=False):
        """
        Returns True if the compound is a cofactor, Fals otherwise
        """

        if name and use_name_pattern:
            for pattern in cls.COFACTOR_NAME_PATTERNS:
                if pattern in name:
                    return True

        return chebi_id in cls.get_factors_as_list()
