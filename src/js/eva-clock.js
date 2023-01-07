customElements.define("eva-clock", class extends NeonSVG {
    init() {
        this.configs = this.getConfigs();
        this.svg = this.shadowRoot.querySelector("svg");

        this.registerEventListeners();
        this.registerKeyboardListeners();

        this.clock = this.createClock();
        this.#showClockMode();
        this.helpMode = 0;

        //Set default view
        if (this.configs["perspective"] == 1) {
            this.svg.classList.toggle("sideView");
        } else {
            this.svg.classList.toggle("frontView");
        }
        //Auto Play
        if (this.configs["play"] == 1) {
            this.clock.play();
        }
    }

    getConfigs() {
        //Load the configs from URL (first priority) or HTML attributes
        let params = new URL(window.location.href).searchParams;
        return {
            mode: params.get("mode") || this.getAttribute('mode'),
            play: params.get("play") || this.getAttribute('play'),
            perspective: params.get("perspective") || this.getAttribute('perspective'),
            maxDuration:
                params.get("total-min") * 60 * 1000 || this.getAttribute('total-min') * 60 * 1000 ||
                params.get("total-sec") * 1000 || this.getAttribute('total-sec') * 1000 ||
                params.get("total-ms") || this.getAttribute('total-ms'),
            dangerDuration:
                params.get("danger-min") * 60 * 1000 || this.getAttribute('danger-min') * 60 * 1000 ||
                params.get("danger-sec") * 1000 || this.getAttribute('danger-sec') * 1000 ||
                params.get("danger-ms") || this.getAttribute('danger-ms'),
        };
    }

    createClock() {
        let systemTimeClock = new SystemTimeClock({
            onRender: (ms, ts) => { this.#showSystemTime(ms, ts); },
        });

        let countDownClock = new StopWatchClock({
            onRender: (ms, ts) => { this.#showStopWatchTime(ms, ts); },
            onPlayerEvent: (event) => { this.#onPlayerEvent(event); },
            onStateChange: (s1, s2) => { this.#showStateChange(s1, s2); },
            mode: Clock.MODE.COUNTDOWN,
            maxDuration: this.configs["maxDuration"],
            dangerDuration: this.configs["dangerDuration"],
        });

        let countUpClock = new StopWatchClock({
            onRender: (ms, ts) => { this.#showStopWatchTime(ms, ts); },
            onPlayerEvent: (event) => { this.#onPlayerEvent(event); },
            onStateChange: (s1, s2) => { this.#showStateChange(s1, s2); },
            mode: Clock.MODE.COUNTUP,
            maxDuration: this.configs["maxDuration"],
            dangerDuration: this.configs["dangerDuration"],
        });

        //A multi-mode clock
        return new UnifiedClock(
            this.configs["mode"],
            systemTimeClock,
            countDownClock,
            countUpClock,
        );
    }

    registerKeyboardListeners() {
        document.addEventListener('keydown', event => {
            switch (event.code) {
                case 'Space':
                    event.preventDefault();
                    this.clock.playOrPause();
                    break;
                case 'KeyR':
                    this.clock.reset();
                    break;
                case 'KeyP':
                    this.#tooglePerspectiveView();
                    break;
                case 'KeyF':
                    this.#toggleFullscreen();
                    break;
                case 'KeyC':
                    this.#toggleNeonAmber();
                    break;
                case 'KeyM':
                    this.#toggleNextMode();
                    break;
                case 'KeyH':
                    this.#toggleHelp();
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    this.clock.adjustTimeRemain(1000);
                    break;
                case 'ArrowDown':
                    event.preventDefault();
                    this.clock.adjustTimeRemain(-1000);
                    break;
                case '+':
                    break;
                case '-':
                    break;
            };
        });
    }

    registerEventListeners() {
        this.registerOnClick(SEL.CLICKABLE_TOP, () => {
            this.#tooglePerspectiveView();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.CLICKABLE_LEFT, () => {
            this.#toggleHelp();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_POWER_EXTERNAL, () => {
            this.#toggleNextMode();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_POWER_SYSETM, () => {
            this.#toggleFullscreen();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_POWER_INTERNAL, () => {
            this.clock.reset();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_EMERGENCY, () => {
            this.#toggleNeonAmber();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.PANEL_CLOCK, () => {
            this.clock.playOrPause();
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_NORMAL, () => {
            this.clock.adjustTimeRemain(1000);
        }, STYLES.CLICKABLE);

        this.registerOnClick(SEL.BUTTON_RACING, () => {
            this.clock.adjustTimeRemain(-1000);
        }, STYLES.CLICKABLE);

        // this.registerOnClick(SEL.BUTTON_STOP, () => {
        //     this.#toggleNeonWireframe();
        //     let e = document.getElementById("helpPanel")
        //     e.style.display = (e.style.display == "inline") ? "none" : "inline";
        // }, STYLES.CLICKABLE);

        this.toogleClass([SEL.BUTTON_SLOW, SEL.BUTTON_STOP, SEL.BUTTON_NORMAL], "disableSelect");
    }

    crossFadeInOut(fadeInSelectors, fadeOutSelectors) {
        this.addClass(fadeInSelectors, STYLES.FADEIN_BLINK);
        this.addClass(fadeOutSelectors, STYLES.FADEOUT_BLINK);
        setTimeout(() => {
            this.removeClass(fadeInSelectors, STYLES.FADEIN_BLINK);
            this.removeClass(fadeOutSelectors, STYLES.FADEOUT_BLINK)
        }, 1100);
    }

    #pad(i) {
        return (i < 10) ? "0" + i : "" + i;
    }

    #showStopWatchTime(ms, ts) {
        this.setText(SEL.TEXT_MINUTES, ts.minutes);
        this.setText(SEL.TEXT_SECONDS, this.#pad(ts.seconds));
        this.setText(SEL.TEXT_SUBSECONDS, this.#pad(ts.subseconds));
    }

    #showSystemTime(ms, ts) {
        this.setText(SEL.TEXT_MINUTES_SYS, this.#pad(ts.hours));
        this.setText(SEL.TEXT_SECONDS_SYS, this.#pad(ts.minutes));
        this.setText(SEL.TEXT_SUBSECONDS_SYS, this.#pad(ts.seconds));
    }

    #showStateChange(fromState, toState) {
        if (toState == StopWatchClock.STATE.RACING) {
            this.#showRacing();
        }
        else if (toState == StopWatchClock.STATE.EMERGENCY) {
            this.#showEmergency();
        }
        else if (toState == StopWatchClock.STATE.ENDED) {
            this.#showEnded();
        }
        else if (toState == StopWatchClock.STATE.STANDBY) {
            this.#showStandby();
        }
    }

    #onPlayerEvent(event) {
        this.toogleClass(SEL.TEXTGROUP_CLOCK_STOPWATCH, STYLES.BREATH);
    }

    #showClockMode() {
        let isSysTimeMode = this.clock.mode == Clock.MODE.SYSTEMTIME;
        this.setVisibility(SEL.TEXTGROUP_CLOCK_STOPWATCH, !isSysTimeMode);
        this.setVisibility(SEL.TEXTGROUP_CLOCK_SYSTEMTIME, isSysTimeMode);
    }

    #showRacing() {
        this.setVisibility([
            SEL.BAR_RACING,
            SEL.STRIP_INTERNAL,
            SEL.BAR_RACING,
        ], true);

        this.setVisibility([
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BUTTON_EMERGENCY,
            SEL.BUTTON_POWER_EXTERNAL,
        ], false);

        this.crossFadeInOut([
            SEL.BUTTON_POWER_INTERNAL,
            SEL.BAR_RACING,
        ], [
            SEL.BUTTON_EMERGENCY,
            SEL.BUTTON_POWER_EXTERNAL,
        ]);
    }

    #showEmergency() {
        this.setColor([SEL.ALL_TEXT, SEL.ALL_DOT_GREEN, SEL.DOT_EMERGENCY], "red");
        this.setStrokeColor(SEL.ALL_BORDERS, "red");
        this.setVisibility([
            SEL.BUTTON_EMERGENCY,
        ], true);
        this.setVisibility([
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BAR_RACING,
        ], false);

        this.crossFadeInOut([
            SEL.BUTTON_EMERGENCY,
        ], [
            SEL.BAR_RACING,
        ]);
    }

    #showEnded() {
        this.toogleClass([SEL.STRIP_INTERNAL, SEL.BAR_RACING], STYLES.BLINK_3_1);
        this.toogleClass([SEL.BUTTON_EMERGENCY, SEL.TEXTGROUP_ACTIVE_TIME], STYLES.BLINK_8_2);
        this.setVisibility([
            SEL.BAR_RACING,
        ], true);
        this.setVisibility([
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.TEXT_SLOW,
            SEL.TEXT_NORMAL,
            SEL.TEXT_RACING,
            SEL.BORDER_SLOW,
            SEL.BORDER_NORMAL,
            SEL.BORDER_RACING,
        ], false);
    }

    #showStandby() {
        this.addClass(SEL.TEXTGROUP_CLOCK_STOPWATCH, STYLES.BREATH);
        this.resetColor([SEL.ALL_TEXT, SEL.ALL_DOT_GREEN, SEL.DOT_EMERGENCY, SEL.ALL_BORDERS]);
        this.removeClass([SEL.STRIP_INTERNAL, SEL.BAR_RACING], STYLES.BLINK_3_1);
        this.removeClass([SEL.BUTTON_EMERGENCY, SEL.TEXTGROUP_ACTIVE_TIME], STYLES.BLINK_8_2);
        this.resetVisibility([
            SEL.BUTTON_EMERGENCY,
            SEL.BUTTON_POWER_EXTERNAL,
            SEL.BUTTON_POWER_INTERNAL,
            SEL.BAR_STOP,
            SEL.BAR_SLOW,
            SEL.BAR_NORMAL,
            SEL.BAR_RACING,
            SEL.TEXT_STOP,
            SEL.TEXT_SLOW,
            SEL.TEXT_NORMAL,
            SEL.TEXT_RACING,
            SEL.BORDER_STOP,
            SEL.BORDER_SLOW,
            SEL.BORDER_NORMAL,
            SEL.BORDER_RACING,
            SEL.BUTTON_EMERGENCY,
            SEL.STRIP_EXTERNAL,
            SEL.STRIP_INTERNAL,
        ]);
    }

    #toggleNextMode() {
        this.clock.reset();
        this.clock.toggleNextMode();
        this.clock.reset();
        this.#showClockMode();
    }

    #tooglePerspectiveView() {
        this.svg.classList.toggle("sideView");
        this.svg.classList.toggle("frontView");
    }

    #toFrontView() {
        if (this.svg.classList.contains("sideView")) {
            this.#tooglePerspectiveView();
        }
    }

    #toggleFullscreen() {
        (document.fullscreenElement) ? this.exitFullscreen() : this.enterFullscreen();
    }

    #toggleNeonAmber() {
        this.toogleClass(SEL.ALL_TEXT, "neon-amber");
    }

    #toggleNeonWireframe() {
        this.toogleClass([
            SEL.ALL_LINES,
            SEL.ALL_RECTS,
            SEL.ALL_PATHS,
            SEL.ALL_TEXT
        ], "neon-wireframe");

        //Keep the clickable areas
        this.toogleClass(SEL.ALL_CLICKABLES, "neon-wireframe");

        //Set text to white
        this.toogleClass(SEL.ALL_CLOCK_TEXTS, "neon-wireframe");
        this.toogleClass(SEL.ALL_CLOCK_TEXTS, "neon-wireframe-text");
    }

    #toggleHelp() {
        this.helpMode = (this.helpMode + 1) % 2;
        switch (this.helpMode) {
            case 1:
                this.#toFrontView();
            case 0:
                this.toogleClass([
                    SEL.ALL_LINES,
                    SEL.ALL_RECTS,
                    SEL.ALL_PATHS,
                    SEL.ALL_TEXT
                ], "neon-wireframe");

                //Dim the text
                this.toogleClass(SEL.ALL_TEXT, "opacity70");

                //Keep the clickable areas filled
                this.toogleClass(SEL.ALL_CLICKABLES, "neon-wireframe");

                //Set Help text visible
                this.setVisibility(SEL.ALL_HELP_TEXTS, true);
                this.toogleClass(SEL.ALL_HELP_TEXTS, "neon-wireframe");
                this.toogleClass(SEL.ALL_HELP_TEXTS, "opacity70");
                break;
        }
    }
})


