from gws_core.model.typing_style import TypingStyle

from gws_core import Protocol, protocol_decorator, ProcessSpec
from .db_bto_creator import BtoDBCreator
from .db_compound_creator import CompoundDBCreator
from .db_eco_creator import EcoDBCreator
from .db_enzyme_creator import EnzymeDBCreator
from .db_go_creator import GoDBCreator
from .db_pathway_creator import PathwayDBCreator
from .db_protein_creator import ProteinDBCreator
from .db_reactions_creator import ReactionDBCreator
from .db_sbo_creator import SboDBCreator
from .db_taxonomy_creator import TaxonomyDBCreator


@protocol_decorator("UpdateBiotaDB",
                    style=TypingStyle.community_icon("database", background_color="#2b6d57"))
class UpdateBiotaDB(Protocol):
    def configure_protocol(self) -> None:
        bto: ProcessSpec = self.add_process(BtoDBCreator, "bto")
        compound: ProcessSpec = self.add_process(CompoundDBCreator, "compound")
        eco: ProcessSpec = self.add_process(EcoDBCreator, "eco")
        enzyme: ProcessSpec = self.add_process(EnzymeDBCreator, "enzyme")
        go: ProcessSpec = self.add_process(GoDBCreator, "go")
        pathway: ProcessSpec = self.add_process(PathwayDBCreator, "pathway")
        protein: ProcessSpec = self.add_process(ProteinDBCreator, "protein")
        reaction: ProcessSpec = self.add_process(ReactionDBCreator, "reaction")
        sbo: ProcessSpec = self.add_process(SboDBCreator, "sbo")
        taxonomy: ProcessSpec = self.add_process(TaxonomyDBCreator, "taxonomy")

        self.add_connectors([
            (eco >> "output_text", go << "input_text"),
            (go >> "output_text", sbo << "input_text"),
            (sbo >> "output_text", bto << "input_text"),
            (bto >> "output_text", compound << "input_text"),
            (bto >> "output_text", enzyme << "input_bto"),
            (bto >> "output_text", reaction << "input_bto"),
            (compound >> "output_text", pathway << "input_text"),
            (pathway >> "output_text", taxonomy << "input_text"),
            (pathway >> "output_text", enzyme << "input_pathway"),
            (pathway >> "output_text", reaction << "input_pathway"),
            (taxonomy >> "output_text", protein << "input_text"),
            (taxonomy >> "output_text", enzyme << "input_taxonomy"),
            (taxonomy >> "output_text", reaction << "input_taxonomy")
        ])

    # Ressource Text à mettre dans le output, vide ou avec une rapide description de ce qu"il s"est passé pour chaque database
    # Créer 3 inputs pour Rhea par exemple et les nommer pour que ce soit plus clair
    # input is_optional dans les inputspecs des différents scripts db
