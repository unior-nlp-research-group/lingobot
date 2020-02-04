import utility
from io import StringIO
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

FONT_SIZE = 20
FONT = ImageFont.truetype("fonts/Symbola.ttf",FONT_SIZE)

MARGIN = 15
#COLUMN_WIDTH = 100
ROW_HEIGHT = 30
TEXT_HEIGHT = FONT.getsize('M')[1]

def getResultImage(result_table, alignment, show=False):
    NUMBER_ROWS = len(result_table)
    #NUMBER_COLUMNS = len(result_table[0])    
    COLUMNS_WIDTH = [ 2*MARGIN+max(FONT.getsize(row[j])[0] for row in result_table) for j in range(len(result_table[0]))]
    WIDTH = MARGIN * 2 + sum(COLUMNS_WIDTH)
    HEIGHT = MARGIN * 2 + TEXT_HEIGHT + NUMBER_ROWS * ROW_HEIGHT
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i, row in enumerate(result_table):
        for j, text in enumerate(row):
            text = utility.safe_decode_utf(text)
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
    imgData = StringIO()
    img.save(imgData, format="PNG")
    if show:
        img.show()
    return imgData.getvalue()

def test():
    result_table = [
        ['RANK', 'NAME', 'POINTS', 'BADGES'],
        ['1', 'BOB', '5', '4'],
        ['2', 'PETER', '3', '2'],
        ['3', 'ALEX', '1', '3']
    ]
    alignment = 'clcc'

    getResultImage(result_table, alignment, show=True)

if __name__ == "__main__": 
    test()