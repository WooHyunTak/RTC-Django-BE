import logging

from bs4 import BeautifulSoup
from channels.db import database_sync_to_async
from django.db import transaction

from message.models import Message, MessageType
from user_channel.models import UserChannel

logger = logging.getLogger(__name__)


async def save_message_by_channel(data):
    """
    채널에 메시지 저장
    :param data: 메시지 데이터
    :return: 전송 데이터
    """

    # 전송할 채널 정보
    channel_id = data.get("channel_id")  # 채널 아이디

    # 보낸사람 정보
    from_user_id = data.get("from_user_id")

    # 메시지 내용
    message_content = data.get("message")
    message_type = data.get("type") or MessageType.NORMAL

    # 메시지 DB저장
    await database_sync_to_async(Message.objects.create)(
        content=message_content,
        type=message_type,
        from_user_id=from_user_id,
        channel=channel_id,
    )

    return message_content


async def save_message_to_user(data):
    """
    사용자에게 메시지 전송
    :param data: 메시지 데이터
    """
    try:
        to_user_id = data.get("toUserId")  # 받는 사람 프론트에서 온 data
        from_user_id = data.get("from_user_id")  # 보낸 사람 서버 토큰 data
        message = data.get("content")

        # html형식을 clean_content로 변환
        clean_content = clean_html_content(message)

        # 모든 ORM + 트랜잭션을 하나의 동기 함수로 묶어서 실행
        return await database_sync_to_async(_save_message_to_user_txn)(
            from_user_id, to_user_id, message, clean_content
        )

    except Exception as e:
        logger.error(f"Error saving message to user: {e}")
        raise e


def _save_message_to_user_txn(from_user_id, to_user_id, message, clean_content):
    # 동기 트랜잭션 컨텍스트
    with transaction.atomic():
        # 개인간의 DM 채널 확인 (있으면 get, 없으면 create)
        channel, created = UserChannel.objects.get_or_create(
            name=f"{from_user_id}#{to_user_id}",
            is_direct=True,
            defaults={
                "name": f"{from_user_id}#{to_user_id}",
                "description": "",
                "is_direct": True,
                "created_by_id": from_user_id,
            },
        )
        if created:
            channel.members.add(from_user_id)

        # 메시지 DB저장
        Message.objects.create(
            content=message,
            clean_content=clean_content,
            type=MessageType.NORMAL,
            from_user_id=from_user_id,
            channel=channel,
        )

    return message


def clean_html_content(html):
    """
    html 형식의 태그를 모두 제거하고 텍스트만 반환
    :param html: html 형식
    :return: clean_content
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
