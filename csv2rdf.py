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
        for label in text[0].split(';', -2):
            if not '\n' in label:
                labels.append(label)



def main():
    cr = Csv2Rdf(input('Name of .csv file:'))
    cr.readTextInput()

if __name__ == '__main__':
    main()