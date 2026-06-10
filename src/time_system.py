class TimeSystem:
    def __init__(self, start_hour=8, start_minute=0):
        self.day = 1
        self.hour = start_hour
        self.minute = start_minute
        self.frame_count = 0
        self.frames_per_game_minute = 300

    def update(self):
        self.frame_count += 1
        if self.frame_count >= self.frames_per_game_minute:
            self.frame_count = 0
            self.minute += 1
            if self.minute >= 60:
                self.minute = 0
                self.hour += 1
                if self.hour >= 24:
                    self.hour = 0
                    self.day += 1

    def get_current_hour(self):
        return self.hour

    def get_current_minute(self):
        return self.minute

    def get_time_string(self):
        return f"{self.hour:02d}:{self.minute:02d}"

    def is_night(self):
        return self.hour >= 18 or self.hour < 6

    def is_daytime(self):
        return not self.is_night()

    def is_night_daytime(self):
        return self.is_night() and self.is_daytime()

    # 新增：获取星期文字
    def get_weekday(self):
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        # day 从 1 开始，1 -> 星期一
        index = (self.day - 1) % 7
        return weekdays[index]
