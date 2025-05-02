import logging
import json
import os
import CouchEventPortfolioDB
from pathlib import Path

if __name__ == "__main__":
    logging.info("Starting the event portfolio manager load service for UAT...")
    try:
        dbcfg = "couchdb.json"
        datadir = "/data/"

        # Get a database instance here...
        with open(dbcfg, "r", encoding="utf-8") as cfg:
            data = json.loads(cfg.read())

            db = CouchEventPortfolioDB.CouchEventPortfolioDB(data)

            logging.info("Purge the database before loading new event portfolios...")
            db.purge_portfolios()
            logging.info("Database purged successfully")

            # Get each of the JSON files from the given data directory and load into the database
            for fn in sorted(Path(datadir).glob("*.json"), reverse=True):
                if os.path.isfile(fn):
                    try:
                        with open(fn) as json_file:
                            db.save_portfolio(json.load(json_file))
                    except Exception as e:
                        logging.warning(
                            "Unable to save event portfolio from %s due to exception: %s",
                            str(fn),
                            str(e),
                        )
                else:
                    logging.warning("Unable to located and/or read event portfolio: %s", fn)

    except Exception as e:
        logging.error("Could not start the event portfolio manager loader due to exception: %s", e)
    finally:
        logging.info("Shutting down the event portfolio manager loader")
