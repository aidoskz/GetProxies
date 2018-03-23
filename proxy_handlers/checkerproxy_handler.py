# -*- coding: utf-8 -*-

import json
import lxml.html
import requests

from thread_manager import ThreadHandler
from requests.exceptions import Timeout, TooManyRedirects, RequestException


class CheckerProxyHandler(ThreadHandler):
    """
    Class to get proxies in checkerproxy.net
    """

    def __init__(self, event_log, header):
        super(CheckerProxyHandler, self).__init__()
        self.log = event_log
        self.header = header

    def initialize(self):
        """
        Start threads to get proxies

        :return: Array list proxies
        """

        self.log(
            'Looking at checkerproxy.net...',
            flush=True
        )

        results = []
        threads = []

        pages = self.pages()
        pages_per_threads = (pages[i:i + 2] for i in xrange(0, len(pages), 2))
        for pgs in pages_per_threads:
            threads.append(
                ThreadHandler(
                    target=self.get,
                    args=(
                        pgs,
                    )
                )
            )

        for thread in threads:
            thread.start()

        for thread in threads:
            results.append(
                thread.join()
            )

        result = [x for i in results for x in i]

        self.log(
            'Total at checkerproxy.net: \033[93m{}'.format(
                len(result)
            )
        )

        return result

    def pages(self):
        """
        Get pages link's

        :return: Pages link's
        """

        result = []

        try:
            resp = requests.get(
                'https://checkerproxy.net/getAllProxy',
                headers=self.header
            )
        except Timeout:
            return result
        except TooManyRedirects:
            return result
        except RequestException as err:
            self.log(err, 'ERROR', True)
            return result

        tree = lxml.html.fromstring(resp.text)
        div = tree.find('.//div[@class="block archive full_list"]')
        for page in div.findall('.//a'):
            result.append(page.attrib['href'])

        return result

    def get(self, pages):
        """
        Get proxies

        :param pages: Pages to get proxies
        :return: Array proxies
        """

        result = []

        for page in pages:
            try:
                resp = requests.get(
                    'https://checkerproxy.net/api{}'.format(
                        page
                    ),
                    headers=self.header
                )
            except Timeout:
                return result
            except TooManyRedirects:
                return result
            except RequestException as err:
                self.log(err, 'ERROR', True)
                return result

            data = json.loads(resp.text)
            for i in data:
                result.append(str(i['addr']))

        return result
