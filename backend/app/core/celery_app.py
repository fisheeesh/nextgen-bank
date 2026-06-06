from celery import Celery
from .config import settings

# $ rabbitmq as connection string and redis as result backend

celery_app = Celery(
    # ? the name of the celery app
    "worker",
    # ? rabbitmq connection string
    # ? amqp -> the advanced message messaging queuing protocol
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
)

celery_app.conf.update(
    # ? json as the serialization format for our tasks
    task_serializer="json",
    # ? enable tracking when tasks start the execution
    task_track_started=True,
    # ? json as the serialization format for task result
    result_serializer="json",
    # ? restrict the accepted content types to json
    accept_content=["application/json"],
    # ? max retries when connection to the result backend
    result_backend_max_retries=10,
    # ? enable sending of the task - send evnets to monitoring tools
    task_send_sent_event=True,
    # ? store additional metadata information about our tasks
    result_extended=True,
    result_backend_always_retry=True,
    result_expires=3600,
    # ? timelimit for task execution -> tasks will be killed after this time
    task_time_limit=5 * 60,
    # ? soft time for task execution -> tasks will receive a timeout exception after this time
    task_soft_time_limit=5 * 60,
    # ? enable sending of the task related events
    worker_send_taks_events=True,
    # ? tasks are acknowledged after completion
    taks_acks_late=True,
    # ? rejexts tasks if worker is lost or disconnect
    task_reject_on_worker_lost=True,
    # ? prevent worker from prefetching too many tasks
    worker_prefetch_multiplier=1,
    # ? default retry delay
    task_default_retry_delay=300,
    # ? max number of retries for task
    task_max_retries=3,
    # ? default queue name for tasks
    task_default_queue="nextgen_tasks",
    # ? create missing queue if they dun exist
    task_create_missing_queues=True,
    # ? restart the workers after a thousand tasks -> prevent any memory leaks
    worker_max_tasks_per_child=1000,
    # ? max memory usage by child process
    worker_max_memory_per_child=50000,
    # ? log format for the workers
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s]%(message)s",
    # ? task log format
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

#  $ configure celery to automically discover the tasks
celery_app.autodiscover_tasks(
    packages=["app.core"],
    related_name="tasks",
    force=True
)
