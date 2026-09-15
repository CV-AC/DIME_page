const dialog = document.querySelector("#figure-dialog");
const dialogImage = dialog.querySelector("img");
const dialogCaption = dialog.querySelector("p");

document.querySelectorAll("[data-lightbox]").forEach((button) => {
  button.addEventListener("click", () => {
    dialogImage.src = button.dataset.lightbox;
    dialogImage.alt = button.dataset.caption || "Expanded paper figure";
    dialogCaption.textContent = button.dataset.caption || "";
    dialog.showModal();
  });
});

dialog.querySelector(".lightbox-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
dialog.addEventListener("close", () => {
  dialogImage.removeAttribute("src");
});

const citation = `@article{yu2026dime,
  title={DIME: Scaling Self-Supervised Facial Representation Learning via Differential Masked Autoencoding},
  author={Yu, Hao and Chen, Haoyu and Wei, Hui and Jiang, Yan and Sebe, Nicu and Zhao, Guoying},
  year={2026}
}`;

document.querySelector("#citation-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  const label = button.querySelector("span");
  try {
    await navigator.clipboard.writeText(citation);
    label.textContent = "Citation copied";
  } catch {
    label.textContent = "Copy unavailable";
  }
  window.setTimeout(() => { label.textContent = "Copy BibTeX citation"; }, 2400);
});
