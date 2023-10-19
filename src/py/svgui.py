from js import document, window, console
from pyodide.http import open_url
from pyodide.ffi import create_proxy
import asyncio


class DOMUtils:
    idx = 0

    @classmethod
    def to_list(cls, anything):
        if not isinstance(anything, list):
            return [anything]
        return anything

    @classmethod
    def get_shadown_root(cls, host_element):
        # Ensure shadow root is created
        if hasattr(host_element, "shadowRoot") and host_element.shadowRoot is not None:
            return host_element.shadowRoot
        else:
            return host_element.attachShadow(mode="open")

    @classmethod
    def append_shadow_and_layer(cls, parent_element, layer_id, src_url, css_urls):
        # Create a layer
        layer = document.createElement("div")
        if layer_id:
            layer.setAttribute("id", layer_id)
        parent_element.appendChild(layer)

        # Create shadow root
        shadow_root = cls.get_shadown_root(layer)

        # Load content if any
        if src_url:
            shadow_root.innerHTML = open_url(src_url).read()

        # Load css if any
        if css_urls:
            for css_url in css_urls:
                style = document.createElement("style")
                style.id = "s" + str(abs(hash(css_url)))
                style.textContent = open_url(css_url).read()
                shadow_root.appendChild(style)
        return shadow_root

    @classmethod
    def next_id(cls):
        cls.idx += 1
        return cls.idx


class Svgui:
    def __init__(self, root, targets):
        self.root = root
        self.targets = targets

    def __str__(self):
        return f"Svgui {[t.id for t in self.targets]}"

    def select_document(self):
        return Svgui(self.root, [document])

    def select(self, selectors):
        if isinstance(selectors, list):
            targets = self.root.querySelectorAll(",".join(selectors))
        else:
            targets = self.root.querySelectorAll(selectors)
        return Svgui(self.root, targets)

    def is_shadow_dom(self) -> bool:
        return hasattr(self.root.getRootNode(), "host")

    def add_event_listener(self, eventType, listener):
        for e in self.targets:
            e.addEventListener(eventType, create_proxy(listener))
        return self

    def toggle_class(self, classname):
        for c in DOMUtils.to_list(classname):
            for e in self.targets:
                e.classList.toggle(c)
        return self

    def add_class(self, classname):
        for c in DOMUtils.to_list(classname):
            for e in self.targets:
                e.classList.add(c)
        return self

    def remove_class(self, classname):
        for c in DOMUtils.to_list(classname):
            for e in self.targets:
                e.classList.remove(c)
        return self

    def contain_class(self, classname) -> bool:
        for e in self.targets:
            if e.classList.contains(classname):
                return True
        return False

    def classes(self):
        r = []
        for e in self.targets:
            r.append(e.classList)
        return r

    def style(self, attr_values: dict):
        for e in self.targets:
            for attribute, value in attr_values.items():
                setattr(e.style, attribute, value)
        return self

    def is_fullscreen(self) -> bool:
        if hasattr(document, "fullscreenElement"):
            return bool(document.fullscreenElement)
        elif hasattr(document, "webkitFullscreenElement"):
            return bool(document.webkitFullscreenElement)
        elif hasattr(document, "mozFullScreenElement"):
            return bool(document.mozFullScreenElement)
        return False

    def request_fullscreen(self):
        e = self.root.getRootNode().host if self.is_shadow_dom() else self.root
        if hasattr(e, "requestFullscreen"):
            e.requestFullscreen()
        elif hasattr(e, "webkitRequestFullscreen"):  # Safari
            e.webkitRequestFullscreen()
        elif hasattr(e, "msRequestFullscreen"):  # IE11
            e.msRequestFullscreen()
        return self

    def exit_fullscreen(self):
        e = document
        if hasattr(e, "exitFullscreen"):
            e.exitFullscreen()
        elif hasattr(e, "webkitExitFullscreen"):  # Safari
            e.webkitExitFullscreen()
        elif hasattr(e, "msExitFullscreen"):  # IE11
            e.msExitFullscreen()
        return self

    def toggle_fullscreen(self):
        if self.is_fullscreen():
            return self.exit_fullscreen()
        return self.request_fullscreen()

    def is_visible(self):
        style = window.getComputedStyle(self.targets[0])
        if style.display == "none":
            return False
        if style.visibility != "visible":
            return False
        if float(style.opacity) < 0.1:
            return False
        return True

    def hide(self):
        return self.style({"visibility": "hidden", "opacity": "0"})

    def show(self):
        return self.style({"visibility": "visible", "opacity": "1"})

    def toggle_visibility(self):
        if self.is_visible():
            self.hide()
        else:
            self.show()

    # --- shortcuts
    def set_checked(self, b):
        for e in self.targets:
            e.checked = b
        return self

    def set_value(self, value):
        for e in self.targets:
            e.value = value
        return self

    def text_content(self, text):
        for e in self.targets:
            e.textContent = text
        return self

    def all_color(self, color):
        return self.style({"fill": color, "stroke": color})

    def reset_all_color(self):
        return self.all_color("")

    def fill_color(self, color):
        return self.style({"fill": color})

    def stroke_color(self, color):
        return self.style({"stroke": color})

    def opacity(self, i):
        return self.style({"opacity": i})

    def font_family(self, fontface):
        return self.style({"fontFamily": fontface})
    
    def on_click(self, listener):
        for e in self.targets:
            e.addEventListener("click", create_proxy(listener))
        return self

    def on_input(self, listener):
        for element in self.targets:
            element.addEventListener("input", create_proxy(lambda event: listener(element, event)))
        return self

    def on_focusout(self, listener):
        for element in self.targets:
            element.addEventListener("focusout", create_proxy(lambda event: listener(element, event)))
        return self

    # --- Methods that depends on css
    def clickable(self):
        return self.add_class("clickable")

    def blink_show_hide(self, shows, hides):
        async def _effect():
            self.select(shows).add_class("blink-show")
            self.select(hides).add_class("blink-hide")
            # After a while remove the blinkIn/Out effect and set visibility
            await asyncio.sleep(0.5)
            self.select(shows).remove_class("blink-show").show()
            self.select(hides).remove_class("blink-hide").hide()

        asyncio.ensure_future(_effect())


