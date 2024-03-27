# -*- coding: utf-8 -*-

"""This module contains all the constants used in pubmed2pdf repo."""

import logging
import os
import re
import urllib

import requests
from bs4 import BeautifulSoup

from Bio import Entrez

logger = logging.getLogger(__name__)


def getMainUrl(url):
    return "/".join(url.split("/")[:3])


def save_pdf_from_url(pdf_url: str, output_dir: str, name: str, headers: str) -> None:
    """Save file as a pdf."""
    response = requests.get(pdf_url, headers=headers, allow_redirects=True)

    # likely to be a pdf
    if response.apparent_encoding is None:
        with open('{0}/{1}.pdf'.format(output_dir, name), 'wb') as f:
            f.write(response.content)
    else:
        with open('{0}/{1}.html'.format(output_dir, name), 'wb') as f:
            f.write(response.content)


def fetch(pmid, finders, name, headers, errorPmids, output_dir):
    """Download a pdf from a pmid."""
    if os.path.exists("{0}/{1}.pdf".format(output_dir, pmid)):  # bypass finders if pdf reprint already stored locally
        logger.debug("** Reprint #{0} already downloaded and in folder; skipping.".format(pmid))
        return

    uri = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id={0}&retmode=ref&cmd=prlinks".format(
        pmid
    )
    success = False
    dontTry = False

    # first, download the html from the page that is on the other side of the pubmed API
    req = requests.get(uri, headers=headers)
    if 'ovid' in req.url:
        logger.debug(
            "** Reprint {0} cannot be fetched as ovid is not supported by the requests package.".format(pmid)
        )
        errorPmids.write("{}\t{}\n".format(pmid, name))
        dontTry = True
        success = True

    soup = BeautifulSoup(req.content, 'lxml')
    #         return soup
    # loop through all finders until it finds one that return the pdf reprint
    if not dontTry:
        for finder in finders:
            logger.debug("Trying {0}".format(finder))
            pdf_url = eval(finder)(req, soup, headers)
            if type(pdf_url) != type(None):
                save_pdf_from_url(pdf_url.strip(), output_dir, name, headers)
                success = True
                logger.debug("** fetching of reprint {0} succeeded".format(pmid))
                break

    if not success:
        logger.debug("** Reprint {0} could not be fetched with the current finders.".format(pmid))
        errorPmids.write("{}\t{}\n".format(pmid, name))


def search_pubmed(query):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=100)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def acsPublications(req, soup, headers):
    possibleLinks = [
        x
        for x in soup.find_all('a')
        if type(x.get('title')) == str and (
            'high-res pdf' in x.get('title').lower()
            or 'low-res pdf' in x.get('title').lower())
    ]

    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'acsPublications' finder...")
        pdfUrl = getMainUrl(req.url) + possibleLinks[0].get('href')
        return pdfUrl

    return None


def direct_pdf_link(req):
    if req.content[-4:] == '.pdf':
        logger.debug("** fetching reprint using the 'direct pdf link' finder...")
        pdfUrl = req.content
        return pdfUrl

    return None


def futureMedicine(req, soup, headers):
    possibleLinks = soup.find_all('a', attrs={'href': re.compile("/doi/pdf")})
    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'future medicine' finder...")
        pdfUrl = getMainUrl(req.url) + possibleLinks[0].get('href')
        return pdfUrl
    return None


def genericCitationLabelled(req, soup, headers):
    possibleLinks = soup.find_all('meta', attrs={'name': 'citation_pdf_url'})
    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'generic citation labelled' finder...")
        pdfUrl = possibleLinks[0].get('content')
        return pdfUrl
    return None


def nejm(req, soup, headers):
    possibleLinks = [
        x for x in soup.find_all('a')
        if type(x.get('data-download-type')) == str and (x.get('data-download-type').lower() == 'article pdf')
    ]

    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'NEJM' finder...")
        pdfUrl = getMainUrl(req.url) + possibleLinks[0].get('href')
        return pdfUrl

    return None


def pubmed_central_v1(req, soup, headers):
    possibleLinks = soup.find_all('a', re.compile('pdf'))

    possibleLinks = [
        x for x in possibleLinks
        if 'epdf' not in x.get('title').lower()
    ]  # this allows the pubmed_central finder to also work for wiley

    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'pubmed central' finder...")
        pdfUrl = getMainUrl(req.url) + possibleLinks[0].get('href')
        return pdfUrl

    return None


def pubmed_central_v2(req, soup, headers):
    possibleLinks = soup.find_all('a', attrs={'href': re.compile('/pmc/articles')})

    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'pubmed central' finder...")
        pdfUrl = "https://www.ncbi.nlm.nih.gov/{}".format(possibleLinks[0].get('href'))
        return pdfUrl

    return None


def science_direct(req, soup, headers):
    newUri = urllib.parse.unquote(soup.find_all('input')[0].get('value'))
    req = requests.get(newUri, allow_redirects=True, headers=headers)
    soup = BeautifulSoup(req.content, 'lxml')

    possibleLinks = soup.find_all('meta', attrs={'name': 'citation_pdf_url'})

    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'science_direct' finder...")
        req = requests.get(possibleLinks[0].get('content'), headers=headers)
        soup = BeautifulSoup(req.content, 'lxml')
        pdfUrl = soup.find_all('a')[0].get('href')
        return pdfUrl
    return None


def uchicagoPress(req, soup, headers):
    possibleLinks = [
        x
        for x in soup.find_all('a')
        if type(x.get('href')) == str and 'pdf' in x.get('href') and '.edu/doi/' in x.get('href')
    ]
    if len(possibleLinks) > 0:
        logger.debug("** fetching reprint using the 'uchicagoPress' finder...")
        pdfUrl = getMainUrl(req.url) + possibleLinks[0].get('href')
        return pdfUrl

    return None
