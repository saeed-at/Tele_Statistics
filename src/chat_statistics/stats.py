import json
from collections import Counter
from importlib.resources import path
from pathlib import Path
from typing import Dict, Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """
    Generates chat statistics from telegran chat json file
    """
    def __init__(self, chat_json:Union[str, Path]):
        """
         Args:
            chat_json (Union[str, Path]): path to telegram export json file
        """
        #load chat data
        logger.info(f"Loading chat data from {chat_json}...")
        with open(chat_json) as f :
            self.chat_data = json.load(f)

        self.normalizer = Normalizer()

        #load stop words 
        logger.info(f"Loading stop words from {DATA_DIR}...")
        stop_words = open(str(DATA_DIR/'stopwords.txt')).readlines()
        stop_words = list(map(str.strip,stop_words))
        self.stop_words = list(map(self.normalizer.normalize,stop_words))

    def generate_word_cloud(self, output_dir):
        #Reading chat data
        logger.info(f"Reading data and removing stop words...")
        text_content = ''
        for msg in self.chat_data['messages'] :
            if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item : item not in self.stop_words, tokens))
                text_content += f" {' '.join(tokens)}"
        # normalize text content
        text_content = self.normalizer.normalize(text_content)
        #Making word cloud
        logger.info(f"Making word cloud...")
        wordcloud = WordCloud(
            font_path= str(DATA_DIR/'font.ttf'),
            background_color='white',
            width=1920,height=1080,
            collocations=False,
            max_font_size=250,
            ).generate(text_content)
        # save word cloud
        logger.info(f"Saving word cloud in {output_dir}...")
        wordcloud.to_file(str(Path(output_dir)/'wordcloud.png'))

if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR/'result.json')
    chat_stats.generate_word_cloud(DATA_DIR)
    print('done')


        
