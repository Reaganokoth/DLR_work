# Change the path to where you want the data stored in your local file system.
# If the code returns an error, it could be due to faulty pdf files that were not properly downloaded or because of pdf formats that
# is not in the monthly format report(not supported). Good news, the code will always be printing out which file it is extracting data from on the console.
# look for "Extracting data from file x of 143 ... the current file name is Mar_2021.pdf" then
# Just go to the file name that returns the error (in this case the file would be Mar_2021.pdf) in the directory and manually delete it.
# Unfortunately this is a bug that will be fixed in the future versions.
def FAO_DL_pdfReportScrapper (path):
    import pandas as pd
    import os
    import re
    import pdfplumber
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
    #path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/test_dowload/"
    begin_pattern = re.compile(r'[A]rea\s+[Tt]reated')
    stop_pattern = re.compile(r'[L]ocust\s+[Ss]ituation\s+and\s+[Ff]orecast')
    country_pattern3 = re.compile(r"SITUATION")
    forecast_pattern = re.compile("FORECAST")

    # Define pattern to extract country names and also treated area numbers.

    country_pattern2 = re.compile(r"([a-zA-Z]+\s|[a-zA-Z]+)\s\W\sSITUATION")

    treated_area_full = []
    treated_countries_full = []
    Year_full = []
    Month_full = []


    def fileFilter(path, pattern):
        files = os.listdir(path)
        new_pattern = re.sub("\.", ".*", pattern) + '$'
        filtered = [i for i in files if re.match(new_pattern, i)]
        return (filtered)

    list_of_files = sorted(fileFilter(path, ".pdf"))

    for i,file in enumerate(list_of_files):
        treated_area = []
        treated_countries = []
        Year = []
        Month = []
        treated_countries_without_doublicate = []
        if re.findall("_unlocked",file):
            fileX = re.sub("_unlocked", "", file)
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)
        else:
            fileX = file
            month = re.findall(r'[a-zA-Z]+', fileX)
            year = re.findall(r'\d+', fileX)

        stdout.write("\r"f"Extracting data from file {i + 1} of {len(fileFilter(path, '.pdf'))} ... the current file name is {fileX}")
        stdout.flush()


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

        stop_point = []
        start_point = []

        start_matches = begin_pattern.finditer(pdf_text)
        stop_matches = stop_pattern.finditer(pdf_text)

        for match in start_matches:
            start_point.append(match.start(0))

        for match in stop_matches:
            stop_point.append(match.end(0))


        #string_to_search = pdf_text[start[0]:end[0]]
        try:
            string_to_search = pdf_text[start[0]:end[0]]
        except:
            pass  # doing nothing on exception

        month = re.findall(r'[a-zA-Z]+', fileX)[0]
        year = re.findall(r'\d+', fileX)[0]

        add = 0

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

        for i in range(len(filtered_sentence)):
            # this part impliments the 2020 or 2021 August case (Afghanistan 0 ha / 90 584 ha)
            # the problem was that the last if statement under last else was not indented correctly.
            if filtered_sentence[i] == "ha":
                small_list = filtered_sentence[i - 3:i]
                #print(small_list)
                #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                # this part of the code implements cases like this 100 ha/20 0000 ha
                if small_list[0] == "/":
                    if filtered_sentence[i - 4] == "ha":
                        small_list = filtered_sentence[i - 7:i - 4]

                    else:
                        small_list = filtered_sentence[i - 6:i - 3]
                        # print(small_list)

                    if small_list[1].isnumeric():
                        country = small_list[0]
                        if country == "Federation":
                            country = "Russia"

                        area = small_list[1] + small_list[2]
                        # print(area)
                        if country in countries_name:
                            treated_area.append(re.sub("\+","",str(area)))
                            treated_countries.append(country)
                            Year.append(year)
                            Month.append(month)
                            # print(treated_countries)
                    else:
                        country = small_list[1]
                        area = small_list[2]

                        if country in countries_name:
                            treated_area.append(re.sub("\+","",str(area)))
                            treated_countries.append(country)
                            Year.append(year)
                            Month.append(month)
                # implementing multiple entries i.e Eritrea (3000000 ha april) and another updated value for previous month (40000 ha March)
                else:
                    # print(small_list)
                    month_1 = filtered_sentence[i + 2]

                    if month_1 not in calendar.month_name[1:]:
                        month_1 = filtered_sentence[i + 3]


                    if month_1 in calendar.month_name[1:]:
                        previous_month = calendar.month_name[1:][calendar.month_name[1:].index(month_1) - 1]

                        if month_1 != previous_month:
                            small_list = filtered_sentence[i - 3:i]


                            #print("***********************************")
    #                       # grab country information (name).
                            if small_list[1].isnumeric():
                                country = small_list[0]
                                if country == "Arabia":
                                    country = "Saudi Arabia"


                                # check whether the name exists in the predefined list of global country names.
                                # if it exists then append it to the overall treated country list
                                if country in countries_name:
                                    area = small_list[1] + small_list[2]
                                    treated_area.append(re.sub("\+","",str(area)))
                                    treated_countries.append(country)
                                    Year.append(year)
                                    Month.append(month)
                                #print(country)
                                #print("***********************************")
                                # otherwise there must be a case of double entry i.e one country with more than one entry.
                                # we make sure we pick the right value here (some times the reports updates values from previous months in the current month)
                                else:

                                    filtered_sentence1 = filtered_sentence[i + 2:]
                                    # Maybe i do not need the for loop here actually.
                                    # if the bellow condition is true, then update the value of the last entry in the treated area full.
                                    if small_list[0] in calendar.month_name[1:]:
                                        if small_list[0] == previous_month:
                                            treated_area[len(treated_area) - 1] = small_list[2]
                                    else:
                                        small_list = filtered_sentence[i - 4:i]
                                        if small_list[0] == previous_month:
                                            # check if the value is bigger than 1000 then combine then into one number
                                            x = small_list[-2] + small_list[-1]
                                            if x.isnumeric():
                                                treated_area[len(treated_area) - 1] = small_list[-2] + small_list[-1]

                                            else:
                                                treated_area[len(treated_area) - 1] = small_list[-1]


                            else:
                                #print(country)
                                country = small_list[1]
                                if country == "Arabia":
                                    country = "Saudi Arabia"

                                if country in countries_name:
                                    #print(small_list)
                                    #print("*****************************************************")
                                    area = small_list[2]
                                    treated_area.append(re.sub("\+", "", str(area)))
                                    treated_countries.append(country)
                                    Year.append(year)
                                    Month.append(month)
                                ################################################################################
                                # if country name is not in the defined global country names, that means there are two entry for a single country
                                # i.e previous month value update. In this case we want to make sure we pick the value for the present month.
                                # modify the last appended area value.
                                ################################################################################
                                else:

                                    filtered_sentence1 = filtered_sentence[i + 2:]
                                    # Maybe i do not need the for loop here actually.
                                    # if the bellow condition is true, then update the value of the last entry in the treated area full.
                                    if small_list[0] in calendar.month_name[1:]:
                                        if small_list[0] == previous_month:
                                            treated_area[len(treated_area) - 1] = small_list[2]
                                    else:
                                        small_list = filtered_sentence[i - 4:i]
                                        if small_list[0] == previous_month:
                                            x = small_list[-2] + small_list[-1]
                                            if x.isnumeric():
                                                treated_area[len(treated_area) - 1] = small_list[-2] + small_list[-1]

                                            else:
                                                treated_area[len(treated_area) - 1] = small_list[-1]


                    else:
                        small_list = filtered_sentence[i - 3:i]
                        if small_list[1].isnumeric():
                            country = small_list[0]
                            area = small_list[1] + small_list[2]

                            if country in countries_name:
                                treated_countries.append(country)
                                Year.append(year)
                                Month.append(month)
                                treated_area.append(re.sub("\+","",str(area)))
                        else:
                            # small_list = filtered_sentence[i - 3:i]
                            country = small_list[1]
                            area = small_list[2]
                            # treated_area.append(area)
                            if country in countries_name:
                                treated_countries.append(country)
                                Year.append(year)
                                treated_area.append(re.sub("\+","",str(area)))
                                Month.append(month)
        if treated_area:
            for (a, c, y, m) in itertools.zip_longest(treated_area, treated_countries, Year, Month, fillvalue=Month[0]):
                x = re.sub(",", "", a)
                if c not in treated_countries_without_doublicate:
                    treated_area_full.append(x)
                    treated_countries_full.append(c)
                    Year_full.append(y)
                    Month_full.append(m)

    df = pd.DataFrame(
        {'Year': Year_full,
         'Month': Month_full,
         'Country': treated_countries_full,
         'T_area (ha)': treated_area_full
         }
    )

    #df = df.drop_duplicates()
    df.to_csv(f"{path}2010_2021_DL_Treatment_Areas.csv", index=False)
path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/hand_over_Okoth/Data/DL_pdf_and_csv/"

FAO_DL_pdfReportScrapper(path=path)