# -*- coding: utf-8 -*-
from iso3166 import countries

class Csv2Rdf:

    def __init__(self, filename):
        self.filename = filename

    def readInputFile(self):
        f = open(self.filename + '.csv', 'r', encoding="utf-8")
        text = []
        for line in f:
            text.append(line)
        f.close()
        return text

    def readTemplate(self, name):
        t = open(name, 'r', encoding="utf-8")
        text = []
        for line in t:
            text.append(line)
        t.close()
        return text

    def readTextInput(self, splitter):
        text = self.readInputFile()
        labels = []
        data = []
        for label in text[0].split(splitter, -2):
            if not '\n' in label:
                if '\ufeff' in label:
                    labels.append(label[1:])
                else:
                    labels.append(label)
        data.append(labels)
        for entry in text[1:]:
            lineData = []
            for value in entry.split(splitter, -2):
                if not '\n' in value:
                    lineData.append(value)
            data.append(lineData)
        return data

    def readMultilineInput(self, splitter):
        text = self.readInputFile()
        labels = []
        data = []
        for label in text[0].split(splitter):
            if '\n' != label:
                if '\ufeff' in label:
                    labels.append(label[1:])
                else:
                    labels.append(label)
        data.append(labels)
        toggle = False
        newLineData= True
        for entry in text[1:]:
            if newLineData:
                lineData = []
                newLineData = not newLineData
            for value in entry.split(splitter):
                if len(value) > 1:
                    value[:2].replace('"','')
                    value[-3:].replace('"','')
                    value[:2].replace("'",'')
                    value[-3:].replace("'",'')
                if toggle:
                    lineData[-1] = lineData[-1] + value.replace('ᛘ','')
                else:
                    if value == '\n':
                        value = ''
                    lineData.append(value.replace('ᛘ',''))
                if 'ᛘ' in value:
                    toggle = not toggle
            if (len(data[0]) == len(lineData)):
                lineData[-1] = lineData[-1][:-1]
                data.append(lineData)
                newLineData = not newLineData
        return data

    def createOutput(self, data):
        template = self.readTemplate(self.filename + '_template.ttl')
        if self.filename == 'employment':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                        'qb:dataSet\tstatbel:dataset-employmentUnemployment;\n\t' +
                        'sdmx-dimension:refPeriod\t"' + self.transferQuartal(entry[0][-4:], entry[0][1]) + '"^^xsd:date;\n\t' +
                        'statbel:employed\t' + entry[3] + ';\n\t' +
                        'statbel:unemployed\t' + entry[1] + ';\n\t' +
                        'statbel:inactive\t' + entry[2] + ';\n\t.\n\n')
                template.append(output)
        elif self.filename == 'hpi':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                        'qb:dataSet\tstatbel:dataset-hpi;\n\t'
                        'sdmx-dimension:refPeriod\t"' + self.transferQuartal(entry[0][:4], entry[0][-1]) + '"^^xsd:date;\n\t' +
                        'statbel:inflation\t' + entry[1].replace(',','.') + ';\n\t.\n\n')
                template.append(output)
        elif self.filename == 'cordis_projects':
            for entry in data[1:]:
                template.append(self.createCordisProjects(entry))
        of = open(self.filename + '_output.ttl', 'w', encoding="utf-8")
        for line in template:
            of.write(line)
        of.close

    def createCordisProjects(self, entry):
        output = ('cordis:' + entry[0] + ' a doap:Project ;\n\t' +
                    'doap:name\t' + entry[2] + ';\n\t' +
                    'dc:title\t' + entry[7] + ';\n\t')
        if len(entry[10]) > 1:
            output = output + 'doap:homepage\t' + entry[10] + ';\n\t'
        output = output + 'doap:description\t' + entry[11] + ';\n\t'
        return output


    def transferQuartal(self, year, quartal):
        return str(int(year) + 1*(quartal == '4')) + '-' + '0'*(quartal != '3') + str((int(quartal)*3 + 1)%12) + '-01'

    def alpha2Name(self, alpha2):
        return countries.get(alpha2).name

    """
    Testmethod
    """
    def printData(self, data):
        output = "|"
        for line in data:
            for value in line:
                output = output + value + '\t|'
            output = output + '\n|'
        print(output)


def main():
    file = input('Name of .csv file:')
    cr = Csv2Rdf(file)
    if 'cordis' in file:
        cr.createOutput(cr.readMultilineInput('ᛥ'))
    else:
        cr.createOutput(cr.readTextInput(';'))

if __name__ == '__main__':
    main()