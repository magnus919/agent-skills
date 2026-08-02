#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "minitest/autorun"
require "tmpdir"

require_relative "validate-references"

# Regression tests for the references/*.md stale-reference scan (#205). The
# scan must catch a stale prose backtick reference to a nonexistent file inside
# a references/*.md file (the RICE typo class) without flagging generic
# doc-type names, examples, external-repository paths, or change-ledger
# removal records.
class ReferenceFileScanTest < Minitest::Test
  def test_clean_resolving_references_pass
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "See `references/details.md` in this skill.\n")
      write_file(root, "test-skill/references/details.md", "# Details\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_stale_backtick_reference_is_detected
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/product-strategy.md",
                      "See `#{stale_rice_token}` in the product-methodology skill for the full treatment.\n")
      write_skill_ref(root, "product-methodology/references/rice-framework.md", "# RICE\n")
      errors = ReferenceFileScan.stale_reference_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "test-skill/references/product-strategy.md:1"
      assert_includes errors.first, stale_rice_token
      assert_includes errors.first, "stale prose backtick reference"
    end
  end

  def test_stale_reference_to_nonexistent_sibling_file_is_detected
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "See `missing-guide.md` in the product-methodology skill.\n")
      write_skill_ref(root, "product-methodology/references/rice-framework.md", "# RICE\n")
      errors = ReferenceFileScan.stale_reference_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "missing-guide.md"
    end
  end

  def test_corrected_rice_reference_passes
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/product-strategy.md",
                      "See `rice-framework.md` in the product-methodology skill for the full treatment.\n")
      write_skill_ref(root, "product-methodology/references/rice-framework.md", "# RICE\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_sibling_skill_reference_resolves
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/routing.md",
                      "For evals guidance see the [langgraph](../../langgraph/SKILL.md) skill's `references/evals.md`.\n")
      write_file(root, "langgraph/SKILL.md", "---\nname: langgraph\n---\n")
      write_skill_ref(root, "langgraph/references/evals.md", "# Evals\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_repo_root_and_path_prefixed_references_resolve
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "Read `AGENTS.md` and `CONTRIBUTING.md`; see `.github/PULL_REQUEST_TEMPLATE.md`.\n")
      write_file(root, "AGENTS.md", "# Agents\n")
      write_file(root, "CONTRIBUTING.md", "# Contributing\n")
      write_file(root, ".github/PULL_REQUEST_TEMPLATE.md", "# Template\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_generic_doc_type_names_are_not_file_references
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "Write `SPEC.md`, `TASK-PLAN.md`, `VERIFICATION-PLAN.md`, and `index.md`.\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_runtime_and_external_paths_are_not_file_references
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "Store results in `02-analysis/epoch-trajectory.md` under /tmp (see `docker/versions.md` upstream).\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_removal_ledger_lines_are_ignored
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/source-index.md",
                      "| `references/old-guide.md` | Removed | Not portable |\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_case_mismatched_reference_is_detected
    # Case-sensitivity must match CI's Linux runners even on a
    # case-insensitive host filesystem (default macOS APFS).
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/guide.md",
                      "See `OVERVIEW.md` in this skill.\n")
      write_file(root, "test-skill/references/overview.md", "# Overview\n")
      errors = ReferenceFileScan.stale_reference_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "OVERVIEW.md"
    end
  end

  def test_exact_case_reference_passes
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/guide.md",
                      "See `OVERVIEW.md` in this skill.\n")
      write_file(root, "test-skill/references/OVERVIEW.md", "# Overview\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_packet_field_names_are_not_file_references
    with_fixture do |root|
      write_skill_ref(root, "test-skill/references/overview.md",
                      "Fields: `SPEC.md`, `TASK-PLAN.md`, `VERIFICATION-PLAN.md`, `VERIFICATION.md`, `EVIDENCE-LEDGER.md`, `CHANGE-CONTRACT.md`, `ARCHITECTURE-DELTA.md`.\n")
      assert_empty ReferenceFileScan.stale_reference_errors(root, "test-skill")
    end
  end

  def test_all_repo_references_scan_clean
    # Guard against the scan drifting from the repository's own conventions:
    # the check must pass on the real tree (the stale RICE reference is gone).
    assert_empty ReferenceFileScan.stale_reference_errors(File.expand_path("..", __dir__), "product-strategy")
  end

  private

  # The stale token is assembled at runtime so the misspelling never appears
  # contiguously in a tracked file (the repo-wide typo check must stay clean).
  def stale_rice_token
    "r" + "rice-framework.md"
  end

  def with_fixture
    Dir.mktmpdir do |directory|
      yield directory
    end
  end

  def write_skill_ref(root, relative, content)
    path = File.join(root, relative)
    FileUtils.mkdir_p(File.dirname(path))
    File.write(path, content)
  end

  def write_file(root, relative, content)
    path = File.join(root, relative)
    FileUtils.mkdir_p(File.dirname(path))
    File.write(path, content)
  end
end
