from flask import Flask, request
from flask import render_template
import requests
import json


app = Flask(__name__)


@app.route('/')
def index():
    client_id = '11337103815c4efba7f885a174f7710e'
    redirect_uri = request.base_url + 'results/'
    print(redirect_uri)
    scope = 'user-top-read'
    login_url = 'https://accounts.spotify.com/authorize?client_id=' + client_id + '&state=bravo_charlie&response_type=code&redirect_uri=' + redirect_uri + '&scope=' + scope
    return render_template('index.html', login_url=login_url)




@app.route('/results/')
def results():
    code = request.args['code']
    headers = get_headers(code)
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user = json.loads(response.text)
    term = 'long'
    base_url = 'https://api.spotify.com/v1/me/top/tracks?time_range={}_term&limit=50'.format(term)
    response = requests.get(base_url, headers=headers)
    long_tracks = json.loads(response.text)['items']
    long_swag, long_image = get_bravo_charlie(long_tracks, headers)
    return render_template('results.html', user=user, long_image=long_image,long_swag=long_swag)

def get_headers(code):
    redirect_uri = request.base_url
    encoded_client_credentials = 'MTEzMzcxMDM4MTVjNGVmYmE3Zjg4NWExNzRmNzcxMGU6NjRhYmJhODk5NzBlNDAyYmFhMTE3YjFmNmQxMWMyNTc='
    headers = {
        'Authorization': 'Basic ' + encoded_client_credentials,
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    print(response.text)
    bearer_token = 'Bearer ' + json.loads(response.text)['access_token']

    headers = {
        'Authorization': bearer_token,
    }
    return headers

def get_bravo_charlie(tracks,headers):
    album_ids = []
    albums_image_urls = []
    white_url = 'https://dummyimage.com/300x300/ffffff/ffffff'
    for track in tracks:
        album = track['album']
        if album['id'] not in album_ids:
            album_ids.append(album['id'])
            albums_image_urls.append(album['images'][1]['url'])
        if len(album_ids) > 4:
            break
    albums_image_urls = albums_image_urls + [white_url]*(4-len(albums_image_urls))
    bravo_charlie_url = 'https://www.billclintonswag.com/api/image?album_url={}&album_url={}&album_url={}&album_url={}'.format(
        albums_image_urls[0], albums_image_urls[1], albums_image_urls[2], albums_image_urls[3])

    swag_url = requests.get(bravo_charlie_url, stream=True).url
    image_id = swag_url.rsplit('/', 1)[-1]
    image_url = 'https://s3.amazonaws.com/Clinton_Swag/{}/swag.png'.format(image_id)
    return(swag_url,image_url)


if __name__ == '__main__':
    app.run(port = 8081)