from enum import Enum


class RegistrationState(str, Enum):
    WAITING_FULL_NAME = "reg:waiting_full_name"
    WAITING_CONTACT = "reg:waiting_contact"


class TrainingFormState(str, Enum):
    WAITING_PARTNER_NAME = "train:waiting_partner_name"
    WAITING_SURNAME = "train:waiting_surname"
    WAITING_PHONE = "train:waiting_phone"
    WAITING_TOPIC = "train:waiting_topic"
    WAITING_DATE = "train:waiting_date"
    WAITING_TIME = "train:waiting_time"


class FeedbackState(str, Enum):
    WAITING_QUESTION = "feedback:waiting_question"


class RequestState(str, Enum):
    WAITING_ORDER_NUMBER = "request:waiting_order_number"
