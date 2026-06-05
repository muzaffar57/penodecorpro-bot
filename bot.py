import os
import logging
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.units import cm
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

ROM_NARXLAR = {
    "MODEL-01": {"Rom bezak": {"Katta razmer": 140000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 110000, "Kichik razmer": 85000}},
    "MODEL-02": {"Rom bezak": {"Katta razmer": 110000, "Kichik razmer": 80000}, "Eshik bezak": {"Katta razmer": 80000, "Kichik razmer": 60000}},
    "MODEL-03": {"Rom bezak": {"Katta razmer": 120000, "Kichik razmer": 96000}, "Eshik bezak": {"Katta razmer": 90000, "Kichik razmer": 70000}},
    "MODEL-04": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 120000}, "Eshik bezak": {"Katta razmer": 110000, "Kichik razmer": 90000}},
    "MODEL-05": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 140000, "Kichik razmer": 100000}},
    "MODEL-06": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 140000, "Kichik razmer": 100000}},
    "MODEL-07": {"Rom bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}, "Eshik bezak": {"Katta razmer": 90000, "Kichik razmer": 70000}},
    "MODEL-08": {"Rom bezak": {"Katta razmer": 140000, "Kichik razmer": 105000}, "Eshik bezak": {"Katta razmer": 110000, "Kichik razmer": 90000}},
    "MODEL-09": {"Rom bezak": {"Katta razmer": 140000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 110000, "Kichik razmer": 90000}},
    "MODEL-10": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 120000}, "Eshik bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}},
    "MODEL-11": {"Rom bezak": {"Katta razmer": 140000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 85000, "Kichik razmer": 70000}},
    "MODEL-12": {"Rom bezak": {"Katta razmer": 160000, "Kichik razmer": 130000}, "Eshik bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}},
    "MODEL-13": {"Rom bezak": {"Katta razmer": 160000, "Kichik razmer": 130000}, "Eshik bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}},
    "MODEL-14": {"Rom bezak": {"Katta razmer": 160000, "Kichik razmer": 130000}, "Eshik bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}},
    "MODEL-15": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 120000}, "Eshik bezak": {"Katta razmer": 120000, "Kichik razmer": 100000}},
    "MODEL-16": {"Rom bezak": {"Katta razmer": 130000, "Kichik razmer": 100000}, "Eshik bezak": {"Katta razmer": 100000, "Kichik razmer": 80000}},
}

USTUN_NARXLAR = {
    "25sm": 18000, "30sm": 21000, "35sm": 24000,
    "40sm": 28000, "45sm": 32000, "50sm": 36000,
}

KARNIZ_NARXLAR = {
    "MODEL-01": {"Kichik (17sm)": 38000, "Ortacha (20sm)": 48000, "Katta (25sm)": 70000},
    "MODEL-02": {"Kichik (17sm)": 22000, "Ortacha (20sm)": 32000, "Katta (25sm)": 45000},
    "MODEL-03": {"Kichik (17sm)": 32000, "Ortacha (20sm)": 42000, "Katta (25sm)": 55000},
    "MODEL-04": {"Kichik (17sm)": 30000, "Ortacha (20sm)": 42000, "Katta (25sm)": 60000},
    "MODEL-05": {"Kichik (17sm)": 20000, "Ortacha (20sm)": 25000, "Katta (25sm)": 42000},
    "MODEL-06": {"Kichik (17sm)": 19000, "Ortacha (20sm)": 25000, "Katta (25sm)": 34000},
    "MODEL-07": {"Kichik (17sm)": 16000, "Ortacha (20sm)": 20000, "Katta (25sm)": 28000},
    "MODEL-08": {"Kichik (17sm)": 26000, "Ortacha (20sm)": 34000, "Katta (25sm)": 50000},
    "MODEL-09": {"Kichik (17sm)": 19000, "Ortacha (20sm)": 26000, "Katta (25sm)": 40000},
    "MODEL-10": {"Kichik (17sm)": 17000, "Ortacha (20sm)": 24000, "Katta (25sm)": 36000},
    "MODEL-11": {"Kichik (17sm)": 22000, "Ortacha (20sm)": 30000, "Katta (25sm)": 44000},
    "MODEL-12": {"Kichik (17sm)": 17000, "Ortacha (20sm)": 28000, "Katta (25sm)": 44000},
    "MODEL-13": {"Kichik (17sm)": 21000, "Ortacha (20sm)": 28000, "Katta (25sm)": 45000},
    "MODEL-14": {"Kichik (17sm)": 18000, "Ortacha (20sm)": 25000, "Katta (25sm)": 36000},
    "MODEL-15": {"Kichik (17sm)": 20000, "Ortacha (20sm)": 28000, "Katta (25sm)": 45000},
    "MODEL-16": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 18000, "Katta (25sm)": 25000},
    "MODEL-17": {"Kichik (17sm)": 25000, "Ortacha (20sm)": 44000, "Katta (25sm)": 55000},
    "MODEL-18": {"Kichik (17sm)": 27000, "Ortacha (20sm)": 36000, "Katta (25sm)": 55000},
    "MODEL-19": {"Kichik (17sm)": 33000, "Ortacha (20sm)": 42000, "Katta (25sm)": 65000},
    "MODEL-20": {"Kichik (17sm)": 30000, "Ortacha (20sm)": 42000, "Katta (25sm)": 65000},
    "MODEL-21": {"Kichik (17sm)": 32000, "Ortacha (20sm)": 44000, "Katta (25sm)": 66000},
    "MODEL-22": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 18000, "Katta (25sm)": 24000},
    "MODEL-23": {"Kichik (17sm)": 23000, "Ortacha (20sm)": 37000, "Katta (25sm)": 50000},
    "MODEL-24": {"Kichik (17sm)": 16000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-25": {"Kichik (17sm)": 20000, "Ortacha (20sm)": 30000, "Katta (25sm)": 43000},
    "MODEL-26": {"Kichik (17sm)": 32000, "Ortacha (20sm)": 40000, "Katta (25sm)": 62000},
}

BELBOG_NARXLAR = {
    "MODEL-01": {"Kichik (17sm)": 22000, "Ortacha (20sm)": 30000, "Katta (25sm)": 46000},
    "MODEL-02": {"Kichik (17sm)": 18000, "Ortacha (20sm)": 26000, "Katta (25sm)": 42000},
    "MODEL-03": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-04": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-05": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-06": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-07": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-08": {"Kichik (17sm)": 17000, "Ortacha (20sm)": 22000, "Katta (25sm)": 30000},
    "MODEL-09": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-10": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-11": {"Kichik (17sm)": 17000, "Ortacha (20sm)": 20000, "Katta (25sm)": 35000},
    "MODEL-12": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-13": {"Kichik (17sm)": 15000, "Ortacha (20sm)": 21000, "Katta (25sm)": 31000},
    "MODEL-14": {"Kichik (17sm)": 18000, "Ortacha (20sm)": 24000, "Katta (25sm)": 30000},
    "MODEL-15": {"Kichik (17sm)": 19000, "Ortacha (20sm)": 27000, "Katta (25sm)": 40000},
    "MODEL-16": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-17": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 21000, "Katta (25sm)": 33000},
    "MODEL-18": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
    "MODEL-19": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 18000, "Katta (25sm)": 20000},
    "MODEL-20": {"Kichik (17sm)": 15000, "Ortacha (20sm)": 21000, "Katta (25sm)": 32000},
    "MODEL-21": {"Kichik (17sm)": 16000, "Ortacha (20sm)": 22000, "Katta (25sm)": 32000},
    "MODEL-22": {"Kichik (17sm)": 20000, "Ortacha (20sm)": 27000, "Katta (25sm)": 42000},
    "MODEL-23": {"Kichik (17sm)": 21000, "Ortacha (20sm)": 28000, "Katta (25sm)": 42000},
    "MODEL-24": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 20000, "Katta (25sm)": 28000},
    "MODEL-25": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 18000, "Katta (25sm)": 29000},
    "MODEL-26": {"Kichik (17sm)": 14000, "Ortacha (20sm)": 19000, "Katta (25sm)": 29000},
    "MODEL-27": {"Kichik (17sm)": 16000, "Ortacha (20sm)": 22000, "Katta (25sm)": 32500},
    "MODEL-28": {"Kichik (17sm)": 13000, "Ortacha (20sm)": 20000, "Katta (25sm)": 30000},
}

