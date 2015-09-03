# -*- coding: utf-8 -*-


class Csv2Rdf:

    def __init__(self, filename):
        self.filename = filename

    def readInputFile(self):
        f = open(self.filename, 'r', encoding="utf-8")
        text = []
        for line in f:
            text.append(line)
        f.close()
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

    def printData(self, data):
        output = "|"
        for line in data:
            for value in line:
                output = output + value + '\t|'
            output = output + '\n|'
        print(output)


def main():
    cr = Csv2Rdf(input('Name of .csv file:'))
    cr.printData(cr.readTextInput())

if __name__ == '__main__':
    main()