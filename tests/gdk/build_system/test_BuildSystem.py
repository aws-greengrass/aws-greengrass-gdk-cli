import pytest
from unittest import TestCase

from gdk.build_system.BuildSystem import BuildSystem


class BuildSystemTests(TestCase):

    def test_build_system_create_singleton(self):
        build_system_one = BuildSystem()
        build_system_two = BuildSystem()

        assert build_system_one == build_system_two

    def test_build_system_register(self):

        class FakeSystem:
            def __init__(self):
                pass

            def __str__(self):
                return "fake_sys"

            def build(self):
                return True

        build_system = BuildSystem()
        build_system.register(FakeSystem())

        assert build_system.build("fake_sys") is True

    def test_build_system_unregistered_module(self):

        with pytest.raises(TypeError):
            build_system = BuildSystem()
            build_system.build("fake")
