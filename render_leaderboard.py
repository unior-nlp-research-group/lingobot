import utility
import io
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

FONT_SIZE = 20
EMOJI_FONT = ImageFont.truetype("fonts/Symbola.ttf", FONT_SIZE, encoding="utf-8")
TEXT_FONT = ImageFont.truetype("fonts/Roboto-Regular.ttf", FONT_SIZE, encoding="utf-8")

MARGIN = 25
#COLUMN_WIDTH = 100
ROW_HEIGHT = 30
TEXT_HEIGHT = max(EMOJI_FONT.getsize('M')[1], TEXT_FONT.getsize('M')[1])

def get_image_data_from_table(result_table, alignment, show=False):
    NUMBER_ROWS = len(result_table)
    #NUMBER_COLUMNS = len(result_table[0])    
    COLUMNS_WIDTH = [ 2*MARGIN+max(TEXT_FONT.getsize(row[j])[0] for row in result_table) for j in range(len(result_table[0]))]
    WIDTH = MARGIN * 2 + sum(COLUMNS_WIDTH)
    HEIGHT = MARGIN * 2 + TEXT_HEIGHT + NUMBER_ROWS * ROW_HEIGHT
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i, row in enumerate(result_table):
        for j, text in enumerate(row):
            text = text
            text_int = utility.representsInt(text)
            FONT = EMOJI_FONT if (j==0 and i!=0 and not text_int) else TEXT_FONT
            TEXT_WIDTH = FONT.getsize(text)[0]
            aligne = alignment[j]
            if aligne=='l':                
                x = sum(COLUMNS_WIDTH[:j]) + MARGIN 
            elif aligne=='c':
                x = sum(COLUMNS_WIDTH[:j]) + MARGIN + (COLUMNS_WIDTH[j]-TEXT_WIDTH)/2
            else:
                assert(aligne=='r')
                x = sum(COLUMNS_WIDTH[:j]) - TEXT_WIDTH
            y = ROW_HEIGHT*(i+1) + MARGIN - TEXT_HEIGHT
            draw.text((x, y), text, (0, 0, 0), font=FONT)
    with io.BytesIO() as imgData:
        img.save(imgData, format="PNG")
        contents = imgData.getvalue()
    if show:
        img.show()
    return contents

def test():
    result_table = [
        ['RANK', 'NAME', 'POINTS', 'BADGES'],
        ['🥇', 'BOàB', '8', '4'],
        ['🥈', 'PETER', '53', '2'],
        ['🥉', 'ALEX', '3', '3'],
        ['4', 'fdas', '2', '3'],
        ['5', 'trwfgfg', '1', '3']
    ]
    alignment = 'clcc'

    get_image_data_from_table(result_table, alignment, show=True)

if __name__ == "__main__": 
    test()