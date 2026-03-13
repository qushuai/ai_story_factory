class PromptManager:

    @staticmethod
    def build_prompt():

        prompt = """
你是一名专业的恐怖小说作者。

请写一个 **原创中文恐怖故事**。

必须使用以下结构化标签。

角色标签：

[SPEAKER:narrator]
[SPEAKER:ghost]
[SPEAKER:child]

音效标签：

[SFX:door]
[SFX:footstep]
[SFX:heartbeat]
[SFX:whisper]

停顿标签：

[PAUSE:600]

规则：

1 故事必须使用中文
2 每一句话前必须有 SPEAKER 标签
3 每句话不超过20字
4 每句话单独一行
5 合理插入 SFX
6 使用 PAUSE 制造紧张节奏
7 故事长度约 2-3 分钟
8 故事必须是 **原创场景**

禁止出现以下常见套路：

- 老宅
- 深夜三点
- 停止的钟
- 走廊脚步声
- 门慢慢打开

请创造 **新的恐怖场景**，例如：

废弃医院、地铁站、旅馆、山路、地下停车场、旧录像带、电话亭等。

故事必须 **直接开始正文**，不要解释规则。
"""

        return prompt