def get_birlik_narx(category, model, razmer, tur=None, qoplama="Ha"):
    narx = None
    try:
        if category == "Rom bezaklari":
            narx = ROM_NARXLAR[model][tur][razmer]
        elif category == "Ustunlar":
            narx = USTUN_NARXLAR.get(razmer)
        elif category == "Karnizlar":
            narx = KARNIZ_NARXLAR[model][razmer]
        elif category == "Belbog' karnizlar":
            narx = BELBOG_NARXLAR[model][razmer]
        elif category == "Devorga ramkalar":
            narx = RAMKA_NARXLAR.get(model)
    except:
        return None
    if narx and qoplama == "Yo'q":
        narx = narx // 2
    return narx

def format_narx(narx):
    return "{:,}".format(narx).replace(",", " ") + " so'm"

def create_pdf_bytes(mijoz_ism, savat_items):
    buffer = io.BytesIO()

    def on_page(canvas_obj, doc):
        canvas_obj.saveState()
        w, h = A4

        # Header
        canvas_obj.setFillColor(colors.HexColor("#1A252F"))
        canvas_obj.rect(0, h - 3.5*cm, w, 3.5*cm, fill=1, stroke=0)

        # Logo rasm
        try:
            import urllib.request
            from reportlab.lib.utils import ImageReader
            logo_url = "https://muzaffar57.github.io/-penodecor-katalog/LOGO.jpg"
            logo_data = urllib.request.urlopen(logo_url, timeout=5).read()
            logo_img = ImageReader(io.BytesIO(logo_data))
            canvas_obj.drawImage(logo_img, 1.5*cm, h - 3.2*cm, width=2.2*cm, height=2.2*cm, preserveAspectRatio=True, mask='auto')
        except:
            # Logo yuklanmasa qizil doira chiqsin
            canvas_obj.setFillColor(colors.HexColor("#E74C3C"))
            canvas_obj.circle(3*cm, h - 1.75*cm, 1.1*cm, fill=1, stroke=0)
            canvas_obj.setFillColor(colors.white)
            canvas_obj.setFont("Helvetica-Bold", 22)
            canvas_obj.drawCentredString(3*cm, h - 2.1*cm, "P")

        # Kompaniya nomi
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont("Helvetica-Bold", 20)
        canvas_obj.drawString(4.5*cm, h - 1.5*cm, "PenoDecorPro")
        canvas_obj.setFillColor(colors.HexColor("#BDC3C7"))
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(4.5*cm, h - 2.1*cm, "Fasad bezaklari ishlab chiqarish")

        # Telefonlar
        canvas_obj.setFillColor(colors.HexColor("#ECF0F1"))
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(w - 2*cm, h - 1.2*cm, "+998 97 999 57 57")
        canvas_obj.drawRightString(w - 2*cm, h - 1.7*cm, "+998 90 623 22 72")
        canvas_obj.drawRightString(w - 2*cm, h - 2.2*cm, "+998 97 699 19 19")

        # Sariq chiziq
        canvas_obj.setFillColor(colors.HexColor("#F39C12"))
        canvas_obj.rect(0, h - 3.5*cm, w, 0.15*cm, fill=1, stroke=0)

        # Footer
        canvas_obj.setFillColor(colors.HexColor("#1A252F"))
        canvas_obj.rect(0, 0, w, 2.8*cm, fill=1, stroke=0)
        canvas_obj.setFillColor(colors.HexColor("#F39C12"))
        canvas_obj.rect(0, 2.8*cm, w, 0.12*cm, fill=1, stroke=0)

        canvas_obj.setFillColor(colors.HexColor("#BDC3C7"))
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawString(2*cm, 2.1*cm, "MANZIL:")
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(2*cm, 1.7*cm, "Andijon shahar, 134-uy, mo'ljal: Yog' zavodi orqa tomoni")

        canvas_obj.setFillColor(colors.HexColor("#F39C12"))
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawCentredString(w/2, 1.1*cm, "Doimiy mijozlar ro'yxatiga qo'shiling va bonuslarga ega bo'ling!")

        canvas_obj.setFillColor(colors.HexColor("#7F8C8D"))
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawRightString(w - 2*cm, 0.4*cm, "PenoDecorPro © 2026")

        canvas_obj.restoreState()

    frame = Frame(2*cm, 3.2*cm, A4[0] - 4*cm, A4[1] - 7.2*cm, id='main')
    template = PageTemplate(id='main', frames=[frame], onPage=on_page)
    doc = BaseDocTemplate(buffer, pagesize=A4, pageTemplates=[template])

    story = []
    title_style = ParagraphStyle('t', fontSize=16, fontName='Helvetica-Bold', alignment=1, textColor=colors.HexColor("#1A252F"), spaceAfter=4)
    sub_style = ParagraphStyle('s', fontSize=9, fontName='Helvetica', alignment=1, textColor=colors.HexColor("#7F8C8D"), spaceAfter=8)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("BUYURTMA HISOB-KITOBI", title_style))
    story.append(Paragraph("Ushbu hujjat rasmiy buyurtma tasdiqlash hujjati hisoblanadi", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#F39C12")))
    story.append(Spacer(1, 0.3*cm))

    from datetime import timezone, timedelta
    uzb_tz = timezone(timedelta(hours=5))
    now_uzb = datetime.now(uzb_tz)
    sana = now_uzb.strftime("%d.%m.%Y %H:%M") + " (Andijon vaqti)"
    buyurtma_no = "BDP-" + now_uzb.strftime("%Y%m%d%H%M")
    info_data = [
        ["Mijoz:", mijoz_ism, "Sana:", sana],
        ["Buyurtma №:", buyurtma_no, "Holat:", "Kutilmoqda"],
    ]
    info_table = Table(info_data, colWidths=[2.5*cm, 7.5*cm, 2.5*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(info_table)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7")))
    story.append(Spacer(1, 0.3*cm))

    table_data = [["#", "Mahsulot", "Miqdor", "Birlik narx", "Jami"]]
    jami_umumiy = 0

    for i, item in enumerate(savat_items, 1):
        category = item.get("category", "")
        model = item.get("model", "")
        razmer = item.get("razmer", "")
        qoplama = item.get("qoplama", "")
        rom_tur = item.get("rom_tur", "")
        miqdor_text = item.get("miqdor_text", "")
        jami_narx = item.get("jami_narx", 0) or 0
        birlik_narx = item.get("birlik_narx", 0) or 0

        mahsulot = category + "\n" + model
        if rom_tur:
            mahsulot += " | " + rom_tur
        if razmer:
            mahsulot += "\n" + razmer
        if qoplama:
            mahsulot += " | Qoplama: " + qoplama

        jami_umumiy += jami_narx
        table_data.append([
            str(i), mahsulot, miqdor_text,
            format_narx(birlik_narx) if birlik_narx else "-",
            format_narx(jami_narx) if jami_narx else "Hisoblanadi"
        ])

    table_data.append(["", "", "", "UMUMIY JAMI:", format_narx(jami_umumiy) if jami_umumiy else "Hisoblanadi"])

    col_widths = [0.8*cm, 7*cm, 3.5*cm, 3.2*cm, 3.5*cm]
    prod_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A252F")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8F9FA")]),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#DEE2E6")),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('LEFTPADDING', (1,1), (1,-1), 6),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EBF5FB")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 10),
        ('TEXTCOLOR', (3,-1), (-1,-1), colors.HexColor("#E74C3C")),
        ('LINEABOVE', (0,-1), (-1,-1), 2, colors.HexColor("#1A252F")),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 0.5*cm))

    rahmat_style = ParagraphStyle('r', fontSize=9, fontName='Helvetica-Bold',
        alignment=1, textColor=colors.HexColor("#E74C3C"))
    story.append(Paragraph("Rahmat! Buyurtmangiz qabul qilindi. Tez orada siz bilan bog'lanamiz.", rahmat_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

KATALOG_LINKS = {
    "Rom bezaklari": "https://muzaffar57.github.io/-penodecor-katalog/katalog.html",
    "Ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/ustun.html",
    "Belbog' karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/belbog.html",
    "Yumaloq ustunlar": "https://muzaffar57.github.io/-penodecor-katalog/yumaloq.html",
    "Kapitel va baza": "https://muzaffar57.github.io/-penodecor-katalog/kapitel.html",
    "Kalvak": "https://muzaffar57.github.io/-penodecor-katalog/kalvak.html",
    "Karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/karniz.html",
    "Shohona karnizlar": "https://muzaffar57.github.io/-penodecor-katalog/shohona.html",
    "Barelef gullar": "https://muzaffar57.github.io/-penodecor-katalog/barelef.html",
    "Devorga ramkalar": "https://muzaffar57.github.io/-penodecor-katalog/ramka.html",
}

KATALOG_COUNTS = {
    "Rom bezaklari": 16, "Ustunlar": 13, "Belbog' karnizlar": 27,
    "Yumaloq ustunlar": 12, "Kapitel va baza": 16, "Kalvak": 9,
    "Karnizlar": 26, "Shohona karnizlar": 12, "Barelef gullar": 7,
    "Devorga ramkalar": 7,
}

USTUN_RAZMERLAR = ["25sm", "30sm", "35sm", "40sm", "45sm", "50sm"]
KARNIZ_RAZMERLAR = ["17sm", "20sm", "25sm", "25sm dan katta"]

# Karniz razmer → narx kaliti mapping
KARNIZ_RAZMER_MAP = {
    "17sm": "Kichik (17sm)",
    "20sm": "Ortacha (20sm)",
    "25sm": "Katta (25sm)",
    "Kichik 17sm": "Kichik (17sm)",
    "Ortacha 20sm": "Ortacha (20sm)",
    "Katta 25sm": "Katta (25sm)",
    "Kichik (17sm)": "Kichik (17sm)",
    "Ortacha (20sm)": "Ortacha (20sm)",
    "Katta (25sm)": "Katta (25sm)",
}

MIQDOR_SHABLONLAR = {
    "Rom bezaklari": "Nechta rom va nechta eshik bor?\n\nRom soni: ___\nEshik soni: ___\n\nMasalan:\nRom soni: 8\nEshik soni: 4",
    "Ustunlar": "Qancha metr kerak?\nMasalan: 12",
    "Belbog' karnizlar": "Qancha metr kerak?\nMasalan: 25",
    "Karnizlar": "Qancha metr kerak?\nMasalan: 30",
    "Devorga ramkalar": "Necha dona kerak?\nFaqat raqam yozing:\nMasalan: 3",
}

OLCHAM_SHABLONLAR = {
    "Shohona karnizlar": "Bo'yi necha sm va qancha metr kerak?\nMasalan: Bo'yi 50sm, 20 metr",
    "Yumaloq ustunlar": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 30sm, 4 dona",
    "Kapitel va baza": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 40sm, 4 dona",
    "Barelef gullar": "O'lchamlarni kiriting:\nUzunligi: ___\nBo'yi: ___\nSoni: ___",
    "Kalvak": "O'lchamlarni kiriting:\nUzunligi: ___\nEni: ___\nQalinligi: ___\nSoni: ___",
}

RAMKA_NARXLAR = {
    "MODEL-01": 180000,
    "MODEL-02": 250000,
    "MODEL-03": 240000,
    "MODEL-04": 190000,
    "MODEL-05": 290000,
    "MODEL-06": 220000,
    "MODEL-07": 250000,
}

KAPITEL_NARXLAR = {
    "25sm": 14000, "30sm": 16000, "35sm": 18000,
    "40sm": 20000, "45sm": 22000, "50sm": 24000,
}
BAZA_NARXLAR = {
    "25sm": 12000, "30sm": 14000, "35sm": 16000,
    "40sm": 18000, "45sm": 20000, "50sm": 22000,
}

CHOOSING, MODEL_SELECTION, QOPLAMA, RAZMER_TANLOV, ROM_TUR, ROM_SONI, ESHIK_SONI, MIQDOR, OLCHAM, LOYIHA_PHOTO, FASAD_PHOTO, CUSTOM_PHOTO, KONTAKT_ISM, KONTAKT_TEL, TAHRIR_MIQDOR, KAPITEL_SONI, BAZA_SONI = range(17)

orders = {}
savat = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("📐 Mahsulotlar (Katalog)")],
        [KeyboardButton("🧮 Loyiha bo'yicha hisoblash")],
        [KeyboardButton("🏡 Fasad loyihasi tayyorlash")],
        [KeyboardButton("🏗 Bajarilgan loyihalar")],
        [KeyboardButton("🛒 Savatim"), KeyboardButton("🧾 Jami hisob (PDF)")],
        [KeyboardButton("📞 Kontaktlar / Menejer")],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Deep link parametrini tekshirish
    # Format: /start karniz_MODEL-05
    if context.args:
        param = context.args[0]  # masalan: karniz_MODEL-05
        parts = param.split("_", 1)
        if len(parts) == 2:
            bolim_kod = parts[0]
            model = parts[1].replace("-", "-")

            bolim_map = {
                "karniz": "Karnizlar",
                "belbog": "Belbog' karnizlar",
                "rom": "Rom bezaklari",
                "ustun": "Ustunlar",
                "yumaloq": "Yumaloq ustunlar",
                "kapitel": "Kapitel va baza",
                "kalvak": "Kalvak",
                "shohona": "Shohona karnizlar",
                "barelef": "Barelef gullar",
                "ramka": "Devorga ramkalar",
            }

            category = bolim_map.get(bolim_kod)
            if category and model.startswith("MODEL"):
                model = model.replace("_", "-")  # MODEL_06 → MODEL-06
                context.user_data["category"] = category
                context.user_data["model"] = model

                await update.message.reply_text(
                    "Assalomu alaykum, " + user.first_name + "!\n\n"
                    "Katalogdan tanladingiz:\n"
                    "📦 " + category + " — " + model,
                    reply_markup=markup
                )

                # Qoplama so'rash
                kb = [
                    [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
                    [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
                ]

                if category == "Rom bezaklari":
                    kb2 = [
                        [InlineKeyboardButton("Katta razmer", callback_data="razmer_Katta_razmer")],
                        [InlineKeyboardButton("Kichik razmer", callback_data="razmer_Kichik_razmer")],
                    ]
                    await update.message.reply_text(
                        model + " — Razmer tanlang:",
                        reply_markup=InlineKeyboardMarkup(kb2)
                    )
                    return RAZMER_TANLOV
                elif category in ["Karnizlar", "Belbog' karnizlar"]:
                    kb2 = [[InlineKeyboardButton(r, callback_data="razmer_" + r.replace(" ", "_").replace("(","").replace(")",""))] for r in KARNIZ_RAZMERLAR]
                    await update.message.reply_text(
                        model + " — Razmer tanlang:",
                        reply_markup=InlineKeyboardMarkup(kb2)
                    )
                    return RAZMER_TANLOV
                elif category == "Ustunlar":
                    kb2 = [[InlineKeyboardButton(r, callback_data="razmer_" + r)] for r in USTUN_RAZMERLAR]
                    await update.message.reply_text(
                        model + " — Razmer tanlang:",
                        reply_markup=InlineKeyboardMarkup(kb2)
                    )
                    return RAZMER_TANLOV
                elif category in ["Barelef gullar", "Kalvak", "Shohona karnizlar", "Yumaloq ustunlar", "Kapitel va baza"]:
                    context.user_data["qoplama"] = "Yo'q"
                    keyboard_aloqa = [
                        [InlineKeyboardButton("📞 Boshqa razmer — aloqaga chiqing", url="https://t.me/penodecorprobot")]
                    ]
                    await update.message.reply_text(
                        model + " tanlandingiz!\n\n"
                        "ℹ️ Bu mahsulotlar qoplamasiz holatda taqdim etiladi.\n\n"
                        "Necha dona kerak?\nFaqat raqam yozing:\nMasalan: 4",
                        reply_markup=InlineKeyboardMarkup(keyboard_aloqa)
                    )
                    return OLCHAM
                else:
                    await update.message.reply_text(
                        model + " tanlandi!\n\nQoplama tortilsinmi?\n\n"
                        "ℹ️ Narxlar qoplama bilan hisoblangan.\n"
                        "Qoplama shart bo'lmasa — narx 2 barobar arzon!",
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                    return QOPLAMA

    await update.message.reply_text(
        "Assalomu alaykum, " + user.first_name + "! 👋\n\n"
        "🏛️ *PenoDecorPro* botiga xush kelibsiz!\n\n"
        "Biz Andijon shahrida fasad bezaklari ishlab chiqaramiz:\n\n"
        "🪟 Rom va eshik bezaklari\n"
        "📐 Karnizlar va belbog' karnizlar\n"
        "🏛️ Ustunlar va yumaloq ustunlar\n"
        "🌸 Barelef gullar va kalvak\n"
        "🔲 Devorga ramkalar\n\n"
        "Bu bot orqali:\n"
        "✅ Katalogni ko'rishingiz\n"
        "✅ Narxlarni bilishingiz\n"
        "✅ PDF hisob-kitob olishingiz\n"
        "✅ Buyurtma berishingiz mumkin!\n\n"
        "👇 Quyidagi menyudan boshlang:",
        parse_mode="Markdown"
    )
    await update.message.reply_text(
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=markup
    )
    return CHOOSING


async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    uid = user.id

    if text == "📐 Mahsulotlar (Katalog)":
        keyboard2 = ReplyKeyboardMarkup([
            [KeyboardButton("Rom bezaklari"), KeyboardButton("Ustunlar")],
            [KeyboardButton("Belbog' karnizlar"), KeyboardButton("Yumaloq ustunlar")],
            [KeyboardButton("Kapitel va baza"), KeyboardButton("Kalvak")],
            [KeyboardButton("Karnizlar"), KeyboardButton("Shohona karnizlar")],
            [KeyboardButton("Barelef gullar"), KeyboardButton("Devorga ramkalar")],
            [KeyboardButton("🌟 Keng qamrovlik yechim")],
            [KeyboardButton("🔙 Bosh menyu")],
        ], resize_keyboard=True)
        await update.message.reply_text(
            "📐 Mahsulotlar katalogi\n\nQaysi bo'limni ko'rmoqchisiz?",
            reply_markup=keyboard2
        )
        return CHOOSING

    if text == "🔙 Bosh menyu":
        keyboard_main = ReplyKeyboardMarkup([
            [KeyboardButton("📐 Mahsulotlar (Katalog)")],
            [KeyboardButton("🧮 Loyiha bo'yicha hisoblash")],
            [KeyboardButton("🏡 Fasad loyihasi tayyorlash")],
            [KeyboardButton("🏗 Bajarilgan loyihalar")],
            [KeyboardButton("🛒 Savatim"), KeyboardButton("🧾 Jami hisob (PDF)")],
            [KeyboardButton("📞 Kontaktlar / Menejer")],
        ], resize_keyboard=True)
        await update.message.reply_text("Bosh menyu:", reply_markup=keyboard_main)
        return CHOOSING

    if text == "🧾 Jami hisob (PDF)":
        if uid in savat and savat[uid]:
            try:
                mijoz_ism = user.first_name + " " + (user.last_name or "")
                pdf_bytes = create_pdf_bytes(mijoz_ism, savat[uid])
                keyboard = [
                    [InlineKeyboardButton("✅ Buyurtma qilish", callback_data="buyurtma_ber")],
                    [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
                ]
                await update.message.reply_document(
                    document=pdf_bytes,
                    filename="PenoDecorPro_hisob.pdf",
                    caption="Sizning buyurtmangiz hisob-kitobi. Ko'rib chiqing:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                logger.error("PDF xato: " + str(e))
                await update.message.reply_text("Xato yuz berdi: " + str(e))
        else:
            await update.message.reply_text("Savat bo'sh. Avval mahsulot tanlang!")
        return CHOOSING

    if text == "📋 Buyurtmalarim":
        if uid in orders and orders[uid]:
            msg = "Sizning buyurtmalaringiz:\n\n"
            for i, o in enumerate(orders[uid], 1):
                msg += str(i) + ". " + o["category"] + " — " + o.get("model", "") + "\n"
                if o.get("jami_narx"):
                    msg += "   Jami: " + format_narx(o["jami_narx"]) + "\n\n"
        else:
            msg = "Hozircha buyurtma yo'q."
        await update.message.reply_text(msg)
        return CHOOSING

    if text == "🛒 Savatim":
        if uid in savat and savat[uid]:
            for i, s in enumerate(savat[uid]):
                # Har mahsulot uchun alohida xabar
                mahsulot = s["category"] + " — " + s.get("model", "")
                if s.get("rom_tur"):
                    mahsulot += " | " + s["rom_tur"]
                if s.get("razmer"):
                    mahsulot += " | " + s["razmer"]
                miqdor = s.get("miqdor_text", "")
                qoplama = s.get("qoplama", "")
                jami = s.get("jami_narx", 0) or 0

                msg = str(i+1) + ". " + mahsulot + "\n"
                msg += "   Miqdor: " + miqdor + "\n"
                msg += "   Qoplama: " + qoplama + "\n"
                if jami:
                    msg += "   Jami: " + format_narx(jami)

                keyboard = [
                    [
                        InlineKeyboardButton("✏️ Miqdorni o'zgartir", callback_data="tahrir_" + str(i)),
                        InlineKeyboardButton("❌ O'chir", callback_data="ochir_" + str(i)),
                    ]
                ]
                await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

            # Umumiy tugmalar
            keyboard = [
                [InlineKeyboardButton("💰 Jami hisobni ko'rish (PDF)", callback_data="hisob_korsatish")],
                [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
            ]
            await update.message.reply_text("━━━━━━━━━━━━━━\nYuqoridagi mahsulotlarni tahrirlash yoki buyurtma berish:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Savat bo'sh. Mahsulot tanlang!")
        return CHOOSING

    if text == "🧮 Loyiha bo'yicha hisoblash":
        context.user_data["category"] = text
        await update.message.reply_text("📐 Loyiha bo'yicha hisoblash\n\nLoyihangiz rasmini yuboring.")
        return LOYIHA_PHOTO

    if text == "🏡 Fasad loyihasi tayyorlash":
        context.user_data["category"] = text
        await update.message.reply_text("🏠 Fasad loyihasi tayyorlash\n\nUyingizning fasad rasmini yuboring va yoqtirgan modellarni yozing.")
        return FASAD_PHOTO

    if text == "📞 Kontaktlar / Menejer":
        await update.message.reply_text(
            "📞 BIZ BILAN BOG'LANING\n\n"
            "📱 Telefon raqamlar:\n"
            "+998 97 999 57 57\n"
            "+998 90 623 22 72\n"
            "+998 97 699 19 19\n\n"
            "📍 Manzil:\n"
            "Andijon shahar, 134-uy\n"
            "Mo'ljal: Yog' zavodi orqa tomoni\n\n"
            "🕐 Ish vaqti:\n"
            "Dushanba — Shanba: 9:00 — 18:00\n\n"
            "📲 Ijtimoiy tarmoqlar:\n"
            "✈️ Telegram: https://t.me/penodecorpro\n"
            "📸 Instagram: https://www.instagram.com/penodecorpro\n"
            "▶️ YouTube: https://www.youtube.com/@Penodecorpro"
        )
        await context.bot.send_location(
            chat_id=update.effective_chat.id,
            latitude=40.765830,
            longitude=72.348286
        )
        return CHOOSING

    if text == "🏗 Bajarilgan loyihalar":
        await update.message.reply_text("🏗️ Bajarilgan loyihalar:\n\nhttps://muzaffar57.github.io/-penodecor-katalog/loyihalar.html")
        return CHOOSING

    if text == "🌟 Keng qamrovlik yechim":
        await update.message.reply_text("🌟 Keng qamrovlik yechim:\n\nhttps://muzaffar57.github.io/-penodecor-katalog/yechim.html")
        return CHOOSING

    if text in KATALOG_LINKS:
        context.user_data["category"] = text
        count = KATALOG_COUNTS.get(text, 16)
        link = KATALOG_LINKS[text]

        # Rom bezaklari uchun tushuntirish
        if text == "Rom bezaklari":
            await update.message.reply_text(
                "🪟 ROM VA ESHIK BEZAKLARI\n\n"
                "Bizda ikki xil razmer mavjud:\n\n"
                "📐 KATTA RAZMER:\n"
                "• Rom karnizi: 17-18 sm\n"
                "• Ikki yondagi nalichnik: 15 sm\n"
                "• Podkolnik: 17 sm\n\n"
                "📏 KICHIK RAZMER:\n"
                "• Rom karnizi: 15 sm\n"
                "• Ikki yondagi nalichnik: 12 sm\n"
                "• Podkolnik: 14-15 sm\n\n"
                "💡 Narx farqi ana shu o'lchamlar tufayli yuzaga keladi — katta razmer ko'proq material talab qiladi.\n\n"
                "Quyida modelni tanlang 👇"
            )
        row = []
        model_buttons = []
        for i in range(1, count + 1):
            row.append(InlineKeyboardButton("MODEL-" + str(i).zfill(2), callback_data="model_" + str(i).zfill(2)))
            if len(row) == 4:
                model_buttons.append(row)
                row = []
        if row:
            model_buttons.append(row)
        model_buttons.append([InlineKeyboardButton("📷 O'z rasmimni yuboraman", callback_data="custom_photo")])
        model_buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_start")])
        await update.message.reply_text(
            text + " katalogi:\n\nKatalogni ko'rish: " + link + "\n\nYoqtirgan modelingizni tanlang:",
            reply_markup=InlineKeyboardMarkup(model_buttons)
        )
        return MODEL_SELECTION

    await update.message.reply_text("Iltimos, menyudan tanlang.")
    return CHOOSING


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    category = context.user_data.get("category", "")

    if query.data.startswith("model_"):
        model = "MODEL-" + query.data.replace("model_", "")
        context.user_data["model"] = model

        if category == "Rom bezaklari":
            keyboard = [
                [InlineKeyboardButton("Katta razmer", callback_data="razmer_Katta_razmer")],
                [InlineKeyboardButton("Kichik razmer", callback_data="razmer_Kichik_razmer")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")],
            ]
            await query.message.reply_text(
                model + " tanlandingiz!\n\nRazmer tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return RAZMER_TANLOV

        if category in ["Karnizlar", "Belbog' karnizlar"]:
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r.replace(" ", "_"))] for r in KARNIZ_RAZMERLAR]
            buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")])
            await query.message.reply_text(model + " tanlandingiz!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(buttons))
            return RAZMER_TANLOV

        if category == "Ustunlar":
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r)] for r in USTUN_RAZMERLAR]
            buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")])
            await query.message.reply_text(model + " tanlandingiz!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(buttons))
            return RAZMER_TANLOV

        # Qoplama so'ralmaydigan bo'limlar
        if category in ["Barelef gullar", "Kalvak", "Shohona karnizlar", "Yumaloq ustunlar", "Kapitel va baza"]:
            context.user_data["qoplama"] = "Yo'q"
            keyboard_aloqa = [
                [InlineKeyboardButton("📞 Boshqa razmer — aloqaga chiqing", url="https://t.me/penodecorprobot")]
            ]
            await query.message.reply_text(
                model + " tanlandingiz!\n\n"
                "ℹ️ Bu mahsulotlar qoplamasiz holatda taqdim etiladi.\n\n"
                "Necha dona kerak?\nFaqat raqam yozing:\nMasalan: 4",
                reply_markup=InlineKeyboardMarkup(keyboard_aloqa)
            )
            return OLCHAM

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")],
        ]
        await query.message.reply_text(
            model + " tanlandingiz!\n\n"
            "🖌 Qoplama tortilsinmi?\n\n"
            "ℹ️ Katalogdagi narxlar qoplama bilan hisoblangan.\n"
            "Qoplama shart bo'lmasa — narx 2 barobar arzonlashadi!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return QOPLAMA

    if query.data.startswith("romtur_"):
        tur = "Rom bezak" if query.data == "romtur_rom" else "Eshik bezak"
        context.user_data["rom_tur"] = tur
        keyboard = [
            [InlineKeyboardButton("Katta razmer", callback_data="razmer_Katta_razmer")],
            [InlineKeyboardButton("Kichik razmer", callback_data="razmer_Kichik_razmer")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")],
        ]
        await query.message.reply_text(tur + " tanlandi!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
        return RAZMER_TANLOV

    if query.data.startswith("razmer_"):
        razmer_raw = query.data.replace("razmer_", "").replace("_", " ")
        # Karniz uchun narx kalitiga o'tkazish
        razmer = KARNIZ_RAZMER_MAP.get(razmer_raw, razmer_raw)
        context.user_data["razmer"] = razmer
        context.user_data["razmer_display"] = razmer_raw  # Ko'rsatish uchun

        if razmer == "25sm dan katta":
            await query.message.reply_text("Katta razmer uchun bizga murojaat qiling:\n\n📞 Telefon orqali yoki admin bilan bog'laning.")
            return CHOOSING

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_model")],
        ]
        await query.message.reply_text(
            "Razmer: " + razmer + "\n\n"
            "🖌 Qoplama tortilsinmi?\n\n"
            "ℹ️ Katalogdagi narxlar qoplama bilan hisoblangan.\n"
            "Qoplama shart bo'lmasa — narx 2 barobar arzonlashadi!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return QOPLAMA

    if query.data in ["qoplama_ha", "qoplama_yoq"]:
        context.user_data["qoplama"] = "Ha" if query.data == "qoplama_ha" else "Yo'q"
        category = context.user_data.get("category", "")
        if category == "Rom bezaklari":
            await query.message.reply_text("Nechta ROM kerak?\n\nFaqat raqam yozing:\nMasalan: 8")
            return ROM_SONI
        elif category in MIQDOR_SHABLONLAR:
            await query.message.reply_text("📐 " + MIQDOR_SHABLONLAR[category])
            return MIQDOR
        else:
            await query.message.reply_text("📐 " + OLCHAM_SHABLONLAR.get(category, "O'lchamlarni kiriting:"))
            return OLCHAM

    if query.data == "custom_photo":
        await query.message.reply_text("Namuna rasmingizni yuboring:")
        return CUSTOM_PHOTO

    if query.data == "buyurtma_ber":
        await query.message.reply_text(
            "Buyurtmani rasmiylashtirish uchun:\n\n"
            "Ismingizni yozing:\nMasalan: Akbar Karimov"
        )
        return KONTAKT_ISM

    if query.data == "hisob_korsatish":
        user = query.from_user
        if uid in savat and savat[uid]:
            try:
                mijoz_ism = user.first_name + " " + (user.last_name or "")
                pdf_bytes = create_pdf_bytes(mijoz_ism, savat[uid])
                await context.bot.send_document(
                    chat_id=uid,
                    document=pdf_bytes,
                    filename="PenoDecorPro_hisob.pdf",
                    caption="Sizning buyurtmangiz hisob-kitobi"
                )
                keyboard = [
                    [InlineKeyboardButton("✅ Buyurtma qilish", callback_data="buyurtma_ber")],
                    [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
                ]
                await context.bot.send_message(
                    chat_id=uid,
                    text="PDF ni korib chiqing va qaror qiling:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                logger.error("PDF xato: " + str(e))
                await query.message.reply_text("Xato: " + str(e))
        return CHOOSING

    if query.data == "orqaga_start":
        # Kategoriya tanlash menyusiga qaytish
        await query.message.reply_text("Bosh menyuga qaytdingiz. Bo'lim tanlang:")
        return CHOOSING

    if query.data == "orqaga_model":
        # Model tanlashga qaytish
        category = context.user_data.get("category", "")
        if category in KATALOG_LINKS:
            count = KATALOG_COUNTS.get(category, 16)
            link = KATALOG_LINKS[category]
            row = []
            model_buttons = []
            for i in range(1, count + 1):
                row.append(InlineKeyboardButton("MODEL-" + str(i).zfill(2), callback_data="model_" + str(i).zfill(2)))
                if len(row) == 4:
                    model_buttons.append(row)
                    row = []
            if row:
                model_buttons.append(row)
            model_buttons.append([InlineKeyboardButton("📷 O'z rasmimni yuboraman", callback_data="custom_photo")])
            model_buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga_start")])
            await query.message.reply_text(
                category + " katalogi:\n\nKatalogni ko'rish: " + link + "\n\nModelni tanlang:",
                reply_markup=InlineKeyboardMarkup(model_buttons)
            )
        return MODEL_SELECTION

    if query.data == "kapitel_ha":
        await query.message.reply_text(
            "Necha dona KAPITEL kerak?\n"
            "Faqat raqam yozing:\nMasalan: 4"
        )
        return KAPITEL_SONI

    if query.data == "kapitel_yoq":
        keyboard = [
            [InlineKeyboardButton("🛒 Savatim", callback_data="savatim_kor")],
            [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
        ]
        await query.message.reply_text("Yaxshi! Davom etamiz.", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING

    if query.data == "yana_qosh":
        category = context.user_data.get("category", "")
        if category in KATALOG_LINKS:
            count = KATALOG_COUNTS.get(category, 16)
            link = KATALOG_LINKS[category]
            row = []
            model_buttons = []
            for i in range(1, count + 1):
                row.append(InlineKeyboardButton("MODEL-" + str(i).zfill(2), callback_data="model_" + str(i).zfill(2)))
                if len(row) == 4:
                    model_buttons.append(row)
                    row = []
            if row:
                model_buttons.append(row)
            model_buttons.append([InlineKeyboardButton("📷 O'z rasmimni yuboraman", callback_data="custom_photo")])
            model_buttons.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="orqaga_start")])
            await query.message.reply_text(
                category + " katalogi:\n\nKatalogni ko'rish: " + link + "\n\nModelni tanlang:",
                reply_markup=InlineKeyboardMarkup(model_buttons)
            )
        else:
            # Bosh menyuni ko'rsat
            await query.message.reply_text(
                "Bo'lim tanlang:\n\n"
                "Pastdagi menyudan kerakli bo'limni bosing 👇"
            )
        return CHOOSING

    if query.data == "savatim_kor":
        if uid in savat and savat[uid]:
            for i, s in enumerate(savat[uid]):
                mahsulot = s["category"] + " — " + s.get("model", "")
                if s.get("rom_tur"):
                    mahsulot += " | " + s["rom_tur"]
                if s.get("razmer"):
                    mahsulot += " | " + s["razmer"]
                miqdor = s.get("miqdor_text", "")
                qoplama = s.get("qoplama", "")

                msg = str(i+1) + ". " + mahsulot + "\n"
                msg += "   Miqdor: " + miqdor + "\n"
                msg += "   Qoplama: " + qoplama

                keyboard = [[
                    InlineKeyboardButton("✏️ O'zgartir", callback_data="tahrir_" + str(i)),
                    InlineKeyboardButton("❌ O'chir", callback_data="ochir_" + str(i)),
                ]]
                await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

            keyboard = [
                [InlineKeyboardButton("💰 Jami hisob (PDF)", callback_data="hisob_korsatish")],
                [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
            ]
            await query.message.reply_text("━━━━━━━━━━━━━━\nJami hisobni ko'rish yoki tahrirlash:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.reply_text("Savat bo'sh!")
        return CHOOSING

    if query.data.startswith("ochir_"):
        idx = int(query.data.replace("ochir_", ""))
        if uid in savat and 0 <= idx < len(savat[uid]):
            olingan = savat[uid].pop(idx)
            mahsulot = olingan["category"] + " — " + olingan.get("model", "")
            await query.message.reply_text("❌ O'chirildi: " + mahsulot)
        return CHOOSING

    if query.data.startswith("tahrir_"):
        idx = int(query.data.replace("tahrir_", ""))
        context.user_data["tahrir_idx"] = idx
        if uid in savat and 0 <= idx < len(savat[uid]):
            item = savat[uid][idx]
            category = item.get("category", "")
            rom_tur = item.get("rom_tur", "")
            if category == "Rom bezaklari" and rom_tur:
                await query.message.reply_text(
                    "Yangi miqdorni kiriting (" + rom_tur + "):\nFaqat raqam yozing:"
                )
            else:
                await query.message.reply_text(
                    "Yangi miqdorni kiriting (metr):\nFaqat raqam yozing:"
                )
        return TAHRIR_MIQDOR

    if query.data == "savat_tozala":
        savat[uid] = []
        await query.message.reply_text("🗑 Savat tozalandi!")
        return CHOOSING

    return CHOOSING


async def kapitel_soni_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    try:
        soni = int(text)
        context.user_data["kapitel_soni"] = soni
        razmer = context.user_data.get("razmer", "25sm")
        narx = KAPITEL_NARXLAR.get(razmer, 14000)
        qoplama = context.user_data.get("qoplama", "Ha")
        if qoplama == "Yo'q":
            narx = narx // 2
        context.user_data["kapitel_narx"] = narx

        if uid not in savat:
            savat[uid] = []
        savat[uid].append({
            "category": "Kapitel",
            "model": "Kapitel",
            "rom_tur": "",
            "qoplama": qoplama,
            "razmer": razmer,
            "miqdor_text": str(soni) + " ta dona",
            "jami_narx": soni * narx,
            "birlik_narx": narx,
        })
        await update.message.reply_text(
            "✅ Kapitel savatga qo'shildi!\n"
            "En: " + razmer + " | " + str(soni) + " ta dona\n\n"
            "Necha dona BAZA kerak?\n"
            "Faqat raqam yozing:\nMasalan: 4"
        )
        return BAZA_SONI
    except:
        await update.message.reply_text("Iltimos, faqat raqam yozing!\nMasalan: 4")
        return KAPITEL_SONI


async def baza_soni_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    try:
        soni = int(text)
        razmer = context.user_data.get("razmer", "25sm")
        narx = BAZA_NARXLAR.get(razmer, 12000)
        qoplama = context.user_data.get("qoplama", "Ha")
        if qoplama == "Yo'q":
            narx = narx // 2

        if uid not in savat:
            savat[uid] = []
        savat[uid].append({
            "category": "Baza",
            "model": "Baza",
            "rom_tur": "",
            "qoplama": qoplama,
            "razmer": razmer,
            "miqdor_text": str(soni) + " ta dona",
            "jami_narx": soni * narx,
            "birlik_narx": narx,
        })

        keyboard = [
            [InlineKeyboardButton("🛒 Savatim", callback_data="savatim_kor")],
            [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
        ]
        await update.message.reply_text(
            "✅ Baza ham savatga qo'shildi!\n"
            "En: " + razmer + " | " + str(soni) + " ta dona",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSING
    except:
        await update.message.reply_text("Iltimos, faqat raqam yozing!\nMasalan: 4")
        return BAZA_SONI


async def tahrir_miqdor_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    idx = context.user_data.get("tahrir_idx", -1)

    if uid not in savat or idx < 0 or idx >= len(savat[uid]):
        await update.message.reply_text("Xato. Qaytadan urinib ko'ring.")
        return CHOOSING

    item = savat[uid][idx]
    category = item.get("category", "")
    model = item.get("model", "")
    qoplama = item.get("qoplama", "Ha")
    razmer = item.get("razmer", "")
    rom_tur = item.get("rom_tur", "")

    try:
        yangi_miqdor = int(text)
        birlik_narx = item.get("birlik_narx", 0) or 0

        if category == "Rom bezaklari" and rom_tur:
            yangi_jami = yangi_miqdor * birlik_narx
            savat[uid][idx]["miqdor_text"] = str(yangi_miqdor) + " ta dona"
            savat[uid][idx]["jami_narx"] = yangi_jami
        else:
            birlik_narx = get_birlik_narx(category, model, razmer, None, qoplama) or 0
            yangi_jami = yangi_miqdor * birlik_narx
            savat[uid][idx]["miqdor_text"] = str(yangi_miqdor) + " metr"
            savat[uid][idx]["jami_narx"] = yangi_jami
            savat[uid][idx]["birlik_narx"] = birlik_narx

        await update.message.reply_text(
            "✅ Yangilandi!\n\n" +
            category + " — " + model + "\n" +
            "Yangi miqdor: " + savat[uid][idx]["miqdor_text"]
        )
    except:
        await update.message.reply_text("Iltimos, faqat raqam yozing!")
        return TAHRIR_MIQDOR

    return CHOOSING


async def rom_soni_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        soni = int(text)
        context.user_data["rom_soni"] = soni
        await update.message.reply_text(
            "Nechta ESHIK kerak?\n\nFaqat raqam yozing:\nMasalan: 4"
        )
        return ESHIK_SONI
    except:
        await update.message.reply_text("Iltimos, faqat raqam yozing!\nMasalan: 8")
        return ROM_SONI


async def eshik_soni_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    try:
        eshik_soni = int(text)
    except:
        await update.message.reply_text("Iltimos, faqat raqam yozing!\nMasalan: 4")
        return ESHIK_SONI

    rom_soni = context.user_data.get("rom_soni", 0)
    category = context.user_data.get("category", "")
    model = context.user_data.get("model", "")
    qoplama = context.user_data.get("qoplama", "Ha")
    razmer = context.user_data.get("razmer", "Katta razmer")
    if not razmer:
        razmer = "Katta razmer"

    logger.info(f"DEBUG eshik: model={model}, razmer={razmer}, qoplama={qoplama}")
    rom_narx = get_birlik_narx(category, model, razmer, "Rom bezak", qoplama) or 0
    eshik_narx = get_birlik_narx(category, model, razmer, "Eshik bezak", qoplama) or 0
    logger.info(f"DEBUG narxlar: rom_narx={rom_narx}, eshik_narx={eshik_narx}")

    if uid not in savat:
        savat[uid] = []

    if rom_soni > 0:
        savat[uid].append({
            "category": "Rom bezaklari", "model": model,
            "rom_tur": "Rom bezak", "qoplama": qoplama, "razmer": razmer,
            "miqdor_text": str(rom_soni) + " ta dona",
            "jami_narx": rom_soni * rom_narx, "birlik_narx": rom_narx,
        })
    if eshik_soni > 0:
        savat[uid].append({
            "category": "Rom bezaklari", "model": model,
            "rom_tur": "Eshik bezak", "qoplama": qoplama, "razmer": razmer,
            "miqdor_text": str(eshik_soni) + " ta dona",
            "jami_narx": eshik_soni * eshik_narx, "birlik_narx": eshik_narx,
        })

    jami = rom_soni * rom_narx + eshik_soni * eshik_narx

    keyboard = [
        [InlineKeyboardButton("🛒 Savatim", callback_data="savatim_kor")],
        [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
    ]

    msg = "✅ Savatga qo'shildi!\n\n"
    msg += "📦 Rom bezaklari — " + model + "\n"
    msg += "📏 Razmer: " + razmer + "\n"
    msg += "🖌 Qoplama: " + qoplama + "\n"
    if rom_soni > 0:
        msg += "🪟 Rom: " + str(rom_soni) + " ta dona\n"
    if eshik_soni > 0:
        msg += "🚪 Eshik: " + str(eshik_soni) + " ta dona"

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING


async def kontakt_ism_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ism = update.message.text.strip()
    context.user_data["kontakt_ism"] = ism
    await update.message.reply_text(
        "Telefon raqamingizni yozing:\nMasalan: +998901234567"
    )
    return KONTAKT_TEL


async def kontakt_tel_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    tel = update.message.text.strip()
    ism = context.user_data.get("kontakt_ism", user.first_name)

    if uid in savat and savat[uid]:
        # Admin ga xabar
        msg = "🆕 YANGI BUYURTMA!\n\n"
        msg += "👤 Ism: " + ism + "\n"
        msg += "📞 Tel: " + tel + "\n"
        msg += "🆔 Telegram ID: " + str(uid) + "\n\n"
        jami = 0
        for i, s in enumerate(savat[uid], 1):
            msg += str(i) + ". " + s["category"] + " — " + s.get("model", "") + "\n"
            if s.get("rom_tur"):
                msg += "   Tur: " + s["rom_tur"] + "\n"
            if s.get("razmer"):
                msg += "   Razmer: " + s["razmer"] + "\n"
            msg += "   Qoplama: " + s.get("qoplama", "") + "\n"
            if s.get("miqdor_text"):
                msg += "   Miqdor: " + s["miqdor_text"] + "\n"
            if s.get("jami_narx"):
                msg += "   Jami: " + format_narx(s["jami_narx"]) + "\n"
                jami += s["jami_narx"]
            msg += "\n"
        if jami:
            msg += "━━━━━━━━━━━━━━\n💰 UMUMIY JAMI: " + format_narx(jami)

        if ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

        # PDF adminga yuborish
        try:
            pdf_bytes = create_pdf_bytes(ism + " | " + tel, savat[uid])
            if ADMIN_ID:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=pdf_bytes,
                    filename="PenoDecorPro_buyurtma.pdf",
                    caption="📄 Yangi buyurtma PDF!\n👤 " + ism + "\n📞 " + tel
                )
        except Exception as e:
            logger.error("PDF xato: " + str(e))

        if uid not in orders:
            orders[uid] = []
        orders[uid].extend(savat[uid])
        savat[uid] = []

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "Tez orada " + tel + " raqamiga qo'ng'iroq qilamiz. Rahmat! 🙏"
    )
    return CHOOSING


async def miqdor_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    text = update.message.text
    category = context.user_data.get("category", "")
    model = context.user_data.get("model", "")
    qoplama = context.user_data.get("qoplama", "Ha")
    razmer = context.user_data.get("razmer", "")

    jami_narx = 0
    miqdor_text = text
    birlik_narx = 0

    try:
        import re
        if uid not in savat:
            savat[uid] = []
        metr_match = re.search(r'(\d+[\.,]?\d*)', text)
        if metr_match:
            miqdor = float(metr_match.group(1).replace(",", "."))
            birlik_narx = get_birlik_narx(category, model, razmer, None, qoplama) or 0
            jami_narx = int(miqdor * birlik_narx)
            if category == "Devorga ramkalar":
                miqdor_text = str(int(miqdor)) + " ta dona"
            else:
                miqdor_text = str(int(miqdor)) + " metr"
            savat[uid].append({
                "category": category, "model": model, "rom_tur": "",
                "qoplama": qoplama, "razmer": razmer,
                "miqdor_text": miqdor_text, "jami_narx": jami_narx, "birlik_narx": birlik_narx,
            })
    except Exception as e:
        logger.error("Miqdor xato: " + str(e))

    keyboard = [
        [InlineKeyboardButton("🛒 Savatim", callback_data="savatim_kor")],
        [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
    ]

    msg = "✅ Savatga qo'shildi!\n\n"
    msg += "📦 " + category + " — " + model + "\n"
    if razmer:
        msg += "📏 Razmer: " + razmer + "\n"
    msg += "🖌 Qoplama: " + qoplama + "\n"
    msg += "📐 Miqdor: " + miqdor_text

    if category == "Ustunlar":
        keyboard2 = [
            [InlineKeyboardButton("✅ Ha, kerak", callback_data="kapitel_ha")],
            [InlineKeyboardButton("❌ Yo'q, kerak emas", callback_data="kapitel_yoq")],
        ]
        await update.message.reply_text(msg)
        await update.message.reply_text(
            "Kapitel va baza ham qo'shish kerakmi?",
            reply_markup=InlineKeyboardMarkup(keyboard2)
        )
        return KAPITEL_SONI

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING


async def olcham_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    olcham = update.message.text
    category = context.user_data.get("category", "Noma'lum")
    model = context.user_data.get("model", "Noma'lum")
    qoplama = context.user_data.get("qoplama", "Yo'q")
    razmer = context.user_data.get("razmer", "")
    rom_tur = context.user_data.get("rom_tur", "")

    item = {"category": category, "model": model, "rom_tur": rom_tur,
            "qoplama": qoplama, "razmer": razmer, "miqdor_text": olcham,
            "jami_narx": None, "birlik_narx": None}

    if uid not in savat:
        savat[uid] = []
    savat[uid].append(item)

    keyboard = [
        [InlineKeyboardButton("🛒 Savatim", callback_data="savatim_kor")],
        [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
    ]

    msg = "✅ Savatga qo'shildi!\n\n📦 " + category + " — " + model + "\n"
    if razmer:
        msg += "📏 Razmer: " + razmer + "\n"
    msg += "🖌 Qoplama: " + qoplama + "\n📐 O'lcham: " + olcham

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING


async def loyiha_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        await update.message.reply_text("✅ Loyihangiz qabul qilindi!\n\nMutaxassislarimiz ko'rib chiqib, tez orada narx yuboramiz. Rahmat! 🙏")
        if ADMIN_ID:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id,
                caption="📐 LOYIHA BO'YICHA HISOBLASH!\n\n👤 " + user.first_name + "\n🆔 " + str(user.id))
        return CHOOSING
    # Rasm emas matn kelsa — menyuga qaytarish
    return await category_chosen(update, context)


async def fasad_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    caption = update.message.caption or ""
    if photo:
        await update.message.reply_text("✅ Fasad rasmingiz qabul qilindi!\n\nDizaynerlarimiz loyiha tayyorlab, tez orada yuboramiz. Rahmat! 🙏")
        if ADMIN_ID:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id,
                caption="🏠 FASAD LOYIHASI!\n\n👤 " + user.first_name + "\n🆔 " + str(user.id) + "\n📝 " + caption)
        return CHOOSING
    # Matn kelsa menyuga qaytarish
    return await category_chosen(update, context)


async def custom_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        context.user_data["model"] = "Mijoz namunasi"
        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await update.message.reply_text("Rasmingiz qabul qilindi!\n\nQoplama tortilsinmi?", reply_markup=InlineKeyboardMarkup(keyboard))
        if ADMIN_ID:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id,
                caption="📷 Yangi namuna!\n👤 " + user.first_name + "\n🆔 " + str(user.id))
        return QOPLAMA
    await update.message.reply_text("Iltimos, rasm yuboring.")
    return CUSTOM_PHOTO


async def send_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Ishlatish: /narx [mijoz_id] [narx va xabar]")
        return
    try:
        client_id = int(args[0])
        price_text = " ".join(args[1:])
        await context.bot.send_message(chat_id=client_id, text="💰 Sizning buyurtmangiz narxi:\n\n" + price_text)
        await update.message.reply_text("✅ Narx mijozga yuborildi!")
    except Exception as e:
        await update.message.reply_text("Xato: " + str(e))


def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen), CallbackQueryHandler(button_handler)],
            MODEL_SELECTION: [CallbackQueryHandler(button_handler), MessageHandler(filters.PHOTO, custom_photo_received)],
            ROM_TUR: [CallbackQueryHandler(button_handler)],
            RAZMER_TANLOV: [CallbackQueryHandler(button_handler)],
            QOPLAMA: [CallbackQueryHandler(button_handler)],
            ROM_SONI: [MessageHandler(filters.TEXT & ~filters.COMMAND, rom_soni_received)],
            ESHIK_SONI: [MessageHandler(filters.TEXT & ~filters.COMMAND, eshik_soni_received)],
            MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, miqdor_received)],
            OLCHAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, olcham_received)],
            LOYIHA_PHOTO: [MessageHandler(filters.PHOTO, loyiha_photo_received)],
            FASAD_PHOTO: [MessageHandler(filters.PHOTO, fasad_photo_received), MessageHandler(filters.TEXT & ~filters.COMMAND, fasad_photo_received)],
            CUSTOM_PHOTO: [MessageHandler(filters.PHOTO, custom_photo_received)],
            KONTAKT_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, kontakt_ism_received)],
            KONTAKT_TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, kontakt_tel_received)],
            TAHRIR_MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, tahrir_miqdor_received)],
            KAPITEL_SONI: [MessageHandler(filters.TEXT & ~filters.COMMAND, kapitel_soni_received), CallbackQueryHandler(button_handler)],
            BAZA_SONI: [MessageHandler(filters.TEXT & ~filters.COMMAND, baza_soni_received)],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen),
        ],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", send_price))
    app.run_polling()


if __name__ == "__main__":
    main()
