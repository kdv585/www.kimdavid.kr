import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging
from konlpy.tag import Okt
import pandas as pd

logger = logging.getLogger(__name__)

class SamsungWordCloud:
    
    
    def __init__(self):
        pass