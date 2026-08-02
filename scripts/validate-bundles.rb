#!/usr/bin/env ruby
# frozen_string_literal: true

# Validates bundle manifests (bundles/*/manifest.yaml) against the
# bundle-manifest v1 contract declared in schemas/bundle-manifest-v1.schema.json.
#
# Checks:
#   - the schema file itself parses as JSON (VAL-MNF-002)
#   - required-field completeness: every required field present, naming the
#     manifest file and the missing field (VAL-MNF-013)
#   - contradiction checks (VAL-MNF-014):
#       * included_skills entry resolves to an existing SKILL.md file
#       * handoffs.artifact names a declared output or stage
#       * conflicts.skill resolves to a catalog skill
#   - eval_suite resolves to existing eval manifests (VAL-MNF-017)
#   - declared conflicts pass (VAL-MNF-021(a)); undeclared cross-bundle
#     overlaps on included skills are rejected, naming both manifests
#     (VAL-MNF-021(b))
#   - bundle_name matches the parent directory name
#
# Boundaries: manifests are NOT a second skill format. This validator never
# requires a top-level skill to belong to a bundle and never touches
# validate-skills.rb's ALLOWED_FIELDS (VAL-MNF-005/006).
#
# Usage:
#   ruby scripts/validate-bundles.rb   # validate all bundle manifests, exit 0 if valid

require "json"
require "set"
require "yaml"

ROOT = File.expand_path("..", __dir__)
SCHEMA_PATH = File.join(ROOT, "schemas", "bundle-manifest-v1.schema.json")
REQUIRED_FIELDS = %w[
  schema_version bundle_name purpose audience stages included_skills
  prerequisites outputs handoffs conflicts eval_suite
].freeze

def manifest_paths
  Dir.glob("#{ROOT}/bundles/*/manifest.yaml").sort
end

def errors_for(manifest)
  relative = manifest.delete_prefix("#{ROOT}/")
  errors = []
  begin
    data = YAML.safe_load(File.read(manifest), permitted_classes: [], aliases: false)
  rescue Psych::Exception => e
    return ["#{relative}: invalid YAML: #{e.message.lines.first.strip}"]
  end

  unless data.is_a?(Hash)
    return ["#{relative}: manifest must be a mapping"]
  end

  REQUIRED_FIELDS.each do |field|
    errors << "#{relative}: missing required field: #{field}" unless data.key?(field)
  end
  return errors unless errors.empty?

  expected_name = File.basename(File.dirname(manifest))
  if data["bundle_name"] != expected_name
    errors << "#{relative}: bundle_name #{data['bundle_name'].inspect} does not match directory name #{expected_name.inspect}"
  end
  unless data["schema_version"] == 1
    errors << "#{relative}: schema_version must be 1 (found #{data['schema_version'].inspect})"
  end
  %w[purpose audience].each do |field|
    value = data[field]
    errors << "#{relative}: #{field} must be a non-empty string" unless value.is_a?(String) && !value.strip.empty?
  end

  included_skills = data["included_skills"]
  unless included_skills.is_a?(Array) && included_skills.all? { |entry| entry.is_a?(String) }
    errors << "#{relative}: included_skills must be a non-empty array of path strings"
  else
    included_skills.each do |entry|
      unless file_resolves?(File.dirname(manifest), entry)
        errors << "#{relative}: included_skills entry #{entry.inspect} does not resolve to an existing SKILL.md"
      end
    end
  end

  stages = data["stages"]
  unless stages.is_a?(Array) && stages.all? { |stage| stage.is_a?(Hash) }
    errors << "#{relative}: stages must be a non-empty ordered array of stage objects"
  else
    stage_names = stages.map { |stage| stage["name"] }
    stages.each do |stage|
      unless stage["name"].is_a?(String) && !stage["name"].strip.empty?
        errors << "#{relative}: stages entry must have a non-empty name"
      end
      skills = stage["skills"]
      unless skills.is_a?(Array) && skills.all? { |entry| entry.is_a?(String) }
        errors << "#{relative}: stages entry #{stage['name'].inspect} must have a skills array of path strings"
      else
        skills.each do |entry|
          unless file_resolves?(File.dirname(manifest), entry)
            errors << "#{relative}: stages entry #{stage['name'].inspect} references #{entry.inspect} which does not resolve to an existing SKILL.md"
          end
        end
      end
    end

    outputs = data["outputs"]
    unless outputs.is_a?(Array) && outputs.all? { |entry| entry.is_a?(String) }
      errors << "#{relative}: outputs must be a non-empty array of artifact-name strings"
    end

    handoffs = data["handoffs"]
    unless handoffs.is_a?(Array) && handoffs.all? { |entry| entry.is_a?(Hash) }
      errors << "#{relative}: handoffs must be a non-empty array of handoff objects"
    else
      declared = (outputs.is_a?(Array) ? outputs : []) + stage_names
      handoffs.each_with_index do |handoff, index|
        artifact = handoff["artifact"]
        unless artifact.is_a?(String) && declared.include?(artifact)
          errors << "#{relative}: handoffs[#{index}].artifact #{artifact.inspect} does not match any declared output or stage"
        end
        unless handoff["to"].is_a?(String) && !handoff["to"].to_s.strip.empty?
          errors << "#{relative}: handoffs[#{index}].to must be a non-empty string"
        end
      end
    end
  end

  prerequisites = data["prerequisites"]
  unless prerequisites.is_a?(Array) && prerequisites.all? { |entry| entry.is_a?(Hash) }
    errors << "#{relative}: prerequisites must be a non-empty array of prerequisite objects"
  else
    prerequisites.each_with_index do |prereq, index|
      unless prereq["artifact"].is_a?(String) && !prereq["artifact"].to_s.strip.empty?
        errors << "#{relative}: prerequisites[#{index}].artifact must be a non-empty string"
      end
      skill = prereq["skill"]
      if skill && !file_resolves?(File.dirname(manifest), skill)
        errors << "#{relative}: prerequisites[#{index}].skill #{skill.inspect} does not resolve to an existing SKILL.md"
      end
    end
  end

  conflicts = data["conflicts"]
  unless conflicts.is_a?(Array) && conflicts.all? { |entry| entry.is_a?(Hash) }
    errors << "#{relative}: conflicts must be an array of conflict objects"
  else
    conflicts.each_with_index do |conflict, index|
      skill = conflict["skill"]
      if !skill.is_a?(String) || !file_resolves?(File.dirname(manifest), skill)
        errors << "#{relative}: conflicts[#{index}].skill #{skill.inspect} is not a catalog skill (path must resolve to an existing SKILL.md)"
      end
      unless conflict["with"].is_a?(String) && !conflict["with"].to_s.strip.empty?
        errors << "#{relative}: conflicts[#{index}].with must be a non-empty string"
      end
      unless conflict["guidance"].is_a?(String) && !conflict["guidance"].to_s.strip.empty?
        errors << "#{relative}: conflicts[#{index}].guidance must be a non-empty string"
      end
    end
  end

  eval_suite = data["eval_suite"]
  unless eval_suite.is_a?(Array) && eval_suite.all? { |entry| entry.is_a?(String) }
    errors << "#{relative}: eval_suite must be a non-empty array of path strings"
  else
    eval_suite.each do |entry|
      unless file_resolves?(File.dirname(manifest), entry)
        errors << "#{relative}: eval_suite entry #{entry.inspect} does not resolve to an existing file"
      end
    end
  end

  errors
