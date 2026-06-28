"""随机宿舍事件生成器"""

import random

# ──────────────────────────────────────────────
# 事件分类
# ──────────────────────────────────────────────
EVENTS = {
    "饮食": [
        "外卖到了！炸鸡+奶茶，香味飘满整个宿舍。谁去楼下拿？",
        "老王从家里带来了一箱特产，正在分给大家。",
        "有人提议深夜点烧烤，但已经11点了。",
        "宿舍最后一包泡面被吃了，案发现场只有一个空碗。",
        "隔壁宿舍送来了一盒切好的西瓜。",
        "不知道谁在宿舍吃螺蛳粉，味道已经飘到走廊了。",
    ],
    "作息": [
        "已经凌晨1点了，阿哲还在刷题，台灯照着其他人睡不着。",
        "小宇的养生闹钟响了：该睡觉了。",
        "明天早上8点有课，但现在大家还在激情打游戏。",
        "周末早上10点，有人定了7个闹钟但一个都没听见。",
        "宿舍停电了！所有人被迫放下手机开始聊天。",
    ],
    "学习": [
        "期末考试成绩出来了，有人欢喜有人愁。",
        "阿哲发现自己的作业答案被传遍了全班。",
        "明天是ddl，现在一个字还没写。",
        "有人提议组队参加校园创业大赛。",
        "班主任突然发消息说明天要查寝。",
    ],
    "感情": [
        "小明在图书馆看到一个很心动的女生，正在宿舍分享。",
        "有人失恋了，情绪低落，室友们围过来安慰。",
        "隔壁班花给宿舍某个人发了微信，大家都在猜是谁。",
        "情人节快到了，宿舍开始讨论送什么礼物。",
        "朋友圈看到前女友/前男友有了新欢，有点emo。",
    ],
    "金钱": [
        "月底了，大家集体吃土，开始研究泡面的100种吃法。",
        "有人中了彩票（其实就50块），要请客。",
        "宿舍空调费爆了，大家在商讨怎么分摊。",
        "老王借钱买了新皮肤，现在被集体讨伐。",
    ],
    "日常": [
        "宿舍大扫除时间到，有人在装死。",
        "快递小哥打电话来了，但所有人都不想下楼。",
        "有人新买了一个奇奇怪怪的小家电（比如迷你洗衣机）。",
        "隔壁宿舍来串门，带来了一个劲爆八卦。",
        "网断了！游戏打到一半，整个宿舍炸了。",
        "今天学校里出现了一只流浪猫，照片在宿舍群里刷屏。",
    ],
}

# 扁平化事件列表
ALL_EVENTS = []
for category, event_list in EVENTS.items():
    for event in event_list:
        ALL_EVENTS.append({"category": category, "text": event})


def get_random_event(exclude_categories: list[str] | None = None) -> dict:
    """获取一个随机事件

    Args:
        exclude_categories: 要排除的事件类别

    Returns:
        {"category": str, "text": str}
    """
    pool = ALL_EVENTS
    if exclude_categories:
        pool = [e for e in pool if e["category"] not in exclude_categories]
    return random.choice(pool)


def get_event_by_category(category: str) -> dict | None:
    """获取指定类别的一个随机事件"""
    events_in_cat = [e for e in ALL_EVENTS if e["category"] == category]
    if not events_in_cat:
        return None
    return random.choice(events_in_cat)
