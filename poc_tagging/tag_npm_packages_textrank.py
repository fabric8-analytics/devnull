#!/usr/bin/env python
import mistune
from bs4 import BeautifulSoup
import json
import textrank
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

stop_words = set(stopwords.words("english"))


def remove_stopwords(sentence):
    return " ".join([word.lower() for word in word_tokenize(sentence)
                    if word.lower() not in stop_words and word.isalpha()])


def clean_stopwords(txt):
    sentences = sent_tokenize(txt)
    sentences = [remove_stopwords(sentence) for sentence in sentences]
    return " ".join(sentences)


npm_data = open('npm_data.json')
npm_data_dict = json.loads(npm_data.read())

for package_name in npm_data_dict.keys():
    readme = npm_data_dict[package_name]['readme']
    readme_rendered = mistune.markdown(readme, escape=False)
    soup = BeautifulSoup(readme_rendered, "html.parser")
    # Replace anchors with content where relevant and extract otherwise
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
    npm_data_dict[package_name]['readme_cleaned'] = clean_stopwords(soup.text)
npm_data.close()

tags = {}
for package_name in npm_data_dict.keys():
    print("Processing: " + package_name)
    tags[package_name] = list(textrank.extract_key_phrases(
        npm_data_dict[package_name]["readme_cleaned"]))
    print("tagged: " + package_name)

with open('package_tag_map.json', 'w') as package_tag_map:
    package_tag_map.write(json.dumps(tags))
