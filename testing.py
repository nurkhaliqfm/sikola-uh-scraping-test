from datetime import datetime, timezone, timedelta

convertDate = (
    datetime.fromtimestamp(1708963200, timezone.utc) + timedelta(hours=8)
).strftime("%Y-%m-%d")
print(convertDate)
