from __future__ import print_function
from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
import json
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import os
import sys

DATA_DIR = '/Users/avgupta/devnull/poc_tagging/data_bigquery/'

class TopicExtraction(object):
    """Extract topics using NMF and LDA"""
    def __init__(self):
        # set the hyperparameters
        self.n_features = 1000
        self.n_topics = 1
        self.n_top_words = 4
        self.keywords = {}

    def save_top_words(self, model, feature_names, n_top_words, package_name, method):
        if package_name not in self.keywords:
            self.keywords[package_name] = {}
        if method not in self.keywords[package_name]:
            self.keywords[package_name][method] = []
        for topic_idx, topic in enumerate(model.components_):
            # print("Topic #%d:" % topic_idx)
            # print(package_name)
            # print(method)
            self.keywords[package_name][method].append(
                [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        return self.keywords

    def save_to_file(self):
        with open('topics_all_packages.json', 'w') as f:
            f.write(json.dumps(self.keywords))

    def load_dataset(self, path_to_bigquery_json):
        print("Loading dataset...")
        t0 = time()
        with open(os.path.join(DATA_DIR, path_to_bigquery_json), 'r') as struts_data_file:
            dataset = json.loads(struts_data_file.read())
        # Replace anchors with content where relevant and extract otherwise
        cleaned_dataset = []

        for readme in dataset:
            soup = BeautifulSoup(readme, "html.parser")
            for link in soup.findAll('a'):
                if link.text.startswith('http'):
                    link.extract()
                else:
                    link.replaceWithChildren()
            # Remove all the images
            for image in soup.findAll('img'):
                image.extract()
            # Remove all the code blocks
            for code_block in soup.findAll('code'):
                code_block.extract()
            cleaned_dataset.append(soup.text)
        print("done in %0.3fs." % (time() - t0))
        return cleaned_dataset

    def model_topics(self, package_name, dataset):

        if dataset is None:
            print("No dataset loaded")
            return
        self.n_samples = len(dataset)

        if len(dataset) <= 2:
            sys.stderr.write("Data too less for {}, aborting".format(package_name))
            return
        # Use tf-idf features for NMF.
        print("Extracting tf-idf features for NMF...")
        tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                        max_features=self.n_features,
                                        stop_words='english')
        t0 = time()
        tfidf = tfidf_vectorizer.fit_transform(dataset)
        print("done in %0.3fs." % (time() - t0))

        # Use tf (raw term count) features for LDA.
        print("Extracting tf features for LDA...")
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                        max_features=self.n_features,
                                        stop_words='english')
        t0 = time()
        tf = tf_vectorizer.fit_transform(dataset)
        print("done in %0.3fs." % (time() - t0))

        # Fit the NMF model
        print("Fitting the NMF model with tf-idf features, "
            "n_samples=%d and n_features=%d..."
            % (self.n_samples, self.n_features))
        t0 = time()
        nmf = NMF(n_components=self.n_topics, random_state=1,
                alpha=.1, l1_ratio=.5).fit(tfidf)
        print("done in %0.3fs." % (time() - t0))

        # print("\nTopics in NMF model:")
        tfidf_feature_names = tfidf_vectorizer.get_feature_names()
        self.save_top_words(nmf, tfidf_feature_names, self.n_top_words, package_name, 'nmf')

        print("Fitting LDA models with tf features, "
            "n_samples=%d and n_features=%d..."
            % (self.n_samples, self.n_features))
        lda = LatentDirichletAllocation(n_components=self.n_topics, max_iter=5,
                                        learning_method='online',
                                        learning_offset=50.,
                                        random_state=0)
        t0 = time()
        lda.fit(tf)
        print("done in %0.3fs." % (time() - t0))

        # print("\nTopics in LDA model:")
        tf_feature_names = tf_vectorizer.get_feature_names()
        self.save_top_words(lda, tf_feature_names, self.n_top_words, package_name, 'lda')


def main():
    topic_extraction = TopicExtraction()
    for dirpath, dirs, files in os.walk(DATA_DIR):
        for filename in files:
            print("Processing: " + filename)
            dataset = topic_extraction.load_dataset(filename)
            if len(dataset) <= 2:
                dataset_modified = []
                for dat in dataset:
                    dataset_modified += sent_tokenize(dat)
                dataset = dataset_modified
            topic_extraction.model_topics(filename[:filename.rfind('.json')], dataset)
            topic_extraction.save_to_file()


if __name__ == '__main__':
    main()
    