# Cross-reference plugin for Jekyll
# Allows easy linking between documentation pages using simple syntax

module Jekyll
  class CrossReferenceTag < Liquid::Tag
    def initialize(tag_name, markup, tokens)
      super
      @markup = markup.strip
    end

    def render(context)
      site = context.registers[:site]
      page = context.registers[:page]
      
      # Parse the markup: type:name or just name
      if @markup.include?(':')
        type, name = @markup.split(':', 2)
        type = type.strip
        name = name.strip
      else
        name = @markup
        type = 'auto' # Auto-detect type
      end

      # Find the referenced page
      referenced_page = find_page(site, type, name)
      
      if referenced_page
        url = referenced_page['url']
        title = referenced_page['title'] || name
        css_class = "cross-ref cross-ref-#{type}"
        
        case type
        when 'function'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Function: #{name}\"><code>#{name}()</code></a>"
        when 'module'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Module: #{name}\">#{title}</a>"
        when 'class'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Class: #{name}\">#{title}</a>"
        when 'tutorial'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Tutorial: #{title}\">#{title}</a>"
        when 'concept'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Concept: #{title}\">#{title}</a>"
        when 'example'
          "<a href=\"#{url}\" class=\"#{css_class}\" title=\"Example: #{title}\">#{title}</a>"
        else
          "<a href=\"#{url}\" class=\"cross-ref\" title=\"#{title}\">#{title}</a>"
        end
      else
        # Page not found - return a placeholder
        "<span class=\"cross-ref-missing\" title=\"Documentation not yet available\">#{name}</span>"
      end
    end

    private

    def find_page(site, type, name)
      case type
      when 'function'
        site.pages.find { |p| p.data['function_name'] == name }
      when 'module'
        site.pages.find { |p| p.data['layout'] == 'reference' && p.data['title'] == name }
      when 'class'
        site.pages.find { |p| p.data['class_name'] == name }
      when 'tutorial'
        site.pages.find { |p| p.data['layout'] == 'tutorial' && p.data['title'] == name }
      when 'concept'
        site.pages.find { |p| p.path.include?('core-concepts') && p.data['title'] == name }
      when 'example'
        site.pages.find { |p| p.path.include?('examples') && p.data['title'] == name }
      when 'auto'
        # Try to auto-detect the type
        find_page(site, 'function', name) ||
        find_page(site, 'module', name) ||
        find_page(site, 'class', name) ||
        find_page(site, 'tutorial', name) ||
        find_page(site, 'concept', name) ||
        find_page(site, 'example', name) ||
        site.pages.find { |p| p.data['title'] == name }
      else
        site.pages.find { |p| p.data['title'] == name }
      end
    end
  end

  # Register the tag
  Liquid::Template.register_tag('xref', CrossReferenceTag)
end

# Usage examples:
# {% xref function:char_to_room %}
# {% xref module:mudsys %}
# {% xref tutorial:Creating NPCs %}
# {% xref concept:Auxiliary Data %}
# {% xref Getting Started %} (auto-detect)