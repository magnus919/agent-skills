#!/usr/bin/env ruby
# frozen_string_literal: true

# Scans references/*.md files for stale prose backtick references to
# nonexistent files (the #205 RICE-reference class of bug). The link-resolution
# pass over SKILL.md bodies cannot see these: a backtick token
# (`` `rice-framework.md` ``) is inline code, not a markdown link, and
# reference files were previously not scanned at all. Required by
# scripts/validate-skills.rb so the check runs on every PR and push.
module ReferenceFileScan
  # Backtick-quoted .md tokens that are NOT references to files that should
  # exist inside this repository: prose conventions and doc-type names,
  # illustrative examples, external repositories, runtime-generated paths, and
  # change-ledger removal records. Kept explicit (with a reason per entry) so
  # new skills cannot silently reintroduce stale file references, and so the
  # real reference checks stay strict for everything not listed here.
  NON_FILE_PATTERNS = [
    # Generic / doc-type names used as prose concepts, not specific repo files
    # (includes neckbeard delivery-packet field names and packaging doc names).
    %r{\A(?:README|SKILL|index|log|_index|00-index|SPEC|DELIVERY-SPEC|V2-SPEC|TASK-PLAN|VERIFICATION-PLAN|VERIFICATION|REVIEW|CHANGE-CONTRACT|ARCHITECTURE-DELTA|DESIGN|DEVELOPMENT|REFERENCE|FORMS|CLAUDE|CHANGELOG|CONFIG|versions|DOCKER|NIXOS|SECURITY-AUDIT|EVIDENCE-LEDGER|campaign|finance|legal|instructions)\.md\z},
    # Numbered ADR / doc naming examples ("Good:", "Bad:", placeholders) in
    # adr-authoring/references/adr-format.md and project-setup-guide.md.
    %r{\A(?:\d{3}-|PLAT-\d{3}-|NNNN-)},
    # External-repository or runtime-generated paths, not this catalog:
    # docs/adr/ (GroktoCrawl convention), docker/ and adr/ (upstream projects),
    # content/ and post.*.md (Hugo examples), tables/ (OKF spec concept),
    # .agents/ (VS Code example), 0N- and ../researcher- (artifact-pyramid
    # runtime layout), suganthan.com/ and references/*.md (URL / glob).
    %r{\A(?:docs/adr/|docker/|adr/|content/|tables/|\.agents/|0\d-|\.\./researcher-|suganthan\.com/|references/\*\.md)},
    # Hugo multilingual example filenames.
    %r{\Apost\.[a-z]{2}\.md\z},
    # Illustrative loading-guide example quoted in
    # agent-skills/references/best-practices.md.
    %r{\Areferences/api-errors\.md\z},
    # Pre-existing reference to the hugo-contrib skill, which is not part of
    # this catalog (opensource-contributions/references/phase-0-before-you-start.md).
    %r{\Areferences/finding-bugfix-candidates\.md\z},
    # Pre-existing external-archive reference
    # (color-management/references/dcraw-pipeline.md points at a file from the
    # ninedegreesbelow.com archive).
    %r{\Areferences/srgb-versus-photographic-colors\.md\z},
    # Shell-command or markup fragments captured by the backtick scan.
    /\s/,
    /\|/,
    /[<>]/,
    %r{\A/},
    %r{://},
    # Domain-qualified paths such as suganthan.com/okf/index.md.
    %r{\A[a-z0-9-]+(?:\.[a-z0-9-]+)+/},
  ].freeze

  # A line documenting that a file was removed (source-index change ledgers)
  # records history rather than pointing at a live file.
  REMOVAL_MARKER = /\bremoved\b/i

  module_function

  # Returns error strings for stale prose backtick references to nonexistent
  # files found in <root>/<skill_rel>/references/*.md.
  def stale_reference_errors(root, skill_rel)
    errors = []
    ref_dir = File.join(root, skill_rel, "references")
    Dir.glob("#{ref_dir}/*.md").sort.each do |ref|
      ref_rel = ref.delete_prefix("#{root}/")
      File.readlines(ref).each_with_index do |line, idx|
        next if line.match?(REMOVAL_MARKER)

        siblings = named_skills(line)
        line.scan(/`([^`]+\.md)`/).flatten.each do |token|
          token = token.strip
          next if token.empty? || non_file?(token)
          next if resolve_candidates(root, File.dirname(ref), File.dirname(File.dirname(ref)), token, siblings).any? { |path| file_exists_case_sensitive?(path) }

          errors << "#{ref_rel}:#{idx + 1}: stale prose backtick reference to nonexistent file `#{token}`"
        end
      end
    end
    errors
  end

  # Skill names named on a line, either in prose ("the X skill") or via a
  # relative SKILL.md link to a sibling skill.
  def named_skills(line)
    names = line.scan(/\b([a-z0-9-]+) skill/).flatten
    names += line.scan(%r{\.\./\.\.?/([a-z0-9-]+)/SKILL\.md}).flatten
    names.uniq
  end

  # Candidate absolute paths a token could legitimately resolve to: the
  # reference file's own directory, the skill root, the repository root, and
  # any existing sibling skill named on the same line.
  def resolve_candidates(root, ref_dir, skill_root, token, siblings)
    candidates = []
    if token.include?("/")
      candidates << File.expand_path(token, ref_dir)
      candidates << File.expand_path(token, skill_root)
      candidates << File.expand_path(token, root)
    else
      candidates << File.expand_path(token, ref_dir)
      candidates << File.expand_path(token, skill_root)
      candidates << File.expand_path(token, root)
    end
    siblings.each do |sibling|
      sibling_root = File.join(root, sibling)
      next unless File.directory?(sibling_root)

      if token.include?("/")
        candidates << File.expand_path(token, sibling_root)
      else
        candidates << File.expand_path(token, File.join(sibling_root, "references"))
        candidates << File.expand_path(token, sibling_root)
      end
    end
    candidates.uniq
  end

  def non_file?(token)
    NON_FILE_PATTERNS.any? { |pattern| token.match?(pattern) }
  end

  # Existence check that stays case-sensitive even on case-insensitive host
  # filesystems (e.g., default macOS APFS), so results match CI's Linux
  # runners. File.exist? alone resolves `EVIDENCE-LEDGER.md` to an existing
  # lowercase `evidence-ledger.md` on macOS but not on Linux.
  def file_exists_case_sensitive?(path)
    return false unless File.exist?(path)

    Dir.children(File.dirname(path)).include?(File.basename(path))
  end
end
