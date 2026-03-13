class PromptManager:

    @staticmethod
    def build_prompt():

        prompt = """
你是一名专业的恐怖小说作者。

请写一个 **中文恐怖故事**。

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

1 故事必须使用 **中文**
2 每一句话前必须有 SPEAKER 标签
3 每句话不超过20字
4 每句话单独一行
5 故事要有恐怖氛围
6 合理插入音效
7 使用停顿制造紧张感
8 故事长度约 2-3 分钟

格式示例：

[SPEAKER:narrator]
深夜三点。

[SFX:footstep]

[SPEAKER:narrator]
走廊里传来脚步声。

[PAUSE:800]

[SPEAKER:ghost]
你终于来了。

[SFX:heartbeat]

[SPEAKER:narrator]
我不敢回头。

现在开始写故事。
"""

        return prompt