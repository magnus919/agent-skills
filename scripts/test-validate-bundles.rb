#!/usr/bin/env ruby
# frozen_string_literal: true

# Tests for the bundle-manifest validation and lifecycle capability matrix
# tooling (issue #203):
#   - schema conformance of the committed example manifest
#   - validator positive cases (valid manifest, declared conflicts)
#   - validator negative cases (incomplete, contradictory, undeclared overlap)
#   - matrix generator check/--write modes and drift detection
#   - matrix validator completeness/traceability
#
# The five issue evaluation scenarios are deterministically reproducible here:
# complete product-lifecycle discovery (VAL-MNF-018), production-readiness
# path (VAL-MNF-019), nested-skill loading boundary (VAL-MNF-020), conflicting
# bundle (VAL-MNF-021), and incomplete manifest (VAL-MNF-013/022).
#
# Run: ruby scripts/test-validate-bundles.rb

require "fileutils"
require "json"
require "minitest/autorun"
require "open3"
require "rbconfig"
require "tmpdir"
require "yaml"

REPO_ROOT = File.expand_path("..", __dir__)
VALIDATOR = File.expand_path("validate-bundles.rb", __dir__)
GENERATOR = File.expand_path("gen-lifecycle-matrix.rb", __dir__)
MATRIX_VALIDATOR = File.expand_path("validate-lifecycle-matrix.rb", __dir__)
SCHEMA = File.expand_path("../schemas/bundle-manifest-v1.schema.json", __dir__)
EXAMPLE = File.expand_path("../docs/examples/bundle-manifest.example.yaml", __dir__)
REQUIRED_FIELDS = %w[
  schema_version bundle_name purpose audience stages included_skills
  prerequisites outputs handoffs conflicts eval_suite
].freeze

SKILL_STUB = <<~YAML
  ---
  name: %<name>s
  description: Fixture skill used by bundle manifest tests.
  ---
YAML

def valid_manifest_yaml
  <<~YAML
    schema_version: 1
    bundle_name: demo
    purpose: Demo bundle purpose.
    audience: Demo bundle audience.
    stages:
      - name: Stage one
        skills:
          - ../alpha/SKILL.md
    included_skills:
      - ../alpha/SKILL.md
    prerequisites:
      - artifact: Input artifact
        skill: ../alpha/SKILL.md
    outputs:
      - decision
    handoffs:
      - to: next team
        artifact: decision
        note: Hands the decision onward.
    conflicts: []
    eval_suite:
      - evals/evals.json
  YAML
end

def manifest_yaml(bundle_name:, skill_path:, conflicts: "conflicts: []")
  <<~YAML
    schema_version: 1
    bundle_name: #{bundle_name}
    purpose: #{bundle_name} bundle purpose.
    audience: #{bundle_name} bundle audience.
    stages:
      - name: Stage one
        skills:
          - #{skill_path}
    included_skills:
      - #{skill_path}
    prerequisites:
      - artifact: Input artifact
        skill: #{skill_path}
    outputs:
      - decision
    handoffs:
      - to: next team
        artifact: decision
        note: Hands the decision onward.
    #{conflicts}
    eval_suite:
      - evals/evals.json
  YAML
end

def write_bundle_pair(root, skill: "shared", alpha_conflicts: "conflicts: []", beta_conflicts: "conflicts: []")
  write_skill(root, skill)
  write_manifest(root, "alpha/manifest.yaml", manifest_yaml(bundle_name: "alpha", skill_path: "../#{skill}/SKILL.md", conflicts: alpha_conflicts))
  write_manifest(root, "beta/manifest.yaml", manifest_yaml(bundle_name: "beta", skill_path: "../#{skill}/SKILL.md", conflicts: beta_conflicts))
  write_skill(root, "alpha", name: "alpha")
  write_skill(root, "beta", name: "beta")
  write_manifest(root, "alpha/evals/evals.json", "{}\n")
  write_manifest(root, "beta/evals/evals.json", "{}\n")
end

def write_skill(root, relative, name: nil)
  directory = File.join(root, relative)
  FileUtils.mkdir_p(directory)
  File.write(File.join(directory, "SKILL.md"), format(SKILL_STUB, name: name || File.basename(directory)))
