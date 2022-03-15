# This code downloads ACC monthly report from FAO archives https://www.fao.org/locusts-cca/current-situation/
# the function takes in one parameter (path) which points to the directory where you want the files to be stored.
# the path should point to the folder to store the files.Change the path parameter to where you want the files to be stored in your local directory.
path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/CIT_MDA_CCA_MLI_Cental_Asia/test/"
def FAO_ACC_monthly_report_downloader(path):
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

    def fileFilter(path, pattern):
        files = os.listdir(path)
        new_pattern = re.sub("\.", ".*", pattern) + '$'
        filtered = [i for i in files if re.match(new_pattern, i)]
        return filtered

    pages = list(range(1,17))
    date_pattern = re.compile(r":?\s[a-zA-Z]+\s\d{4}")

    #path = "/Users/rragankonywa/OneDrive/UniWurzburg/EAGLES/Semester3/Internship/DLR_Internship/Internship/week1/CIT_MDA_CCA_MLI_Cental_Asia/"
    for item in pages:
            #link = "https://www.fao.org/locusts-cca/current-situation/en/"
        #link = f"https://www.fao.org/locusts-cca/resources/en/?page={item}&ipp=5&tx_dynalist_pi1[par]=YToxOntzOjE6IkwiO3M6MToiMCI7fQ=="
        link = f"https://www.fao.org/locusts-cca/current-situation/en/?page={item}&ipp=5&tx_dynalist_pi1[par]=YToxOntzOjE6IkwiO3M6MToiMCI7fQ=="

        page = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.text, 'html.parser')
        # print(soup.prettify())
        reports = soup.find(class_="news-list")

        reports_as_list = re.split('"', str(reports))
        links2 = []
        for item in reports_as_list:
            if r".pdf" in item:
                links2.append(item)

        date_info = re.findall(date_pattern, str(reports))
        file_names = []
        m = calendar.month_name[1:]

        for i in range(len(date_info)):
            if i % 2 == 0:
                year = re.split(" ", date_info[i])[2]
                full_month = re.split(" ", date_info[i])[1]
                if full_month in m:
                    month = full_month[0:3]
                    file_name = f'{month}_{year}'
                if file_name not in file_names:
                    file_names.append(file_name)
                #file_names.append(file_name)
        if item == 11:
            file_names = file_names[1:]
        for link, fileName in zip(links2, file_names):
            if os.path.isfile(f'{fileName}.pdf'):
                print(f'{fileName} already in the directory')
            elif "win" not in fileName:
                file = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
                with open(f'{path}{fileName}.pdf', 'wb') as f:
                    f.write(file.content)
    print(f"{len(fileFilter(path, '.pdf'))} files have been downloaded and saved in  {path}")

FAO_ACC_monthly_report_downloader(path=path)