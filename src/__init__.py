#!/usr/bin/python
"""
Created on 2013-07-24
Author: Wiwiweb

Initialises and runs the bot in a loop.

"""

from sakuraibot import SakuraiBot
import logging
import sys
import urllib2
import smtplib
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from time import sleep

FREQUENCY = 300

LOG_FILE = "../logs/sakuraibot.log"
LOG_FILE_DEBUG = "../logs/sakuraibot-debug.log"
LAST_POST_FILENAME = "../res/last-post.txt"
EXTRA_COMMENT_FILENAME = "../res/extra-comment.txt"
PICTURE_MD5_FILENAME = "../res/last-picture-md5.txt"

MAIL_ADDRESS = "sakuraibotalert@gmail.com"
SENDER_MAIL_ADDRESS = "sakuraibotalert@gmail.com"
SMTP_HOST = "smtp.gmail.com:587"
MAIL_PASSWORD_FILENAME = "../res/private/mail-password.txt"

f = open(MAIL_PASSWORD_FILENAME, 'r')
mail_password = f.read().strip()
f.close()

# -------------------------------------------------
# Main loop
# -------------------------------------------------

if len(sys.argv) > 1 and '--debug' in sys.argv:
    debug = True
    username = 'SakuraiBot_test'
    subreddit = 'SakuraiBot_test'
    imgur_album_id = 'ugL4N'
else:
    debug = False
    username = 'SakuraiBot'
    subreddit = 'smashbros'
    imgur_album_id = '8KnTr'

root_logger = logging.getLogger()
if debug:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')
else:
    # Logging
    timed_handler = TimedRotatingFileHandler(LOG_FILE, 'midnight')
    timed_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    timed_handler.setLevel(logging.INFO)
    debug_handler = RotatingFileHandler(LOG_FILE_DEBUG, maxBytes=102400,
                                        backupCount=1)
    debug_handler.setLevel(logging.DEBUG)
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(timed_handler)
    root_logger.addHandler(debug_handler)

if len(sys.argv) > 1 and '--miiverse' in sys.argv:
    miiverse_main = True
    logging.info("Main pic: Miiverse")
else:
    miiverse_main = False
    logging.info("Main pic: smashbros.com")


def send_alert_mail():
    message = "From: Script Alert: SakuraiBot <" + MAIL_ADDRESS + ">\n" \
              "Subject: SakuraiBot stopped unexpectedly!\n\n"
    f = open(LOG_FILE_DEBUG, 'r')
    log_content = f.read()
    f.close()
    message += log_content
    try:
        smtp = smtplib.SMTP(SMTP_HOST)
        smtp.starttls()
        logging.debug(MAIL_ADDRESS)
        logging.debug(mail_password)
        smtp.login(MAIL_ADDRESS, mail_password)
        smtp.sendmail(MAIL_ADDRESS, MAIL_ADDRESS, message)
        logging.info("Alert email sent.")
    except smtplib.SMTPException as e:
        logging.error("ERROR: Couldn't send alert email: " + str(e))

global_retries = 5


def retry_or_die(dont_retry):
    global global_retries
    if global_retries == 0 or dont_retry:
        logging.error("ERROR: Shutting down SakuraiBot.")
        send_alert_mail()
        quit()
    else:
        global_retries -= 1
        logging.error("ERROR: Sleeping another cycle and retrying "
                      + str(global_retries) + " more times.")

if __name__ == '__main__':
    logging.info("--- Starting sakuraibot ---")
    sbot = SakuraiBot(username, subreddit, imgur_album_id,
                      LAST_POST_FILENAME, EXTRA_COMMENT_FILENAME,
                      PICTURE_MD5_FILENAME,
                      debug=debug)
    try:
        while True:
            try:
                logging.info("Starting the cycle again.")
                sbot.bot_cycle()
                if debug:  # Don't loop in debug
                    quit()
                global_retries = 5
                sbot.dont_retry = False

            except urllib2.HTTPError as e:
                logging.exception("ERROR: HTTPError code " + str(e.code) +
                                  " encountered while making request.")
                retry_or_die(sbot.dont_retry)
            except urllib2.URLError as e:
                logging.exception("ERROR: URLError: " + str(e.reason))
                retry_or_die(sbot.dont_retry)
            except Exception as e:
                logging.exception("ERROR: Unknown error: " + str(e))
                retry_or_die(sbot.dont_retry)

            sleep(FREQUENCY)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected, shutting down Sakuraibot.")
        quit()
