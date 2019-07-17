#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import signal
import sys
from threading import Event
import time
import traceback


# -- Set Up Import Paths:
# -----------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitecomber.settings.worker")

import django
from django.conf import settings
from django.db import close_old_connections, reset_queries
from django.db import connection
from django.utils.log import configure_logging

configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)

logger = logging.getLogger(settings.WORKER_ID)
django.setup()

from sitecomber.apps.config.models import Site


class Worker:

    running = False
    heartbeat_start_time = time.time()
    heartbeat_url_valid = None
    database_restart_time = time.time()
    loop_timer = Event()
    loop_duration = 1

    sites = None

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        logger.info("%s :: %s" % (settings.WORKER_NAME, self.pidfile))

        signal.signal(signal.SIGINT, self.sigint)
        signal.signal(signal.SIGTERM, self.sigterm)
        signal.signal(signal.SIGQUIT, self.sigquit)

    def start(self):
        if self.running:
            return
        self.running = True
        logger.info("%s :: start" % settings.WORKER_NAME)

        self.pidcheck()
        try:
            self.on_start()
        except Exception as ex:
            sys.stderr.write(u"%s :: Error calling on_start" % settings.WORKER_NAME)
            logger.exception(ex)
            self.stop()
            sys.exit(1)

        self.run()

    def stop(self):
        if not self.running:
            return

        self.loop_timer.set()
        self.running = False

        logger.info("%s :: stop" % settings.WORKER_NAME)

        try:
            self.on_stop()
        except Exception as ex:
            sys.stderr.write(u"%s :: Error calling on_stop" % settings.WORKER_NAME,)
            logger.exception(ex)

        self.delpid()

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        while self.running and not self.loop_timer.is_set():
            self.check_database()

            try:
                self.on_loop()
            except Exception as ex:
                sys.stderr.write(u"%s :: Error calling on_loop" % settings.WORKER_NAME)
                logger.exception(ex)

                # If an error has happened in the loop, attempt to establish a
                # new DB connection
                self.reset_database_connection()

            logger.debug("%s :: waiting to loop for %s seconds" %
                         (settings.WORKER_NAME, self.loop_duration))
            self.loop_timer.wait(self.loop_duration)

    def on_start(self):
        self.sites = Site.objects.filter(active=True)
        for site in self.sites:
            if not self.running:
                return
            site.parse_sitemap()

    def on_loop(self):
        for site in self.sites:
            if not self.running:
                return
            site.crawl(settings.LOAD_BATCH_SIZE)

    def on_stop(self):
        # OVERRIDE IN SUBCLASS
        pass

    # -- Signal Handlers
    def sigint(self, signum, frame):
        logger.info("%s :: sigint" % settings.WORKER_NAME)
        self.stop()

    def sigterm(self, signum, frame):
        logger.info("%s :: sigterm" % settings.WORKER_NAME)
        self.stop()

    def sigquit(self, signum, frame):
        logger.info("%s :: sigquit" % settings.WORKER_NAME)
        self.stop()

    def pidcheck(self):

        # Check for a pidfile to see if the daemon already runs
        if os.path.exists(self.pidfile):
            message = "%s :: pidfile %s already exists. Worker is already running." % (
                settings.WORKER_NAME, self.pidfile)
            logger.error(message)
            sys.stderr.write(message)
            sys.exit(1)

        pid = str(os.getpid())
        logger.info("%s :: create PID file %s : %s" %
                    (settings.WORKER_NAME, self.pidfile, pid))

        f = open(self.pidfile, 'w')
        f.write(pid)
        f.close()

        if not os.path.exists(self.pidfile):
            message = "%s :: pidfile %s does not exist." % (settings.WORKER_NAME, self.pidfile)
            logger.error(message)
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        else:
            logger.info("%s :: pidfile %s exists as expected." %
                        (settings.WORKER_NAME, self.pidfile))

    def delpid(self):

        if os.path.exists(self.pidfile):

            try:
                    # Attempt to stop by PID:
                if os.path.exists(settings.PID_FILE):
                    f = open(settings.PID_FILE, 'r')
                    id = int(f.read())
                    os.kill(id, signal.SIGTERM)
            except OSError as e:
                logger.info(
                    "%s :: Error when trying to kill PID %s: %s" % (settings.WORKER_NAME, self.pidfile, e))

        if not os.path.exists(self.pidfile):
            message = "pidfile %s does not exist. Daemon worker not running?"
            logger.info(message)
            sys.stderr.write(message % self.pidfile)
            return

        os.remove(self.pidfile)

    def check_database(self):
        elapsed_time = time.time() - self.database_restart_time
        if(elapsed_time >= settings.WORKER_DATABASE_REFRESH_FREQUENCY):
            self.reset_database_connection()

    def reset_database_connection(self):
        self.database_restart_time = time.time()

        # If database becomes disconnected, you can reset it with these
        # functions:
        reset_queries()
        close_old_connections()
        connection.close()


# -- Run It!
# -----------------------------------------------------------------------------


def worker_exception_handler(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
    logger.error(traceback.format_exception(exc_type, exc_value, exc_tb))
    if worker:
        worker.stop()
sys.excepthook = worker_exception_handler


if __name__ == "__main__":

    if len(sys.argv) == 2:
        command = sys.argv[1]
    else:
        command = 'start'

    logger.info("%s [%s] " % (settings.WORKER_NAME, command))

    logger.info("%s is using PID: %s" % (settings.WORKER_NAME, settings.PID_FILE))
    logger.info("%s is using log file: %s" % (settings.WORKER_NAME, settings.LOG_FILE))

    if 'start' == command:
        logger.info(u"%s: Starting ..." % (settings.WORKER_NAME))
        worker = Worker(settings.PID_FILE)
        worker.start()
    elif 'stop' == command:
        logger.info(u"%s: Stopping ..." % (settings.WORKER_NAME))

        if os.path.exists(settings.PID_FILE):

            try:
                # Attempt to stop by PID:
                f = open(settings.PID_FILE, 'r')
                id = int(f.read())
                logger.info(u"%s: Stopping PID %s" %
                            (settings.WORKER_NAME, id))
                os.kill(id, signal.SIGTERM)

            except OSError as e:
                logger.info(u"%s: Error stopping: %s" %
                            (settings.WORKER_NAME, e))

            os.remove(settings.PID_FILE)

    elif 'restart' == command:
        worker = Worker(settings.PID_FILE)
        worker.restart()
    else:
        print("Unknown command")
    sys.exit(0)
