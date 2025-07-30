// Table of Contents generation
(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    generateTableOfContents();
  });

  function generateTableOfContents() {
    let tocContainer = document.getElementById('toc-content');
    if (!tocContainer) return;

    let headings = document.querySelectorAll('.content h2, .content h3, .content h4');
    if (headings.length === 0) {
      // Hide TOC if no headings found
      let tocAside = document.querySelector('.toc');
      if (tocAside) {
        tocAside.style.display = 'none';
      }
      return;
    }

    let tocHTML = '<ul>';
    let currentLevel = 2;

    headings.forEach(function(heading, index) {
      let level = parseInt(heading.tagName.charAt(1));
      let id = heading.id || generateId(heading.textContent);
      let text = heading.textContent;

      // Ensure heading has an ID for linking
      if (!heading.id) {
        heading.id = id;
      }

      // Handle nesting
      if (level > currentLevel) {
        tocHTML += '<ul>';
      } else if (level < currentLevel) {
        for (let i = level; i < currentLevel; i++) {
          tocHTML += '</ul>';
        }
      }

      tocHTML += `<li><a href="#${id}">${text}</a></li>`;
      currentLevel = level;
    });

    // Close any remaining open lists
    for (let i = 2; i < currentLevel; i++) {
      tocHTML += '</ul>';
    }
    tocHTML += '</ul>';

    tocContainer.innerHTML = tocHTML;

    // Add smooth scrolling and active link highlighting
    setupTocInteractions();
  }

  function generateId(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '') // Remove special characters
      .replace(/\s+/g, '-')     // Replace spaces with hyphens
      .replace(/--+/g, '-')     // Replace multiple hyphens with single
      .trim();
  }

  function setupTocInteractions() {
    let tocLinks = document.querySelectorAll('.toc a');
    
    // Add smooth scrolling
    tocLinks.forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        let targetId = this.getAttribute('href').substring(1);
        let targetElement = document.getElementById(targetId);
        
        if (targetElement) {
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Highlight active section on scroll
    window.addEventListener('scroll', throttle(updateActiveLink, 100));
  }

  function updateActiveLink() {
    let headings = document.querySelectorAll('.content h2, .content h3, .content h4');
    let tocLinks = document.querySelectorAll('.toc a');
    let scrollPosition = window.scrollY + 100; // Offset for better UX

    let activeHeading = null;
    
    headings.forEach(function(heading) {
      if (heading.offsetTop <= scrollPosition) {
        activeHeading = heading;
      }
    });

    // Remove active class from all links
    tocLinks.forEach(function(link) {
      link.classList.remove('active');
    });

    // Add active class to current section
    if (activeHeading) {
      let activeLink = document.querySelector(`.toc a[href="#${activeHeading.id}"]`);
      if (activeLink) {
        activeLink.classList.add('active');
      }
    }
  }

  function throttle(func, limit) {
    let inThrottle;
    return function() {
      let args = arguments;
      let context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
})();