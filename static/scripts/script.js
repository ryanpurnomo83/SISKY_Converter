document.addEventListener("DOMContentLoaded", () => {
    // ===== Dropzone =====
    const fileInput = document.getElementById("file");
    const fileName = document.getElementById("file-name");
    const dropzone = document.getElementById("dropzone");

    function showFileName() {
        if (!fileInput || !fileName || !dropzone) return;
        const hasFile = fileInput.files.length > 0;
        fileName.textContent = hasFile ? fileInput.files[0].name : "Pilih file .docx";
        dropzone.classList.toggle("has-file", hasFile);
    }

    if (fileInput && fileName && dropzone) {
        fileInput.addEventListener("change", showFileName);

        ["dragenter", "dragover"].forEach(ev =>
            dropzone.addEventListener(ev, e => {
                e.preventDefault();
                dropzone.classList.add("is-over");
            }));

        ["dragleave", "drop"].forEach(ev =>
            dropzone.addEventListener(ev, () => dropzone.classList.remove("is-over")));
    }

    // ===== Hasil konversi (hanya jika ada) =====
    const resultBox = document.getElementById("result-box");
    if (resultBox) {
        const resultText = resultBox.dataset.result;
        const downloadName = resultBox.dataset.downloadName;

        const copyBtn = document.getElementById("copy-btn");
        const downloadBtn = document.getElementById("download-btn");

        copyBtn.addEventListener("click", async () => {
            await navigator.clipboard.writeText(resultText);
            copyBtn.textContent = "Tersalin";
            setTimeout(() => (copyBtn.textContent = "Salin"), 1800);
        });

        downloadBtn.addEventListener("click", () => {
            const blob = new Blob([resultText], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = downloadName;
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    const docTypeInput = document.querySelector("input[name='doc_type']");
    const formatDD = document.querySelector("input[name='format']").closest(".js-dropdown");
    const resultDD = document.querySelector("input[name='format_result']").closest(".js-dropdown");
    // const result2DD = document.querySelector("input[name='format_assignment_result']").closest(".js-dropdown");
    // const result3DD = document.querySelector("input[name='format_questionAnswer_result']").closest(".js-dropdown");
    const formatMap = JSON.parse(formatDD.dataset.formats);

    function selectOption(dd, li){
        const toggle = dd.querySelector(".dropdown-toggle");
        const input = dd.querySelector("input[type='hidden']");
        input.value = li.dataset.value;
        toggle.querySelector(".dropdown-label").textContent = li.querySelector("span").textContent;

        const liIcon = li.querySelector("i");
        const toggleIcon = toggle.querySelector("i");
        if (liIcon && toggleIcon) {
            toggleIcon.className = liIcon.className;
            toggleIcon.style.color = "";
        }
    }

    function renderMenu(dd, options){
        const menu = dd.querySelector(".dropdown-menu");
        const input = dd.querySelector("input[type='hidden']");
        menu.innerHTML = "";
        dd.classList.toggle("d-none", options.length === 0);
        input.disabled = options.length === 0;

        options.forEach(opt => {
            const li = document.createElement("li");
            li.setAttribute("role", "option");
            li.dataset.value = opt.value;
            li.innerHTML = `<i class="bi ${opt.icon}"></i><span> ${opt.label}</span>`;
            menu.appendChild(li);
        });

        if (options.length) selectOption(dd, menu.firstElementChild);
    }

    function renderFormats(docType){
        /*
        const options = formatMap[docType] || [];
        const menu = formatDD.querySelector(".dropdown-menu");
        menu.innerHTML = "";

        options.forEach(opt => {
            const li = document.createElement("li");
            li.setAttribute("role", "option");
            li.dataset.value = opt.value;
            li.innerHTML = `<i class="bi ${opt.icon}"></i><span> ${opt.label}</span>`;
            menu.appendChild(li);
        });

        if (options.length) selectOption(formatDD, menu.firstElementChild);
        */
        renderMenu(formatDD, formatMap[docType] || []);
        renderMenu(resultDD, formatMap[docType + "-result"] || []);
    }

   document.querySelectorAll(".js-dropdown").forEach(dd => {
    /*  
        const toggle = dd.querySelector(".dropdown-toggle");
        const input = dd.querySelector("input[type='hidden']");

        dd.querySelectorAll(".dropdown-menu li").forEach(li => {
            li.addEventListener("click", () => {
                input.value = li.dataset.value;
                toggle.querySelector(".dropdown-label").textContent = li.querySelector("span").textContent;
                const liIcon = li.querySelector("i");
                const toggleIcon = toggle.querySelector("i");
                if (liIcon && toggleIcon) {
                    toggleIcon.className = liIcon.className;
                    toggleIcon.style.color = "";
                }

                if (input.name === "format" && fileInput) {
                    fileInput.accept = li.dataset.accept;
                    fileInput.value = "";
                    showFileName();
                }
            });
        });
        */
        dd.querySelector(".dropdown-menu").addEventListener("click", e => {
            const li = e.target.closest("li");
            if (!li) return;
            selectOption(dd, li);
            if (dd.contains(docTypeInput)) renderFormats(docTypeInput.value);
        });
   });

   document.querySelectorAll(".js-dropdown").forEach(dd => {
        dd.querySelector(".dropdown-menu").addEventListener("click", e => {
            const li = e.target.closest("li");
            if (!li) return;
            selectOption(dd, li);
            if (dd.contains(docTypeInput)) renderFormats(docTypeInput.value);
        });
   });
   renderFormats(docTypeInput.value);
});