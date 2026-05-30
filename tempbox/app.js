/* TempBox — Full-featured temporary email client.
 * Supports: mail.tm, Guerrilla Mail (random auto-select)
 * Features: OTP detection, QR code, download .eml, delete, search, history, sound notifications
 */
(() => {
  "use strict";

  const POLL_INTERVAL = 10;
  let currentProvider = null;
  let messages = [];
  let countdown = POLL_INTERVAL;
  let countdownTimer = null;
  let busy = false;
  let totalReceived = 0;
  let soundEnabled = true;
  let currentMsgId = null;

  const $ = (id) => document.getElementById(id);
  const el = {
    address: $("emailAddress"),
    spinner: $("emailSpinner"),
    copyBtn: $("copyBtn"),
    qrBtn: $("qrBtn"),
    refreshBtn: $("refreshBtn"),
    newBtn: $("newBtn"),
    statusDot: $("statusDot"),
    statusText: $("statusText"),
    countdown: $("countdown"),
    list: $("messageList"),
    empty: $("emptyState"),
    count: $("inboxCount"),
    themeToggle: $("themeToggle"),
    soundToggle: $("soundToggle"),
    toast: $("toast"),
    overlay: $("modalOverlay"),
    modalSubject: $("modalSubject"),
    modalFrom: $("modalFrom"),
    modalDate: $("modalDate"),
    modalBody: $("modalBody"),
    modalClose: $("modalClose"),
    modalDownload: $("modalDownload"),
    modalForward: $("modalForward"),
    modalDelete: $("modalDelete"),
    providerName: $("providerName"),
    totalReceived: $("totalReceived"),
    searchInput: $("searchInput"),
    deleteAllBtn: $("deleteAllBtn"),
    historyBar: $("historyBar"),
    historyList: $("historyList"),
    qrOverlay: $("qrOverlay"),
    qrCanvas: $("qrCanvas"),
    qrAddress: $("qrAddress"),
    qrClose: $("qrClose"),
    shareBtn: $("shareBtn"),
    autoDeleteSelect: $("autoDeleteSelect"),
  };

  // ===================== UTILITIES =====================
  function randomString(len) {
    const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
    let out = "";
    for (let i = 0; i < len; i++) out += chars[Math.floor(Math.random() * chars.length)];
    return out;
  }

  function setStatus(text, mode) {
    el.statusText.textContent = text;
    el.statusDot.className = "status-dot" + (mode ? " " + mode : "");
  }

  function showToast(msg) {
    el.toast.textContent = msg;
    el.toast.style.display = "block";
    requestAnimationFrame(() => el.toast.classList.add("show"));
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => {
      el.toast.classList.remove("show");
      setTimeout(() => (el.toast.style.display = "none"), 300);
    }, 2200);
  }

  function setButtons(enabled) {
    el.copyBtn.disabled = !enabled;
    el.qrBtn.disabled = !enabled;
    el.shareBtn.disabled = !enabled;
    el.refreshBtn.disabled = !enabled;
    el.newBtn.disabled = !enabled;
    el.deleteAllBtn.disabled = !enabled;
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function timeAgo(iso) {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    if (isNaN(then)) return iso;
    const diff = Math.max(0, Date.now() - then);
    const m = Math.floor(diff / 60000);
    if (m < 1) return "Vừa xong";
    if (m < 60) return m + " phút trước";
    const h = Math.floor(m / 60);
    if (h < 24) return h + " giờ trước";
    return new Date(iso).toLocaleDateString("vi-VN");
  }

  // ===================== SOUND =====================
  function playNotificationSound() {
    if (!soundEnabled) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.frequency.setValueAtTime(1100, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.3);
    } catch (_) {}
  }

  // ===================== QR CODE (simple canvas) =====================
  function generateQR(text) {
    // Simple QR using external API rendered to image then drawn on canvas
    const size = 200;
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = "https://api.qrserver.com/v1/create-qr-code/?size=" + size + "x" + size + "&data=" + encodeURIComponent(text);
    img.onload = () => {
      const canvas = el.qrCanvas;
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);
    };
  }

  function showQR() {
    if (!currentProvider) return;
    const addr = currentProvider.getAddress();
    if (!addr) return;
    el.qrAddress.textContent = addr;
    generateQR(addr);
    el.qrOverlay.style.display = "grid";
  }

  function closeQR() {
    el.qrOverlay.style.display = "none";
  }

  // ===================== HISTORY =====================
  function addToHistory(address, provider) {
    let history = getHistory();
    // Don't add duplicates
    if (history.some((h) => h.address === address)) return;
    history.unshift({ address, provider, time: Date.now() });
    if (history.length > 10) history = history.slice(0, 10);
    localStorage.setItem("tempbox.history", JSON.stringify(history));
    renderHistory();
  }

  function getHistory() {
    try { return JSON.parse(localStorage.getItem("tempbox.history") || "[]"); } catch (_) { return []; }
  }

  function renderHistory() {
    const history = getHistory();
    if (history.length <= 1) { el.historyBar.style.display = "none"; return; }
    el.historyBar.style.display = "block";
    // Show all except current
    const current = currentProvider ? currentProvider.getAddress() : "";
    const others = history.filter((h) => h.address !== current);
    if (!others.length) { el.historyBar.style.display = "none"; return; }
    el.historyList.innerHTML = others.map((h) =>
      `<span class="history-item" title="${escapeHtml(h.provider)}">${escapeHtml(h.address)}</span>`
    ).join("");
    el.historyList.querySelectorAll(".history-item").forEach((item) => {
      item.addEventListener("click", () => {
        navigator.clipboard.writeText(item.textContent).then(() => showToast("📋 Đã sao chép: " + item.textContent));
      });
    });
  }

  // ===================== DOWNLOAD .EML =====================
  function downloadEml(msg) {
    const eml = [
      "From: " + (msg.from || "unknown"),
      "Subject: " + (msg.subject || ""),
      "Date: " + (msg.date || new Date().toISOString()),
      "MIME-Version: 1.0",
      "Content-Type: text/html; charset=utf-8",
      "",
      msg.html || msg.text || ""
    ].join("\r\n");
    const blob = new Blob([eml], { type: "message/rfc822" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (msg.subject || "email").replace(/[^a-zA-Z0-9]/g, "_").slice(0, 40) + ".eml";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("💾 Đã tải xuống email");
  }

  // ===================== OTP DETECTION =====================
  const OTP_PATTERNS = [
    /(?:code|mã|ma|otp|pin|token|verify|xác minh|xac minh|verification|passcode|security code|mã bảo mật|confirmation code)[\s:：=\-]*(\d{4,8})/i,
    /\b(\d{4,8})\b[\s]*(?:is your|là mã|la ma|is the|là)/i,
    /(?:OTP|code|mã)[\s]*(?:is|:|\s)[\s]*(\d{4,8})/i,
    /\b([A-Z]-\d{4,8})\b/,
    /(?:^|[>\s:：\-])(\d{4,8})(?:[<\s.\-,]|$)/m,
    /(?:code|mã|otp|verify|verification|confirm)[\s:：=\-]*([A-Z0-9]{5,8})\b/i,
  ];

  function extractOTP(text) {
    if (!text) return null;
    for (const pattern of OTP_PATTERNS) {
      const match = text.match(pattern);
      if (match && match[1]) {
        const code = match[1].trim();
        if (/^(19|20)\d{2}$/.test(code)) continue;
        if (/^0+$/.test(code)) continue;
        return code;
      }
    }
    return null;
  }

  function detectOTP(msg) {
    return extractOTP(msg.subject) || extractOTP(msg.intro) || (msg._bodyText ? extractOTP(msg._bodyText) : null);
  }

  async function copyOTP(code, event) {
    if (event) { event.stopPropagation(); event.preventDefault(); }
    try {
      await navigator.clipboard.writeText(code);
      showToast("🔑 Đã sao chép mã: " + code);
    } catch (_) {
      const ta = document.createElement("textarea");
      ta.value = code;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      showToast("🔑 Đã sao chép mã: " + code);
    }
  }

  // ===================== PROVIDER: MAIL.TM =====================
  const mailTm = {
    name: "mailtm", label: "Mail.tm", state: {},

    async request(path, options = {}) {
      const headers = { "Accept": "application/json", ...(options.headers || {}) };
      if (options.body) headers["Content-Type"] = "application/json";
      if (this.state.token) headers["Authorization"] = "Bearer " + this.state.token;
      const res = await fetch("https://tempbox-email.netlify.app/api/mailtm" + path, { ...options, headers });
      const text = await res.text();
      const data = text ? JSON.parse(text) : null;
      if (!res.ok) {
        const msg = (data && (data["hydra:description"] || data.message || data.detail)) || ("HTTP " + res.status);
        const err = new Error(msg); err.status = res.status; throw err;
      }
      return data;
    },

    async createEmail() {
      const domData = await this.request("/domains?page=1");
      const list = domData["hydra:member"] || domData || [];
      const domains = Array.isArray(list) ? list.filter((d) => d.isActive !== false) : [];
      if (!domains.length) throw new Error("Không có domain");
      const domain = domains[0].domain;
      const address = randomString(10) + "@" + domain;
      const password = randomString(16);
      await this.request("/accounts", { method: "POST", body: JSON.stringify({ address, password }) });
      const tokenData = await this.request("/token", { method: "POST", body: JSON.stringify({ address, password }) });
      this.state = { address, password, token: tokenData.token, id: tokenData.id };
      this.save();
      return address;
    },

    async refreshToken() {
      const tokenData = await this.request("/token", {
        method: "POST", body: JSON.stringify({ address: this.state.address, password: this.state.password }),
      });
      this.state.token = tokenData.token; this.state.id = tokenData.id; this.save();
    },

    async getMessages() {
      let data;
      try { data = await this.request("/messages?page=1"); }
      catch (e) { if (e.status === 401) { await this.refreshToken(); data = await this.request("/messages?page=1"); } else throw e; }
      const list = data["hydra:member"] || data || [];
      return list.map((m) => ({
        id: m.id, from: (m.from && (m.from.name || m.from.address)) || "Không rõ",
        subject: m.subject || "", intro: m.intro || "", date: m.createdAt, seen: m.seen,
      }));
    },

    async getMessage(id) {
      const msg = await this.request("/messages/" + encodeURIComponent(id));
      const html = Array.isArray(msg.html) ? msg.html.join("") : msg.html;
      return { from: (msg.from && (msg.from.name || msg.from.address)) || "Không rõ", subject: msg.subject || "", date: msg.createdAt, html: html || "", text: msg.text || "" };
    },

    async deleteMessage(id) { await this.request("/messages/" + encodeURIComponent(id), { method: "DELETE" }); },
    getAddress() { return this.state.address || ""; },
    save() { try { localStorage.setItem("tempbox.mailtm", JSON.stringify(this.state)); } catch (_) {} },
    load() { try { const r = localStorage.getItem("tempbox.mailtm"); if (r) { this.state = JSON.parse(r); return true; } } catch (_) {} return false; },
    clear() { this.state = {}; try { localStorage.removeItem("tempbox.mailtm"); } catch (_) {} },
    async init() {
      if (this.load() && this.state.address && this.state.token) {
        try { await this.getMessages(); return this.state.address; }
        catch (e) { if (e.status === 401) { await this.refreshToken(); return this.state.address; } }
      }
      return await this.createEmail();
    },
  };

  // ===================== PROVIDER: GUERRILLA MAIL =====================
  const guerrilla = {
    name: "guerrilla", label: "Guerrilla Mail", state: {},

    async request(params) {
      const qs = new URLSearchParams(params);
      if (this.state.sid_token) qs.set("sid_token", this.state.sid_token);
      const res = await fetch("https://tempbox-email.netlify.app/api/guerrilla?" + qs.toString());
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      if (data.sid_token) this.state.sid_token = data.sid_token;
      return data;
    },

    async createEmail() {
      const data = await this.request({ f: "get_email_address" });
      this.state.email_addr = data.email_addr; this.save(); return data.email_addr;
    },

    async getMessages() {
      const data = await this.request({ f: "check_email", seq: "0" });
      const list = data.list || [];
      return list.filter((m) => m.mail_id !== "1").map((m) => ({
        id: m.mail_id, from: m.mail_from || "Không rõ", subject: m.mail_subject || "",
        intro: m.mail_excerpt || "", date: m.mail_timestamp ? new Date(m.mail_timestamp * 1000).toISOString() : "",
        seen: m.mail_read !== "0",
      }));
    },

    async getMessage(id) {
      const msg = await this.request({ f: "fetch_email", email_id: id });
      return { from: msg.mail_from || "Không rõ", subject: msg.mail_subject || "", date: msg.mail_date || "", html: msg.mail_body || "", text: "" };
    },

    async deleteMessage(id) { await this.request({ f: "del_email", email_ids: JSON.stringify([id]) }); },
    getAddress() { return this.state.email_addr || ""; },
    save() { try { localStorage.setItem("tempbox.guerrilla", JSON.stringify(this.state)); } catch (_) {} },
    load() { try { const r = localStorage.getItem("tempbox.guerrilla"); if (r) { this.state = JSON.parse(r); return true; } } catch (_) {} return false; },
    clear() { this.state = {}; try { localStorage.removeItem("tempbox.guerrilla"); } catch (_) {} },
    async init() {
      if (this.load() && this.state.sid_token && this.state.email_addr) {
        try { await this.getMessages(); return this.state.email_addr; } catch (_) {}
      }
      return await this.createEmail();
    },
  };

  // ===================== PROVIDER REGISTRY =====================
  const providers = [mailTm, guerrilla];
  function randomProvider() { return providers[Math.floor(Math.random() * providers.length)]; }

  // ===================== RENDER =====================
  function renderMessages(list) {
    const prevCount = messages.length;
    messages = list;
    el.count.textContent = list.length;
    el.deleteAllBtn.disabled = list.length === 0;

    if (!list.length) { el.list.innerHTML = ""; el.empty.style.display = "block"; return; }
    el.empty.style.display = "none";
    renderList();

    if (list.length > prevCount && prevCount > 0) {
      const diff = list.length - prevCount;
      totalReceived += diff;
      el.totalReceived.textContent = totalReceived;
      localStorage.setItem("tempbox.totalReceived", totalReceived);
      playNotificationSound();
      updateFaviconBadge(diff);
      sendBrowserNotification("📬 TempBox", "Bạn có " + diff + " email mới!");
      enrichAndNotify(list.slice(0, diff));
    }
  }

  function renderList(filter) {
    const query = (filter || el.searchInput.value || "").toLowerCase().trim();
    const filtered = query ? messages.filter((m) =>
      (m.from + " " + m.subject + " " + m.intro).toLowerCase().includes(query)
    ) : messages;

    el.list.innerHTML = filtered.map((m) => {
      const initial = escapeHtml((m.from || "?").trim().charAt(0));
      const otp = detectOTP(m);
      const otpHtml = otp ? `<button class="otp-badge" data-otp="${escapeHtml(otp)}" title="Nhấn để sao chép mã">🔑 ${escapeHtml(otp)}</button>` : "";
      return `
        <li class="message-item ${m.seen ? "" : "unseen"}" data-id="${escapeHtml(m.id)}">
          <div class="msg-avatar">${initial}</div>
          <div class="msg-content">
            <div class="msg-from">${escapeHtml(m.from)}</div>
            <div class="msg-subject">${escapeHtml(m.subject || "(Không có tiêu đề)")} ${otpHtml}</div>
            <div class="msg-intro">${escapeHtml(m.intro || "")}</div>
          </div>
          <div class="msg-right">
            <div class="msg-time">${escapeHtml(timeAgo(m.date))}</div>
            <button class="msg-delete-btn" data-id="${escapeHtml(m.id)}" title="Xóa">🗑️</button>
          </div>
        </li>`;
    }).join("");

    el.list.querySelectorAll(".message-item").forEach((node) => {
      node.addEventListener("click", (e) => {
        if (e.target.closest(".otp-badge") || e.target.closest(".msg-delete-btn")) return;
        openMessage(node.dataset.id);
      });
    });
    el.list.querySelectorAll(".otp-badge").forEach((btn) => {
      btn.addEventListener("click", (e) => copyOTP(btn.dataset.otp, e));
    });
    el.list.querySelectorAll(".msg-delete-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => { e.stopPropagation(); deleteMessage(btn.dataset.id); });
    });
  }

  async function enrichAndNotify(newMsgs) {
    for (const m of newMsgs) {
      if (m._bodyText !== undefined) continue;
      try {
        const full = await currentProvider.getMessage(m.id);
        m._bodyText = (full.text || "") + " " + (full.html || "").replace(/<[^>]+>/g, " ");
      } catch (_) { m._bodyText = ""; }
    }
    renderList();
    const firstOtp = newMsgs.map(detectOTP).find(Boolean);
    if (firstOtp) {
      showToast("🔑 Mã OTP: " + firstOtp + " (đã sao chép)");
      navigator.clipboard.writeText(firstOtp).catch(() => {});
    } else {
      showToast("📬 Bạn có " + newMsgs.length + " email mới!");
    }
  }

  // ===================== MESSAGE VIEWER =====================
  let currentFullMsg = null;

  async function openMessage(id) {
    try {
      const msg = await currentProvider.getMessage(id);
      currentFullMsg = msg;
      currentMsgId = id;
      el.modalSubject.textContent = msg.subject || "(Không có tiêu đề)";
      el.modalFrom.textContent = msg.from || "Không rõ";
      el.modalDate.textContent = msg.date ? new Date(msg.date).toLocaleString("vi-VN") : "";

      const bodyText = (msg.text || "") + " " + (msg.html || "").replace(/<[^>]+>/g, " ");
      const otp = extractOTP(msg.subject) || extractOTP(bodyText);
      const otpBanner = otp
        ? `<div class="otp-banner"><span class="otp-banner-label">🔑 Mã xác minh:</span><span class="otp-banner-code">${escapeHtml(otp)}</span><button class="btn btn-primary otp-banner-copy" id="modalOtpCopy">Sao chép</button></div>`
        : "";

      if (msg.html) {
        const frame = document.createElement("iframe");
        frame.setAttribute("sandbox", "allow-same-origin");
        frame.referrerPolicy = "no-referrer";
        el.modalBody.innerHTML = otpBanner;
        el.modalBody.appendChild(frame);
        frame.srcdoc = "<!DOCTYPE html><html><head><meta charset='utf-8'><base target='_blank'><style>body{font-family:system-ui,sans-serif;color:#1a1f2b;background:#fff;padding:8px;margin:0;}img{max-width:100%;height:auto;}a{color:#3b5bdb;word-break:break-all;}</style></head><body>" + msg.html + "</body></html>";
        frame.addEventListener("load", () => { try { const h = frame.contentDocument.body.scrollHeight; if (h) frame.style.height = (h + 24) + "px"; } catch (_) {} });
      } else {
        el.modalBody.innerHTML = otpBanner + "<pre style='white-space:pre-wrap;font-family:inherit;margin:0;'>" + escapeHtml(msg.text || "(Không có nội dung)") + "</pre>";
      }

      const otpCopyBtn = document.getElementById("modalOtpCopy");
      if (otpCopyBtn && otp) otpCopyBtn.addEventListener("click", (e) => copyOTP(otp, e));

      el.overlay.style.display = "grid";
      document.body.style.overflow = "hidden";
      const node = el.list.querySelector('[data-id="' + id + '"]');
      if (node) node.classList.remove("unseen");
    } catch (e) { showToast("Không mở được email: " + e.message); }
  }

  function closeModal() {
    el.overlay.style.display = "none";
    el.modalBody.innerHTML = "";
    document.body.style.overflow = "";
    currentFullMsg = null; currentMsgId = null;
  }

  // ===================== DELETE =====================
  async function deleteMessage(id) {
    try {
      if (currentProvider.deleteMessage) await currentProvider.deleteMessage(id);
      messages = messages.filter((m) => m.id !== id);
      el.count.textContent = messages.length;
      renderList();
      if (!messages.length) el.empty.style.display = "block";
      if (currentMsgId === id) closeModal();
      showToast("🗑️ Đã xóa email");
    } catch (e) { showToast("Lỗi xóa: " + e.message); }
  }

  async function deleteAll() {
    if (!messages.length) return;
    const confirmed = confirm("Xóa tất cả " + messages.length + " email?");
    if (!confirmed) return;
    for (const m of [...messages]) {
      try { if (currentProvider.deleteMessage) await currentProvider.deleteMessage(m.id); } catch (_) {}
    }
    messages = [];
    el.count.textContent = 0;
    renderList();
    el.empty.style.display = "block";
    showToast("🗑️ Đã xóa tất cả email");
  }

  // ===================== FORWARD (copy content) =====================
  function forwardEmail() {
    if (!currentFullMsg) return;
    const text = "--- Forwarded ---\nFrom: " + currentFullMsg.from + "\nSubject: " + currentFullMsg.subject + "\nDate: " + currentFullMsg.date + "\n\n" + (currentFullMsg.text || currentFullMsg.html.replace(/<[^>]+>/g, " "));
    navigator.clipboard.writeText(text).then(() => showToast("📤 Đã sao chép nội dung email")).catch(() => showToast("Lỗi sao chép"));
  }

  // ===================== POLLING =====================
  async function poll(showSpinner) {
    if (busy || !currentProvider) return;
    busy = true;
    if (showSpinner) el.spinner.classList.remove("hidden");
    try {
      const list = await currentProvider.getMessages();
      renderMessages(list);
      const unenriched = messages.filter((m) => m._bodyText === undefined);
      if (unenriched.length) {
        for (const m of unenriched) {
          try { const full = await currentProvider.getMessage(m.id); m._bodyText = (full.text || "") + " " + (full.html || "").replace(/<[^>]+>/g, " "); } catch (_) { m._bodyText = ""; }
        }
        renderList();
      }
      setStatus("Đang hoạt động — " + currentProvider.label, "live");
    } catch (e) { setStatus("Lỗi: " + e.message, "error"); }
    finally { busy = false; el.spinner.classList.add("hidden"); countdown = POLL_INTERVAL; }
  }

  function startTimers() {
    stopTimers(); countdown = POLL_INTERVAL;
    countdownTimer = setInterval(() => {
      countdown--;
      if (countdown <= 0) { poll(true); countdown = POLL_INTERVAL; }
      el.countdown.textContent = Math.max(0, countdown);
    }, 1000);
  }
  function stopTimers() { if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; } }

  // ===================== INIT =====================
  async function init(provider) {
    setButtons(false); stopTimers();
    el.spinner.classList.remove("hidden");
    setStatus("Đang khởi tạo…");
    messages = []; renderMessages([]);

    if (!provider) {
      const savedName = localStorage.getItem("tempbox.currentProvider");
      if (savedName) provider = providers.find((p) => p.name === savedName);
      if (!provider) provider = randomProvider();
    }

    currentProvider = provider;
    localStorage.setItem("tempbox.currentProvider", currentProvider.name);
    el.providerName.textContent = currentProvider.label;

    try {
      const addr = await currentProvider.init();
      el.address.textContent = addr;
      addToHistory(addr, currentProvider.label);
      setButtons(true);
      await poll(true);
      startTimers();
    } catch (e) {
      const other = providers.find((p) => p !== currentProvider);
      if (other) {
        currentProvider.clear(); currentProvider = other;
        localStorage.setItem("tempbox.currentProvider", currentProvider.name);
        el.providerName.textContent = currentProvider.label;
        try {
          const addr = await currentProvider.init();
          el.address.textContent = addr;
          addToHistory(addr, currentProvider.label);
          setButtons(true); await poll(true); startTimers(); return;
        } catch (_) {}
      }
      el.address.textContent = "Lỗi tạo email";
      setStatus("Lỗi: " + e.message, "error");
      el.spinner.classList.add("hidden");
      setTimeout(() => init(), 5000);
    }
  }

  async function createNew() {
    if (busy) return;
    setButtons(false); stopTimers();
    el.spinner.classList.remove("hidden");
    el.address.textContent = "Đang tạo email mới…";
    setStatus("Đang tạo email mới…");
    currentProvider = randomProvider();
    currentProvider.clear();
    localStorage.setItem("tempbox.currentProvider", currentProvider.name);
    el.providerName.textContent = currentProvider.label;
    messages = []; renderMessages([]);
    try {
      const addr = await currentProvider.createEmail();
      el.address.textContent = addr;
      addToHistory(addr, currentProvider.label);
      setButtons(true);
      showToast("✨ Email mới từ " + currentProvider.label);
      await poll(true); startTimers();
    } catch (e) {
      const other = providers.find((p) => p !== currentProvider);
      if (other) {
        currentProvider = other; currentProvider.clear();
        localStorage.setItem("tempbox.currentProvider", currentProvider.name);
        el.providerName.textContent = currentProvider.label;
        try {
          const addr = await currentProvider.createEmail();
          el.address.textContent = addr;
          addToHistory(addr, currentProvider.label);
          setButtons(true); showToast("✨ Email mới từ " + currentProvider.label);
          await poll(true); startTimers(); return;
        } catch (_) {}
      }
      el.address.textContent = "Lỗi"; setStatus("Lỗi: " + e.message, "error");
      el.spinner.classList.add("hidden"); setButtons(true);
    }
  }

  async function copyAddress() {
    if (!currentProvider) return;
    const addr = currentProvider.getAddress();
    if (!addr) return;
    try { await navigator.clipboard.writeText(addr); showToast("📋 Đã sao chép: " + addr); }
    catch (_) { const ta = document.createElement("textarea"); ta.value = addr; document.body.appendChild(ta); ta.select(); document.execCommand("copy"); document.body.removeChild(ta); showToast("📋 Đã sao chép"); }
  }

  // ===================== THEME & SOUND =====================
  function initTheme() {
    const saved = localStorage.getItem("tempbox.theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
    updateThemeIcon();
  }
  function toggleTheme() {
    const cur = document.documentElement.getAttribute("data-theme");
    const next = cur === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("tempbox.theme", next);
    updateThemeIcon();
  }
  function updateThemeIcon() {
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    el.themeToggle.textContent = isLight ? "☀️" : "🌙";
  }

  function initSound() {
    soundEnabled = localStorage.getItem("tempbox.sound") !== "off";
    updateSoundIcon();
  }
  function toggleSound() {
    soundEnabled = !soundEnabled;
    localStorage.setItem("tempbox.sound", soundEnabled ? "on" : "off");
    updateSoundIcon();
    showToast(soundEnabled ? "🔔 Đã bật âm thanh" : "🔕 Đã tắt âm thanh");
  }
  function updateSoundIcon() {
    el.soundToggle.textContent = soundEnabled ? "🔔" : "🔕";
  }

  // ===================== BROWSER NOTIFICATIONS =====================
  let notifPermission = Notification.permission || "default";

  async function requestNotifPermission() {
    if (!("Notification" in window)) return;
    if (Notification.permission === "default") {
      notifPermission = await Notification.requestPermission();
    } else {
      notifPermission = Notification.permission;
    }
  }

  function sendBrowserNotification(title, body) {
    if (notifPermission !== "granted") return;
    if (!document.hidden) return; // only when tab is hidden
    try { new Notification(title, { body, icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📬</text></svg>" }); } catch (_) {}
  }

  // ===================== FAVICON BADGE =====================
  const originalTitle = document.title;
  let unreadCount = 0;

  function updateFaviconBadge(count) {
    unreadCount = count;
    if (count > 0) {
      document.title = "(" + count + ") " + originalTitle;
      // Draw badge on favicon
      const canvas = document.createElement("canvas");
      canvas.width = 32; canvas.height = 32;
      const ctx = canvas.getContext("2d");
      ctx.font = "22px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("📬", 16, 22);
      ctx.fillStyle = "#ff4444";
      ctx.beginPath(); ctx.arc(24, 8, 8, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "bold 10px sans-serif";
      ctx.fillText(count > 9 ? "9+" : String(count), 24, 12);
      const link = document.querySelector("link[rel='icon']") || document.createElement("link");
      link.rel = "icon";
      link.href = canvas.toDataURL();
      document.head.appendChild(link);
    } else {
      document.title = originalTitle;
    }
  }

  // ===================== AUTO-DELETE OLD EMAILS =====================
  let autoDeleteMinutes = parseInt(localStorage.getItem("tempbox.autoDelete") || "0", 10); // 0 = disabled

  function checkAutoDelete() {
    if (!autoDeleteMinutes || !messages.length) return;
    const now = Date.now();
    const toDelete = messages.filter((m) => {
      const msgTime = new Date(m.date).getTime();
      return !isNaN(msgTime) && (now - msgTime) > autoDeleteMinutes * 60000;
    });
    for (const m of toDelete) {
      try { if (currentProvider.deleteMessage) currentProvider.deleteMessage(m.id); } catch (_) {}
      messages = messages.filter((x) => x.id !== m.id);
    }
    if (toDelete.length) {
      el.count.textContent = messages.length;
      renderList();
      if (!messages.length) el.empty.style.display = "block";
    }
  }

  function setAutoDelete(minutes) {
    autoDeleteMinutes = minutes;
    localStorage.setItem("tempbox.autoDelete", String(minutes));
    if (minutes > 0) showToast("⏱️ Tự xóa email sau " + minutes + " phút");
    else showToast("⏱️ Đã tắt tự động xóa");
  }

  // ===================== SHARE LINK =====================
  function shareEmail() {
    if (!currentProvider) return;
    const addr = currentProvider.getAddress();
    if (!addr) return;
    const shareUrl = window.location.origin + "?email=" + encodeURIComponent(addr);
    navigator.clipboard.writeText(shareUrl).then(() => showToast("🔗 Đã sao chép link chia sẻ"));
  }

  // ===================== KEYBOARD SHORTCUTS =====================
  function handleShortcuts(e) {
    // Don't trigger when typing in search
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (el.overlay.style.display !== "none" || el.qrOverlay.style.display !== "none") {
      if (e.key === "Escape") { closeModal(); closeQR(); }
      return;
    }
    switch (e.key.toLowerCase()) {
      case "c": copyAddress(); break;
      case "n": createNew(); break;
      case "r": poll(true); countdown = POLL_INTERVAL; break;
      case "q": showQR(); break;
      case "s": shareEmail(); break;
      case "/": e.preventDefault(); el.searchInput.focus(); break;
    }
  }

  // ===================== FAST POLL MODE (waiting for OTP) =====================
  let fastPollMode = false;

  function toggleFastPoll() {
    fastPollMode = !fastPollMode;
    stopTimers();
    if (fastPollMode) {
      countdown = 3;
      countdownTimer = setInterval(() => {
        countdown--;
        if (countdown <= 0) { poll(true); countdown = 3; }
        el.countdown.textContent = Math.max(0, countdown);
      }, 1000);
      showToast("⚡ Chế độ nhanh: refresh mỗi 3s");
      el.refreshBtn.querySelector(".btn-label").textContent = "⚡ 3s";
    } else {
      startTimers();
      showToast("🔄 Chế độ bình thường: refresh mỗi 10s");
      el.refreshBtn.querySelector(".btn-label").textContent = "Làm mới";
    }
  }

  // ===================== EVENTS =====================
  el.copyBtn.addEventListener("click", copyAddress);
  el.qrBtn.addEventListener("click", showQR);
  el.shareBtn.addEventListener("click", shareEmail);
  el.refreshBtn.addEventListener("click", () => { poll(true); countdown = POLL_INTERVAL; });
  el.refreshBtn.addEventListener("dblclick", toggleFastPoll); // double-click to toggle fast mode
  el.newBtn.addEventListener("click", createNew);
  el.themeToggle.addEventListener("click", toggleTheme);
  el.soundToggle.addEventListener("click", toggleSound);
  el.modalClose.addEventListener("click", closeModal);
  el.modalDownload.addEventListener("click", () => { if (currentFullMsg) downloadEml(currentFullMsg); });
  el.modalForward.addEventListener("click", forwardEmail);
  el.modalDelete.addEventListener("click", () => { if (currentMsgId) deleteMessage(currentMsgId); });
  el.overlay.addEventListener("click", (e) => { if (e.target === el.overlay) closeModal(); });
  el.qrClose.addEventListener("click", closeQR);
  el.qrOverlay.addEventListener("click", (e) => { if (e.target === el.qrOverlay) closeQR(); });
  el.deleteAllBtn.addEventListener("click", deleteAll);
  el.searchInput.addEventListener("input", () => renderList());
  el.autoDeleteSelect.addEventListener("change", (e) => setAutoDelete(parseInt(e.target.value, 10)));
  document.addEventListener("keydown", handleShortcuts);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopTimers();
    else { if (currentProvider) { poll(true); if (fastPollMode) toggleFastPoll(); else startTimers(); } updateFaviconBadge(0); }
  });

  // Auto-delete check every 30s
  setInterval(checkAutoDelete, 30000);

  // ===================== START =====================
  totalReceived = parseInt(localStorage.getItem("tempbox.totalReceived") || "0", 10);
  el.totalReceived.textContent = totalReceived;
  el.autoDeleteSelect.value = String(autoDeleteMinutes);
  initTheme();
  initSound();
  requestNotifPermission();
  renderHistory();
  init();
})();
