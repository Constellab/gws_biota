

from pprint import pformat


class Param():
    """
    Adpater class that represents a BRENDA parameter

    :property name: Description of the parameter
    :type name: str
    :property value: Value of the parameter
    :type value: str
    :property refs: References numbers associated with the parameter value
    :type refs: list
    :property full_refs: Full references (pubmed id, or description) associated with the parameter value
    :type full_refs: list
    :property comments: Short comments extracted from the references
    :type comments: str
    """

    name: str = None
    data: dict = None
    refs: list = []
    full_refs: list = []
    comments: str = None

    def __init__(self, data=None, refs=None, full_refs=None, comments=None, name=None):
        self.data = data
        self.refs = refs
        self.full_refs = full_refs
        self.comments = comments
        self.name = name

    @property
    def value(self):
        if self.data is None:
            return None
        else:
            return self.data.get("data", None)

    def exists(self) -> bool:
        """
        Returns True if the parameter exists (i.e. `value` is not `None`)
        and False otherwise.

        :rtype: bool
        """
        return not self.value is None

    def get(self, key):
        return self.data.get(key, None)

    def to_json(self):
        return {
            "name": self.name,
            "value": self.value,
            "refs": self.refs
        }


class Params():
    """
    Adpater class that represents a list of BRENDA parameters
    """

    _name = None
    _data = None
    _full_refs = None

    _names = dict(
        AC="activating compound",
        AP="application",
        CF="cofactor",
        CL="cloned",
        CR="crystallization",
        EN="engineering",
        EXP="expression",
        GI="general information on enzyme",
        GS="general stability",
        IC50="IC-50 Value",
        ID="EC-class",
        IN="inhibitors",
        KKM="Kcat/KM-Value substrate in {...}",
        KI="Ki-value    inhibitor in {...}",
        KM="KM-value    substrate in {...}",
        LO="localization",
        ME="metals/ions",
        MW="molecular weight",
        NSP="natural substrates/products    reversibilty information in {...}",
        OS="oxygen stability",
        OSS="organic solvent stability",
        PHO="pH-optimum",
        PHR="pH-range",
        PHS="pH stability",
        PI="isoelectric point",
        PM="posttranslation modification",
        PR="protein",
        PU="purification",
        RE="reaction catalyzed",
        RF="references",
        REN="renatured",
        RN="accepted name (IUPAC)",
        RT="reaction type",
        SA="specific activity",
        SN="synonyms",
        SP="substrates/products    reversibilty information in {...}",
        SS="storage stability",
        ST="source/tissue",
        SU="subunits",
        SY="systematic name",
        TN="turnover number substrate in {...}",
        TO="temperature optimum",
        TR="temperature range",
        TS="temperature stability"
    )

    def __init__(self, name, data):
        self._name = name
        self._data = data.get(name, None)
        self._full_refs = data.get("references", None)

    # -- G --

    def __len__(self):
        if isinstance(self._data, list):
            return len(self._data)
        else:
            return 0

    def __getitem__(self, index=0):
        if isinstance(self._data, list):
            if index < len(self):
                if isinstance(self._data[index], str):
                    return Param(
                        data={'data': self._data[index]},
                        name=self._names[self._name]
                    )
                elif isinstance(self._data[index], dict):
                    return Param(
                        data=self._data[index],
                        refs=self._data[index].get("refs", None),
                        full_refs=self._full_refs,
                        comments=self._data[index].get("comment", None),
                        name=self._names[self._name]
                    )
                else:
                    return Param()
            else:
                return Param()
        else:
            return Param()

    def __str__(self):
        """
        String representation.
        """

        return pformat({
            "name": self._name,
            "data": self._data,
            "full_refs": self._full_refs
        })

    def to_json(self):
        data = []
        for param in self:
            data.append(param.to_json())
        return data
