class PromptManager:

    @staticmethod
    def build_prompt():

        prompt = """
你是一名专业的恐怖小说作者。

请写一个 **原创中文恐怖故事**。
必须包含两个部分：
[TITLE]
生成一个吸引人的短视频标题
不超过20字
具有悬疑感
标题前需要用[场景英文]标注 必须与提供的场景英文一致 如 剧场 就只写  [theater]
[STORY]
写一个中文恐怖故事。
必须使用以下结构化标签。

角色标签：

[SPEAKER:male]
[SPEAKER:female]
旁白使用[SPEAKER:female]
音效标签：

[SFX:door]
[SFX:footstep]
[SFX:heartbeat]
[SFX:whisper]

停顿标签：

[PAUSE:600]

规则：

1 故事必须使用中文
2 每一句话前必须有 SPEAKER 标签，且标签后必须换行跟内容
3 每句话不超过20字
4 每句话单独一行
5 合理插入 SFX
6 使用 PAUSE 制造紧张节奏
7 故事长度约 1-2分钟
8 故事必须是 **原创场景**
9 故事必须包含 1-2行对白
10 不要有标点符号
禁止出现以下常见套路：

- 老宅
- 深夜三点
- 停止的钟
- 走廊脚步声
- 门慢慢打开

请创造 **新的恐怖场景**，【随机场景池（必须随机选择一个）】

剧场theater
房子house
楼房building
病房hospital_room
图书馆library
墓地cemetery
操场playground
楼梯staircase
镜子mirror
午夜电梯midnight_elevator
先 来个house 场景的

故事必须 **直接开始正文**，不要解释规则。
"""

        return prompt