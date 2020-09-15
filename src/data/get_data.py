##### libraries ######

import pandas as pd
import numpy as np

import subprocess
import os

from datetime import datetime

import requests
import json


##### gitub data #####

def get_johns_hopkins():
    """ 
    Get or update data by a git pull request, the source code has to be pulled first.
    Result is stored in the predifined csv structure
    """

    git_pull = subprocess.Popen( "git pull " ,
                         cwd = 'data/raw/COVID-19/',
                         shell = True,
                         stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE )
    (out, error) = git_pull.communicate()


    print("Error : " + str(error))
    print("out : " + str(out))


if __name__ == '__main__':
    get_johns_hopkins()