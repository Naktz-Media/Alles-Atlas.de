/* Alles-Atlas.de: kleine Helfer, keine Tracker */
(function () {
  "use strict";

  // Mobiles Menü
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Header-Linie beim Scrollen
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // E-Mail-Adresse erst im Browser zusammensetzen (Spam-Schutz)
  document.querySelectorAll("[data-mail]").forEach(function (el) {
    var addr = el.getAttribute("data-mail").replace(" (at) ", "@");
    if (el.tagName === "A") el.href = "mailto:" + addr;
    var t = el.querySelector("[data-mail-text]") || el;
    t.textContent = addr;
  });

  // Jahreszahl im Footer
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // Alte WordPress-Links (?page_id=…) auf neue Seiten umleiten
  var m = { "7": "kontakt/", "14": "impressum/", "17": "service/", "702": "dsgvo/" };
  var q = new URLSearchParams(window.location.search);
  if (q.get("page_id") && m[q.get("page_id")]) window.location.replace("/" + m[q.get("page_id")]);
})();
