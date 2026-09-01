from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "blog" / "assets" / "2026-08-25-retirement-pension-withdrawal"
FONT = Path("C:/Windows/Fonts/malgun.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/malgunbd.ttf")


def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT), size)


def canvas():
    return Image.new("RGB", (1080, 1080), "#F7F5EF")


def title(draw, kicker, headline, sub=None):
    draw.text((72, 65), kicker, font=font(28, True), fill="#1C6B55")
    draw.multiline_text((72, 125), headline, font=font(54, True), fill="#17211D", spacing=14)
    if sub:
        draw.multiline_text((72, 275), sub, font=font(29), fill="#52605A", spacing=9)


def rounded(draw, box, fill="#FFFFFF", outline="#D9DED9", radius=30, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def footer(draw, source):
    draw.line((72, 995, 1008, 995), fill="#D4D9D4", width=2)
    draw.text((72, 1014), "브링이슈 정리 · 2026.08.25 확인", font=font(22), fill="#66716C")
    draw.text((1008, 1014), source, font=font(20), fill="#66716C", anchor="ra")


def save_cover():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1080, 18), fill="#1C6B55")
    title(d, "40대 이후 돈과 선택", "퇴직연금 수령방법", "일시금과 연금, 무엇부터 확인해야 할까요?")
    rounded(d, (72, 405, 1008, 885), fill="#FFFFFF")
    d.text((135, 480), "한 번에 받기", font=font(36, True), fill="#8A4F27")
    d.text((135, 548), "일시금", font=font(72, True), fill="#17211D")
    d.line((540, 470, 540, 820), fill="#D9DED9", width=3)
    d.text((605, 480), "나눠서 받기", font=font(36, True), fill="#1C6B55")
    d.text((605, 548), "연금", font=font(72, True), fill="#17211D")
    d.rounded_rectangle((136, 700, 944, 795), 20, fill="#FFF0A8")
    d.text((540, 747), "세금만 보지 말고 생활비 계획까지 함께 비교", font=font(31, True), fill="#3A3420", anchor="mm")
    footer(d, "고용노동부·국세청·법제처")
    im.save(OUT / "cover.png")


