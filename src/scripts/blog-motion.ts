// Scroll animation for the blog pages, in the same style as the home page:
// the page title and intro rise in on load, and cards and text blocks rise in as they scroll into view.
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduce) {
  gsap.registerPlugin(ScrollTrigger);

  // entrance: eyebrow, title, intro, chips, post meta
  const intro = gsap.utils.toArray<HTMLElement>(
    '.eyebrow, article h1, section h1, .lede, .chips, .back, .cat:not(.blog-grid .cat), article .fine'
  ).filter((el) => !el.closest('.blog-grid') && !el.closest('.more'));
  if (intro.length) {
    gsap.fromTo(intro, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 1, ease: 'power3.out', stagger: 0.12, delay: 0.1 });
  }

  // cards and text blocks reveal as they come into view
  const reveal = (els: HTMLElement[], stagger = 0.1) => {
    els.forEach((el, i) => {
      gsap.fromTo(
        el,
        { opacity: 0, y: 34 },
        {
          opacity: 1,
          y: 0,
          duration: 1,
          ease: 'power3.out',
          delay: (i % 2) * stagger,
          scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        }
      );
    });
  };
  reveal(gsap.utils.toArray<HTMLElement>('.blog-grid article'));
  reveal(gsap.utils.toArray<HTMLElement>('.post > *'), 0);
  reveal(gsap.utils.toArray<HTMLElement>('.post-cta, .more h2, .more__grid a'));

  window.addEventListener('load', () => ScrollTrigger.refresh());
}
