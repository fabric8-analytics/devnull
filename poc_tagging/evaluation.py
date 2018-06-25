import json
from pythonrouge.pythonrouge import Pythonrouge
from nltk.tokenize import sent_tokenize
import os
import sys

ROUGE_path = os.environ.get("ROUGE_PATH", None)  # ROUGE-1.5.5.pl
data_path = os.environ.get("ROUGE_DATA_PATH", None)  # data folder in RELEASE-1.5.5

if not ROUGE_path or not data_path:
    print("No ROUGE path or rouge data path specified in env.")
    sys.exit(1)

# initialize setting of ROUGE, eval ROUGE-1, 2, SU4, L
rouge = Pythonrouge(n_gram=2, ROUGE_SU4=True, ROUGE_L=True, stemming=True, stopwords=True,
                    word_level=True, length_limit=True, length=50, use_cf=False, cf=95,
                    scoring_formula="average", resampling=True, samples=1000, favor=True, p=0.5)


def evaluate_rouge(summary, reference):
    # If you evaluate ROUGE by sentence list as above, set files=False
    setting_file = rouge.setting(files=False, summary=summary, reference=reference)

    # If you need only recall of ROUGE metrics, set recall_only=True
    result = rouge.eval_rouge(setting_file, recall_only=True, ROUGE_path=ROUGE_path,
                              data_path=data_path)
    print(result)


with open('package_tag_map.json') as tag_json_file, open('npm_data.json') as npm_data_file:
    tag_json = json.loads(tag_json_file.read())
    npm_json = json.loads(npm_data_file.read())

reference_descriptions = []
tags = []

for package_name, package_tags in tag_json.items():
    reference_descriptions.append([sent_tokenize(npm_json[package_name]['description'])])
    tags.append(tag_json[package_name])

evaluate_rouge(tags, reference_descriptions)
