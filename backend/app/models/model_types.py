from app.extensions import db


ID_TYPE = db.BigInteger().with_variant(db.Integer, "sqlite")