end

def write_manifest(root, relative, content)
  path = File.join(root, relative)
  FileUtils.mkdir_p(File.dirname(path))
  File.write(path, content)
end

def install_tooling(root)
  FileUtils.mkdir_p(File.join(root, "scripts"))
  FileUtils.cp(VALIDATOR, File.join(root, "scripts", "validate-bundles.rb"))
  FileUtils.cp(GENERATOR, File.join(root, "scripts", "gen-lifecycle-matrix.rb"))
  FileUtils.cp(MATRIX_VALIDATOR, File.join(root, "scripts", "validate-lifecycle-matrix.rb"))
  FileUtils.mkdir_p(File.join(root, "schemas"))
  FileUtils.cp(SCHEMA, File.join(root, "schemas", "bundle-manifest-v1.schema.json"))
  # Migration path referenced by deferred matrix cells.
  FileUtils.mkdir_p(File.join(root, "docs"))
  File.write(File.join(root, "docs", "bundle-manifest-design.md"), "# Bundle Manifest Design\n\n## Migration path\n")
end

def install_valid_bundle(root, bundle: "demo")
  write_skill(root, "alpha")
  write_manifest(root, "#{bundle}/manifest.yaml", valid_manifest_yaml)
  write_skill(root, bundle, name: bundle)
  write_manifest(root, "#{bundle}/evals/evals.json", "{}\n")
end

def run_validator(root, *args)
  Open3.capture3(RbConfig.ruby, "scripts/validate-bundles.rb", *args, chdir: root)
end

def run_generator(root, *args)
  Open3.capture3(RbConfig.ruby, "scripts/gen-lifecycle-matrix.rb", *args, chdir: root)
end

def run_matrix_validator(root, *args)
  Open3.capture3(RbConfig.ruby, "scripts/validate-lifecycle-matrix.rb", *args, chdir: root)
end

