class NeonSVG extends HTMLElement {
    constructor() {
        super();
        this.containerId = this.getAttribute("container-id");
        this.src = this.getAttribute("src");
    }

    async connectedCallback() {
        //QUOTE: Code based on Danny Engelman <load-file>
        //https://dev.to/dannyengelman/load-file-web-component-add-external-content-to-the-dom-1nd
        this.shadowRoot || this.attachShadow({ mode: "open" });
        this.shadowRoot.innerHTML = `<div id="${this.containerId}">` +
            await (await fetch(this.src)).text() + '</div>';
        this.shadowRoot.append(...this.children);
        this.hasAttribute("replaceWith") && this.replaceWith(...this.shadowRoot.children);
        //UNQUOTE
        this.init();
    }

    init() {
    }

    applyAll(selectors, lambda) {
        let s = (Array.isArray(selectors)) ? selectors.join(",") : selectors;
        for (let e of this.svg.querySelectorAll(s)) {
            lambda(e);
        }
    }

    registerOnClick(selector, func, style = null) {
        let e = this.svg.querySelector(selector);
        e.addEventListener("click", func);
        if (style !== null && !e.classList.contains(style))
            e.classList.add(style);
    }

    setText(selectors, text) {
        this.applyAll(selectors, (e => {
            e.textContent = text;
        }));
    }

    resetColor(selectors) {
        this.applyAll(selectors, (e) => {
            e.style.fill = null;
            e.style.stroke = null;
        });
    }

    setColor(selectors, color) {
        this.applyAll(selectors, (e) => {
            e.style.fill = color;
            e.style.stroke = color;
        });
    }

    setStrokeColor(selectors, color) {
        this.applyAll(selectors, (e) => {
            e.style.stroke = color;
        });
    }

    resetVisibility(selectors) {
        this.applyAll(selectors, (e) => {
            e.style.visibility = null;
        });
    }

    setVisibility(selectors, isVisible) {
        this.applyAll(selectors, (e) => {
            e.style.visibility = (isVisible) ? "visible" : "hidden";
        });
    }

    toogleClass(selectors, clazz) {
        this.applyAll(selectors, (e) => {
            e.classList.toggle(clazz);
        });
    }

    removeClass(selectors, clazz) {
        this.applyAll(selectors, (e) => {
            if (e.classList.contains(clazz))
                e.classList.remove(clazz);
        });
    }

    addClass(selectors, clazz) {
        this.applyAll(selectors, (e) => {
            if (!e.classList.contains(clazz))
                e.classList.add(clazz);
        });
    }

    enterFullscreen() {
        let e = this.shadowRoot.querySelector("#" + this.containerId);
        if (e.requestFullscreen) {
            e.requestFullscreen();
        } else if (e.webkitRequestFullscreen) { /* Safari */
            e.webkitRequestFullscreen();
        } else if (e.msRequestFullscreen) { /* IE11 */
            e.msRequestFullscreen();
        }
    }

    exitFullscreen() {
        let e = document;
        if (document.exitFullscreen) {
            e.exitFullscreen();
        } else if (e.webkitExitFullscreen) { /* Safari */
            e.webkitExitFullscreen();
        } else if (e.msExitFullscreen) { /* IE11 */
            e.msExitFullscreen();
        }
    }
}