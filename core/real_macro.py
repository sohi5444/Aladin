import fred
import os

FRED_KEY = os.environ.get("FRED_API_KEY")
if FRED_KEY:
    fred.key(FRED_KEY)

class RealMacroBrain:
    @staticmethod
    def get_gdp():
        if not FRED_KEY:
            return None
        try:
            data = fred.observations('A191RL1Q225SBEA', limit=1, sort='desc')
            return round(float(data[0]['value']), 2) if data else None
        except:
            return None

    @staticmethod
    def get_cpi_yoy():
        if not FRED_KEY:
            return None
        try:
            cpi = fred.observations('CPIAUCSL', limit=13, sort='desc')
            if len(cpi) >= 13:
                latest = float(cpi[0]['value'])
                year_ago = float(cpi[12]['value'])
                return round((latest - year_ago) / year_ago * 100, 2)
        except:
            pass
        return None

    @staticmethod
    def get_unemployment():
        if not FRED_KEY:
            return None
        try:
            data = fred.observations('UNRATE', limit=1, sort='desc')
            return round(float(data[0]['value']), 1) if data else None
        except:
            return None

    @staticmethod
    def get_fed_rate():
        if not FRED_KEY:
            return None
        try:
            data = fred.observations('DFF', limit=1, sort='desc')
            return round(float(data[0]['value']), 2) if data else None
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
