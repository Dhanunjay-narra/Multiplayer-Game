from server.gateway.anti_cheat import AntiCheatTracker

def test_anti_cheat_packet_rate_limiting():
    tracker = AntiCheatTracker(max_packets_per_sec=50)
    for _ in range(50):
        assert tracker.validate_packet_rate("player-101") is True
    # 51st packet exceeds threshold
    assert tracker.validate_packet_rate("player-101") is False
