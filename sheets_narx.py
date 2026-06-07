import requests
import csv
import io
import time
import logging

logger = logging.getLogger(__name__)

SHEET_ID = "1SlD45_qUPoQKpgXnZfyNuGh8BuAeegvs2TPjXkFwxjA"

# Zaxira narxlar
ZAXIRA_NARXLAR = {
    "Karniz_01_17sm": 38000, "Karniz_01_20sm": 48000, "Karniz_01_25sm": 70000,
    "Karniz_02_17sm": 22000, "Karniz_02_20sm": 32000, "Karniz_02_25sm": 45000,
    "Karniz_03_17sm": 32000, "Karniz_03_20sm": 42000, "Karniz_03_25sm": 55000,
    "Karniz_04_17sm": 30000, "Karniz_04_20sm": 42000, "Karniz_04_25sm": 60000,
    "Karniz_05_17sm": 20000, "Karniz_05_20sm": 25000, "Karniz_05_25sm": 42000,
    "Karniz_06_17sm": 19000, "Karniz_06_20sm": 25000, "Karniz_06_25sm": 34000,
    "Karniz_07_17sm": 16000, "Karniz_07_20sm": 20000, "Karniz_07_25sm": 28000,
    "Karniz_08_17sm": 26000, "Karniz_08_20sm": 34000, "Karniz_08_25sm": 50000,
    "Karniz_09_17sm": 19000, "Karniz_09_20sm": 26000, "Karniz_09_25sm": 40000,
    "Karniz_10_17sm": 17000, "Karniz_10_20sm": 24000, "Karniz_10_25sm": 36000,
    "Karniz_11_17sm": 22000, "Karniz_11_20sm": 30000, "Karniz_11_25sm": 44000,
    "Karniz_12_17sm": 17000, "Karniz_12_20sm": 28000, "Karniz_12_25sm": 44000,
    "Karniz_13_17sm": 21000, "Karniz_13_20sm": 28000, "Karniz_13_25sm": 45000,
    "Karniz_14_17sm": 18000, "Karniz_14_20sm": 25000, "Karniz_14_25sm": 36000,
    "Karniz_15_17sm": 20000, "Karniz_15_20sm": 28000, "Karniz_15_25sm": 45000,
    "Karniz_16_17sm": 14000, "Karniz_16_20sm": 18000, "Karniz_16_25sm": 25000,
    "Karniz_17_17sm": 25000, "Karniz_17_20sm": 44000, "Karniz_17_25sm": 55000,
    "Karniz_18_17sm": 27000, "Karniz_18_20sm": 36000, "Karniz_18_25sm": 55000,
    "Karniz_19_17sm": 33000, "Karniz_19_20sm": 42000, "Karniz_19_25sm": 65000,
    "Karniz_20_17sm": 30000, "Karniz_20_20sm": 42000, "Karniz_20_25sm": 65000,
    "Karniz_21_17sm": 32000, "Karniz_21_20sm": 44000, "Karniz_21_25sm": 66000,
    "Karniz_22_17sm": 14000, "Karniz_22_20sm": 18000, "Karniz_22_25sm": 24000,
    "Karniz_23_17sm": 23000, "Karniz_23_20sm": 37000, "Karniz_23_25sm": 50000,
    "Karniz_24_17sm": 16000, "Karniz_24_20sm": 20000, "Karniz_24_25sm": 30000,
    "Karniz_25_17sm": 20000, "Karniz_25_20sm": 30000, "Karniz_25_25sm": 43000,
    "Karniz_26_17sm": 32000, "Karniz_26_20sm": 40000, "Karniz_26_25sm": 62000,
    "Belbog_01_17sm": 22000, "Belbog_01_20sm": 30000, "Belbog_01_25sm": 46000,
    "Belbog_02_17sm": 18000, "Belbog_02_20sm": 26000, "Belbog_02_25sm": 42000,
    "Belbog_03_17sm": 14000, "Belbog_03_20sm": 20000, "Belbog_03_25sm": 30000,
    "Belbog_04_17sm": 14000, "Belbog_04_20sm": 20000, "Belbog_04_25sm": 30000,
    "Belbog_05_17sm": 14000, "Belbog_05_20sm": 20000, "Belbog_05_25sm": 30000,
    "Belbog_06_17sm": 14000, "Belbog_06_20sm": 20000, "Belbog_06_25sm": 30000,
    "Belbog_07_17sm": 14000, "Belbog_07_20sm": 20000, "Belbog_07_25sm": 30000,
    "Belbog_08_17sm": 17000, "Belbog_08_20sm": 22000, "Belbog_08_25sm": 30000,
    "Belbog_09_17sm": 14000, "Belbog_09_20sm": 20000, "Belbog_09_25sm": 30000,
    "Belbog_10_17sm": 14000, "Belbog_10_20sm": 20000, "Belbog_10_25sm": 30000,
    "Belbog_11_17sm": 17000, "Belbog_11_20sm": 20000, "Belbog_11_25sm": 35000,
    "Belbog_12_17sm": 14000, "Belbog_12_20sm": 20000, "Belbog_12_25sm": 30000,
    "Belbog_13_17sm": 15000, "Belbog_13_20sm": 21000, "Belbog_13_25sm": 31000,
    "Belbog_14_17sm": 18000, "Belbog_14_20sm": 24000, "Belbog_14_25sm": 30000,
    "Belbog_15_17sm": 19000, "Belbog_15_20sm": 27000, "Belbog_15_25sm": 40000,
    "Belbog_16_17sm": 14000, "Belbog_16_20sm": 20000, "Belbog_16_25sm": 30000,
    "Belbog_17_17sm": 14000, "Belbog_17_20sm": 21000, "Belbog_17_25sm": 33000,
    "Belbog_18_17sm": 14000, "Belbog_18_20sm": 20000, "Belbog_18_25sm": 30000,
    "Belbog_19_17sm": 14000, "Belbog_19_20sm": 18000, "Belbog_19_25sm": 20000,
    "Belbog_20_17sm": 15000, "Belbog_20_20sm": 21000, "Belbog_20_25sm": 32000,
    "Belbog_21_17sm": 16000, "Belbog_21_20sm": 22000, "Belbog_21_25sm": 32000,
    "Belbog_22_17sm": 20000, "Belbog_22_20sm": 27000, "Belbog_22_25sm": 42000,
    "Belbog_23_17sm": 21000, "Belbog_23_20sm": 28000, "Belbog_23_25sm": 42000,
    "Belbog_24_17sm": 14000, "Belbog_24_20sm": 20000, "Belbog_24_25sm": 28000,
    "Belbog_25_17sm": 14000, "Belbog_25_20sm": 18000, "Belbog_25_25sm": 29000,
    "Belbog_26_17sm": 14000, "Belbog_26_20sm": 19000, "Belbog_26_25sm": 29000,
    "Belbog_27_17sm": 16000, "Belbog_27_20sm": 22000, "Belbog_27_25sm": 32500,
    "Belbog_28_17sm": 13000, "Belbog_28_20sm": 20000, "Belbog_28_25sm": 30000,
    "Ustun_25sm": 18000, "Ustun_30sm": 21000, "Ustun_35sm": 24000,
    "Ustun_40sm": 28000, "Ustun_45sm": 32000, "Ustun_50sm": 36000,
    "Rom_01_Rom_katta": 140000, "Rom_01_Rom_kichik": 110000, "Rom_01_Eshik_katta": 110000, "Rom_01_Eshik_kichik": 85000,
    "Rom_02_Rom_katta": 110000, "Rom_02_Rom_kichik": 80000, "Rom_02_Eshik_katta": 80000, "Rom_02_Eshik_kichik": 60000,
    "Rom_03_Rom_katta": 120000, "Rom_03_Rom_kichik": 96000, "Rom_03_Eshik_katta": 90000, "Rom_03_Eshik_kichik": 70000,
    "Rom_04_Rom_katta": 150000, "Rom_04_Rom_kichik": 120000, "Rom_04_Eshik_katta": 110000, "Rom_04_Eshik_kichik": 90000,
    "Rom_05_Rom_katta": 150000, "Rom_05_Rom_kichik": 110000, "Rom_05_Eshik_katta": 140000, "Rom_05_Eshik_kichik": 100000,
    "Rom_06_Rom_katta": 150000, "Rom_06_Rom_kichik": 110000, "Rom_06_Eshik_katta": 140000, "Rom_06_Eshik_kichik": 100000,
    "Rom_07_Rom_katta": 120000, "Rom_07_Rom_kichik": 100000, "Rom_07_Eshik_katta": 90000, "Rom_07_Eshik_kichik": 70000,
    "Rom_08_Rom_katta": 140000, "Rom_08_Rom_kichik": 105000, "Rom_08_Eshik_katta": 110000, "Rom_08_Eshik_kichik": 90000,
    "Rom_09_Rom_katta": 140000, "Rom_09_Rom_kichik": 110000, "Rom_09_Eshik_katta": 110000, "Rom_09_Eshik_kichik": 90000,
    "Rom_10_Rom_katta": 150000, "Rom_10_Rom_kichik": 120000, "Rom_10_Eshik_katta": 120000, "Rom_10_Eshik_kichik": 100000,
    "Rom_11_Rom_katta": 140000, "Rom_11_Rom_kichik": 110000, "Rom_11_Eshik_katta": 85000, "Rom_11_Eshik_kichik": 70000,
    "Rom_12_Rom_katta": 160000, "Rom_12_Rom_kichik": 130000, "Rom_12_Eshik_katta": 120000, "Rom_12_Eshik_kichik": 100000,
    "Rom_13_Rom_katta": 160000, "Rom_13_Rom_kichik": 130000, "Rom_13_Eshik_katta": 120000, "Rom_13_Eshik_kichik": 100000,
    "Rom_14_Rom_katta": 160000, "Rom_14_Rom_kichik": 130000, "Rom_14_Eshik_katta": 120000, "Rom_14_Eshik_kichik": 100000,
    "Rom_15_Rom_katta": 150000, "Rom_15_Rom_kichik": 120000, "Rom_15_Eshik_katta": 120000, "Rom_15_Eshik_kichik": 100000,
    "Rom_16_Rom_katta": 130000, "Rom_16_Rom_kichik": 100000, "Rom_16_Eshik_katta": 100000, "Rom_16_Eshik_kichik": 80000,
    "Ramka_01": 180000, "Ramka_02": 250000, "Ramka_03": 240000, "Ramka_04": 190000,
    "Ramka_05": 290000, "Ramka_06": 220000, "Ramka_07": 250000,
    "Kapitel_25sm": 14000, "Kapitel_30sm": 16000, "Kapitel_35sm": 18000,
    "Kapitel_40sm": 20000, "Kapitel_45sm": 22000, "Kapitel_50sm": 24000,
    "Baza_25sm": 12000, "Baza_30sm": 14000, "Baza_35sm": 16000,
    "Baza_40sm": 18000, "Baza_45sm": 20000, "Baza_50sm": 22000,
    # Nostandart mahsulotlar
    "Yumaloq ustun baza": 75000,
    "Yumaloq ustun ustama": 23000,
    "Yumaloq ustun oq baza": 53000,
    "Yumaloq ustun oq ustama": 3200,
    "Kapitel_25sm": 14000, "Kapitel_30sm": 16000, "Kapitel_35sm": 18000,
    "Kapitel_40sm": 20000, "Kapitel_45sm": 22000, "Kapitel_50sm": 24000,
    "Baza_25sm": 12000, "Baza_30sm": 14000, "Baza_35sm": 16000,
    "Baza_40sm": 18000, "Baza_45sm": 20000, "Baza_50sm": 22000,
    "Kapitel_30sm_oq": 70000,
    "Kapitel_30sm_qoplama": 100000,
    "Baza_30sm_oq": 50000,
    "Baza_30sm_qoplama": 80000,
    "Kapitel baza": 80000,
    "Kapitel ustama": 4000,
    "Ustun_25sm_baza": 16500, "Ustun_25sm_ustama": 2700,
    "Ustun_30sm_baza": 19800, "Ustun_30sm_ustama": 3300,
    "Ustun_35sm_baza": 23000, "Ustun_35sm_ustama": 3900,
    "Ustun_40sm_baza": 26500, "Ustun_40sm_ustama": 4300,
    "Ustun_45sm_baza": 29800, "Ustun_45sm_ustama": 4800,
    "Ustun_50sm_baza": 33000, "Ustun_50sm_ustama": 5500,
    "Ustun qalinlik ustamasi": 6000,
    # Rom narx foiz (100 = o'zgarishsiz, 80 = 20% arzon)
    "Rom_narx_foiz": 100,
    # Rom bezaklari narxlar zaxirasi
    "Rom_Ekonom_Katta_metr": 30000, "Rom_Ekonom_Katta_dona": 35000,
    "Rom_Ekonom_Kichik_metr": 22000, "Rom_Ekonom_Kichik_dona": 25000,
    "Rom_Standart_Katta_metr": 40000, "Rom_Standart_Katta_dona": 45000,
    "Rom_Standart_Kichik_metr": 30000, "Rom_Standart_Kichik_dona": 35000,
    "Rom_Premium_Katta_metr": 55000, "Rom_Premium_Katta_dona": 60000,
    "Rom_Premium_Kichik_metr": 42000, "Rom_Premium_Kichik_dona": 48000,
    "Xomashyo_kuba_baza": 1200000,
    "Kalvak kub metr baza": 4000000,
    "Barelyef_standart_baza": 350000,
    "Barelyef kub metr baza": 5000000,
}

