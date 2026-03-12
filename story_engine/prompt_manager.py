class PromptManager:

    @staticmethod
    def build_prompt():
        prompt = """
你是一个专业的恐怖故事作家，请生成一个悬疑恐怖故事。要求如下：

1. 故事对白用中文撰写。
2. 使用固定角色：旁白(narrator)、孩子(child)、幽灵(ghost)。
3. 使用音效(SFX)和背景音乐(BGM)来增强氛围。
4. 使用停顿(PAUSE:毫秒)表示故事中需要停顿的时间。
5. SFX/BGM 标签必须保留原始标识，如 door、footstep、heartbeat、whisper、dark_ambience。
6. 输出格式示例：

[SPEAKER:narrator] 老宅的挂钟停在午夜。
[SFX:door] 门自己开了。
[PAUSE:600]
[SPEAKER:child] 妈妈，地下室有人。
[SFX:footstep]
[SPEAKER:narrator] 可她的孩子三年前就死了。
[PAUSE:600]
[SPEAKER:ghost] 妈妈，我好冷……
[BGM:dark_ambience]
[SFX:heartbeat] 心跳声急促而疼痛。

请生成大约 30-50 段故事，合理交替对白、音效和停顿。
"""
        return prompt