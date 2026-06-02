"""Verify the Viseron application boots and serves traffic."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from . import _helpers as helpers

if TYPE_CHECKING:
    import testinfra

# Lines that we treat as fatal in the boot logs.
FATAL_LOG_PATTERNS = (
    re.compile(r"^Traceback \(most recent call last\):", re.MULTILINE),
    re.compile(r"\b(viseron(\.[\w\.]+)?)\b\s+ERROR\b", re.IGNORECASE | re.MULTILINE),
)


def test_viseron_process_running(host: testinfra.host.Host) -> None:
    """The viseron python process must be running."""
    cmd = host.run("pgrep -f 'python3 .*-m viseron'")
    assert cmd.rc == 0, (
        f"no viseron process found: rc={cmd.rc}\n"
        f"stdout=\n{cmd.stdout}\nstderr=\n{cmd.stderr}"
    )


def test_webserver_responds(host: testinfra.host.Host, webserver_url: str) -> None:
    """The nginx-fronted webserver should answer HTTP requests."""
    status = helpers.wait_for_http_in_container(host, webserver_url, timeout=30.0)
    assert status in (200, 301, 302, 401, 403), (
        f"unexpected status {status} from {webserver_url}"
    )


def test_boot_logs_have_no_tracebacks(boot_logs: str) -> None:
    """Boot logs must not contain a Python traceback."""
    matches = [match.group(0) for match in FATAL_LOG_PATTERNS[0].finditer(boot_logs)]
    assert not matches, (
        f"found {len(matches)} traceback(s) in boot logs. First 2KB of logs:\n"
        f"{boot_logs[:2048]}"
    )
