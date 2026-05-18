(function () {
  const links = [...document.querySelectorAll("[data-route]")];
  const panels = [...document.querySelectorAll("[data-route-panel]")];

  if (!links.length || !panels.length) {
    return;
  }

  function currentRoute() {
    return window.location.hash.replace("#", "") || defaultRoute();
  }

  function defaultRoute() {
    const active = panels.find((panel) => panel.classList.contains("active"));
    return active?.dataset.routePanel || panels[0].dataset.routePanel;
  }

  function hasRoute(route) {
    return panels.some((panel) => panel.dataset.routePanel === route);
  }

  function setRoute(route, options = {}) {
    const target = hasRoute(route) ? route : defaultRoute();

    for (const panel of panels) {
      const active = panel.dataset.routePanel === target;
      panel.classList.toggle("active", active);
      panel.hidden = !active;
    }

    for (const link of links) {
      link.classList.toggle("active", link.dataset.route === target);
      if (link.dataset.route === target) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    }

    document.body.dataset.route = target;

    if (options.scroll) {
      scrollToRoute(target);
    }
  }

  function scrollToRoute(route) {
    const panel = panels.find((item) => item.dataset.routePanel === route);
    if (!panel) {
      return;
    }

    const nav = document.querySelector("[data-sticky-nav]");
    const offset = nav ? nav.getBoundingClientRect().height : 0;
    const top =
      panel.getBoundingClientRect().top + window.scrollY - offset - 18;

    window.scrollTo({
      top: Math.max(0, top),
      behavior: prefersReducedMotion() ? "auto" : "smooth",
    });
  }

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  for (const link of links) {
    link.addEventListener("click", (event) => {
      const route = link.dataset.route;
      if (!route || !hasRoute(route)) {
        return;
      }

      event.preventDefault();
      if (window.location.hash !== `#${route}`) {
        window.history.pushState(null, "", `#${route}`);
      }
      setRoute(route, { scroll: true });
    });
  }

  window.addEventListener("hashchange", () => {
    setRoute(currentRoute(), { scroll: true });
  });

  setRoute(currentRoute(), { scroll: false });
})();
