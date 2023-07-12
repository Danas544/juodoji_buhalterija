

def insert_invoice_rule():
    validation_rules1 = {
        "validator": {
            "$jsonSchema": {
                "required": ["invoice_details", "Date", "invoice_number"],
                "properties": {
                    "Date": {"bsonType": "double"},
                    "invoice_number": {"bsonType": "string"},
                    "invoice_details": {
                        "bsonType": "object",
                        "required": [
                            "seller_name",
                            "buyer_name",
                            "price",
                            "tax_amount",
                            "tax",
                            "price_with_tax",
                            "goods",
                        ],
                        "properties": {
                            "seller_name": {"bsonType": "string"},
                            "buyer_name": {"bsonType": "string"},
                            "price": {"bsonType": "double"},
                            "tax_amount": {"bsonType": "double"},
                            "tax": {"bsonType": "int"},
                            "price_with_tax": {"bsonType": "double"},
                            "goods": {
                                "bsonType": "object",
                                "required": ["name", "code", "price"],
                                "properties": {
                                    "name": {"bsonType": "string"},
                                    "code": {"bsonType": "int"},
                                    "price": {"bsonType": "double"},
                                },
                            },
                        },
                    },
                },
            }
        }
    }
    return validation_rules1
