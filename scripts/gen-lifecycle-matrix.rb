#!/usr/bin/env ruby
# frozen_string_literal: true

# Generates and validates the lifecycle capability matrix artifacts:
#
#   docs/lifecycle-capability-matrix.md   # human-readable, one row per canonical bundle
#   docs/lifecycle-capability-matrix.json # machine-readable, per-cell source provenance
#
# Every matrix entry derives from a declared bundle manifest field
# (<name>/manifest.yaml) or a documented derivation (SKILL.md
# frontmatter description for manifest-less bundles; a documented deferral
# marker for the remaining cells). See docs/bundle-manifest-design.md.
#
# Conventions follow gen-claude-marketplace.rb / gen-codex-plugin.rb /
# gen-llms-txt.rb: ROOT constant, the same PUBLIC_SKILLS glob semantics,
# YAML.safe_load frontmatter parsing, deterministic ordering, --write mode,
# and a check mode that exits non-zero with a "Run: ... --write" hint when
# output is stale.
#
# Usage:
#   ruby scripts/gen-lifecycle-matrix.rb           # validate committed artifacts are current
#   ruby scripts/gen-lifecycle-matrix.rb --write   # regenerate both artifacts

require "fileutils"
require "json"
require "yaml"

ROOT = File.expand_path("..", __dir__)
SCHEMA_VERSION = 1
GENERATOR_REL = "scripts/gen-lifecycle-matrix.rb"
MD_PATH = File.join(ROOT, "docs", "lifecycle-capability-matrix.md")
JSON_PATH = File.join(ROOT, "docs", "lifecycle-capability-matrix.json")
DEFERRED_MARKER = "migration deferred — see docs/bundle-manifest-design.md §Migration path"
DESIGN_NOTE = "docs/bundle-manifest-design.md#migration-path"

# Public install candidates: top-level skills and bundle entrypoints.
# Same glob as the other generators and validate-skills.rb; excludes
# bundle-internal helper skills (<x>/skills/<sub>/SKILL.md).
PUBLIC_SKILLS = Dir.glob("#{ROOT}/*/SKILL.md").sort

CANONICAL_BUNDLES = Dir.glob("#{ROOT}/*/manifest.yaml").map do |path|
  File.basename(File.dirname(path))
end.sort

def normalize_description(text)
  text.to_s.gsub(/\s+/, " ").strip
end

def frontmatter(skill_path)
  text = File.read(skill_path)
  match = text.match(/\A---\n(.*?)\n---\n/m)
  raise "#{skill_path}: missing YAML frontmatter" unless match

  data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
  raise "#{skill_path}: frontmatter must be a mapping" unless data.is_a?(Hash)

  data
end

def skill_display_name(entry, base_dir = ROOT)
  expanded = File.expand_path(entry, base_dir)
  return entry unless File.file?(expanded)

  File.basename(File.dirname(expanded))
rescue ArgumentError
  entry
end

def field_cell(relative_manifest, field, value)
  { "value" => value, "source" => "#{relative_manifest}#/#{field}" }
end

def deferred_cell
  { "value" => DEFERRED_MARKER, "source" => DESIGN_NOTE, "derivation" => "migration-deferred" }
end

def manifest_row(name, data, relative_manifest)
  {
    "name" => name,
    "derivation" => "manifest",
    "source" => relative_manifest,
    "fields" => {
      "purpose" => field_cell(relative_manifest, "purpose", data["purpose"]),
      "audience" => field_cell(relative_manifest, "audience", data["audience"]),
      "stages" => field_cell(relative_manifest, "stages", data["stages"]),
      "included_skills" => field_cell(relative_manifest, "included_skills", data["included_skills"]),
      "prerequisites" => field_cell(relative_manifest, "prerequisites", data["prerequisites"]),
      "outputs" => field_cell(relative_manifest, "outputs", data["outputs"]),
      "handoffs" => field_cell(relative_manifest, "handoffs", data["handoffs"]),
      "conflicts" => field_cell(relative_manifest, "conflicts", data["conflicts"]),
      "eval_suite" => field_cell(relative_manifest, "eval_suite", data["eval_suite"])
    }
  }
