class SettingsImport():

    def importSettingsFromTextFile(self,filename):
        res = []
        f = open('datatest/%s.txt' % filename,'r')
        key = None
        for l in f:
            fields = l.replace('\n','').split('\t')
            if len(fields) and not fields[0].isdigit():
                key = fields
            if len(fields) and fields[0].isdigit() and key:
                dic = {}
                for k in range(len(fields)):
                    dic[key[k]] = fields[k]
                res.append(dic)
        return res

if __name__ == "__main__":

    r = SettingsImport()
    res = r.importSettingsFromTextFile('tvlimitaux')
    print(res)