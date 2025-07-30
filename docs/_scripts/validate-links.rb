#!/usr/bin/env ruby
# Link validation script for Jekyll documentation

require 'yaml'
require 'find'

class LinkValidator
  def initialize(docs_dir = 'docs')
    @docs_dir = docs_dir
    @pages = []
    @errors = []
    @warnings = []
  end

  def validate
    puts "Validating documentation links..."
    
    load_pages
    check_internal_links
    check_cross_references
    check_navigation_links
    
    report_results
  end

  private

  def load_pages
    Find.find(@docs_dir) do |path|
      next unless path.end_with?('.md', '.html')
      next if path.include?('/_site/')
      
      content = File.read(path)
      
      # Extract front matter
      if content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
        front_matter = YAML.load($1) rescue {}
        body = content.sub(/\A---\s*\n.*?\n---\s*\n/m, '')
      else
        front_matter = {}
        body = content
      end
      
      @pages << {
        path: path,
        front_matter: front_matter,
        body: body,
        title: front_matter['title'],
        url: path_to_url(path)
      }
    end
    
    puts "Loaded #{@pages.length} pages"
  end

  def check_internal_links
    puts "Checking internal links..."
    
    @pages.each do |page|
      # Find markdown links [text](url)
      page[:body].scan(/\[([^\]]+)\]\(([^)]+)\)/) do |text, url|
        next if url.start_with?('http', 'mailto:', '#')
        
        # Convert relative URL to absolute path
        target_url = resolve_url(url, page[:url])
        target_page = @pages.find { |p| p[:url] == target_url }
        
        unless target_page
          @errors << {
            type: 'broken_link',
            page: page[:path],
            link_text: text,
            target_url: url,
            message: "Broken internal link: #{url}"
          }
        end
      end
    end
  end

  def check_cross_references
    puts "Checking cross-references..."
    
    @pages.each do |page|
      # Find xref tags {% xref ... %}
      page[:body].scan(/\{\%\s*xref\s+([^%]+)\s*\%\}/) do |ref|
        ref_text = ref[0].strip
        
        # Parse reference
        if ref_text.include?(':')
          type, name = ref_text.split(':', 2)
          type = type.strip
          name = name.strip
        else
          type = 'auto'
          name = ref_text
        end
        
        # Check if referenced page exists
        unless find_referenced_page(type, name)
          @warnings << {
            type: 'missing_xref',
            page: page[:path],
            ref_type: type,
            ref_name: name,
            message: "Cross-reference target not found: #{ref_text}"
          }
        end
      end
    end
  end

  def check_navigation_links
    puts "Checking navigation links..."
    
    config_path = File.join(@docs_dir, '_config.yml')
    return unless File.exist?(config_path)
    
    config = YAML.load_file(config_path)
    navigation = config['navigation'] || []
    
    navigation.each do |nav_item|
      check_nav_item(nav_item)
      
      if nav_item['children']
        nav_item['children'].each { |child| check_nav_item(child) }
      end
    end
  end

  def check_nav_item(item)
    url = item['url']
    return if url.start_with?('http')
    
    target_page = @pages.find { |p| p[:url] == url }
    unless target_page
      @errors << {
        type: 'broken_nav_link',
        nav_title: item['title'],
        target_url: url,
        message: "Navigation link points to non-existent page: #{url}"
      }
    end
  end

  def find_referenced_page(type, name)
    case type
    when 'function'
      @pages.find { |p| p[:front_matter]['function_name'] == name }
    when 'module'
      @pages.find { |p| p[:front_matter]['layout'] == 'reference' && p[:title] == name }
    when 'class'
      @pages.find { |p| p[:front_matter]['class_name'] == name }
    when 'tutorial'
      @pages.find { |p| p[:front_matter]['layout'] == 'tutorial' && p[:title] == name }
    when 'concept'
      @pages.find { |p| p[:path].include?('core-concepts') && p[:title] == name }
    when 'example'
      @pages.find { |p| p[:path].include?('examples') && p[:title] == name }
    when 'auto'
      find_referenced_page('function', name) ||
      find_referenced_page('module', name) ||
      find_referenced_page('class', name) ||
      find_referenced_page('tutorial', name) ||
      find_referenced_page('concept', name) ||
      find_referenced_page('example', name) ||
      @pages.find { |p| p[:title] == name }
    else
      @pages.find { |p| p[:title] == name }
    end
  end

  def path_to_url(path)
    url = path.sub(@docs_dir, '')
    url = url.sub(/\.md$/, '/')
    url = url.sub(/\/index\/$/, '/')
    url = '/' if url.empty?
    url
  end

  def resolve_url(url, base_url)
    return url if url.start_with?('/')
    
    base_parts = base_url.split('/').reject(&:empty?)
    url_parts = url.split('/').reject(&:empty?)
    
    # Handle relative paths
    url_parts.each do |part|
      if part == '..'
        base_parts.pop
      elsif part != '.'
        base_parts << part
      end
    end
    
    '/' + base_parts.join('/')
  end

  def report_results
    puts "\n" + "="*50
    puts "VALIDATION RESULTS"
    puts "="*50
    
    if @errors.empty? && @warnings.empty?
      puts "✅ All links are valid!"
      return
    end
    
    unless @errors.empty?
      puts "\n❌ ERRORS (#{@errors.length}):"
      @errors.each_with_index do |error, i|
        puts "\n#{i+1}. #{error[:message]}"
        puts "   File: #{error[:page]}" if error[:page]
        puts "   Link: #{error[:link_text]} -> #{error[:target_url]}" if error[:link_text]
      end
    end
    
    unless @warnings.empty?
      puts "\n⚠️  WARNINGS (#{@warnings.length}):"
      @warnings.each_with_index do |warning, i|
        puts "\n#{i+1}. #{warning[:message]}"
        puts "   File: #{warning[:page]}" if warning[:page]
      end
    end
    
    puts "\nSummary:"
    puts "  Pages checked: #{@pages.length}"
    puts "  Errors: #{@errors.length}"
    puts "  Warnings: #{@warnings.length}"
    
    exit(1) unless @errors.empty?
  end
end

# Run validation if script is called directly
if __FILE__ == $0
  validator = LinkValidator.new(ARGV[0] || 'docs')
  validator.validate
end