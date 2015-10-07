# -*- coding: utf-8 -*-
from iso3166 import countries
from datetime import date
from organization import Organization
from project import Project
from person import Person

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
                if '"' in value or "'" in value:
                    value.replace('"','')
                    value.replace("'",'')
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
        elif self.filename == 'cordis_organizations':
            for entry in data[1:]:
                template.append(self.createCordisOrganizations(entry))
        of = open(self.filename + '_output.ttl', 'w', encoding="utf-8")
        for line in template:
            of.write(line)
        of.close

    def createCordisProjects(self, entry):
        output = ('cordis:' + entry[0] + ' a dbc:ResearchProject;\n\t' +
                  'dbc:projectReferenceID\t' + entry[1] + ';\n\t' +
                  'doap:name\t' + entry[2] + ';\n\t' +
                  'dc:title\t' + entry[7] + ';\n\t')
        if len(entry[10]) > 1:
            output = output + 'doap:homepage\t' + entry[10] + ';\n\t'
        if len(entry[8]) > 1:
            output = output + ( 'dbc:projectStartDate\t' + entry[8].split('/')[2] + '-' + entry[8].split('/')[0] + '-' + entry[8].split('/')[1] + '^^xsd:date;\n\t' +
                                'dbc:projectEndDate\t' + entry[9].split('/')[2] + '-' + entry[9].split('/')[0] + '-' + entry[9].split('/')[1] + '^^xsd:date;\n\t')
            #'dc:PeriodOfTime\t' + str((date(int(entry[9].split('/')[2]), int(entry[9].split('/')[0]), int(entry[9].split('/')[1])) - date(int(entry[8].split('/')[2]), int(entry[8].split('/')[0]), int(entry[8].split('/')[1]))).days) + ';\n\t'
        if len(entry[3]) > 1:
            output = output + 'cordis:status\t' + self.transcribeStatus(entry[3]) + ';\n\t'
        output = output + ('cordis:programme\t' + entry[4] + ';\n\t' +
                           'cordis:frameworkProgramme\t' + entry[6] + ';\n\t' +
                           'cordis:projectTopics\t' + entry[5] + ';\n\t')
        if len(entry[14]) > 1:
            output = output + 'cordis:projectFundingScheme' + entry[14] + ';\n\t'
        output = output + ('dbc:projectBudgetFunding\t' + entry[13].replace(',','.') + '^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbc:projectBudgetTotal\t' + entry[12].replace(',','.') +'^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbc:projectCoordinator\t' + entry[16] + ';\n\t' +
                           'cordis:projectCoordinatorCountry\t' + 'dbr:' + self.alpha2Name(entry[17]) + ';\n\t')
        if len(entry[18]) > 1:
            for participant in entry[18].split(';'):
                output = output + '<http://dbpedia.org/ontology/projectParticipant>\t' + participant + ';\n\t'
        if len(entry[19]) > 1:
            for country in entry[19].split(';'):
                output = output + 'cordis:projectParticipantCountry\t' + 'dbr:' + self.alpha2Name(country) + ';\n\t'
        if len(entry[20]) > 1:
            for subject in entry[20].split(';'):
                output = output + 'cordis:projectSubject\t' + subject + ';\n\t'
        output = output + 'dbc:projectObjective\t' + entry[11] + ';\n\t.\n\n'
        return output

    def createCordisOrganizations(self, entry):
        output = ('cordis:' + entry[6] + entry[0] + ' a dbc:ResearchProject, doap:project, rdf:type;\n\t' +
                  'dbc:projectReferenceID\t' + self.setLiterals(entry[1]) + ';\n\t' +
                  'doap:name\t' + self.setLiterals(entry[2]) + ';\n\t'
                  # 'cordis:role\t' + entry[3] + ';\n\t'
                                                               'foaf:organization\t [cordis:organizationName\t' + self.setLiterals(entry[5]) + ';\n\t\t' +
                  'cordis:organizationShortName\t' + self.setLiterals(entry[6]) + ';\n\t\t')
        if len(entry[10]) > 1:
            output = output + 'cordis:organizationCountry\tdbr:' + self.alpha2Name(entry[10]) + ';\n\t\t'
        if len(entry[7]) > 1:
            output = output + 'cordis:activityType\t' + entry[7] + ';\n\t\t'
        if len(entry[8]) > 1:
            output = output + 'cordis:endOfParticipation\t' + entry[8] + ';\n\t\t'
        if len(entry[9]) > 1:
            output = output + 'dbc:projectBudgetFunding\t' + entry[9].split('.')[0] + '^^<http://dbpedia.org/datatype/euro>;\n\t\t'
        if len(entry[12]) > 1:
            output = output + 'dbc:locationCity\t' + '<http://dbpedia.org/page/' + self.capitalizeAll(entry[12]) + '>;\n\t'
        if len(entry[11]) > 1:
            output = output + 'dbo:address\t' + entry[11] + ';\n\t'
        if len(entry[13]) > 1:
            output = output + '<http://dbpedia.org/ontology/postalCode>\t' + entry[13] + ';\n\t'
        if len(entry[14]) > 1:
            output = output + 'cordis:organizationHomepage\t' + (entry[14][:4] != 'http')*'http://' + entry[14] + ';\n\t'
            # if len(entry[15]) > 1:
            #     output = output + 'cordis:contactType\t' + entry[15] +';\n\t'
        if len(entry[16]) > 1:
            output = output + 'foaf:title\t' + entry[16] + ';\n\t'
        if len(entry[17]) > 1:
            output = output + 'foaf:firstName\t' + entry[17] + ';\n\t'
        if len(entry[18]) > 1:
            output = output + 'foaf:lastName\t' + entry[18] + ';\n\t'
        if len(entry[20]) > 1:
            output = output + 'foaf:phone\t' + entry[20] + ';\n\t'
        if len(entry[21]) > 1:
            output = output + 'cordis:faxNumber\t' + entry[21] + ';\n\t'
        if len(entry[22]) > 1:
            output = output + 'foaf:mbox\t' + entry[22] + ';\n\t'
        output = output + '.\n\n'
        return output

    def parseCordisProject(self, entry):
        project = Project()
        project.identifier = entry[0]
        project.referenceID = entry[1]
        project.name = entry[2]
        project.homepage = entry[10]
        project.startDate = entry[8]
        project.endDate = entry[9]
        project.status = self.transcribeStatus(entry[3])
        project.frameworkProgramme = entry[6]
        project.topics = entry[5]
        project.fundingScheme = entry[14]
        project.budgetTotal = entry[12]
        project.budgetFunding = entry[13]
        return project

    def parseCordisOrganization(self, entry):
        org = Organization()
        org.identifier = entry[0]
        org.referenceID = entry[1]
        org.projectName = entry[2]
        org.role = entry[3]
        org.name = entry[5]
        org.shortName = entry[6]
        if len(entry[10]) > 1:
            org.country = self.alpha2Name(entry[10])
        org.activityType = entry[7]
        org.endOfParticipation = entry[8]
        org.city = 'http://dbpedia.org/page/' + self.capitalizeAll(entry[12])
        org.postalCode = entry[13]
        org.street = entry[11]
        org.homepage = (entry[14][:4] != 'http')*'http://' + entry[14]
        return org

    def parseCordisPerson(self, entry):
        person = Person()
        person.type = entry[15]
        person.title = entry[16]
        person.firstName = entry[17]
        person.lastName = entry[18]
        person.phone = entry[20]
        person.fax = entry[21]
        person.mail = entry[22]
        return person

    def createCordisObjects(self, projectsData, organizationData):
        projects = []
        organizations = []
        persons = []
        for project in projectsData[1:]:
            projects.append(self.parseCordisProject(project))
        for organization in organizationData[1:]:
            organizations.append(self.parseCordisOrganization(organization))
            persons.append(self.parseCordisPerson(organization))
        for pro in projects:
            print(pro)
        for org in organizations:
            print(org)
        for per in persons:
            print(per)

    def setLiterals(self, string):
        return (string[0] != '"') * '"' + string + (string[-1] != '"') * '"'

    def capitalizeAll(self, string):
        output = ''
        for word in string.split(' '):
            output = output + word.capitalize()
        return output

    """
    legacy
    """
    def setYesNoBool(self, yn):
        if yn == 'yes':
            return True
        else:
            return False

    def transcribeStatus(self, status):
        if status == 'ONG':
            return 'ongoing'
        elif status == 'CAN':
            return 'cancelled'
        else:
            return 'undefined'

    def transferQuartal(self, year, quartal):
        return str(int(year) + 1*(quartal == '4')) + '-' + '0'*(quartal != '3') + str((int(quartal)*3 + 1)%12) + '-01'

    def alpha2Name(self, alpha2):
        if alpha2 == 'UK':
            alpha2 = 'GB'
        if alpha2 == 'EL':
            alpha2 = 'GR'
        if alpha2 == 'FY':
            alpha2 = 'MK'
        if alpha2 == 'KO':
            alpha2 = 'KR'
        if alpha2 == 'XK':
            return 'Kosovo'
        if alpha2 == 'AN':
            return 'Netherlands_Antilles'
        return countries.get(alpha2).name.replace(' ','_')

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
        #cr.createOutput(cr.readMultilineInput('ᛥ'))
        if 'projects' in file:
            projectsData = cr.readMultilineInput('ᛥ')
            cr.filename = 'cordis_organizations'
            organizationsData = cr.readMultilineInput('ᛥ')
        elif 'organizations' in file:
            organizationsData = cr.readMultilineInput('ᛥ')
            cr.filename = 'cordis_projects'
            projectsData = cr.readMultilineInput('ᛥ')
        cr.createCordisObjects(projectsData, organizationsData)
    else:
        cr.createOutput(cr.readTextInput(';'))

if __name__ == '__main__':
    main()