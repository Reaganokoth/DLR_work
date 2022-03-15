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
path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/test_dowload/"
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

for i,file in enumerate(list_of_files[0:20]):
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

    # stdout.write("\r"f"Extracting data from file {i + 1} of {len(fileFilter(path, '.pdf'))} ... the current file name is {fileX}")
    # stdout.flush()
    print(f"the current file name is {fileX}")

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
            # stop_page = re.findall(stop_and_break, string_to_search)
            # print(string_to_search)
            # if stop_page:
            #     print("end of the while loop".upper())
            #     print(string_to_search)
            # break
            # print(string_to_search)
        else:
            # print(string_to_search)
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
            # this part of the code implements cases like this 100 ha/20 0000 ha
            if small_list[0] == "/":
                if filtered_sentence[i - 4] == "ha":
                    small_list = filtered_sentence[i - 7:i - 4]
                    print(small_list)
                else:
                    small_list = filtered_sentence[i - 6:i - 3]
                    #print(small_list)

                if small_list[1].isnumeric():
                    country = small_list[0]
                    if country == "Federation":
                        country = "Russia"

                    area = small_list[1] + small_list[2]
                    #print(area)
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
                #print(small_list)
                month_1 = filtered_sentence[i + 2]
                print(month_1)
                if month_1 in calendar.month_name[1:]:
                    small_list = filtered_sentence[i - 3:i]
                    #print(small_list)
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
    #print(treated_area)
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

df = df.drop_duplicates()
df.to_csv(f"{path}2010_2021_ACC_Treatment_data_test.csv", index=False)