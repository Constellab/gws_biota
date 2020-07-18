
import sys
import re
import os
from brendapy import BrendaParser

############################################################################################
#
#                                        Brenda class
#                                         
############################################################################################

class Brenda():
    parser = None  # reuse parser

    def __init__(self, file_path):
        self.parser = BrendaParser(brenda_file = file_path)
    
    def parse_all_protein_to_dict(self):
        list_proteins = []
        for ec in self.parser.keys():
            proteins = self.parser.get_proteins(ec)
            for p in proteins.values():
                dict_p = {}
                #Set main information about the enzyme
                dict_p['ec'] = p.ec
                dict_p['taxonomy'] = p.taxonomy
                dict_p['organism'] = p.organism
                dict_p['uniprot'] = p.uniprot

                #Set referenced name of the enzyme
                if (p.RN != None):
                    dict_p['name'] = list(p.RN)[0]

                #Set ec_group
                dict_p['ec_group'] = dict_p['ec'].split('.')[0]

                #Set activating compound
                list_copy = getattr(p, 'AC')
                if list_copy != None:
                    list_ac = []
                    for d in list_copy:
                        list_ac.append(d['data'])
                        if len(list_ac) <= 1:
                            dict_p['ac'] = list_ac[0]
                        else:
                            dict_p['ac'] = list_ac
                
                #Set cofactors
                list_copy = getattr(p, 'CF')
                if list_copy != None:
                    list_cf = []
                    for d in list_copy:
                        list_cf.append(d['data'])
                        if len(list_cf) <= 1:
                            dict_p['cf'] = list_cf[0]
                        else:
                            dict_p['cf'] = list_cf
                
                #Set cloned (CL)
                list_copy = getattr(p, 'CL')
                if list_copy != None:
                    list_cl = []
                    for d in list_copy:
                        list_cl.append(d['data'])
                        if len(list_cl) <= 1:
                            dict_p['cl'] = list_cl[0]
                        else:
                            dict_p['cl'] = list_cl
                
                #Set crystallization
                list_copy = getattr(p, 'CR')
                if list_copy != None:
                    list_cr = []
                    for d in list_copy:
                        list_cr.append(d['data'])
                        if len(list_cr) <= 1:
                            dict_p['cr'] = list_cr[0]
                        else:
                            dict_p['cr'] = list_cr
                
                #Set engeneering (EN)
                list_copy = getattr(p, 'EN')
                if list_copy != None:
                    list_en = []
                    for d in list_copy:
                        list_en.append(d['data'])
                        if len(list_en) <= 1:
                            dict_p['en'] = list_en[0]
                        else:
                            dict_p['en'] = list_en
                
                #Set expression (EXP)
                list_copy = getattr(p, 'EXP')
                if list_copy != None:
                    list_exp = []
                    for d in list_copy:
                        list_exp.append(d['data'])
                        if len(list_exp) <= 1:
                            dict_p['exp'] = list_exp[0]
                        else:
                            dict_p['exp'] = list_exp

                #Set general information on enzyme (GI)
                list_copy = getattr(p, 'GI')
                if list_copy != None:
                    list_gi = []
                    for d in list_copy:
                        list_gi.append(d['data'])
                        if len(list_gi) <= 1:
                            dict_p['gi'] = list_gi[0]
                        else:
                            dict_p['gi'] = list_gi

                #Set general stability (GS)
                list_copy = getattr(p, 'GS')
                if list_copy != None:
                    list_gs = []
                    for d in list_copy:
                        list_gs.append(d['data'])
                        if len(list_gs) <= 1:
                            dict_p['gs'] = list_gs[0]
                        else:
                            dict_p['gs'] = list_gs

                #Set IC-50
                list_copy = getattr(p, 'IC50')
                if list_copy != None:
                    list_IC50 = []
                    for d in list_copy:
                        try:
                            list_IC50.append({'value': str(d['data']), 'units':d['units'], 'substrate': d['substrate']})
                            if len(list_IC50) <= 1:
                                dict_p['ic50'] = list_IC50[0]
                            else:
                                dict_p['ic50'] = list_IC50
                        except:
                            pass
                            #print('missing value or units or substrate')
                        
                """
                #Set EC-class (ID)
                list_copy = getattr(p, 'ID')
                if (list_copy != None):
                    print(list_copy)
                    list_ID = []
                    
                    for d in list_copy:
                        list_ID.append(d['data'])
                        print(list_ID)
                        if(len(list_ID) <= 1):
                                dict_p['ID'] = list_ID[0]
                            else:
                                dict_p['ID'] = list_ID
                    print(dict_p['ID'])
                """


                #Set Inhibitors (IN)
                list_copy = getattr(p, 'IN')
                if list_copy != None:
                    list_in = []
                    for d in list_copy:
                        list_in.append(d['data'])
                    dict_p['in'] = list_in

                #Set localisation
                list_copy = getattr(p, 'LO')
                if list_copy != None:
                    list_lo = []
                    for d in list_copy:
                        list_lo.append(d['data'])
                    dict_p['lo'] = list_lo

                #Set metals/ions
                list_copy = getattr(p, 'ME')
                if list_copy != None:
                    list_me = []
                    for d in list_copy:
                        list_me.append(d['data'])
                        if len(list_me) <= 1:
                            dict_p['me'] = list_me[0]
                        else:
                            dict_p['me'] = list_me
                
                #Set molecular weight
                list_copy = getattr(p, 'MW')
                if list_copy != None:
                    list_mw = []
                    for d in list_copy:
                        list_mw.append(d['data'])
                        if len(list_mw) <= 1:
                            dict_p['mw'] = list_mw[0]
                        else:
                            dict_p['mw'] = list_mw
                
                #Set natural substrates and product
                list_copy = getattr(p, 'NSP')
                if list_copy != None:
                    list_nsp = []
                    for d in list_copy:
                        list_nsp.append(d['data'])
                    dict_p['nsp'] = list_nsp

                #Set Oxygen stability
                list_copy = getattr(p, 'OS')
                if list_copy != None:
                    list_os = []
                    for d in list_copy:
                        try:
                            list_os.append(d['data'])
                        except:
                            pass
                            #print('can not extract oxygen stability')

                        if len(list_os) <= 1:
                            dict_p['os'] = list_os[0]
                        else:
                            dict_p['os'] = list_os
                
                #Set Organic solvent stability
                list_copy = getattr(p, 'OSS')
                if list_copy != None:
                    list_oss = []
                    for d in list_copy:
                        try:
                            list_oss.append(d['data'])
                        except:
                            pass
                            #print('can not extract oxygen stability')

                        if len(list_oss) <= 1:
                            dict_p['oss'] = list_oss[0]
                        else:
                            dict_p['oss'] = list_oss

                #Set pH Optimum
                list_copy = getattr(p, 'PHO')
                if list_copy != None:
                    list_pho = []
                    for d in list_copy:
                        list_pho.append(d['data'])
                        if(len(list_pho) <= 1):
                            dict_p['pho'] = list_pho[0]
                        else:
                            dict_p['pho'] = list_pho

                #Set pH Range
                list_copy = getattr(p, 'PHR')
                if list_copy != None:
                    list_phr = []
                    for d in list_copy:
                        list_phr.append(d['data'])
                    dict_p['phr'] = list_phr
                
                #Set pH Stability
                list_copy = getattr(p, 'PHS')
                if list_copy != None:
                    list_phs = []
                    for d in list_copy:
                        list_phs.append(d['data'])
                        if(len(list_phs) <= 1):
                            dict_p['phs'] = list_phs[0]
                        else:
                            dict_p['phs'] = list_phs
                
                #Set isoelectirc point
                list_copy = getattr(p, 'PI')
                if list_copy != None:
                    list_pi = []
                    for d in list_copy:
                        list_pi.append(d['data'])
                        if(len(list_pi) <= 1):
                            dict_p['pi'] = list_pi[0]
                        else:
                            dict_p['pi'] = list_pi

                #Set posttranslation modification
                list_copy = getattr(p, 'PM')
                if list_copy != None:
                    list_pm = []
                    for d in list_copy:
                        list_pm.append(d['data'])
                    dict_p['pm'] = list_pm
                
                #Set purification
                list_copy = getattr(p, 'PU')
                if list_copy != None:
                    list_pu = []
                    for d in list_copy:
                        list_pu.append(d['data'].replace('(', '').replace(')',''))
                        if len(list_pu) <= 1:
                            dict_p['pu'] = list_pu[0]
                        else:
                            dict_p['pu'] = list_pu
                
                
                
                #Set Reaction catalyzed
                """
                list_copy = getattr(p, 'RE')
                if (list_copy != None):
                    print(list_copy)
                    list_re = []
                    
                    for d in list_copy:
                        list_re.append(d['data'])
                        if(len(list_re) <= 1):
                            dict_p['re'] = list_re[0]
                        else:
                            dict_p['re'] = list_re
                """
                #Set renatured (REN)
                list_copy = getattr(p, 'REN')
                if list_copy != None:
                    list_ren = []
                    for d in list_copy:
                        list_ren.append(d['data'].replace('(', '').replace(')',''))
                        if len(list_ren) <= 1:
                            dict_p['ren'] = list_ren[0]
                        else:
                            dict_p['ren'] = list_ren
                
                #Set references
                list_copy = getattr(p, 'references')
                if list_copy != None:
                    list_ref = []
                    for key in list_copy.keys():
                        if 'pubmed' in list_copy[key].keys():
                            try:
                                list_ref.append(list_copy[key]['pubmed'])
                            except:
                                pass
                                #print('can not exctract pubmed id')

                    dict_p['refs'] = list_ref
                
                #Set reaction type
                """
                list_copy = getattr(p, 'RT')
                if (list_copy != None):
                    print(list_copy)
                    list_rt = []
                    
                    for d in list_copy:
                        
                        list_rt.append(d['data'])
                        if(len(list_rt) <= 1):
                            dict_p['rt'] = list_rt[0]
                        else:
                            dict_p['rt'] = list_rt
                """
                #Set specific activity
                list_copy = getattr(p, 'SA')
                if (list_copy != None):
                    list_sa = []
                    for d in list_copy:
                        try:
                            list_sa.append({'value': str(d['value']), 'units':d['units']})
                            if(len(list_sa) <= 1):
                                dict_p['sa'] = list_sa[0]
                            else:
                                dict_p['sa'] = list_sa
                        except:
                            pass
                            #print('No value available for specific activity')

                #Set synonyms
                list_copy = getattr(p, 'SN')
                if (list_copy != None):
                    list_sn = []
                    for d in list_copy:
                        list_sn.append(d)
                        if(len(list_sn) <= 1):
                            dict_p['sn'] = list_sn[0]
                        else:
                            dict_p['sn'] = list_sn

                #Set systematic name
                list_copy = getattr(p, 'SY')
                if (list_copy != None):
                    list_sy = []
                    for d in list_copy:
                        list_sy.append(d['data'])
                        if(len(list_sy) <= 1):
                            dict_p['sy'] = list_sy[0]
                        else:
                            dict_p['sy'] = list_sy

                #Set subunits
                list_copy = getattr(p, 'SU')
                if (list_copy != None):
                    list_su = []
                    for d in list_copy:
                        list_su.append(d['data'])
                        if(len(list_su) <= 1):
                            dict_p['su'] = list_su[0]
                        else:
                            dict_p['su'] = list_su

                #Set temperature optimum
                list_copy = getattr(p, 'TO')
                if (list_copy != None):
                    list_to = []
                    for d in list_copy:
                        list_to.append(d['data'])
                        if(len(list_to) <= 1):
                            dict_p['to'] = list_to[0]
                        else:
                            dict_p['to'] = list_to
                    dict_p['to'] = list_to

                #Set temperature range
                list_copy = getattr(p, 'TR')
                if (list_copy != None):
                    list_tr = []
                    for d in list_copy:
                        list_tr.append(d['data'])
                    dict_p['tr'] = list_tr
                
                #Set temperature stability
                list_copy = getattr(p, 'TS')
                if (list_copy != None):
                    list_ts = []
                    for d in list_copy:
                        list_ts.append(d['data'])
                        if(len(list_ts) <= 1):
                            dict_p['ts'] = list_ts[0]
                        else:
                            dict_p['ts'] = list_ts
                
                #Set source tissue
                list_copy = getattr(p, 'ST')
                if (list_copy != None):
                    list_st = []
                    for d in list_copy:
                        try:
                            list_st.append(d['bto'])
                        except:
                            #print("Can not extract bto")
                            list_st.append("")

                        if(len(list_st) <= 1):
                            dict_p['st'] = list_st[0]
                        else:
                            dict_p['st'] = list_st

                #Set kinetics information about the enzyme: KKM, KI, KM
                list_copy = getattr(p, 'KKM')
                if (list_copy != None):
                    list_kkm = []
                    for d in list_copy:
                        try:
                            list_kkm.append({'value': str(d['data']), 'units':d['units']})
                        except:
                            list_kkm.append(d['units'])

                        if(len(list_kkm) <= 1):
                            dict_p['kkm'] = list_kkm[0]
                        else:
                            dict_p['kkm'] = list_kkm

                list_copy = getattr(p, 'KI')
                if (list_copy != None):
                    list_ki = []
                    for d in list_copy:
                        try:
                            list_ki.append({'value': str(d['value']), 'units':d['units'], 'substrate': d['substrate']})
                        except:
                            #print("value not available")
                            list_ki.append({})

                        if(len(list_ki) <= 1):
                            dict_p['ki'] = list_ki[0]
                        else:
                            dict_p['ki'] = list_ki
                
                list_copy = getattr(p, 'KM')

                if (list_copy != None):
                    list_km = []
                    for d in list_copy:
                        copy_dict = d
                        try:
                            del copy_dict['data']
                            del copy_dict['refs']
                            del copy_dict['comment'] 
                            del copy_dict['substrate']
                            del copy_dict['chebi']
                            #to remove unexpected character in comment use re.findall("#\d#" or "#\d,\d#", "<\d>")
                        except:
                            pass
                            #print('remove error')

                        if('value' and 'units' in copy_dict.keys()):
                            try:
                                list_km.append({'value': str(d['value']), 'units':d['units']})
                            except:
                                pass
                                #print("no value available ")

                            if(len(list_km) == 1):
                                dict_p['km'] = list_km[0]
                            else:
                                dict_p['km'] = list_km
                
                list_copy = getattr(p, 'TN')

                if (list_copy != None):
                    list_tn = []

                    for d in list_copy:
                        
                        copy_dict = d
                        try:
                            del copy_dict['data']
                            del copy_dict['refs']
                            del copy_dict['comment'] 
                            del copy_dict['substrate']
                            del copy_dict['chebi']
                        except:
                            pass
                            #print('remove error')

                        if('value' and 'units' in copy_dict.keys()):
                            try:
                                list_tn.append({'value': str(copy_dict['value']), 'units': copy_dict['units']})
                            except:
                                pass
                                #print("no value available: ")

                            if(len(list_tn) == 1):
                                dict_p['tn'] = list_tn[0]
                            else:
                                dict_p['tn'] = list_tn

                list_proteins.append(dict_p)

        return(list_proteins)
