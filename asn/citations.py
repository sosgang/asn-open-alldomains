import csv
import asn
import os
from datetime import datetime
import configurations


SESSIONS_MAP = configurations.SESSIONS_MAP
TIME_GAPS = configurations.TIME_GAPS

LIST_INCOMING = './data/LIST_ALL_INCOMING_CITATIONS.csv'
LIST_INCOMING_BY_SESSION_PREF = './data/LIST_INCOMING_SESSION_'

def logCountedCitation(filename, citation):
    log = open(filename, 'a')
    log.write(citation + "\n")
    log.close();

def getCitationLogFilename(session, level):
    return LIST_INCOMING_BY_SESSION_PREF + str(session) + '_LEVEL_' + str(level) + '.csv'

def cleanCitationsLogs():
    if asn.checkFileIsPresent(LIST_INCOMING):
         os.remove(LIST_INCOMING)

    for session in SESSIONS_MAP[6]:
        for i in range(1, 3):
            INCOMING_IN_SESSION = getCitationLogFilename(session, i)
            if asn.checkFileIsPresent(INCOMING_IN_SESSION):
                os.remove(INCOMING_IN_SESSION)


# ANALISI DEI DATI COCI
# VIENE COSTRUITO UN DIZIONARIO CONTENENTE {DOI: NUMERO_DI_CITAZIONI_RICEVUTE}
# I DOI CHE NON SONO PRESENTI TRA I DOI DELLE PRODUZIONI DEI CANDIDATI VENGONO SCARTATI
# QUANDO L'ANALISI TERMINA VIENE CREATO UN CSV CONTENENTE I DATI DEL DIZIONARIO
def analizeCociData(filename, citationsCSV, candidatesCSV):
    candidatesDois = asn.createCandidatesDoisDict(candidatesCSV)

    dois = {}

    cleanCitationsLogs()

    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")

        for row in reader:
            doi = row[2]
            doi = doi.lower()
            if doi in candidatesDois:

                #debug: force saving all incoming citations for the candidate

                # debug: log citations

                found_incoming_cit_line = row[1] + "," + row[2] + "," + row[3]
                print(found_incoming_cit_line)
                logCountedCitation(LIST_INCOMING, found_incoming_cit_line)

#                print(found_incoming_cit_line)
#                log = open(LIST_INCOMING, 'a')
#                log.write(found_incoming_cit_line + "\n")
#                log.close();
                #debug


                if not doi in dois:
                    dois[doi] = {}
                    for session in SESSIONS_MAP[6]:
                        dois[doi][session] = {
                            1: 0,
                            2: 0
                        }
                for session in SESSIONS_MAP[6]:
                    sessionDate = SESSIONS_MAP[6][session]
                    sessionDate = datetime.strptime(
                        sessionDate, '%Y-%m-%d').date()
                    firstLevelTimeGap = TIME_GAPS['citations'][1]
                    secondLevelTimeGap = TIME_GAPS['citations'][2]
                    try:
                        if len(row[3].split('-')) == 3:
                            creation = datetime.strptime(
                                row[3], '%Y-%m-%d').date()
                        elif len(row[3].split('-')) == 2:
                            creation = datetime.strptime(
                                row[3], '%Y-%m').date()
                        else:
                            creation = datetime.strptime(row[3], '%Y').date()
                        if creation < sessionDate and (int(sessionDate.year)-int(creation.year)) < secondLevelTimeGap:
                            dois[doi][session][1] = dois[doi][session][1] + 1
                            dois[doi][session][2] = dois[doi][session][2] + 1
                            # debug: log citations
                            logCountedCitation(getCitationLogFilename(session,1), found_incoming_cit_line)
                            logCountedCitation(getCitationLogFilename(session,2), found_incoming_cit_line)

                        elif creation < sessionDate and (int(sessionDate.year)-int(creation.year)) < firstLevelTimeGap:
                            dois[doi][session][1] = dois[doi][session][1] + 1
                            # debug: log citations
                            logCountedCitation(getCitationLogFilename(session,1), found_incoming_cit_line)
                    except:
                        pass

    print(dois)
    asn.createCitationsCSV(dois, citationsCSV, 0)
