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
    "MODEL-05": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 110000, "Kichik razmer": 90000}},
    "MODEL-06": {"Rom bezak": {"Katta razmer": 150000, "Kichik razmer": 110000}, "Eshik bezak": {"Katta razmer": 90000, "Kichik razmer": 70000}},
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

        # Logo doira
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

    sana = datetime.now().strftime("%d.%m.%Y %H:%M")
    buyurtma_no = "BDP-" + datetime.now().strftime("%Y%m%d%H%M")
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
}

KATALOG_COUNTS = {
    "Rom bezaklari": 16, "Ustunlar": 13, "Belbog' karnizlar": 27,
    "Yumaloq ustunlar": 12, "Kapitel va baza": 16, "Kalvak": 9,
    "Karnizlar": 26, "Shohona karnizlar": 12, "Barelef gullar": 7,
}

USTUN_RAZMERLAR = ["25sm", "30sm", "35sm", "40sm", "45sm", "50sm"]
KARNIZ_RAZMERLAR = ["Kichik (17sm)", "Ortacha (20sm)", "Katta (25sm)", "25sm dan katta"]

MIQDOR_SHABLONLAR = {
    "Rom bezaklari": "Nechta rom va nechta eshik bor?\n\nRom soni: ___\nEshik soni: ___\n\nMasalan:\nRom soni: 8\nEshik soni: 4",
    "Ustunlar": "Qancha metr kerak?\nMasalan: 12",
    "Belbog' karnizlar": "Qancha metr kerak?\nMasalan: 25",
    "Karnizlar": "Qancha metr kerak?\nMasalan: 30",
}

OLCHAM_SHABLONLAR = {
    "Shohona karnizlar": "Bo'yi necha sm va qancha metr kerak?\nMasalan: Bo'yi 50sm, 20 metr",
    "Yumaloq ustunlar": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 30sm, 4 dona",
    "Kapitel va baza": "Diametri yoki aylanasini va necha dona:\nMasalan: Diametri 40sm, 4 dona",
    "Barelef gullar": "O'lchamlarni kiriting:\nUzunligi: ___\nBo'yi: ___\nSoni: ___",
    "Kalvak": "O'lchamlarni kiriting:\nUzunligi: ___\nEni: ___\nQalinligi: ___\nSoni: ___",
}

CHOOSING, MODEL_SELECTION, QOPLAMA, RAZMER_TANLOV, ROM_TUR, MIQDOR, OLCHAM, LOYIHA_PHOTO, FASAD_PHOTO, CUSTOM_PHOTO = range(10)

orders = {}
savat = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("Rom bezaklari"), KeyboardButton("Ustunlar")],
        [KeyboardButton("Belbog' karnizlar"), KeyboardButton("Yumaloq ustunlar")],
        [KeyboardButton("Kapitel va baza"), KeyboardButton("Kalvak")],
        [KeyboardButton("Karnizlar"), KeyboardButton("Shohona karnizlar")],
        [KeyboardButton("Barelef gullar")],
        [KeyboardButton("📐 Loyiha bo'yicha hisoblash")],
        [KeyboardButton("🏠 Fasad loyihasi tayyorlash")],
        [KeyboardButton("🏗️ Bajarilgan loyihalar")],
        [KeyboardButton("🌟 Keng qamrovlik yechim")],
        [KeyboardButton("🛒 Savatim"), KeyboardButton("📋 Buyurtmalarim")],
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum, " + user.first_name + "!\n\nPenoDecorPro botiga xush kelibsiz!\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=markup
    )
    return CHOOSING


