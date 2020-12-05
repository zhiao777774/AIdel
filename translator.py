import requests


_API_URL = 'http://120.125.83.10:8090'

def google_translate(phrase, target = 'zh-TW'):
    service_url = f'{_API_URL}/googleTranslate'
    post_data = {
        'phrase': phrase,
        'target': target
    }

    response = requests.post(service_url, json = post_data)
    translated = None
    if response.status_code == 200:
        translated = response.text

    return translated

def translate(phrase, source, target):
    service_url = f'{_API_URL}/pyTranslate'
    post_data = {
        'phrase': phrase,
        'source': source,
        'target': target
    }

    response = requests.post(service_url, json = post_data)
    translated = None
    if response.status_code == 200:
        translated = response.text

    return translated


if __name__ == '__main__':
    # translated = google_translate('cup')
    translated = translate('cup', 'EN', 'zh-TW')
    print(translated)