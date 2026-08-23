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

  def test_oversized_reference_under_limit_passes
    with_fixture do |root|
      content = "a" * 59_999
      write_skill_ref(root, "test-skill/references/details.md", content)
      assert_empty ReferenceFileScan.oversized_reference_errors(root, "test-skill")
    end
  end

  def test_oversized_reference_over_limit_fails_with_path_and_size
    with_fixture do |root|
      content = "a" * 60_001
      write_skill_ref(root, "test-skill/references/details.md", content)
      errors = ReferenceFileScan.oversized_reference_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "test-skill/references/details.md"
      assert_includes errors.first, "60001"
    end
  end

  def test_oversized_reference_exactly_at_limit_passes
    with_fixture do |root|
      content = "a" * 60_000
      write_skill_ref(root, "test-skill/references/details.md", content)
      assert_equal 60_000, File.read(File.join(root, "test-skill/references/details.md")).length
      assert_empty ReferenceFileScan.oversized_reference_errors(root, "test-skill")
    end
  end

  def test_oversized_reference_error_mentions_split_remediation
    with_fixture do |root|
      content = "a" * 60_001
      write_skill_ref(root, "test-skill/references/details.md", content)
      errors = ReferenceFileScan.oversized_reference_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "split the file into focused files"
      assert_includes errors.first, "update SKILL.md's index"
    end
  end

  def test_oversized_reference_scan_ignores_non_markdown_files
    with_fixture do |root|
      content = "a" * 60_001
      write_skill_ref(root, "test-skill/references/notes.txt", content)
      assert_empty ReferenceFileScan.oversized_reference_errors(root, "test-skill")
    end
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

# Regression tests for the SKILL.md token-budget gate (#382). The gate strips
# YAML frontmatter, measures the body in characters (~4 chars/token proxy for
# the ~5,000-token budget), and must not fire on frontmatter size or at
# exactly the limit.
class OversizedSkillMdTest < Minitest::Test
  FRONTMATTER = "---\nname: test-skill\n---\n"

  def test_body_under_limit_passes
    with_fixture do |root|
      write_skill_md(root, FRONTMATTER + ("a" * 19_999))
      assert_empty ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
    end
  end

  def test_body_over_limit_fails_with_path_and_size
    with_fixture do |root|
      write_skill_md(root, FRONTMATTER + ("a" * 20_001))
      errors = ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "test-skill/SKILL.md"
      assert_includes errors.first, "20001"
    end
  end

  def test_body_exactly_at_limit_passes
    with_fixture do |root|
      write_skill_md(root, FRONTMATTER + ("a" * 20_000))
      errors = ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
      assert_equal 20_000, ReferenceFileScan::MAX_SKILL_MD_BODY_CHARS
      assert_empty errors
    end
  end

  def test_gate_does_not_count_frontmatter
    with_fixture do |root|
      # Huge frontmatter (well past the cap) with a tiny body must pass: only
      # the body after the closing --- counts toward the budget.
      frontmatter = "---\nname: test-skill\ndescription: #{'y' * 30_000}\n---\n"
      write_skill_md(root, frontmatter + ("x" * 100))
      text = File.read(File.join(root, "test-skill/SKILL.md"))
      match = text.match(/\A---\n.*?\n---\n/m)
      assert_operator match.end(0), :>, 25_000
      assert_empty ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
    end
  end

  def test_error_mentions_references_remediation
    with_fixture do |root|
      write_skill_md(root, FRONTMATTER + ("a" * 20_001))
      errors = ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
      assert_equal 1, errors.length
      assert_includes errors.first, "references/"
      assert_includes errors.first, "triggers + workflow skeleton"
    end
  end

  def test_missing_frontmatter_is_skipped_not_flagged_here
    # validate-skills.rb reports missing YAML frontmatter itself; the body
    # gate has nothing meaningful to measure and stays silent.
    with_fixture do |root|
      write_skill_md(root, "# No frontmatter\n" + ("a" * 30_000))
      assert_empty ReferenceFileScan.oversized_skill_md_errors(root, "test-skill")
    end
  end

  def test_missing_skill_md_is_ignored
    with_fixture do |root|
      FileUtils.mkdir_p(File.join(root, "empty-skill"))
      assert_empty ReferenceFileScan.oversized_skill_md_errors(root, "empty-skill")
    end
  end

  private

  def with_fixture(&block)
    Dir.mktmpdir do |directory|
      block.call(directory)
    end
  end

  def write_skill_md(root, content)
    path = File.join(root, "test-skill", "SKILL.md")
    FileUtils.mkdir_p(File.dirname(path))
    File.write(path, content)
  end
end