end

def file_resolves?(base_dir, relative)
  return false unless relative.is_a?(String) && !relative.empty?
  return false if relative.match?(%r{\A/}) || relative.match?(%r{\A\./})

  File.file?(File.expand_path(relative, base_dir))
end

def resolved_skill_paths(manifest, data)
  base = File.dirname(manifest)
  (data["included_skills"] || []).map { |entry| File.expand_path(entry, base) }
end

def conflict_declares?(manifest, data, skill_abs, other_name)
  (data["conflicts"] || []).any? do |entry|
    skill = entry["skill"]
    next false unless skill.is_a?(String)

    File.expand_path(skill, File.dirname(manifest)) == skill_abs && entry["with"] == other_name
  end
end

def overlap_errors(manifests)
  errors = []
  manifests.combination(2) do |a, b|
    a_data = YAML.safe_load(File.read(a), permitted_classes: [], aliases: false)
    b_data = YAML.safe_load(File.read(b), permitted_classes: [], aliases: false)
    next unless a_data.is_a?(Hash) && b_data.is_a?(Hash)

    a_name = File.basename(File.dirname(a))
    b_name = File.basename(File.dirname(b))
    a_skills = resolved_skill_paths(a, a_data).to_set
    b_skills = resolved_skill_paths(b, b_data).to_set

    (a_skills & b_skills).sort.each do |skill_abs|
      declared = conflict_declares?(a, a_data, skill_abs, b_name) ||
                 conflict_declares?(b, b_data, skill_abs, a_name)
      next if declared

      display = skill_abs.delete_prefix("#{ROOT}/")
      errors << "#{a.delete_prefix("#{ROOT}/")} and #{b.delete_prefix("#{ROOT}/")}: undeclared overlap on included skill #{display.inspect}; declare it in the conflicts field of one of the two manifests"
    end
  end
  errors
end

begin
  schema = JSON.parse(File.read(SCHEMA_PATH))
  unless schema.is_a?(Hash) && schema["title"] == "agent-skills bundle manifest v1"
    warn "#{SCHEMA_PATH.delete_prefix("#{ROOT}/")} is not the expected bundle-manifest v1 schema"
    exit 1
  end
rescue JSON::ParserError => e
  warn "#{SCHEMA_PATH.delete_prefix("#{ROOT}/")} is invalid JSON: #{e.message.lines.first.strip}"
  exit 1
rescue Errno::ENOENT
  warn "#{SCHEMA_PATH.delete_prefix("#{ROOT}/")} is missing"
  exit 1
end

manifests = manifest_paths
errors = manifests.flat_map { |manifest| errors_for(manifest) }
errors.concat(overlap_errors(manifests))

if errors.empty?
  puts "Validated #{manifests.length} bundle manifest(s)."
else
  warn errors.join("\n")
  exit 1
end
