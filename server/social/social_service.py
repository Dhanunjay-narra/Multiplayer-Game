"""Social friends list, clans, presence, and chat channel distribution."""
import uuid
import time
from typing import Dict, List, Optional
from shared.schemas.social_schemas import FriendRecord, ClanData, ClanMemberRecord, ChatMessageData
from shared.enums.game_enums import FactionType


class SocialService:
    """Manages friends, online presence, chat rooms, and persistent clans."""

    def __init__(self) -> None:
        self.friends: Dict[str, List[FriendRecord]] = {}
        self.clans: Dict[str, ClanData] = {}
        self.user_to_clan: Dict[str, str] = {}
        self.chat_history: List[ChatMessageData] = []

    def add_friend(self, user_id: str, friend_id: str, friend_name: str) -> None:
        """Adds a friend to user's list."""
        if user_id not in self.friends:
            self.friends[user_id] = []
        if not any(f.friend_id == friend_id for f in self.friends[user_id]):
            self.friends[user_id].append(FriendRecord(friend_id=friend_id, username=friend_name, is_online=True))

    def get_friends(self, user_id: str) -> List[FriendRecord]:
        return self.friends.get(user_id, [])

    def create_clan(self, user_id: str, username: str, name: str, tag: str, faction: FactionType) -> ClanData:
        """Creates a new clan with the creator as Leader."""
        if user_id in self.user_to_clan:
            raise ValueError("Already in a clan")

        clan_id = f"cln_{uuid.uuid4().hex[:8]}"
        leader_record = ClanMemberRecord(user_id=user_id, username=username, role="LEADER", joined_at=time.time())
        clan = ClanData(
            clan_id=clan_id,
            name=name,
            tag=tag,
            faction_alignment=faction,
            level=1,
            members=[leader_record],
        )
        self.clans[clan_id] = clan
        self.user_to_clan[user_id] = clan_id
        return clan

    def send_chat_message(self, sender_id: str, sender_name: str, channel: str, content: str) -> ChatMessageData:
        """Broadcasts a chat message to the designated channel."""
        msg = ChatMessageData(
            message_id=f"msg_{uuid.uuid4().hex[:10]}",
            sender_id=sender_id,
            sender_name=sender_name,
            channel=channel,
            content=content,
            timestamp=time.time(),
        )
        self.chat_history.append(msg)
        if len(self.chat_history) > 1000:
            self.chat_history = self.chat_history[-500:]
        return msg


social_service = SocialService()
