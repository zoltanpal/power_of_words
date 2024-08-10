from dataclasses import dataclass, field


@dataclass
class DBConfig:
    username: str
    password: str
    dbname: str
    host: str
    dialect: str = field(default="mysql+pymysql")
    port: int = field(default=3306)
    maxconn: int = 10
    minconn: int = 1

    def validate(self):
        """Validate the types and fields' values"""

        for field_name, field_type in self.__annotations__.items():
            field_value = getattr(self, field_name)

            if not isinstance(field_value, field_type):
                msg = f"Invalid attribute type. '{field_name}' must be '{field_type}'"
                raise TypeError(msg)

            if field_value == "":
                error_msg = (
                    f"Missing value from the database configuration: '{field_name}'"
                )
                raise ValueError(error_msg)

    def __post_init__(self) -> None:
        self.validate()
