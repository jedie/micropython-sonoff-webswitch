"""
    dev script just for generate html for copy&paste ;)
"""

weekday_names = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

for no, day in enumerate(weekday_names):
    print(
        f'<input type="checkbox" id="d{no}" name="d{no}" {{d{no}}}>'
        f'<label for="d{no}">{day}</label>'
    )
