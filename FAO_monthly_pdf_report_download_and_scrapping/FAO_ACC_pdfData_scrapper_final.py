# Change the path to where the ACC pdf files are located in the local dir.
def FAO_ACC_pdfReportData_scrapper(path):
    import pandas as pd
    import os
    import re
    import pdfplumber
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
    import numbers
    import calendar
    import pycountry
    from country_list import countries_for_language
    import itertools
    from sys import stdout
    from time import sleep
    import sys

    path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/CIT_MDA_CCA_MLI_Cental_Asia/"

    begin_pattern = re.compile(r'[Aa]rea\s+[Tt]reated')
    stop_pattern = re.compile(r'[Ll]ocust\s+[Ss]ituation\s+and\s+[Ff]orecast')

    # Define pattern to extract country names and also treated area numbers.

    country_pattern2 = re.compile(r"([a-zA-Z]+\s|[a-zA-Z]+)\s\W\sSITUATION")
    country_pattern3 = re.compile(r"SITUATION|Situation")
    forecast_pattern = re.compile(r"FORECAST|Forecast")
    stop_and_break = re.compile(r"Announcements")

    def unique(list_):
        unique_list = []
        for item in list_:
            if item not in unique_list:
                unique_list.append(item)
        return unique_list

    def fileFilter(path, pattern):
        files = os.listdir(path)
        new_pattern = re.sub("\.", ".*", pattern) + '$'
        filtered = [i for i in files if re.match(new_pattern, i)]
        return filtered

    treated_area_full = []
    treated_countries_full = []
    Year_full = []
    Month_full = []
    species_treated = []
    operation_type = []
    files = fileFilter(path, ".pdf")

    for i, file in enumerate(files):
        treated_area = []
        treated_countries = []
        Year = []
        Month = []

        if re.findall("_unlocked", file):
            fileX = re.sub("_unlocked", "", file)
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)
        else:
            fileX = file
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)

        stdout.write(
            "\r"f"Extracting data from file {i + 1} of {len(fileFilter(path, '.pdf'))} ... the current file name is {fileX}")
        stdout.flush()

        # print(f'Extracting data from {month[0]} {year[0]} ({i}th file of {len(fileFilter(path, ".pdf")) - 1} files)')
        ##############################################################################################
        # Reading the pdf file page by page, and extracting text from each column
        ##############################################################################################
        pdf_text = ""
        x0 = 0  # Distance of left side of character from left side of page.
        x1 = 0.5  # Distance of right side of character from left side of page.
        y0 = 0  # Distance of bottom of character from bottom of page.
        y1 = 1  # Distance of to
        try:
            with pdfplumber.open(f'{path}{fileX}') as pdf:
                for i, page in enumerate(pdf.pages):
                    width = page.width
                    height = page.height
                    # Crop pages
                    left_bbox = (x0 * float(width), y0 * float(height), x1 * float(width), y1 * float(height))
                    page_crop = page.crop(bbox=left_bbox)
                    left_text = page_crop.extract_text()

                    right_bbox = (0.5 * float(width), y0 * float(height), 1 * float(width), y1 * float(height))
                    page_crop = page.crop(bbox=right_bbox)
                    right_text = page_crop.extract_text()

                    page_context = '\n'.join([left_text, right_text])
                    pdf_text += page_context
        except:
            pass  # doing nothing on exception

        ##############################################################################################
        # Defining start and stop index positions of variables of interest
        # For example, each country summary is located between SITUATION and Forecast
        # Grabbing the index position of these two patterns allows us to single out
        # individual countries.
        ##############################################################################################

        stop_and_break_match = stop_and_break.finditer(pdf_text)
        stop_and_break_start = []
        stop_and_break_stop = []

        for match in stop_and_break_match:
            stop_and_break_start.append(match.start(0))
            stop_and_break_stop.append(match.end(0))

        start = []
        end = []

        matches = begin_pattern.finditer(pdf_text)
        for match in matches:
            start.append(match.start(0))
            end.append(match.end(0))

        start2 = []
        end2 = []

        matches2 = country_pattern3.finditer(pdf_text)
        for match in matches2:
            start2.append(match.start(0))
            end2.append(match.end(0))

        start_forecast = []
        end_forecast = []

        matches_forecast = forecast_pattern.finditer(pdf_text)
        for match in matches_forecast:
            start_forecast.append(match.start(0))
            end_forecast.append(match.end(0))

        new_start_forecast = []
        new_start2 = []

        start2.reverse()
        start_forecast.reverse()

        if len(start2) > len(end_forecast):
            for item in start2:
                if item >= 1000:
                    new_start2.append(item)
            for item in end_forecast:
                if item >= 1000:
                    new_start_forecast.append(item)
        else:
            for item in start2:
                if item >= 1000:
                    new_start2.append(item)
            for item in end_forecast:
                if item >= 1000:
                    new_start_forecast.append(item)

        new_start2.reverse()

        stop_point = []
        start_point = []

        start_matches = begin_pattern.finditer(pdf_text)
        stop_matches = stop_pattern.finditer(pdf_text)

        for match in start_matches:
            start_point.append(match.start(0))

        for match in stop_matches:
            stop_point.append(match.end(0))

        # string_to_search = pdf_text[start[0]:end[0]]
        try:
            string_to_search = pdf_text[start[0]:end[0]]
        except:
            pass  # doing nothing on exception

        month = re.findall(r'[a-zA-Z]+', fileX)[0]
        year = re.findall(r'\d+', fileX)[0]

        add = 0

        ##############################################################################################
        # Index the section of the pdf_text of interest (based on the index positions)
        # of the patterns above.
        # Then remove the english stop words (u can easily read about this online).
        ###############################################################################################

        if start_point > stop_point:
            string_to_search = pdf_text[start[0]:start[0] + 1000]
            stop_words = set(stopwords.words('english'))

            corpus_word = nl.word_tokenize(string_to_search)
            filtered_sentence = []

            for j in range(len(corpus_word)):
                if corpus_word[j] not in stop_words:
                    filtered_sentence.append(corpus_word[j])
        else:
            while re.findall(stop_pattern, string_to_search) == []:
                add = add + 50
                string_to_search = pdf_text[start[0]:end[0] + add]

            else:
                stop_words = set(stopwords.words('english'))

                corpus_word = nl.word_tokenize(string_to_search)
                filtered_sentence = []
                for j in range(len(corpus_word)):
                    if corpus_word[j] not in stop_words:
                        filtered_sentence.append(corpus_word[j])

        countries = countries_for_language('en')

        countries_name = []
        for item in countries:
            countries_name.append(item[1])

        ##############################################################################################
        # Extracting per country treated area monthly totals
        ##############################################################################################

        for i in range(len(filtered_sentence) - 1):
            # this part impliments the 2020 or 2021 August case (Afghanistan 0 ha / 90 584 ha)
            # the problem was that the last if statement under last else was not indented correctly.
            if filtered_sentence[i] == "ha":
                small_list = filtered_sentence[i - 3:i]
                if small_list[0] == "/":
                    if filtered_sentence[i - 4] == "ha":
                        small_list = filtered_sentence[i - 7:i - 4]

                    else:
                        small_list = filtered_sentence[i - 6:i - 3]

                    if small_list[1].isnumeric():
                        country = small_list[0]
                        if country == "Federation":
                            country = "Russia"

                        area = small_list[1] + small_list[2]
                        if country in countries_name:
                            treated_area.append(area)
                            treated_countries.append(country)
                            Year.append(year)
                            Month.append(month)
                            # print(treated_countries)
                    else:
                        country = small_list[1]
                        area = small_list[2]

                        if country in countries_name:
                            treated_area.append(area)
                            treated_countries.append(country)
                            Year.append(year)
                            Month.append(month)
                else:

                    month_1 = filtered_sentence[i + 2]
                    if month_1 in calendar.month_name[1:]:
                        small_list = filtered_sentence[i - 3:i]
                        if small_list[1].isnumeric():
                            country = small_list[0]
                        else:
                            country = small_list[1]

                        filtered_sentence1 = filtered_sentence[i + 2:]
                        for j in range(len(filtered_sentence1)):
                            if filtered_sentence1[j] == "ha":
                                month_2 = filtered_sentence1[j + 2]
                                # print(month_2)
                                if month_2 in calendar.month_name[1:]:
                                    # print(month_2[0:3])
                                    if month_2[0:3] == month:
                                        small_list = filtered_sentence1[j - 3:j]

                                        if small_list[1].isnumeric():
                                            # country = small_list[0]
                                            area = small_list[1] + small_list[2]
                                            treated_area.append(area)
                                            treated_countries.append(country)
                                            Year.append(year)
                                            Month.append(month)
                                        else:
                                            # small_list = filtered_sentence[i - 3:i]
                                            # country = small_list[1]
                                            area = small_list[2]
                                            treated_area.append(area)
                                            treated_countries.append(country)
                                            Year.append(year)
                                            Month.append(month)
                                    break
                    else:
                        small_list = filtered_sentence[i - 3:i]
                        if small_list[1].isnumeric():
                            country = small_list[0]
                            area = small_list[1] + small_list[2]

                            if country in countries_name:
                                treated_countries.append(country)
                                Year.append(year)
                                Month.append(month)
                                treated_area.append(area)
                        else:
                            # small_list = filtered_sentence[i - 3:i]
                            country = small_list[1]
                            area = small_list[2]
                            # treated_area.append(area)
                            if country in countries_name:
                                treated_countries.append(country)
                                Year.append(year)
                                treated_area.append(area)
                                Month.append(month)

        # Remove the dublicate countries and treated areas

        # iterates over 3 lists and till all are exhausted
        treated_countries_without_doublicate = []
        if treated_area:
            for (a, c, y, m) in itertools.zip_longest(treated_area, treated_countries, Year, Month, fillvalue=Month[0]):
                x = re.sub(",", "", a)
                if c not in treated_countries_without_doublicate:
                    treated_area_full.append(x)
                    treated_countries_full.append(c)
                    Year_full.append(y)
                    Month_full.append(m)
                treated_countries_without_doublicate.append(c)

        ##############################################################################################
        # This part extracts the species and control type information.
        ##############################################################################################

        countries_ordered_by_treatment_type = []

        for i in range(len(new_start2)):
            # print(list(range(len(new_start2))))
            # print(list(range(0,10)))
            # print(start2[10])
            # print(i)
            # print(len(new_start2))
            # grab all the countries named in the document.
            # compare them to countries with treatment summary on page one.
            # if the country is present in a list of countries with treatment, then get the species and treatment type for it.
            # nations = re.sub("[\W]", " ", pdf_text[start2[i]-16:end2[i]])
            if i == len(new_start2) - 1:

                nations = re.sub("[\W]", " ", pdf_text[new_start2[i] - 20:stop_and_break_stop[0]])

                nations = re.split(" ", nations)
                nations_no_empty_items = [item for item in nations if item.strip()]

                for nation in nations_no_empty_items:
                    if nation == "Federation":
                        nation = "Russia"
                        # print(nation)
                    elif nation[0].isnumeric():
                        nation = nation[1:]
                        # print(nation)
                    if nation in treated_countries_without_doublicate:
                        if nation not in countries_ordered_by_treatment_type:
                            countries_ordered_by_treatment_type.append(nation)

                            # print(i)
                            text = pdf_text[new_start2[i]: stop_and_break_stop[0]]

                            # Impliment locating the species by their common names i.e Italian Locust as is the case in

                            species = unique(re.findall(re.compile(r'CIT|DMA|LMI'), text))

                            # extract the treatment types/ operation types.
                            # convert all "Control" operations to "control" and then format them to past tense (controlled)
                            operations = re.findall(re.compile(r'[cC]ontrol|[tT]reated|[Tt]reatment'), text)

                            operation_clean = []
                            for operation in operations:
                                if operation.lower() == "control":
                                    operation_clean.append(f'{operation.lower()}led')
                                elif operation.lower() == "treatment":
                                    operation_clean.append("treated")
                                else:
                                    operation_clean.append(operation.lower())
                            operations = unique(operation_clean)

                            # for each country with treated species, if there are more than one specie for each treatment campaign, then concatenate them using &
                            # do the same for the operation types.
                            species_concatenated = ""
                            if species:
                                if len(species) > 1:
                                    for i in range(len(species)):
                                        if i == 0:
                                            species_concatenated += species[i]
                                        else:
                                            species_concatenated += f' & {species[i]}'
                                else:
                                    species_concatenated += species[0]

                            # for each country with treated species, if there are more than one specie for each treatment campaign, then concatenate them using &
                            # do the same for the operation types.

                            operation_concatenated = ""
                            if operations:
                                if len(operations) > 1:
                                    for i in range(len(operations) - 1):
                                        if i == 0:
                                            operation_concatenated += operations[i]
                                        else:
                                            operation_concatenated += f' & {operations[i]}'
                                else:
                                    operation_concatenated = operations[0]

                            species_treated.append(species_concatenated)

                            operation_type.append(operation_concatenated)
            else:

                nations = re.sub("[\W]", " ", pdf_text[new_start2[i] - 20:new_start2[i]])

                nations = re.split(" ", nations)
                nations_no_empty_items = [item for item in nations if item.strip()]

                for nation in nations_no_empty_items:
                    if nation == "Federation":
                        nation = "Russia"
                        # print(nation)
                    elif nation[0].isnumeric():
                        nation = nation[1:]
                        # print(nation)
                    if nation in treated_countries_without_doublicate:
                        if nation not in countries_ordered_by_treatment_type:
                            countries_ordered_by_treatment_type.append(nation)
                            # countries_ordered_by_treatment_type.append(nation)
                            # print(i)
                            text = pdf_text[new_start2[i]: new_start_forecast[i]]

                            # Impliment locating the species by their common names i.e Italian Locust as is the case in

                            species = unique(re.findall(re.compile(r'CIT|DMA|LMI'), text))

                            # extract the treatment types/ operation types.
                            # convert all "Control" operations to "control" and then format them to past tense (controlled)
                            operations = re.findall(re.compile(r'[cC]ontrol|[tT]reated|[Tt]reatment'), text)

                            operation_clean = []
                            for operation in operations:
                                if operation.lower() == "control":
                                    operation_clean.append(f'{operation.lower()}led')
                                elif operation.lower() == "treatment":
                                    operation_clean.append("treated")
                                else:
                                    operation_clean.append(operation.lower())
                            operations = unique(operation_clean)

                            # for each country with treated species, if there are more than one specie for each treatment campaign, then concatenate them using &
                            # do the same for the operation types.
                            species_concatenated = ""
                            if species:
                                if len(species) > 1:
                                    for i in range(len(species)):
                                        if i == 0:
                                            species_concatenated += species[i]
                                        else:
                                            species_concatenated += f' & {species[i]}'
                                else:
                                    species_concatenated += species[0]

                            # for each country with treated species, if there are more than one specie for each treatment campaign, then concatenate them using &
                            # do the same for the operation types.

                            operation_concatenated = ""
                            if operations:
                                if len(operations) > 1:
                                    for i in range(len(operations) - 1):
                                        if i == 0:
                                            operation_concatenated += operations[i]
                                        else:
                                            operation_concatenated += f' & {operations[i]}'
                                else:
                                    operation_concatenated = operations[0]

                            species_treated.append(species_concatenated)

                            operation_type.append(operation_concatenated)

        treated_area_ordered_by_treatment_type = []
        for item in countries_ordered_by_treatment_type:
            index = treated_countries_full.index(item)
            treated_area_ordered_by_treatment_type.append(treated_area_full[index])

    df = pd.DataFrame(
        {'Year': Year_full,
         'Month': Month_full,
         'Country': treated_countries_full,
         'T_area (ha)': treated_area_full,
         'Species': species_treated,
         'Operation_type': operation_type
         }
    )
    #print(df)
    df = df.drop_duplicates()
    df.to_csv(f"{path}2010_2021_ACC_Treatment_data.csv", index=False)
    return df


path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/hand_over_Okoth/Data/CIT_MDA_CCA_MLI_Cental_Asia_pdfs_and_csv"

FAO_ACC_pdfReportData_scrapper(path=path)
