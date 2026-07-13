#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"

ROOT = File.expand_path("..", __dir__)
ALLOWED_FIELDS = %w[name description license compatibility metadata allowed-tools].freeze
README_HEADINGS = ["Why Install This Skill", "What You Get", "Quick Start", "Triggers", "Requirements"].freeze

errors = []
skills = Dir.glob("#{ROOT}/**/SKILL.md").sort.reject do |skill|
  skill.include?("/agent-council/profiles/skills/")
end

catalog_names = File.read(File.join(ROOT, "README.md")).scan(
  /^### \[([a-z0-9]+(?:-[a-z0-9]+)*)\]\([^)]+\/SKILL\.md\)\s*$/
).flatten
expected_catalog_names = catalog_names.sort_by { |name| [name.downcase, name] }
unless catalog_names == expected_catalog_names
  mismatch = catalog_names.zip(expected_catalog_names).index { |actual, expected| actual != expected }
  errors << "README.md: skill catalog headings must be sorted case-insensitively; " \
            "position #{mismatch + 1} is #{catalog_names[mismatch].inspect}, " \
            "expected #{expected_catalog_names[mismatch].inspect}"
end

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
end

if errors.empty?
  puts "Validated #{skills.length} canonical skills."
else
  warn errors.join("\n")
  exit 1
end
