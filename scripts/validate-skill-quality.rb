#!/usr/bin/env ruby
# frozen_string_literal: true

require "optparse"
require "open3"
require "pathname"
require "set"
require "yaml"

class SkillQualityValidator
  IMPERATIVE_VERBS = %w[
    add administer analyze apply assess audit automate author backup browse build calculate
    capture chain check clean compare configure connect control convert create debug define
    deploy design diagnose discover document draft edit evaluate export extract fetch find
    fix flash format generate guide identify implement import ingest inspect install interact
    investigate load maintain make manage migrate model monitor operate optimize organize parse
    plan play prepare process publish query read refactor release remove render repair research
    resolve restore review reverse-engineer route run scan scaffold scrape search secure select
    send set simulate start stop structure summarize sync teach test track train transform
    translate troubleshoot update use validate verify visualize write
  ].to_set.freeze

  DESCRIPTION_BOUNDARY_PATTERNS = [
    /\bdo not use(?: this skill)? for\s+[`*_"']*[[:alnum:]]/i,
    /\bnot for\s+[`*_"']*[[:alnum:]]/i,
    /\bwhen not to use\s+[`*_"']*[[:alnum:]]/i,
    /(?:\A|[.!?;:]\s+)unlike\s+[`*_"']*[[:alnum:]]/i,
    /(?:\A|[.!?;:]\s+)distinct from\s+[`*_"']*[[:alnum:]]/i
  ].freeze
  BOUNDARY_HEADING = /^\#{1,6}\s+When not to use\s*\#*\s*$/i
  NO_OP_PATTERNS = {
    "write clear or clean code" => /\bwrite\s+(?:clear|clean)\s+code\b/i,
    "follow best practices" => /\bfollow\s+best\s+practices\b/i,
    "handle errors appropriately or gracefully" => /\bhandle\s+errors\s+(?:appropriately|gracefully)\b/i,
    "ensure high quality" => /\bensure\s+high\s+quality\b/i,
    "make it easy to read" => /\bmake\s+it\s+easy\s+to\s+read\b/i,
    "write maintainable code" => /\bwrite\s+maintainable\s+code\b/i
  }.freeze

  Finding = Struct.new(:severity, :path, :line, :message)

  def validate(path, relative: path.to_s)
    text = File.read(path)
    match = text.match(/\A---\r?\n(.*?)\r?\n---\r?\n/m)
    return [Finding.new(:error, relative, 1, "missing YAML frontmatter")] unless match

    begin
      data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
    rescue Psych::Exception => error
      return [Finding.new(:error, relative, 1, "invalid YAML: #{error.message.lines.first.strip}")]
    end

    unless data.is_a?(Hash)
      return [Finding.new(:error, relative, 1, "frontmatter must be a mapping")]
    end

    description = data["description"]
    unless description.is_a?(String) && !description.strip.empty?
      return [Finding.new(:error, relative, 1, "description must be a non-empty string")]
    end

    body = text[match.end(0)..] || ""
    findings = []
    first_word = description.sub(/\ADeprecated:\s*/i, "").strip[/\A[[:alpha:]]+(?:-[[:alpha:]]+)?/]
    unless first_word && IMPERATIVE_VERBS.include?(first_word.downcase)
      findings << Finding.new(
        :error,
        relative,
        1,
        "description must start with a recognized imperative verb (found #{first_word.inspect})"
      )
    end

    unless negative_boundary?(description, body)
      findings << Finding.new(
        :error,
        relative,
        1,
        "description or body must define a negative boundary (for example, a 'When not to use' section)"
      )
    end

    body_start_line = text[0...match.end(0)].count("\n") + 1
    NO_OP_PATTERNS.each do |label, pattern|
      body.to_enum(:scan, pattern).each do
        match = Regexp.last_match
        findings << Finding.new(
          :warning,
          relative,
          body_start_line + body[0...match.begin(0)].count("\n"),
          "possible no-op instruction: #{label}"
        )
      end
    end

    findings
  rescue Errno::ENOENT => error
    [Finding.new(:error, relative, 1, error.message)]
  end

  private

  def negative_boundary?(description, body)
    return true if DESCRIPTION_BOUNDARY_PATTERNS.any? { |pattern| description.match?(pattern) }

    lines = body.lines
    lines.each_with_index.any? do |line, index|
      next false unless line.strip.match?(BOUNDARY_HEADING)

      section = lines[(index + 1)..].take_while { |candidate| !candidate.match?(/^\s*\#{1,6}\s+/) }
      substantive_boundary_section?(section)
    end
  end

  def substantive_boundary_section?(lines)
    in_comment = false
    fence = nil

    lines.any? do |candidate|
      content = strip_markdown_container(candidate.strip)

      if in_comment
        in_comment = false if content.include?("-->")
        next false
      end

      if content.start_with?("<!--")
        in_comment = !content.include?("-->")
        next false
      end

      if fence
        fence = nil if content.start_with?(fence)
        next false
      end

      if (marker = content[/\A(?:```|~~~)/])
        fence = marker
        next false
      end

      visible = content.gsub(/<!--.*?-->/, "").strip
      visible = visible.gsub(/\A[*_`~]+|[*_`~]+\z/, "").strip
      next false if visible.empty? || visible.match?(/\A[-*_]{3,}\z/)
      next false if visible.match?(/\A(?:TODO|TBD|TBA)\b/i)

      visible.scan(/[[:alnum:]]+/).length >= 3
    end
  end

  def strip_markdown_container(content)
    loop do
      stripped = content.sub(/\A>\s?/, "").sub(/\A(?:[-+*]|\d+[.)])\s+/, "").strip
      return content if stripped == content

      content = stripped
    end
  end
