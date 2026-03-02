import time
import unittest
from unittest.mock import patch

from graph_lib.providers.base import DataPoint
from graph_lib.providers.command_provider import CommandProvider
from graph_lib.widgets.graph_widget import GraphWidget


class CommandProviderRealtimeTests(unittest.TestCase):
    def test_realtime_callback_receives_full_history(self):
        provider = CommandProvider(
            command="printf '7\\n'",
            poll_interval_ms=50,
            history_seconds=10,
        )
        lengths = []

        def on_data(data):
            lengths.append(len(data))

        provider.subscribe(on_data)
        provider.start()
        try:
            time.sleep(0.25)
        finally:
            provider.stop()
            provider.unsubscribe()

        self.assertGreaterEqual(len(lengths), 2)
        self.assertGreater(max(lengths), 1)
        self.assertTrue(all(length >= 1 for length in lengths))


class GraphWidgetSchedulingTests(unittest.TestCase):
    def test_should_use_poll_timer_respects_push_capability(self):
        push_provider = type("PushProvider", (), {"supports_push_updates": True})()
        poll_provider = type("PollProvider", (), {"supports_push_updates": False})()
        fake_widget = type(
            "FakeWidget",
            (),
            {"_provider_supports_push": GraphWidget._provider_supports_push},
        )()

        fake_widget.refresh_interval_ms = 1000
        fake_widget.provider = push_provider
        self.assertFalse(GraphWidget._should_use_poll_timer(fake_widget))

        fake_widget.provider = poll_provider
        self.assertTrue(GraphWidget._should_use_poll_timer(fake_widget))

        fake_widget.refresh_interval_ms = 0
        self.assertFalse(GraphWidget._should_use_poll_timer(fake_widget))

    def test_on_data_update_queues_main_thread_apply(self):
        class FakeRenderer:
            def __init__(self):
                self.calls = 0
                self.data = []

            def set_data(self, data):
                self.calls += 1
                self.data = data

        class FakeWidget:
            _apply_data_update = GraphWidget._apply_data_update

            def __init__(self):
                self.renderer = FakeRenderer()
                self._on_data_hook = None
                self.draw_called = False

            def queue_draw(self):
                self.draw_called = True

        fake = FakeWidget()
        scheduled = []

        def capture_idle_add(callback, *args):
            scheduled.append((callback, args))
            return 1

        data = [
            DataPoint(timestamp=1.0, value=10.0),
            DataPoint(timestamp=2.0, value=12.5),
        ]

        with patch("graph_lib.widgets.graph_widget.GLib.idle_add", side_effect=capture_idle_add):
            GraphWidget._on_data_update(fake, data)

        self.assertEqual(fake.renderer.calls, 0)
        self.assertEqual(len(scheduled), 1)

        callback, args = scheduled[0]
        self.assertEqual(callback, fake._apply_data_update)
        callback(*args)

        self.assertEqual(fake.renderer.calls, 1)
        self.assertEqual(len(fake.renderer.data), 2)
        self.assertTrue(fake.draw_called)


if __name__ == "__main__":
    unittest.main()
