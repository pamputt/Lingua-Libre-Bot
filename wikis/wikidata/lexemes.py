#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# Author: Sylvain Boissel
# Date: 16 December 2018
# License: GNU GPL v2+

import re
import uuid

from wikis.wikifamily import WikiFamily

PRONUNCIATION_PROPERTY = "P443"
REFURL_PROPERTY = "P854"
SUMMARY = "Add an audio pronunciation file from Lingua Libre"
BRACKET_REGEX = re.compile(r" \([^(]+\)$")


class Lexemes(WikiFamily):

    def __init__(self, user, password):
        """
        Constructor.

        Parameters
        ----------
        user
            Username to login to the wiki.
        password
            Password to log into the account.
        """
        super().__init__(user, password, "wikidata", "www")

    """
    Public methods
    """
    # Prepare all the records for their use on Wikidata
    # Currently not needed
    def prepare(self, records):
        return records

    def execute(self, record):
        if record["links"]["lexeme"] is None:
            return False

        if not re.match("^L\d+-F\d+$", record["links"]["lexeme"]):
            print(record["links"]["lexeme"] + "is not a valid lexeme form id")

        if self.is_already_present(record["links"]["lexeme"], record["file"]):
            print(record["id"] + ": already on Wikidata")
            return False

        result = self.do_edit(
            record["links"]["lexeme"],
            record["file"],
            record["id"],
        )
        if result is True:
            print(
                record["id"]
                + ": added to Wikidata - https://www.wikidata.org/wiki/Lexeme:"
                + record["links"]["lexeme"].replace("-", "#")
            )

        return result

    """
    Private methods
    """

    def is_already_present(self, entityId, filename):
        response = self.api.request(
            {
                "action": "wbgetclaims",
                "format": "json",
                "entity": entityId,
                "property": PRONUNCIATION_PROPERTY,
            }
        )

        if PRONUNCIATION_PROPERTY in response["claims"]:
            for claim in response["claims"][PRONUNCIATION_PROPERTY]:
                if claim["mainsnak"]["datavalue"]["value"] == filename:
                    return True
        return False

        # Add the given record in a new claim of the given item

    def do_edit(self, entityId, filename, lingualibreId):
        response = self.api.request(
            {
                "action": "wbsetclaim",
                "format": "json",
                "claim": '{"type":"statement","mainsnak":{"snaktype":"value","property":"'
                + PRONUNCIATION_PROPERTY
                + '","datavalue":{"type":"string","value":"'
                + filename
                + '"}},"id":"'
                + entityId
                + "$"
                + str(uuid.uuid4())
                + '","qualifiers":{},"references":[{"snaks":{"'
                + REFURL_PROPERTY
                + '":[{"snaktype":"value","property":"'
                + REFURL_PROPERTY
                + '","datavalue":{"type":"string","value":"https://lingualibre.org/wiki/'
                + lingualibreId
                + '"}}]}}],"rank":"normal"}',
                "summary": SUMMARY,
                "token": self.api.get_csrf_token(),
                "bot": 1,
            }
        )

        if "success" in response:
            return True

        print(response)
        return False
