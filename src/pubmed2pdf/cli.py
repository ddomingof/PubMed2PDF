# -*- coding: utf-8 -*-

"""Command line interface."""

import logging

import click

logger = logging.getLogger(__name__)
from .constants import DEFAULT_ERROR_FILE, DATA_DIR
from .utils import *


@click.group(help='pubmed2pdf')
def main():
    """Run pubmed2pdf."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


@main.command()
@click.option('--pmids', help='Comma separated list of pmids to fetch', type=str)
@click.option('--pmidsfile', help='File with pmids to fetch inside', type=click.Path(exists=True))
@click.option('--out', help='Output directory for fetched articles', default=DATA_DIR,
              type=click.Path(exists=True), show_default=True)
@click.option('--errors', help='Output file path for pmids which failed to fetch', default=DEFAULT_ERROR_FILE,
              type=click.Path(), show_default=True)
@click.option('--maxtries', help='Max number of tries per article', default=3, type=int, show_default=True)
@click.option('-v', '--verbose', help='Log everything', is_flag=True)
def pdf(pmids, pmidsfile, out, errors, maxtries, verbose):
    """Get PDFs from PubMed idenfiers."""

    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('Full log mode activated')
    else:
        logger.setLevel(logging.INFO)

    # Checking arguments
    if not pmids and not pmidsfile:
        click.echo("Error: One of the two arguments '--pmids' or '--pmidsfile' must be used. Exiting...")
        exit(1)
    if pmids and pmidsfile:
        click.echo("Error: --pmids and --pmidsfile cannot be used together. Please select only one. Exiting...")
        exit(1)

    if not os.path.exists(out):
        click.echo(f"Output directory of {out} did not exist.  Created the directory.")
        os.mkdir(out)

    finders = [
        'genericCitationLabelled',
        'pubmed_central_v2',
        'acsPublications',
        'uchicagoPress',
        'nejm',
        'futureMedicine',
        'science_direct',
        'direct_pdf_link',
    ]

    # Add headers
    headers = requests.utils.default_headers()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) ' \
                            'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/56.0.2924.87 ' \
                            'Safari/537.36'

    if pmids:
        # Split by comma the pubmeds
        pmids = pmids.split(",")
        names = pmids
    else:
        # Read file and get the pubmeds
        pmids = [
            line.strip().split()
            for line in open(pmidsfile)
        ]
        # Get names if there are two columns
        if len(pmids[0]) == 1:
            pmids = [
                x[0]
                for x in pmids
            ]
            names = pmids

        else:
            names = [x[1] for x in pmids]
            pmids = [x[0] for x in pmids]

    failed_pubmeds = []

    # Fetching pubmeds from different sources and exporting
    for pmid, name in zip(pmids, names):
        logger.info("Trying to fetch pmid {0}".format(pmid))
        retriesSoFar = 0
        while retriesSoFar < maxtries:
            try:
                soup = fetch(pmid, finders, name, headers, failed_pubmeds, out)
                retriesSoFar = maxtries
            except requests.ConnectionError as e:
                if '104' in str(e) or 'BadStatusLine' in str(e):
                    retriesSoFar += 1
                    if retriesSoFar < maxtries:
                        logger.debug("** fetching of reprint {0} failed from error {1}, retrying".format(pmid, e))
                    else:
                        logger.debug("** fetching of reprint {0} failed from error {1}".format(pmid, e))
                        failed_pubmeds.append(pmid)
                else:
                    logger.debug("** fetching of reprint {0} failed from error {1}".format(pmid, e))
                    retriesSoFar = maxtries
                    failed_pubmeds.append(pmid)
            except Exception as e:
                logger.debug("** fetching of reprint {0} failed from error {1}".format(pmid, e))
                retriesSoFar = maxtries
                failed_pubmeds.append(pmid)

    with open(errors, 'w+') as error_file:
        for pubmed_id in failed_pubmeds:
            error_file.write("{}\n".format(pubmed_id))

    click.echo(f"Done downloading. All downloaded can be found in {out}")


if __name__ == '__main__':
    main()
