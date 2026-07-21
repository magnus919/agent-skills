#!/usr/bin/env ruby
# frozen_string_literal: true

# Generates and validates .claude-plugin/marketplace.json — the metadata-only
# catalog that lets Claude Code install skills straight from this repository:
#
#   /plugin marketplace add magnus919/agent-skills
#   /plugin install cli-builder@magnus-agent-skills
#
# Each public skill becomes a plugin entry whose source is the repository root
# and whose `skills` field points at the skill's own directory. `strict: false`
# means no per-skill plugin.json is required. Bundle-internal helper skills are
# intentionally excluded — they ship inside their bundle, not standalone.
#
# Usage:
#   ruby scripts/gen-claude-marketplace.rb           # validate committed file is current
#   ruby scripts/gen-claude-marketplace.rb --write   # regenerate the file

require "fileutils"
require "json"
require "yaml"

ROOT = File.expand_path("..", __dir__)
MARKETPLACE_PATH = File.join(ROOT, ".claude-plugin", "marketplace.json")
MARKETPLACE_NAME = "magnus-agent-skills" # "agent-skills" is reserved by Claude Code

# Public install candidates: top-level skills and bundle entrypoints. This is
# the same glob validate-skills.rb uses for the README catalog, and it excludes
# bundle-internal helper skills (bundles/<bundle>/skills/<sub>/SKILL.md).
PUBLIC_SKILLS = (Dir.glob("#{ROOT}/*/SKILL.md") + Dir.glob("#{ROOT}/bundles/*/SKILL.md")).sort

def frontmatter(skill_path)
  text = File.read(skill_path)
  match = text.match(/\A---\n(.*?)\n---\n/m)
  raise "#{skill_path}: missing YAML frontmatter" unless match

  data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
  raise "#{skill_path}: frontmatter must be a mapping" unless data.is_a?(Hash)

  data
end

def build_marketplace
  plugins = PUBLIC_SKILLS.map do |skill|
    dir = File.dirname(skill)
    name = File.basename(dir)
    data = frontmatter(skill)
    description = data["description"].to_s.gsub(/\s+/, " ").strip
    {
      "name" => name,
      "source" => "./",
      "skills" => ["./#{name}"],
      "strict" => false,
      "description" => description
    }
  end.sort_by { |entry| entry["name"] }

  {
    "name" => MARKETPLACE_NAME,
    "owner" => { "name" => "Magnus Hedemark" },
    "description" => "AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems.",
    "plugins" => plugins
  }
end

def render(marketplace)
  JSON.pretty_generate(marketplace) + "\n"
end

expected = render(build_marketplace)

if ARGV.include?("--write")
  FileUtils.mkdir_p(File.dirname(MARKETPLACE_PATH))
  File.write(MARKETPLACE_PATH, expected)
  puts "Wrote #{MARKETPLACE_PATH.delete_prefix("#{ROOT}/")} (#{PUBLIC_SKILLS.length} plugins)."
  exit 0
end

unless File.file?(MARKETPLACE_PATH)
  warn "#{MARKETPLACE_PATH.delete_prefix("#{ROOT}/")} is missing. Run: ruby scripts/gen-claude-marketplace.rb --write"
  exit 1
end

actual = File.read(MARKETPLACE_PATH)
if actual != expected
  warn "#{MARKETPLACE_PATH.delete_prefix("#{ROOT}/")} is out of date. Run: ruby scripts/gen-claude-marketplace.rb --write"
  exit 1
end

puts "marketplace.json is current (#{PUBLIC_SKILLS.length} plugins)."
