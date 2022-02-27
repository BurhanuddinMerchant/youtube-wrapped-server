from pkgutil import extend_path
from unittest import result
import requests

from server.settings import YOUTUBE_API_KEY


def requestHelper(rating,auth_token):
    API_KEY = YOUTUBE_API_KEY
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails%2Cid%2CliveStreamingDetails%2Clocalizations%2Cplayer%2CrecordingDetails%2Csnippet%2Cstatistics%2CtopicDetails&maxResults=50&myRating={rating}&key={API_KEY}"
    header = {
    "Authorization":f"Bearer {auth_token}"
    }
    result = requests.get(url,headers=header)
    status_code = result.status_code
    result=result.json()
    if('nextPageToken' in result):
        nextPageToken = result["nextPageToken"]
        cnt = 0
        while cnt<3 and nextPageToken!=None:
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails%2Cid%2CliveStreamingDetails%2Clocalizations%2Cplayer%2CrecordingDetails%2Csnippet%2Cstatistics%2CtopicDetails&maxResults=50&myRating={rating}&pageToken={nextPageToken}&key={API_KEY}"
            extra = requests.get(url, headers=header)
            status_code=extra.status_code
            extra = extra.json()
            cnt+=1
            result["items"]+=extra["items"]
            if('nextPageToken' in extra):
                nextPageToken =extra["nextPageToken"]
            else:
                break

    if status_code == 200:
        return result
    return None