class ValidateBundlesTest < Minitest::Test
  # -- committed example is schema-conformant (VAL-MNF-003) --

  def test_committed_example_manifest_is_schema_conformant
    schema = JSON.parse(File.read(SCHEMA))
    manifest = YAML.safe_load(File.read(EXAMPLE), permitted_classes: [], aliases: false)
    assert_instance_of Hash, manifest
    assert_schema_valid(schema, manifest, schema["$defs"])
  end

  # -- validator positives --

  def test_valid_manifest_passes
    Dir.mktmpdir("bundle-valid") do |root|
      install_tooling(root)
      install_valid_bundle(root)

      stdout, stderr, status = run_validator(root)
      assert status.success?, stderr
      assert_includes stdout, "Validated 1 bundle manifest"
    end
  end

  def test_declared_conflict_accepted
    Dir.mktmpdir("bundle-conflict-declared") do |root|
      install_tooling(root)
      declared = <<~CONFLICT
        conflicts:
          - skill: ../shared/SKILL.md
            with: beta
            guidance: Both bundles include shared; route by context.
      CONFLICT
      write_bundle_pair(root, alpha_conflicts: declared)

      _stdout, stderr, status = run_validator(root)
      assert status.success?, stderr
    end
  end

  # -- validator negatives: incomplete manifests (VAL-MNF-013) --

  def test_missing_required_field_rejected_with_named_field
    REQUIRED_FIELDS.each do |field|
      Dir.mktmpdir("bundle-incomplete") do |root|
        install_tooling(root)
        install_valid_bundle(root)
        manifest_path = File.join(root, "demo", "manifest.yaml")
        data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
        data.delete(field)
        File.write(manifest_path, data.to_yaml)

        _stdout, stderr, status = run_validator(root)
        refute status.success?, "expected rejection when #{field} is missing"
        assert_includes stderr, "demo/manifest.yaml"
        assert_includes stderr, field
      end
    end
  end

  # -- validator negatives: contradictory manifests (VAL-MNF-014) --

  def test_nonexistent_included_skill_rejected
    Dir.mktmpdir("bundle-bad-skill") do |root|
      install_tooling(root)
      install_valid_bundle(root)
      manifest_path = File.join(root, "demo", "manifest.yaml")
      data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
      data["included_skills"] = ["../missing-skill/SKILL.md"]
      File.write(manifest_path, data.to_yaml)

      _stdout, stderr, status = run_validator(root)
      refute status.success?
      assert_includes stderr, "demo/manifest.yaml"
      assert_includes stderr, "included_skills"
      assert_includes stderr, "../missing-skill/SKILL.md"
    end
  end

  def test_handoff_undeclared_artifact_rejected
    Dir.mktmpdir("bundle-bad-handoff") do |root|
      install_tooling(root)
      install_valid_bundle(root)
      manifest_path = File.join(root, "demo", "manifest.yaml")
      data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
      data["handoffs"] = [{ "to" => "next team", "artifact" => "not-declared" }]
      File.write(manifest_path, data.to_yaml)

      _stdout, stderr, status = run_validator(root)
      refute status.success?
      assert_includes stderr, "demo/manifest.yaml"
      assert_includes stderr, "handoffs"
      assert_includes stderr, "not-declared"
    end
  end

  def test_conflict_non_catalog_skill_rejected
    Dir.mktmpdir("bundle-bad-conflict") do |root|
      install_tooling(root)
      install_valid_bundle(root)
      manifest_path = File.join(root, "demo", "manifest.yaml")
      data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
      data["conflicts"] = [{ "skill" => "../missing-skill/SKILL.md", "with" => "other", "guidance" => "guidance" }]
      File.write(manifest_path, data.to_yaml)

      _stdout, stderr, status = run_validator(root)
      refute status.success?
      assert_includes stderr, "demo/manifest.yaml"
      assert_includes stderr, "conflicts"
      assert_includes stderr, "../missing-skill/SKILL.md"
    end
  end

  def test_dangling_eval_suite_reference_rejected
    Dir.mktmpdir("bundle-bad-eval") do |root|
      install_tooling(root)
      install_valid_bundle(root)
      manifest_path = File.join(root, "demo", "manifest.yaml")
      data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
      data["eval_suite"] = ["evals/missing.json"]
      File.write(manifest_path, data.to_yaml)

      _stdout, stderr, status = run_validator(root)
      refute status.success?
      assert_includes stderr, "demo/manifest.yaml"
      assert_includes stderr, "eval_suite"
      assert_includes stderr, "evals/missing.json"
    end
  end

  # -- undeclared overlap (VAL-MNF-021(b)) --

  def test_undeclared_overlap_rejected_naming_both_manifests
    Dir.mktmpdir("bundle-overlap") do |root|
      install_tooling(root)
      write_bundle_pair(root)

      _stdout, stderr, status = run_validator(root)
      refute status.success?
      assert_includes stderr, "alpha/manifest.yaml"
      assert_includes stderr, "beta/manifest.yaml"
      assert_includes stderr, "undeclared overlap"
    end
  end

  # -- boundary: no forbidden bundle-membership error path (VAL-MNF-006) --

  def test_validator_has_no_bundle_membership_error_path
    source = File.read(VALIDATOR)
    refute_includes source, "must belong to a bundle"
    refute_includes source, "not a member of any bundle"
  end

  # -- matrix generator: committed outputs are current (VAL-MNF-011) --

  def test_matrix_generator_check_mode_passes_on_committed_outputs
    stdout, stderr, status = Open3.capture3(RbConfig.ruby, "scripts/gen-lifecycle-matrix.rb", chdir: REPO_ROOT)
    assert status.success?, stderr
    assert_includes stdout, "lifecycle capability matrix is current"
  end

  def test_matrix_generator_drift_detection_and_write_mode
    Dir.mktmpdir("gen-matrix") do |root|
      install_tooling(root)
      install_valid_bundle(root)
      # A top-level skill without a manifest.yaml is not a canonical bundle and
      # must be excluded from the matrix (only <skill>/manifest.yaml dirs are).
      write_skill(root, "legacy", name: "legacy")

      _stdout, stderr, status = run_generator(root, "--write")
      assert status.success?, stderr
      md_path = File.join(root, "docs", "lifecycle-capability-matrix.md")
      json_path = File.join(root, "docs", "lifecycle-capability-matrix.json")
      assert File.file?(md_path)
      assert File.file?(json_path)

      md = File.read(md_path)
      assert_includes md, "| demo |"
      refute_includes md, "| legacy |"
      refute_includes md, "migration deferred"
      refute_includes md, "|  |"

      _stdout, stderr, status = run_generator(root)
      assert status.success?, stderr
      assert_includes _stdout, "is current"

      File.open(json_path, "a") { |file| file.write("drift\n") }
      _stdout, stderr, status = run_generator(root)
      refute status.success?
      assert_includes stderr, "ruby scripts/gen-lifecycle-matrix.rb --write"

      _stdout, stderr, status = run_generator(root, "--write")
      assert status.success?, stderr
      _stdout, _stderr, status = run_generator(root)
      assert status.success?
    end
  end

  # -- matrix validator: completeness and traceability (VAL-MNF-024) --

  def test_matrix_validator_passes_on_committed_artifacts
    stdout, stderr, status = Open3.capture3(RbConfig.ruby, "scripts/validate-lifecycle-matrix.rb", chdir: REPO_ROOT)
    assert status.success?, stderr
    assert_includes stdout, "Validated lifecycle capability matrix"
  end

  def test_matrix_validator_rejects_missing_bundle_row
    Dir.mktmpdir("matrix-row") do |root|
      install_tooling(root)
      install_valid_bundle(root)

      _stdout, stderr, status = run_generator(root, "--write")
      assert status.success?, stderr

      json_path = File.join(root, "docs", "lifecycle-capability-matrix.json")
      document = JSON.parse(File.read(json_path))
      document["bundles"].reject! { |row| row["name"] == "demo" }
      File.write(json_path, JSON.pretty_generate(document) + "\n")

      _stdout, stderr, status = run_matrix_validator(root)
      refute status.success?
      assert_includes stderr, "missing row"
      assert_includes stderr, "demo"
    end
  end

  private

  # Minimal JSON-Schema subset validator covering the keywords used by
  # schemas/bundle-manifest-v1.schema.json: type, const, minLength, maxLength,
  # pattern, required, properties, additionalProperties:false, items, minItems,
  # uniqueItems, and $ref into $defs. Proves the committed example is
  # schema-conformant (VAL-MNF-003) without adding dependencies.
  def assert_schema_valid(schema, instance, defs, path = "$")
    if schema.key?("$ref")
      ref = schema["$ref"].delete_prefix("#/$defs/")
      return assert_schema_valid(defs.fetch(ref), instance, defs, path)
    end

    case schema["type"]
    when "string"
      assert_kind_of String, instance, "#{path}: expected string"
      if schema.key?("minLength") && instance.length < schema["minLength"]
        flunk "#{path}: string shorter than minLength #{schema['minLength']}"
      end
      if schema.key?("maxLength") && instance.length > schema["maxLength"]
        flunk "#{path}: string longer than maxLength #{schema['maxLength']}"
      end
      if schema.key?("pattern") && !Regexp.new(schema["pattern"]).match?(instance)
        flunk "#{path}: string does not match pattern #{schema['pattern']}"
      end
    when "integer"
      assert_kind_of Integer, instance, "#{path}: expected integer"
      assert_equal schema["const"], instance, "#{path}: const mismatch" if schema.key?("const")
    when "array"
      assert_kind_of Array, instance, "#{path}: expected array"
      if schema.key?("minItems") && instance.length < schema["minItems"]
        flunk "#{path}: array has fewer than minItems #{schema['minItems']} items"
      end
      if schema.key?("uniqueItems") && schema["uniqueItems"] && instance.uniq.length != instance.length
        flunk "#{path}: array items are not unique"
      end
      instance.each_with_index do |item, index|
        assert_schema_valid(schema["items"], item, defs, "#{path}[#{index}]")
      end
    when "object"
      assert_kind_of Hash, instance, "#{path}: expected object"
      Array(schema["required"]).each do |key|
        assert instance.key?(key), "#{path}: missing required property #{key}"
      end
      if schema["additionalProperties"] == false
        extra = instance.keys - schema["properties"].keys
        assert_empty extra, "#{path}: unexpected properties #{extra.join(', ')}"
      end
      schema["properties"].to_a.each do |key, subschema|
        assert_schema_valid(subschema, instance[key], defs, "#{path}.#{key}") if instance.key?(key)
      end
    end
  end
end
