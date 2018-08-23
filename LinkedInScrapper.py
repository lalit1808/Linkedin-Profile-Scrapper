from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wd
from bs4 import BeautifulSoup
import os
import datetime
from threading import Timer
import time
import math
import pandas as pd
import csv
from selenium.webdriver.chrome.options import Options as OP

    
def Init():
    timer = Timer(Init, 259200)
    timer.start()
    op=OP()
    op.add_argument("--headless")
    DriverPath =input('Enter the ChromeDriver Path')
    Browser = webdriver.Chrome(executable_path=DriverPath, chrome_options=op)
    wd(Browser, timeout=10)
    Browser.get("https://www.linkedin.com/uas/login?")
    UserName =input('Enter the Username:')
    Password =input('Enter the Password')
    Path = input('Enter the Input csv path')
    Browser.find_element_by_name('session_key').send_keys(UserName)
    Browser.find_element_by_name('session_password').send_keys(Password)
    Browser.find_element_by_name('signin').click() 
    
    Emp_list=[]
    with open(Path, 'r', newline='') as file:
        Emp_dictionary = csv.DictReader(file)
        for Emp_profile in Emp_dictionary:
            Emp_dt = {}
            Emp_dt['FirstName'] = Emp_profile['FirstName']
            Emp_dt['LastName'] = Emp_profile['LastName']
            Emp_dt['Profile_url'] = Emp_profile['Profile_url']
            Emp_list.append(Emp_dt)

    
    Profile_data = []
    Current_data = []
        
    
    for i in range(0 , len(Emp_list)):
        Emp_profile = Emp_list[i]
        first = Emp_profile['FirstName']
        last = Emp_profile['LastName']
        url = Emp_profile['Profile_url']
        #print(url)
        if url != None :
            if os.path.exists('prev_data.csv') == True:
                DataFrame = pd.read_csv('prev_data.csv', sep=',')
                DataFrame.set_index("Link", inplace=True)
                try:
                    indexx = DataFrame.loc[url]
                except KeyError:
                    indexx = None
                if indexx is not None:
                    Dictionary_data, dt_new = scrapper(Browser, first, last, url, indexx["Skills"], indexx["Title"], indexx["Description"])
                    Profile_data.append(Dictionary_data)
                    Current_data.append(dt_new)
                else:
                    Dictionary_data, dt_new = scrapper(Browser, first, last, url)
                    Profile_data.append(Dictionary_data)
                    Current_data.append(dt_new)
            else:            
                Dictionary_data, dt_new = scrapper(Browser, first, last, url)
                Profile_data.append(Dictionary_data)
                Current_data.append(dt_new)
        
        
    
    write_temp_data(Current_data)
    
    write_data(Profile_data)
    
def similar(new, old):
    if new.lower() != old.lower():
        return "Yes"
    else:
        return "No"
            
def write_temp_data(Current_data):
    with open('prev_data.csv', 'w', newline='') as file1:
        w = csv.DictWriter(file1, fieldnames=['Link', 'Title', 'Skills', 'Description'])
        w.writeheader()
        for i in range(0, len(Current_data)):
            ext_data = Current_data[i]
            w.writerow({'Link': ext_data['Link'], 'Skills': ext_data['Skills'], 'Title': ext_data['Title'], 'Description': ext_data['Description']})

    
def write_data(Profile_data):
    file_name = str(datetime.datetime.now())[:10]+'.csv'
    with open(file_name, 'w', newline='') as file2:
        fieldnames = ['FirstName', 'LastName', 'Profile_url', 'Contacts', 'Recruiter_count', 'Recommendations', 'Updated_skills', 'Title_update', 'Summary']
        w = csv.DictWriter(file2, fieldnames=fieldnames)
        w.writeheader()
        for i in range(0, len(Profile_data)):
            data = Profile_data[i]
            w.writerow({'FirstName': data['FirstName'], 'LastName': data['LastName'], 'Profile_url': data['Profile_url'], 'Contacts': data['Contacts'], 'Recruiter_count': data['Recruiter_count'], 'Recommendations': data['Recommendations'], 'Updated_skills': data['Updated_skills'], 'Title_update': data['Title_update'], 'Summary': data['Summary']})

            