async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    uid = user.id

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
            msg = "🛒 Savatingiz:\n\n"
            for i, s in enumerate(savat[uid], 1):
                msg += str(i) + ". " + s["category"] + " — " + s.get("model", "") + "\n"
                if s.get("rom_tur"):
                    msg += "   Tur: " + s["rom_tur"] + "\n"
                if s.get("razmer"):
                    msg += "   Razmer: " + s["razmer"] + "\n"
                msg += "   Qoplama: " + s.get("qoplama", "") + "\n"
                if s.get("miqdor_text"):
                    msg += "   Miqdor: " + s["miqdor_text"] + "\n"
                msg += "\n"
            msg += "━━━━━━━━━━━━━━\n"
            msg += "💰 Jami hisobni ko'rish uchun tugmani bosing:"
            keyboard = [
                [InlineKeyboardButton("💰 Jami hisobni ko'rish (PDF)", callback_data="hisob_korsatish")],
                [InlineKeyboardButton("🗑 Savatni tozalash", callback_data="savat_tozala")],
            ]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Savat bo'sh. Mahsulot tanlang!")
        return CHOOSING

    if text == "📐 Loyiha bo'yicha hisoblash":
        context.user_data["category"] = text
        await update.message.reply_text("📐 Loyiha bo'yicha hisoblash\n\nLoyihangiz rasmini yuboring.")
        return LOYIHA_PHOTO

    if text == "🏠 Fasad loyihasi tayyorlash":
        context.user_data["category"] = text
        await update.message.reply_text("🏠 Fasad loyihasi tayyorlash\n\nUyingizning fasad rasmini yuboring va yoqtirgan modellarni yozing.")
        return FASAD_PHOTO

    if text == "🏗️ Bajarilgan loyihalar":
        await update.message.reply_text("🏗️ Bajarilgan loyihalar:\n\nhttps://muzaffar57.github.io/-penodecor-katalog/loyihalar.html")
        return CHOOSING

    if text == "🌟 Keng qamrovlik yechim":
        await update.message.reply_text("🌟 Keng qamrovlik yechim:\n\nhttps://muzaffar57.github.io/-penodecor-katalog/yechim.html")
        return CHOOSING

    if text in KATALOG_LINKS:
        context.user_data["category"] = text
        count = KATALOG_COUNTS.get(text, 16)
        link = KATALOG_LINKS[text]
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
                [InlineKeyboardButton("🪟 Rom bezak", callback_data="romtur_rom")],
                [InlineKeyboardButton("🚪 Eshik bezak", callback_data="romtur_eshik")],
            ]
            await query.message.reply_text(model + " tanlandingiz!\n\nQaysi tur kerak?", reply_markup=InlineKeyboardMarkup(keyboard))
            return ROM_TUR

        if category in ["Karnizlar", "Belbog' karnizlar"]:
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r.replace(" ", "_").replace("(", "").replace(")", ""))] for r in KARNIZ_RAZMERLAR]
            await query.message.reply_text(model + " tanlandingiz!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(buttons))
            return RAZMER_TANLOV

        if category == "Ustunlar":
            buttons = [[InlineKeyboardButton(r, callback_data="razmer_" + r)] for r in USTUN_RAZMERLAR]
            await query.message.reply_text(model + " tanlandingiz!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(buttons))
            return RAZMER_TANLOV

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await query.message.reply_text(model + " tanlandingiz!\n\nQoplama tortilsinmi?", reply_markup=InlineKeyboardMarkup(keyboard))
        return QOPLAMA

    if query.data.startswith("romtur_"):
        tur = "Rom bezak" if query.data == "romtur_rom" else "Eshik bezak"
        context.user_data["rom_tur"] = tur
        keyboard = [
            [InlineKeyboardButton("Katta razmer", callback_data="razmer_Katta_razmer")],
            [InlineKeyboardButton("Kichik razmer", callback_data="razmer_Kichik_razmer")],
        ]
        await query.message.reply_text(tur + " tanlandi!\n\nRazmer tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
        return RAZMER_TANLOV

    if query.data.startswith("razmer_"):
        razmer_raw = query.data.replace("razmer_", "")
        if razmer_raw in USTUN_RAZMERLAR:
            razmer = razmer_raw
        elif "Katta_razmer" in razmer_raw:
            razmer = "Katta razmer"
        elif "Kichik_razmer" in razmer_raw:
            razmer = "Kichik razmer"
        elif "Kichik_17sm" in razmer_raw:
            razmer = "Kichik (17sm)"
        elif "Ortacha_20sm" in razmer_raw:
            razmer = "Ortacha (20sm)"
        elif "Katta_25sm" in razmer_raw:
            razmer = "Katta (25sm)"
        elif "25sm_dan_katta" in razmer_raw:
            razmer = "25sm dan katta"
        else:
            razmer = razmer_raw.replace("_", " ")
        context.user_data["razmer"] = razmer

        if razmer == "25sm dan katta":
            await query.message.reply_text("Katta razmer uchun bizga murojaat qiling:\n\n📞 Telefon orqali yoki admin bilan bog'laning.")
            return CHOOSING

        keyboard = [
            [InlineKeyboardButton("✅ Ha, qoplama bilan", callback_data="qoplama_ha")],
            [InlineKeyboardButton("❌ Yo'q, qoplama siz", callback_data="qoplama_yoq")],
        ]
        await query.message.reply_text("Razmer: " + razmer + "\n\nQoplama tortilsinmi?", reply_markup=InlineKeyboardMarkup(keyboard))
        return QOPLAMA

    if query.data in ["qoplama_ha", "qoplama_yoq"]:
        context.user_data["qoplama"] = "Ha" if query.data == "qoplama_ha" else "Yo'q"
        category = context.user_data.get("category", "")
        if category in MIQDOR_SHABLONLAR:
            await query.message.reply_text("📐 " + MIQDOR_SHABLONLAR[category])
            return MIQDOR
        else:
            await query.message.reply_text("📐 " + OLCHAM_SHABLONLAR.get(category, "O'lchamlarni kiriting:"))
            return OLCHAM

    if query.data == "custom_photo":
        await query.message.reply_text("Namuna rasmingizni yuboring:")
        return CUSTOM_PHOTO

    if query.data == "buyurtma_ber":
        user = query.from_user
        if uid in savat and savat[uid]:
            # Admin ga matn
            msg = "🆕 YANGI BUYURTMA!\n\n"
            msg += "👤 Mijoz: " + user.first_name + " " + (user.last_name or "") + "\n"
            msg += "🆔 ID: " + str(uid) + "\n\n"
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

            # PDF yaratish va adminga yuborish
            try:
                mijoz_ism = user.first_name + " " + (user.last_name or "")
                pdf_bytes = create_pdf_bytes(mijoz_ism, savat[uid])
                if ADMIN_ID:
                    await context.bot.send_document(
                        chat_id=ADMIN_ID,
                        document=pdf_bytes,
                        filename="PenoDecorPro_buyurtma.pdf",
                        caption="📄 Yangi buyurtma PDF!"
                    )
            except Exception as e:
                logger.error("PDF xato: " + str(e))

            await context.bot.send_message(
                chat_id=uid,
                text="✅ Buyurtmangiz qabul qilindi!\n\nTez orada siz bilan bog'lanamiz. Rahmat! 🙏"
            )

            if uid not in orders:
                orders[uid] = []
            orders[uid].extend(savat[uid])
            savat[uid] = []
        return CHOOSING

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

    if query.data == "savat_tozala":
        savat[uid] = []
        await query.message.reply_text("🗑 Savat tozalandi!")
        return CHOOSING

    return CHOOSING


async def miqdor_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    text = update.message.text
    category = context.user_data.get("category", "")
    model = context.user_data.get("model", "")
    qoplama = context.user_data.get("qoplama", "Ha")
    razmer = context.user_data.get("razmer", "")
    rom_tur = context.user_data.get("rom_tur", "")

    jami_narx = 0
    miqdor_text = text
    birlik_narx = 0

    try:
        import re
        if category == "Rom bezaklari":
            rom_soni = 0
            eshik_soni = 0
            rom_match = re.search(r'[Rr]om\s*[Ss]oni\s*[:\-]?\s*(\d+)', text)
            eshik_match = re.search(r'[Ee]shik\s*[Ss]oni\s*[:\-]?\s*(\d+)', text)
            if rom_match:
                rom_soni = int(rom_match.group(1))
            if eshik_match:
                eshik_soni = int(eshik_match.group(1))

            rom_narx = get_birlik_narx(category, model, razmer, "Rom bezak", qoplama) or 0
            eshik_narx = get_birlik_narx(category, model, razmer, "Eshik bezak", qoplama) or 0
            jami_narx = rom_soni * rom_narx + eshik_soni * eshik_narx
            miqdor_text = str(rom_soni) + " ta rom, " + str(eshik_soni) + " ta eshik"
            birlik_narx = rom_narx

        elif category in ["Ustunlar", "Karnizlar", "Belbog' karnizlar"]:
            metr_match = re.search(r'(\d+[\.,]?\d*)', text)
            if metr_match:
                metr = float(metr_match.group(1).replace(",", "."))
                birlik_narx = get_birlik_narx(category, model, razmer, None, qoplama) or 0
                jami_narx = int(metr * birlik_narx)
                miqdor_text = str(metr) + " metr"
    except Exception as e:
        logger.error("Miqdor xato: " + str(e))

    item = {
        "category": category, "model": model, "rom_tur": rom_tur,
        "qoplama": qoplama, "razmer": razmer,
        "miqdor_text": miqdor_text, "jami_narx": jami_narx, "birlik_narx": birlik_narx,
    }

    if uid not in savat:
        savat[uid] = []
    savat[uid].append(item)

    keyboard = [
        [InlineKeyboardButton("🛒 Savatni ko'rish va buyurtma berish", callback_data="buyurtma_ber")],
        [InlineKeyboardButton("➕ Yana mahsulot qo'shish", callback_data="yana_qosh")],
    ]

    msg = "✅ Savatga qo'shildi!\n\n"
    msg += "📦 " + category + " — " + model + "\n"
    if razmer:
        msg += "📏 Razmer: " + razmer + "\n"
    msg += "🖌 Qoplama: " + qoplama + "\n"
    msg += "📐 Miqdor: " + miqdor_text

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
        [InlineKeyboardButton("🛒 Savatni ko'rish va buyurtma berish", callback_data="buyurtma_ber")],
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
    await update.message.reply_text("Iltimos, rasm yuboring.")
    return LOYIHA_PHOTO


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
    await update.message.reply_text("Iltimos, fasad rasmini yuboring.")
    return FASAD_PHOTO


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
            MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, miqdor_received)],
            OLCHAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, olcham_received)],
            LOYIHA_PHOTO: [MessageHandler(filters.PHOTO, loyiha_photo_received)],
            FASAD_PHOTO: [MessageHandler(filters.PHOTO, fasad_photo_received), MessageHandler(filters.TEXT & ~filters.COMMAND, fasad_photo_received)],
            CUSTOM_PHOTO: [MessageHandler(filters.PHOTO, custom_photo_received)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("narx", send_price))
    app.run_polling()


if __name__ == "__main__":
    main()
