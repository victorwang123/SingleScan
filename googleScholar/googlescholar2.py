# This script must be run after Python version 3.7
# Due to Google's academic restrictions on crawling, you must use a proxy for crawling
# http or socket proxy
PROXY = '*********' # make sure you input the correct proxy

from aiohttp import ClientSession, TCPConnector, ClientTimeout
from bs4 import BeautifulSoup
import re, asyncio
from typing import List


cookies = {
    'NID': '511=lbr1KGswChAjjZx1dt_ooN5rM3rnhSGOXx4hI-6t1JLEiQPy0SlS1jjUufhq-M80IUpxG8OBNTp-40eiRC5rnskbxq1a4QFynaNcXUtqfiIQooaz4x013lSJG5VgOHg8xlwKuOvVuv9QVEaR-G-bxehdWxGiOGhd9E5Gy1l8hE4',
    'GSP': 'A=0ljPxw:CPTS=1695199738:LM=1695199738:S=OIqf1mtadc3jLqxj',
}

headers = {
    'authority': 'scholar.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en',
    'cache-control': 'no-cache',
    # 'cookie': 'NID=511=lbr1KGswChAjjZx1dt_ooN5rM3rnhSGOXx4hI-6t1JLEiQPy0SlS1jjUufhq-M80IUpxG8OBNTp-40eiRC5rnskbxq1a4QFynaNcXUtqfiIQooaz4x013lSJG5VgOHg8xlwKuOvVuv9QVEaR-G-bxehdWxGiOGhd9E5Gy1l8hE4; GSP=A=0ljPxw:CPTS=1695199738:LM=1695199738:S=OIqf1mtadc3jLqxj',
    'pragma': 'no-cache',
    'referer': 'https://scholar.google.com/scholar',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-arch': '"arm"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version-list': '"Not.A/Brand";v="8.0.0.0", "Chromium";v="114.0.5735.198", "Google Chrome";v="114.0.5735.198"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"macOS"',
    'sec-ch-ua-platform-version': '"11.4.0"',
    'sec-ch-ua-wow64': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


async def search(doi: str, session, retryTime: int=0) -> int:
    try:
        resp = await session.get(
            'https://scholar.google.com/scholar',
            params = {
                'hl': 'en',
                'as_sdt': '0,5',
                # 'q': '10.1038/s41587-019-0336-3',
                'q': doi or '10.1093/bioinformatics-btp324',
                'btnG': '',
            },
            headers=headers,
            proxy=PROXY
        )
        html = await resp.text()
        soup = BeautifulSoup(html, features='html.parser')
        titleDom = soup.select_one('.gs_rt > a')
        # <a id="JaOV1zChDIsJ" href="https://academic.oup.com/bioinformatics/article-abstract/36/2/533/5540320" data-clk="hl=zh-TW&amp;sa=T&amp;ct=res&amp;cd=0&amp;d=10019560502139921189&amp;ei=y3IJZe70IJH4yASf76GYCA" data-clk-atid="JaOV1zChDIsJ">ACTINN: automated identification of cell types in single cell RNA sequencing</a>
        if not titleDom:
            print(doi, 'fail!')
            return {'msg': f'{doi} risk', 'data': None, 'status': False}
        link = titleDom.attrs['href']
        title = titleDom.getText().strip()

        # author，publication，website
        if soup.select_one('.gs_a.gs_fma_p'):
            authors, publicationInfo, _dot, publicationUrl = map(lambda node: node.getText().strip(), list(soup.select_one('.gs_a.gs_fma_p').children))
        else:
            authors, publicationInfo, publicationUrl = map(lambda s: s.strip(), soup.select_one('.gs_a').getText().strip().split('-'))
        
        # citation number
        citeDom = soup.select('.gs_fl.gs_flb a')[2]
        # soup.select_one('.gs_fl.gs_flb a:nth-child(3)')
        # <a href="/scholar?cites=10019560502139921189&amp;as_sdt=2005&amp;sciodt=0,5&amp;hl=zh-TW">被引用 132 次</a>
        # <a href="/scholar?q=related:S_2lphy-QXIJ:scholar.google.com/&amp;scioq=arxiv/2302.10776&amp;hl=en&amp;as_sdt=0,5">Related articles</a>
        if '/scholar?cites=' in citeDom.attrs['href']:
            paperId = {item.split('=')[0]: item.split('=')[1] for item in citeDom.attrs['href'].split('&')}['/scholar?cites']
            cites_nums = int(re.search(r'\d+', citeDom.getText().replace(',', '')).group())
        else:
            paperId = None
            cites_nums = 0
            
        cites_2023 = 0  # no reference
        if paperId:
            # citation number 2023
            resp = await session.get(
                f'https://scholar.google.com/scholar?as_ylo=2023&hl=en&as_sdt=2005&sciodt=0,5&cites={paperId}&scipsc=',
                headers=headers,
                proxy=PROXY,
            )
            html = await resp.text()
            soup = BeautifulSoup(html, features='html.parser')
            if 'e not a robot' in html:
                print(paperId, 'robot！')
                return {'msg': f'{paperId} robot!', 'data': None, 'status': False}
            citedDom = soup.select_one('#gs_ab_md .gs_ab_mdw')
            nums = citedDom.getText().strip()
            # print(paperId, nums)
            if nums:
                # About 1,310 results
                cites_2023 = int(re.search(r'\d+', nums.replace(',', '')).group())
            else:
                # no reference
                cites_2023 = 0

        return {'msg': f'success', 'data': dict(doi=doi, title=title, authors=authors, publicationInfo=publicationInfo, link=link, cites_nums=cites_nums, cites_2023=cites_2023), 'status': True}
    except Exception as ec:
        print(f'{doi} fail {retryTime+1}：{ec}')
        if retryTime <= 3:
            return await search(doi, session, retryTime=retryTime+1)
        return {'msg': f'{doi} failed', 'data': None, 'status': False}

async def spider(doiList: list) -> List[dict]:
    async with ClientSession(cookies=cookies, connector=TCPConnector(limit_per_host=10), timeout=ClientTimeout(65)) as session:
        results = await asyncio.gather(*[
            search(doi, session)
            for doi in doiList
        ])
        rowList = []
        for result in results:
            if result['status']:
                rowList.append(result['data'])
            else:
                print(result["msg"])
        return rowList

import csv, os

def readDoiList(filename: str) -> list:
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
    
def readCsvOutput(filename: str,) -> List[dict]:
    lst = []
    if not os.path.exists(filename):
        return lst
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lst.append(dict(row))
    return lst

def writeCsvOutput(filename: str, rowList: List[dict]) -> bool:
    if not rowList:
        return False
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(rowList[0].keys()))
        writer.writeheader()
        for rowData in rowList:
            writer.writerow(rowData)
    return True

def main(inFile: str, outFile: str) -> None:
    # 1. get total doi from `inFile`
    allDoiList = readDoiList(inFile)
    # 2. get finished doi from `outFile`
    exisitList = readCsvOutput(outFile)
    # extract unfinished doi to search
    unfinishedDoiList = []
    for doi in allDoiList:
        exisited = False
        for doneDoiObj in exisitList:
            if doi == doneDoiObj["doi"]:
                exisited = True
                break
        if exisited == False:
            unfinishedDoiList.append(doi)

    results = asyncio.run(spider(unfinishedDoiList))
    print(len(results+exisitList), '/', len(allDoiList))
    # merge current results into exisitList and write out
    writeCsvOutput(outFile, exisitList + results)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='A googlescholar citations searcher by doi. \n')
    parser.add_argument(
        'inFile', type=str,
        help='file contains doi to be searched, one item per line'
    )
    parser.add_argument(
        'outFile', type=str,
        help='output file'
    )
    args = parser.parse_args()
    main(args.inFile, args.outFile)
