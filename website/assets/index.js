document.querySelectorAll("[data-copy-text]").forEach((button) => {
    button.addEventListener("click", async () => {
        const text = button.getAttribute("data-copy-text") || "";

        try {
            await copyText(text);
            button.classList.add("copied");
            button.setAttribute("aria-label", "Copied install command");
            button.setAttribute("title", "Copied");
            window.setTimeout(() => {
                button.classList.remove("copied");
                button.setAttribute("aria-label", "Copy install command");
                button.setAttribute("title", "Copy install command");
            }, 1400);
        } catch {
            button.classList.add("copy-failed");
            window.setTimeout(
                () => button.classList.remove("copy-failed"),
                1400,
            );
        }
    });
});

async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "0";
    textarea.style.left = "0";
    textarea.style.width = "1px";
    textarea.style.height = "1px";
    textarea.style.padding = "0";
    textarea.style.border = "0";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();

    try {
        if (!document.execCommand("copy")) {
            throw new Error("copy command failed");
        }
    } finally {
        textarea.remove();
    }
}

const demoToggles = document.querySelectorAll("[data-demo-toggle]");
const demoPanels = document.querySelectorAll("[data-demo-panel]");

demoToggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
        const target = toggle.getAttribute("data-demo-toggle");

        demoToggles.forEach((button) => {
            const active = button === toggle;
            button.classList.toggle("active", active);
            button.setAttribute("aria-pressed", String(active));
        });

        demoPanels.forEach((panel) => {
            panel.hidden = panel.getAttribute("data-demo-panel") !== target;
        });
    });
});
