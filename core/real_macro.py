import os
from fredapi import Fred

FRED_KEY = os.environ.get("FRED_API_KEY")
fred = Fred(api_key=FRED_KEY) if FRED_KEY else None

class RealMacroBrain:
    @staticmethod
    def get_gdp():
        if not fred:
            return None
        try:
            series = fred.get_series('A191RL1Q225SBEA')
            return round(float(series.iloc[-1]), 2) if not series.empty else None
        except:
            return None

    @staticmethod
    def get_cpi_yoy():
        if not fred:
            return None
        try:
            cpi = fred.get_series('CPIAUCSL')
            if len(cpi) >= 13:
                latest = cpi.iloc[-1]
                year_ago = cpi.iloc[-13]
                return round((latest - year_ago) / year_ago * 100, 2)
        except:
            pass
        return None

    @staticmethod
    def get_unemployment():
        if not fred:
            return None
        try:
            unemp = fred.get_series('UNRATE')
            return round(float(unemp.iloc[-1]), 1) if not unemp.empty else None
        except:
            return None

    @staticmethod
    def get_fed_rate():
        if not fred:
            return None
        try:
            rate = fred.get_series('DFF')
            return round(float(rate.iloc[-1]), 2) if not rate.empty else None
        except:
            return None

    @staticmethod
    def get_regime():
        gdp = RealMacroBrain.get_gdp()
        cpi = RealMacroBrain.get_cpi_yoy()
        unemp = RealMacroBrain.get_unemployment()
        if gdp is None or cpi is None or unemp is None:
            return "Unknown"
        if gdp > 2 and cpi < 3 and unemp < 5:
            return "Risk On 🔥"
        elif gdp < 0:
            return "Risk Off ❄️"
        elif cpi > 4 and gdp < 1:
            return "Stagflation 🐢"
        return "Quiet 😴"
