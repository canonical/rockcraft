from abc import ABC, abstractmethod

import pytest

from rockcraft.providers import Provider


class BaseProviderTest(ABC):
    """Base class for tests that apply to multiple providers"""

    @abstractmethod
    def create_provider(self) -> Provider:
        """Create a new instance of the specific Provider subclass to test"""

    def test_get_command_environment_all_opts(self, monkeypatch):
        monkeypatch.setenv("IGNORE_ME", "or-im-failing")
        monkeypatch.setenv("PATH", "not-using-host-path")
        monkeypatch.setenv("http_proxy", "test-http-proxy")
        monkeypatch.setenv("https_proxy", "test-https-proxy")
        monkeypatch.setenv("no_proxy", "test-no-proxy")

        provider = self.create_provider()
        env = provider.get_command_environment()

        assert env == {
            "ROCKCRAFT_MANAGED_MODE": "1",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin",
            "http_proxy": "test-http-proxy",
            "https_proxy": "test-https-proxy",
            "no_proxy": "test-no-proxy",
        }

    @pytest.mark.parametrize(
        "name,expected_valid,expected_reason",
        [
            ("ubuntu:18.04", True, None),
            ("ubuntu:20.04", True, None),
            (
                "ubuntu:19.04",
                False,
                "Base 'ubuntu:19.04' is not supported (must be 'ubuntu:18.04' or 'ubuntu:20.04')",
            ),
        ],
    )
    def test_is_base_available(
        self,
        name,
        expected_valid,
        expected_reason,
    ):
        provider = self.create_provider()

        valid, reason = provider.is_base_available(name)

        assert (valid, reason) == (expected_valid, expected_reason)