class Div:
    def __init__(self, id=None):
        if id is not None:
            # Locate the host element
            host_element = document.getElementById(id)
            if host_element is None:
                raise NameError(f"Host element ({id}) not found")
            self.root = host_element
            self.target = host_element
        else:
            self.root = None
            self.target = None

    def is_shadow_dom(self) -> bool:
        return hasattr(self.root.getRootNode(), "host")

    def load_css(self, url):
        # unload previous loaded
        self.unload_css(url)
        style = document.createElement("style")
        style.id = "s" + str(abs(hash(url)))
        style.textContent = open_url(url).read()
        if self.is_shadow_dom():
            console.log(f"{self.root}: {url} loaded into shadow dom")
            self.root.appendChild(style)
        else:
            console.log(f"{self.root}: {url} loaded into document")
            document.head.appendChild(style)
        return self

    def unload_css(self, url):
        _id = "s" + str(abs(hash(url)))
        style = self.root.getRootNode().getElementById(_id)
        if style:
            style.remove()
        return self

    def load_url(self, url, append=True):
        if append:
            self.target.innerHTML += open_url(url).read()
        else:
            self.target.innerHTML = open_url(url).read()
        return self

    def load_html(self, url, append=True):
        self.load_url(url)
        first_child = self.target.firstElementChild
        if first_child is None:
            raise FileNotFoundError("Failed to load HTML:" + url)
        console.log(f"{self.target}: {url} HTML loaded. append={append}")
        return self

    def load_svg(self, url, append=True):
        self.load_url(url)
        first_svg = self.target.querySelector("svg:first-of-type")
        if first_svg is None:
            raise FileNotFoundError("Failed to load svg:" + url)
        console.log(f"{self.target}: {url} SVG loaded. append={append}")
        return self

    def load_inner_html(self, inner_html, append=True):
        if append:
            self.target.innerHTML += inner_html
        else:
            self.target.innerHTML = inner_html
        first_child = self.target.firstElementChild
        if first_child is None:
            raise FileNotFoundError("Invalid inner_html:" + inner_html)
        return self

    def shadow(self):
        # Preserve the original html
        original_innerHTML = self.target.innerHTML
        self.target.innerHTML = ""

        # Create a shadowRoot
        shadow_root = DOMUtils.get_shadown_root(self.target)
        child = shadow_root.firstElementChild

        # Create a layer if no existing child
        if child is None:
            child = document.createElement("div")
            child.innerHTML = original_innerHTML
            shadow_root.appendChild(child)
        div = Div()
        div.root = child
        div.target = child
        return div

    def popup(self, bg_id=None, bg_color="rgba(254, 0, 0, 0.5)", fg_id=None, fg_color="black"):
        if bg_id is None:
            bg_id = f"popup-bg-{DOMUtils.next_id()}"
        if fg_id is None:
            fg_id = f"popup-fg-{DOMUtils.next_id()}"
        assert bg_id != fg_id, "Foreground and background element id need to be different"

        # Preserve the original html
        original_innerHTML = self.target.innerHTML
        self.target.innerHTML = ""

        self.load_inner_html(
            f"""
            <div id="{bg_id}" class="popup-background">
                <div class="popup-foreground" onclick="event.stopPropagation()" style="width: 80%; height: 80%;">
                    <div id="{fg_id}"></div>
                </div>
            </div>
            """
        )

        bg = self.select(f"#{bg_id}")
        bg.on_click(lambda e: bg.hide())

        bg_layer = self.root.querySelector(f"#{bg_id}")
        fg_layer = self.root.querySelector(f"#{fg_id}")
        bg_layer.style.backgroundColor = bg_color
        fg_layer.style.backgroundColor = fg_color
        fg_layer.innerHTML = original_innerHTML

        div = Div()
        div.root = bg_layer
        div.target = fg_layer
        return div

    def overlay(self):
        self.root.classList.add("overlay")
        return self

    def load(self, svg=None, html=None, css=None):
        shadow_child = self.shadow()
        if svg is not None:
            shadow_child.load_svg(svg)
        if html is not None:
            shadow_child.load_html(html)
        if css is not None:
            shadow_child.load_css(css)
        shadow_child.load_css("svgui.css")
        return shadow_child

    def select(self, selectors=None):
        if selectors is None:
            return Svgui(self.root, [self.root])
        if isinstance(selectors, list):
            targets = self.root.querySelectorAll(",".join(selectors))
        else:
            targets = self.root.querySelectorAll(selectors)
        return Svgui(self.root, targets)
