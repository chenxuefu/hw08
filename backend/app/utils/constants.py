CLASS_ID_TO_NAME = {
    1: "rust",
    2: "smut",
    3: "healthy",
    4: "aphid",
}

CLASS_NAME_TO_ID = {value: key for key, value in CLASS_ID_TO_NAME.items()}

CLASS_NAME_TO_CN = {
    "rust": "锈病",
    "smut": "黑穗病",
    "healthy": "健康叶",
    "aphid": "蚜虫",
}

ROLE_ADMIN = "ROLE_ADMIN"
ROLE_EXPERT = "ROLE_EXPERT"
ROLE_USER = "ROLE_USER"

DATA_ALL = "DATA_ALL"
DATA_SELF = "DATA_SELF"
