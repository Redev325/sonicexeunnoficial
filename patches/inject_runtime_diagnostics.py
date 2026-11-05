#!/usr/bin/env python3
"""Inject a non-invasive browser error and freeze diagnostic panel into HTML5 output."""

from pathlib import Path
import sys


STYLE = r"""
<style id="sonicexe-runtime-diagnostics-style">
#sonicexe-runtime-diagnostics {
  position: fixed; left: 12px; bottom: 12px; z-index: 2147483647;
  width: min(380px, calc(100vw - 24px)); color: #f4f4f4;
  background: rgba(10, 10, 12, .94); border: 1px solid rgba(255, 139, 35, .75);
  border-radius: 8px; box-shadow: 0 5px 24px rgba(0,0,0,.55);
  font: 12px/1.4 Arial, sans-serif; text-align: left;
  pointer-events: auto; overflow: hidden;
}
#sonicexe-runtime-diagnostics * { box-sizing: border-box; }
#sonicexe-runtime-diagnostics .sx-head {
  display: flex; align-items: center; gap: 8px; min-height: 34px;
  padding: 6px 8px; background: rgba(255,139,35,.12);
}
#sonicexe-runtime-diagnostics .sx-title {
  color: #ffad60; font-weight: 700; letter-spacing: .7px; flex: 1;
}
#sonicexe-runtime-diagnostics .sx-status {
  color: #9ce4a5; font-weight: 700; white-space: nowrap;
}
#sonicexe-runtime-diagnostics.sx-error .sx-status { color: #ff7777; }
#sonicexe-runtime-diagnostics button {
  background: #25252a; color: #fff; border: 1px solid #555;
  border-radius: 4px; padding: 3px 7px; cursor: pointer; font: inherit;
}
#sonicexe-runtime-diagnostics button:hover { background: #393940; }
#sonicexe-runtime-diagnostics .sx-summary {
  padding: 6px 9px; color: #dedede; overflow-wrap: anywhere;
  border-top: 1px solid rgba(255,255,255,.08);
}
#sonicexe-runtime-diagnostics .sx-details { display: none; }
#sonicexe-runtime-diagnostics.sx-open .sx-details { display: block; }
#sonicexe-runtime-diagnostics .sx-meta {
  padding: 0 9px 7px; color: #bcbcc2; overflow-wrap: anywhere;
}
#sonicexe-runtime-diagnostics .sx-log {
  max-height: 190px; overflow: auto; padding: 5px 8px;
  border-top: 1px solid #38383d; background: rgba(0,0,0,.24);
}
#sonicexe-runtime-diagnostics .sx-entry {
  padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,.07);
  white-space: pre-wrap; overflow-wrap: anywhere;
}
#sonicexe-runtime-diagnostics .sx-entry:last-child { border-bottom: 0; }
#sonicexe-runtime-diagnostics .sx-entry[data-level="ERROR"] { color: #ff8585; }
#sonicexe-runtime-diagnostics .sx-entry[data-level="WARN"] { color: #ffd18b; }
#sonicexe-runtime-diagnostics .sx-actions {
  display: flex; gap: 6px; padding: 6px 8px; border-top: 1px solid #38383d;
}
#sonicexe-runtime-diagnostics .sx-hint { margin-left: auto; color: #999; align-self: center; }
</style>
"""

