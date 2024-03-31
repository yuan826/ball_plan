import urllib.request as req
import bs4
import pandas as pd

def getData(url, keyword=None, start_date=None, end_date=None):
    dates_list = []
    titles_list = []
    
    # 建立一個 Request 物件，附加 Request Headers 的資訊
    request = req.Request(url, headers={
        "cookie": "over18=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    })
    # 利用建立的  request物件 打開網址
    with req.urlopen(request) as response:
        data = response.read().decode("utf-8")
    
    # 解析原始碼，取得每篇文章的標題和日期
    root = bs4.BeautifulSoup(data, "html.parser")  #讓 BeautifulSoup 協助我們解析 HTML 格式文件
    titles = root.find_all("div", class_="title")  # 尋找 class="title"的 div 標籤  (標籤名,篩選條件)
    dates = root.find_all("div", class_="date")
    for title, date in zip(titles, dates):
        if title.a is not None:  # 如果標題包含 a 標籤(沒有被刪除)
            article_date = date.string.strip()
            if start_date is None or end_date is None or (start_date <= article_date <= end_date):
                if keyword is None or keyword in title.a.string:  # 如果沒有關鍵字或標題包含關鍵字
                    dates_list.append(article_date)
                    titles_list.append(title.a.string)
    
    df = pd.DataFrame({"Date": dates_list, "Title": titles_list})
    
    #  (動態)抓取上一頁的連結
    nextLink = root.find("a", string="‹ 上頁")  # 利用bs4，找到內文是 ‹ 上頁 的 a標籤
    next_page_url = "https://www.ptt.cc" + nextLink["href"] if nextLink else None
    
    return df, next_page_url

# 主程式
pageURL = "https://www.ptt.cc/bbs/Gossiping/index.html"
keyword = input("請輸入要搜尋的關鍵字(若不需搜尋可直接按Enter): ")
start_date = input("請輸入搜尋的開始日期(MM/DD，若不指定則直接按Enter): ")
end_date = input("請輸入搜尋的結束日期(MM/DD，若不指定則直接按Enter): ")

all_results = pd.DataFrame(columns=["Date", "Title"])

while True:
    df, pageURL = getData(pageURL, keyword, start_date, end_date)
    if not df.empty:  # 检查 DataFrame 是否为空
        all_results = pd.concat([all_results, df], ignore_index=True)
    if pageURL:
        pageURL = pageURL
    else:
        break

print(all_results)
