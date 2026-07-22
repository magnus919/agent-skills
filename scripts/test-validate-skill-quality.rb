#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "minitest/autorun"
require "open3"
require "stringio"
require "tmpdir"

require_relative "validate-skill-quality"

class ValidateSkillQualityTest < Minitest::Test
  def test_valid_imperative_description_and_boundary_pass
    with_skill(
      "Use this skill to review Ruby code. Not for application deployment.",
      "# Ruby review\n"
    ) do |path|
      assert_empty SkillQualityValidator.new.validate(path)
    end
  end

  def test_passive_description_fails
    with_skill(
      "This skill reviews Ruby code. Not for application deployment.",
      "# Ruby review\n"
    ) do |path|
      errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
      assert_equal 1, errors.length
      assert_includes errors.first.message, "imperative verb"
    end
  end

  def test_missing_negative_boundary_fails
    with_skill("Review Ruby code for correctness.", "# Ruby review\n") do |path|
      errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
      assert_equal 1, errors.length
      assert_includes errors.first.message, "negative boundary"
    end
  end

  def test_when_not_to_use_heading_satisfies_boundary
    with_skill(
      "Review Ruby code for correctness.",
      "# Ruby review\n\n## When not to use\n\nUse a deployment skill for releases.\n"
    ) do |path|
      assert_empty SkillQualityValidator.new.validate(path)
    end
  end

  def test_empty_when_not_to_use_heading_does_not_satisfy_boundary
    with_skill("Review Ruby code for correctness.", "# Ruby review\n\n## When not to use\n") do |path|
      errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
      assert_equal 1, errors.length
      assert_includes errors.first.message, "negative boundary"
    end
  end

  def test_non_substantive_when_not_to_use_sections_do_not_satisfy_boundary
    bodies = [
      "## When not to use\n\n---\n",
      "## When not to use\n\nTODO\n",
      "## When not to use\n\n**TODO:** Document this later.\n",
      "## When not to use\n\n- TODO: Document this later.\n",
      "## When not to use\n\n<!--\nTODO: explain this later\n-->\n",
      "## When not to use\n\n- <!--\nTODO: explain this later\n-->\n",
      "## When not to use\n\n> <!-- boundary goes here -->\n",
      "## When not to use\n\n```text\nUse another skill instead.\n```\n",
      "## When not to use\n\n> ```text\n> Use another skill instead.\n> ```\n",
      "## When not to use\n\n`TODO: Document this later.`\n",
      "## When not to use\n\nDetails will be added later.\n",
      "## When not to use\n\nThis section explains deployment behavior.\n"
    ]

    bodies.each do |body|
      with_skill("Review Ruby code for correctness.", body) do |path|
        errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
        assert_equal 1, errors.length, body
        assert_includes errors.first.message, "negative boundary"
      end
    end
  end

  def test_incidental_unlike_does_not_satisfy_boundary
    with_skill("Review Ruby behavior unlike prior benchmarks.", "# Ruby review\n") do |path|
      errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
      assert_equal 1, errors.length
      assert_includes errors.first.message, "negative boundary"
    end
  end

  def test_boundary_phrase_without_content_does_not_satisfy_boundary
    with_skill("Review Ruby code. Not for.", "# Ruby review\n") do |path|
      errors = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :error }
      assert_equal 1, errors.length
      assert_includes errors.first.message, "negative boundary"
    end
  end

  def test_common_imperative_outside_issue_examples_is_recognized
    with_skill("Automate repository maintenance. Not for deployments.", "# Automation\n") do |path|
      assert_empty SkillQualityValidator.new.validate(path)
    end
  end

  def test_no_op_phrases_warn_with_lines_without_blocking
    body = <<~MARKDOWN
      # Ruby review
      Write clear code.
      Write clean code.
      Follow
      best practices.
      Handle errors appropriately and handle errors gracefully.
      Ensure high quality.
      Make it easy to read.
      Write maintainable code.

      ## When not to use
      Use a deployment skill for releases.
    MARKDOWN

    with_skill("Review Ruby code for correctness.", body) do |path|
      findings = SkillQualityValidator.new.validate(path)
      assert_empty findings.select { |finding| finding.severity == :error }
      warnings = findings.select { |finding| finding.severity == :warning }
      assert_equal 8, warnings.length
      assert_equal [6, 7, 8, 10, 10, 11, 12, 13], warnings.map(&:line).sort
      assert warnings.all? { |warning| warning.message.include?("possible no-op instruction") }
    end
  end

  def test_inline_markdown_does_not_hide_no_op_phrases
    body = <<~MARKDOWN
      # Ruby review
      Follow **best practices**.
      Write *maintainable* code.
      Follow __best practices__.
      Write _maintainable_ code.
      `Follow best practices.`
      Call `follow_best_practices()`.
      Call `follow__best__practices()`.
      Follow ***best practices***.
      Follow **_best practices_**.
      Follow _**best practices**_.
      Follow **best** *practices*.
      Follow *best* **practices**.
      Write **maintainable** **code**.

      ## When not to use
      Use a deployment skill for releases.
    MARKDOWN

    with_skill("Review Ruby code for correctness.", body) do |path|
      warnings = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :warning }
      assert_equal 11, warnings.length
      assert_equal [6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18], warnings.map(&:line).sort
    end
  end

  def test_whole_phrase_emphasis_is_detected_for_every_no_op_family
    phrases = [
      "Write clear code",
      "Follow best practices",
      "Handle errors gracefully",
      "Ensure high quality",
      "Make it easy to read",
      "Write maintainable code"
    ]

    phrases.each do |phrase|
      ["**_#{phrase}_**.", "__#{phrase}__."].each do |formatted|
        body = "#{formatted}\n\n## When not to use\nUse a deployment skill for releases.\n"
        with_skill("Review Ruby code for correctness.", body) do |path|
          warnings = SkillQualityValidator.new.validate(path).select { |finding| finding.severity == :warning }
          assert_equal 1, warnings.length, formatted
          assert_equal 5, warnings.first.line, formatted
        end
      end
    end
  end

  def test_malformed_frontmatter_is_reported_without_crashing
    Dir.mktmpdir do |directory|
      path = File.join(directory, "SKILL.md")
      File.write(path, "---\nname: [\ndescription: nope\n---\n# Broken\n")
      findings = SkillQualityValidator.new.validate(path)
      assert_equal 1, findings.length
      assert_equal :error, findings.first.severity
      assert_includes findings.first.message, "invalid YAML"
    end
  end

  def test_selector_finds_added_modified_renamed_and_untracked_skills
    with_repo do |root|
      write_skill(root, "unchanged/SKILL.md", "This legacy description is intentionally invalid.")
      write_skill(root, "modified/SKILL.md", valid_description("modified"))
      write_skill(root, "old-name/SKILL.md", valid_description("old name"))
      commit_all(root, "baseline")
      base = git(root, "rev-parse", "HEAD").strip

      write_skill(root, "added/SKILL.md", valid_description("added"))
      commit_all(root, "add skill")
      write_skill(root, "modified/SKILL.md", valid_description("modified again"))
      git(root, "mv", "old-name/SKILL.md", "old-name/RENAMED.md")
      FileUtils.mkdir_p(File.join(root, "renamed"))
      git(root, "mv", "old-name/RENAMED.md", "renamed/SKILL.md")
      write_skill(root, "untracked/SKILL.md", valid_description("untracked"))
      write_skill(root, "SKILL.md", valid_description("root-level"))
      write_skill(root, "agent-council/profiles/skills/vendored/SKILL.md", valid_description("vendored"))
      write_skill(root, "not-agent-council/profiles/skills/changed/SKILL.md", valid_description("similarly named"))

      assert_equal(
        %w[SKILL.md added/SKILL.md modified/SKILL.md not-agent-council/profiles/skills/changed/SKILL.md renamed/SKILL.md untracked/SKILL.md],
        ChangedSkillSelector.new(root: root, base: base).paths
      )
    end
  end

  def test_runner_ignores_unchanged_legacy_skill
    with_repo do |root|
      write_skill(root, "legacy/SKILL.md", "This legacy description lacks both rules.")
      commit_all(root, "baseline")
      base = git(root, "rev-parse", "HEAD").strip
      write_skill(root, "new/SKILL.md", valid_description("new"))

      stdout = StringIO.new
      stderr = StringIO.new
      status = SkillQualityCheck.new(root: root, base: base, output: stdout, error: stderr).run

      assert_equal 0, status
      refute_includes stdout.string, "legacy/SKILL.md"
      refute_includes stderr.string, "legacy/SKILL.md"
      assert_includes stdout.string, "Quality-checked 1 changed skill(s): 0 error(s), 0 warning(s)."
    end
  end

  def test_runner_exits_successfully_for_warning_only_findings
    with_repo do |root|
      File.write(File.join(root, "placeholder"), "baseline\n")
      commit_all(root, "baseline")
      base = git(root, "rev-parse", "HEAD").strip
      write_skill(
        root,
        "warning/SKILL.md",
        valid_description("warning"),
        "# Warning\n\nFollow best practices.\n\n## When not to use\n\nUse another skill.\n"
      )

      stdout = StringIO.new
      stderr = StringIO.new
      status = SkillQualityCheck.new(root: root, base: base, output: stdout, error: stderr).run

      assert_equal 0, status
      assert_includes stdout.string, "WARNING warning/SKILL.md:"
      assert_includes stdout.string, "0 error(s), 1 warning(s)"
      assert_empty stderr.string
    end
  end

  def test_runner_exits_nonzero_for_blocking_findings
    with_repo do |root|
      File.write(File.join(root, "placeholder"), "baseline\n")
      commit_all(root, "baseline")
      base = git(root, "rev-parse", "HEAD").strip
      write_skill(root, "invalid/SKILL.md", "This skill has no negative boundary.", "# Invalid\n")

      stdout = StringIO.new
      stderr = StringIO.new
      status = SkillQualityCheck.new(root: root, base: base, output: stdout, error: stderr).run

      assert_equal 1, status
      assert_includes stderr.string, "imperative verb"
      assert_includes stderr.string, "negative boundary"
      assert_includes stderr.string, "2 error(s), 0 warning(s)"
    end
  end

  def test_all_zero_base_validates_all_tracked_skills
    with_repo do |root|
      write_skill(root, "tracked/SKILL.md", valid_description("tracked"))
      commit_all(root, "initial")

      assert_equal(
        ["tracked/SKILL.md"],
        ChangedSkillSelector.new(root: root, base: "0" * 40).paths
      )
    end
  end

  def test_explicit_base_compares_endpoint_snapshots_after_history_rewrite
    with_repo do |root|
      write_skill(root, "rewritten/SKILL.md", "This legacy description is invalid.", "# Legacy\n")
      commit_all(root, "common ancestor")
      common = git(root, "rev-parse", "HEAD").strip

      write_skill(root, "rewritten/SKILL.md", valid_description("before rewrite"))
      commit_all(root, "before force push")
      before = git(root, "rev-parse", "HEAD").strip
      git(root, "reset", "--hard", common)

      assert_equal(
        ["rewritten/SKILL.md"],
        ChangedSkillSelector.new(root: root, base: before).paths
      )
    end
  end

  private

  def valid_description(subject)
    "Review #{subject} behavior. Not for deployment work."
  end

  def with_skill(description, body)
    Dir.mktmpdir do |directory|
      path = File.join(directory, "SKILL.md")
      File.write(path, skill_text(description, body))
      yield path
    end
  end

  def with_repo
    Dir.mktmpdir do |directory|
      git(directory, "init", "-b", "main")
      git(directory, "config", "user.name", "Test User")
      git(directory, "config", "user.email", "test@example.invalid")
      yield directory
    end
  end

  def write_skill(root, relative, description, body = "# Test\n\n## When not to use\n\nUse another skill.\n")
    path = File.join(root, relative)
    FileUtils.mkdir_p(File.dirname(path))
    File.write(path, skill_text(description, body))
  end

  def skill_text(description, body)
    <<~SKILL
      ---
      name: test-skill
      description: #{description.inspect}
      ---
      #{body}
    SKILL
  end

  def commit_all(root, message)
    git(root, "add", "-A")
    git(root, "commit", "-m", message)
  end

  def git(root, *arguments)
    stdout, stderr, status = Open3.capture3("git", *arguments, chdir: root)
    assert status.success?, "git #{arguments.join(' ')} failed: #{stderr}"
    stdout
  end
end
