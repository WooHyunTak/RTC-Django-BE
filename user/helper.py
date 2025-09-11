from message.models import Message, MessageType


async def save_message_by_channel(data):
    """
    채널에 메시지 저장
    :param data: 메시지 데이터
    :return: 전송 데이터
    """

    # 전송할 채널 정보
    channel_id = data.get("channel_id")  # 채널 아이디
    group_name = data.get("group_name")  # 장고 레디스 그룹 이름

    # 보낸사람 정보
    from_user = data.get("from_user")

    # 메시지 내용
    message_content = data.get("message")
    message_type = data.get("type") | MessageType.NORMAL

    # 메시지 DB저장
    Message.objects.create(
        content=message_content,
        type=message_type,
        from_user=from_user,
        channel=channel_id,
    )

    return group_name, message_content
