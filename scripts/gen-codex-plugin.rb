#!/usr/bin/env ruby
# frozen_string_literal: true

# Generates and validates the Codex plugin packaging:
#   .codex-plugin/plugin.json  — single plugin manifest listing all public skills
#   .agents/plugins/marketplace.json — one-entry marketplace pointing at repo root
#
# Usage:
#   ruby scripts/gen-codex-plugin.rb           # validate committed files are current
#   ruby scripts/gen-codex-plugin.rb --write   # regenerate both files

require "fileutils"
require "json"
require "yaml"

ROOT = File.expand_path("..", __dir__)
PLUGIN_JSON_PATH = File.join(ROOT, ".codex-plugin", "plugin.json")
MARKETPLACE_PATH = File.join(ROOT, ".agents", "plugins", "marketplace.json")

PLUGIN_NAME = "magnus919"
PLUGIN_VERSION = "1.0.0"

# Same glob as gen-claude-marketplace.rb: top-level skills + bundle entrypoints.
# Excludes bundle-internal helpers (bundles/<x>/skills/<sub>/SKILL.md).
PUBLIC_SKILLS = (Dir.glob("#{ROOT}/*/SKILL.md") + Dir.glob("#{ROOT}/bundles/*/SKILL.md")).sort

def build_plugin_json
  skill_paths = PUBLIC_SKILLS.map do |skill|
    "./#{File.dirname(skill).delete_prefix("#{ROOT}/")}"
  end.sort

  {
    "name" => PLUGIN_NAME,
    "version" => PLUGIN_VERSION,
    "description" => "AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems.",
    "author" => {
      "name" => "Magnus Hedemark",
      "url" => "https://github.com/magnus919"
    },
    "homepage" => "https://github.com/magnus919/agent-skills",
    "repository" => "https://github.com/magnus919/agent-skills",
    "license" => "MIT",
    "keywords" => %w[agent-skills engineering product research infrastructure methodology],
    "skills" => skill_paths
  }
end

def build_marketplace
  {
    "name" => PLUGIN_NAME,
    "interface" => {
      "displayName" => "Magnus Agent Skills"
    },
    "plugins" => [
      {
        "name" => PLUGIN_NAME,
        "source" => {
          "source" => "local",
          "path" => "./"
        },
        "policy" => {
          "installation" => "AVAILABLE",
          "authentication" => "ON_INSTALL"
        },
        "category" => "Developer Tools"
      }
    ]
  }
end

def render(obj)
  JSON.pretty_generate(obj) + "\n"
end

expected_plugin = render(build_plugin_json)
expected_marketplace = render(build_marketplace)

if ARGV.include?("--write")
  FileUtils.mkdir_p(File.dirname(PLUGIN_JSON_PATH))
  FileUtils.mkdir_p(File.dirname(MARKETPLACE_PATH))
  File.write(PLUGIN_JSON_PATH, expected_plugin)
  File.write(MARKETPLACE_PATH, expected_marketplace)
  puts "Wrote .codex-plugin/plugin.json and .agents/plugins/marketplace.json (#{PUBLIC_SKILLS.length} skills)."
  exit 0
end

errors = []

if !File.file?(PLUGIN_JSON_PATH)
  errors << ".codex-plugin/plugin.json is missing."
elsif File.read(PLUGIN_JSON_PATH) != expected_plugin
  errors << ".codex-plugin/plugin.json is out of date."
end

if !File.file?(MARKETPLACE_PATH)
  errors << ".agents/plugins/marketplace.json is missing."
elsif File.read(MARKETPLACE_PATH) != expected_marketplace
  errors << ".agents/plugins/marketplace.json is out of date."
end

if errors.empty?
  puts "Codex plugin packaging is current (#{PUBLIC_SKILLS.length} skills)."
else
  warn errors.join("\n")
  warn "Run: ruby scripts/gen-codex-plugin.rb --write"
  exit 1
end
