
import datetime

def get_time(relative_time: str):
    
    if (relative_time == "Vài giây trước"):
        datetime.datetime.now()

    relative_time = relative_time.replace("Một", "1")
    amount, unit, _ = relative_time.split()
    amount = int(amount)
    unit = unit.strip().lower()
    switcher = {
        "giây": datetime.timedelta(seconds=amount),
        "phút": datetime.timedelta(minutes=amount),
        "giờ": datetime.timedelta(hours=amount),
        "ngày": datetime.timedelta(days=amount),
        "tuần": datetime.timedelta(weeks=amount),
        "tháng": datetime.timedelta(days=30 * amount),
        "năm": datetime.timedelta(days=365 * amount)
    }
    

    return datetime.datetime.now() - switcher.get(unit)



