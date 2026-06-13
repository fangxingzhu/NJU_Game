import os
import pygame


class MusicManager:
    def __init__(self, playlist=None):
        self.enabled = True
        self.current_music = None
        self.volume = 0.45
        self.playlist = playlist or []          # 歌曲路径列表
        self.current_index = -1                 # 当前播放索引
        self.loop_playlist = True               # 列表循环

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error:
            print("音乐系统初始化失败")
            self.enabled = False

        # 注册音乐结束事件，用于更灵敏的切歌
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

    def set_playlist(self, playlist):
        """设置歌单"""
        self.playlist = playlist
        self.current_index = -1

    def play(self, path=None, loop=False):
        """播放指定音乐，若未指定路径则继续播放当前曲目"""
        if not self.enabled:
            return

        if path:
            if not os.path.exists(path):
                print(f"找不到音乐文件：{path}")
                return
            if self.current_music == path:
                return
            self.current_music = path
            pygame.mixer.music.load(path)
            # 如果是单曲循环则 -1，否则只播一次（之后由 update 切歌）
            pygame.mixer.music.play(-1 if loop else 0)
        elif self.playlist:
            # 没有指定路径，从歌单中继续播放
            self._play_next()

    def _play_next(self):
        """播放歌单中的下一首"""
        if not self.playlist or not self.enabled:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        path = self.playlist[self.current_index]
        if not os.path.exists(path):
            print(f"找不到音乐文件：{path}")
            # 跳过并尝试下一首
            self._play_next()
            return
        self.current_music = path
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)  # 播放一次，结束后触发 USEREVENT

    def update(self):
        """每帧调用，检测是否需要切歌"""
        if not self.enabled or not self.playlist:
            return

        # 检查是否有音乐结束事件（更可靠）
        for event in pygame.event.get(pygame.USEREVENT):
            if event.type == pygame.USEREVENT:
                self._play_next()

        # 备用检测：如果没有结束事件，但音乐不在播放且之前有播放过
        if not pygame.mixer.music.get_busy() and self.current_index >= 0:
            self._play_next()

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def is_enabled(self):
        return self.enabled