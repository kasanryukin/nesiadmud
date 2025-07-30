# NakedMud Python 3 Documentation

This is the documentation site for the NakedMud Python 3 library implementation, built with Jekyll and the just-the-docs theme for ReadTheDocs-compatible styling.

## Local Development

To run the site locally for testing:

```bash
# Install dependencies (first time only)
bundle install

# Serve the site locally
bundle exec jekyll serve

# Or with live reload
bundle exec jekyll serve --livereload
```

The site will be available at `http://localhost:4000`.

## GitHub Pages Deployment

This site is configured to deploy automatically to GitHub Pages. Simply push changes to the repository and GitHub will build and deploy the site.

## Structure

- `docs/` - Main documentation directory
  - `_layouts/` - Custom page layouts
  - `_includes/` - Reusable components
  - `_sass/` - Custom SCSS styling
  - `_plugins/` - Jekyll plugins
  - `_scripts/` - Utility scripts
  - `_templates/` - Content templates
  - `assets/` - CSS, JS, and other assets
  - `getting-started/` - Getting started guides
  - `core-concepts/` - Core concept documentation
  - `reference/` - API reference documentation
  - `tutorials/` - Step-by-step tutorials
  - `examples/` - Code examples and samples

## Content Creation

### Using Templates

Template files are available in `_templates/` for creating new content:

- `function-template.md` - For API function documentation
- `tutorial-template.md` - For tutorial pages
- `reference-template.md` - For module reference pages

### Cross-References

Use the `{% xref %}` tag to create cross-references between pages:

```markdown
{% xref function:char_to_room %}
{% xref module:mudsys %}
{% xref tutorial:Creating NPCs %}
{% xref concept:Auxiliary Data %}
```

### Navigation

The site uses just-the-docs automatic navigation based on front matter:

```yaml
---
layout: default
title: "Page Title"
nav_order: 1
parent: "Parent Page"
has_children: true  # For parent pages
---
```

## Link Validation

Run the link validation script to check for broken links:

```bash
ruby _scripts/validate-links.rb
```

## Theme

This site uses the [just-the-docs](https://just-the-docs.github.io/just-the-docs/) theme with custom styling to match ReadTheDocs appearance.