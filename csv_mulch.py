from csv import DictReader, DictWriter
from datetime import datetime, timedelta

AL_CONST = 143


def dates_between(date1, date2, include_end=True):
    """Return all dates between date1 and date2. Written with a for loop to make readable.
    Examples:

    >>> dates_between(datetime(year=2020, month=1, day=1), datetime(year=2021, month=1, day=1))
    [datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 2, 0, 0), ..., datetime(2020, 12, 31, 0, 0), datetime(2021, 1, 1, 0, 0)]
    >>> dates_between(datetime(year=2020, month=1, day=1), datetime(year=2021, month=1, day=1), include_end=False)
    [datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 2, 0, 0), ..., datetime(2020, 12, 31, 0, 0)] # NOTE: Does not include first of 2021
    """
    delta = date2 - date1
    dates = []
    days = delta.days + 1 if include_end else delta.days
    for i in range(days):
        date = date1 + timedelta(days=i)
        dates.append(date)
    return dates


def read_date(date_string):
    """Read in a date as a string and return that date.
    NOTE: If you give this function '*' or '-' it will just return '*' or '-'

    Examples:
    >>> read_date('20/01/2020')
    datetime(2020, 1, 1, 0, 0)
    >>> read_date('20/01/2020?')
    datetime(2020, 1, 1, 0, 0)
    >>> read_date('*')
    '*'
    """
    actual_date = date_string
    if not date_string:
        return "-"
    if date_string in {"*", "-"}:
        return date_string
    if actual_date[-1] == "?":
        actual_date = date_string[:-1]

    try:
        dt = datetime.strptime(actual_date, "%Y %b %d")
    except ValueError:
        dt = datetime.strptime(actual_date, "%Y %b")
    return dt


def read_csv(csv_filename):
    """Read in the CSV file from a given filename.

    The output is a list of dictionaries that look like this:

    {'Sat ID': 'Tintin A', 'SSN': 'S43216', 'Status': 'R', 'Launch Date': datetime.datetime(2018, 2, 22, 0, 0), 'Fail Date': datetime.datetime(2020, 8, 29, 0, 0), 'Reentry Date': datetime.datetime(2020, 8, 29, 0, 0)}

    If you've forgotten how dictionaries work, try looking at the either the Python doc entry on dictionaries (https://docs.python.org/3/tutorial/datastructures.html#dictionaries),
    or you could refer to your COSC121 notes (or ask me for a refresher if you have more pointed questions).

    Examples:
    >>> read_csv('bigdata.csv')
    # Output will be a really long list of all the launches
    """
    launches = []
    with open(csv_filename, "r") as f:
        reader = DictReader(f)
        for row in reader:
            row["Launch Date"] = read_date(row["Launch Date"])
            row["Fail Date"] = read_date(row["Fail Date"])
            row["Reentry Date"] = read_date(row["Reentry Date"])
            launches.append(row)
    return launches


def increment_month(cur_date):
    """Given a date (first of the month), return the date one month after (first of the next month).

    Examples:
    >>> increment_month(datetime(year=2022, month=1, day=1))
    datetime(year=2022, month=2, day=1)
    >>> increment_month(datetime(year=2018, month=12, day=1))
    datetime(year=2019, month=1, day=1)
    """
    month = cur_date.month
    if cur_date.month == 12:
        return cur_date.replace(year=cur_date.year + 1, month=1)
    return cur_date.replace(year=cur_date.year, month=month + 1)


def reentry_date(launch):
    """Return the reentry date of a launch, if the launch has not yet reentered the atmosphere, return the current date."""
    if launch["Reentry Date"] == "-":
        return datetime.now()
    return launch["Reentry Date"]


# Sort the launches by the date of reentry
launches = sorted(read_csv("output.csv"), key=reentry_date)

# The basic approach is to run through each launch in the order they reenter the atmosphere, starting with the first launch that reenters the atmosphere.
# We keep a running total for each month "cur_month_total", and add to that whilst the month stays the same.
# When the month changes, we add the current month total to the monthly totals and move forward one month.


# Set the start date to the first month something reenters the atmosphere, and set the day to the first of the month.
cur_date = reentry_date(launches[0]).replace(day=1)
# This array contains all the monthly totals
monthly_totals = []
cur_month_total = 0
for launch in launches:
    # If we've reached the sattelites that are no longer in orbit, we can just stop. "break" leaves the loop.
    if launch["Reentry Date"] == "-":
        break
    # This checks if the current reentry date of the current launch is after the end of the current month.
    while reentry_date(launch) >= increment_month(cur_date):
        # Add this months total to the monthly totals and then add one to the month
        monthly_totals.append(
            {
                "Month": cur_date.strftime("%d/%m/%Y"),
                "Reentered": cur_month_total,
                "Al": cur_month_total * AL_CONST,
            }
        )
        cur_date = increment_month(cur_date)
        # Need to reset the current total so each month only tallies launches in the current month
        cur_month_total = 0

    # Add the current month's launch to the current total
    cur_month_total += 1


# This code just writes the outputs to a file, it's the same as before essentially.
with open("monthly.csv", "w") as f:
    writer = DictWriter(f, fieldnames=["Month", "Reentered", "Al"])
    writer.writeheader()
    writer.writerows(monthly_totals)


# Old code

# sd=datetime(year=2018, month=2, day=22)
# ed=datetime(year=2022, month=3, day=15)
# dates=dates_between(sd, ed)
# rows = [{'Date': date.strftime('%d/%m/%Y'), 'In Orbit': 0, 'Al': 0, 'Reentered': 0} for date in dates]

# for launch in launches:
#     launch_date = launch['Launch Date']
#     reentry_date = launch['Reentry Date']
#     if reentry_date=='-':
#         reentry_date=ed + timedelta(days=1)
#     delta=(reentry_date-launch_date).days
#     start_index=(launch_date-sd).days
#     for i in range(start_index, start_index+delta):
#         rows[i]['In Orbit'] += 1

#     for i in range(start_index+delta, len(rows)):
#         rows[i]['Al'] += 143
#         rows[i]['Reentered'] += 1

# with open("launch-stats.csv", "w", newline='\n') as f:
#     writer = DictWriter(
#         f,
#         fieldnames=['Date', 'In Orbit', 'Al', 'Reentered'],
#     )
#     writer.writeheader()
#     for r in rows:
#         writer.writerow(r)
