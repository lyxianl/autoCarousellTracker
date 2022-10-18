import pendulum
import requests
import pandas
import json
import re

from vars import sortMapping

def requiredHeaders():
    session = requests.Session()
    url = 'https://www.carousell.sg/'
    response = session.get(url)
    if response.ok:
        cookies = session.cookies.get_dict()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'cookie': '_csrf={}'.format(cookies['_csrf']), # '; '.join([f'{i[0]}={i[1]}' for i in cookies.items()]),
        }
        response = session.get(url, headers=headers)
        if response.ok:
            appState = json.loads(re.search(r'.*Application":({[^}]*}).*', response.text).group(1))
        else:
            print('No cookies..')
            return ''
        headers['csrf-token'] = appState['csrfToken']
        return headers
    else:
        print('No cookies..')
        return ''

# ===== CAROUSELL-API =====

def paginationHelper():
    return {
        'enforce': True,
        'fieldName': 'collections',
        'idsOrKeywords': { 'value': ['0'] }
    }

def requestPayload(query, querySize): #, sortFilter='recent'):

    return {
        'bestMatchEnabled': True,
        'canChangeKeyword': False, #True,
        # 'ccid': '2195',
        # 'ccid': '5699',
        # 'ccid': '5732',
        'count': querySize,
        'countryCode': 'SG',
        'countryId': '1880251',
        'filters': [paginationHelper() for _ in range(1)],
        'includeEducationBanner': True,
        'includeSuggestions': False,
        'locale': 'en',
        'query': query,
        "prefill": {},
        "sortParam": {},
        # 'prefill': { 'prefill_sort_by': sortMapping[sortFilter] },
        # 'sortParam': { 'fieldName': sortMapping[sortFilter] },
        # 'searchContext': '0a0208301a0408bbe17222130a0f616e696d616c2063726f7373696e6778012a140a0b636f6c6c656374696f6e7312030a013078013204080378013a02180742060801100118004a0620012801400150005a020801',
        # 'session': 'eyJhZ2dyZWdhdGVfY291bnQiOjQ4LCJhcHBsaWVkX2NjaWQiOiIiLCJjb250ZW50Ijp7ImJhbm5lcl9jY2lkIjoiNTczMiIsImN1cnJlbnRfY291bnQiOjQ4LCJzcmNfcGFnaW5nX2luZm8iOnsiaW50ZXJuYWxfYWRzIjp7InBhZ2VfbnVtYmVyIjoxfSwibGlzdGluZ19jYXJkLWJsb2NrIjp7ImNodW5rX251bWJlciI6MCwiY2h1bmtfc3RhcnRfb2Zmc2V0IjowLCJjcmVhdGVkX2F0IjoiMjAyMi0xMC0xN1QxODowMjowNVoiLCJvZmZzZXQiOjQ4LCJ2ZXJzaW9uIjoiMGUwZWFkNWMtMTZmMi00NTIxLTk4YjktNzRmOGY3NTM0OWZlIn19fSwiZW5mb3JjZV9jYXRlZ29yeV9maWx0ZXIiOnRydWUsImZpZWxkc2V0X2NjaWQiOiI1NzMyIiwicGFnZV9zaXplIjo0OCwicXVzdmNfcmVzcCI6IkNoQUtCRFUzTXpJVnZla3RQeDBBQUlBL0NoQUtCRFUzTWpnVjA1dGVQaDBLMTZNK0VoQUtCRFUzTXpJVnZla3RQeDBBQUlBL0VoQUtCRFUzTWpnVjA1dGVQaDBLMTZNK0doQUtCRFUzTXpJVkpuRndQeDBBQUlBL0dnWUtCRFUzTWpnaVdnb1BZVzVwYldGc0lHTnliM056YVc1bkVnOWhibWx0WVd3Z1kzSnZjM05wYm1kSUFsb1JFZzloYm1sdFlXd2dZM0p2YzNOcGJtZHFEMkZ1YVcxaGJDQmpjbTl6YzJsdVo0b0JEMkZ1YVcxaGJDQmpjbTl6YzJsdVp6SUNDQUZDRUFvRU5UY3pNaFVtY1hBL0hRQUFnRDlDQmdvRU5UY3lPQT09IiwicmVxX2hhc19jaGFuZ2VkIjpmYWxzZSwic2VhcmNoX3BhcmFtcyI6IkdnSUlNQ29FQ0x2aGNqSVRDZzloYm1sdFlXd2dZM0p2YzNOcGJtZDRBVUlFQ0FONEFVb0NHQWRTQkFnQkVBRmFCaUFCS0FGQUFXb0NDQUU9Iiwic2Vzc2lvbl9pZCI6IjI2NTg1YzEwLTczNmUtNDM4MS1iM2RmLTRhYmQ5NGViZGMxNSIsInN1Z2dlc3RlZF9jYXRlZ29yeV90eXBlIjoyLCJzdWdnZXN0ZWRfY2NpZCI6IjU3MzIifQ==',
    }

def allListings(response, query, num, keywords, base_url_search):
    columnOrder = ['no.', 'timestamp', 'status', 'title',
                     'url', 'price (S$)', 'state', 'body', 'meetup', 'user', 'img']

    df = pandas.DataFrame([listingInfo(i['listingCard']) for i in sortListingsFromResponse(response)])

    if keywords != ['']:
        # First Exclude
        df = df.loc[excludeListings(df, keywords), :]

        # Continue search till <num> reached
        response_1 = response
        while df.shape[0] < num:
            # TODO - searchMore
            break
            # response_1 = searchCarousell_cont(
            #     response_1, base_url_search, requestPayload(query, num))
            # df_1 = pandas.DataFrame([listingInfo(i['listingCard']) for i in sortListingsFromResponse(response_1)])
            # df = df.append(df_1.loc[excludeListings(df_1, keywords), :])

        # Trim to <num> results
        # df = df.iloc[:num, :]

    df['no.'] = df.index.map(lambda x: x+1).to_list()[::-1]
    return df[columnOrder]