end

class ChangedSkillSelector
  ZERO_SHA = /\A0+\z/
  SKILL_PATHSPEC = ":(glob)**/SKILL.md"

  def initialize(root:, base: nil)
    @root = Pathname(root).expand_path
    @base = base
  end

  def paths
    selected = Set.new
    base = resolved_base

    if base == :all
      selected.merge(git_paths("ls-files", "-z", "--", SKILL_PATHSPEC))
    else
      selected.merge(git_paths("diff", "--name-only", "--diff-filter=ACMR", "-z", base, "HEAD", "--", SKILL_PATHSPEC))
    end

    selected.merge(git_paths("diff", "--name-only", "--diff-filter=ACMR", "-z", "--", SKILL_PATHSPEC))
    selected.merge(git_paths("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z", "--", SKILL_PATHSPEC))
    selected.merge(git_paths("ls-files", "--others", "--exclude-standard", "-z", "--", SKILL_PATHSPEC))

    selected
      .reject { |path| path.include?("agent-council/profiles/skills/") }
      .select { |path| (@root / path).file? }
      .sort
  end

  private

  def resolved_base
    requested = @base || ENV["SKILL_QUALITY_BASE"]
    return :all if requested&.match?(ZERO_SHA)

    requested ||= "origin/main"
    output, status = git_capture("rev-parse", "--verify", "#{requested}^{commit}")
    unless status.success? && !output.strip.empty?
      raise ArgumentError,
            "cannot establish a quality-check base from #{requested.inspect}; pass --base REF"
    end

    output.strip
  end

  def git_paths(*arguments)
    output, status = git_capture(*arguments)
    raise "git #{arguments.first} failed" unless status.success?

    output.split("\0").reject(&:empty?)
  end

  def git_capture(*arguments)
    stdout, stderr, status = Open3.capture3("git", *arguments, chdir: @root.to_s)
    warn stderr unless status.success? || stderr.empty?
    [stdout, status]
  end
end

class SkillQualityCheck
  def initialize(root:, base: nil, output: $stdout, error: $stderr)
    @root = Pathname(root).expand_path
    @base = base
    @output = output
    @error = error
  end

  def run
    paths = ChangedSkillSelector.new(root: @root, base: @base).paths
    if paths.empty?
      @output.puts "No changed SKILL.md files to quality-check."
      return 0
    end

    validator = SkillQualityValidator.new
    findings = paths.flat_map do |relative|
      validator.validate(@root / relative, relative: relative)
    end

    findings.sort_by { |finding| [finding.path, finding.line, finding.severity.to_s, finding.message] }.each do |finding|
      stream = finding.severity == :error ? @error : @output
      stream.puts "#{finding.severity.to_s.upcase} #{finding.path}:#{finding.line}: #{finding.message}"
    end

    error_count = findings.count { |finding| finding.severity == :error }
    warning_count = findings.count { |finding| finding.severity == :warning }
    summary = "Quality-checked #{paths.length} changed skill(s): #{error_count} error(s), #{warning_count} warning(s)."
    error_count.zero? ? @output.puts(summary) : @error.puts(summary)
    error_count.zero? ? 0 : 1
  rescue ArgumentError, RuntimeError => error
    @error.puts "Skill quality check failed: #{error.message}"
    1
  end
end

if $PROGRAM_NAME == __FILE__
  options = {}
  parser = OptionParser.new do |opts|
    opts.banner = "Usage: ruby scripts/validate-skill-quality.rb [--base REF]"
    opts.on("--base REF", "Compare committed SKILL.md changes with REF") { |ref| options[:base] = ref }
  end
  parser.parse!

  root = File.expand_path("..", __dir__)
  exit SkillQualityCheck.new(root: root, base: options[:base]).run
end
