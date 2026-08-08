/* DellMatrix shared client — state, cmd, chrome */
(function (global) {
  'use strict';

  const PAGES = [
    { id: 'menu', href: '/', label: 'Menu' },
    { id: 'walk', href: '/walk', label: 'Walk' },
    { id: 'lattice', href: '/lattice', label: 'Lattice' },
    { id: 'nursery', href: '/nursery', label: 'Nursery' },
    { id: 'program', href: '/program', label: 'Program' },
    { id: 'personas', href: '/personas', label: 'Personas' },
    { id: 'forces', href: '/forces', label: 'Forces' },
    { id: 'geometry', href: '/geometry', label: 'Geometry' },
    { id: 'matrices', href: '/matrices', label: 'Matrices' },
    { id: 'workshops', href: '/workshops', label: 'Workshops' },
    { id: 'inspire', href: '/inspire', label: 'Inspire' },
    { id: 'console', href: '/console', label: 'Console' },
  ];

  const SKIN = {
    cube: '#5b9dff', sphere: '#a78bfa', seed: '#34d399', flower: '#fbbf24',
    building: '#d4a574', words: '#94a3b8', circle: '#2dd4bf', core: '#fb923c',
  };

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function short(s, n) {
    s = String(s ?? '');
    return s.length > n ? s.slice(0, Math.max(1, n - 1)) + '…' : s;
  }

  function ensureChrome() {
    if (!document.getElementById('dm-toast')) {
      const t = document.createElement('div');
      t.id = 'dm-toast';
      t.className = 'toast';
      document.body.appendChild(t);
    }
    if (!document.getElementById('dm-loading')) {
      const b = document.createElement('div');
      b.id = 'dm-loading';
      b.className = 'loading-bar';
      document.body.prepend(b);
    }
  }

  function toast(msg) {
    ensureChrome();
    const el = document.getElementById('dm-toast');
    el.textContent = short(msg, 100);
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), 1800);
  }

  function setLoading(on) {
    ensureChrome();
    const b = document.getElementById('dm-loading');
    b.classList.toggle('on', !!on);
    b.style.width = on ? '70%' : '100%';
    if (!on) setTimeout(() => { b.style.width = '0'; b.classList.remove('on'); }, 180);
  }

  let _stateCache = null, _stateAt = 0;
  async function getState() {
    /* pageenh:js-gs */
    if (_stateCache && Date.now() - _stateAt < 400) return _stateCache;
    const r = await fetch('/state', { cache: 'no-store' });
    if (!r.ok) throw new Error('state ' + r.status);
    const j = await r.json();
    _stateCache = j;
    _stateAt = Date.now();
    return j;
  }

  let _dmBusy=false; /* enhance:busy-guard */
  async function sendCmd(cmd, opts) {
    if(_dmBusy && !(opts&&opts.force)) return {ok:false,error:'busy'};
    _dmBusy=true;
    opts = opts || {};
    cmd = String(cmd || '').trim();
    if (!cmd) return null;
    setLoading(true);
    try {
      const r = await fetch('/cmd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd }),
      });
      let data;
      try { data = await r.json(); } catch (e) { data = { ok: false, error: 'bad JSON' }; }
      if (data.ok) {
        // first line of end-page message for toast; full body stays on page out
        const raw = String(data.msg || cmd);
        const msg = raw.split('\n')[0] || cmd;
        /* syncux:cache-bust */
        _stateCache = null; _stateAt = 0;
        if (!opts.silent) toast(msg);
        if (opts.onOk) opts.onOk(data);
        return data;
      }
      const err = String(data.error || 'failed').split('\n')[0];
      if (!opts.silent) toast('✗ ' + err);
      if (opts.onErr) opts.onErr(data);
      return data;
    } catch (e) {
      if (!opts.silent) toast('offline: ' + e);
      return { ok: false, error: String(e) };
    } finally {
      setLoading(false); _dmBusy=false;
    }
  }

  function pathPage() {
    const p = location.pathname.replace(/\/+$/, '') || '/';
    if (p === '/' || p === '/menu' || p === '/index.html') return 'menu';
    const hit = PAGES.find((x) => x.href === p);
    return hit ? hit.id : 'menu';
  }

  function renderTopbar(active, metaText) {
    const nav = PAGES.map((pg) => {
      const on = pg.id === active ? ' on' : '';
      return `<a class="nav${on}" href="${pg.href}" title="${esc(pg.label)}">${esc(pg.label)}</a>`; /* enhance:nav-title */
    }).join('');
    return `
      <header class="topbar">
        <div class="brand">
          <a href="/">DellMatrix</a>
          <span class="sub" id="dm-meta">${esc(metaText || 'live')}</span>
        </div>
        <nav>${nav}</nav>
      </header>`;
  }

  /* syncux:foot-sync */
  function renderFoot(s) {
    const fp = (s && s.fp) || {};
    const mandel = fp.mandel || '15[Map] :: …';
    const left = s
      ? `Floor locked · ${s.owner || 'Operator'} · ideas ${s.ideas ?? 0} · nursery ${(s.nursery || []).length} · gen ${s.generation ?? 0} · form ${s.form || '?'}`
      : 'DellMatrix · Nursery law · Floor locked';
    return `
      <footer class="foot">
        <div id="dm-foot-left">${esc(left)}</div>
        <div class="mandel" id="dm-foot-mandel">${esc(mandel)}</div>
      </footer>`;
  }

  function mountShell(opts) {
    opts = opts || {};
    const active = opts.page || pathPage();
    const root = document.getElementById('app') || document.body;
    if (!document.getElementById('dm-shell')) {
      const content = root.innerHTML;
      root.innerHTML = `
        <div class="shell" id="dm-shell">
          ${renderTopbar(active, opts.meta || 'connecting…')}
          <main id="dm-main">${content}</main>
          ${renderFoot(null)}
        </div>`;
    } else {
      const tb = document.querySelector('.topbar');
      if (tb) tb.outerHTML = renderTopbar(active, opts.meta || '');
    }
    ensureChrome();
    return {
      main: document.getElementById('dm-main'),
      setMeta(t) {
        const el = document.getElementById('dm-meta');
        if (el) el.textContent = t;
      },
      setFoot(s) {
        const foot = document.querySelector('.foot');
        if (foot) foot.outerHTML = renderFoot(s);
      },
    };
  }

  function pillarBars(pil) {
    pil = pil || {};
    return ['standing', 'spect', 'tonea', 'spirea', 'mandetail', 'omegate'].map((k) => {
      const pct = Math.max(0, Math.min(100, Math.round(Number(pil[k] || 0) * 100)));
      return `<div class="pbar"><span class="n">${esc(k)}</span><div class="t"><div class="f" style="width:${pct}%"></div></div><span>${pct}%</span></div>`;
    }).join('');
  }

  
  function formatSyncLine(s) {
    s = s || {};
    const fp = s.fp || {};
    const c = fp.center || [0, 0, 0];
    const pil = s.pillars || {};
    return `owner=${s.owner || '?'} · ideas=${s.ideas ?? 0} · form=${s.form || '?'} · gen=${s.generation ?? 0} · nursery=${(s.nursery || []).length} · ${pil.label || '—'} · @ (${c.join(',')})`;
  }
  /* syncux:sync-line */
