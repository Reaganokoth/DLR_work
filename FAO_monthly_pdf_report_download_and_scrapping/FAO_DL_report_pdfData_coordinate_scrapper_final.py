# change the path to point to where the DL pdf reports are stored in the local directory.
# The code returns the extracted data so you can already store it in a variable in during your current session (implemetation2). It writes the data in the defined path.

#path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/test_dowload/"


def FAO_DL_pdfReportData_scrapper(path, which_data):
    import pandas as pd
    import os
    import re

    # Loading pdf file and extracting text from the file
    from io import StringIO
    import pdfminer as pm
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser
    import nltk as nl
    from nltk.corpus import stopwords
    from sys import stdout
    from time import sleep
    import sys

    # test_path = "/Users/rragankonywa/Downloads/ilovepdf_unlocked/March_2019_unlocked.pdf"

    # treated_area_pattern = re.compile(r"((treated|estimated)\s\d{1,9}(\s\d{1,9}|\s))")
    treated_area_pattern = re.compile(r"((treated|estimated)\s\d{1,9}(,?\d{1,9}|\s))")

    # Define pattern to extract country names and also treated area numbers.
    country_pattern = re.compile(r"([A-Z]{4,20}\s|[A-Z]{4,20})")
    country_pattern2 = re.compile(r"([a-zA-Z]+\s|[a-zA-Z]+)\s\W\sSITUATION")
    location_pattern = re.compile(r'(near|between)\s([a-zA-Z]+\s[a-zA-Z]+|[a-zA-Z]+)')
    forecast_pattern = re.compile(r"FORECAST")
    page_pattern = re.compile(r'page\s+\d\sof\s+\d')

    # define patterns to extract location data based on the Northing and Easting given in the document
    north_location_pattern = re.compile(r"([0-9]+[NS])")
    east_location_pattern = re.compile(r"([0-9]+[EW])")
    north_and_east_location_pattern = re.compile(r"([0-9]+[NS]/[0-9]+[EW])")

    # Read the pdf and extract the text
    # path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/2003_2005/Unlocked/"
    # path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/Decrypted/"
    # path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/test_dowload/"

    # files = re.findall(r"\.pdf", os.listdir("/Users/rragankonywa/Downloads/ilovepdf_unlocked/"))

    def fileFilter(path, pattern):
        files = os.listdir(path)
        new_pattern = re.sub("\.", ".*", pattern) + '$'
        filtered = [i for i in files if re.match(new_pattern, i)]
        return filtered

    # Define output variables expected
    list_of_country = []
    treated_area = []
    treated_countries = []
    treatment_location = []
    Year = []
    Month = []
    all_Easting = []
    all_Northing = []
    possible_treatment_location = []
    Lat = []
    Lon = []
    list_of_files = sorted(fileFilter(path, ".pdf"))
    # print(list_of_files)
    for file in list_of_files:
        if re.findall("_unlocked", file):
            fileX = re.sub("_unlocked", "", file)
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)
        else:
            fileX = file
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)

        stdout.write("\r"f"Extracting data from file {list_of_files.index(file) + 1} of {len(fileFilter(path, '.pdf'))} ... the current file name is {file}")
        stdout.flush()

        # print(f"Current file is {file}",end= "\r")
        # Read and extract the pdf text
        output_string = StringIO()
        with open(f'{path + file}', 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

        pdf_text = output_string.getvalue()

        # get the last page of the document
        last_page = re.findall(page_pattern, pdf_text)[-1]
        last_page = re.findall(r'\d+', last_page)
        if int(int(last_page[0]) - 1) > int(last_page[1]):
            last_page = int(last_page[0])
        else:
            last_page = int(last_page[1])

        # Grab the index positions of countries in the extracted pdf text
        start = []
        end = []
        matches = country_pattern2.finditer(pdf_text)
        for match in matches:
            start.append(match.start(0))
            end.append(match.end(0))

        # grab the names of the countries present in the pdf and store them in  LIST OBJECT.

        for i in range(len(start)):
            add = 0
            string_to_search = pdf_text[start[i]:end[i]]
            country = re.split(r"\W", string_to_search)[0]
            list_of_country.append(country)

            while re.findall(forecast_pattern, string_to_search) == []:
                add = add + 50
                string_to_search = pdf_text[start[i]:end[i] + add]

                page_number = re.findall(page_pattern, re.sub("\n", "", string_to_search))
                if page_number:
                    if len(page_number) == 1:
                        page_number = re.findall(r'\d+', page_number[0])
                        # print(page_number[0])
                        # print(page_number[1])

                    else:
                        page_number = re.findall(r'\d+', page_number[len(page_number) - 1])
                        # print(page_number[0])
                        # print(page_number[1])

                    if int(page_number[0]) > int(last_page) - 1:
                        if int(page_number[0]) == last_page - 1:
                            break
                    elif int(page_number[0]) == last_page - 1:
                        break

            else:
                string_to_search = pdf_text[start[i]:end[i] + add]
                string_to_search_no_newline = re.sub("\n", "", string_to_search)

                country = re.split(r"\W", string_to_search)[0]

                treated_area_as_str = re.findall(treated_area_pattern, string_to_search_no_newline)

                location = re.findall(location_pattern, string_to_search)

                if treated_area_as_str != []:
                    # Remove the stop-words (see stopwords in nltk package) to remain only with key words
                    stop_words = set(stopwords.words('english'))

                    corpus_word = nl.word_tokenize(string_to_search)

                    # find the location data and store it in east, north
                    # Grab the last location mentioned and save it in possible treatment location

                    north = (re.findall(north_location_pattern, string_to_search_no_newline))
                    east = (re.findall(east_location_pattern, string_to_search_no_newline))
                    north_and_east = (re.findall(north_and_east_location_pattern, string_to_search_no_newline))
                    all_Northing.append(north)
                    all_Easting.append(east)

                    if country == "ARABIA":
                        treated_countries.append("SAUDI ARABIA")
                    else:
                        treated_countries.append(country)

                    Year.append(year[0])
                    Month.append(month[0])

                    # check if there is location information captured for each section
                    # if there is, check if the last coordinates are in the filtered words
                    # if tt is in the filtered words, grab the second word and check whether it has less or equal to three characters
                    # this is needed because of the Arabic countries with place names such as Al fafa amd so on
                    # if the name is in two parts, combine them and add them to the list of location as a single word separated by space
                    # Otherwise add the next word following coordinates to the possible-locations list.

                    filtered_sentence = []
                    for j in range(len(corpus_word)):
                        if corpus_word[j] not in stop_words:
                            filtered_sentence.append(corpus_word[j])
                            if north_and_east != []:
                                if north_and_east[len(north_and_east) - 1] == corpus_word[j]:
                                    if 1 < len(filtered_sentence[-4:-3][0]) <= 3:
                                        x_sep = filtered_sentence[-4: -2]
                                        x_joined = " ".join(x_sep)
                                        possible_treatment_location.append(x_joined)

                                    else:
                                        possible_treatment_location.append(filtered_sentence[-3: -2][0])
                    if north_and_east == []:
                        possible_treatment_location.append("Location Missing")
                        Lon.append('Missing')
                        Lat.append('Missing')
                    else:
                        x_all = re.split("/", north_and_east[len(north_and_east) - 1])
                        p_lat = re.findall(r'[0-9]+', x_all[0])[0]
                        p_lat = p_lat[0:2] + "." + p_lat[2:4]

                        if x_all[1][-1] == "W":
                            P_lon = re.findall(r'[0-9]+', x_all[1])[0]
                            P_lon = "-" + P_lon[0:2] + "." + P_lon[2:4]
                        else:
                            P_lon = re.findall(r'[0-9]+', x_all[1])[0]
                            P_lon = P_lon[0:2] + "." + P_lon[2:4]

                        Lat.append(p_lat)
                        Lon.append(P_lon)

                # Check if there are more than 1 treatment events if there are, sum them up and add it to the treated areas
                treated_area_as_int = []
                for y in range(len(treated_area_as_str)):
                    if y != len(treated_area_as_str) - 1:
                        treated_area_as_int.append(int(re.sub(r"((treated|estimated)\s|,?)", "", treated_area_as_str[y][0])))
                    else:
                        treated_area_as_int.append(int(re.sub(r"((treated|estimated)\s|,?)", "", treated_area_as_str[y][0])))
                        if len(treated_area_as_int) > 1:
                            treated_area.append(sum(treated_area_as_int))
                        else:
                            treated_area.append(treated_area_as_int[0])

    # make a pandas dataframe and export it as csv file to local directory

    data = {'Year': Year, 'Month': Month, 'Country': treated_countries, 'all_Northing': all_Northing,
            'all_Easting': all_Easting,
            #'T_area (ha)': treated_area,
            'Lat': Lat,
            'Lon': Lon
            }
    df = pd.DataFrame(data=data)

    df.to_csv(f"{path}2003_205_DL_Treatment_data1.csv", index=False)
    df.to_csv(f"{path}2010_2021_{which_data}_Treatment_points.csv", index=False)
    return df

path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/hand_over_Okoth/Data/DL_pdf_and_csv/"
#FAO_DL_pdfReportData_scrapper(path=path)  # implementation 1
my_data = FAO_DL_pdfReportData_scrapper(path=path,which_data="DL")  # implementation 2
