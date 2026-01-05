

import csv
import os


class BKMS:
    """
    This module allows to parse and process the BKMS (Brend Kegg MetaCyc  and Sabio-RK) csv file
    obtained from http://bkms-react.tu-bs.de
    """

    @staticmethod
    def parse_csv_from_file(path, file) -> list:
        """
        Parses a .csv file

        :type path: str
        :param path: Location of the bkms file
        :type file: str
        :param file: Name of the bkms file
        :returns: list of dictionnaries reapresenting rows of the spreadsheet
        :rtype: list
        """
        bkms_file = f"{file}/Reactions_BKMS.csv"
        file_path = os.path.join(path, bkms_file)
        list__ = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                list__.append({key.lower() if type(key) == str else key: value for key, value in row.items()})

        return list__
