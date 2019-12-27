import sys
import pickle
from collections import Counter
from lextract.keyed_db.extract import extract_toks_indexed, get_connection
from finntk.omor.anlys import ud_to_omor, IGNORE_ALL, IGNORE_VERB, IGNORE_NOUN
import conllu
from wikiparse.utils.db import get_session
from consts import (LEM, CMP, SCH, MWE)
import click


def ud_feats_to_omor_lextract(lemma, pos, feats):
    res = ud_to_omor(lemma, pos, feats)
    filtered = {}
    for k, v in res.items():
        k_lower = k.lower()
        pair = (k_lower, v)
        if pair in IGNORE_ALL or (pos == "NOUN" and pair in IGNORE_NOUN) or (pos == "VERB" and pair in IGNORE_VERB):
            continue
        filtered[k_lower] = v
    return filtered


@click.command()
@click.option("--do-lextract/--no-lextract", default=True)
@click.argument('inf', type=click.File('r'))
@click.argument("outf", type=click.File("wb"))
def main(do_lextract, inf, outf):
    session = get_session()
    conn = get_connection(session)
    cnt = Counter()

    for sent_idx, sent in enumerate(conllu.parse_incr(inf)):
        lemma_map = {}
        all_lemma_feats = []
        for tok_idx, tok in enumerate(sent):
            lemma = tok["lemma"].lower()
            pos = tok["upostag"]
            if pos not in ("PUNCT", "SYM", "NUM"):
                if "#" in lemma or "-" in lemma:
                    cnt[(lemma, CMP)] += 1
                else:
                    cnt[(lemma, LEM)] += 1
            omor_tok = ud_feats_to_omor_lextract(lemma, pos, tok["feats"])
            del omor_tok["word_id"]
            lemma_map.setdefault(lemma, []).append(tok_idx)
            all_lemma_feats.append({lemma: [omor_tok]})
        if do_lextract:
            extracted = extract_toks_indexed(conn, lemma_map, all_lemma_feats)
            for matching, payload in extracted:
                form = payload["form"].lower()
                if payload["type"] == "multiword":
                    cnt[(form, MWE)] += 1
                elif payload["type"] == "frame":
                    cnt[(form, SCH)] += 1
                else:
                    assert False
        if (sent_idx % 1000) == 999:
            print("@ sent {}".format(sent_idx + 1))

    pickle.dump(cnt, outf)


if __name__ == "__main__":
    main()
