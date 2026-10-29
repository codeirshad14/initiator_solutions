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
   * Clients Slider
   */
  new Swiper('.clients-slider', {
    speed: 400,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    },
    breakpoints: {
      320: {
        slidesPerView: 2,
        spaceBetween: 40
      },
      480: {
        slidesPerView: 3,
        spaceBetween: 60
      },
      640: {
        slidesPerView: 4,
        spaceBetween: 80
      },
      992: {
        slidesPerView: 6,
        spaceBetween: 120
      }
    }
  });

  /**
   * Porfolio isotope and filter
   */
  window.addEventListener('load', () => {
    let portfolioContainer = select('.portfolio-container');
    if (portfolioContainer) {
      let portfolioIsotope = new Isotope(portfolioContainer, {
        itemSelector: '.portfolio-item',
        layoutMode: 'fitRows'
      });

      let portfolioFilters = select('#portfolio-flters li', true);

      on('click', '#portfolio-flters li', function(e) {
        e.preventDefault();
        portfolioFilters.forEach(function(el) {
          el.classList.remove('filter-active');
        });
        this.classList.add('filter-active');

        portfolioIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        aos_init();
      }, true);
    }

  });

  /**
   * Initiate portfolio lightbox 
   */
  const portfolioLightbox = GLightbox({
    selector: '.portfokio-lightbox'
  });

  /**
   * Portfolio details slider
   */
  new Swiper('.portfolio-details-slider', {
    speed: 400,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

  /**
   * Testimonials slider
   */
  new Swiper('.testimonials-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    },
    breakpoints: {
      320: {
        slidesPerView: 1,
        spaceBetween: 40
      },

      1200: {
        slidesPerView: 3,
      }
    }
  });

  /**
   * Animation on scroll
   */
  function aos_init() {
    AOS.init({
      duration: 1000,
      easing: "ease-in-out",
      once: true,
      mirror: false
    });
  }
  // Start when the HTML is ready, not on window "load": waiting for every image,
  // the map and the fonts kept the hero (and all data-aos content) invisible.
  // Positions are re-measured once images have loaded.
  aos_init();
  window.addEventListener('load', () => {
    AOS.refresh();
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
   * Typing animation for headings marked data-typing (home hero), left to right.
   * The full text stays in the HTML for search engines and no-JS visitors. Letters
   * not typed yet stay in place but invisible, so the heading always has its final
   * size and the page never jumps. Reduced-motion visitors see the full text.
   */
  const typeHeading = (heading) => {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const originalHtml = heading.innerHTML
    const parts = []
    const splitTextNodes = (parent) => {
      [...parent.childNodes].forEach((child) => {
        if (child.nodeType === Node.ELEMENT_NODE) {
          splitTextNodes(child)
        } else if (child.nodeType === Node.TEXT_NODE && child.textContent) {
          const typed = document.createTextNode('')
          const rest = document.createElement('span')
          rest.className = 'typing-rest'
          rest.textContent = child.textContent
          child.replaceWith(typed, rest)
          parts.push({ typed, rest, text: rest.textContent })
        }
      })
    }
    heading.setAttribute('aria-label', heading.textContent.trim())
    splitTextNodes(heading)
    const caret = document.createElement('span')
    caret.className = 'typing-caret'
    caret.setAttribute('aria-hidden', 'true')

    let partIndex = 0
    let charCount = 0
    const typeNext = () => {
      if (partIndex >= parts.length) {
        heading.innerHTML = originalHtml
        heading.removeAttribute('aria-label')
        return
      }
      const { typed, rest, text } = parts[partIndex]
      charCount += 1
      typed.textContent = text.slice(0, charCount)
      rest.textContent = text.slice(charCount)
      rest.before(caret)
      if (charCount >= text.length) {
        partIndex += 1
        charCount = 0
      }
      setTimeout(typeNext, 55)
    }
    setTimeout(typeNext, 300)
  }
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

  // Start once the fonts are ready (not after every image on the page), so the
  // typing runs during the AOS fade-in.
  const startTyping = () => select('[data-typing]', true).forEach(typeHeading)
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(startTyping)
  } else {
    window.addEventListener('load', startTyping)
  }

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
