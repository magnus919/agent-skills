#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "minitest/autorun"
require "open3"
require "rbconfig"
require "tmpdir"

class GenLlmsTxtTest < Minitest::Test
  GENERATOR = File.expand_path("gen-llms-txt.rb", __dir__)

  def test_generation_and_drift_detection
    Dir.mktmpdir("gen-llms-txt") do |root|
      install_generator(root)

      write_skill(root, "omega", <<~YAML)
        ---
        name: omega
        description: |-
          First line
          second line
        ---
      YAML
      write_skill(root, "bundles/zulu", <<~YAML)
        ---
        name: zulu
        description: Zulu bundle.
        ---
      YAML
      write_skill(root, "bundles/zulu/skills/helper", <<~YAML)
        ---
        name: helper
        description: Nested helper that must be excluded.
        ---
      YAML

      stdout, stderr, status = run_generator(root)
      refute status.success?
      assert_empty stdout
      assert_includes stderr, "llms.txt is missing"
      assert_includes stderr, "ruby scripts/gen-llms-txt.rb --write"

      stdout, stderr, status = run_generator(root, "--write")
      assert status.success?, stderr
      assert_includes stdout, "Wrote llms.txt (2 skills)."
      assert_empty stderr

      expected = <<~TEXT
        # agent-skills

        ## Skills

        - [omega](omega/SKILL.md): First line second line
        - [zulu](bundles/zulu/SKILL.md): Zulu bundle.
      TEXT
      llms_path = File.join(root, "llms.txt")
      assert_equal expected, File.binread(llms_path)
      refute_includes File.binread(llms_path), "helper"

      stdout, stderr, status = run_generator(root)
      assert status.success?, stderr
      assert_includes stdout, "llms.txt is current (2 skills)."
      assert_empty stderr

      File.open(llms_path, "a") { |file| file.write("drift\n") }
      stdout, stderr, status = run_generator(root)
      refute status.success?
      assert_empty stdout
      assert_includes stderr, "llms.txt is out of date"
      assert_includes stderr, "ruby scripts/gen-llms-txt.rb --write"

      _stdout, stderr, status = run_generator(root, "--write")
      assert status.success?, stderr
      assert_equal expected, File.binread(llms_path)
    end
  end

  def test_rejects_missing_description
    Dir.mktmpdir("gen-llms-txt") do |root|
      install_generator(root)
      write_skill(root, "invalid", <<~YAML)
        ---
        name: invalid
        ---
      YAML

      _stdout, stderr, status = run_generator(root, "--write")
      refute status.success?
      assert_includes stderr, "invalid/SKILL.md: description must be a nonempty string"
    end
  end

  def test_rejects_missing_name
    Dir.mktmpdir("gen-llms-txt") do |root|
      install_generator(root)
      write_skill(root, "invalid", <<~YAML)
        ---
        description: Missing name fixture.
        ---
      YAML

      _stdout, stderr, status = run_generator(root, "--write")
      refute status.success?
      assert_includes stderr, "invalid/SKILL.md: name must match directory name \"invalid\""
    end
  end

  def test_rejects_mismatched_name
    Dir.mktmpdir("gen-llms-txt") do |root|
      install_generator(root)
      write_skill(root, "expected-name", <<~YAML)
        ---
        name: wrong-name
        description: Mismatched name fixture.
        ---
      YAML

      _stdout, stderr, status = run_generator(root, "--write")
      refute status.success?
      assert_includes stderr, "expected-name/SKILL.md: name must match directory name \"expected-name\""
    end
  end

  def test_rejects_duplicate_catalog_names
    Dir.mktmpdir("gen-llms-txt") do |root|
      install_generator(root)
      skill = <<~YAML
        ---
        name: duplicate
        description: Duplicate fixture.
        ---
      YAML
      write_skill(root, "duplicate", skill)
      write_skill(root, "bundles/duplicate", skill)

      _stdout, stderr, status = run_generator(root, "--write")
      refute status.success?
      assert_includes stderr, "duplicate catalog name \"duplicate\""
      assert_includes stderr, "duplicate/SKILL.md"
      assert_includes stderr, "bundles/duplicate/SKILL.md"
    end
  end

  private

  def install_generator(root)
    FileUtils.mkdir_p(File.join(root, "scripts"))
    FileUtils.cp(GENERATOR, File.join(root, "scripts", "gen-llms-txt.rb"))
  end

  def run_generator(root, *args)
    Open3.capture3(
      RbConfig.ruby,
      "scripts/gen-llms-txt.rb",
      *args,
      chdir: root
    )
  end

  def write_skill(root, relative_dir, content)
    directory = File.join(root, relative_dir)
    FileUtils.mkdir_p(directory)
    File.write(File.join(directory, "SKILL.md"), content)
  end
end
