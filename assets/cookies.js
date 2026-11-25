/* Reol-Loppen: besøgsstatistik (Google Analytics) – indlæses KUN hvis den besøgende siger ja til cookies */
(function () {
  var GA_ID = 'G-JW3YFVRJQJ';
  var KEY = 'rl-cookie-valg';

  function hent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function gem(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function startGA() {
    if (window.__rlGA) return;
    window.__rlGA = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { anonymize_ip: true });
  }

  var css = '.rl-ck{position:fixed;left:16px;right:16px;bottom:16px;z-index:60;max-width:560px;margin:0 auto;background:#141414;color:#fff;border-radius:16px;padding:18px 20px;box-shadow:0 10px 30px rgba(0,0,0,.3);font:15px/1.45 Nunito,system-ui,sans-serif}' +
    '.rl-ck p{margin:0 0 12px}.rl-ck a{color:#ffb27a}' +
    '.rl-ck .b{display:flex;gap:10px;flex-wrap:wrap}' +
    '.rl-ck button{font:inherit;font-weight:800;border-radius:999px;padding:8px 18px;cursor:pointer;border:2px solid #E8772E}' +
    '.rl-ck .ja{background:#E8772E;color:#141414}.rl-ck .nej{background:transparent;color:#fff}';

  function visBanner() {
    if (document.querySelector('.rl-ck')) return;
    if (!document.getElementById('rl-ck-css')) {
      var st = document.createElement('style'); st.id = 'rl-ck-css'; st.textContent = css; document.head.appendChild(st);
    }
    var d = document.createElement('div');
    d.className = 'rl-ck'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Cookies');
    d.innerHTML = '<p><strong>Må vi tælle besøg? 🍪</strong><br>Vi bruger Google Analytics til at se, hvor mange der besøger siden, og hvor de kommer fra. Det sker kun, hvis du siger ja. Du kan altid ændre dit valg under "Cookies" nederst på siden.</p>' +
      '<div class="b"><button type="button" class="ja">Ja tak</button><button type="button" class="nej">Nej tak</button></div>';
    document.body.appendChild(d);
    d.querySelector('.ja').addEventListener('click', function () { gem('ja'); d.remove(); startGA(); });
    d.querySelector('.nej').addEventListener('click', function () {
      gem('nej'); d.remove();
      if (window.__rlGA) { location.reload(); }
    });
  }

  window.rlCookies = visBanner;
  document.addEventListener('click', function (e) { var a = e.target.closest && e.target.closest('[data-cookies]'); if (a) { e.preventDefault(); visBanner(); } });
  var v = hent();
  if (v === 'ja') startGA();
  else if (v !== 'nej') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', visBanner); else visBanner();
  }
})();