// function _httpParams() {
//     let url = new URL(window.location.href);
//     alert(" max=" + url.searchParams.get("max"));
//     alert(" danger=" + url.searchParams.get("danger"));
// let params = new URL(window.location.href).searchParams;
// let maxDuration = params.get("maxDuration");
// let dangerDuration = params.get("dangerDuration");
// }

var SEL = {
    PANEL_MAIN: "#pan-main",
    PANEL_CLOCK: "#pan-clock",
    PANEL_MODE: "#pan-mode",
    PANEL_POWER: "#pan-power",
    ALL_TEXT: "text, #colon1a, #colon1b, #colon2a, #colon2b, #colon1a-sys, #colon1b-sys",
    ALL_BORDERS: "path[id*=border], rect[id*=border]",
    ALL_DOT_GREEN: "#dot-green line",
    ALL_DOT_BLACK: "#dot-black line",
    ALL_DOT_AMBER: "#dot-amber line",
    ALL_RECTS: "rect",
    ALL_LINES: "line",
    ALL_PATHS: "path",
    ALL_CLICKABLES: "[id^=clickable-]",
    ALL_HELP_TEXTS: "[id^=help-]",
    BORDER_STOP: "#border-stop",
    BORDER_SLOW: "#border-slow",
    BORDER_NORMAL: "#border-normal",
    BORDER_RACING: "#border-racing",
    BUTTON_POWER_INTERNAL: "#pan-internal",
    BUTTON_POWER_EXTERNAL: "#pan-external",
    BUTTON_POWER_SYSETM: "#pan-system",
    BUTTON_STOP: "#pan-stop",
    BUTTON_SLOW: "#pan-slow",
    BUTTON_NORMAL: "#pan-normal",
    BUTTON_RACING: "#pan-racing",
    BUTTON_EMERGENCY: "#pan-emergency",
    DOT_EMERGENCY: "#dot-emergency1, #dot-emergency2",
    BAR_STOP: "#bar-stop",
    BAR_SLOW: "#bar-slow",
    BAR_NORMAL: "#bar-normal",
    BAR_RACING: "#bar-racing",
    TEXT_STOP: "#en-stop",
    TEXT_SLOW: "#en-slow",
    TEXT_NORMAL: "#en-normal",
    TEXT_RACING: "#en-racing",
    TEXTGROUP_ACTIVE_TIME: "#textgroup-active-time",
    STRIP_INTERNAL: "#strip-internal",
    STRIP_EXTERNAL: "#strip-external",
    CLICKABLE_BOTTOM: "#clickable-bottom",
    CLICKABLE_TOP: "#clickable-top",
    CLICKABLE_LEFT: "#clickable-left",
    //--------
    TEXTGROUP_CLOCK_STOPWATCH: "#textgroup-clock",
    TEXTGROUP_CLOCK_SYSTEMTIME: "#textgroup-clock-sys",
    TEXT_MINUTES_SYS: "#en-minute-sys",
    TEXT_SECONDS_SYS: "#en-second-sys",
    TEXT_SUBSECONDS_SYS: "#en-millis-sys",
    TEXT_MINUTES: "#en-minute",
    TEXT_SECONDS: "#en-second",
    TEXT_SUBSECONDS: "#en-millis",
    ALL_CLOCK_TEXTS: "#en-minute-sys, #en-second-sys, #en-millis-sys, #en-minute, #en-second, #en-millis, [id^=colon]"
};

var STYLES = {
    CLICKABLE: "clickable",
    BLINK_3_1: "blink_3_1",
    BLINK_8_2: "blink_8_2",
    BREATH: "breath",
    FADEIN_BLINK: "fadeIn_blink",
    FADEOUT_BLINK: "fadeOut_blink",
};