SCRIPT = r"""
<script id="sonicexe-runtime-diagnostics-script">
(function () {
  if (window.sonicEXEDiagnostics) return;

  var records = [];
  var panel = null;
  var expanded = false;
  var currentState = "Booting";
  var currentAction = "Waiting for game startup";
  var lastHeartbeat = Date.now();
  var lastGamePulse = Date.now();
  var gamePulseSeen = false;
  var pulseStallReported = false;
  var creatingState = null;
  var createToken = 0;
  var switchToken = 0;
  var pendingSwitch = null;
  var errorCount = 0;

  function now() {
    return new Date().toLocaleTimeString();
  }

  function stringify(value) {
    if (value === undefined || value === null) return String(value);
    if (value && value.stack) return String(value.stack);
    if (typeof value === "object") {
      try { return JSON.stringify(value); } catch (_) {}
    }
    return String(value);
  }

  function add(level, message, detail) {
    var text = String(message || "Unknown diagnostic event");
    var full = detail ? text + "\n" + stringify(detail) : text;
    records.unshift({ time: now(), level: level, message: full });
    if (records.length > 45) records.length = 45;
    if (level === "ERROR") {
      errorCount++;
      expanded = true;
      if (panel) panel.classList.add("sx-error", "sx-open");
    }
    render();
  }

  function render() {
    if (!panel) return;
    panel.classList.toggle("sx-open", expanded);
    panel.classList.toggle("sx-error", errorCount > 0);
    var status = panel.querySelector(".sx-status");
    var summary = panel.querySelector(".sx-summary");
    var meta = panel.querySelector(".sx-meta");
    var log = panel.querySelector(".sx-log");
    status.textContent = errorCount ? ("ERRORS: " + errorCount) : "LIVE";
    summary.textContent = currentAction;
    meta.textContent = "Current state: " + currentState + " | Last event: " +
      (records.length ? records[0].time : "none") +
      " | Browser: " + navigator.userAgent;
    while (log.firstChild) log.removeChild(log.firstChild);
    records.slice(0, 18).forEach(function (entry) {
      var line = document.createElement("div");
      line.className = "sx-entry";
      line.setAttribute("data-level", entry.level);
      line.textContent = "[" + entry.time + "] " + entry.level + ": " + entry.message;
      log.appendChild(line);
    });
  }

  function mount() {
    if (panel || !document.body) return;
    panel = document.createElement("section");
    panel.id = "sonicexe-runtime-diagnostics";
    panel.innerHTML =
      '<div class="sx-head">' +
        '<span class="sx-title">SONIC.EXE RUNTIME DIAGNOSTICS</span>' +
        '<span class="sx-status">LIVE</span>' +
        '<button type="button" class="sx-toggle">Details</button>' +
      '</div>' +
      '<div class="sx-summary">Monitoring startup and game loading</div>' +
      '<div class="sx-details">' +
        '<div class="sx-meta"></div>' +
        '<div class="sx-log" aria-live="polite"></div>' +
        '<div class="sx-actions">' +
          '<button type="button" class="sx-copy">Copy report</button>' +
          '<button type="button" class="sx-clear">Clear log</button>' +
          '<span class="sx-hint">F8 toggles details</span>' +
        '</div>' +
      '</div>';
    document.body.appendChild(panel);
    panel.querySelector(".sx-toggle").addEventListener("click", function () {
      expanded = !expanded;
      render();
      this.textContent = expanded ? "Hide" : "Details";
    });
    panel.querySelector(".sx-copy").addEventListener("click", function () {
      var report = [
        "SONIC.EXE HTML5 RUNTIME REPORT",
        "Time: " + new Date().toISOString(),
        "State: " + currentState,
        "Action: " + currentAction,
        "User agent: " + navigator.userAgent,
        "",
        records.slice().reverse().map(function (r) {
          return "[" + r.time + "] " + r.level + ": " + r.message;
        }).join("\n")
      ].join("\n");
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(report).then(function () {
          add("INFO", "Diagnostic report copied to clipboard");
        }).catch(function () {
          add("WARN", "Clipboard access was blocked; expand Details and inspect the log");
        });
      } else {
        add("WARN", "Clipboard API is unavailable in this browser");
      }
    });
    panel.querySelector(".sx-clear").addEventListener("click", function () {
      records = [];
      errorCount = 0;
      add("INFO", "Log cleared; monitoring continues");
    });
    render();
  }

  function mark(message) {
    var text = String(message || "");
    lastHeartbeat = Date.now();
    currentAction = text;
    add(/^ERROR:/.test(text) ? "ERROR" : "INFO", text);

    var match = text.match(/^STATE CREATE START:\s*(.*)$/);
    if (match) {
      currentState = "Creating " + match[1];
      creatingState = match[1];
      var token = ++createToken;
      setTimeout(function () {
        if (token === createToken && creatingState === match[1]) {
          add("ERROR", "STATE INITIALIZATION STALLED: " + match[1] +
            " did not reach its create-complete checkpoint within 15 seconds.");
        }
      }, 15000);
      switchToken++;
      pendingSwitch = null;
      return;
    }

    match = text.match(/^STATE CREATE COMPLETE:\s*(.*)$/);
    if (match) {
      currentState = match[1];
      creatingState = null;
      createToken++;
      switchToken++;
      pendingSwitch = null;
      return;
    }

    match = text.match(/^STATE SWITCH REQUESTED:\s*(.*)$/);
    if (match) {
      pendingSwitch = match[1];
      var switchId = ++switchToken;
      setTimeout(function () {
        if (switchId === switchToken && pendingSwitch === match[1] && !creatingState) {
          add("ERROR", "STATE TRANSITION STALLED: requested " + match[1] +
            " but no destination state began creating within 12 seconds.");
        }
      }, 12000);
      return;
    }

    if (/^LOADING STATE REQUESTED:/.test(text)) {
      var loadingMessage = text;
      setTimeout(function () {
        if (currentAction === loadingMessage) {
          add("WARN", "LOADING CHECKPOINT STALLED: the loading request has not produced another state checkpoint after 12 seconds.");
        }
      }, 12000);
    }
  }

  window.sonicEXEDiagnostics = {
    mark: mark,
    pulse: function () {
      lastGamePulse = Date.now();
      gamePulseSeen = true;
      pulseStallReported = false;
    },
    report: function (level, message, detail) {
      add(level || "INFO", message, detail);
    },
    getRecords: function () { return records.slice(); }
  };

  window.addEventListener("error", function (event) {
    if (event.target && event.target !== window) {
      var target = event.target;
      var url = target.currentSrc || target.src || target.href || "(unknown resource)";
      add("ERROR", "RESOURCE LOAD FAILED: " + (target.tagName || "resource") + " " + url);
      return;
    }
    var location = (event.filename || "unknown file") + ":" +
      (event.lineno || 0) + ":" + (event.colno || 0);
    add("ERROR", "JAVASCRIPT ERROR at " + location + ": " +
      (event.message || "Unknown exception"), event.error);
  }, true);

  window.addEventListener("unhandledrejection", function (event) {
    add("ERROR", "UNHANDLED PROMISE REJECTION", event.reason);
  });

  window.addEventListener("unhandledrejection", function (event) {
    if (event.reason) currentAction = "Promise rejected: " + stringify(event.reason);
  });

  if (window.console && console.error) {
    var originalConsoleError = console.error.bind(console);
    console.error = function () {
      var message = Array.prototype.map.call(arguments, stringify).join(" ");
      add("ERROR", "console.error: " + message);
      originalConsoleError.apply(console, arguments);
    };
  }

  if (window.fetch) {
    var originalFetch = window.fetch.bind(window);
    window.fetch = function () {
      var requestUrl = arguments[0] && arguments[0].url ? arguments[0].url : arguments[0];
      return originalFetch.apply(null, arguments).then(function (response) {
        if (!response.ok) {
          add("ERROR", "HTTP REQUEST FAILED: " + response.status + " " + requestUrl);
        }
        return response;
      }).catch(function (error) {
        add("ERROR", "FETCH FAILED: " + requestUrl, error);
        throw error;
      });
    };
  }

  if (window.XMLHttpRequest) {
    var originalOpen = XMLHttpRequest.prototype.open;
    var originalSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function (method, url) {
      this.__sonicExeMethod = method;
      this.__sonicExeUrl = url;
      return originalOpen.apply(this, arguments);
    };
    XMLHttpRequest.prototype.send = function () {
      var xhr = this;
      if (!xhr.__sonicExeDiagnosticBound) {
        xhr.__sonicExeDiagnosticBound = true;
        xhr.addEventListener("loadend", function () {
          if (xhr.status === 0 || xhr.status >= 400) {
            add("ERROR", "XHR FAILED: " + (xhr.__sonicExeMethod || "GET") +
              " " + (xhr.status || "NETWORK ERROR") + " " + (xhr.__sonicExeUrl || "(unknown URL)"));
          }
        });
        xhr.addEventListener("error", function () {
          add("ERROR", "XHR NETWORK ERROR: " + (xhr.__sonicExeUrl || "(unknown URL)"));
        });
      }
      return originalSend.apply(this, arguments);
    };
  }

  var heartbeatTimer = setInterval(function () {
    var current = Date.now();
    var gap = current - lastHeartbeat;
    if (gap > 5000) {
      add("WARN", "MAIN THREAD STALL DETECTED: browser JavaScript was unresponsive for " +
        (gap / 1000).toFixed(1) + " seconds.");
    }
    if (gamePulseSeen && document.visibilityState === "visible") {
      var pulseGap = current - lastGamePulse;
      if (pulseGap > 6000 && !pulseStallReported) {
        pulseStallReported = true;
        add("ERROR", "GAME UPDATE LOOP STOPPED: no Psych Engine update checkpoint for " +
          (pulseGap / 1000).toFixed(1) + " seconds while this tab was visible. Last state: " + currentState);
      }
    }
    lastHeartbeat = current;
  }, 1000);

  window.addEventListener("keydown", function (event) {
    if (event.key === "F8") {
      expanded = !expanded;
      render();
      if (panel) panel.querySelector(".sx-toggle").textContent = expanded ? "Hide" : "Details";
      event.preventDefault();
    }
  }, true);

  window.addEventListener("pageshow", function () {
    mark("BROWSER PAGE: visible and running");
  });
  window.addEventListener("beforeunload", function () {
    clearInterval(heartbeatTimer);
  });

  document.addEventListener("DOMContentLoaded", mount);
  if (document.readyState === "interactive" || document.readyState === "complete") mount();
  add("INFO", "Diagnostics initialized; waiting for game startup checkpoints");
})();
</script>
"""


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: inject_runtime_diagnostics.py path/to/index.html")
    page = Path(sys.argv[1])
    if not page.is_file():
        raise SystemExit(f"HTML5 entry page not found: {page}")
    html = page.read_text(encoding="utf-8")
    if "sonicexe-runtime-diagnostics-script" in html:
        raise SystemExit("Runtime diagnostics overlay is already installed.")
    head_end = html.lower().rfind("</head>")
    if head_end < 0:
        raise SystemExit("Generated HTML5 page has no closing head tag.")
    html = html[:head_end] + STYLE + "\n" + SCRIPT + "\n" + html[head_end:]
    page.write_text(html, encoding="utf-8")
    print("Injected the Sonic.EXE runtime diagnostics panel and browser error watchers.")


if __name__ == "__main__":
    main()
