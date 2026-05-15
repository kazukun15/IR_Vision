
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger
from PIL import Image as PILImage

# メタルUIの背景色
Window.clearcolor = (0.2, 0.22, 0.25, 1)

class PillowIRProcessor:
    def __init__(self):
        self._accumulated = None
        self._palette = self._create_palette()

    def _create_palette(self):
        palette = []
        for i in range(256):
            if i == 0:
                palette.extend([0, 0, 0])
            else:
                palette.extend([255, max(0, 255 - int(i * 1.5)), 0])
        return palette

    def process(self, pixels, width, height, threshold, decay, enable_trail):
        # 変換負荷を抑えるため、即座にリサイズ
        img = PILImage.frombytes('RGBA', (width, height), pixels)
        img = img.resize((320, 240), PILImage.NEAREST)
        
        gray = img.convert('L')
        thresh_img = gray.point(lambda p: p if p >= threshold else 0)
        
        thresh_img.putpalette(self._palette)
        colored = thresh_img.convert('RGB')

        if not enable_trail:
            self._accumulated = None
            return colored
            
        if self._accumulated is None or self._accumulated.size != colored.size:
            self._accumulated = colored
        else:
            safe_decay = max(0.01, min(1.0, decay))
            self._accumulated = PILImage.blend(self._accumulated, colored, safe_decay)

        return self._accumulated

class IRMetalApp(App):
    def build(self):
        self.processor = PillowIRProcessor()
        # [修正点] GPUメモリリークを防ぐため、Textureを使い回す
        self._camera_texture = None 
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])

        self.root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.root.add_widget(Label(text="IR VISION - LIGHTWEIGHT", size_hint_y=0.1, bold=True, font_size='22sp'))
        
        self.img_widget = KivyImage(size_hint_y=0.6)
        self.root.add_widget(self.img_widget)

        self.camera = Camera(play=True, resolution=(640, 480))
        
        ctrl_panel = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        
        ctrl_panel.add_widget(Label(text="SENSITIVITY (Threshold)", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.sens_slider = Slider(min=100, max=255, value=220, cursor_image='knob.png', cursor_size=(40, 40))
        ctrl_panel.add_widget(self.sens_slider)

        ctrl_panel.add_widget(Label(text="AFTERIMAGE TRAIL (Decay)", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.trail_slider = Slider(min=0.01, max=0.3, value=0.15, cursor_image='knob.png', cursor_size=(40, 40))
        ctrl_panel.add_widget(self.trail_slider)

        self.effect_toggle = ToggleButton(text="EFFECT: ON", state='down', size_hint_y=0.4, background_color=(0.4, 0.45, 0.5, 1))
        ctrl_panel.add_widget(self.effect_toggle)
        self.root.add_widget(ctrl_panel)

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        return self.root

    def update(self, dt):
        if not self.camera.texture: return
        try:
            w, h = self.camera.texture.width, self.camera.texture.height
            pixels = self.camera.texture.pixels
            
            processed_pil = self.processor.process(
                pixels=pixels, width=w, height=h,
                threshold=self.sens_slider.value, decay=self.trail_slider.value,
                enable_trail=(self.effect_toggle.state == 'down')
            )
            
            processed_pil = processed_pil.transpose(PILImage.FLIP_TOP_BOTTOM)
            buf = processed_pil.tobytes()
            
            # [修正点] 毎フレーム生成せず、既存のテクスチャを上書き更新
            if self._camera_texture is None or self._camera_texture.size != processed_pil.size:
                self._camera_texture = Texture.create(size=processed_pil.size, colorfmt='rgb')
            
            self._camera_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.img_widget.texture = self._camera_texture
            
        except Exception as e:
            # [修正点] エラーの握り潰しをやめ、実機デバッグ可能なロギングに変更
            Logger.exception(f"IRVision Frame processing error: {e}")

if __name__ == '__main__':
    IRMetalApp().run()
