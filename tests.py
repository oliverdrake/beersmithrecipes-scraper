import mock
from httplib import OK
import urlparse
from nose.tools import assert_in

from scrapebeersmith import Beersmith, _download_file


def test_login_uses_params():
    username = "me"
    password = "mypass"
    session = mock.Mock()
    session.post().status_code = OK
    url = "dummyurl"
    Beersmith(username=username, password=password, session=session, url=url)
    session.post.assert_called_with(url, data={
            'submitted': 1,
            'action': 'dologin',
            'submit': 'Login',
            'uname': username,
            'password': password,
        })


@mock.patch("scrapebeersmith._download_file")
@mock.patch("requests.Session")
def test_download_all_recipes(Session, _download_file):
    Session().post().status_code = OK
    Session().get().status_code = OK
    Session().get().text = """
    <div class="ratingfloat">
        <a href="http://blah.com/download/1/">download</a>
    </div>
    <div class="ratingfloat">
        <a href="http://blah.com/download/23/">download</a>
    </div>
    """
    beersmith = Beersmith("me", "password", url="http://base.com/")
    beersmith.download_all_recipes()
    for i in [1, 23]:
        url = urlparse.urljoin("http://base.com/", "download.php?id=%d" % i)
        assert_in(
            mock.call(url, "%d.bsmx" % i, beersmith.session),
            _download_file.mock_calls)


@mock.patch("__builtin__.open")
def test__download_file(open_):
    session = mock.Mock()
    session.get().iter_content.return_value = chunks = "abcdef"
    url = "http://dummy"
    local_filename = "test.bsmx"
    _download_file(url, local_filename, session)
    session.get.assert_called_with(url)
    for c in chunks:
        assert_in(mock.call(c), open_().__enter__().write.mock_calls)

