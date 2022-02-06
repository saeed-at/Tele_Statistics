import json
from collections import Counter, defaultdict
from importlib.resources import path
from pathlib import Path
from typing import Dict, Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, sent_tokenize, word_tokenize
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
        stop_words = set(map(str.strip,stop_words))
        self.stop_words = set(map(self.normalizer.normalize,stop_words))

    def generate_word_cloud(self, output_dir):
        """ Generates a word cloud for telegran json file

        Args:
            output_dir (str): path to save wordcloud.png image
        """
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

    def get_top_users(self, top_n=1):
        """get top users in replying to others questions.

        Args:
            top_n (int): number of top users . Defaults to 1.

        Returns:
            [dict]: dictionary which contain 'top_n' users.
        """
        logger.info("getting top users...")
        # get check messages for questions 
        is_question = defaultdict(bool)
        for msg in self.chat_data["messages"] :
            if not isinstance(msg,str):
                msg['text'] = self.rebuild_msg(msg['text'])
            sentences = sent_tokenize(msg['text'])
            for sentence in sentences :
                if ('?' not in sentence) and ('؟' not in sentence) :
                    continue
                is_question[msg['id']] = True
        #get top users replying to questions 
        users = []
        for msg in self.chat_data['messages'] :
            if not msg.get('reply_to_message_id'):
               continue
            if not is_question[msg['reply_to_message_id']] :
                continue
            users.append(msg['from'])
        return dict(Counter(users).most_common(top_n))

    @staticmethod
    def rebuild_msg(sub_messages):
        """rebiulds messages.

        Args:
            sub_messages list: list of different types like links,text,media and

        Returns:
            list: a lits of texts which are in between data in sub messages.
        """
        msg_text = ''
        for sub_msg in sub_messages :
            if isinstance(sub_msg,str):
                msg_text+= sub_msg  
            elif 'text' in sub_msg:
                msg_text+= sub_msg['text']
        return msg_text


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR/'result.json')
    chat_stats.generate_word_cloud(DATA_DIR)
    top_users = chat_stats.get_top_users()
    print(top_users)
    print('done')
    