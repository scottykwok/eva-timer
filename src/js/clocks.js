//An Abstract class
class Clock {
    static MODE = {
        COUNTDOWN: 'COUNTDOWN',
        COUNTUP: 'COUNTUP',
        SYSTEMTIME: 'SYSTEMTIME',
    };

    play() { };
    pause() { };
    playOrPause() { };
    reset() { };
    adjustTimeRemain(ms) { };
}

//An CountDown or CountUp clock
class StopWatchClock extends Clock {
    static STATE = {
        STANDBY: 'STANDBY',
        RACING: 'RACING',
        EMERGENCY: 'EMERGENCY',
        ENDED: 'ENDED',
    };
    static EVENT = {
        PLAY: 'PLAY',
        PAUSE: 'PAUSE',
    };

    static MAX_DURATION = 9 * 60 * 1000; // 9:00:00

    constructor(
        { onRender = null,
            onStateChange: onStateChange = null,
            onPlayerEvent: onPlayerEvent = null,
            maxDuration = 60 * 1000,
            dangerDuration = 10 * 1000,
            mode = Clock.MODE.COUNTDOWN,
            renderInterval = 35,
            loop = false }
    ) {
        super();
        this.maxDuration = isNaN(maxDuration) ? 60 * 1000 : maxDuration;
        this.dangerDuration = isNaN(dangerDuration) ? 10 * 1000 : dangerDuration;
        //Sanity Check
        this.maxDuration = Math.min(this.maxDuration, StopWatchClock.MAX_DURATION);
        this.dangerDuration = Math.min(this.maxDuration, this.dangerDuration);
        this.loop = loop;
        this.renderInterval = renderInterval;
        this.state = null;
        this.onRender = (typeof onRender === 'function') ? onRender : (ms, dict) => { console.log(ms, dict); }
        this.onStateChange = (typeof onStateChange === 'function') ? onStateChange : (s1, s2) => { console.log("state: " + s1 + "->" + s2); }
        this.onPlayerEvent = (typeof onPlayerEvent === 'function') ? onPlayerEvent : (e) => { console.log("event:" + e); }
        this.reset();
        this.setMode(mode);
    }

    asCountDownClock() {
        return this.setMode(Clock.MODE.COUNTDOWN);
    }

    asCountUpClock() {
        return this.setMode(Clock.MODE.COUNTDOWN);
    }

    #updateText() {
        let ms = (this.mode == Clock.MODE.COUNTDOWN) ? this.timeRemain : this.maxDuration - this.timeRemain;
        let subseconds = Math.floor((ms / 10) % 100),
            seconds = Math.floor((ms / 1000) % 60),
            minutes = Math.floor((ms / (1000 * 60)) % 60),
            hours = Math.floor((ms / (1000 * 60 * 60)) % 24);
        this.onRender(ms, { hours: hours, minutes: minutes, seconds: seconds, subseconds: subseconds });
    }

    #updateState(toState) {
        if (toState != this.state) {
            let fromState = this.state;
            this.state = toState;
            this.onStateChange(fromState, toState);
        }
    }

    #updateEvent(event) {
        this.onPlayerEvent(event);
    }

    #tick() {
        let now = Date.now();
        this.timeRemain -= now - this.lastRenderedTime;
        this.lastRenderedTime = now;
        if (this.timeRemain <= 0) {
            clearInterval(this.timer);
            this.isRunning = false;
            this.timeRemain = 0;
            this.#updateState(StopWatchClock.STATE.ENDED);
        }
        else if (this.timeRemain <= this.dangerDuration)
            this.#updateState(StopWatchClock.STATE.EMERGENCY);
        this.#updateText();
    }

    setMode(mode) {
        this.mode = mode;
        if (!this.isRunning)
            this.#updateText();
        return this;
    }

    play() {
        if (!this.isRunning && this.timeRemain > 0) {
            this.lastRenderedTime = Date.now();
            this.isRunning = true;
            if (this.state == StopWatchClock.STATE.STANDBY)
                this.#updateState(StopWatchClock.STATE.RACING);
            this.#updateText();
            this.timer = setInterval(() => { this.#tick(); }, this.renderInterval);
            this.#updateEvent(StopWatchClock.EVENT.PLAY);
            return true;
        }
        return false;
    }

    pause() {
        if (this.isRunning) {
            clearInterval(this.timer);
            this.isRunning = false;
            this.#tick();
            this.#updateEvent(StopWatchClock.EVENT.PAUSE);
            return true;
        } else {
            this.#updateText();
            return false;
        }
    }

    playOrPause() {
        return this.play() || this.pause();
    }

    reset() {
        this.pause();
        this.timeRemain = this.maxDuration;
        this.#updateState(StopWatchClock.STATE.STANDBY);
        this.#updateText();
    }

    adjustTimeRemain(ms) {
        if (this.state != StopWatchClock.STATE.ENDED) {
            if (this.state == StopWatchClock.STATE.STANDBY) {
                this.maxDuration = Math.max(0, this.maxDuration + ms);
                this.timeRemain = Math.max(0, this.timeRemain + ms);
            }
            else {
                this.timeRemain = Math.max(0, this.timeRemain + ms);
            }
            this.#updateText();
        }
    }
}

// System Time Clock
class SystemTimeClock extends Clock {
    constructor({
        onRender = null,
        renderInterval = 500,
    }) {
        super();
        this.mode = Clock.MODE.SYSTEMTIME;
        this.renderInterval = renderInterval;
        this.onRender = (typeof onRender === 'function') ? onRender : (ms, dict) => { console.log(ms, dict); }
        this.timer = setInterval(() => { this.#updateTimeRemain(); }, this.renderInterval);
    }

    #updateTimeRemain() {
        let now = new Date();
        let ms = now.getMilliseconds(),
            subseconds = ms / 10,
            seconds = now.getSeconds(),
            minutes = now.getMinutes(),
            hours = now.getHours();
        this.onRender(ms, { hours: hours, minutes: minutes, seconds: seconds, subseconds: subseconds });
    }
}

// A compose clock that encasuplate multiple implementions
class UnifiedClock extends Clock {
    constructor(defaultMode = Clock.MODE.COUNTDOWN, systemTimeClock, countDownClock, countUpClock) {
        super();
        this.systemTimeClock = systemTimeClock;
        this.countDownClock = countDownClock;
        this.countUpClock = countUpClock;
        this.setMode(defaultMode);
        this.reset();
    }

    toggleNextMode() {
        //change to "NEXT" mode
        switch (this.mode) {
            case Clock.MODE.COUNTUP:
                return this.setMode(Clock.MODE.SYSTEMTIME);
            case Clock.MODE.SYSTEMTIME:
                return this.setMode(Clock.MODE.COUNTDOWN);
            case Clock.MODE.COUNTDOWN:
            default:
                return this.setMode(Clock.MODE.COUNTUP);
        }
    }

    setMode(mode) {
        this.mode = mode;
        switch (mode) {
            case Clock.MODE.COUNTUP:
                this.clock = this.countUpClock;
                return this;
            case Clock.MODE.SYSTEMTIME:
                this.clock = this.systemTimeClock;
                return this;
            case Clock.MODE.COUNTDOWN:
            default:
                this.clock = this.countDownClock;
                return this;
        }
    }

    play() {
        return this.clock.play();
    }

    pause() {
        return this.clock.pause();
    }

    playOrPause() {
        return this.clock.playOrPause();
    }

    reset() {
        this.clock.reset();
    }

    adjustTimeRemain(ms) {
        this.clock.adjustTimeRemain(ms);
    };
}