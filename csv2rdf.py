# -*- coding: utf-8 -*-


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

    def readTextInput(self):
        text = self.readInputFile()
        labels = []
        data = []
        for label in text[0].split(';', -2):
            if not '\n' in label:
                if '\ufeff' in label:
                    labels.append(label[1:])
                else:
                    labels.append(label)
        data.append(labels)
        for entry in text[1:]:
            lineData = []
            for value in entry.split(';', -2):
                if not '\n' in value:
                    lineData.append(value)
            data.append(lineData)
        return data

    def createOutput(self, data):
        template = self.readTemplate(self.filename + '_template.ttl')
        if self.filename == 'employment':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                        'qb:dataSet\tstatbel:dataset-employmentUnemployment;\n\t' +
                        'sdmx-dimension:refPeriod\t"' + entry[0] + '"^^dc:date;\n\t' +
                        'statbel:employed\t' + entry[3] + ';\n\t' +
                        'statbel:unemployed\t' + entry[1] + ';\n\t' +
                        'statbel:inactive\t' + entry[2] + ';\n\t.\n\n')
                template.append(output)
        elif self.filename == 'hpi':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                        'sdmx-dimension:refPeriod\t"' + entry[0][4:6] + '/' + entry[0][:4] + '"^^dc:date;\n\t' +
                        'statbel:inflation\t' + entry[1] + '\n\t.\n\n')
                template.append(output)
        of = open(self.filename + '_output.ttl', 'w', encoding="utf-8")
        for line in template:
            of.write(line)
        of.close

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
    cr = Csv2Rdf(input('Name of .csv file:'))
    cr.createOutput(cr.readTextInput())

if __name__ == '__main__':
    main()