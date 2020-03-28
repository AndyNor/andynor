# -*- coding: utf-8 -*-
import os
def this_env():
	os.environ["THIS_ENV"] = 'DEV' # "PROD" | "DEV"

from secrets_dev import load_secrets
load_secrets()