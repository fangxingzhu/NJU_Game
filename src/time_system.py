class TimeSystem:
    def __init__(self, start_hour=8, start_minute=0):
        self.hour = start_hour
        self.minute = start_minute
        self.frame_count = 0

        # 300帧 = 5秒，5秒走1游戏分钟
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