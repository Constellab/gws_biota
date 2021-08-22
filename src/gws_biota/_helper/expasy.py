import sys
import os
import re
import csv

reg = re.compile("(\d+\.[\d\-\s]+\.[\d\-\s]+\.[\d\-\s]+)\s+(.+)")

class Expasy():
    
    @staticmethod
    def parse_all_enzclasses_to_dict(path, file) -> list:
        """
        Parses a .csv file

        :type path: str
        :param path: Location of the spreadsheet
        :type file: str
        :param file: Name of the spreadsheet
        :returns: list of dictionnaries reapresenting rows of the spreadsheet
        :rtype: list
        """
        
        file_path = os.path.join(path, file)
        list__ = []
        with open(file_path, newline='') as fp:
            tab = fp.readlines()
            for line in tab:
                found = reg.search(line)
                if found:
                    list__.append({
                        'ec_number': found.group(1).replace(" ", ""),
                        'data': {
                            'name': found.group(2).strip(".")
                        }
                    })
        return list__