function pageCard(title, bodyHtml, actionsHtml) {
    return `<div class="card"><h3>${esc(title)}</h3><div class="d">${bodyHtml || ''}</div>${actionsHtml || ''}</div>`;
  }

  /**
   * Enhanced lattice map painter (canvas).
   * opts: { nodes, edges, me, meFacing, ai, vision, selectedId, cam:{x,y,scale}, form }
   */
  function drawLatticeMap(canvas, opts) {
    opts = opts || {};
    if (!canvas) return;
    const parent = canvas.parentElement;
    const rect = parent ? parent.getBoundingClientRect() : { width: 800, height: 520 };
    const W = Math.max(200, Math.floor(rect.width || canvas.width || 400));
    const H = Math.max(160, Math.floor(rect.height || canvas.height || 220));
    if (canvas.width !== W || canvas.height !== H) {
      canvas.width = W;
      canvas.height = H;
    }
    const ctx = canvas.getContext('2d');
    const cam = opts.cam || { x: 0, y: 0, scale: 8 };
    const sc = Math.max(1.5, Number(cam.scale) || 8);
    const cx = W / 2 - (Number(cam.x) || 0) * sc;
    const cy = H / 2 + (Number(cam.y) || 0) * sc;
    const form = String(opts.form || 'cube');
    const nodes = opts.nodes || [];
    const edges = opts.edges || [];
    const allNodes = opts.allNodes || nodes;
    const byId = {};
    allNodes.forEach((n) => { byId[String(n.id)] = n; });

    // background vignette
    const bg = ctx.createRadialGradient(W * 0.5, H * 0.45, 20, W * 0.5, H * 0.5, Math.max(W, H) * 0.7);
    bg.addColorStop(0, form === 'flower' ? '#12100a' : form === 'sphere' ? '#0c0a14' : '#0a1018');
    bg.addColorStop(1, '#04060a');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    // soft ambient glow
    ctx.fillStyle = form === 'flower' ? 'rgba(251,191,36,0.04)' : 'rgba(91,157,255,0.05)';
    ctx.beginPath();
    ctx.arc(cx, cy, 90, 0, Math.PI * 2);
    ctx.fill();

    // grid
    const step = Math.max(1, Math.round(36 / sc));
    ctx.strokeStyle = form === 'flower' ? 'rgba(200,160,40,0.10)' : 'rgba(100,140,200,0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let g = -80; g <= 80; g += step) {
      const px = cx + g * sc;
      const py = cy - g * sc;
      ctx.moveTo(px, 0); ctx.lineTo(px, H);
      ctx.moveTo(0, py); ctx.lineTo(W, py);
    }
    ctx.stroke();

    // axes through origin
    ctx.strokeStyle = 'rgba(91,157,255,0.28)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(0, cy); ctx.lineTo(W, cy);
    ctx.moveTo(cx, 0); ctx.lineTo(cx, H);
    ctx.stroke();

    // shell rings (core/sphere/flower)
    if (form === 'core' || form === 'sphere' || form === 'circle' || form === 'flower') {
      ctx.strokeStyle = form === 'flower' ? 'rgba(251,191,36,0.18)' : 'rgba(167,139,250,0.16)';
      ctx.setLineDash([4, 4]);
      for (let r = 1; r <= 4; r++) {
        ctx.beginPath();
        ctx.arc(cx, cy, r * sc, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.setLineDash([]);
    }

    // edges
    const edgeColor = {
      enhance: 'rgba(61,90,128,0.45)',
      vesica: 'rgba(167,139,250,0.35)',
      sandbox: 'rgba(180,120,40,0.4)',
      verita: 'rgba(52,211,153,0.35)',
    };
    edges.slice(0, 400).forEach((e) => {
      const a = byId[String(e.a || e.source || e.from)];
      const b = byId[String(e.b || e.target || e.to)];
      if (!a || !b) return;
      const kind = e.kind || e.type || '';
      ctx.strokeStyle = edgeColor[kind] || 'rgba(100,140,200,0.12)';
      ctx.lineWidth = kind === 'vesica' ? 1.4 : 1;
      if (kind === 'sandbox') ctx.setLineDash([4, 3]);
      else ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(cx + (a.x || 0) * sc, cy - (a.y || 0) * sc);
      ctx.lineTo(cx + (b.x || 0) * sc, cy - (b.y || 0) * sc);
      ctx.stroke();
    });
    ctx.setLineDash([]);

    // vision cone
    const vision = opts.vision;
    if (vision && vision.cone && vision.cone.length >= 3) {
      ctx.beginPath();
      vision.cone.forEach((p, i) => {
        const x = cx + Number(p[0]) * sc;
        const y = cy - Number(p[1]) * sc;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.fillStyle = 'rgba(56,189,248,0.10)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(56,189,248,0.35)';
      ctx.stroke();
    }
    const inView = new Set((vision && vision.in_view_ids) || []);

    function drawSkin(n, x, y, r, selected) {
      const skin = n.skin || 'cube';
      const col = SKIN[skin] || '#5b9dff';
      const score = Number(n.score || 0);
      const rr = Math.max(r, Math.min(r + 6, r + score * 1.2));
      // soft halo for in-view
      if (inView.has(String(n.id))) {
        ctx.beginPath();
        ctx.arc(x, y, rr + 5, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.10)';
        ctx.fill();
      }
      ctx.fillStyle = col;
      ctx.strokeStyle = selected ? '#fff' : (inView.has(String(n.id)) ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.25)');
      ctx.lineWidth = selected ? 2.2 : 1;
      if (skin === 'cube' || skin === 'building') {
        const w = rr * (skin === 'building' ? 1.1 : 1.6);
        const h = rr * (skin === 'building' ? 2.2 : 1.6);
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(x - w / 2, y - h / 2, w, h, 3) : ctx.rect(x - w / 2, y - h / 2, w, h);
        ctx.fill();
        ctx.stroke();
      } else if (skin === 'flower') {
        for (let k = 0; k < 6; k++) {
          const a = (k * Math.PI) / 3;
          ctx.beginPath();
          ctx.arc(x + Math.cos(a) * rr * 0.55, y + Math.sin(a) * rr * 0.55, rr * 0.42, 0, Math.PI * 2);
          ctx.fillStyle = col;
          ctx.globalAlpha = 0.55;
          ctx.fill();
        }
        ctx.globalAlpha = 1;
        ctx.beginPath();
        ctx.arc(x, y, rr * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
        ctx.stroke();
      } else if (skin === 'words') {
        ctx.fillRect(x - rr * 0.55, y - rr, rr * 1.1, rr * 2);
        ctx.strokeRect(x - rr * 0.55, y - rr, rr * 1.1, rr * 2);
        ctx.strokeStyle = 'rgba(15,17,21,0.5)';
        ctx.beginPath();
        ctx.moveTo(x - rr * 0.3, y - rr * 0.4);
        ctx.lineTo(x + rr * 0.3, y - rr * 0.4);
        ctx.stroke();
      } else {
        // sphere / seed / circle / core
        const g = ctx.createRadialGradient(x - rr * 0.3, y - rr * 0.3, 1, x, y, rr);
        g.addColorStop(0, '#ffffff55');
        g.addColorStop(0.35, col);
        g.addColorStop(1, '#00000055');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, rr, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = selected ? '#fff' : 'rgba(255,255,255,0.25)';
        ctx.stroke();
      }
      if (selected) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(x, y, rr + 6, 0, Math.PI * 2);
        ctx.stroke();
      }
      if (n.sandboxed) {
        ctx.setLineDash([3, 2]);
        ctx.strokeStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(x, y, rr + 3, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // painter sort: lower y first for slight depth
    const sorted = nodes.slice().sort((a, b) => (a.y || 0) - (b.y || 0) || (a.x || 0) - (b.x || 0));
    const selId = opts.selectedId != null ? String(opts.selectedId) : '';
    sorted.forEach((n) => {
      const x = cx + (n.x || 0) * sc;
      const y = cy - (n.y || 0) * sc;
      if (x < -20 || y < -20 || x > W + 20 || y > H + 20) return;
      const selected = selId && String(n.id) === selId;
      const baseR = selected ? 7 : 4.2;
      drawSkin(n, x, y, baseR, selected);
      // labels when zoomed in or selected
      if (selected || sc >= 14) {
        ctx.fillStyle = '#eef2f7';
        ctx.font = selected ? '600 11px system-ui,sans-serif' : '10px system-ui,sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(String(n.label || n.id).slice(0, selected ? 22 : 12), x, y + (selected ? 18 : 14));
        ctx.textAlign = 'start';
      }
    });

    // AI companion
    if (opts.ai && opts.ai.pos) {
      const ax = cx + Number(opts.ai.pos[0] || 0) * sc;
      const ay = cy - Number(opts.ai.pos[1] || 0) * sc;
      ctx.fillStyle = '#e879f9';
      ctx.beginPath();
      ctx.arc(ax, ay, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#f5d0fe';
      ctx.stroke();
      const face = String(opts.ai.facing || 'N').toUpperCase();
      const dir = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0], NE: [1, -1], NW: [-1, -1], SE: [1, 1], SW: [-1, 1] }[face] || [0, -1];
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(ax + dir[0] * 12, ay + dir[1] * 12);
      ctx.stroke();
    }

    // YOU
    const me = opts.me || [0, 0];
    const mx = cx + Number(me[0] || 0) * sc;
    const my = cy - Number(me[1] || 0) * sc;
    ctx.fillStyle = '#38bdf8';
    ctx.shadowColor = '#38bdf8';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.arc(mx, my, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = '#7dd3fc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(mx, my, 10, 0, Math.PI * 2);
    ctx.stroke();
    const yaw = String(opts.meFacing || 'N').toUpperCase();
    const mdir = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0], NE: [1, -1], NW: [-1, -1], SE: [1, 1], SW: [-1, 1] }[yaw] || [0, -1];
    ctx.beginPath();
    ctx.moveTo(mx, my);
    ctx.lineTo(mx + mdir[0] * 16, my + mdir[1] * 16);
    ctx.stroke();
    ctx.fillStyle = '#7dd3fc';
    ctx.font = '600 10px system-ui,sans-serif';
    ctx.fillText('YOU', mx + 10, my - 10);

    // form badge
    ctx.fillStyle = 'rgba(15,20,30,0.75)';
    ctx.fillRect(8, 8, 120, 20);
    ctx.strokeStyle = 'rgba(91,157,255,0.3)';
    ctx.strokeRect(8, 8, 120, 20);
    ctx.fillStyle = '#8b97ab';
    ctx.font = '10px ui-monospace,monospace';
    ctx.fillText(`form=${form} · sc=${sc.toFixed(1)}`, 14, 21);
  }

  global.DM = {
    formatSyncLine,
    PAGES, SKIN, esc, short, toast, setLoading, getState, sendCmd,
    pathPage, mountShell, pillarBars, pageCard, renderTopbar, renderFoot,
    drawLatticeMap,
  };
})(window);
