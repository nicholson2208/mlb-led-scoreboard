from RGBMatrixEmulator.emulators.canvas import Canvas

# write a new function to override the other SetPixel
def _NewSetPixel(self, x, y, r, g, b, a=255, threshold=75):
    # print("new set pixel")
    if self.display_adapter.pixel_out_of_bounds(x, y):
        return
    
    if a < threshold:
        # print("this pixel is below!", a)
        return

    try:
        pixel = self._Canvas__pixels[int(y)][int(x)]
        pixel.red = r
        pixel.green = g
        pixel.blue = b
    except Exception as e:
        print(e)
        pass

# redirect the set pixel call to my function
Canvas.SetPixel = _NewSetPixel


class RGBMatrix:
    def __init__(self, options = {}):
        self.options = options

        self.width = options.cols * options.chain_length
        self.height = options.rows * options.parallel
        self.brightness = options.brightness

        self.canvas = None

    def CreateFrameCanvas(self):
        self.canvas = Canvas(options = self.options)

        return self.canvas
    
    def SwapOnVSync(self, canvas):
        canvas.check_for_quit_event()
        canvas.draw_to_screen()
        self.canvas = canvas

        return self.canvas

    def Clear(self):
        self.__sync_canvas()
        self.canvas.Clear()
        self.SwapOnVSync(self.canvas)

    def Fill(self, r, g, b):
        self.__sync_canvas()
        self.canvas.Fill(r, g, b)
        self.SwapOnVSync(self.canvas)

    def SetPixel(self, x, y, r, g, b):
        self.__sync_canvas()
        self.canvas.SetPixel(x, y, r, g, b)
        self.SwapOnVSync(self.canvas)

    def SetImage(self, image, offset_x=0, offset_y=0, *other):
        self.__sync_canvas()
        
        self.canvas.SetImage(image, offset_x, offset_y, *other)
        self.SwapOnVSync(self.canvas)
 
    def __sync_canvas(self):        
        if not self.canvas:
            self.canvas = Canvas(options = self.options)

        self.canvas.display_adapter.options.brightness = self.brightness