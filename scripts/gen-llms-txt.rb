#!/usr/bin/env ruby
# frozen_string_literal: true

# Generates and validates root llms.txt catalog of all public installable skills:
#
#   # agent-skills
#
#   ## Skills
#
#   - [name](relative/path/SKILL.md): Description
#
# Each skill entry appears exactly once, keyed by its skill directory name, with a one-line description.
# Description normalization: folded/multiline YAML frontmatter becomes a single space-separated line.
# Links are relative to repository root per issue #78.
#
# Usage:
#   ruby scripts/gen-llms-txt.rb           # validate committed llms.txt matches current
#   ruby scripts/gen-llms-txt.rb --write   # regenerate llms.txt and report count

require "fileutils"
require "yaml"

ROOT = File.expand_path("..", __dir__)
LLMS_TXT_PATH = File.join(ROOT, "llms.txt")

# Public install candidates: top-level skills and bundle entrypoints.
# Same glob as gen-claude-marketplace.rb, gen-codex-plugin.rb, validate-skills.rb and README catalog:
#   #{ROOT}/*/SKILL.md  +  #{ROOT}/bundles/*/SKILL.md
# Excludes bundle-internal helper skills (bundles/<x>/skills/<sub>/SKILL.md).
PUBLIC_SKILLS = (Dir.glob("#{ROOT}/*/SKILL.md") + Dir.glob("#{ROOT}/bundles/*/SKILL.md")).sort

def frontmatter(skill_path)
  text = File.read(skill_path)
  match = text.match(/\A---\n(.*?)\n---\n/m)
  raise "#{skill_path}: missing YAML frontmatter" unless match

  data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
  raise "#{skill_path}: frontmatter must be a mapping" unless data.is_a?(Hash)

  data
end

def normalize_description(text)
  text.to_s.gsub(/\s+/, " ").strip
end

def build_llms_txt
  skill_entries = []
  seen_names = {}

  PUBLIC_SKILLS.sort_by do |path|
    name = File.basename(File.dirname(path))
    [name.downcase, name, path.delete_prefix("#{ROOT}/")]
  end.each do |skill_path|
    dir = File.dirname(skill_path)
    name = File.basename(dir)
    data = frontmatter(skill_path)
    relative_path = skill_path.delete_prefix("#{ROOT}/")
    raw_name = data["name"]
    unless raw_name.is_a?(String) && raw_name == name
      raise "#{relative_path}: name must match directory name #{name.inspect}"
    end
    name_key = name.downcase
    if seen_names.key?(name_key)
      raise "duplicate catalog name #{name.inspect}: #{seen_names[name_key]} and #{relative_path}"
    end
    seen_names[name_key] = relative_path

    raw_description = data["description"]
    unless raw_description.is_a?(String) && !raw_description.strip.empty?
      raise "#{relative_path}: description must be a nonempty string"
    end
    description = normalize_description(raw_description)

    entry = "- [#{name}](#{relative_path}): #{description}"
    skill_entries << entry
  end

  result = ["# agent-skills", "", "## Skills", "", *skill_entries, ""].join("\n")
  result
end

def write_llms_txt(content)
  FileUtils.mkdir_p(File.dirname(LLMS_TXT_PATH))
  File.write(LLMS_TXT_PATH, content)
  puts "Wrote #{LLMS_TXT_PATH.delete_prefix("#{ROOT}/")} (#{PUBLIC_SKILLS.length} skills)."
end

expected = build_llms_txt

if ARGV.include?("--write")
  write_llms_txt(expected)
  exit 0
end

unless File.file?(LLMS_TXT_PATH)
  warn "#{LLMS_TXT_PATH.delete_prefix("#{ROOT}/")} is missing. Run: ruby scripts/gen-llms-txt.rb --write"
  exit 1
end

actual = File.read(LLMS_TXT_PATH)
if actual != expected
  warn "#{LLMS_TXT_PATH.delete_prefix("#{ROOT}/")} is out of date. Run: ruby scripts/gen-llms-txt.rb --write"
  exit 1
end

puts "llms.txt is current (#{PUBLIC_SKILLS.length} skills)."
