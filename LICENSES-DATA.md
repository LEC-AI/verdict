# Data, models and licences

This file records which third-party datasets and models the paper and its preliminary experiments use, under what
terms, and what this repository contains from each. Licence fields were read from the Hugging Face Hub and checked
against the source papers or dataset cards where the Hub field is empty. This is a record of what the release contains, not legal advice.

## What this repository contains

- **Code** (`verdict/`, `scripts/`): Apache-2.0, copyright LEC AI Limited.
- **Result files** (`results/`): aggregate metrics and per-decision predictions. Each prediction row holds a task
  name, an item id (a dataset index or a hash), the gold label, the predicted label and the predicted probabilities.
  No input text from any dataset is included.
- **Distilled email labels** (`data/labels/`): labels produced by LLM judges over the Enron email corpus, keyed to a
  hash of each message. No message bodies, names or addresses are included.
- **Not included**: trained model checkpoints, copies of any third-party dataset, and the synthetic typed-decision
  corpus used for the negative generalist result in the paper.

Datasets are loaded at run time from their original sources by the scripts in this repository, under their own terms.

## Benchmarks

| Dataset | Use | Licence | In this repository |
|---|---|---|---|
| LocalLLaMA/typed-decisions | main benchmark (training and evaluation) | Apache-2.0 | predictions and metrics only |
| ehovy/race (RACE) | standard benchmark | research use (CMU) | predictions and metrics only |
| google/boolq (BoolQ) | standard benchmark | CC-BY-SA-3.0 | predictions and metrics only |
| aps/super_glue (MultiRC) | standard benchmark | per SuperGLUE task terms | predictions and metrics only |
| clinc/clinc_oos (CLINC150) | intent classification | CC-BY-3.0 | predictions and metrics only |
| PolyAI/banking77, legacy-datasets/banking77 | intent classification | CC-BY-4.0 | predictions and metrics only |
| ought/raft (RAFT) | early external check, not in the paper | per-task terms (RAFT paper appendix) | metrics only |
| zefang-liu/phishing-email-dataset | supplementary check, not in the paper | LGPL-3.0 | hashed ids, gold labels, predictions |

## Other corpora

| Corpus | Use | Terms | In this repository |
|---|---|---|---|
| Enron email corpus (corbt/enron-emails) | source texts for the email tasks | public record released by FERC (2003); Klimt and Yang (2004) | LLM-judge labels keyed to message hashes |
| fancyzhx/ag_news | training data of the public-data generalist (paper appendix, negative result) | provided for research use, no explicit licence | none (loaded by pointer) |
| dair-ai/emotion | training data of the public-data generalist | educational and research use | none (loaded by pointer) |
| fancyzhx/dbpedia_14 | training data of the public-data generalist | CC-BY-SA-3.0 | none (loaded by pointer) |
| community-datasets/yahoo_answers_topics | training data of the public-data generalist | no explicit licence | none (loaded by pointer) |
| SetFit/TREC-QC | training data of the public-data generalist | no explicit licence | none (loaded by pointer) |
| cardiffnlp/tweet_eval (irony, hate) | training data of the public-data generalist | no explicit licence | none (loaded by pointer) |
| stanfordnlp/sst2 | early classification tasks, not in the paper | no explicit licence (GLUE) | none (loaded by pointer) |

The email labels were produced by Qwen3-VL-32B (primary) and DeepSeek V3.2 (independent check); agreement between the
two is reported in `results/RESULTS_labels.md`. The public-data generalist in the paper's negative result ("Verdict-MQ,
public data") was trained on up to 3,000 training examples per task from seven tasks: AG News, dair-ai/emotion,
DBpedia-14, Yahoo Answers topics, TREC question types, and tweet_eval irony and hate. A model trained on them inherits
their terms; no checkpoint of it is distributed. The paper's headline specialist models are fine-tuned on the
typed-decisions benchmark only.

## Models

| Model | Use | Licence |
|---|---|---|
| answerdotai/ModernBERT-base, ModernBERT-large | backbone | Apache-2.0 |
| tasksource/ModernBERT-base-nli, ModernBERT-large-nli | initialization | Apache-2.0 |
| convaiinnovations/laya | baseline; its encoder is one initialization in a controlled comparison | Apache-2.0 (not redistributed) |
| Jev | zero-shot reference, called through its public API | closed; outputs are used for evaluation only |

## Contamination rule

tasksource/ModernBERT-*-nli lists SuperGLUE BoolQ and MultiRC and GLUE SST-2 among its training tasks (training
splits). On BoolQ and MultiRC the primary Verdict-MQ and baseline runs therefore start from raw ModernBERT; the
tasksource-initialized runs are reported as a disclosed secondary row. RACE, CLINC150 and Banking77 are not in that
list.
