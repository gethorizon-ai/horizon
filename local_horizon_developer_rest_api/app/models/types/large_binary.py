from sqlalchemy.sql.sqltypes import LargeBinary as BaseLargeBinary


class CustomLargeBinary(BaseLargeBinary):
    def process(self, value):
        return bytes(value, 'utf-8')
