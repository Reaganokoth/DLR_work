# This function downloads Desert Locust monthly reports from FAO website ("https://www.fao.org/ag/locusts/en/archives/archive/).
# The function takes in two parameters (period and path).
# Period: this is the time period of interest. FAO reports are organised in 10 year period starting from 1970 to present (see here: https://www.fao.org/ag/locusts/en/archives/archive/).
# Available periods are: 1970-1979, 1980-1989, 1990-1999, 2000-2009,2010-2019, 2020-2029.
# It is possible to download reports from multiple periods at the same time. you just need to provide the periods of interest as a list (see implementation 2).
# Path: refers to the location in the local directory where you want to store the downloaded files.
# Both period and path must be defined for the code to run.
def DLrepordDownload(periods, path):
    import re
    import os
    import requests
    import urllib
    import urllib3
    from bs4 import BeautifulSoup
    from urllib.request import urlopen
    import json
    import getpass
    import pprint
    import calendar
    from datetime import date
    from sys import stdout
    from time import sleep
    import sys

    for period in periods:

        path = path
        period2 = period

        start_year = int(re.split("-", period2)[0])
        end_year = int(re.split("-", period2)[1])

        period_pattern = re.compile(period)
        # year_pattern = re.compile("2019")

        years = list(range(start_year, end_year + 1))
        # print(years)
        ########################################################
        # go to the main page and grab the period of interest usually each period is ten years
        # and is represented in the url link by a unique identifier number.
        # Use this unique ID to expand to the data for each YEAR under the period.
        # Each year also has a similar behavior of a unique identifier
        # and same is true for each month under each year.
        # The interest is to walk through these and build a url for each pdf file in each year

        #############################################################################
        # Navigate to the main page with all the available periods listed and grab the period of interest ID.

        Main_page_URL = "https://www.fao.org/ag/locusts/en/archives/archive/"
        link = "https://www.fao.org/ag/locusts/en/archives/archive/index.html"
        Main_page = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
        Main_soup = BeautifulSoup(Main_page.text, 'html.parser')
        # print(soup.prettify())

        start_period = []

        matches_period = period_pattern.finditer(str(Main_soup))
        for match in matches_period:
            start_period.append(match.start(0))
            # end.append(match.end(0))

        Main_page_text = str(Main_soup)[start_period[0] - 55: start_period[0]]
        # x = re.sub("<|>", "",x)

        first_last_list = [years[0], years[len(years) - 1]]
        periodID = re.findall(r'[0-9]+', Main_page_text)

        all_years = re.findall(r'\d{4}', str(Main_soup))
        years_with_report = []
        for year in all_years:
            if int(year) in years and int(year) not in years_with_report:
                years_with_report.append(int(year))
                years_with_report.sort()
        # print(f"downloading report for the years_with_report)

        year_today = date.today().year

        for year in years_with_report:
            if year <= year_today:
                # print(year)
                # print(year_today)
                year_pattern = re.compile(str(year))

                ############################################################################
                # with the period ID grabbed, build a url to navigate to the specific period of interest.
                # Here all the years available within period are listed.
                # The Years also have a unique ID for each year.
                # We will grab this ID and then use it to build another url to a page where all the monthly pdf reports for each year is listed

                periodURL = f'{Main_page_URL}{periodID[0]}/index.html'

                period_page = requests.get(periodURL, headers={'User-Agent': 'Mozilla/5.0'})
                period_soup = BeautifulSoup(period_page.text, 'html.parser')

                year_matches = re.finditer(year_pattern, str(period_soup))

                current_year = []

                matches_year = year_pattern.finditer(str(period_soup))
                for match in year_matches:
                    current_year.append(match.start(0))

                current_year = current_year
                # print(current_year)
                ########################################################################################################################

                dummy_year_url = "https://www.fao.org/ag/locusts/en/archives/archive/1367/1990/index.html"
                respose_code = requests.get(dummy_year_url, headers={'User-Agent': 'Mozilla/5.0'}).status_code
                # print(f'status code == {respose_code}')
                i = 0
                while respose_code != 200:
                    # print(f'status code == {respose_code}')
                    # print(i)

                    if year not in first_last_list:
                        # print(len(current_year))
                        if len(current_year) >= 2:
                            x1 = str(period_soup)[current_year[i] - 55: current_year[i]]
                        else:
                            x1 = str(period_soup)[current_year[0] - 55: current_year[0]]

                    else:
                        x1 = str(period_soup)[current_year[i] - 55: current_year[i]]

                    current_yearID = re.findall(r'[0-9]{4}', x1)

                    New_current_yearID = []

                    if len(current_yearID) > 1:
                        for item in current_yearID:
                            if item != periodID[0]:
                                New_current_yearID.append(item)
                    else:
                        if New_current_yearID:
                            New_current_yearID.append(current_yearID[0])

                    if len(New_current_yearID) > 1:
                        dummy_year_url = f'{Main_page_URL}{periodID[0]}/{New_current_yearID[1]}/index.html'
                    else:
                        if New_current_yearID:
                            dummy_year_url = f'{Main_page_URL}{periodID[0]}/{New_current_yearID[0]}/index.html'
                    yearURL = dummy_year_url
                    respose_code = requests.get(dummy_year_url, headers={'User-Agent': 'Mozilla/5.0'}).status_code

                    i += 1

                ########################################################################################################################
                year_page = requests.get(yearURL, headers={'User-Agent': 'Mozilla/5.0'})
                year_soup = BeautifulSoup(year_page.text, 'html.parser')
                # print(soup3.prettify())

                month_ifos = re.findall(r"No\.?\s[0-9]+,\s[a-zA-Z]+", str(year_soup))
                # print(re.split(" ",month_ifos[0])[2][0:3])

                Month = []
                for month_ifo in month_ifos:
                    Month.append(re.split(" ", month_ifo)[2][0:3])

                for item in current_yearID:
                    if item != periodID[0]:
                        New_current_yearID.append(item)

                month_start_index = []
                month_end_index = []
                month_matches = re.finditer(r"No\.?\s[0-9]+,\s[a-zA-Z]+", str(year_soup))

                for match in month_matches:
                    month_start_index.append(match.start(0))
                    month_end_index.append(match.end(0))

                for i in range(len(month_start_index)):
                    fileName = f'{Month[i]}_{year}'

                    year_text = str(year_soup)[month_start_index[i] + 100:month_start_index[i] + 200]
                    # print(str(year_soup)[month_start_index[2]+100:month_start_index[2]+200])

                    last_url_part = re.split("\.\.", year_text)[5]
                    last_url_part = re.split(" ", last_url_part)
                    last_url_part = re.sub("ar", "en", last_url_part[0])
                    last_url_part = re.sub("a", "e", last_url_part)
                    last_url_part = re.sub("PDF", "pdf", last_url_part)
                    last_url_part = re.sub('"', "", last_url_part)
                    last_url_part = re.sub('>enebic', "", last_url_part)
                    last_url_part = re.sub('_', "", last_url_part)
                    last_url_part = re.sub('>english', "", last_url_part)
                    last_url_part = re.sub('</e>', "", last_url_part)
                    last_url_part = re.sub('<e', "", last_url_part)

                    enf = re.findall("DL\d+\w", last_url_part)
                    if re.findall("f", enf[0]):
                        enf = re.sub("f", "e", enf[0])
                        last_url_part = re.sub("DL\d+\w", enf, last_url_part)

                    if not re.findall("pdf", last_url_part):
                        last_url_part = f"{last_url_part}.pdf"

                    # print(Month[i])

                    final_url = f'https://www.fao.org/ag/locusts{last_url_part}'

                    # print(fileName)
                    # print(xx)
                    # print(final_url)
                    r = requests.get(final_url, stream=True)
                    # https: // www.fao.org / ag / locusts / common / ecg / 705_en_DL193e.pdf

                    if r.status_code != 200:
                        # print(final_url)
                        # print(xx)
                        final_url_split = re.split("en", last_url_part)
                        last_part_of_url = f'{final_url_split[0]}_en_{final_url_split[-1]}'
                        final_url = f'https://www.fao.org/ag/locusts{last_part_of_url}'
                        # print(final_url)

                    r = requests.get(final_url, stream=True)

                    if os.path.exists(f'{path}{fileName}.pdf'):
                        # print(f"{fileName}.pdf already exists")
                        stdout.write("\r"f"{fileName}.pdf already exists")
                        stdout.flush()
                    else:
                        # print(f'{fileName} report from {final_url}')
                        stdout.write("\r"f"{fileName} report from {final_url}")
                        stdout.flush()
                        with open(f'{path}{fileName}.pdf', 'wb') as fd:
                            for chunk in r.iter_content(2000):
                                fd.write(chunk)


# period = ["2010-2019", "2020-2029"]
#period = ["2020-2029"]
path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/test_dowload/"

# Download all reports in a single period
#DLrepordDownload(periods="2020-2029", path=path)  # implementation 1

# Download all reports in a multiple periods
DLrepordDownload(periods=["2010-2019", "2020-2029"], path=path)  # implementation 2