def listingInfo(result):
    raw = dict(zip(['body', 'state'], [i['stringContent'] for i in result['belowFold'][2:4]]))
    dateTime = pendulum.from_timestamp(result['overlayContent']['timestampContent']['seconds']['low'], tz='Asia/Singapore')
    location_name, meetups = getLocation(result['id'])
    return {
        'title': re.sub(r'\n', '', result['title']),
        'price (S$)': result['price'].split('$')[-1].replace(',', ''),
        'timestamp': dateTime.format('MM-DD-YYYY hh:mm A'),
        'url': 'https://www.carousell.sg/p/' + result['id'],
        'img': result['photos'][0]['thumbnailUrl'],
        'user': result['seller']['username'],
        'status': '-',
        'meetup': '; '.join(meetups) if isinstance(meetups, list) else '-',
        **raw
    }

def sortListingsFromResponse(response):
    return sorted([listing for listing in response['data']['results']], key=lambda x: x['listingCard']['overlayContent']['timestampContent']['seconds']['low'], reverse=True)

def excludeListings(df, keywords):
    ls = []
    for word in keywords:
        ls.append(df.loc[:, 'title'].apply(
            lambda x: word not in x.lower()).values)
    return [any(i) for i in zip(*ls)]

def getLocation(listing_id):
    listing_url = f'https://www.carousell.sg/api-service/listing/3.1/listings/{listing_id}/detail/'
    response = requests.get(listing_url)

    if response.status_code == 200:
        meta_values = response.json()['data']['screens'][0]['meta']['default_value']
        location_name = meta_values['location_name']
        if meta_values['meetup']:
            locations = [i['name'] for i in meta_values['meetups']]
        else:
            locations = None
        return location_name, locations
    else:
        raise Exception('Failed to get location...')

# ===== GOOGLE-API =====

def updatedListings(new_df, sheet):
    retry_times = len(sheet.get_all_records())
    if sheet.get_all_records() == []:
        # Empty Sheet
        return new_df, new_df.shape[0]
    else:
        # Locate Start Point
        new_df = new_df.reset_index(drop=True)
        records = sheet.get_all_records()
        urls = [rec['url'] for rec in records]
        for url in urls[:retry_times]:
            # Found
            if new_df.loc[new_df['url'] == url, :].shape[0] >= 1:
                new_count = new_df[new_df['url'] == url].index[-1]
                new_df = new_df.iloc[:new_count, :]
                # Update Index of "new_df"
                start = records[0]['no.'] + 1
                new_df.loc[:, 'no.'] = [
                    i for i in range(start, start+new_count)][::-1]
                # Add rest of records
                new_df = new_df.append(pandas.DataFrame(records))
                return new_df, new_count

        # Push entire "new_df"
        start = records[0]['no.'] + 1
        new_df.loc[:, 'no.'] = [i for i in range(
            start, start+new_df.shape[0])][::-1]
        new_df = new_df.append(pandas.DataFrame(records))
        return new_df, new_df.shape[0]

def sheetPayload(df):
    return [df.columns.tolist()] + df.values.tolist()

def sheetStatus_all(sheet):    # Update Past Listings Every 8 Hours
    new_df = pandas.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0])
    # Check for last updated row + Check Status
    urls = new_df.loc[new_df.loc[:, 'status'].apply(lambda x: x not in ['-', 'MIA', 'Sold']), 'url']

    if len(urls) != 0:
        checkResults = [checkStatus(re.search(r'/p/(.*)', url).group(1)) for url in urls]
        new_df.loc[new_df.loc[:, 'status'].apply(lambda x: x not in ['-', 'MIA', 'Sold']), 'status'] = checkResults
        sheet.update(sheetPayload(new_df))
        return f'{sheet.title} (all) : {len(checkResults)-len([i for i in checkResults if i == "-"])}/{len(checkResults)} listing status updated'
    else:
        return 'Already Updated'

def sheetStatus_new(sheet, num):    # Update '-' Every Hour
    new_df = pandas.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0])
    # Check for last updated row + Check Status
    check_range = new_df.loc[:, 'status'] == '-'
    if num != 0:
        check_range[:num] = [False for _ in range(num)]
    urls = new_df.loc[check_range, 'url']

    if len(urls) != 0:
        #checkResults = [checkStatus([url[0], re.search(r'/p/(.*)', url[1]).group(1)]) for url in enumerate(urls)]
        checkResults = [checkStatus(re.search(r'/p/(.*)', url).group(1)) for url in urls]
        new_df.loc[check_range, 'status'] = checkResults
        sheet.update(sheetPayload(new_df))
        return f'{sheet.title} (new) : {len(checkResults)-len([i for i in checkResults if i == "-"])}/{len(checkResults)} listing status updated'
    else:
        return 'Already Updated'

def checkStatus(listing_id):
    base_url_listing = f'https://www.carousell.sg/api-service/listing/3.1/listings/{listing_id}/detail/'
    try:
        resp = requests.get(base_url_listing).json()
    except:
        #print(f'{listing_id} [Failed]')
        return '-'
    if 'screens' in resp['data'].keys():
        if resp['data']['screens'][0]['ui_rules']['actions']['primary_button']['button_text'] == 'Sold':
            return 'Sold'
        elif resp['data']['screens'][0]['ui_rules']['actions']['primary_button']['button_text'] == 'Reserved':
            return 'Close'
        else:
            return 'Open'
    else:
        return 'MIA'