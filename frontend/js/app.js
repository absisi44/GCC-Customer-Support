// ======================================================
// GCC Customer Support AI — منطق التطبيق الكامل
// يوم 3 من الكورس: ربط الواجهة بـ Multi-Agent Backend
//
// هذا الملف يشرح للطلاب كيف:
//  1. نتحقق من حالة الـ Backend (Health Check)
//  2. نرسل طلب Chat POST ونعالج الرد
//  3. نعرض الرسائل وبيانات الوكيل ديناميكياً
//  4. ندير حالة الجلسة (Session State)
// ======================================================

// ============================================================
// القسم 1: الإعدادات الأساسية — Configuration
// ============================================================

/**
 * عنوان الـ Backend API
 * غيّر هذا إذا كان السيرفر يعمل على منفذ مختلف
 */
const API_BASE = "http://localhost:8000";

/**
 * حالة التطبيق الكاملة — App State
 * نحتفظ بكل البيانات في كائن واحد لسهولة الإدارة
 */
const state = {
    isLoading: false,           // هل يوجد طلب جارٍ الآن؟
    messageCount: 0,            // عدد الرسائل في الجلسة
    sessionStart: null,         // وقت بدء الجلسة
    lastResponseTime: null,     // وقت آخر استجابة
    agentCallLog: [],           // سجل كل الوكلاء المستدعاة
    currentCustomer: null,      // بيانات العميل الحالي
};

/**
 * خريطة الوكلاء — Agent Map
 * تربط اسم الوكيل من الـ API بالأيقونة والدور والفئة
 */
const AGENT_MAP = {
    "router":              { icon: "🔀", nameAr: "الموجّه",            role: "يحلل الرسالة ويُحدد الوكيل المناسب",   cls: "router"   },
    "shipping_executor":   { icon: "📦", nameAr: "وكيل الشحن",         role: "يتتبع الطلبات والشحنات",               cls: "shipping" },
    "billing_executor":    { icon: "💰", nameAr: "وكيل الفواتير",      role: "يعرض تفاصيل الفواتير والمدفوعات",      cls: "billing"  },
    "rag_node":            { icon: "📚", nameAr: "قاعدة المعرفة (RAG)", role: "يجيب من سياسات الشركة في ChromaDB",    cls: "rag"      },
    "technical_handler":   { icon: "🔧", nameAr: "الدعم التقني",        role: "يعالج المشكلات التقنية",               cls: "technical"},
    "human_handoff":       { icon: "🙋", nameAr: "التحويل لموظف",      role: "يحوّل المحادثة لموظف بشري",            cls: "human"    },
};

// ============================================================
// القسم 2: تهيئة التطبيق — App Initialization
// ============================================================

/**
 * عند تحميل الصفحة:
 *  1. نولّد معرّف جلسة جديد
 *  2. نتحقق من حالة الـ Backend
 *  3. نُحدّث واجهة بيانات العميل
 */
document.addEventListener("DOMContentLoaded", () => {
    generateSessionId();         // توليد Thread ID تلقائي
    checkHealth();               // فحص الاتصال فور فتح الصفحة
    onCustomerChange();          // تحديث رأس الدردشة
    focusInput();                // التركيز على حقل الإدخال
    state.sessionStart = Date.now();
});

// ============================================================
// القسم 3: Health Check — فحص حالة الـ Backend
// ============================================================

/**
 * checkHealth()
 * يرسل GET /  ويعرض حالة الاتصال في الرأس
 *
 * درس للطلاب: هذا هو أبسط طلب HTTP — لا يحتاج body
 */
