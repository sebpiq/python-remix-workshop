import urllib
import requests

credentials = {
    'client_id': '',
    'api_key': ''
}


def search(keyword, max=500, fetch_infos=True):
    """
    Searches sounds with `keyword` from freesound.org, returns the search results. 
    """
    next_url = 'http://www.freesound.org/apiv2/search/text?' + urllib.urlencode({
        'query': keyword
    })
    all_results = []

    while next_url and len(all_results) < max:
        resp = requests.get(next_url, params={'token': credentials['api_key']})
        resp.raise_for_status()
        data = resp.json()
        all_results.extend(data['results'])
        next_url = data['next']

    if fetch_infos:
        fetched = []
        for result in all_results[:max]:
            sound_infos_url = 'http://www.freesound.org/apiv2/sounds/%s/' % result['id']
            resp = requests.get(sound_infos_url, params={'token': credentials['api_key']})
            resp.raise_for_status()
            fetched.append(resp.json())
        return fetched
    else: return all_results[:max]


def download_sound(sound_id, file_name):
    """
    Downloads `sound_id` from freesound.org, saves it to `file_name`.
    """
    sound_infos_url = 'http://www.freesound.org/apiv2/sounds/%s/' % sound_id
    resp = requests.get(sound_infos_url, params={ 'token': credentials['api_key'] })
    resp.raise_for_status()
    mp3_url = resp.json()['previews']['preview-hq-mp3']

    resp = requests.get(mp3_url, params={ 'token': credentials['api_key'] }, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in resp.iter_content(512):
            fd.write(chunk)