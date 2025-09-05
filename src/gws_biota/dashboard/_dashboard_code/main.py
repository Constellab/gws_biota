#packages à installer : pip install stmol==0.0.9   pip install py3Dmol==2.0.0.post2  pip install ipython_genutils
# pip install rcsbsearchapi

import os
import pandas as pd
import streamlit as st
from gws_biota import Compound as BiotaCompound
from gws_biota import Protein

from stmol import *
import py3Dmol
import requests

from rcsbsearchapi.search import TextQuery

# thoses variable will be set by the streamlit app
# don't initialize them, there are create to avoid errors in the IDE
sources: list
params: dict

# Your Streamlit app code here
st.title("Biota Dashboard ")

#a = BiotaCompound.select().where(BiotaCompound.chebi_id == "CHEBI:17234")

        # result = Protein.select().where(Protein.uniprot_id == "P11411")

        # for compound in result:
        #     compound_data = {
        #         "name": compound.name,
        #         "data": compound.data,
        #         "uniprot_id": compound.uniprot_id,
        #         "uniprot_db": compound.uniprot_db,
        #         "uniprot_gene": compound.uniprot_gene,
        #         "evidence_score": compound.evidence_score,
        #         "tax_id": compound.tax_id
        #     }
        #     st.write(compound_data)

def show_content(type : str):

    #Create tabs
    tab_infos, tab_visu= st.tabs(["Infos", "Visualisation"])

    with tab_infos:
        chebi_user = st.text_input("Chebi", "CHEBI:17234")
        name_user = st.text_input("Name", "Glucose")

        if chebi_user :
            result = BiotaCompound.select().where(BiotaCompound.chebi_id == chebi_user)
        elif name_user :
            result = BiotaCompound.select().where(BiotaCompound.name.contains(name_user))

        # Prepare the list to store compound data
        compound_list = []
        for compound in result:
            compound_data = {"id": compound.id,"created_at": compound.created_at,"last_modified_at": compound.last_modified_at,
                "name": compound.name,"data": compound.data,"ft_names": compound.ft_names,
                "chebi_id": compound.chebi_id,"kegg_id": compound.kegg_id,"metacyc_id": compound.metacyc_id,
                "formula": compound.formula,"charge": compound.charge,"mass": compound.mass,
                "monoisotopic_mass": compound.monoisotopic_mass, "inchi": compound.inchi,"inchikey": compound.inchikey,
                "smiles": compound.smiles, "chebi_star": compound.chebi_star}

            compound_list.append(compound_data)

        # Convert to DataFrame for better display
        compound_df = pd.DataFrame(compound_list)
        # Display the compounds in a nice table
        st.write("## Compound Table")
        st.dataframe(compound_df)


    with tab_visu :
        name_compound_selected = st.selectbox("Sélectionnez le métabolite qui vous intéresse", compound_df["name"].to_list())

        q1 = TextQuery(name_compound_selected)
        list_pdb_id = []
        for assemblyid in q1("assembly"):
            list_pdb_id.append(assemblyid)
            if len(list_pdb_id) ==10 :
                break

        pdb_selected = st.selectbox("PDB ID - seuls les 10 premiers sont affichés", list_pdb_id)

        bcolor = st.color_picker('Pick A Color','#F3F3F3')
        style = st.selectbox('style',['cartoon','line','cross','stick','sphere'])
        protein = pdb_selected.split("-")[0]
        xyzview = py3Dmol.view(query='pdb:'+protein)
        xyzview.setStyle({style:{'color':'spectrum'}})
        xyzview.setBackgroundColor(bcolor)
        showmol(xyzview, height = 500,width=800)







# Sidebar navigation
st.sidebar.header("Sélectionnez les résultats à afficher :")
# Main level selection
type_selected = st.sidebar.radio("Sélectionnez", ["Métabolites", "Réactions"])
# Sublevel selection based on main level
if type_selected :
    show_content(type=type_selected)