async function checkHealth() {
    const dot   = document.getElementById("statusDot");
    const text  = document.getElementById("statusText");
    const btn   = document.getElementById("healthCheckBtn");

    // نُظهر حالة "جاري الفحص"
    dot.className  = "status-dot checking";
    text.textContent = "جاري الفحص...";
    btn.disabled   = true;

    try {
        // ===== الطلب الفعلي =====
        const response = await fetch(`${API_BASE}/`, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });

        if (response.ok) {
            const data = await response.json();
            // ✅ الاتصال ناجح
            dot.className    = "status-dot online";
            text.textContent = `✅ متصل — ${data.service || "GCC AI"}`;
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (err) {
        // ❌ خطأ في الاتصال
        dot.className    = "status-dot offline";
        text.textContent = `❌ غير متصل (${err.message})`;
    } finally {
        btn.disabled = false;
    }
}

// ============================================================
// القسم 4: إدارة الجلسة — Session Management
// ============================================================

/**
 * generateSessionId()
 * يولّد Thread ID فريد لكل جلسة
 * يظهر في حقل "معرّف الجلسة" في الشريط الجانبي
 */
function generateSessionId() {
    const id = `session-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    document.getElementById("threadId").value = id;
}

/**
 * regenerateSession()
 * زر 🔀 — يولّد Thread ID جديد (لجلسة منفصلة)
 */
function regenerateSession() {
    generateSessionId();
    showNotice("تم إنشاء معرّف جلسة جديد");
}

/**
 * startNewSession()
 * يمسح المحادثة ويبدأ من صفر
 */
function startNewSession() {
    clearChat();
    generateSessionId();
    resetStats();
    showNotice("تم بدء جلسة جديدة ✨");
}

/**
 * onCustomerChange()
 * يُحدّث رأس الدردشة عند تغيير العميل من القائمة
 */
function onCustomerChange() {
    const customerId = document.getElementById("customerId").value;
    const tier       = document.getElementById("accountTier").value;
    document.getElementById("chatHeaderCustomer").textContent = customerId;
    document.getElementById("chatHeaderTier").textContent     = tier === "VIP" ? "VIP ⭐" : "Standard";
}

// ============================================================
// القسم 5: إرسال الرسائل — Send Message
// ============================================================

/**
 * sendMessage()
 * الدالة الرئيسية: تأخذ النص من الحقل وترسله للـ Backend
 *
 * درس للطلاب: هذا هو طلب POST مع JSON body
 * لاحظ: async/await لجعل الكود أسهل للقراءة
 */
async function sendMessage() {
    // نأخذ النص ونتحقق أنه غير فارغ
    const input   = document.getElementById("messageInput");
    const message = input.value.trim();

    if (!message || state.isLoading) return;

    // نأخذ باقي الإعدادات من الواجهة
    const customerId = document.getElementById("customerId").value;
    const tier       = document.getElementById("accountTier").value;
    const threadId   = document.getElementById("threadId").value;
    const ticketId   = document.getElementById("ticketId").value.trim() || null;

    // 1️⃣ نضيف فقاعة المستخدم فوراً (لا ننتظر الرد)
    addUserMessage(message);
    input.value = "";
    autoResize(input);

    // 2️⃣ نُخفي الأمثلة بعد أول رسالة
    document.getElementById("quickExamples").style.display = "none";
    document.getElementById("welcomeState")?.remove();

    // 3️⃣ نُظهر مؤشر التحميل (Typing Indicator)
    const typingId = showTypingIndicator();

    // 4️⃣ نضبط حالة التحميل
    state.isLoading = true;
    document.getElementById("sendBtn").disabled = true;
    const startTime = Date.now();

    try {
        // ===== الطلب الفعلي إلى /chat =====
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept":       "application/json"
            },
            // نبني الـ body بنفس حقول ChatRequest في الـ Backend
            body: JSON.stringify({
                message:         message,
                customer_id:     customerId,
                account_tier:    tier,
                thread_id:       threadId,
                open_ticket_id:  ticketId,
            })
        });

        // نحسب وقت الاستجابة
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${response.status}`);
        }

        // ===== معالجة الرد =====
        const data = await response.json();

        // 5️⃣ نُزيل مؤشر التحميل
        removeTypingIndicator(typingId);

        // 6️⃣ نضيف فقاعة الوكيل
        addAgentMessage(data.answer, data.active_agent);

        // 7️⃣ نُحدّث اللوحة التعليمية
        updateAgentPanel(data.active_agent, data.messages_count);

        // 8️⃣ نعرض بطاقات البيانات إذا وُجدت
        if (data.customer)   renderCustomerCard(data.customer);
        if (data.complaint)  renderComplaintCard(data.complaint);

        // 9️⃣ نُحدّث الإحصائيات
        updateStats(data.messages_count, elapsed);

    } catch (err) {
        removeTypingIndicator(typingId);
        addErrorMessage(`حدث خطأ: ${err.message}`);
    } finally {
        state.isLoading = false;
        document.getElementById("sendBtn").disabled = false;
        focusInput();
    }
}

// ============================================================
// القسم 6: بناء الرسائل — Message Builders
// ============================================================

/**
 * addUserMessage(text)
 * يُضيف فقاعة رسالة المستخدم في يمين الشاشة
 */
