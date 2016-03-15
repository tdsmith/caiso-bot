import os
import sys

import requests
import requests_oauthlib

import fetch_caiso

secrets = os.path.join(os.path.dirname(__file__), "secrets")

consumer_key, consumer_secret, token, token_secret = \
    [line.strip() for line in open(secrets)]


def compose_tweet():
    renewables = fetch_caiso.get_current_renewables()
    demand = fetch_caiso.get_current_demand()
    tweet = "⚡️🐻⚡️ Total: %d MW\n☀️: %d MW (%03.1f%%)\n🌬: %d MW (%03.1f%%)" % (
        demand,
        renewables["Solar"],
        abs(renewables["Solar"]/demand * 100),
        renewables["Wind"],
        renewables["Wind"]/demand * 100
    )
    return tweet


def perform_tweet():
    auth = requests_oauthlib.OAuth1(consumer_key, consumer_secret, token, token_secret)
    response = requests.post(
        "https://api.twitter.com/1.1/statuses/update.json",
        auth=auth,
        params={
            "status": compose_tweet(),
        })
    response.raise_for_status()


if __name__ == "__main__":
    if "tweet" in sys.argv:
        perform_tweet()
    else:
        print(compose_tweet())
