from app.handlers import base_handler_router, file_handler_router
from app.uploading_file import uploading_file_router
from app.view_subscription_price import subscripition_router
from app.generate_pro_keys import pro_key_router
from app.stats import stats_router
from app.start_poll import start_poll_router
from app.sending_file import sending_file_router

all_router = [
    base_handler_router,
    uploading_file_router,
    subscripition_router,
    pro_key_router,
    start_poll_router,
    stats_router,
    sending_file_router,
    file_handler_router,
]


