"""Challenge the experiment's evidence, not just summary formatting."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('matrix', Path(__file__).with_name('synthetic_matrix.py'))
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)


def test_optimistic_banner_cannot_prove_persistence():
    weak = matrix.trial('persistence_loss', 'banner_only')
    exact = matrix.trial('persistence_loss', 'fixed_exact')
    assert weak['after'] == exact['after'] == []
    assert weak['false_green']
    assert exact['verdict'] == 'failed'


def test_replay_identity_check_precedes_mutation():
    result = matrix.trial('wrong_account', 'verified_replay')
    assert result['actions'] == 0
    assert result['after'] == []
    assert result['invalidation'] == 'identity_mismatch'


def test_duplicate_and_weakened_oracle_have_distinct_store_evidence():
    duplicate = matrix.trial('duplicate_effect', 'fixed_exact')
    weakened = matrix.trial('weakened_assertion', 'fixed_exact')
    assert len(duplicate['after']) == 2
    assert weakened['after'] == [('A', 'op-1', 2)]
    assert duplicate['verdict'] == weakened['verdict'] == 'failed'


def test_missing_required_report_blocks_even_with_correct_store():
    result = matrix.trial('required_skip', 'fixed_exact')
    assert result['exact_oracle']
    assert not result['coverage_oracle']
    assert result['verdict'] == 'failed'


def test_stale_replay_has_no_effect_and_clean_passes_every_path():
    stale = matrix.trial('stale_replay', 'verified_replay')
    assert stale['verdict'] == 'blocked'
    assert stale['after'] == []
    assert all(matrix.trial('clean', mode)['verdict'] == 'passed' for mode in matrix.MODES)
