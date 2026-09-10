<!-- prompts/single_page_app.md -->
# Single Page App (SPA) — Premium UI Prompt Template

## Role
You are building a premium, motion-rich Single Page Application. All components must feel alive with spring physics, scroll reveals, and branded micro-interactions.

## Mandatory Elements

### Loader Gate Pattern
```js
// Gate all above-fold reveals on loader completion
let ready = false;

// After loader exit:
ready = true;
startScroll();
playHeroReveals();  // Only now

// For scroll reveals: gate on (ready && inViewport)
```

### Scroll-driven Reveals
```css
/* Initial state — hidden */
.reveal { opacity: 0; transform: translateY(32px); }

/* Revealed state */
.reveal.revealed {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.9s cubic-bezier(.22,1,.36,1),
              transform 0.9s cubic-bezier(.22,1,.36,1);
}

/* Stagger via delay */
.reveal:nth-child(2) { transition-delay: 90ms; }
.reveal:nth-child(3) { transition-delay: 180ms; }
```

### Spring Physics Hierarchy
```
UI Layer          Spring Config       CSS Equivalent              Duration
─────────────────────────────────────────────────────────────────────────
Hover (fast)      {320, 18}           cubic-bezier(.2,.8,.2,1)   350ms
Reveal (smooth)   {210, 26}           cubic-bezier(.22,1,.36,1)  700ms
Card lift         {260, 22}           cubic-bezier(.25,1,.5,1)   500ms
Modal enter       {260, 30}           cubic-bezier(.34,1.56,.64,1) 600ms
Service fill      {240, 26}           cubic-bezier(.3,.7,.3,1)   400ms
Loader exit       {220, 30}           cubic-bezier(.22,1,.36,1)  700ms
Carousel swap     {300, 28}           cubic-bezier(.25,1,.5,1)   500ms
```

### Count-up Numbers (Stats sections)
```js
// Scroll-progress driven, not just IntersectionObserver
function countUp(element, target) {
  const observer = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    let start = null;
    const DURATION = 1500;
    function step(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / DURATION, 1);
      const eased = 1 - Math.pow(1 - progress, 3);  // easeOutCubic
      element.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
    observer.disconnect();
  }, { threshold: 0.3 });
  observer.observe(element);
}
```

### Live Clock Pattern
```js
// Update every 1s, no leading zero on hour
function updateClock(el) {
  const now = new Date();
  const h = now.getHours() % 12 || 12;
  const m = String(now.getMinutes()).padStart(2, '0');
  const ampm = now.getHours() >= 12 ? 'pm' : 'am';
  el.textContent = `${h}:${m}${ampm}`;
}
setInterval(() => updateClock(clockEl), 1000);
updateClock(clockEl);  // immediate
```

### Hero Canvas Effect (Signature Differentiator)
```js
// Always check reduced motion first
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  // Skip canvas — show only static base image
  return;
}

// LiquidReveal pattern:
// 1. Base image = always visible (beforeSrc)
// 2. Canvas overlay = painted by cursor trail (afterSrc)
// 3. brushRadius = 143px, decay = 0.016/frame, dpr = min(dpr, 2)
// 4. Offscreen cover canvas for source-in masking
// 5. Idle > 120 frames → clearRect (hard reset)
```

## MCP Tools Order
```
1. generate_ui_prompt("saas", "description")   → get structured spec
2. generate_color_palette(accent, "analogous") → color tokens
3. check_wcag_contrast(fg, bg)                 → verify contrast
4. calc_type_scale(16, 1.25)                   → font sizes
5. calc_spacing_scale(8)                        → spacing
6. calc_z_stack([...])                          → z-index system
7. calc_elevation_shadow(2)                     → card shadow
8. spec_button("dark", "md", true)             → button spec
9. spec_loader("branded", 1300)                → loader spec
10. review_ui_quality(
      css_snippets=[...],
      no_adaptive_grid=False,
      loader_missing=False,
    )                                           → final check
```

## Quality Gates (Must Pass Before Shipping)
- [ ] `review_ui_quality` score >= 85 (grade B+)
- [ ] All transitions use spring cubic-bezier (no `ease`/`linear`)
- [ ] Loader has branded counter (000→100)
- [ ] Hero has canvas/interactive element
- [ ] Modal/overlay locks scroll
- [ ] All z-index values from `calc_z_stack` system
- [ ] Font sizes from `calc_type_scale` (no arbitrary px)
- [ ] WCAG AA contrast on all text pairs
- [ ] `prefers-reduced-motion` disables all animations
- [ ] Brand watermark on hero and/or footer
