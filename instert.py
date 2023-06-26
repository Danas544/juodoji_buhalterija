# pylint: disable-all
from main import Collections
import pytz
from datetime import datetime, timedelta, timezone
from py_random_words import RandomWords
import random

def get_random_date_ts():
    datetime_now = datetime.now()
    datetime_after = datetime_now + timedelta(days=365)
    ts_now = datetime_now.replace(tzinfo=timezone.utc).timestamp()
    ts_after = datetime_after.replace(tzinfo=timezone.utc).timestamp()
    random_date = random.uniform(ts_now,ts_after)
    return random_date

def get_string_field_value():
    r = RandomWords()
    r.get_word()
    return r.get_word()


def get_float_field_value(
    min_value: float = 1.00, max_value: float = 100000.00
) -> float:
    return random.uniform(min_value, max_value)


def get_integer_field_value(min_value=1, max_value=1000):
    return random.randint(min_value, max_value)


def str_to_time(time: str) -> "datetime":
    date_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    return date_time


def time_to_ts(time: datetime):
    timezone = pytz.timezone("Europe/Vilnius")
    dtzone = timezone.localize(time)
    tstamp = dtzone.timestamp()
    return tstamp


def insert_invoice(number, date, sel_name, b_name, price, tax, good_name, code):

    invoice = {
        "invoice_number": f"D-{number}",
        "Date": date,
        "invoice_details": {
            "seller_name": sel_name,
            "buyer_name": b_name,
            "price": price,
            "tax_amount": price / tax,
            "tax": tax,
            "price_with_tax": price + (price / tax),
            "goods": {"name": good_name, "code": code, "price": price},
        },
    }
    db.create_document(task=invoice)
    return invoice


if "__main__" == __name__:
    db = Collections(db="black_database", collection="invoices")
    for i in range(500, 601):
        invoice = insert_invoice(
            i,
            get_random_date_ts(),
            "Danielius",
            get_string_field_value(),
            get_float_field_value(),
            21,
            get_string_field_value(),
            get_integer_field_value(),
        )
    
