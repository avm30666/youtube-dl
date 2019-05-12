# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    smuggle_url,
    ExtractorError,
)


class SBSIE(InfoExtractor):
    IE_DESC = 'sbs.com.au'
    _VALID_URL = r'https?://(?:www\.)?sbs\.com\.au/(?:ondemand|news)/(?:video/)?(?:single/)?([0-9]+|[0-9a-z-]+)'

    _TESTS = [{
        'url': 'https://www.sbs.com.au/news/are-the-campaigns-working-voters-speak-out',
        'md5': '2b73ddcbb597f24a87167826c47398f8',
        'info_dict': {
            'id': 'Vznr2YGb83mF',
            'ext': 'mp4',
            'title': 'Are the campaigns cutting through?',
            'description': 'md5:d41d8cd98f00b204e9800998ecf8427e',
            'thumbnail': r're:http://.*\.jpg',
            'duration': 146,
            'timestamp': 1557552900,
            'upload_date': '20190511',
            'uploader': 'SBSC',
        }
    }, {
        # Original URL is handled by the generic IE which finds the iframe:
        # http://www.sbs.com.au/thefeed/blog/2014/08/21/dingo-conservation
        'url': 'http://www.sbs.com.au/ondemand/video/single/320403011771/?source=drupal&vertical=thefeed',
        'md5': '3150cf278965eeabb5b4cea1c963fe0a',
        'info_dict': {
            'id': '_rFBPRPO4pMR',
            'ext': 'mp4',
            'title': 'Dingo Conservation (The Feed)',
            'description': 'md5:f250a9856fca50d22dec0b5b8015f8a5',
            'thumbnail': r're:http://.*\.jpg',
            'duration': 308,
            'timestamp': 1408613220,
            'upload_date': '20140821',
            'uploader': 'SBSC',
        },
    }, {
        'url': 'http://www.sbs.com.au/ondemand/video/320403011771/Dingo-Conservation-The-Feed',
        'only_matching': True,
    }, {
        'url': 'http://www.sbs.com.au/news/video/471395907773/The-Feed-July-9',
        'only_matching': True,
    }]

    def video_id_from_page_contents(self, url):
        page_contents = self._download_webpage(url, None)
        video_id = self._search_regex(r'id="video-(\d+)"', page_contents, 'video id')
        return video_id

    def video_id(self, url):
        ID_BEARING_URL = r'https?://(?:www\.)?sbs\.com\.au/(?:ondemand|news)/video/(?:single/)?(?P<id>[0-9]+)'
        match = re.match(ID_BEARING_URL, url)
        if match:
            return match.group('id')
        else:
            return self.video_id_from_page_contents(url)

    def _real_extract(self, url):
        video_id = self.video_id(url)
        player_params = self._download_json(
            'http://www.sbs.com.au/api/video_pdkvars/id/%s?form=json' % video_id, video_id)

        error = player_params.get('error')
        if error:
            error_message = 'Sorry, The video you are looking for does not exist.'
            video_data = error.get('results') or {}
            error_code = error.get('errorCode')
            if error_code == 'ComingSoon':
                error_message = '%s is not yet available.' % video_data.get('title', '')
            elif error_code in ('Forbidden', 'intranetAccessOnly'):
                error_message = 'Sorry, This video cannot be accessed via this website'
            elif error_code == 'Expired':
                error_message = 'Sorry, %s is no longer available.' % video_data.get('title', '')
            raise ExtractorError('%s said: %s' % (self.IE_NAME, error_message), expected=True)

        urls = player_params['releaseUrls']
        theplatform_url = (urls.get('progressive') or urls.get('html')
                           or urls.get('standard') or player_params['relatedItemsURL'])

        return {
            '_type': 'url_transparent',
            'ie_key': 'ThePlatform',
            'id': video_id,
            'url': smuggle_url(self._proto_relative_url(theplatform_url), {'force_smil_url': True}),
        }
