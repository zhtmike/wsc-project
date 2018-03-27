import os

from pycorenlp import StanfordCoreNLP


class NLPFactory:
    def __init__(self):
        self.url = os.environ.get("CORENLP_URL", "http://localhost:9000")
        self.nlp = StanfordCoreNLP(self.url)

    def annotate(self, text):
        """
        annotate by dependence parser
        Args:
            text (str): input data

        Returns:
            json
        """
        # corenlp will treat sentences with full stop independently
        text = text.replace('.', ',').replace('!', ',')
        return self.nlp.annotate(text, properties={"annotators": "pos,lemma,depparse,sentiment", "outputFormat": "json"})


class ContentParser:
    @staticmethod
    def dependencies(content):
        """
        Read the depencencies
        """
        assert len(content['sentences']) == 1, content
        tree = {}
        for item in content['sentences'][0]['basicDependencies']:
            tree[item['dependentGloss']] = {
                'dep': item['dep'], 'gvn': item['governorGloss']}
        return tree

    @staticmethod
    def tokenize(content):
        """
        Read the token
        """
        assert len(content['sentences']) == 1
        return content['sentences'][0]['tokens']

    @staticmethod
    def sentiment(content):
        """
        Read the sentiment, from 0 (Very negative) to 4 (Very positive)
        """
        assert len(content['sentences']) == 1
        return int(content['sentences'][0]['sentimentValue'])

    def create_lemma(self, content):
        """
        Create a lemma dict
        """
        return {item['originalText']: item['lemma'] for item in self.tokenize(content)}

    def create_tagging(self, content):
        """
        Create a POS tagging dict
        """
        return {item['originalText']: item['pos'] for item in self.tokenize(content)}