end

def deferred_row(name, description)
  {
    "name" => name,
    "derivation" => "frontmatter-description-and-deferred-migration",
    "source" => "#{name}/SKILL.md",
    "fields" => {
      "purpose" => { "value" => description, "source" => "#{name}/SKILL.md#/description", "derivation" => "frontmatter-description" },
      "audience" => deferred_cell,
      "stages" => deferred_cell,
      "included_skills" => deferred_cell,
      "prerequisites" => deferred_cell,
      "outputs" => deferred_cell,
      "handoffs" => deferred_cell,
      "conflicts" => deferred_cell,
      "eval_suite" => deferred_cell
    }
  }
end

def build_matrix
  CANONICAL_BUNDLES.map do |name|
    manifest = File.join(ROOT, name, "manifest.yaml")
    relative_manifest = "#{name}/manifest.yaml"
    if File.file?(manifest)
      data = YAML.safe_load(File.read(manifest), permitted_classes: [], aliases: false)
      raise "#{relative_manifest}: manifest must be a mapping" unless data.is_a?(Hash)

      manifest_row(name, data, relative_manifest)
    else
      description = normalize_description(frontmatter(File.join(ROOT, name, "SKILL.md"))["description"])
      deferred_row(name, description)
    end
  end
end

def cell_value(cell)
  cell["value"]
end

def join_cells(values)
  values.compact.reject { |value| value.to_s.strip.empty? }.join(", ")
end

def summary_cell(row, field)
  base = File.join(ROOT, row["name"])
  value = cell_value(row["fields"][field])
  result =
    case field
    when "purpose"
      value.to_s
    when "audience"
      value.to_s
    when "stages"
      value.is_a?(Array) ? value.map { |stage| stage["name"] }.join(" → ") : value.to_s
    when "included_skills"
      value.is_a?(Array) ? value.map { |entry| skill_display_name(entry, base) }.join(", ") : value.to_s
    when "prerequisites"
      if value.is_a?(Array)
        value.map do |entry|
          skill = entry["skill"] ? "(#{skill_display_name(entry['skill'], base)})" : ""
          "#{entry['artifact']}#{skill}"
        end.join("; ")
      else
        value.to_s
      end
    when "outputs"
      value.is_a?(Array) ? value.join(", ") : value.to_s
    when "handoffs"
      if value.is_a?(Array)
        value.map { |entry| "#{entry['artifact']} → #{entry['to']}" }.join("; ")
      else
        value.to_s
      end
    when "conflicts"
      if value.is_a?(Array)
        value.map { |entry| "#{skill_display_name(entry['skill'], base)} (with #{entry['with']})" }.join("; ")
      else
        value.to_s
      end
    when "eval_suite"
      value.is_a?(Array) ? value.join(", ") : value.to_s
    else
      value.to_s
    end
  result.strip.empty? ? "none declared" : result
end

