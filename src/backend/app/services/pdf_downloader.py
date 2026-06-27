import os
import requests


def download_pdf(
    pdf_url,
    destination
):

    response = requests.get(pdf_url)

    with open(destination, "wb") as f:
        f.write(response.content)

    return destination