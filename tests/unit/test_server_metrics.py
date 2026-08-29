from server.world.metrics import GameServerTelemetry

def test_server_telemetry_tick_aggregation():
    telemetry = GameServerTelemetry()
    for t in [16.6, 16.7, 16.5, 16.6]:
        telemetry.record_tick(t)
    assert telemetry.average_tick_ms == 16.6
