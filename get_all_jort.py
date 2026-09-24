#%%
import os
import time
import urllib.request
import requests


def get_url_and_file_name(year:int=2000,num:int=1):
    str_num = ""
    if num < 10:
        str_num = f"00{num}"
    elif num < 100 :
        str_num = f"0{num}"
    else:
        str_num = str(num)

    md_file_name = f"{year}/{str_num}.md"
    pdf_file_name = f"{year}/{str_num}.pdf"

    md_url = f"https://ocr.jort.tn/journal-officiel/fr/{md_file_name}"
    pdf_url = f"https://lake.jort.tn/journal-officiel/fr/{pdf_file_name}"

    return md_file_name, md_url , pdf_file_name , pdf_url

def download(year:int=2000,num:int=1,sleep_time:int=1):
    chrome_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', chrome_user_agent)]
    urllib.request.install_opener(opener)
    
    md , md_url , pdf , pdf_url = get_url_and_file_name(year,num)


    os.makedirs(str(year),exist_ok=True)
    try:
        urllib.request.urlretrieve(md_url,md)
        time.sleep(sleep_time)
        urllib.request.urlretrieve(pdf_url,pdf)
    except Exception as ex:
        print(str(ex))
        
    time.sleep(sleep_time)
    print(f"____download____md___{md}__pdf___{pdf}___")

def get_years_and_last_jort_number(url:str="https://index.jort.tn/",last_year:int=1957,last_num:int=1):
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept" : "application/json"
    }

    response = requests.get(url,headers=headers)
    data = response.json()

    _n = 0
    _y = 0
    last_n = last_num
    for year, lng in data["collections"][0]["years"].items():
        num = lng.get("fr")
        if isinstance(num,str):
            _n = int(num) + 1
        else:
            _n = num + 1
        if isinstance(year,str):
            _y = int(year)
        else:
            _y = year

        if _y > last_year:
            print(f"Begin of year _____ {_y} ______")
            for x in range(last_n,_n):
                download(_y,x)
            print(f"End of year ____ {_y}  ______")
            last_n = 1


#%%

get_years_and_last_jort_number(last_year=2015,last_num=52)
# %%
