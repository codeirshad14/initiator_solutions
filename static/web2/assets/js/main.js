/**
* Template Name: FlexStart - v1.7.0
* Template URL: https://bootstrapmade.com/flexstart-bootstrap-startup-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    if (!el) {
      return all ? [] : null
    }
    el = el.trim()
    if (!el) {
      return all ? [] : null
    }
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      let selected = select(el, all)
      if (selected) {
        selected.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Scrolls to an element with header offset
   */
  const scrollto = (el) => {
    let header = select('#header')
    let offset = header.offsetHeight

    if (!header.classList.contains('header-scrolled')) {
      offset -= 10
    }

    let elementPos = select(el).offsetTop
    window.scrollTo({
      top: elementPos - offset,
      behavior: 'smooth'
    })
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    let navbar = select('#navbar')
    if (!navbar) return
    navbar.classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    let navbar = select('#navbar')
    if (navbar && navbar.classList.contains('navbar-mobile')) {
      e.preventDefault()
      if (this.nextElementSibling) {
        this.nextElementSibling.classList.toggle('dropdown-active')
      }
    }
  }, true)

  /**
   * Scrool with ofset on links with a class name .scrollto
   */
  on('click', '.scrollto', function(e) {
    if (!this.hash) {
      return
    }
    if (select(this.hash)) {
      e.preventDefault()

      let navbar = select('#navbar')
      if (navbar && navbar.classList.contains('navbar-mobile')) {
        navbar.classList.remove('navbar-mobile')
        let navbarToggle = select('.mobile-nav-toggle')
        if (navbarToggle) {
          navbarToggle.classList.add('bi-list')
          navbarToggle.classList.remove('bi-x')
        }
      }
      scrollto(this.hash)
    }
  }, true)

  /**
   * Scroll with ofset on page load with hash links in the url
   */
  window.addEventListener('load', () => {
    if (window.location.hash) {
      if (select(window.location.hash)) {
        scrollto(window.location.hash)
      }
    }
  });

  /**
   * Animation on scroll: started inline in wbase.html right after aos.js, so
   * content never waits for this file. Positions are re-measured once images load.
   */
  window.addEventListener('load', () => {
    if (window.AOS) AOS.refresh();
  });

  /**
   * Replace broken content images with the standard no-image placeholder.
   */
  const renderNoImagePlaceholder = (img) => {
    if (!img || img.dataset.noImageHandled === 'true') return
    if (img.classList.contains('site-logo-mark') || img.classList.contains('footer-logo-mark')) return

    img.dataset.noImageHandled = 'true'
    const placeholder = document.createElement('div')
    placeholder.className = `no-image-placeholder no-image-generated ${img.dataset.placeholderClass || ''}`.trim()
    placeholder.setAttribute('role', 'img')
    placeholder.setAttribute('aria-label', img.alt || 'No image available')
    placeholder.innerHTML = '<i class="bi bi-image"></i><span>No Image</span>'

    const rect = img.getBoundingClientRect()
    if (rect.height > 0) {
      placeholder.style.minHeight = `${Math.round(rect.height)}px`
    }

    img.replaceWith(placeholder)
  }

  window.addEventListener('error', (event) => {
    const target = event.target
    if (target && target.tagName === 'IMG') {
      renderNoImagePlaceholder(target)
    }
  }, true)

  /**
   * Swipeable group filters on phones: scroll the selected group into view.
   */
  window.addEventListener('load', () => {
    select('.product-filter, .service-filter, .module-filter', true).forEach((filter) => {
      const active = filter.querySelector('.btn-primary')
      if (active && filter.scrollWidth > filter.clientWidth) {
        filter.scrollLeft = active.offsetLeft - (filter.clientWidth - active.offsetWidth) / 2
      }
    })
  })

  /**
   * Analytics: send enquiries, phone, WhatsApp and email clicks as GA4 lead
   * events. Does nothing unless GA4 or GTM is set in Site SEO Settings.
   */
  const trackEvent = (name, method) => {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, { method: method })
    } else if (Array.isArray(window.dataLayer)) {
      window.dataLayer.push({ event: name, method: method })
    }
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest ? event.target.closest('a[href]') : null
    if (!link) return
    const href = link.getAttribute('href') || ''
    if (href.startsWith('tel:')) {
      trackEvent('generate_lead', 'phone')
    } else if (href.includes('wa.me/') || href.includes('api.whatsapp.com')) {
      trackEvent('generate_lead', 'whatsapp')
    } else if (href.startsWith('mailto:')) {
      trackEvent('generate_lead', 'email')
    }
  })

  document.addEventListener('submit', (event) => {
    const action = event.target.getAttribute('action') || ''
    if (action.includes('contact_email')) {
      trackEvent('generate_lead', 'enquiry_form')
    } else if (action.includes('news_letter')) {
      trackEvent('sign_up', 'newsletter')
    }
  })

})();
