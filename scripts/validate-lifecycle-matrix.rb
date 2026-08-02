#!/usr/bin/env ruby
# frozen_string_literal: true

# Validates the lifecycle capability matrix artifacts:
#
#   docs/lifecycle-capability-matrix.md   (human-readable)
#   docs/lifecycle-capability-matrix.json (machine-readable)
#
# Checks:
#   (a) every canonical bundle (bundles/*/SKILL.md) has a row in the JSON
#       artifact (VAL-MNF-024)
#   (b) every populated cell traces to its source: for manifest-derived rows
#       the source manifest exists and the named field is present; for
#       frontmatter-derived rows the source SKILL.md exists and the field is
#       description; for migration-deferred cells the design note exists
#       (VAL-MNF-011/024)
#   (c) the structured artifacts are current: the generator's check mode
#       passes (regenerated output matches the committed files) (VAL-MNF-024)
#   (d) nested bundle helpers (bundles/<x>/skills/<sub>/SKILL.md) never appear
#       in the four generated catalogs; only umbrella bundles do (VAL-MNF-020)
#
# Usage:
#   ruby scripts/validate-lifecycle-matrix.rb   # exit 0 when current/complete

require "json"
require "open3"
require "rbconfig"
require "set"
require "yaml"

ROOT = File.expand_path("..", __dir__)
JSON_PATH = File.join(ROOT, "docs", "lifecycle-capability-matrix.json")
GENERATOR = File.join(ROOT, "scripts", "gen-lifecycle-matrix.rb")
DESIGN_NOTE = File.join(ROOT, "docs", "bundle-manifest-design.md")
CATALOG_PATHS = [
  File.join(ROOT, "llms.txt"),
  File.join(ROOT, ".claude-plugin", "marketplace.json"),
  File.join(ROOT, ".codex-plugin", "plugin.json"),
  File.join(ROOT, ".agents", "plugins", "marketplace.json")
].freeze
MATRIX_FIELDS = %w[
  purpose audience stages included_skills prerequisites outputs handoffs
  conflicts eval_suite
].freeze
DOCUMENTED_DERIVATIONS = %w[manifest frontmatter-description migration-deferred].freeze
NESTED_HELPER_PATTERN = %r{bundles/[^/]+/skills/}

errors = []

# (c) structured artifacts are current: generator check mode must pass.
stdout, stderr, status = Open3.capture3(
  RbConfig.ruby,
  File.join("scripts", "gen-lifecycle-matrix.rb"),
  chdir: ROOT
)
unless status.success?
  errors << "lifecycle capability matrix is stale: #{stderr.lines.first&.strip || stdout.lines.first&.strip}"
end

unless File.file?(JSON_PATH)
  warn "docs/lifecycle-capability-matrix.json is missing. Run: ruby scripts/gen-lifecycle-matrix.rb --write"
  exit 1
end

begin
  document = JSON.parse(File.read(JSON_PATH))
rescue JSON::ParserError => e
  warn "docs/lifecycle-capability-matrix.json is invalid JSON: #{e.message.lines.first.strip}"
  exit 1
end

unless document.is_a?(Hash) && document["bundles"].is_a?(Array)
  errors << "docs/lifecycle-capability-matrix.json: top-level document must be a mapping with a bundles array"
end

canonical_bundles = Dir.glob("#{ROOT}/bundles/*/SKILL.md").map do |path|
  File.basename(File.dirname(path))
end.sort
rows = document.is_a?(Hash) ? document["bundles"] : []

# (a) every canonical bundle has a row.
row_names = rows.map { |row| row["name"] }
missing_rows = canonical_bundles - row_names
unless missing_rows.empty?
  errors << "docs/lifecycle-capability-matrix.json: missing row(s) for canonical bundle(s): #{missing_rows.join(', ')}"
end
extra_rows = row_names - canonical_bundles
unless extra_rows.empty?
  errors << "docs/lifecycle-capability-matrix.json: unexpected row(s) for non-canonical bundle(s): #{extra_rows.join(', ')}"
end

# (b) every populated cell traces to its source.
rows.each do |row|
  next unless row.is_a?(Hash)

  name = row["name"]
  fields = row["fields"]
  unless fields.is_a?(Hash)
    errors << "docs/lifecycle-capability-matrix.json: row #{name.inspect} has no fields mapping"
    next
  end

  MATRIX_FIELDS.each do |field|
    cell = fields[field]
    next unless cell.is_a?(Hash)
    next unless cell["value"].is_a?(String) && !cell["value"].strip.empty?
    next if cell["value"].to_s == "migration deferred — see docs/bundle-manifest-design.md §Migration path"

    source = cell["source"].to_s
    derivation = cell["derivation"] || (row["derivation"] == "manifest" ? "manifest" : "unknown")

    case derivation
    when "manifest"
      manifest_rel, pointer = source.split("#/", 2)
      manifest_path = File.join(ROOT, manifest_rel.to_s)
      unless File.file?(manifest_path)
        errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} source manifest #{manifest_rel.inspect} does not exist"
        next
      end
      begin
        data = YAML.safe_load(File.read(manifest_path), permitted_classes: [], aliases: false)
      rescue Psych::Exception
        data = nil
      end
      if data.is_a?(Hash) && pointer && !data.key?(pointer.split("/", 2).first)
        errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} source field #{pointer.inspect} is not declared in #{manifest_rel}"
      elsif !data.is_a?(Hash)
        errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} source manifest #{manifest_rel.inspect} is not a valid YAML mapping"
      end
    when "frontmatter-description"
      source_path = File.join(ROOT, source.split("#/", 2).first.to_s)
      unless File.file?(source_path)
        errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} source #{source_path.delete_prefix("#{ROOT}/")} does not exist"
      end
    when "migration-deferred"
      unless File.file?(DESIGN_NOTE)
        errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} references #{DESIGN_NOTE.delete_prefix("#{ROOT}/")} which does not exist"
      end
    else
      errors << "docs/lifecycle-capability-matrix.json: #{name}.#{field} has undocumented derivation #{derivation.inspect} (allowed: #{DOCUMENTED_DERIVATIONS.join(', ')})"
    end
  end
end

# (d) catalog-exactness: nested bundle helpers never appear in the catalogs.
catalog_matches = []
CATALOG_PATHS.each do |path|
  next unless File.file?(path)

  matches = File.readlines(path).grep(NESTED_HELPER_PATTERN)
  next if matches.empty?

  catalog_matches << "#{path.delete_prefix("#{ROOT}/")} contains nested bundle helper reference(s): #{matches.first.strip}"
end
errors.concat(catalog_matches)

if errors.empty?
  puts "Validated lifecycle capability matrix (#{rows.length} bundle(s)): complete, traceable, and current."
else
  warn errors.join("\n")
  exit 1
end