def scrapper(Browser, first, last, link, skills=None, title=None, desc=None):
    Browser.get(link)
        
    
    wd(Browser, 200).until(EC.presence_of_element_located((By.CLASS_NAME, 'pv-top-card-section__headline')))
    try:
        Title = Browser.find_element_by_class_name('pv-top-card-section__headline').get_attribute('innerText')
    except:
        Title = 'None'
    Browser.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
    try:
        Browser.find_element_by_class_name('pv-top-card-section__summary-toggle-button')
        wd(Browser, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'pv-top-card-section__summary-toggle-button')))
        wd(Browser, 50).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pv-top-card-section__summary-toggle-button')))
        Browser.find_element_by_class_name('pv-top-card-section__summary-toggle-button').click()
    except NoSuchElementException as e:
        pass
    try:
        Description = Browser.find_element_by_class_name('pv-top-card-section__summary-text').get_attribute('innerText')
    except:
        Description = 'None'
    Browser.execute_script("window.scrollTo(0, document.body.scrollHeight/1.7);")
    Skills = ''
    Jhanda = 0
    try:
        wd(Browser, 12).until(EC.presence_of_element_located((By.CLASS_NAME, 'pv-skills-section__additional-skills')))
        Browser.find_element_by_class_name('pv-skills-section__additional-skills')
        wd(Browser, 14).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pv-skills-section__additional-skills')))
        time.sleep(0.5)
        Browser.find_element_by_class_name('pv-skills-section__additional-skills').click()
    except NoSuchElementException as e:    
        pass
    except ElementClickInterceptedException as e:
        try:
            wd(Browser, 12).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pv-skills-section__additional-skills')))
            Browser.find_element_by_class_name('pv-skills-section__additional-skills').click()
        except:
            pass
    try:
        s = Browser.find_elements_by_class_name('pv-skill-category-entity__name')
        for item in s:
            Skills = Skills+item.text
    except:
        Jhanda = 1
        
    if Jhanda == 1:
        Skills = 'None'
    
    wd(Browser, 50).until(EC.presence_of_element_located((By.TAG_NAME, "artdeco-tab")))
    
    rec = Browser.find_element_by_tag_name("artdeco-tab").text
    Recommendations_count = int(rec[10:-1])
        
    Browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    Contacts = int(Browser.find_element_by_class_name('pv-top-card-v2-section__connections ').text[17:-1])
    Browser.find_element_by_class_name('pv-top-card-v2-section__link--connections').click()
    wd(Browser, 500).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results-container')))
    url = Browser.current_url+"&page="
    
    total_pages = int(Contacts/10)
    if(Contacts%10!=0):
        total_pages= total_pages+1
        
    list_conn_head = []
    for i in range(1, total_pages+1):
        Browser.set_page_load_timeout(time_to_wait=222)
        Browser.get(url+str(i))
        wd(Browser, 150).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results-container')))
        Browser.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(0.50)
        wd(Browser, 150).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results-container')))
        conn_html = Browser.execute_script("return document.body.innerHTML")
        parsed = BeautifulSoup(conn_html, "lxml")
        paras = parsed.select('p.subline-level-1.search-result__truncate')
        for i in range(0, len(paras)):
            list_conn_head.append(paras[i].text)
        
    Recruiter_count = 0
    list_comp = ['HR Manager', 'HR Executive', 'Recruiter', 'HR', 'Human Resource']
    for i in range(0, len(list_conn_head)):
        designation = list_conn_head[i].lower()
        for j in range(0, len(list_comp)):
            if list_comp[j].lower() in designation:
                Recruiter_count+=1
        

        
    
    title_updated = 'No'
    if title != None:
        title_updated = similar(Title, title)
        
    
    desc_updated = 'No'
    if desc != None:
        desc_updated = similar(Description, desc)
        
   
    skills_updated = 'No'
    if skills != None:
        skills_updated = similar(Skills, skills)
    data = {'FirstName': first, 'LastName': last, 'Profile_url': link, 'Contacts': Contacts, 'Recruiter_count': Recruiter_count, 'Recommendations': Recommendations_count, 'Updated_skills': skills_updated, 'Title_update': title_updated, 'Summary': desc_updated}
    dt_new = {'Link': link, 'Title': Title, 'Skills': Skills, 'Description': Description }
    return data, dt_new


Init()
