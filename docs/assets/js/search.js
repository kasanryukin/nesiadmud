// Simple search functionality for Jekyll documentation
(function() {
  'use strict';

  let searchIndex = [];
  let searchInput = document.getElementById('search-input');
  let searchResults = document.getElementById('search-results');

  // Initialize search when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    if (searchInput && searchResults) {
      buildSearchIndex();
      setupSearchHandlers();
    }
  });

  function buildSearchIndex() {
    // Build search index from page content
    // This is a simplified version - in production you might want to use a more sophisticated search solution
    let pages = [
      {
        title: 'Home',
        url: '/',
        content: 'NakedMud Python 3 Documentation comprehensive guide mud builders wizards'
      },
      {
        title: 'Getting Started',
        url: '/getting-started/',
        content: 'getting started tutorial basics first steps python scripting'
      },
      {
        title: 'Core Concepts',
        url: '/core-concepts/',
        content: 'auxiliary data prototypes python integration security model'
      },
      {
        title: 'API Reference',
        url: '/reference/',
        content: 'efuns eobs sefuns modules functions classes documentation'
      },
      {
        title: 'Tutorials',
        url: '/tutorials/',
        content: 'tutorials step by step guides npcs rooms objects triggers'
      },
      {
        title: 'Examples',
        url: '/examples/',
        content: 'examples code samples basic advanced complete systems'
      }
    ];

    searchIndex = pages;
  }

  function setupSearchHandlers() {
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('focus', handleSearchFocus);
    document.addEventListener('click', handleDocumentClick);
  }

  function handleSearch(event) {
    let query = event.target.value.trim().toLowerCase();
    
    if (query.length < 2) {
      hideSearchResults();
      return;
    }

    let results = searchIndex.filter(page => {
      return page.title.toLowerCase().includes(query) || 
             page.content.toLowerCase().includes(query);
    });

    displaySearchResults(results, query);
  }

  function handleSearchFocus() {
    let query = searchInput.value.trim().toLowerCase();
    if (query.length >= 2) {
      handleSearch({ target: searchInput });
    }
  }

  function handleDocumentClick(event) {
    if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
      hideSearchResults();
    }
  }

  function displaySearchResults(results, query) {
    if (results.length === 0) {
      searchResults.innerHTML = '<div class="search-result">No results found</div>';
    } else {
      searchResults.innerHTML = results.map(result => {
        let excerpt = generateExcerpt(result.content, query);
        return `
          <div class="search-result" onclick="navigateToResult('${result.url}')">
            <div class="search-result-title">${highlightQuery(result.title, query)}</div>
            <div class="search-result-excerpt">${highlightQuery(excerpt, query)}</div>
          </div>
        `;
      }).join('');
    }
    
    searchResults.style.display = 'block';
  }

  function hideSearchResults() {
    searchResults.style.display = 'none';
  }

  function generateExcerpt(content, query) {
    let index = content.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) {
      return content.substring(0, 100) + '...';
    }
    
    let start = Math.max(0, index - 30);
    let end = Math.min(content.length, index + query.length + 30);
    let excerpt = content.substring(start, end);
    
    if (start > 0) excerpt = '...' + excerpt;
    if (end < content.length) excerpt = excerpt + '...';
    
    return excerpt;
  }

  function highlightQuery(text, query) {
    let regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
  }

  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Make navigateToResult available globally
  window.navigateToResult = function(url) {
    window.location.href = url;
  };
})();