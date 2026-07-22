#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"
require "set"
require "json"

ROOT = File.expand_path("..", __dir__)
ALLOWED_FIELDS = %w[name description license compatibility metadata allowed-tools].freeze
README_HEADINGS = ["Why Install This Skill", "What You Get", "Quick Start", "Triggers", "Requirements"].freeze
GRANDFATHER_FILE = File.join(ROOT, "scripts", "grandfathered-skills.txt")
MIN_EVAL_CASES = 5

errors = []
skills = Dir.glob("#{ROOT}/**/SKILL.md").sort.reject do |skill|
  skill.include?("/agent-council/profiles/skills/")
end

catalog_entries = File.read(File.join(ROOT, "README.md")).scan(
  /^### \[([a-z0-9]+(?:-[a-z0-9]+)*)\]\(([^)]+\/SKILL\.md)\)\s*$/
)
catalog_names = catalog_entries.map(&:first)
expected_catalog_names = catalog_names.sort_by { |name| [name.downcase, name] }
unless catalog_names == expected_catalog_names
  mismatch = catalog_names.zip(expected_catalog_names).index { |actual, expected| actual != expected }
  errors << "README.md: skill catalog headings must be sorted case-insensitively; " \
            "position #{mismatch + 1} is #{catalog_names[mismatch].inspect}, " \
            "expected #{expected_catalog_names[mismatch].inspect}"
end

catalog_paths = catalog_entries.map(&:last).sort
expected_catalog_paths = (Dir.glob("#{ROOT}/*/SKILL.md") + Dir.glob("#{ROOT}/bundles/*/SKILL.md"))
                         .map { |path| path.delete_prefix("#{ROOT}/") }
                         .sort
missing_catalog_paths = expected_catalog_paths - catalog_paths
unexpected_catalog_paths = catalog_paths - expected_catalog_paths
duplicate_catalog_names = catalog_names.group_by { |name| name }.select { |_name, values| values.length > 1 }.keys.sort
duplicate_catalog_paths = catalog_paths.group_by { |path| path }.select { |_path, values| values.length > 1 }.keys.sort
mislabeled_catalog_entries = catalog_entries.reject do |name, path|
  name == File.basename(File.dirname(path))
end
errors << "README.md: missing catalog path(s): #{missing_catalog_paths.join(', ')}" unless missing_catalog_paths.empty?
errors << "README.md: unexpected catalog path(s): #{unexpected_catalog_paths.join(', ')}" unless unexpected_catalog_paths.empty?
errors << "README.md: duplicate catalog name(s): #{duplicate_catalog_names.join(', ')}" unless duplicate_catalog_names.empty?
errors << "README.md: duplicate catalog path(s): #{duplicate_catalog_paths.join(', ')}" unless duplicate_catalog_paths.empty?
unless mislabeled_catalog_entries.empty?
  labels = mislabeled_catalog_entries.map { |name, path| "#{name.inspect} -> #{path}" }
  errors << "README.md: catalog label/path mismatch(es): #{labels.join(', ')}"
end

grandfathered = File.exist?(GRANDFATHER_FILE) ? File.readlines(GRANDFATHER_FILE, chomp: true).reject { |l| l.strip.empty? || l.start_with?("#") }.to_set : Set.new

skills.each do |skill|
  relative = skill.delete_prefix("#{ROOT}/")
  text = File.read(skill)
  match = text.match(/\A---\n(.*?)\n---\n/m)
  unless match
    errors << "#{relative}: missing YAML frontmatter"
    next
  end

  begin
    data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
  rescue Psych::Exception => e
    errors << "#{relative}: invalid YAML: #{e.message.lines.first.strip}"
    next
  end

  unless data.is_a?(Hash)
    errors << "#{relative}: frontmatter must be a mapping"
    next
  end

  name = data["name"]
  expected_name = File.basename(File.dirname(skill))
  errors << "#{relative}: invalid name" unless name.is_a?(String) && name.match?(/\A[a-z0-9]+(?:-[a-z0-9]+)*\z/) && name.length.between?(1, 64) && name == expected_name
  description = data["description"]
  errors << "#{relative}: invalid description" unless description.is_a?(String) && description.length.between?(1, 1024)
  errors << "#{relative}: unsupported field(s): #{(data.keys - ALLOWED_FIELDS).join(', ')}" unless (data.keys - ALLOWED_FIELDS).empty?
  if data.key?("compatibility") && (!data["compatibility"].is_a?(String) || !data["compatibility"].length.between?(1, 500))
    errors << "#{relative}: invalid compatibility"
  end
  if data.key?("metadata") && (!data["metadata"].is_a?(Hash) || !data["metadata"].all? { |key, value| key.is_a?(String) && value.is_a?(String) })
    errors << "#{relative}: metadata must map strings to strings"
  end
  errors << "#{relative}: metadata.hermes is client-specific and not allowed" if data.dig("metadata", "hermes")
  errors << "#{relative}: must stay under 500 lines" unless text.lines.length < 500

  root = File.dirname(skill)
  text.scan(/\[[^\]]+\]\(([^)]+)\)/).flatten.each do |target|
    path = target.split("#", 2).first
    next if path.empty? || path.match?(%r{\A(?:https?:|mailto:|/)})
    errors << "#{relative}: missing linked resource #{path}" unless File.exist?(File.expand_path(path, root))
  end

  readme = File.join(root, "README.md")
  unless File.file?(readme)
    errors << "#{relative}: missing README.md"
    next
  end
  readme_text = File.read(readme)
  README_HEADINGS.each do |heading|
    errors << "#{relative}: README missing #{heading}" unless readme_text.match?(/^#+ #{Regexp.escape(heading)}\s*$/)
  end

  # Phase 1: new skills (not grandfathered) must have evals with >= MIN_EVAL_CASES cases
  skill_dir = File.dirname(skill).delete_prefix("#{ROOT}/")
  unless grandfathered.include?(skill_dir)
    evals_path = File.join(root, "evals", "evals.json")
    unless File.file?(evals_path)
      errors << "#{relative}: new skill must have evals/evals.json (not in grandfathered-skills.txt)"
      next
    end
    begin
      evals_data = JSON.parse(File.read(evals_path))
      case_count = evals_data.is_a?(Hash) && evals_data["evals"].is_a?(Array) ? evals_data["evals"].length : 0
      if case_count < MIN_EVAL_CASES
        errors << "#{relative}: evals/evals.json has #{case_count} case(s), minimum is #{MIN_EVAL_CASES}"
      end
    rescue JSON::ParserError => e
      errors << "#{relative}: evals/evals.json is invalid JSON: #{e.message.lines.first.strip}"
    end
  end
end

if errors.empty?
  puts "Validated #{skills.length} canonical skills."
else
  warn errors.join("\n")
  exit 1
end
