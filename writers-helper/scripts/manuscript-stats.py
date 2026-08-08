#!/usr/bin/env python3
"""Analyze a manuscript or other text file for editing signals.

Computes word and sentence stats, a passive-voice estimate, adverb density,
crutch-word counts, overused words, readability scores, and per-chapter
pacing. The output is diagnostic: use the numbers as questions, not
verdicts. Standard library only.

Examples:
    manuscript-stats.py mydraft.txt
    manuscript-stats.py mydraft.txt --json
    manuscript-stats.py mydraft.txt --crutch-words just,really,very,that
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Basic overuse probes every draft should be checked against.
DEFAULT_CRUTCH_WORDS = ["just", "really", "very", "so", "then", "suddenly", "felt", "looked"]

WORD_RE = re.compile(r"[A-Za-z']+")
SENTENCE_END_RE = re.compile(r"[.!?]+")
PASSIVE_RE = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being)\s+(\w+ed|(\w+en))\b", re.IGNORECASE
)
LONG_SENTENCE_WORDS = 30
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


def flesch_scores(avg_words_per_sentence, avg_syllables_per_word):
    """Flesch Reading Ease and Flesch-Kincaid Grade Level."""
    if avg_words_per_sentence <= 0 or avg_syllables_per_word <= 0:
        return None, None
    ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
    return round(ease, 1), round(grade, 1)


def syllable_count(word):
    """Approximate syllable count for a word (standard heuristic)."""
    word = word.lower()
    if len(word) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    previous_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_vowel:
            count += 1
        previous_vowel = is_vowel
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    return max(1, count)


def split_chapters(text, chapter_regex):
    """Split text into chapters by a header regex, keeping the header."""
    if not chapter_regex:
        return [("full text", text)]
    matches = list(re.finditer(chapter_regex, text, re.MULTILINE))
    if len(matches) < 2:
        return [("full text", text)]
    chapters = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chapters.append((match.group(0).strip(), text[start:end]))
    return chapters


def analyze_text(text, crutch_words):
    words = WORD_RE.findall(text)
    total_words = len(words)
    counts = Counter(word.lower() for word in words)
    unique_words = len(counts)
    if total_words == 0:
        return None

    sentences = [s for s in SENTENCE_END_RE.split(text) if s.strip()]
    sentence_word_counts = [len(WORD_RE.findall(s)) for s in sentences]
    sentence_count = len(sentence_word_counts)
    avg_sentence_words = sum(sentence_word_counts) / sentence_count if sentence_count else 0

    syllables = sum(syllable_count(word) for word in words)
    avg_syllables = syllables / total_words

    ease, grade = flesch_scores(avg_sentence_words, avg_syllables)

    passives = len(PASSIVE_RE.findall(text))
    adverbs = len(re.findall(r"\b\w+ly\b", text, re.IGNORECASE))

    crutch = {word: counts.get(word, 0) for word in crutch_words if counts.get(word, 0) > 0}
    # Most overused content words, excluding the crutch probes and stopwords.
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "with",
        "as",
        "by",
        "is",
        "was",
        "were",
        "be",
        "been",
        "being",
        "he",
        "she",
        "it",
        "they",
        "them",
        "his",
        "her",
        "its",
        "their",
        "i",
        "you",
        "we",
        "that",
        "this",
        "these",
        "those",
        "not",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "can",
        "could",
        "from",
    }
    overused = [
        {"word": word, "count": count}
        for word, count in counts.most_common(20)
        if word not in stop and count >= 10 and len(word) > 2
    ]

    paragraphs = [p for p in PARAGRAPH_SPLIT_RE.split(text) if p.strip()]
    long_sentences = sum(1 for count in sentence_word_counts if count >= LONG_SENTENCE_WORDS)

    return {
        "words": total_words,
        "unique_words": unique_words,
        "sentences": sentence_count,
        "avg_words_per_sentence": round(avg_sentence_words, 1),
        "long_sentences_over_30": long_sentences,
        "paragraphs": len(paragraphs),
        "passive_voice_estimates": passives,
        "ly_adverbs": adverbs,
        "adverb_ratio_per_1000_words": round(adverbs * 1000 / total_words, 1) if total_words else 0,
        "passive_ratio_per_1000_words": round(passives * 1000 / total_words, 1)
        if total_words
        else 0,
        "crutch_words": crutch,
        "overused_words": overused,
        "flesch_reading_ease": ease,
        "flesch_kincaid_grade": grade,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze a manuscript for editing signals.")
    parser.add_argument("file", help="Path to the text file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument(
        "--chapter-regex", default=r"^#+\s+Chapter\s+\d+", help="Regex for chapter headers."
    )
    parser.add_argument(
        "--crutch-words",
        default=",".join(DEFAULT_CRUTCH_WORDS),
        help="Comma-separated crutch words.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print what would be analyzed (no-op).",
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error: no such file: {args.file}", file=sys.stderr)
        return 1
    crutch_words = [word.strip().lower() for word in args.crutch_words.split(",") if word.strip()]
    if args.dry_run:
        print(
            f"would analyze {path} ({path.stat().st_size} bytes), "
            f"{len(crutch_words)} crutch probes: {', '.join(crutch_words)}"
        )
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        print(f"error: cannot read {args.file}: {error}", file=sys.stderr)
        return 1

    overall = analyze_text(text, crutch_words)
    if overall is None:
        print("error: no words found in the file", file=sys.stderr)
        return 1

    chapters = split_chapters(text, args.chapter_regex)
    chapter_stats = []
    for name, chunk in chapters:
        stats = analyze_text(chunk, crutch_words)
        if stats is not None:
            chapter_stats.append({"chapter": name, "words": stats["words"]})

    result = {"overall": overall, "chapters": chapter_stats}
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"Words: {overall['words']}  Unique: {overall['unique_words']}")
    print(
        f"Sentences: {overall['sentences']}  Avg length: {overall['avg_words_per_sentence']} words "
        f"(long >30: {overall['long_sentences_over_30']})"
    )
    print(f"Paragraphs: {overall['paragraphs']}")
    print(
        f"Passive-voice estimates: {overall['passive_voice_estimates']} "
        f"({overall['passive_ratio_per_1000_words']}/1000 words)"
    )
    print(
        f"-ly adverbs: {overall['ly_adverbs']} ({overall['adverb_ratio_per_1000_words']}/1000 words)"
    )
    if overall["crutch_words"]:
        print("Crutch words: " + ", ".join(f"{w}={c}" for w, c in overall["crutch_words"].items()))
    if overall["overused_words"]:
        print(
            "Overused words: "
            + ", ".join(f"{w['word']}={w['count']}" for w in overall["overused_words"][:8])
        )
    if overall["flesch_reading_ease"] is not None:
        print(
            f"Readability: Flesch {overall['flesch_reading_ease']} / "
            f"grade {overall['flesch_kincaid_grade']} (target ~7th-10th grade unless audience warrants more)"
        )
    print("Chapter pacing (words per chapter):")
    for item in chapter_stats:
        print(f"  {item['chapter']}: {item['words']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
