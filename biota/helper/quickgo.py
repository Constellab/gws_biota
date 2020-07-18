import requests
from gws.settings import Settings

############################################################################################
#
#                         QuickGo annotations loader and parser
#                                         
############################################################################################


class QuickGOAnnotation():

    @classmethod
    def get_tsv_file_from_uniprot_id(cls, uniprot_id):
        settings = Settings.retrieve()
        URL = settings.get_data('quickgo_api_url')
        try:
            requestURL = URL + str(uniprot_id)
            r = requests.get(requestURL, headers={ "Accept" : "text/tsv"})

            if not r.ok:
                r.raise_for_status()
            else:
                responseBody = r.text
                text = responseBody.split('\n')
                text = text[0:len(text)-1]
                list_annotations = []
                list_return = cls.__parse_tsv_from_file(text, list_annotations)
            return(list_return)

        except:
            pass
            #print('Can not find the uniprot id ' + uniprot_id + ' on QuickGO')

    @classmethod
    def __parse_tsv_from_file(cls, list_text, list_annotations) -> list:
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
                        
            
                