function addUserMessage(text) {
    const window = document.getElementById("messagesWindow");
    const time   = getTimeNow();

    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper user";
    wrapper.innerHTML = `
        <div class="message-avatar">👤</div>
        <div>
            <div class="message-bubble">${escapeHTML(text)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    window.appendChild(wrapper);
    scrollToBottom();
    state.messageCount++;
}

/**
 * addAgentMessage(text, agentKey)
 * يُضيف فقاعة رد الوكيل في يسار الشاشة
 * مع شارة اسم الوكيل فوق النص
 */
function addAgentMessage(text, agentKey) {
    const window = document.getElementById("messagesWindow");
    const time   = getTimeNow();
    const agent  = getAgentInfo(agentKey);

    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper agent";
    wrapper.innerHTML = `
        <div class="message-avatar">${agent.icon}</div>
        <div>
            <div class="message-bubble">
                <div class="agent-badge ${agent.cls}">${agent.icon} ${agent.nameAr}</div>
                <div>${formatMarkdown(text)}</div>
            </div>
            <div class="message-time">${time}</div>
        </div>
    `;
    window.appendChild(wrapper);
    scrollToBottom();
}

/**
 * addErrorMessage(text)
 * يُضيف رسالة خطأ بأسلوب مميز
 */
function addErrorMessage(text) {
    const window = document.getElementById("messagesWindow");
    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper agent";
    wrapper.innerHTML = `
        <div class="message-avatar">⚠️</div>
        <div>
            <div class="message-bubble" style="border-color:var(--color-error);background:rgba(239,68,68,0.08)">
                <div class="agent-badge" style="background:rgba(239,68,68,0.2);color:#f87171">⚠️ خطأ</div>
                <div>${escapeHTML(text)}</div>
            </div>
        </div>
    `;
    window.appendChild(wrapper);
    scrollToBottom();
}

// ============================================================
// القسم 7: مؤشر التحميل — Typing Indicator
// ============================================================

/**
 * showTypingIndicator()
 * يُضيف نقاط "يكتب..." أثناء انتظار الرد
 * يعيد ID فريد لإزالته لاحقاً
 */
function showTypingIndicator() {
    const window = document.getElementById("messagesWindow");
    const id     = `typing-${Date.now()}`;

    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper agent typing-indicator";
    wrapper.id        = id;
    wrapper.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    window.appendChild(wrapper);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    document.getElementById(id)?.remove();
}

// ============================================================
// القسم 8: اللوحة التعليمية — Agent Panel
// ============================================================

/**
 * updateAgentPanel(agentKey, messageCount)
 * يُحدّث:
 *  - بطاقة "الوكيل النشط الحالي"
 *  - سجل الاستدعاءات
 *  - تمييز الوكيل في دليل الوكلاء
 */
function updateAgentPanel(agentKey, messageCount) {
    const agent = getAgentInfo(agentKey);

    // تحديث البطاقة الرئيسية
    document.getElementById("agentIcon").textContent   = agent.icon;
    document.getElementById("agentName").textContent   = agent.nameAr;
    document.getElementById("agentRole").textContent   = agent.role;

    // تأثير توهّج عند التغيير
    const card = document.getElementById("activeAgentCard");
    card.classList.remove("highlight");
    void card.offsetWidth; // reflow لإعادة تشغيل الحركة
    card.classList.add("highlight");

    // تمييز العنصر في دليل الوكلاء
    document.querySelectorAll(".legend-item").forEach(el => el.classList.remove("active-item"));
    const legendItem = document.querySelector(`.legend-item[data-agent="${agent.cls}"]`);
    if (legendItem) legendItem.classList.add("active-item");

    // إضافة للسجل
    const logEntry = {
        agent: agentKey,
        info:  agent,
        time:  getTimeNow(),
        num:   state.agentCallLog.length + 1,
    };
    state.agentCallLog.push(logEntry);
    addLogEntry(logEntry);
}

/**
 * addLogEntry(entry)
 * يُضيف سطراً في سجل الاستدعاءات
 */
function addLogEntry(entry) {
    const log = document.getElementById("agentLog");

    // نُزيل "لم تبدأ المحادثة" إذا كانت موجودة
    const empty = log.querySelector(".log-empty");
    if (empty) empty.remove();

    const item = document.createElement("div");
    item.className = `log-entry ${entry.info.cls}`;
    item.innerHTML = `
        <span class="log-num">#${entry.num}</span>
        <span>${entry.info.icon}</span>
        <span class="log-name">${entry.info.nameAr}</span>
        <span class="log-time">${entry.time}</span>
    `;
    // نضيف في الأعلى (أحدث أولاً)
    log.insertBefore(item, log.firstChild);
}

// ============================================================
// القسم 9: بطاقات البيانات — Data Cards
// ============================================================

/**
 * renderCustomerCard(customer)
 * يُظهر بطاقة "بيانات العميل" بعد استلام customer من الرد
 *
 * درس للطلاب: هذه البيانات تأتي مباشرة من الـ ChatResponse
 */
function renderCustomerCard(customer) {
    const body = document.getElementById("customerCardBody");
    body.innerHTML = "";

    // نبني عناصر البيانات ديناميكياً
    const fields = [
        { label: "رقم العميل",    value: customer.customer_id    || "—" },
        { label: "الاسم",         value: customer.name           || "—" },
        { label: "مستوى الخدمة", value: customer.tier           || "—" },
        { label: "البريد",        value: customer.email          || "—", full: true },
    ];

    fields.forEach(f => {
        const div = document.createElement("div");
        div.className = `info-item${f.full ? " full-width" : ""}`;
        div.innerHTML = `
            <span class="info-label">${f.label}</span>
            <span class="info-value">${escapeHTML(String(f.value))}</span>
        `;
        body.appendChild(div);
    });

    document.getElementById("customerCard").classList.remove("hidden");
}

/**
 * renderComplaintCard(complaint)
 * يُظهر بطاقة "تفاصيل الشكوى" إذا جاءت في الرد
 */
function renderComplaintCard(complaint) {
    const body = document.getElementById("complaintCardBody");
    body.innerHTML = "";

    const fields = [
        { label: "رقم التذكرة",  value: complaint.ticket_id    || complaint.id    || "—" },
        { label: "النوع",         value: complaint.type         || complaint.category || "—" },
        { label: "الحالة",        value: complaint.status       || "—" },
        { label: "الأولوية",     value: complaint.priority     || "—" },
        { label: "الوصف",        value: complaint.description  || complaint.notes  || "—", full: true },
    ];

    fields.forEach(f => {
        if (f.value === "—") return; // نتخطى الحقول الفارغة
        const div = document.createElement("div");
        div.className = `info-item${f.full ? " full-width" : ""}`;
        div.innerHTML = `
            <span class="info-label">${f.label}</span>
            <span class="info-value">${escapeHTML(String(f.value))}</span>
        `;
        body.appendChild(div);
    });

    document.getElementById("complaintCard").classList.remove("hidden");
}

/**
 * closeCard(cardId)
 * يُغلق بطاقة البيانات
 */
function closeCard(cardId) {
    document.getElementById(cardId).classList.add("hidden");
}

// ============================================================
// القسم 10: إعادة تهيئة قاعدة المعرفة — Reindex KB
// ============================================================

/**
 * reindexKB()
 * يرسل POST /ingest لإعادة تحميل ChromaDB
 *
 * درس للطلاب: هذا طلب POST بدون body
 */
async function reindexKB() {
    const statusEl = document.getElementById("ingestStatus");
    statusEl.className  = "ingest-status";
    statusEl.textContent = "⏳ جاري إعادة التهيئة...";

    try {
        const response = await fetch(`${API_BASE}/ingest`, {
            method: "POST",
            headers: { "Accept": "application/json" }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            statusEl.className  = "ingest-status success";
            statusEl.textContent = `✅ ${data.message}`;
        } else {
            throw new Error(data.detail || "فشل الطلب");
        }
    } catch (err) {
        statusEl.className  = "ingest-status error";
        statusEl.textContent = `❌ خطأ: ${err.message}`;
    }
}

// ============================================================
// القسم 11: الأمثلة السريعة — Quick Examples
// ============================================================

/**
 * useExample(message)
 * عند الضغط على مثال جاهز، نضعه في حقل الإدخال ونرسله
 */
function useExample(message) {
    const input = document.getElementById("messageInput");
    input.value = message;
    autoResize(input);
    sendMessage();
}

// ============================================================
// القسم 12: دوال مساعدة — Utility Functions
// ============================================================

/**
 * handleKeyDown(event)
 * Enter = إرسال، Shift+Enter = سطر جديد
 */
function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * autoResize(textarea)
 * يُعيد حساب ارتفاع الحقل تلقائياً مع الكتابة
 */
function autoResize(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
}

/**
 * clearChat()
 * يمسح كل الرسائل وإحصائيات الجلسة
 */
function clearChat() {
    const window = document.getElementById("messagesWindow");
    window.innerHTML = `
        <div class="welcome-state" id="welcomeState">
            <div class="welcome-icon">🤖</div>
            <h3>مرحباً بك في نظام دعم العملاء</h3>
            <p>اكتب استفسارك أو اختر أحد الأمثلة أدناه للبدء</p>
            <p class="welcome-hint">الوكلاء المتاحون: <strong>الشحن · الفواتير · سياسات الشركة · التحويل لموظف</strong></p>
        </div>
    `;

    // نُظهر الأمثلة مجدداً
    document.getElementById("quickExamples").style.display = "";

    // نُغلق البطاقات
    closeCard("customerCard");
    closeCard("complaintCard");

    // نُعيد السجل
    const log = document.getElementById("agentLog");
    log.innerHTML = `<div class="log-empty">لم تبدأ المحادثة بعد</div>`;
    state.agentCallLog = [];

    // نُعيد بطاقة الوكيل
    document.getElementById("agentIcon").textContent = "🔀";
    document.getElementById("agentName").textContent = "في انتظار الرسالة الأولى";
    document.getElementById("agentRole").textContent = "لم يتم استدعاء أي وكيل بعد";
    document.querySelectorAll(".legend-item").forEach(el => el.classList.remove("active-item"));

    resetStats();
}

/**
 * resetStats()
 * يُعيد ضبط إحصائيات الجلسة
 */
function resetStats() {
    state.messageCount = 0;
    document.getElementById("statMessages").textContent = "0";
    document.getElementById("statDuration").textContent = "0s";
    state.sessionStart = Date.now();
}

/**
 * updateStats(count, elapsed)
 * يُحدّث أرقام الإحصائيات
 */
function updateStats(count, elapsed) {
    document.getElementById("statMessages").textContent = count || state.messageCount;
    document.getElementById("statDuration").textContent = elapsed + "s";
}

/**
 * scrollToBottom()
 * يُنزل نافذة الرسائل لأسفل
 */
function scrollToBottom() {
    const window = document.getElementById("messagesWindow");
    window.scrollTop = window.scrollHeight;
}

/**
 * focusInput()
 * يضع التركيز على حقل الكتابة
 */
function focusInput() {
    document.getElementById("messageInput")?.focus();
}

/**
 * getTimeNow()
 * يعيد الوقت الحالي بصيغة HH:MM
 */
function getTimeNow() {
    return new Date().toLocaleTimeString("ar-SA", {
        hour:   "2-digit",
        minute: "2-digit",
        hour12: true,
    });
}

/**
 * getAgentInfo(key)
 * يعيد معلومات الوكيل من الخريطة
 * يتعامل مع أسماء غير معروفة برشاقة
 */
function getAgentInfo(key) {
    if (!key) return { icon: "🤖", nameAr: "غير محدد", role: "وكيل غير معروف", cls: "router" };

    // نُجرّب المطابقة المباشرة أولاً
    if (AGENT_MAP[key]) return AGENT_MAP[key];

    // ثم البحث الجزئي (مثلاً "shipping" في "shipping_executor")
    const lower = key.toLowerCase();
    if (lower.includes("shipping")) return AGENT_MAP["shipping_executor"];
    if (lower.includes("billing"))  return AGENT_MAP["billing_executor"];
    if (lower.includes("rag"))      return AGENT_MAP["rag_node"];
    if (lower.includes("human") || lower.includes("handoff")) return AGENT_MAP["human_handoff"];
    if (lower.includes("technical")) return AGENT_MAP["technical_handler"];

    // الافتراضي
    return { icon: "🤖", nameAr: key, role: "وكيل متخصص", cls: "router" };
}

/**
 * escapeHTML(str)
 * يمنع XSS — مهم جداً عند عرض نصوص من المستخدم
 *
 * درس للطلاب: لا تضع مدخلات المستخدم مباشرة في innerHTML
 */
function escapeHTML(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * formatMarkdown(text)
 * تحويل بسيط للـ Markdown في ردود الوكيل:
 *  **굵은** → <strong>
 *  줄바꿈 → <br>
 */
function formatMarkdown(text) {
    return escapeHTML(text)
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g,     "<em>$1</em>")
        .replace(/\n/g,            "<br>");
}

/**
 * showNotice(msg)
 * يُظهر إشعاراً مؤقتاً في نافذة الرسائل
 */
function showNotice(msg) {
    const window = document.getElementById("messagesWindow");
    const notice = document.createElement("div");
    notice.style.cssText = `
        text-align:center;
        font-size:0.75rem;
        color:var(--color-text-muted);
        padding:6px 0;
        animation:fadeIn 0.3s ease;
    `;
    notice.textContent = `— ${msg} —`;
    window.appendChild(notice);
    scrollToBottom();
    setTimeout(() => notice.remove(), 4000);
}
