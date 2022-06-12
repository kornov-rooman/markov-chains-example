from __future__ import annotations

import json
import random
import re
import string
import typing as ty
import functools
from collections import Counter, defaultdict
from pathlib import Path


def make_pairs(texts: list[list[str]]) -> ty.Iterator[str, str]:
    for sentence in texts:
        for left_word, right_word in zip(sentence, sentence[1:]):
            yield left_word, right_word


def get_simplified_transition_matrix(texts: list[list[str]]) -> dict[str, Counter[str]]:
    # NOTE: not memory-optimized
    transition_matrix = defaultdict(Counter)
    pair_count = 0
    for left_word, right_word in make_pairs(texts):
        transition_matrix[left_word].update([right_word])
        pair_count += 1

    print(f"total pairs: {pair_count}")
    return transition_matrix


def text_msg_filter(from_id: str, message: dict[str, ty.Any]) -> bool:
    try:
        return message["from_id"] == from_id
    except KeyError:
        return False


def split_and_normalize(text_message: str) -> list[list[str]]:
    translator = str.maketrans('', '', string.punctuation)

    by_sentence_and_words = []
    for sentence in re.split(r"\(|\)|;|!|\?|\.", text_message):
        sentence = sentence.strip()
        if not sentence:
            continue

        by_words = sentence.lower().translate(translator).strip().split()
        by_sentence_and_words.append(by_words)

    return by_sentence_and_words


def build_simplified_transition_matrix(user_id: str) -> dict[str, Counter[str]]:
    all_messages = []
    file_processed = 0
    for filename in Path(".").glob("telegram_dumps/*.json"):
        with open(filename) as export:
            data = json.load(export)

            all_messages += data["messages"]
            file_processed += 1

    print(f"processed files: {file_processed}")
    print(f"total messages: {len(all_messages)}")

    split_by_sentence_and_words = []
    message_processed = 0
    for message in filter(functools.partial(text_msg_filter, user_id), all_messages):
        if isinstance(message["text"], list):
            # NOTE: there's non-relevant data in list
            continue
        split_by_sentence_and_words += split_and_normalize(message["text"])
        message_processed += 1

    print(f"processed messages: {message_processed}")

    return get_simplified_transition_matrix(split_by_sentence_and_words)


def build_random_sentence(
    transition_matrix: dict[str, Counter[str]],
    sentence_length: int = 5,
    by_most_common: ty.Optional[int] = None,
) -> str:
    sentence = [random.choice(list(transition_matrix.keys()))]
    for i in range(sentence_length):
        counted_values = transition_matrix[sentence[-1]]
        most_common = counted_values.most_common(n=by_most_common)
        if most_common:
            sentence.append(random.choice(list(map(lambda x: x[0], most_common))))

    return " ".join(sentence)


if __name__ == "__main__":
    matrix = build_simplified_transition_matrix("user71398848")
    print()
    for _ in range(10):
        print(build_random_sentence(matrix, sentence_length=10, by_most_common=None))
