/*
 * PD 2027 — animations for the Prizes, Registration fee, FAQ and Footer sections
 * + the site-wide three-circle cursor. GSAP only (gsap, ScrollTrigger, SplitText, Observer).
 *
 * Every block looks for its own data-* hooks and quietly does nothing if they're
 * missing, so this file is safe to load on any page.
 * Everything respects prefers-reduced-motion.
 */
(function () {
  "use strict";
  if (!window.gsap) return;

  gsap.registerPlugin(ScrollTrigger, SplitText, Observer);

  var MOTION_OK = "(prefers-reduced-motion: no-preference)";
  var REDUCED = "(prefers-reduced-motion: reduce)";
  var prefersReduced = function () {
    return window.matchMedia(REDUCED).matches;
  };

  /* ------------------------------------------------------------------
   * 1. WAVE HEADINGS  [data-pd-wave]
   *    Figma: "Wave animation" (ref: Motion Text FX › Wave)
   *    Letters rise in one after another when the heading scrolls into
   *    view, then a gentle wave ripples through them every few seconds
   *    while the heading is on screen (and again on hover).
   * ------------------------------------------------------------------ */
  function initWaves() {
    document.querySelectorAll("[data-pd-wave]").forEach(function (el) {
      gsap.matchMedia().add(MOTION_OK, function () {
        var split = SplitText.create(el, { type: "words,chars", aria: "auto" });
        gsap.set(split.words, { display: "inline-block", whiteSpace: "nowrap" });
        gsap.set(split.chars, { display: "inline-block", willChange: "transform" });

        var wave = gsap.timeline({ paused: true, repeat: -1, repeatDelay: 2.2 });
        wave.to(split.chars, {
          keyframes: { y: [0, "-0.22em", 0], ease: "none" },
          duration: 0.7,
          ease: "sine.inOut",
          stagger: 0.045,
        });

        var intro = gsap.from(split.chars, {
          yPercent: 115,
          rotation: 8,
          opacity: 0,
          duration: 0.8,
          ease: "back.out(2)",
          stagger: 0.03,
          paused: true,
          onComplete: function () {
            if (st.isActive) wave.play(0);
          },
        });

        var st = ScrollTrigger.create({
          trigger: el,
          start: "top 88%",
          end: "bottom top",
          onEnter: function () { intro.play(); },
          onToggle: function (self) {
            if (!intro.progress() || intro.isActive()) return;
            self.isActive ? wave.play() : wave.pause();
          },
        });

        var replay = function () {
          if (intro.progress() === 1) wave.restart();
        };
        el.addEventListener("mouseenter", replay);

        return function () {
          el.removeEventListener("mouseenter", replay);
          split.revert();
        };
      });
    });
  }

  /* ------------------------------------------------------------------
   * 2. PRIZES — FAN CARD CAROUSEL  [data-pd-fan]
   *    Figma: "Fan card carousal animation" (ref: Fan Card Carousel)
   *    Cards sit on an arc. Click a side card, swipe/drag, or use the
   *    arrow keys to bring a card to the centre. Autoplays while visible,
   *    pauses on hover/focus.
   * ------------------------------------------------------------------ */
  // Offsets measured from Figma frame 3 (centre card = 604×779, side cards = 482×621 ≈ 0.8)
  var FAN = [
    { x: 0, y: 0, r: 0, s: 1 },
    { x: 474, y: 173, r: 20, s: 0.8 },
    { x: 1019, y: 451, r: 40, s: 0.8 },
    { x: 1450, y: 820, r: 60, s: 0.8 },
  ];
  function fanSlot(d) {
    var a = Math.min(Math.abs(d), 3);
    var sign = d < 0 ? -1 : 1;
    return {
      x: sign * FAN[a].x,
      y: FAN[a].y,
      rotation: sign * FAN[a].r,
      scale: FAN[a].s,
      zIndex: 20 - a * 5,
      autoAlpha: a > 2 ? 0 : 1,
    };
  }

  function initFan(root) {
    var stage = root.querySelector("[data-fan-stage]");
    var cards = gsap.utils.toArray(root.querySelectorAll("[data-fan-card]"));
    if (!stage || cards.length < 2) return;

    var n = cards.length;
    var start = cards.findIndex(function (c) { return c.hasAttribute("data-fan-start"); });
    var active = start < 0 ? 0 : start;
    var autoplay, lastDrag = 0, hovering = false, inView = false;

    // Scale the whole fan to the viewport (desktop: 1440px design, mobile: tighter so the centre card stays big)
    function fit() {
      var w = root.clientWidth;
      var s = Math.min(1, w / (w < 768 ? 860 : 1440));
      root.style.setProperty("--s", s.toFixed(4));
    }
    fit();
    new ResizeObserver(fit).observe(root);

    // Offset of card i from the active card, wrapped to -⌊n/2⌋…⌊n/2⌋
    function offset(i) {
      var d = (((i - active) % n) + n) % n;
      return d > n / 2 ? d - n : d;
    }

    root.querySelectorAll("[data-fan-deco]").forEach(function (deco) {
      gsap.set(deco, Object.assign(fanSlot(+deco.getAttribute("data-fan-deco")), { zIndex: 1 }));
    });

    function layout(animate, dir) {
      cards.forEach(function (card, i) {
        var d = offset(i);
        var prev = card._fanD;
        card.setAttribute("aria-current", d === 0 ? "true" : "false");
        card.tabIndex = -1;
        if (!animate || prefersReduced()) {
          gsap.set(card, fanSlot(d));
        } else if (prev !== undefined && Math.abs(d - prev) > 1) {
          // Wrapping round: exit off one end of the fan, come back in from the other
          gsap.timeline()
            .to(card, Object.assign(fanSlot(prev + (dir > 0 ? -1 : 1)), { autoAlpha: 0, duration: 0.35, ease: "power2.in" }))
            .set(card, Object.assign(fanSlot(d + (dir > 0 ? 1 : -1)), { autoAlpha: 0 }))
            .to(card, Object.assign(fanSlot(d), { duration: 0.55, ease: "power3.out" }));
        } else {
          gsap.to(card, Object.assign(fanSlot(d), { duration: 0.75, ease: "power3.out" }));
        }
        card._fanD = d;
      });
    }

    function go(delta) {
      if (!delta) return;
      active = (((active + delta) % n) + n) % n;
      layout(true, delta);
      queue();
    }

    function queue() {
      if (autoplay) autoplay.kill();
      if (prefersReduced() || hovering || !inView) return;
      autoplay = gsap.delayedCall(4, function () { go(1); });
    }

    // Click a side card to focus it
    cards.forEach(function (card, i) {
      card.addEventListener("click", function () {
        if (Date.now() - lastDrag < 350) return;
        go(offset(i));
      });
      var inner = card.querySelector("[data-fan-inner]");
      card.addEventListener("mouseenter", function () {
        if (offset(i) === 0 && !prefersReduced()) gsap.to(inner, { y: -14, duration: 0.4, ease: "power2.out" });
      });
      card.addEventListener("mouseleave", function () {
        gsap.to(inner, { y: 0, duration: 0.5, ease: "power2.out" });
      });
    });

    // Keyboard
    stage.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
    });

    // Drag / swipe (mouse + touch)
    Observer.create({
      target: stage,
      type: "touch,pointer",
      dragMinimum: 6,
      onDragEnd: function (self) {
        var dx = self.x - self.startX;
        if (Math.abs(dx) < 50) return;
        lastDrag = Date.now();
        go(dx < 0 ? 1 : -1);
      },
    });

    // Pause autoplay on hover / keyboard focus
    root.addEventListener("mouseenter", function () { hovering = true; queue(); });
    root.addEventListener("mouseleave", function () { hovering = false; queue(); });
    stage.addEventListener("focusin", function () { hovering = true; queue(); });
    stage.addEventListener("focusout", function () { hovering = false; queue(); });

    cards.forEach(function (card, i) {
      card.setAttribute("aria-current", offset(i) === 0 ? "true" : "false");
    });

    // Entrance: cards start stacked in the centre and fan out when the section scrolls in
    if (prefersReduced()) {
      layout(false);
      inView = true;
    } else {
      gsap.set(cards, Object.assign(fanSlot(0), { y: 160, autoAlpha: 0 }));
      ScrollTrigger.create({
        trigger: root,
        start: "top 70%",
        once: true,
        onEnter: function () {
          cards.forEach(function (card, i) {
            var d = offset(i);
            card._fanD = d;
            gsap.to(card, Object.assign(fanSlot(d), { duration: 1.1, ease: "expo.out", delay: 0.08 * Math.abs(d) }));
          });
        },
      });
    }
    ScrollTrigger.create({
      trigger: root,
      start: "top bottom",
      end: "bottom top",
      onToggle: function (self) { inView = self.isActive; queue(); },
    });
  }

  /* ------------------------------------------------------------------
   * 3. REGISTRATION FEE — FLIP-TO-CENTRE CARDS  [data-pd-fees]
   *    Figma: "While hovering over a card it'll flip, get zoomed and
   *    come in centre" (ref: Polaroid Flip Card — spring flip).
   *    Desktop only; on mobile the cards are simply stacked.
   * ------------------------------------------------------------------ */
  var FEE_SLOTS = {
    "0": { x: 0, scale: 1, zIndex: 3 },
    "-1": { x: -455, scale: 0.5, zIndex: 2 },
    "1": { x: 455, scale: 0.5, zIndex: 2 },
  };

  function initFees(root) {
    var cards = gsap.utils.toArray(root.querySelectorAll("[data-fee-card]"));
    if (cards.length !== 3) return;

    gsap.matchMedia().add("(min-width: 768px)", function () {
      var busy = false;
      var cleanups = [];

      // Colours follow the position: data-fee-slot drives the card + edge colours in fees.html
      function paint(card) {
        card.setAttribute("data-active", card._slot === 0 ? "true" : "false");
        card.setAttribute("data-fee-slot", String(card._slot));
      }

      cards.forEach(function (card) {
        card._slot = +card.getAttribute("data-fee-slot-default");
        card._skipHover = false;
        gsap.set(card, Object.assign({ transformPerspective: 1600, transformOrigin: "50% 50%" }, FEE_SLOTS[card._slot]));
        paint(card);
      });

      function promote(card) {
        if (busy || card._slot === 0) return;
        busy = true;
        var centre = cards.find(function (c) { return c._slot === 0; });
        var target = card._slot;

        card._slot = 0;
        centre._slot = target;
        centre._skipHover = true; // the old centre lands under the cursor — don't bounce it straight back

        if (prefersReduced()) {
          paint(card);
          paint(centre);
          gsap.set(card, FEE_SLOTS["0"]);
          gsap.set(centre, FEE_SLOTS[String(target)]);
          busy = false;
          return;
        }

        gsap.timeline({ onComplete: function () { busy = false; } })
          .set(card, { zIndex: 4 }, 0)
          .call(function () { paint(card); paint(centre); }, null, 0.45) // swap colours mid-flip
          .to(card, { x: 0, rotationY: "+=360", duration: 1, ease: "back.inOut(1.2)" }, 0)
          .to(card, { scale: 1.12, duration: 0.5, ease: "power2.out" }, 0)
          .to(card, { scale: 1, duration: 0.5, ease: "power2.in" }, 0.5)
          .to(centre, { x: FEE_SLOTS[String(target)].x, scale: 0.5, duration: 0.9, ease: "power3.inOut" }, 0)
          .set(centre, { zIndex: 2 }, 0.45)
          .set(card, { zIndex: 3 });
      }

      cards.forEach(function (card) {
        var onEnter = function () { if (!card._skipHover) promote(card); };
        var onLeave = function () { card._skipHover = false; };
        var onClick = function (e) {
          if (card._slot !== 0) { e.preventDefault(); promote(card); }
        };
        var onKey = function (e) {
          if ((e.key === "Enter" || e.key === " ") && e.target === card && card._slot !== 0) {
            e.preventDefault();
            promote(card);
          }
        };
        card.addEventListener("mouseenter", onEnter);
        card.addEventListener("mouseleave", onLeave);
        card.addEventListener("click", onClick);
        card.addEventListener("keydown", onKey);
        cleanups.push(function () {
          card.removeEventListener("mouseenter", onEnter);
          card.removeEventListener("mouseleave", onLeave);
          card.removeEventListener("click", onClick);
          card.removeEventListener("keydown", onKey);
        });
      });

      // Entrance
      if (!prefersReduced()) {
        gsap.from(cards, {
          y: 140,
          autoAlpha: 0,
          duration: 1,
          ease: "power3.out",
          stagger: 0.12,
          scrollTrigger: { trigger: root.querySelector("[data-fee-stage]"), start: "top 80%", once: true },
        });
      }

      return function () {
        cleanups.forEach(function (fn) { fn(); });
        gsap.set(cards, { clearProps: "all" });
        cards.forEach(function (card) {
          card.setAttribute("data-active", card.getAttribute("data-active-default"));
          card.setAttribute("data-fee-slot", card.getAttribute("data-fee-slot-default"));
        });
      };
    });

    // Mobile: simple reveal
    gsap.matchMedia().add("(max-width: 767px) and " + MOTION_OK, function () {
      cards.forEach(function (card) {
        gsap.from(card, { y: 80, autoAlpha: 0, duration: 0.8, ease: "power3.out", scrollTrigger: { trigger: card, start: "top 90%", once: true } });
      });
    });
  }

  /* ------------------------------------------------------------------
   * 4. SHIFT BUTTONS  [data-shift]
   *    Figma: "Shift button animation" / "Same button animation"
   *    (ref: Shift Button — shifts left with a springy bounce and the
   *    arrow turns to point the way).
   * ------------------------------------------------------------------ */
  function initShiftButtons() {
    document.querySelectorAll("[data-shift]").forEach(function (btn) {
      var pill = btn.querySelector("[data-shift-pill]");
      var icon = btn.querySelector("[data-shift-icon]");
      var on = function () {
        if (prefersReduced()) return;
        gsap.to(pill, { x: -10, duration: 0.7, ease: "elastic.out(1, 0.45)" });
        gsap.to(icon, { x: 6, rotation: 45, duration: 0.7, ease: "elastic.out(1, 0.45)" });
      };
      var off = function () {
        gsap.to([pill, icon], { x: 0, rotation: 0, duration: 0.6, ease: "elastic.out(1, 0.5)" });
      };
      btn.addEventListener("mouseenter", on);
      btn.addEventListener("focus", on);
      btn.addEventListener("mouseleave", off);
      btn.addEventListener("blur", off);
    });
  }

  /* ------------------------------------------------------------------
   * 5. FAQ ACCORDION  [data-pd-faq]
   *    Figma: "FAQ animation" (ref: Framer FAQs — smooth expand/collapse).
   *    One item open at a time; chevron flips; answer slides in.
   * ------------------------------------------------------------------ */
  function initFaq(root) {
    var items = gsap.utils.toArray(root.querySelectorAll("[data-faq-item]"));
    if (!items.length) return;

    function parts(item) {
      return {
        btn: item.querySelector("[data-faq-trigger]"),
        panel: item.querySelector("[data-faq-panel]"),
        answer: item.querySelector("[data-faq-answer]"),
        icon: item.querySelector("[data-faq-icon]"),
      };
    }

    function setOpen(item, open, animate) {
      var p = parts(item);
      p.btn.setAttribute("aria-expanded", open ? "true" : "false");
      p.panel.inert = !open;
      var d = animate && !prefersReduced() ? 1 : 0;
      gsap.to(p.panel, { height: open ? "auto" : 0, duration: 0.55 * d, ease: "power3.inOut", overwrite: true });
      gsap.to(p.icon, { rotation: open ? 180 : 0, duration: 0.45 * d, ease: "back.out(2)", overwrite: true });
      if (open) {
        gsap.fromTo(p.answer, { y: -12, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5 * d, delay: 0.12 * d, ease: "power2.out", overwrite: true });
      } else {
        gsap.to(p.answer, { autoAlpha: 0, duration: 0.25 * d, overwrite: true });
      }
    }

    items.forEach(function (item) {
      setOpen(item, item.hasAttribute("data-faq-open"), false);
      parts(item).btn.addEventListener("click", function () {
        var willOpen = this.getAttribute("aria-expanded") !== "true";
        items.forEach(function (other) {
          if (other !== item && parts(other).btn.getAttribute("aria-expanded") === "true") setOpen(other, false, true);
        });
        setOpen(item, willOpen, true);
      });
    });

    // Items rise in one by one
    gsap.matchMedia().add(MOTION_OK, function () {
      gsap.from(items, {
        y: 40,
        autoAlpha: 0,
        duration: 0.7,
        ease: "power3.out",
        stagger: 0.08,
        scrollTrigger: { trigger: root, start: "top 85%", once: true },
      });
    });
  }

  /* ------------------------------------------------------------------
   * 6. THREE-CIRCLE CURSOR  [data-pd-cursor]  (site-wide)
   *    Figma: "Cursor animation" (ref: Three Circle Cursor — a layered
   *    trail of three circles). Lime leads, pink and green follow with
   *    more lag. Grows over clickable things. Mouse only.
   * ------------------------------------------------------------------ */
  function initCursor() {
    var root = document.querySelector("[data-pd-cursor]");
    if (!root) return;

    gsap.matchMedia().add("(pointer: fine) and " + MOTION_OK, function () {
      var dots = [0, 1, 2].map(function (i) { return root.querySelector('[data-pd-cursor-dot="' + i + '"]'); });
      var lag = [0.08, 0.22, 0.4];
      var movers = dots.map(function (dot, i) {
        return {
          x: gsap.quickTo(dot, "x", { duration: lag[i], ease: "power3.out" }),
          y: gsap.quickTo(dot, "y", { duration: lag[i], ease: "power3.out" }),
        };
      });

      root.classList.remove("hidden");
      document.documentElement.classList.add("pd-has-cursor");
      gsap.set(root, { autoAlpha: 0 });

      var hot = "a, button, [role='button'], input, select, textarea, label, [data-fan-card], [data-fee-card]";
      var onMove = function (e) {
        gsap.to(root, { autoAlpha: 1, duration: 0.2, overwrite: "auto" });
        movers.forEach(function (m) { m.x(e.clientX); m.y(e.clientY); });
      };
      var onOver = function (e) {
        var isHot = !!(e.target.closest && e.target.closest(hot));
        gsap.to(dots, { scale: isHot ? 1.6 : 1, duration: 0.35, ease: "power2.out", stagger: 0.04, overwrite: "auto" });
      };
      var onLeaveWindow = function () { gsap.to(root, { autoAlpha: 0, duration: 0.2 }); };

      window.addEventListener("pointermove", onMove, { passive: true });
      document.addEventListener("pointerover", onOver);
      document.documentElement.addEventListener("mouseleave", onLeaveWindow);

      return function () {
        window.removeEventListener("pointermove", onMove);
        document.removeEventListener("pointerover", onOver);
        document.documentElement.removeEventListener("mouseleave", onLeaveWindow);
        root.classList.add("hidden");
        document.documentElement.classList.remove("pd-has-cursor");
      };
    });
  }

  /* ------------------------------------------------------------------ */
  function init() {
    document.querySelectorAll("[data-pd-fan]").forEach(initFan);
    document.querySelectorAll("[data-pd-fees]").forEach(initFees);
    document.querySelectorAll("[data-pd-faq]").forEach(initFaq);
    initShiftButtons();
    initCursor();
    // Split headings only once the real fonts have loaded, so letters are measured correctly
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () {
      initWaves();
      ScrollTrigger.refresh();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
