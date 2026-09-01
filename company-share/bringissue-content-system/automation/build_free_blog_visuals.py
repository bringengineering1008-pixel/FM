from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1200, 675
FONT = "C:/Windows/Fonts/malgun.ttf"
BOLD = "C:/Windows/Fonts/malgunbd.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def canvas(bg="#F7F4EE"):
    return Image.new("RGB", (W, H), bg), ImageDraw.Draw(Image.new("RGB", (1, 1)))


def rr(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def header(draw, eyebrow, title, subtitle, accent):
    rr(draw, (64, 54, 242, 92), 19, accent)
    draw.text((84, 62), eyebrow, font=font(20, True), fill="white")
    draw.text((64, 122), title, font=font(52, True), fill="#18202A")
    draw.text((66, 190), subtitle, font=font(25), fill="#59616C")


def gift_icon(draw, cx, cy, color):
    rr(draw, (cx-60, cy-38, cx+60, cy+62), 12, color)
    draw.rectangle((cx-7, cy-38, cx+7, cy+62), fill="#FFF5D9")
    draw.rectangle((cx-60, cy-8, cx+60, cy+8), fill="#FFF5D9")
    draw.arc((cx-58, cy-86, cx+2, cy-20), 205, 355, fill=color, width=11)
    draw.arc((cx-2, cy-86, cx+58, cy-20), 185, 335, fill=color, width=11)


def build_gift():
    im = Image.new("RGB", (W, H), "#FFF8ED"); d = ImageDraw.Draw(im)
    header(d, "2026 추석 준비", "선물은 사람부터 나눠보세요", "할인율보다 수령 대상과 배송일을 먼저 정리합니다", "#C56A3A")
    cards = [(64, 275, 400, 590, "부모님·가족", "보관 공간과 식습관", "#D46A55"),
             (432, 275, 768, 590, "직장·거래처", "포장과 전달 편의", "#4F7B72"),
             (800, 275, 1136, 590, "가까운 지인", "보관이 쉬운 구성", "#7B6EA8")]
    for x1,y1,x2,y2,t,s,c in cards:
        rr(d,(x1,y1,x2,y2),28,"#FFFFFF",outline="#E9DFD3",width=3)
        gift_icon(d,(x1+x2)//2,385,c)
        d.text((x1+28,490),t,font=font(30,True),fill="#202832")
        d.text((x1+28,535),s,font=font(21),fill="#68717B")
    d.text((64,625),"BRING ISSUE  ·  자체 제작 이해 이미지",font=font(18),fill="#9A8575")
    out=ROOT/"blog/assets/2026-08-23-chuseok-gift-guide/editorial-gift-planning.jpg"; out.parent.mkdir(parents=True,exist_ok=True); im.save(out,"JPEG",quality=95)


def phone(draw, x, y):
    rr(draw,(x,y,x+245,y+330),34,"#17202B")
    rr(draw,(x+14,y+18,x+231,y+308),25,"#F1F4F7")
    rr(draw,(x+42,y+52,x+203,y+160),16,"#CCD5DF")
    draw.polygon([(x+105,y+82),(x+105,y+132),(x+150,y+107)],fill="#FFFFFF")
    for i,w in enumerate([134,172,105]): rr(draw,(x+42,y+190+i*32,x+42+w,y+205+i*32),7,"#D8DEE6")


def build_viewer():
    im=Image.new("RGB",(W,H),"#F2F6FA"); d=ImageDraw.Draw(im)
    header(d,"조회수 업데이트","숫자가 빨리 오르면 무엇이 달라질까?","공개 조회수와 실제 성과 지표는 같은 뜻이 아닙니다","#D44545")
    phone(d,120,280)
    pts=[(470,515),(545,480),(620,495),(695,420),(770,390),(845,315),(920,350),(1000,245)]
    for a,b in zip(pts,pts[1:]): d.line((a[0],a[1],b[0],b[1]),fill="#D44545",width=10)
    for x,y in pts: d.ellipse((x-13,y-13,x+13,y+13),fill="#D44545")
    d.text((480,555),"보이는 숫자 ↑",font=font(31,True),fill="#D44545")
    d.text((770,555),"수익·추천은 별도 확인",font=font(27,True),fill="#263444")
    d.text((64,625),"BRING ISSUE  ·  자체 제작 설명 이미지",font=font(18),fill="#7D8A98")
    out=ROOT/"blog/assets/2026-08-23-youtube-view-count/editorial-viewer-metrics.png"; out.parent.mkdir(parents=True,exist_ok=True); im.save(out)


def build_creator():
    im=Image.new("RGB",(W,H),"#F8F6F1"); d=ImageDraw.Draw(im)
    header(d,"운영자 체크","조회수 하나만 보면 놓치는 것", "유입과 체류를 나누어 보면 다음 콘텐츠가 보입니다", "#345D8C")
    panels=[(74,286,560,575,"공개 조회수","영상이 시작된 횟수","#D64A4A"),(640,286,1126,575,"유효한 시청 반응","머문 시간과 참여 흐름","#345D8C")]
    for x1,y1,x2,y2,t,s,c in panels:
        rr(d,(x1,y1,x2,y2),28,"#FFFFFF",outline="#DDD8CE",width=3)
        d.text((x1+34,y1+34),t,font=font(34,True),fill="#202832")
        d.text((x1+34,y1+84),s,font=font(22),fill="#68717B")
        if x1<100:
            for i,h in enumerate([60,105,82,150,190]): rr(d,(x1+45+i*75,y2-45-h,x1+95+i*75,y2-45),10,c)
        else:
            p=[(x1+55,y2-95),(x1+145,y2-130),(x1+235,y2-125),(x1+325,y2-185),(x1+415,y2-205)]
            for a,b in zip(p,p[1:]): d.line((*a,*b),fill=c,width=10)
            for x,y in p: d.ellipse((x-12,y-12,x+12,y+12),fill=c)
    d.text((64,625),"BRING ISSUE  ·  자체 제작 설명 이미지",font=font(18),fill="#8B8579")
    out=ROOT/"blog/assets/2026-08-23-youtube-view-count/editorial-creator-analysis.png"; out.parent.mkdir(parents=True,exist_ok=True); im.save(out)


build_gift(); build_viewer(); build_creator()