def render_markdown(matrix)
  lines = []
  lines << "# Lifecycle Capability Matrix"
  lines << ""
  lines << "Deterministically generated by `#{GENERATOR_REL}` (schema version #{SCHEMA_VERSION}). "
  lines << "Every matrix entry derives from a declared bundle manifest field or a documented "
  lines << "derivation; see [bundle-manifest-design.md](bundle-manifest-design.md) for the schema, "
  lines << "the migration path, and the field definitions. Regenerate with "
  lines << "`ruby scripts/gen-lifecycle-matrix.rb --write`."
  lines << ""
  lines << "## Summary"
  lines << ""
  lines << "| Bundle | Purpose | Audience | Lifecycle stages | Included skills | Prerequisites | Outputs | Handoffs | Conflicts | Eval suite |"
  lines << "|---|---|---|---|---|---|---|---|---|---|"
  matrix.each do |row|
    cells = ["#{row['name']}"] + %w[purpose audience stages included_skills prerequisites outputs handoffs conflicts eval_suite].map do |field|
      summary_cell(row, field)
    end
    lines << "| #{cells.join(' | ')} |"
  end
  lines << ""
  lines << "## Details"
  lines << ""
  matrix.each do |row|
    lines << "### #{row['name']}"
    lines << ""
    lines << "- Derivation: `#{row['derivation']}` — source: `#{row['source']}`"
    base = File.join(ROOT, row["name"])
    fields = row["fields"]
    lines << "- **Purpose:** #{cell_value(fields['purpose'])}"
    lines << "- **Audience:** #{cell_value(fields['audience'])}"
    stages = cell_value(fields["stages"])
    if stages.is_a?(Array)
      lines << "- **Stages (ordered):**"
      stages.each_with_index do |stage, index|
        skills = stage["skills"].map { |entry| "#{skill_display_name(entry, base)} (`#{entry}`)" }.join(", ")
        lines << "  #{index + 1}. #{stage['name']} — #{skills}"
      end
    else
      lines << "- **Stages:** #{stages}"
    end
    included = cell_value(fields["included_skills"])
    if included.is_a?(Array)
      lines << "- **Included skills:**"
      included.each { |entry| lines << "  - #{skill_display_name(entry, base)} (`#{entry}`)" }
    else
      lines << "- **Included skills:** #{included}"
    end
    prereqs = cell_value(fields["prerequisites"])
    if prereqs.is_a?(Array)
      lines << "- **Prerequisites:**"
      prereqs.each do |entry|
        skill = entry["skill"] ? " — via #{skill_display_name(entry['skill'], base)} (`#{entry['skill']}`)" : ""
        lines << "  - #{entry['artifact']}#{skill}"
      end
    else
      lines << "- **Prerequisites:** #{prereqs}"
    end
    outputs = cell_value(fields["outputs"])
    lines << "- **Outputs:** #{outputs.is_a?(Array) ? outputs.join(', ') : outputs}"
    handoffs = cell_value(fields["handoffs"])
    if handoffs.is_a?(Array)
      lines << "- **Handoffs:**"
      handoffs.each do |entry|
        note = entry["note"] ? " — #{entry['note']}" : ""
        lines << "  - #{entry['artifact']} → #{entry['to']}#{note}"
      end
    else
      lines << "- **Handoffs:** #{handoffs}"
    end
    conflicts = cell_value(fields["conflicts"])
    if conflicts.is_a?(Array)
      if conflicts.empty?
        lines << "- **Conflicts:** none declared"
      else
        lines << "- **Conflicts:**"
        conflicts.each do |entry|
          lines << "  - #{skill_display_name(entry['skill'], base)} (`#{entry['skill']}`) with #{entry['with']} — #{entry['guidance']}"
        end
      end
    else
      lines << "- **Conflicts:** #{conflicts}"
    end
    eval_suite = cell_value(fields["eval_suite"])
    lines << "- **Eval suite:** #{eval_suite.is_a?(Array) ? eval_suite.join(', ') : eval_suite}"
    lines << ""
  end
  lines.join("\n")
end

matrix = build_matrix

json_document = {
  "schema_version" => SCHEMA_VERSION,
  "generated_by" => GENERATOR_REL,
  "bundles" => matrix
}

expected_md = render_markdown(matrix)
expected_json = JSON.pretty_generate(json_document) + "\n"

def write_artifacts(expected_md, expected_json)
  FileUtils.mkdir_p(File.dirname(MD_PATH))
  FileUtils.mkdir_p(File.dirname(JSON_PATH))
  File.write(MD_PATH, expected_md)
  File.write(JSON_PATH, expected_json)
  puts "Wrote #{MD_PATH.delete_prefix("#{ROOT}/")} and #{JSON_PATH.delete_prefix("#{ROOT}/")} (#{CANONICAL_BUNDLES.length} bundles)."
end

def current?(path, expected)
  File.file?(path) && File.read(path) == expected
end

if ARGV.include?("--write")
  write_artifacts(expected_md, expected_json)
  exit 0
end

unless current?(MD_PATH, expected_md) && current?(JSON_PATH, expected_json)
  warn "lifecycle capability matrix is out of date. Run: ruby scripts/gen-lifecycle-matrix.rb --write"
  exit 1
end

puts "lifecycle capability matrix is current (#{CANONICAL_BUNDLES.length} bundles)."
