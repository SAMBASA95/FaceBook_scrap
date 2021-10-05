import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import re

main_df = pd.read_excel('test_leads.xlsx')
ex_df = main_df[['NAME', 'Facebook']]
ex_df = ex_df.dropna(subset=['Facebook', 'NAME'])
# ex_df = ex_df.head()

keywords = ['technology', 'women', 'marketing', 'baked', 'covid']
result = []
info = []
likes_comm = []
post_detail = []

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)

# specify the path to chromedriver.exe (download and save on your computer)
driver = webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe', chrome_options=chrome_options)
driver.maximize_window()

# open the webpage
driver.get("http://www.facebook.com")

# target username
time.sleep(5)
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

# enter username and password
username.clear()
username.send_keys('asd@mail.com')
password.clear()
password.send_keys('3kgSGNBu4x%;iQ=')
time.sleep(5)

# target the login button and click it
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
# We are logged in!
time.sleep(5)
# open new window with execute_script()
driver.execute_script("window.open('');")
time.sleep(5)
# switch to new window with switch_to.window()
driver.switch_to.window(driver.window_handles[1])
time.sleep(5)

for lead, name in zip(ex_df.Facebook, ex_df.NAME):
    exa = lead
    if "/posts/" in exa:
        head, sep, tail = exa.partition('/posts')
        lead = head
    if "m.facebook.c" and "/posts/" in exa:
        head, sep, tail = exa.partition('/posts')
        m_head = head.replace("https://m.facebook.com", "https://www.facebook.com")
        lead = m_head
    else:
        lead = exa
    print(lead, name)
    try:
        driver.get(lead)
        time.sleep(5)
        ######################
        # Scrolling
        n = 400
        while True:
            page_ht_bef = driver.execute_script("return document.body.scrollHeight")
            if len(driver.find_elements_by_xpath("(//div[@class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0'])")) >= 20:
                break
            try:
                driver.execute_script("window.scrollBy(0, arguments[0]);", 400 + n)
                comment = driver.find_elements_by_xpath(
                    "(//div[@class='oajrlxb2 bp9cbjyn g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 "
                    "goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv "
                    "nhd2j8a9 pq6dq46d mg4g778l btwxx1t3 g5gj957u p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x "
                    "tgvbjcpo hpfvmrgz jb3vyjys p8fzw8mz qt6c0cv9 a8nywdso l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of "
                    "du4w35lb lzcic4wl abiwlrkh gpro0wi8 m9osqain buofh1pr'])")
                for z in comment:
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(z).perform()
                        time.sleep(5)
                        if 'more comments' or 'replied' or 'previous' in z.text:
                            z.click()
                        else:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(3)
                            page_ht_aft = driver.execute_script("return document.body.scrollHeight")
                            n = page_ht_aft
                            if page_ht_aft == page_ht_bef:
                                break
                            pass
                    except:
                        pass

                if not comment:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    page_ht_aft = driver.execute_script("return document.body.scrollHeight")
                    n = page_ht_aft
                    if page_ht_aft == page_ht_bef:
                        break
            except:
                pass
            time.sleep(3)

        get_source = driver.page_source
        bs4_src = BeautifulSoup(get_source, 'lxml')
        prettify = bs4_src.prettify()
        #####################
        try:
            info_container = bs4_src.find('div', {
                'class': "sjgh65i0"}).get_text(strip=True)

            header_container = bs4_src.find('div', {
                'class': "sjgh65i0"}).get_text(strip=True)

            info.append((info_container, header_container))

        except:
            info.append('nada')
            pass
        ####################
        posts = []
        try:
            leads_article = bs4_src.findAll('div', {'class': "du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"})
            for link in leads_article:
                # print(link.get_text(strip=True))
                posts.append(link.get_text(strip=True))

            post_detail.append(posts)

            posts = [each_string.lower() for each_string in posts]
            letters_only = [(re.sub("[^a-zA-Z]", " ", str(location))) for location in posts]

            # search to get only those strings with alphabets
            pattern = '|'.join(f"\\b{k}\\b" for k in keywords)
            matches = {k: 0 for k in keywords}
            for title in letters_only:
                for match in re.findall(pattern, title):
                    matches[match] += 1
            result.append(matches)
        except:
            post_detail.append('nada')
            pass
        ######################
        likes_comments = bs4_src.findAll('div', {
            'class': "bp9cbjyn m9osqain j83agx80 jq4qci2q bkfpd7mw a3bd9o3v kvgmc6g5 wkznzc2l oygrvhab dhix69tm jktsbyx5 rz4wbd8a osnr6wyh a8nywdso s1tcr66n"})
        for lc in likes_comments:
            # print(lc.text)
            likes_comm.append(lc.get_text(strip=True))

        time.sleep(5)

    except:
        # print(name + lead + "is not valid or for")
        info.append('nada')
        post_detail.append('nada')
        time.sleep(5)
        pass

dummy_tup = tuple(zip(result, post_detail, info))
pre_dataFrame = pd.DataFrame(dummy_tup,
                             columns=['result', 'post_detail', 'info'])
df_result = pd.DataFrame(result)
ex_df = ex_df.reset_index()
ex_df = ex_df[['NAME', 'Facebook']]
df_over_content = pd.concat(
    [ex_df, df_result, pre_dataFrame], axis=1, join='inner')

Excel_convertor = pd.ExcelWriter('Result.xlsx')
df_over_content.to_excel(Excel_convertor, index=False)
Excel_convertor.save()
