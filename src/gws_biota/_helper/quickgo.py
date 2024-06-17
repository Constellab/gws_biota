

import requests
from gws.settings import Settings


class QuickGOAnnotation():
    """

    This module allows to get results of a quickgo annotation research from an uniprot identifiers.
    Results are return in a python readable and exploitable format

    """
    @classmethod
    def get_tsv_file_from_uniprot_id(cls, uniprot_id):
        """
        Get results of a quickgo annotation research from an uniprot identifiers

        Use the quickgo API to request QuickGO

        Request internet connection.

        Call the __parse_tsv_from_file() intern function to parse first results


        :type uniprot_id: str
        :param uniprot_id: Uniprot id of a protein
        :returns: list of dictionnaries where each rows correspond to a results given by the request
        :rtype: list

        """

        settings = Settings.get_instance()
        URL = settings.get_variable("biota:quickgo_api_url")
        try:
            requestURL = URL + str(uniprot_id)
            r = requests.get(requestURL, headers={ "Accept" : "text/tsv"})

            if not r.ok:
                r.raise_for_status()
            else:
                responseBody = r.text
                text = responseBody.split('\n')
                text = text[0:len(text)-1]
                list_return = cls.__parse_tsv_from_file(text)
            return(list_return)

        except:
            pass
            #print('Can not find the uniprot id ' + uniprot_id + ' on QuickGO')

    @classmethod
    def __parse_tsv_from_file(cls, list_text) -> list:
        """
        Parse a tsv file of quickgo annotations research from an uniprot identifiers

        It is assumed that the firt row of the spreadsheet is the location of the columns

        This tool accepts tab (\t) separated value files (.csv) as well as excel
        (.xls, .xlsx) files

        :type list_text: str
        :param list_text: Response of the request in list format, each indexs of the list represent
        a raw of the response text
        :returns: list of dictionnaries where each rows correspond to a results given by the request
        :rtype: list

        """
        list_annotations = []
        line_count = 0
        for i in range(0, len(list_text)):
            if(line_count < 1):
                infos_table = list_text[0].split('\t')
                infos_table[len(infos_table)-1] = infos_table[len(infos_table)-1].replace('\n', '')
                for i in range(0, len(infos_table)):
                    infos_table[i] = infos_table[i].lower()
                line_count += 1
            else:
                dict_annotation = {}
                for j in range(0, len(infos_table)):
                    list_info = list_text[i].split('\t')
                    list_info[len(list_info)-1] = list_info[len(list_info)-1].replace('\n', '')
                    dict_annotation[infos_table[j]] = list_info[j]
                list_annotations.append(dict_annotation)
        return(list_annotations)