def save_comparison():
    im = canvas(); d = ImageDraw.Draw(im)
    title(d, "핵심 비교", "일시금 vs 연금")
    headers = [(72, 250, 300, 325, "확인 항목"), (300, 250, 654, 325, "일시금"), (654, 250, 1008, 325, "연금")]
    for x1,y1,x2,y2,t in headers:
        d.rectangle((x1,y1,x2,y2), fill="#1C6B55")
        d.text(((x1+x2)//2,(y1+y2)//2), t, font=font(27, True), fill="white", anchor="mm")
    rows = [
        ("받는 방식", "한 번에 수령", "5년 이상 나눠 수령"),
        ("법상 기준", "55세 이상,\n일시금 희망", "55세 이상"),
        ("세금 흐름", "연금외수령 세율", "이연퇴직소득세의\n일정 비율 적용"),
        ("생활비", "큰 지출에 대응", "정기 현금흐름 관리"),
        ("먼저 볼 것", "당장 필요한 금액", "월 필요 생활비·기간"),
    ]
    y=325
    for i,(a,b,c) in enumerate(rows):
        h=125; fill="#FFFFFF" if i%2==0 else "#F0F3EF"
        for x1,x2 in [(72,300),(300,654),(654,1008)]: d.rectangle((x1,y,x2,y+h), fill=fill, outline="#D4D9D4", width=2)
        d.multiline_text((186,y+h/2),a,font=font(26,True),fill="#26312C",anchor="mm",align="center",spacing=5)
        d.multiline_text((477,y+h/2),b,font=font(25),fill="#26312C",anchor="mm",align="center",spacing=5)
        d.multiline_text((831,y+h/2),c,font=font(25),fill="#26312C",anchor="mm",align="center",spacing=5)
        y+=h
    d.rounded_rectangle((72, 915, 1008, 973), 16, fill="#FFF0A8")
    d.text((540,944),"개인별 실제 세액은 금융회사 예상 세액으로 다시 확인",font=font(25,True),fill="#3A3420",anchor="mm")
    footer(d,"법제처·국세청")
    im.save(OUT / "comparison.png")


def save_steps():
    im=canvas(); d=ImageDraw.Draw(im)
    title(d,"실행 순서","결정 전에 4가지만 확인")
    items=[("1","내 퇴직연금 유형","DB·DC·IRP와 적립금 확인"),("2","55세·수령 요건","연금 지급기간 5년 이상 확인"),("3","두 방식 예상 세액","금융회사에서 일시금·연금 비교"),("4","내 생활비 계획","목돈 지출과 월 현금흐름 대조")]
    y=255
    for n,h,b in items:
        rounded(d,(72,y,1008,y+155),fill="#FFFFFF")
        d.ellipse((105,y+36,188,y+119),fill="#1C6B55")
        d.text((146,y+77),n,font=font(35,True),fill="white",anchor="mm")
        d.text((225,y+32),h,font=font(31,True),fill="#17211D")
        d.text((225,y+87),b,font=font(26),fill="#52605A")
        y+=175
    d.rounded_rectangle((72, 930, 1008, 980), 15, fill="#FFF0A8")
    d.text((540,955),"IRP를 먼저 해지하지 말고 예상 세액부터 비교하세요",font=font(24,True),fill="#3A3420",anchor="mm")
    footer(d,"고용노동부·법제처·국세청")
    im.save(OUT / "steps.png")


def save_warning():
    im=canvas(); d=ImageDraw.Draw(im)
    title(d,"놓치기 쉬운 부분","같은 ‘연금’도 돈의 출처가 다릅니다")
    rounded(d,(72,300,1008,855),fill="#FFFFFF",outline="#E5C7B3")
    d.text((125,365),"퇴직급여 원금",font=font(36,True),fill="#8A4F27")
    d.text((125,425),"→ 이연퇴직소득 과세 기준",font=font(30),fill="#26312C")
    d.line((125,505,955,505),fill="#DDD6CE",width=2)
    d.text((125,565),"내가 추가 납입한 돈",font=font(36,True),fill="#1C6B55")
    d.text((125,625),"→ 세액공제 여부·운용수익을 따로 확인",font=font(30),fill="#26312C")
    d.rounded_rectangle((125,720,955,805),20,fill="#FFF0A8")
    d.text((540,762),"계좌 전체에 한 세율을 단순 적용하면 안 됩니다",font=font(29,True),fill="#3A3420",anchor="mm")
    footer(d,"국세청 연금계좌 원천징수 기준")
    im.save(OUT / "warning.png")


def save_checklist():
    im=canvas(); d=ImageDraw.Draw(im)
    title(d,"저장용 체크리스트","금융회사에 물어볼 5가지")
    items=["현재 적립금과 퇴직급여 원금은 얼마인가","일시금으로 받을 때 예상 세액은 얼마인가","연금 기간별 예상 수령액과 세액은 얼마인가","계좌 수수료와 운용상품은 어떻게 되는가","중도 인출·해지 시 달라지는 조건은 무엇인가"]
    y=275
    for i,t in enumerate(items,1):
        rounded(d,(72,y,1008,y+115),fill="#FFFFFF")
        d.rectangle((110,y+35,158,y+83),outline="#1C6B55",width=4)
        d.text((190,y+57),t,font=font(27),fill="#26312C",anchor="lm")
        y+=132
    d.text((72,955),"상담 화면을 캡처할 때는 이름·계좌번호를 가리세요.",font=font(24,True),fill="#8A4F27")
    footer(d,"브링이슈 정리")
    im.save(OUT / "checklist.png")


def save_official_crop():
    src=Image.open(OUT/"official-page-16-full.png")
    crop=src.crop((65,690,1125,1455))
    im=Image.new("RGB",(1080,1080),"#F7F5EF")
    d=ImageDraw.Draw(im)
    d.text((72,45),"실제 법령 화면",font=font(28,True),fill="#1C6B55")
    d.text((72,92),"개인형퇴직연금의 수급 요건",font=font(42,True),fill="#17211D")
    crop.thumbnail((936,790))
    im.paste(crop,(72,170))
    footer(d,"국가법령정보센터 시행령 제18조")
    im.save(OUT/"official-screen-01.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    save_cover(); save_comparison(); save_steps(); save_warning(); save_checklist()