_kesh = {"narxlar": None, "vaqt": 0, "muddat": 300}


def sheets_dan_narx_ol():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        content = response.content.decode("utf-8")
        narxlar = {}
        reader = csv.reader(io.StringIO(content))
        next(reader)
        for row in reader:
            if len(row) >= 2:
                kalit = row[0].strip()
                narx_str = row[1].strip().replace(" ", "").replace(",", "")
                if kalit and narx_str.isdigit():
                    narxlar[kalit] = int(narx_str)
        if narxlar:
            logger.info(f"Sheets dan {len(narxlar)} ta narx olindi")
            return narxlar
        return ZAXIRA_NARXLAR
    except Exception as e:
        logger.error(f"Sheets xatosi: {e}, zaxira narxlar ishlatiladi")
        return ZAXIRA_NARXLAR


def chegirma_ol() -> int:
    """Sheets dan chegirma foizini oladi (0-100)."""
    hozir = time.time()
    if _kesh["narxlar"] is None or (hozir - _kesh["vaqt"]) > _kesh["muddat"]:
        _kesh["narxlar"] = sheets_dan_narx_ol()
        _kesh["vaqt"] = hozir
    return _kesh["narxlar"].get("Chegirma_foiz", 0)


def narx_ol(kalit: str) -> int:
    hozir = time.time()
    if _kesh["narxlar"] is None or (hozir - _kesh["vaqt"]) > _kesh["muddat"]:
        _kesh["narxlar"] = sheets_dan_narx_ol()
        _kesh["vaqt"] = hozir
    return _kesh["narxlar"].get(kalit, 0)


def narxlarni_yangilash():
    _kesh["narxlar"] = sheets_dan_narx_ol()
    _kesh["vaqt"] = time.time()
    return len(_kesh["narxlar"])
