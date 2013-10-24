import requests
from httplib import OK, CannotSendRequest
from pyquery import PyQuery
import urlparse
import logging

BEERSMITHRECIPES_URL = "http://beersmithrecipes.com/"


class Beersmith(object):
    def __init__(self, username, password, session=None,
            url=BEERSMITHRECIPES_URL):
        self.username = username
        self.password = password
        self.url = url
        if not session:
            session = requests.Session()
        self.session = session
        self._login()
        self.log = logging.getLogger(
            "scrapebeersmith.Beersmith.%s" % self.username)

    def _login(self):
        response = self.session.post(self.url, data={
            'submitted': 1,
            'action': 'dologin',
            'submit': 'Login',
            'uname': self.username,
            'password': self.password
        })
        if response.status_code != OK:
            raise CannotSendRequest(
                "Received unexpected status code: %d" % response.status_code)

    def download_all_recipes(self, destination='.'):
        """
        Download all the user's recipes as bsmx files
        """
        self.log.debug("Downloading all recipes for user: %s" % self.username)
        response = self.session.get("http://beersmithrecipes.com/myrecipes")
        if response.status_code != OK:
            raise CannotSendRequest(
                "Received unexpected status code: %d" % response.status_code)
        d = PyQuery(response.text)
        rating_floats = d('div.ratingfloat')
        for rating_float in rating_floats:
            for link in rating_float.iterchildren('a'):
                if 'download' in link.text.lower():
                    url = link.attrib['href']
                    url_path = urlparse.urlsplit(url).path
                    url_parts = url_path.split("/")
                    recipe_id = int(url_parts[2])
                    download_url = urlparse.urljoin(
                        self.url, "download.php?id=%d" % recipe_id)
                    _download_file(
                        download_url, "%d.bsmx" % recipe_id, self.session)


def _download_file(url, local_filename, session):
    log = logging.getLogger("scrapebeersmith._download_file")
    r = session.get(url)
    with open(local_filename, 'wb') as f:
        log.debug("Downloading %s to file: %s" % (url, local_filename))
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()

