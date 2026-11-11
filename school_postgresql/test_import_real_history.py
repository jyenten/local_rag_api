"""Offline validation regression tests (no DB or PDFs required)."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from import_real_history import git_blob_sha, load_questions, validate_run


class TestImport(unittest.TestCase):
    def test_git_blob_is_genuine_git_object_id(self):
        self.assertEqual(
            git_blob_sha(b"hello"),
            hashlib.sha1(b"blob 5\0hello").hexdigest(),
        )

    def test_validation_accepts_consistent_real_shape(self):
        ids={"a","b"}
        raw={
            "dataset":"dev","dataset_hash":"abc","question_count":2,
            "timestamp":"2026-10-20T08:00:00+01:00",
            "questions":[
                {"id":"a","first_evidence_rank":1,"reciprocal_rank":1.0},
                {"id":"b","first_evidence_rank":None,"reciprocal_rank":0.0}],
            "metrics":{"mrr":0.5,"hit_at_1":0.5,"hit_at_3":0.5,
                       "hit_at_5":0.5,"hit_at_8":0.5}}
        result,_=validate_run(raw,"dev","abc",ids)
        self.assertEqual(result,[("a",1),("b",None)])
        raw["metrics"]["mrr"]=0.8
        with self.assertRaises(ValueError):
            validate_run(raw,"dev","abc",ids)
        raw["metrics"]["mrr"]=0.5
        raw["metrics"]["hit_at_8"]=0.75
        with self.assertRaises(ValueError):
            validate_run(raw,"dev","abc",ids)

    def test_source_hash_check(self):
        with TemporaryDirectory() as t:
            path=Path(t)/"eval.json"
            path.write_text(json.dumps([{"id":"a"},{"id":"b"}]),encoding="utf-8")
            ids,sha,sha256=load_questions(path)
            self.assertEqual(ids,{"a","b"})
            self.assertEqual(len(sha),40)
            self.assertEqual(len(sha256),64)


if __name__=="__main__":
    unittest.main()
